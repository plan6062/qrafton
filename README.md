# 📝 퀴즈를 통한 복습 서비스웹 Q래프톤

![Image](https://github.com/user-attachments/assets/9ab06e5a-262d-4b9e-8aa8-e7a79e58453d)

# 프로젝트 소개
● Q래프톤은 매주 배운 내용을 퀴즈로 복습할 수 있는 웹 서비스입니다.  
● 틀린 문제에 대한 답을 바로 확인할 수 있습니다.  
● 시험모드와 학습모드를 통한 학습을 할 수 있습니다.
  ○시험모드는 주차별로 한번씩만 응시가능하며, 순위를 확인 할 수 있습니다.
  ○학습모드는 사용자가 학습을 중단하기 전까지 반복 학습이 가능합니다.
● 로그인/회원가입 기능을 통해 사용자간의 순위를 비교할 수 있습니다.

# 0. 개발 환경
● Front-end : HTML, tailwindcss, Jinja  
● Back-end : Flask, Jinja  
● 데이터베이스 : mongo DB  
● 협업 툴 : Github  
● 서비스 배포 환경 : AWS

# 1. 프로젝트 구조
📦node_modules
📦static
 ┗📂css
 ┃ ┣ main.css
 ┃ ┗ tailwind.css
📦templates
 ┣ index.html
 ┣ main.html
 ┣ quiz.html
 ┣ quiz_finish.html
 ┣ quiz_learn.html
 ┣ register.html
 ┣ select_week.html
 ┗ select_week_learn.html
📦venv
.gitattributes
.gitignore
app.py
insert_quiz_w1.py
insert_quiz_w2.py
insert_quiz_w3.py
insert_quiz.py
package.json
README.md
requirements.txt
tailwind.config.js

//실행 전 
# 1. 저장소 클론
git clone [저장소URL]
cd [프로젝트폴더]

# 2. 가상환경 설정
python -m venv venv

# 3. 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
# GitBash:
source venv/scripts/activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. Node 패키지 설치
npm install

# 6. Tailwind CSS 빌드 (별도 터미널에서 실행 - 계속 실행됨)
npm run build-css

# 7. 새 터미널에서 (가상환경 활성화 후)
python app.py

# 로컬 주소:
http://localhost:5000/

# EC2 주소:
http://3.39.194.140:5000/
