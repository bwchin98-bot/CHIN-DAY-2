# 🎯 SOUL.md - 기여 철학 및 설계 원칙

본 문서는 이 프로젝트의 영혼(철학), 설계 원칙, 그리고 미래 기여자들이 따라야 할 방향성을 명시합니다.

## 🌟 프로젝트 철학

### "정보의 과부하를 생산성으로 변환"

현대인은 매일 수십 개의 이메일을 받습니다. 대부분 읽지 않은 채 쌓입니다. 

**이 프로젝트의 목표**는:
- ✅ 중요한 것만 빠르게 파악
- ✅ 초인적 집중력 없이 판단하기
- ✅ AI를 "참조자" 아닌 "어시스턴트"로 활용

즉, **사용자가 메일을 읽는 시간을 60%까지 줄이기**가 핵심입니다.

## 🏗️ 설계 원칙

### 1️⃣ **"Simple is Beautiful"**

```
❌ 하지 말 것: 설정 화면, 플러그인 시스템, 템플릿 엔진
✅ 대신: 한 번의 클릭으로 작동, 환경변수로 설정, 폴백 지원
```

**이유**: 사용자는 메일을 정리하는 데 시간을 쓰고 싶지, 도구를 학습하고 싶지 않습니다.

**실천 예**:
- 모의 데이터로 API 없이도 기능 확인
- 불가능한 것보다 "작동하지만 완벽하지 않은 것" 선호
- 에러 메시지는 명확하고 실행 가능하게

### 2️⃣ **"Graceful Degradation (우아한 성능 저하)"**

```
계층화된 폴백 전략:
1) Chrome + Naver 로그인 성공 → 실제 메일 수집
2) Chrome 실패 → 모의 데이터로 기능 시연
3) Gemini API 실패 → 규칙 기반 요약
4) 모든 것 실패 → 사용자에게 명확한 안내
```

**의미**: 한 부분이 고장 나도 전체 시스템이 멈추지 않습니다.

**적용 예**:
- API 키 없어도 웹사이트 열림 (모의 데이터 제공)
- 네이버 메일 선택자 변경되어도 작동 (Selenium 폴백)
- Gemini 토큰 초과해도 기본 요약 제공

### 3️⃣ **"Transparency First (투명성 우선)"**

```
사용자는 항상 알아야 한다:
- 지금 뭐 하고 있는 건지 (진행률 표시)
- 정보가 실제인지 가짜인지 (is_mock_ai 플래그)
- 뭔가 잘못되면 왜인지 (에러 메시지)
```

**구현**:
- 실시간 진행률 표시 (처리 중인 메일 제목)
- JSON 응답에 `is_mock_ai` 플래그 포함
- 에러 발생 시 원인과 해결책 제시

### 4️⃣ **"One Tool, One Job"**

각 모듈은 정확히 하나의 책임만 가집니다:

| 모듈 | 책임 | 범위 |
|------|------|------|
| **app.py** | REST API 계층 | 요청-응답만 |
| **crawler.py** | 데이터 수집 | 웹 자동화만 |
| **summarizer.py** | AI 분석 | Gemini 상호작용만 |
| **index.html** | 사용자 인터페이스 | UI 렌더링만 |

**좋은 예**: `app.py`에서 Selenium 코드를 `crawler.py`로 분리
**나쁜 예**: `app.py`에 크롤링, 요약, 템플릿 렌더링 모두 포함

### 5️⃣ **"Configuration ≠ Code"**

```
설정 우선순위:
1️⃣ 환경변수 (.env)
2️⃣ 설정 파일 (config.json)
3️⃣ 기본값

규칙:
✅ 정보 보안이 필요한가? → .env (커밋 불가)
✅ 개발 중 자주 변경? → .env.example (템플릿만)
✅ 기술적 상수? → 코드 내 하드코딩 (예: Gemini 모델명)
```

**나쁜 코드**:
```python
API_KEY = "sk-123456789"  # 하드코딩 금지!
```

**좋은 코드**:
```python
api_key = os.getenv("GEMINI_API_KEY", "")
# 또는
api_key = config.get("GEMINI_API_KEY", "")
```

## 🎓 설계 결정과 그 이유들

### "왜 Chrome 원격 디버깅 포트를 사용하나?"

**선택지**:
1. Selenium으로 브라우저 새로 열기 → CAPTCHA 차단, 2FA 복잡
2. Selenium으로 기존 Chrome에 연결 → 이미 로그인된 상태에서 자동화

**결정**: 2번 선택 (Chrome 원격 디버깅)

**이유**: 
- 사용자가 이미 메일함에 로그인해있으므로 재인증 불필요
- 크롤링 감지 우회 가능

### "왜 Google Gemini를 선택했나?"

**선택지**:
1. OpenAI GPT → 비싸고, 프리 티어 제한 많음
2. 오픈소스 LLM → 로컬 설치 복잡, 리소스 많음
3. Google Gemini → 무료 티어 충분, API 간단

