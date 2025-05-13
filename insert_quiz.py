# 벌크로 퀴즈 추가하는 부분 -따로 실행필요
# insert_quiz.py
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.quiz

quiz_data = [
    {"question": "파이썬에서 리스트의 길이를 구하는 함수는?", "answer": "len"},
    {"question": "HTML에서 문서의 제목을 지정하는 태그는?", "answer": "title"},
    {"question": "CSS에서 색상을 지정할 때 사용하는 프로퍼티는?", "answer": "color"},
    {"question": "JavaScript에서 함수를 선언할 때 사용하는 키워드는?", "answer": "function"},
]

db.quiz_list.insert_many(quiz_data)
print("문제 삽입 완료!")
