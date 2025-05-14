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
    
    # 퀴즈를 응시한 사용자의 ID 목록 가져오기
    quiz_taken_users = set(answer['userid'] for answer in db.answers.find({}, {'userid': 1}))
    
    # 퀴즈를 응시한 사용자만 필터링
    quiz_takers = [member for member in members if member['userid'] in quiz_taken_users]
    
    # 점수로 정렬
    quiz_takers.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # 퀴즈 응시자 목록에서의 순위 계산
    rank = next((i for i, m in enumerate(quiz_takers, start=1) if m['userid'] == userid), None)
    
    # 점수 통계 계산 - 퀴즈 응시자만 포함
    if quiz_takers:
        total_score = sum(member.get('score', 0) for member in quiz_takers)
        avg_score = total_score / len(quiz_takers)
        max_score = max((member.get('score', 0) for member in quiz_takers), default=10)
    else:
        avg_score = 0
        max_score = 10
    
    # 사용자가 퀴즈를 응시했는지 확인
    has_taken_quiz = userid in quiz_taken_users
    
    # 사용자 점수 가져오기
    user_score = next((member.get('score', 0) for member in members if member['userid'] == userid), 0)
    
    # 전체 멤버 목록 대신 퀴즈 응시자 목록만 반환
    return quiz_takers, rank, user_score, avg_score, max_score, has_taken_quiz


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

@app.route('/check_userid',methods=['POST'])
def check_userid():
    check_userid=request.form['userid']
    existing_user=db.member.find_one({'userid':check_userid})
    
    if existing_user:
        check_result='중복된 아이디입니다'
    else:
        check_result='사용 가능한 아이디입니다'

    return render_template('register.html',userid=check_userid, check_result=check_result)


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
            # 수정된 부분: members 변수가 이제 quiz_takers를 의미함
            quiz_takers, rank_position, user_score, avg_score, max_score, has_taken_quiz = get_user_rank(current_user_id)
            
            return render_template(
                'main.html',
                nickname=user['nickname'],
                members=quiz_takers,  # 퀴즈 응시자 목록
                rank_position=rank_position,
                user_id=current_user_id,
                user_score=user_score,
                avg_score=avg_score,
                max_score=max_score,
                has_taken_quiz=has_taken_quiz
            )
    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')

    return redirect('/')

####################################################################

# 퀴즈 시작 부분
# 학습 모드
@app.route('/quiz/learn_mode')
def quiz_learn_mode():
    return render_quiz_mode(mode='quiz')

#  시험 모드
@app.route('/quiz/exam_mode')
def quiz_exam_mode():
    return render_quiz_mode(mode='exam')

# 공통 퀴즈 렌더링 함수

def render_quiz_mode(mode):
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})

        if not user:
            return redirect('/')

        quiz_list = list(db.quiz_list.find())
        quiz = random.choice(quiz_list)

        return render_template("quiz.html", quiz=quiz, nickname=user['nickname'], mode=mode)
    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')

# 퀴즈 제출 처리 수정: mode 함께 처리
@app.route('/quiz/answer', methods=['POST'])
def quiz_answer():
    data = request.json
    token = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})

        if user:
            is_correct = data.get('is_correct')
            mode = data.get('mode', 'exam')  # 기본값은 시험 모드

            if is_correct and mode == 'exam':
                db.member.update_one(
                    {'userid': current_user_id},
                    {'$inc': {'score': 1}}
                )

            db.answers.insert_one({
                'userid': current_user_id,
                'question_id': data.get('question_id'),
                'is_correct': is_correct,
                'mode': mode,
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
