# 🚀 네이버 메일 AI 자동화 요약

네이버 메일의 읽지 않은 메일을 자동으로 수집하고, Google Gemini AI로 분석하여 핵심 내용을 요약하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- **이메일 자동 수집** - 크롬 디버깅 포트를 통해 네이버 메일 실시간 접근
- **AI 요약 분석** - Google Gemini 2.5 Flash 모델로 2-3문장 상세 요약
- **메일 본문 추출** - 제목뿐 아니라 본문까지 포함한 정확한 분석
- **실시간 진행률 표시** - 처리 중인 메일의 진행 상황 실시간 모니터링
- **선택 삭제 기능** - 불필요한 메일 체크박스로 선택 후 일괄 삭제
- **환경변수 보안** - API 키를 .env 파일로 안전하게 관리
- **모의 데이터 지원** - 테스트용 샘플 메일로 API 없이도 기능 확인 가능

## 🎯 5분 시작 가이드

### 1️⃣ 설치

```bash
# 저장소 복제
git clone https://github.com/bwchin98-bot/CHIN-DAY-2.git
cd CHIN-DAY-2

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ 설정

```bash
# .env 파일 생성 (옵션: Gemini API 키 있을 때)
cp .env.example .env
# .env 파일에 다음 입력:
# GEMINI_API_KEY=your_api_key_here
```

### 3️⃣ 실행

```bash
# Flask 서버 시작
python app.py

# 브라우저에서 열기
# http://localhost:5000
```

### 4️⃣ 사용

1. 브라우저에서 "메일 수집 및 분석" 버튼 클릭
2. 모의 데이터가 로드되고 AI 분석 시작
3. 각 메일의 요약, 우선순위, 카테고리 확인
4. 필요시 체크박스로 메일 선택 후 "선택 메일 삭제" 버튼 클릭

## 🔌 실제 네이버 메일 연동

네이버 메일을 직접 사용하려면:

1. **Chrome 원격 디버깅 활성화**
   ```bash
   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   
   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   ```

2. **네이버 메일 로그인**
   - 열린 브라우저에서 https://mail.naver.com 접속
   - 계정으로 로그인

3. **Flask 서버에서 메일 수집**
   - "메일 수집 및 분석" 버튼 클릭
   - 자동으로 현재 열린 메일함에서 메일을 가져옴

## 🛠️ 기술 스택

| 계층 | 기술 | 역할 |
|------|------|------|
| **백엔드** | Flask, Python | REST API 서버 |
| **크롤러** | Selenium, WebDriver | 메일 수집 및 자동화 |
| **AI** | Google Gemini 2.5 Flash | 이메일 분석 및 요약 |
| **프론트엔드** | HTML, CSS, Vanilla JS | 사용자 인터페이스 |
| **설정** | python-dotenv | 환경변수 관리 |

## 📁 프로젝트 구조

```
CHIN-DAY-2/
├── app.py                    # Flask REST API 서버
├── crawler.py                # Selenium 기반 메일 수집기
├── summarizer.py             # Gemini AI 요약 엔진
├── requirements.txt          # Python 의존성
├── .env.example              # 환경변수 템플릿
├── config.json              # 설정 파일 (실제 API 키 저장)
├── templates/
│   └── index.html           # 웹 UI
├── README.md                # 사용자 가이드 (이 파일)
├── CLAUDE.md                # 에이전트 작업 가이드
├── SOUL.md                  # 기여 철학 가이드
└── SECURITY.md              # 보안 관련 가이드
```

## 🔐 보안 주의사항

- **API 키 보호** - `config.json`과 `.env`는 `.gitignore`에 포함되어 GitHub에 올라가지 않음
- **환경변수 우선** - `.env` 파일의 설정이 `config.json`보다 우선 적용
- **패스워드 마스킹** - API 응답에서 메일 비밀번호는 `********`로 마스킹됨

자세한 내용은 [SECURITY.md](SECURITY.md) 참고

## 🎓 API 엔드포인트

### GET `/` 
메인 웹 페이지 반환

### POST `/api/fetch-mails`
메일 수집 및 AI 분석 실행
- **응답**: 분석된 메일 목록 (요약, 우선순위, 카테고리 포함)

### POST `/api/delete-emails`
선택한 메일 삭제
- **요청**: `{"indices": [0, 2, 5]}`
- **응답**: 삭제 완료 상태

### GET `/api/get-settings`
현재 설정 조회 (패스워드는 마스킹됨)

### POST `/api/save-settings`
설정 저장
- **요청**: `{"GEMINI_API_KEY": "...", "EMAIL_ID": "...", ...}`

## 🐛 문제 해결

### "Chrome 연결 실패"
→ 원격 디버깅 포트(9222)가 열려있는지 확인하세요

### "Gemini API 오류"
→ API 키가 유효한지, .env 파일에 올바르게 설정되어 있는지 확인하세요

### "메일 수집 안 됨"
→ 모의 데이터로 기능 테스트를 먼저 진행한 후, 실제 네이버 메일 연동을 시도하세요

## 📧 문의

문제나 제안사항이 있으시면 [Issues](https://github.com/bwchin98-bot/CHIN-DAY-2/issues)에서 등록해주세요.

---

**버전**: 1.0.0 | **마지막 업데이트**: 2026-06-12
