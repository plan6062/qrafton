# insert_quiz.py
from pymongo import MongoClient
#1주차 db -> quiz_list_w1 컬렉션션

#EC2 연결시에는
#client=MongoClient('mongodb://test:test@3.39.194.140',27017)
client = MongoClient('localhost', 27017)
db = client.quiz

db.quiz_list_w2.drop()

quiz_data = [
    {"question": "[2주차] Python에서 리스트의 길이를 구하는 함수는?", "answer": "len"},
    {"question": "[2주차] HTML에서 문서의 제목을 지정하는 태그는?", "answer": "title"},
    {"question": "[2주차] CSS에서 경계선을 둥글게 만들 때 사용하는 속성은?", "answer": "border-radius"},
    {"question": "[2주차] JavaScript에서 함수를 선언할 때 사용하는 키워드는?", "answer": "function"},
    {"question": "[2주차] Python에서 반복문을 만드는 키워드는?", "answer": "for"},
    {"question": "[2주차] JavaScript에서 리스트의 각 요소에 접근할 수 있는 방법은? ", "answer": "index"},
   
]



unique_questions = set()
clean_quiz_data = []

for quiz in quiz_data:
    q = quiz["question"]
    if q not in unique_questions:
        unique_questions.add(q)
        clean_quiz_data.append(quiz)

# 중복 제거된 퀴즈만 quiz_list 컬렉션에 삽입
db.quiz_list_w2.insert_many(clean_quiz_data)
print("중복 제거된 퀴즈 삽입 완료!")
