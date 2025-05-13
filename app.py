import jwt
import datetime
from flask import Flask, render_template, jsonify, request,redirect,make_response
from pymongo import MongoClient
import random

SECRET_KEY="your_secret_key"
  
  
app = Flask(__name__)
#client = MongoClient('mongodb://아이디:비번번@52.78.119.209', 27017)
client=MongoClient('localhost',27017)

db = client.quiz  # 'quiz' 라는 DB
#컬렉션은 (member,question,answer,rank 등 예정 )

#필요한 함수선언 부분 ###################################
def get_user_rank(userid):
    members = list(db.member.find())
    members.sort(key=lambda x: x.get('score', 0), reverse=True)
    rank = next((i for i, m in enumerate(members, start=1) if m['userid'] == userid), None)
    return members, rank





##############################################


# 첫 로그인 페이지 
@app.route('/')
def home():
    return render_template('index.html')


# 로그인 페이지 
@app.route('/login',methods=['POST']) 
def login():
    
    userid= request.form['userid']
    userpw= request.form['userpw']
    user= db.member.find_one({'userid':userid,'userpw':userpw})

    #로그인 성공시 메인페이지로 이동
    if user:
        payload={
            'id':userid,
            'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
        response=make_response(redirect('/main'))
        response.set_cookie('mytoken',token)
        return response
    else:
        return render_template('index.html', error='아이디 또는 비밀번호 오류')

#회원가입 폼으로 이동 /GET
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

#회원가입 처리  /POST
@app.route('/register', methods=['POST'])
def register():
    userid= request.form['userid']
    userpw= request.form['userpw']
    nickname=request.form['nickname']
    
    existing_user=db.member.find_one({'userid':userid})
    if existing_user==True:
        return render_template('register.html', error = '이미 존재하는 아이디입니다.')
    
    #DB에 삽입 - 초기 score는 0 포함
    db.member.insert_one({'userid':userid,'userpw':userpw,'nickname':nickname,'score':0})
    return render_template('register.html',success=True)

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
            members, rank_position = get_user_rank(current_user_id)
            return render_template(
                'main.html',
                nickname=user['nickname'],
                members=members,
                rank_position=rank_position
            )
    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')

    return redirect('/')


#퀴즈 시작 부분
@app.route('/quiz/start')
def quiz_start():
    quiz_list=list(db.quiz_list.find())  # quiz 컬렉션
    quiz = random.choice(quiz_list)  # 랜덤으로 문제 하나 선택
    
    return render_template("quiz.html",quiz=quiz)

#퀴즈 완료 부분
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

            return render_template("quiz_finish.html",
                                   nickname=nickname,
                                   correct_cnt=correct_cnt,
                                   my_rank=my_rank)
    except jwt.ExpiredSignatureError:
        return redirect('/main')
    except jwt.exceptions.DecodeError:
        return redirect('/main')

    return redirect('/main')




if __name__=='__main__':
    app.run(debug=True)