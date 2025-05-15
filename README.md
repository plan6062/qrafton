# 📝 퀴즈를 통한 복습 서비스웹 Q래프톤

![노란색 흰색 심플한 마케팅 프로젝트 프레젠테이션](https://github.com/user-attachments/assets/647075d4-7405-41d8-93ab-975fecd564c6)

# 프로젝트 소개
● Q래프톤은은 배운 내용을 퀴즈로 복습할 수 있는 웹 서비스입니다.  
● 틀린 문제에 대한 답을 바로 확인할 수 있습니다.  
● 로그인/회원가입 기능을 통해 사용자간의 순위를 비교할 수 있습니다.

# 1. 개발 환경
● Front-end : HTML, tailwindcss, Jinja  
● Back-end : Flask, Jinja  
● 데이터베이스 : mongo DB  
● 협업 툴 : Github  
● 서비스 배포 환경 : AWS

# 2. 페이지별 기능
![image](https://github.com/user-attachments/assets/2d3a63db-17bc-458d-97fa-b958fd8ef33b)
<img src="https://github.com/user-attachments/assets/2d3a63db-17bc-458d-97fa-b958fd8ef33b.png" width="200" height="200"/>

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
