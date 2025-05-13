import jwt
import datetime
from flask import Flask, render_template, jsonify, request, redirect, make_response
from pymongo import MongoClient
import random
import json
import secrets

SECRET_KEY = secrets.token_hex(32)
  
  
app = Flask(__name__)
client = MongoClient('localhost', 27017)

#EC2 연결시에는
#client=MongoClient('mongodb://test:test@3.39.194.140',27017)

db = client.quiz  # 'quiz' 라는 DB
#컬렉션은 (member,question,answer,rank 등 예정 )

#필요한 함수선언 부분 ###################################
def get_user_rank(userid):
    members = list(db.member.find())
    members.sort(key=lambda x: x.get('score', 0), reverse=True)
    rank = next((i for i, m in enumerate(members, start=1) if m['userid'] == userid), None)
    
    # 점수 통계 계산
    total_score = sum(member.get('score', 0) for member in members)
    avg_score = total_score / len(members) if members else 0
    max_score = max((member.get('score', 0) for member in members), default=10)
    
    # 사용자 점수 가져오기
    user_score = next((member.get('score', 0) for member in members if member['userid'] == userid), 0)
    
    return members, rank, user_score, avg_score, max_score


##############################################


# 첫 로그인 페이지 
@app.route('/')
def home():
    return render_template('index.html')


# 로그인 페이지 
@app.route('/login', methods=['POST']) 
def login():
    userid = request.form['userid']
    userpw = request.form['userpw']
    user = db.member.find_one({'userid': userid, 'userpw': userpw})

    # 로그인 성공시 메인페이지로 이동
    if user:
        payload = {
            'id': userid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        response = make_response(redirect('/main'))
        response.set_cookie('mytoken', token)
        return response
    else:
        return render_template('index.html', error='아이디 또는 비밀번호 오류')

# 회원가입 폼으로 이동 /GET
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

# 회원가입 처리 /POST
@app.route('/register', methods=['POST'])
def register():
    userid = request.form['userid']
    userpw = request.form['userpw']
    nickname = request.form['nickname']
    
    existing_user = db.member.find_one({'userid': userid})
    if existing_user:
        return render_template('register.html', error='이미 존재하는 아이디입니다.')
    
    # DB에 삽입 - 초기 score는 0 포함
    db.member.insert_one({
        'userid': userid,
        'userpw': userpw,
        'nickname': nickname,
        'score': 0,
        'wrong_questions': []  # 틀린 문제를 저장할 배열 추가
    })
    return render_template('register.html', success=True)

# 로그인 후 메인 페이지 - main.html과 연결
# 오류시 첫 로그인 페이지로 연결 
# JWT인증 방식으로 로그인 구현 
@app.route('/main')
def main():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})

        if user:
            # 수정된 부분: 사용자 정보와 함께 통계 데이터도 가져오기
            members, rank_position, user_score, avg_score, max_score = get_user_rank(current_user_id)
            return render_template(
                'main.html',
                nickname=user['nickname'],
                members=members,
                rank_position=rank_position,
                user_id=current_user_id,
                user_score=user_score,
                avg_score=avg_score,
                max_score=max_score
            )
    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')

    return redirect('/')

####################################################################

# 퀴즈 시작 부분
@app.route('/quiz/start')
def quiz_start():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})
        
        if not user:
            return redirect('/')
            
        # 세션에 퀴즈 카운트가 없으면 사용자의 퀴즈 기록 초기화
        quiz_list = list(db.quiz_list.find())  # quiz 컬렉션
        quiz = random.choice(quiz_list)  # 랜덤으로 문제 하나 선택
        
        return render_template("quiz.html", quiz=quiz, nickname=user['nickname'])
    except:
        return redirect('/')

# 퀴즈 답변 제출 처리
@app.route('/quiz/answer', methods=['POST'])
def quiz_answer():
    data = request.json
    token = request.cookies.get('mytoken')
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})
        
        if user:
            if data.get('is_correct'):
                # 정답인 경우 점수 증가
                db.member.update_one(
                    {'userid': current_user_id},
                    {'$inc': {'score': 1}}
                )
            
            # 답변 기록 저장
            db.answers.insert_one({
                'userid': current_user_id,
                'question_id': data.get('question_id'),
                'is_correct': data.get('is_correct'),
                'timestamp': datetime.datetime.now()
            })
            
            return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify({'status': 'error'})

# 틀린 문제 저장
@app.route('/quiz/save_wrong', methods=['POST'])
def save_wrong():
    data = request.json
    token = request.cookies.get('mytoken')
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        
        # 틀린 문제 기록 저장
        if data:
            db.member.update_one(
                {'userid': current_user_id},
                {'$set': {'wrong_questions': data}}
            )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify({'status': 'error'})

# 퀴즈 완료 부분
@app.route('/quiz/finish')
def quiz_finish():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})

        if user:
            nickname = user['nickname']
            correct_cnt = user.get('score', 0)  # 맞은 개수는 score 필드에서

            # 모든 유저 점수 기준 정렬
            members = list(db.member.find())
            members.sort(key=lambda x: x.get('score', 0), reverse=True)

            # 현재 유저 순위 계산
            my_rank = next(
                (i for i, m in enumerate(members, start=1) if m['userid'] == current_user_id),
                None
            )
            
            # 틀린 문제 정보 가져오기
            wrong_questions = user.get('wrong_questions', [])
            
            return render_template("quiz_finish.html",
                                  nickname=nickname,
                                  correct_cnt=correct_cnt,
                                  my_rank=my_rank,
                                  wrong_questions=wrong_questions)
    except jwt.ExpiredSignatureError:
        return redirect('/main')
    except jwt.exceptions.DecodeError:
        return redirect('/main')

    return redirect('/main')

# 로그아웃
@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie('mytoken')
    return response


if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