**결정**: 3번 선택 (Gemini)

**이유**: 
- 개인 프로젝트에서 비용 우려 없음
- "Flash" 모델로 빠른 응답 (3~5초)
- JSON 응답 안정적

### "왜 모의 데이터를 기본으로 제공하나?"

**선택지**:
1. 항상 실제 메일 크롤링 필요 → 네이버 계정 필수
2. API 키 필수 → Gemini 세팅 강요
3. 모의 데이터 기본 제공 → 누구나 5분 안에 시작

**결정**: 3번 선택 (모의 데이터)

**이유**: 
- 기여자가 쉽게 로컬 환경에서 개발 가능
- 사용자가 설정 없이 기능 확인 가능
- 테스트 무한 반복 가능

## 🚀 확장 로드맵 (미래 기여자를 위한 방향성)

### Phase 1: 단일 제공자 (현재 ✅)
- 네이버 메일만 지원
- 단순한 웹 UI

### Phase 2: 다중 제공자 (설계 준비됨)
```python
# 향후 구현 예상:
class EmailServiceFactory:
    @staticmethod
    def create(service_type: str):
        if service_type == "naver":
            return NaverEmailService()
        elif service_type == "gmail":
            return GmailEmailService()
```

**파일 추가**: 
- `services/email_service.py` (추상 인터페이스)
- `services/naver_service.py` (현 crawler.py 리팩토링)
- `services/gmail_service.py` (새 구현)

### Phase 3: 스마트 필터링
```
현재: "요약만 제공"
미래: "패턴 학습 (3주 사용 후 중요도 자동 판정)"
```

**구현**: 사용자 행동 기록 (클릭, 삭제, 회신) → 개인화 랭킹

### Phase 4: 크로스 플랫폼 앱
```
웹 → Desktop (Electron) → Mobile (React Native)
```

## 📋 기여 가이드라인

### "좋은 기여란?"

✅ **해도 좋은 것**:
- 기존 선택자 개선 (Naver UI 변경 대응)
- 다른 이메일 서비스 추가 (Gmail, Outlook)
- 폴백 요약 규칙 개선
- 문서 한국화/영문화
- 테스트 코드 추가
- 성능 최적화 (응답 시간 단축)

❌ **하면 안 되는 것**:
- 핵심 철학 무시 (복잡도 추가)
- 설정 파일 git 커밋
- 하드코딩된 매직 넘버
- API 키 로그 출력
- 사용자 입력 검증 없음

### 커밋 메시지 컨벤션

```
feat: 새 기능 추가 (예: feat: Gmail 지원 추가)
fix: 버그 수정 (예: fix: 무한 스크롤 선택자 업데이트)
docs: 문서 추가/수정 (예: docs: 설치 가이드 작성)
refactor: 코드 구조 개선 (예: refactor: crawler.py 모듈화)
test: 테스트 추가 (예: test: 모의 데이터 검증)
```

**좋은 예**:
```
feat: Add graceful fallback for Gemini API failures

- When API fails, use rule-based summary instead
- Log warning with clear error message
- Maintain response format consistency
```

**나쁜 예**:
```
update code
fix stuff
```

## 🤝 코드 리뷰 체크리스트

PR을 열기 전에:

- [ ] 철학과 원칙을 따랐는가?
- [ ] 하나의 책임만 하는가?
- [ ] 폴백 동작이 있는가?
- [ ] 에러 메시지가 명확한가?
- [ ] 새 설정 변수는 .env.example에 추가했는가?
- [ ] API 키가 로그에 노출되지 않는가?
- [ ] 모의 데이터로 테스트했는가?
- [ ] 문서를 업데이트했는가?

## 💡 자주 묻는 질문

### Q: "모의 데이터를 왜 하드코딩하나? 파일로 분리하면?"
**A**: 패키징 단순성. 의존성 줄이기. 사용자는 `get_mock_emails()`만 있으면 됨.

### Q: "지금 중국어/일본어는 지원 안 하나?"
**A**: 모의 데이터는 한국어지만, Gemini는 100+ 언어 지원. Naver는 한국 서비스이므로 우선순위 낮음.

### Q: "왜 WebSocket으로 실시간 스트리밍 안 하나?"
**A**: YAGNI. 폴링으로 충분. 복잡도 추가 가치 < 학습곡선.

### Q: "향후 모바일 앱도?"
**A**: 로드맵에는 있으나, 우선 웹에서 완벽하게.

---

## 📞 연락 및 문의

- **버그 리포트**: [Issues](https://github.com/bwchin98-bot/CHIN-DAY-2/issues)
- **기능 제안**: Discussions (커밍순)
- **직접 기여**: Pull Request (가이드라인 확인 후)

---

**이 문서는 살아있는 문서입니다.** 경험에 따라 진화합니다.

마지막 업데이트: 2026-06-12
