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
            # 미완료 시험이 있는지 확인
            pending_quiz = db.temp_quiz.find_one({
                'userid': current_user_id
            })
            
            has_pending_quiz = pending_quiz is not None and not user.get('quiz_completed', False)
            
            # 수정된 부분: members 변수가 이제 quiz_takers를 의미함
            quiz_takers, rank_position, user_score, avg_score, max_score, has_taken_quiz = get_user_rank(current_user_id)
            
            return render_template(
                'main.html',
                nickname=user['nickname'],
                members=quiz_takers,
                rank_position=rank_position,
                user_id=current_user_id,
                user_score=user_score,
                avg_score=avg_score,
                max_score=max_score,
                has_taken_quiz=has_taken_quiz,
                has_pending_quiz=has_pending_quiz
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

        # 이미 퀴즈를 완료했는지 확인
        completed = db.member.find_one({
            'userid': current_user_id,
            'quiz_completed': True
        })
        
        if completed:
            return redirect('/quiz/finish')  # 완료했으면 결과 페이지로 보냄
        
        # 진행 중인 시험이 있는지 확인
        quiz_started = db.temp_quiz.find_one({'userid': current_user_id})
        
        if quiz_started:
            # 진행 중인 시험이 있으면 마지막 문제로 이동
            last_index = user.get('last_question_index', 0)
            return redirect(f'/quiz/play/{last_index}')
        
        # 아직 시험을 시작하지 않은 경우만 새 시험 생성
        # 문제 5개를 랜덤으로 선택
        all_quizzes = list(db.quiz_list.find())
        selected_quizzes = random.sample(all_quizzes, 5)

        # 새 퀴즈 저장
        for quiz in selected_quizzes:
            db.temp_quiz.insert_one({
                'userid': current_user_id,
                'question_id': str(quiz['_id']),
                'question': quiz['question'],
                'answer': quiz['answer'],
                'options': quiz.get('options'),
                'answered': False
            })
        
        # 퀴즈 진행 상태 초기화
        db.member.update_one(
            {'userid': current_user_id},
            {'$set': {
                'quiz_in_progress': True,
                'quiz_start_time': datetime.datetime.now(),
                'last_question_index': 0,
                'quiz_completed': False  # 명시적으로 완료되지 않음을 표시
            }}
        )
        
        # 첫 번째 문제 페이지로 이동
        return redirect('/quiz/play/0')

    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')

@app.route('/quiz/resume')
def quiz_resume():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})
        
        if not user:
            return redirect('/')
            
        # 진행 중인 시험이 있는지 확인
        quiz_exists = db.temp_quiz.find_one({'userid': current_user_id})
        
        if not quiz_exists:
            return redirect('/quiz/start')  # 없으면 새로 시작
            
        # 퀴즈 진행 중 상태로 표시
        db.member.update_one(
            {'userid': current_user_id},
            {'$set': {
                'quiz_in_progress': True,
                'quiz_completed': False  # 명시적으로 완료되지 않음을 표시
            }}
        )
        
        # 마지막 문제로 이동
        last_index = user.get('last_question_index', 0)
        return redirect(f'/quiz/play/{last_index}')
        
    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')
    
@app.route('/quiz/play/<int:index>')
def quiz_play(index):
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})

        # 현재 인덱스를 저장
        db.member.update_one(
            {'userid': current_user_id},
            {'$set': {'last_question_index': index}}
        )

        quizzes = list(db.temp_quiz.find({'userid': current_user_id}))
        if index >= len(quizzes):
            return redirect('/quiz/finish')

        quiz = quizzes[index]
        
        # 문제가 이미 답변되었는지 확인
        is_answered = quiz.get('answered', False)
        
        if 'options' in quiz and isinstance(quiz['answer'], int):
            correct_text = quiz['options'][quiz['answer'] - 1]  # 0-based index
        else:
            correct_text = quiz['answer']

        
        
        return render_template(
            "quiz.html", 
            quiz=quiz, 
            index=index, 
            is_answered=is_answered,
            question_number=index + 1,
            total_questions=len(quizzes),
            nickname=user['nickname'],
            quiz_in_progress=True,
            correct_answer=correct_text
        )

    except:
        return redirect('/')

@app.route('/quiz/submit', methods=['POST'])
def quiz_submit():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']

        index = int(request.form['index'])
        question_id = request.form['question_id']
        user_answer = request.form['user_answer']

        quiz = db.temp_quiz.find_one({'userid': current_user_id, 'question_id': question_id})
        correct = user_answer.strip().lower() == quiz['answer'].strip().lower()

        db.answers.insert_one({
            'userid': current_user_id,
            'question_id': question_id,
            'user_answer': user_answer,
            'correct': correct
        })

        return redirect(f'/quiz/play/{index + 1}')

    except:
        return redirect('/')

@app.route('/quiz/save_progress', methods=['POST'])
def save_quiz_progress():
    data = request.json
    token = request.cookies.get('mytoken')
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        
        # 현재 진행 상태 저장
        db.member.update_one(
            {'userid': current_user_id},
            {'$set': {
                'last_question_index': data.get('current_index', 0)
            }}
        )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify({'status': 'error'})
    
