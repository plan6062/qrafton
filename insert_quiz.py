# insert_quiz.py
from pymongo import MongoClient


#EC2 연결시에는
#client=MongoClient('mongodb://test:test@3.39.194.140',27017)
client = MongoClient('localhost', 27017)
db = client.quiz

db.quiz_list.drop()

quiz_data = [
    {"question": "파이썬에서 리스트의 길이를 구하는 함수는?", "answer": "len"},
    {"question": "HTML에서 문서의 제목을 지정하는 태그는?", "answer": "title"},
    {"question": "CSS에서 색상을 지정할 때 사용하는 프로퍼티는?", "answer": "color"},
    {"question": "JavaScript에서 함수를 선언할 때 사용하는 키워드는?", "answer": "function"},
    {"question": "Python에서 반복문을 만드는 키워드는?", "answer": "for"},
    {"question": "HTML에서 링크를 만들 때 사용하는 태그는?", "answer": "a"},
    {"question": "CSS에서 글자 크기를 조절하는 속성은?", "answer": "font-size"},
    {"question": "JavaScript에서 값을 출력할 때 사용하는 함수는?", "answer": "console.log"},
    {"question": "Python에서 조건문을 시작할 때 사용하는 키워드는?", "answer": "if"},
    {"question": "HTML에서 가장 큰 제목을 나타내는 태그는?", "answer": "h1"},
    {"question": "CSS에서 요소의 배경색을 지정하는 속성은?", "answer": "background-color"},
    {"question": "Python에서 함수를 정의할 때 사용하는 키워드는?", "answer": "def"},
    {"question": "HTML에서 줄바꿈을 할 때 사용하는 태그는?", "answer": "br"},
    {"question": "JavaScript에서 배열의 길이를 구하는 속성은?", "answer": "length"},
    {"question": "CSS에서 요소를 가운데 정렬할 때 주로 사용하는 속성은?", "answer": "text-align"},
    {"question": "Python에서 리스트에 값을 추가하는 함수는?", "answer": "append"},
    {"question": "HTML에서 이미지를 삽입할 때 사용하는 태그는?", "answer": "img"},
    {"question": "JavaScript에서 조건을 검사할 때 사용하는 키워드는?", "answer": "if"},  # 중복
    {"question": "CSS에서 외부 스타일시트를 연결할 때 사용하는 태그는?", "answer": "link"},
    {"question": "Python에서 값을 출력할 때 사용하는 함수는?", "answer": "print"},
]


unique_questions = set()
clean_quiz_data = []

for quiz in quiz_data:
    q = quiz["question"]
    if q not in unique_questions:
        unique_questions.add(q)
        clean_quiz_data.append(quiz)

# 중복 제거된 퀴즈만 quiz_list 컬렉션에 삽입
db.quiz_list.insert_many(clean_quiz_data)
print("중복 제거된 퀴즈 삽입 완료!")
