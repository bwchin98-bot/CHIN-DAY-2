# 🤖 CLAUDE.md - 에이전트 작업 가이드

본 문서는 Claude 에이전트가 이 프로젝트에서 작업할 때 따라야 할 구조와 운영 규칙을 명시합니다.

## 📊 핵심 아키텍처

### 계층 구조

```
┌─────────────────────────────────┐
│   Frontend (HTML/CSS/JS)        │
│   templates/index.html          │
└──────────────┬──────────────────┘
               │ HTTP REST
┌──────────────▼──────────────────┐
│  Flask Backend (app.py)         │
│  • Route handlers               │
│  • Config management            │
│  • Progress tracking            │
└──────────┬──────────────┬───────┘
           │              │
    ┌──────▼──┐    ┌──────▼──────┐
    │ Crawler │    │ Summarizer  │
    │(Selenium)   │ (Gemini API)│
    └────────────  └─────────────┘
```

### 파일 책임 분담

| 파일 | 책임 | 주요 함수/엔드포인트 |
|------|------|-------------------|
| **app.py** | 웹 서버, 요청 처리, 설정 관리 | `fetch_mails()`, `delete_emails()`, `load_config()` |
| **crawler.py** | 메일 수집, 무한 스크롤 | `EmailCrawler.fetch_naver_emails()`, `get_mock_emails()` |
| **summarizer.py** | AI 분석, 폴백 요약 | `summarize_email()`, `generate_fallback_summary()` |
| **config.json** | 보안 설정 저장소 | `GEMINI_API_KEY`, `EMAIL_ID`, `EMAIL_PW` |
| **.env** | 환경변수 (우선순위 높음) | 모든 설정 키 |
| **index.html** | 웹 UI, 사용자 상호작용 | 체크박스, 진행률 표시, 삭제 버튼 |

## 🔄 데이터 흐름

### 메일 수집 → 분석 → 표시 파이프라인

```
[사용자 클릭]
    ↓
[Flask /api/fetch-mails]
    ↓
┌─ Chrome 디버깅 포트 연결 시도
│  ├─ 성공 → fetch_naver_emails() (실제 메일)
│  └─ 실패 → get_mock_emails() (모의 데이터)
    ↓
[emails_to_analyze: {subject, body}[]]
    ↓
┌─ Gemini API 가능?
│  ├─ Yes → client.models.generate_content() (AI 분석)
│  └─ No  → get_fallback_ai_analysis() (규칙 기반)
    ↓
[processed_data: {title, summary, action, priority, category}[]]
    ↓
[JSON 응답 + 진행률]
    ↓
[Frontend: 카드 렌더링 + 체크박스]
```

## 🛠️ 주요 인터페이스

### Config 로딩 규칙 (app.py:17-35, crawler.py:15-33)

```python
def load_config():
    config = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),  # .env 우선
        "EMAIL_SERVICE": os.getenv("EMAIL_SERVICE", "naver"),
        "EMAIL_ID": os.getenv("EMAIL_ID", ""),
        "EMAIL_PW": os.getenv("EMAIL_PW", "")
    }
    
    # .env에 없으면 config.json 폴백
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            file_config = json.load(f)
            for key in config:
                if not config[key] and file_config.get(key):
                    config[key] = file_config[key]
    
    return config
```

**우선순위**: `os.getenv()` → `config.json` → 기본값

### AI 분석 프롬프트 구조 (app.py:179-193)

```
입력:
  - 이메일 제목: "{title}"
  - 이메일 본문: "{body}"

출력 JSON 스키마:
{
  "summary": "2-3문장 상세 요약 (발신자, 주요 내용, 요청사항)",
  "action": "3~5단어 액션 항목",
  "priority": "High | Medium | Low",
  "category": "업무 | 공지 | 결제 | 보안 | 기타"
}
```

### 무한 스크롤 로직 (crawler.py:119-147)

