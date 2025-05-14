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
    {"question": "Python에서 '==' 연산자는 두 값이 같은지를 비교할 때 사용된다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "HTML에서 <form> 태그는 사용자 입력을 서버로 전송하는 데 사용된다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "Python에서 리스트는 한 번 정의하면 내용을 바꿀 수 없다. (맞으면o, 틀리면 x)", "answer": "x"},
    {"question": "CSS에서 'z-index'는 요소의 쌓임 순서를 조절하는 속성이다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "JavaScript에서 'NaN'은 'Not a Number'를 의미한다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "HTML5에서는 <video> 태그로 동영상을 삽입할 수 있다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "CSS의 'position: fixed'는 스크롤해도 요소의 위치가 고정된다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "JavaScript에서 'alert()' 함수는 브라우저 콘솔에 로그를 출력한다. (맞으면o, 틀리면 x)", "answer": "x"},
    {"question": "Python에서 딕셔너리는 키와 값의 쌍으로 데이터를 저장한다. (맞으면o, 틀리면 x)", "answer": "o"},
    {"question": "HTML의 <head> 태그는 화면에 표시되는 콘텐츠를 포함한다. (맞으면o, 틀리면 x)", "answer": "x"},
    {"question": "CSS에서 'overflow: hidden'은 넘친 콘텐츠를 숨긴다. (맞으면o, 틀리면 x)", "answer": "o"},
    {
        "question": "Python에서 리스트를 정렬하는 메서드는 무엇인가요? (번호만 쓰세요)",
        "options": ["1. sort()", "2. list()", "3. order()", "4. arrange()"],
        "answer": 1
    },
    {
        "question": "HTML 문서에서 문서의 메타 정보를 담는 태그는? (번호만 쓰세요)",
        "options": ["1. <meta>", "2. <head>", "3. <title>", "4. <body>"],
        "answer": 1
    },
    {
        "question": "CSS에서 요소를 보이지 않게 하는 속성은? (번호만 쓰세요)",
        "options": ["1. display", "2. invisible", "3. opacity", "4. visibility"],
        "answer": 1
    },
    {
        "question": "JavaScript에서 반복문 중 조건이 거짓이 될 때까지 실행되는 것은? (번호만 쓰세요)",
        "options": ["1. if", "2. for", "3. while", "4. switch"],
        "answer": 3
    },
    {
        "question": "Python에서 예외 처리를 시작할 때 사용하는 키워드는? (번호만 쓰세요)",
        "options": ["1. catch", "2. try", "3. error", "4. handle"],
        "answer": 2
    },
    {
        "question": "CSS에서 글꼴을 지정하는 속성은? (번호만 쓰세요)",
        "options": ["1. font-family", "2. font-weight", "3. text-style", "4. typeface"],
        "answer": 1
    },
    {
        "question": "JavaScript에서 현재 웹페이지의 URL을 가져오는 객체는? (번호만 쓰세요)",
        "options": ["1. window.url", "2. location", "3. document.url", "4. navigator"],
        "answer": 2
    },
    {
        "question": "HTML에서 체크박스를 만드는 input 타입은? (번호만 쓰세요)",
        "options": ["1. text", "2. button", "3. checkbox", "4. radio"],
        "answer": 3
    },
    {
        "question": "Python에서 set 자료형의 주요 특징은? (번호만 쓰세요)",
        "options": ["1. 순서가 있다", "2. 중복을 허용한다", "3. 키와 값으로 구성된다", "4. 중복을 허용하지 않는다"],
        "answer": 4
    },
    {
        "question": "CSS에서 'flex-direction: row'는 어떤 방향으로 정렬하나요? (번호만 쓰세요)",
        "options": ["1. 수직 방향", "2. 왼쪽에서 오른쪽", "3. 오른쪽에서 왼쪽", "4. 위에서 아래"],
        "answer": 2
    }
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
