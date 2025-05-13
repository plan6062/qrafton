# insert_quiz.py
from pymongo import MongoClient


#EC2 연결시에는
#client=MongoClient('mongodb://test:test@3.39.194.140',27017)
client = MongoClient('localhost', 27017)
db = client.quiz

db.quiz_list.drop()

quiz_data = [
    {"question": "Python에서 리스트의 길이를 구하는 함수는?", "answer": "len"},
    {"question": "HTML에서 문서의 제목을 지정하는 태그는?", "answer": "title"},
    {"question": "CSS에서 경계선을 둥글게 만들 때 사용하는 속성은?", "answer": "border-radius"},
    {"question": "JavaScript에서 함수를 선언할 때 사용하는 키워드는?", "answer": "function"},
    {"question": "Python에서 반복문을 만드는 키워드는?", "answer": "for"},
    {"question": "JavaScript에서 리스트의 각 요소에 접근할 수 있는 방법은? ", "answer": "index"},
    {"question": "CSS에서 글자 크기를 조절하는 속성은?", "answer": "font-size"},
    {"question": "JavaScript에서 값을 출력할 때 사용하는 함수는?", "answer": "console.log"},
    {"question": "Python에서 조건문을 시작할 때 사용하는 키워드는?", "answer": "if"},
    {"question": "HTML에서 가장 큰 제목을 나타내는 태그는?", "answer": "h1"},
    {"question": "일반적인 언어로 코드를 흉내내어 적는 것은?", "answer": "슈도코드"},
    {"question": "Python에서 함수를 정의할 때 사용하는 키워드는?", "answer": "def"},
    {"question": "HTML에서 줄바꿈을 할 때 사용하는 태그는?", "answer": "br"},
    {"question": "JavaScript에서 참,거짓을 나타내는 자료형은?", "answer": "boolean"},
    {"question": "웹 페이지에서 우리가 원하는 부분의 데이터를 수집해오는 것은?", "answer": "웹 스크래핑"},
    {"question": "Python에서 웹 서버와 통신할 때 사용되는 라이브러리는?", "answer": "requests"},
    {"question": "JavaScript에서 조건문을 끝낼 때 사용하는 키워드는?", "answer": "else"},
    {"question": "인터넷 위에서 컴퓨터가 통신할 수 있도록 각 컴퓨터마다 가지는 고유한 주소는?", "answer": "IP주소"},  
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