```python
# 스크롤 반복: 새 메일이 로드되지 않을 때까지
prev_count = 0
while scroll_attempts < max_attempts:
    mail_items = driver.find_elements(...)
    current_count = len(mail_items)
    
    if current_count == prev_count:  # 더 이상 로드 안 됨
        break
    
    prev_count = current_count
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
```

## 📡 API 응답 포맷

### /api/fetch-mails 응답

```json
{
  "status": "success",
  "data": [
    {
      "idx": 1,
      "title": "이메일 제목",
      "summary": "AI 요약 텍스트",
      "action": "액션 항목",
      "priority": "High",
      "category": "업무"
    }
  ],
  "is_mock_ai": false,
  "progress": {
    "current": 5,
    "total": 5
  }
}
```

### /api/delete-emails 요청/응답

```
POST /api/delete-emails
요청: {"indices": [0, 2, 3]}

응답:
{
  "status": "success",
  "message": "3개 메일이 삭제되었습니다.",
  "deleted_count": 3
}
```

## 🔍 설정 관리 엔드포인트

### GET /api/get-settings
```json
{
  "GEMINI_API_KEY": "",
  "EMAIL_SERVICE": "naver",
  "EMAIL_ID": "",
  "EMAIL_PW": "********"  // 항상 마스킹
}
```

### POST /api/save-settings
```json
요청:
{
  "GEMINI_API_KEY": "sk-...",
  "EMAIL_ID": "user@naver.com",
  "EMAIL_PW": "password123"
}

응답:
{
  "status": "success",
  "message": "설정이 성공적으로 저장되었습니다."
}
```

## 🎯 에이전트 작업 시 주의사항

### ✅ 하면 좋은 것

1. **설정 흐름 존중** - 항상 `.env` 먼저, 그 다음 `config.json` 폴백
2. **타입 일관성** - `emails_to_analyze`는 항상 `{subject, body}` 딕셔너리 배열
3. **진행률 추적** - 처리 중인 각 메일마다 로그 출력
4. **폴백 지원** - API 실패 시 자동으로 규칙 기반 분석 사용
5. **무한 스크롤 지원** - 페이지네이션 없이 모든 메일 로드

### ❌ 하면 안 되는 것

1. ⛔ 하드코딩된 선택자 사용 (Naver UI는 자주 변경됨)
2. ⛔ 패스워드를 로그에 출력
3. ⛔ 설정을 git에 커밋 (.gitignore 확인)
4. ⛔ 동기식 `time.sleep()` 남용 (선택적만 사용)
5. ⛔ API 키 검증 없이 Gemini 초기화

## 📝 작업 체크리스트

새 기능을 추가할 때:

- [ ] 파일 책임 분담 확인 (어느 파일에서 처리?)
- [ ] 설정 흐름에 맞게 구현 (load_config 사용)
- [ ] 폴백 동작 구현 (API 없을 때)
- [ ] 에러 핸들링 추가 (try-except)
- [ ] 진행률 로그 출력
- [ ] API 응답 구조 검증
- [ ] 테스트 (모의 데이터, 실제 API)
- [ ] Git 커밋 (명확한 메시지)

## 🔐 보안 검사표

- [ ] API 키가 `.gitignore`에 포함?
- [ ] 패스워드가 로그에 출력되지 않음?
- [ ] `.env.example` 파일이 최신?
- [ ] 응답에서 민감한 정보 마스킹?
- [ ] config.json이 git에 tracked 아님?

## 📚 참고 파일

| 파일 | 용도 |
|------|------|
| [SOUL.md](SOUL.md) | 철학 및 설계 원칙 |
| [SECURITY.md](SECURITY.md) | 보안 설정 상세 |
| [.env.example](.env.example) | 환경변수 템플릿 |
| [requirements.txt](requirements.txt) | 의존성 목록 |

---

**마지막 업데이트**: 2026-06-12
