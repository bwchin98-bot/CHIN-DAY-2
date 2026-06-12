# 🏗️ 실행 환경 설정 가이드

프로젝트를 실행하기 위한 단계별 설정 방법입니다.

## ✅ 환경 요구사항

- **Python**: 3.8 이상
- **OS**: Windows, macOS, Linux
- **브라우저**: Chrome (원격 디버깅 포트 연결 시)

## 🚀 빠른 시작 (5분)

### 1️⃣ 저장소 복제

```bash
git clone https://github.com/bwchin98-bot/CHIN-DAY-2.git
cd CHIN-DAY-2
```

### 2️⃣ 가상환경 생성 및 활성화

**Windows (PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ 의존성 설치

```bash
pip install -r requirements.txt
```

### 4️⃣ 환경 설정

```bash
# .env 파일 생성 (선택사항)
cp .env.example .env
```

.env 파일 내용:
```
GEMINI_API_KEY=sk-your_key_here          # 선택: Gemini API 키
EMAIL_SERVICE=naver                      # 고정
EMAIL_ID=your_email@naver.com            # 선택: 네이버 이메일
EMAIL_PW=your_password                   # 선택: 네이버 비밀번호
```

**주의**: API 키 없이도 모의 데이터로 기본 기능 테스트 가능!

### 5️⃣ 서버 실행

**Windows (PowerShell)**:
```powershell
.\run.ps1
```

**macOS/Linux**:
```bash
python app.py
```

### 6️⃣ 웹 브라우저에서 접속

```
http://localhost:5000
```

---

## 🎯 사용 시나리오

### 시나리오 A: API 키 없이 기본 기능 테스트 (권장)

✅ **사용 가능**:
- 모의 메일 데이터 로드
- 규칙 기반 요약 생성
- UI 테스트
- 삭제 기능

❌ **미지원**:
- Gemini AI 분석 (규칙 기반 사용)
- 실제 네이버 메일 수집

---

### 시나리오 B: Gemini API 키로 AI 분석 활성화

#### Step 1: API 키 획득
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. "Get API key" 클릭
3. 새로운 프로젝트 생성 및 키 발급

#### Step 2: .env 파일 설정
```env
GEMINI_API_KEY=sk-proj-xxxxxxxxxxxx
```

#### Step 3: 서버 재시작
```powershell
.\run.ps1
```

이제 "메일 수집 및 분석" 버튼을 클릭하면 Gemini AI가 요약을 생성합니다!

---

### 시나리오 C: 실제 네이버 메일 수집

#### Step 1: Chrome 원격 디버깅 활성화

**Windows**:
```powershell
# PowerShell 관리자 권한에서 실행
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**macOS**:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

#### Step 2: 네이버 메일 로그인
- 열린 Chrome 윈도우에서 https://mail.naver.com 방문
- 계정으로 로그인

#### Step 3: Flask 서버 실행
```powershell
.\run.ps1
```

#### Step 4: 웹에서 "메일 수집 및 분석" 클릭
- 현재 열린 메일함에서 자동으로 메일 수집
- 각 메일을 분석하여 요약 생성

---

## 🔍 문제 해결

### "Chrome 연결 실패" 오류
```
Chrome 연결 실패: ... Mock 데이터로 대체합니다.
```

**해결책**:
1. Chrome 원격 디버깅 포트가 9222로 열려있는지 확인
2. Chrome 윈도우가 https://mail.naver.com에 로그인되어 있는지 확인
3. 포트가 다른 프로세스에서 사용 중이 아닌지 확인

```powershell
# 포트 9222 사용 프로세스 확인
netstat -ano | findstr :9222
```

---

### "Gemini API 오류" 발생
```
Gemini 호출 실패: ...
```

**해결책**:
1. API 키가 유효한지 확인
2. API 키가 .env 파일에 올바르게 설정되었는지 확인
3. 일일 쿼터 초과 여부 확인
4. 토큰 부족 시 규칙 기반 요약이 자동으로 사용됨

---

### "포트 5000 사용 중" 오류
```
Address already in use
```

**해결책 1**: 기존 프로세스 종료
```powershell
# 포트 5000을 사용하는 프로세스 찾기
netstat -ano | findstr :5000

# 프로세스 ID(PID)로 종료
taskkill /PID [PID] /F
```

**해결책 2**: 다른 포트 사용
```powershell
# app.py 마지막 줄 수정:
app.run(port=5001, debug=True)
```

---

## 📊 프로젝트 구조

```
CHIN-DAY-2/
├── 📄 README.md              # 사용자 가이드
├── 🤖 CLAUDE.md              # 에이전트 작업 가이드
├── 🎯 SOUL.md                # 철학 및 원칙
├── 🏗️ SETUP.md               # 이 파일
├── 🔐 SECURITY.md            # 보안 가이드
│
├── 💻 app.py                 # Flask 메인 서버
├── 🕷️ crawler.py             # Selenium 크롤러
├── 🤖 summarizer.py          # Gemini AI 분석
├── 🎨 templates/index.html   # 웹 UI
│
├── ⚙️ requirements.txt        # 의존성
├── 📝 .env.example           # 환경변수 템플릿
├── 📝 .env                   # 환경변수 (실제)
├── 🔧 run.ps1               # 실행 스크립트
│
└── venv/                    # 가상환경 (자동 생성)
```

---

## 🧪 테스트

### 모의 데이터로 기능 테스트

```bash
# 1. 서버 시작
.\run.ps1

# 2. 브라우저 방문
# http://localhost:5000

# 3. "메일 수집 및 분석" 클릭
# → 5개의 모의 메일이 로드되고 분석됨

# 4. 각 메일:
#   - 체크박스로 선택 가능
#   - "선택 메일 삭제" 버튼으로 삭제 가능
#   - 요약, 우선순위, 카테고리 표시
```

---

## 📚 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 메인 웹 페이지 |
| POST | `/api/fetch-mails` | 메일 수집 및 분석 |
| POST | `/api/delete-emails` | 메일 삭제 |
| GET | `/api/get-settings` | 현재 설정 조회 |
| POST | `/api/save-settings` | 설정 저장 |

---

## 🎓 다음 단계

1. ✅ [기본 설정](SETUP.md) (현재)
2. 📖 [사용자 가이드](README.md)
3. 🤖 [에이전트 가이드](CLAUDE.md)
4. 🎯 [철학 및 원칙](SOUL.md)

---

**문제가 있으신가요?** [Issues](https://github.com/bwchin98-bot/CHIN-DAY-2/issues)에서 보고해주세요!

마지막 업데이트: 2026-06-12
