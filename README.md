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

# 깃배시:
source venv/scripts/activate

*가성 환경 비활성화 : deactivate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. Node 패키지 설치
npm install

# 6. Tailwind CSS 빌드 (별도 터미널에서 실행 - 계속 실행됨)
npm run build-css

# 7. 새 터미널에서 (가상환경 활성화 후)
python app.py

# 8. 주소 접속
http://localhost:5000/