# 퀴즈 답변 제출 처리
@app.route('/quiz/answer', methods=['POST'])
def quiz_answer():
    data = request.json
    token = request.cookies.get('mytoken')
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        
        # 해당 문제를 답변 완료로 표시
        db.temp_quiz.update_one(
            {
                'userid': current_user_id,
                'question_id': data.get('question_id')
            },
            {'$set': {'answered': True}}
        )
        
        # 학습 모드라면 score 반영도, 기록도 하지 않음
        if data.get('mode') == 'learn':
            return jsonify({'status': 'success', 'message': 'learn mode - not recorded'})
      
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
            'user_answer': data.get('user_answer', ''),
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
            # 시험을 본 적이 있는지 확인
            quiz_exists = db.temp_quiz.find_one({'userid': current_user_id})
            if not quiz_exists:
                return redirect('/main')  # 시험을 본 적이 없으면 메인으로
            
            # 모든 문제에 답변했는지 확인
            all_questions = list(db.temp_quiz.find({'userid': current_user_id}))
            answered_count = sum(1 for q in all_questions if q.get('answered', False))
            
            # 완료 상태 표시 (모든 문제를 풀었는지와 상관없이)
            db.member.update_one(
                {'userid': current_user_id},
                {'$set': {
                    'quiz_completed': True,
                    'quiz_in_progress': False
                }}
            )
            
            nickname = user['nickname']
            correct_cnt = db.answers.count_documents({
                'userid': current_user_id, 
                'is_correct': True
            })
            
            # 퀴즈를 응시한 사용자의 ID 목록 가져오기
            quiz_taken_users = set(answer['userid'] for answer in db.answers.find({}, {'userid': 1}))
            
            # 모든 유저 목록에서 퀴즈 응시자만 필터링
            members = list(db.member.find())
            quiz_takers = [member for member in members if member['userid'] in quiz_taken_users]
            
            # 점수 계산 및 순위 업데이트
            user_score = correct_cnt
            db.member.update_one(
                {'userid': current_user_id},
                {'$set': {'score': user_score}}
            )
            
            # 점수 기준 정렬
            quiz_takers.sort(key=lambda x: x.get('score', 0), reverse=True)

            # 현재 유저 순위 계산 - 퀴즈 응시자 중에서만 계산
            my_rank = next(
                (i for i, m in enumerate(quiz_takers, start=1) if m['userid'] == current_user_id),
                None
            )
            
            # 틀린 문제 정보 가져오기
            wrong_answers = list(db.answers.find({
                'userid': current_user_id,
                'is_correct': False
            }))
            
            # wrong_questions = []
            # 기존 wrong_questions 부분을 수정
            wrong_questions = []
            for wrong in wrong_answers:
                q_id = wrong.get('question_id')
                question = db.temp_quiz.find_one({
                    'userid': current_user_id,
                    'question_id': q_id
                })
                if question:
                    wrong_questions.append({
                        'question': question.get('question', ''),
                        'answer': question.get('answer', ''),
                        'userAnswer': wrong.get('user_answer', '')  # 수정: user_answer -> userAnswer
                    })

            # 사용자 문서에 틀린 문제 저장
            db.member.update_one(
                {'userid': current_user_id},
                {'$set': {'wrong_questions': wrong_questions}}
            )
            
            # 미완료 문제 수 계산
            incomplete_count = len(all_questions) - answered_count
            incomplete_warning = None
            if incomplete_count > 0:
                incomplete_warning = f"{incomplete_count}개 문제를 풀지 않았습니다. 풀지 않은 문제는 오답으로 처리됩니다."
            
            return render_template(
                "quiz_finish.html",
                nickname=nickname,
                correct_cnt=correct_cnt,
                total_cnt=len(all_questions),
                my_rank=my_rank,
                wrong_questions=wrong_questions,
                incomplete_warning=incomplete_warning
            )
    except jwt.ExpiredSignatureError:
        return redirect('/main')
    except jwt.exceptions.DecodeError:
        return redirect('/main')

    return redirect('/main')

# 로그아웃
@app.route('/logout')
def logout():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        
        # 시험 진행 중인지 확인
        user = db.member.find_one({
            'userid': current_user_id, 
            'quiz_in_progress': True,
            'quiz_completed': {'$ne': True}
        })
        
        if user:
            # 시험 중 로그아웃 - 진행 중 시험 상태 저장
            # 상태만 변경하고 시험 데이터는 유지
            db.member.update_one(
                {'userid': current_user_id},
                {'$set': {'quiz_in_progress': False}}
            )
    except:
        pass
        
    # 로그아웃 처리
    response = make_response(redirect('/'))
    response.delete_cookie('mytoken')
    return response

# 학습 모드 추가
@app.route('/quiz/learn')
def quiz_learn():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user_id = payload['id']
        user = db.member.find_one({'userid': current_user_id})

        if not user:
            return redirect('/')

        # 학습 모드에서도 이미 푼 문제 포함해서 랜덤으로 5문제 제공
        all_quizzes = list(db.quiz_list.find())
        if not all_quizzes:
            return "퀴즈가 존재하지 않습니다."

        # 랜덤 퀴즈 1개 선택
        quiz = random.choice(all_quizzes)

        return render_template("quiz_learn.html", quiz=quiz, nickname=user['nickname'], is_learn=True)

    except jwt.ExpiredSignatureError:
        return redirect('/')
    except jwt.exceptions.DecodeError:
        return redirect('/')

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)