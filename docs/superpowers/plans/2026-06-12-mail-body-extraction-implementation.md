# 메일 본문 추출 & 수동 삭제 기능 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 메일 본문을 포함해서 분석하고, 사용자가 불필요한 메일을 수동으로 삭제할 수 있도록 구현

**Architecture:** 
- Backend: Chrome 디버깅 포트에서 모든 메일을 스크롤하고, 각 메일을 클릭해서 본문 추출 후 AI 분석
- Frontend: 진행률 실시간 표시 → 완성된 목록에서 사용자가 삭제 선택
- 로컬 상태로만 관리 (메일 자체는 Naver에서 읽음 표시)

**Tech Stack:** Python (Selenium, Flask), JavaScript (Vanilla), Google Gemini API

---

## Task 1: Backend - 메일 목록 전체 스크롤 기능

**Files:**
- Modify: `app.py` (fetch_mails 함수)
- Modify: `crawler.py` (fetch_naver_emails 메서드)

- [ ] **Step 1: 현재 fetch_naver_emails 구조 분석**

파일 읽기: `crawler.py:119-190`
- 현재: 상위 N개만 제한
- 변경: 페이지 끝까지 스크롤하는 로직 추가

- [ ] **Step 2: 스크롤 로직 작성**

`crawler.py`의 `fetch_naver_emails` 메서드 수정:

```python
def fetch_naver_emails(self, limit=None):  # limit=None → 전체
    """네이버 메일함에서 모든 메일 가져오기"""
    emails = []
    try:
        self.driver.get("https://mail.naver.com/")
        time.sleep(3)
        
        # 무한 스크롤 처리
        prev_count = 0
        scroll_attempts = 0
        max_attempts = 50  # 스크롤 횟수 제한
        
        while scroll_attempts < max_attempts:
            # 메일 목록 찾기
            mail_items = self.driver.find_elements(By.CSS_SELECTOR, "ol.mail_list > li")
            if not mail_items:
                mail_items = self.driver.find_elements(By.CSS_SELECTOR, "div.mailList > div.mItem")
            
            current_count = len(mail_items)
            
            # 더 이상 로드 안 되면 멈춤
            if current_count == prev_count:
                break
            
            prev_count = current_count
            
            # 페이지 끝으로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            scroll_attempts += 1
        
        # 이후 메일 추출은 기존 로직 유지
        count = current_count if limit is None else min(current_count, limit)
        # ... 기존 추출 로직 ...
        
        return emails
    except Exception as e:
        raise Exception(f"메일 목록 파싱 중 에러: {e}")
```

- [ ] **Step 3: app.py에서 limit 파라미터 제거**

`app.py`의 `fetch_mails` 함수 수정:

```python
# 기존
raw_titles = [email["subject"] for email in mock_data[:5]]

# 변경
raw_titles = [email["subject"] for email in mock_data]  # 전체 사용
```

- [ ] **Step 4: 테스트 - 메일 스크롤 확인**

실제 환경에서 다음 확인:
- Chrome 원격 디버깅 활성화
- Naver 메일 로그인
- "이메일 자동 확인 시작" 클릭
- 콘솔 로그에서 스크롤 진행 확인

- [ ] **Step 5: 커밋**

```bash
git add crawler.py app.py
git commit -m "feat: Add infinite scroll to fetch all emails instead of top 5"
```

---

## Task 2: Backend - 메일 본문 추출 & 진행률 정보 추가

**Files:**
- Modify: `app.py` (fetch_mails 엔드포인트)

- [ ] **Step 1: 진행률 구조 설계**

API 응답 형식:

```python
{
    "status": "loading",  # loading, success, error
    "progress": {
        "current": 5,
        "total": 32,
        "current_mail_subject": "[긴급] 상반기 매출..."
    },
    "data": [...]  # 완료된 메일들
}
```

- [ ] **Step 2: 본문 추출 로직 수정**

`app.py`의 `fetch_mails` 함수 수정 (현재 코드 교체):

```python
# 현재 코드 (제목만 추출)
if not driver:
    from crawler import get_mock_emails
    mock_data = get_mock_emails()
    raw_titles = [email["subject"] for email in mock_data]
else:
    # ... Selenium으로 제목만 추출 ...

# 변경 (본문도 함께)
if not driver:
    from crawler import get_mock_emails
    mock_data = get_mock_emails()
    emails_to_analyze = mock_data  # 전체 데이터 (제목 + 본문)
else:
    # Selenium으로 메일 객체 추출 (제목 + 본문)
    emails_to_analyze = [
        {
            "subject": title,
            "body": body  # 본문도 포함
        }
        for title, body in extracted_data
    ]
```

- [ ] **Step 3: 진행률 정보 반환 로직**

`app.py`의 분석 루프 수정:

```python
processed_data = []
total_emails = len(emails_to_analyze)

for i, email_data in enumerate(emails_to_analyze, 1):
    title = email_data.get("subject", "")
    body = email_data.get("body", "")
    
    summary = "요약 정보를 추출할 수 없습니다."
    action = "확인 필요"
    priority = "Medium"
    category = "일반"
    
    if use_gemini:
        # 프롬프트에 본문도 포함
        prompt = f"""
당신은 사내 업무를 돕는 AI 비서입니다. 아래의 이메일을 분석하여 다음 정보를 JSON 형식으로만 응답해 주세요.

출력 JSON 포맷:
{{
  "summary": "메일의 핵심 맥락 1줄 요약",
  "action": "메일 수신자가 취해야 할 행동 (3~5단어)",
  "priority": "High" | "Medium" | "Low",
  "category": "업무" | "공지" | "결제" | "보안" | "기타"
}}

이메일 제목: "{title}"
이메일 본문:
{body}
"""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            # ... JSON 파싱 ...
    
    processed_data.append({
        "idx": i,
        "title": title,
        "summary": summary,
        "action": action,
        "priority": priority,
        "category": category
    })
    
    # 진행률 콘솔 로그 (UI는 Step 5에서)
    print(f"Progress: {i}/{total_emails} - {title[:30]}...")

return jsonify({
    "status": "success",
    "data": processed_data,
    "is_mock_ai": not use_gemini,
    "progress": {
        "current": total_emails,
        "total": total_emails
    }
})
```

- [ ] **Step 4: 읽음 표시 로직 추가**

메일을 분석한 후 Naver에서 읽음 표시하는 로직:

```python
# 각 메일 분석 후
if driver:
    try:
        # 읽음 표시 처리 (Naver UI 구조에 따라)
        # 옵션 1: 체크박스 클릭
        # checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        # checkbox.click()
        
        # 옵션 2: 자동으로 로드되면 상태 유지
        pass  # 현재는 스킵 (Chrome 디버깅 모드에서는 자동으로 읽음 처리될 수 있음)
    except Exception as e:
        print(f"읽음 표시 실패: {e}")
```

- [ ] **Step 5: 테스트**

```bash
# Mock 데이터로 테스트
curl "http://localhost:5000/api/fetch-mails"

# 응답에 본문이 포함되었는지 확인
# "progress" 정보가 있는지 확인
```

- [ ] **Step 6: 커밋**

```bash
git add app.py
git commit -m "feat: Include email body in analysis and add progress tracking"
```

---

## Task 3: Backend - 삭제 API 엔드포인트

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 삭제 엔드포인트 작성**

`app.py`에 새 엔드포인트 추가:

```python
@app.route('/api/delete-emails', methods=['POST'])
def delete_emails():
    """사용자가 선택한 메일을 삭제 (로컬 상태 관리)"""
    data = request.json
    email_indices = data.get("indices", [])  # [1, 3, 5] 형태
    
    # 현재: 로컬 상태로만 관리 (프론트에서 UI에서 제거)
    # 향후: 데이터베이스에 "숨김" 상태 저장 가능
    
    return jsonify({
        "status": "success",
        "message": f"{len(email_indices)}개 메일이 삭제되었습니다.",
        "deleted_count": len(email_indices)
    })
```

- [ ] **Step 2: 테스트**

```bash
curl -X POST http://localhost:5000/api/delete-emails \
  -H "Content-Type: application/json" \
  -d '{"indices": [1, 2, 3]}'

# 응답 확인: {"status": "success", "deleted_count": 3}
```

- [ ] **Step 3: 커밋**

```bash
git add app.py
git commit -m "feat: Add DELETE endpoint for manual email deletion"
```

---

## Task 4: Frontend - 진행률 UI 업데이트

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: 진행률 표시 HTML 추가**

`templates/index.html`에서 로더 섹션 수정:

```html
<!-- 기존 로더 -->
<div id="loader" class="loader-wrapper">
    <div class="spinner"></div>
    <p class="fw-bold" style="color: var(--accent-primary);">원격 디버깅 크롬 세션에 연결하여 분석하는 중입니다...</p>
</div>

<!-- 변경: 진행률 정보 추가 -->
<div id="loader" class="loader-wrapper">
    <div class="spinner"></div>
    <p class="fw-bold" style="color: var(--accent-primary);">
        메일 분석 중입니다...
    </p>
    <div id="progressInfo" style="margin-top: 16px; text-align: center; color: var(--text-muted); font-size: 14px;">
        <p id="progressText">0/0</p>
        <p id="currentMailText" style="margin-top: 8px; font-size: 12px; max-width: 400px; word-break: break-word;"></p>
    </div>
</div>
```

- [ ] **Step 2: JavaScript에서 진행률 처리**

`templates/index.html`의 `startScraping` 함수 수정:

```javascript
function startScraping() {
    const runBtn = document.getElementById("runBtn");
    const loader = document.getElementById("loader");
    const container = document.getElementById("emailContainer");
    const mockBadge = document.getElementById("mockBadge");
    const targetUrl = document.getElementById("targetUrlInput").value;

    runBtn.disabled = true;
    loader.style.display = "flex";
    mockBadge.style.display = "none";
    container.innerHTML = '';

    const urlParams = new URLSearchParams();
    if (targetUrl) {
        urlParams.append('url', targetUrl);
    }

    fetch(`/api/fetch-mails?${urlParams.toString()}`)
        .then(r => r.json())
        .then(res => {
            runBtn.disabled = false;
            loader.style.display = "none";

            if (res.status === 'success') {
                if (res.is_mock_ai) {
                    mockBadge.style.display = 'inline-block';
                }
                
                if (res.data.length === 0) {
                    container.innerHTML = `
                        <div class="no-data">
                            <i class="bi bi-envelope-open"></i>
                            <p>${res.message || '현재 열려있는 메일함 화면에서 이메일을 찾지 못했습니다.'}</p>
                        </div>
                    `;
                } else {
                    let cardsHtml = '';
                    res.data.forEach(mail => {
                        const priorityClass = `badge-priority-${mail.priority.toLowerCase()}`;
                        cardsHtml += `
                            <div class="email-card">
                                <div class="email-idx-tag">${mail.idx}</div>
                                <div class="email-title-sec">
                                    <div class="email-title">${mail.title}</div>
                                    <div class="email-meta">
                                        <span class="badge ${priorityClass}">우선순위: ${mail.priority}</span>
                                        <span class="badge badge-category">${mail.category}</span>
                                    </div>
                                </div>
                                <div class="email-summary-sec">
                                    ${mail.summary}
                                </div>
                                <div class="email-action-sec">
                                    <div class="action-title">주요 요청행동</div>
                                    <div class="action-item">
                                        <i class="bi bi-exclamation-circle-fill"></i>
                                        <span>${mail.action}</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    container.innerHTML = cardsHtml;
                }
            } else {
                container.innerHTML = `
                    <div class="no-data">
                        <i class="bi bi-x-circle" style="color: var(--danger);"></i>
                        <p>수집 중 에러가 발생했습니다: ${res.message}</p>
                    </div>
                `;
            }
        })
        .catch(err => {
            runBtn.disabled = false;
            loader.style.display = "none";
            container.innerHTML = `
                <div class="no-data">
                    <i class="bi bi-cloud-slash"></i>
                    <p>서버 통신 실패 또는 타임아웃이 발생했습니다.</p>
                </div>
            `;
        });
}
```

- [ ] **Step 3: 테스트**

브라우저에서 버튼 클릭 → 메일 카드 표시 확인

- [ ] **Step 4: 커밋**

```bash
git add templates/index.html
git commit -m "feat: Update email card rendering with body content"
```

---

## Task 5: Frontend - 체크박스 & 삭제 버튼 UI

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: 이메일 카드에 체크박스 추가**

`templates/index.html`의 `startScraping` 함수 내 카드 렌더링 부분 수정:

```javascript
let cardsHtml = '';
res.data.forEach(mail => {
    const priorityClass = `badge-priority-${mail.priority.toLowerCase()}`;
    cardsHtml += `
        <div class="email-card" data-idx="${mail.idx}">
            <input type="checkbox" class="email-checkbox" data-idx="${mail.idx}" style="width: 18px; height: 18px; cursor: pointer; margin-right: 8px;">
            <div class="email-idx-tag">${mail.idx}</div>
            <div class="email-title-sec">
                <div class="email-title">${mail.title}</div>
                <div class="email-meta">
                    <span class="badge ${priorityClass}">우선순위: ${mail.priority}</span>
                    <span class="badge badge-category">${mail.category}</span>
                </div>
            </div>
            <div class="email-summary-sec">
                ${mail.summary}
            </div>
            <div class="email-action-sec">
                <div class="action-title">주요 요청행동</div>
                <div class="action-item">
                    <i class="bi bi-exclamation-circle-fill"></i>
                    <span>${mail.action}</span>
                </div>
            </div>
        </div>
    `;
});
container.innerHTML = cardsHtml;

// 체크박스 이벤트 리스너 추가
document.querySelectorAll('.email-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', updateSelectedCount);
});
```

- [ ] **Step 2: 삭제 버튼과 선택 카운트 추가**

`templates/index.html`의 section-header 수정:

```html
<div class="section-header">
    <div class="section-title">
        <i class="bi bi-collection-play-fill" style="color: var(--accent-primary);"></i>
        <span>실시간 수집 및 요약 분석 결과</span>
        <span id="mockBadge" class="mock-badge" style="display: none;">로컬 시뮬레이션 적용됨</span>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <span id="selectedCount" style="color: var(--text-muted); font-size: 14px;">선택됨: 0</span>
        <button id="deleteBtn" class="btn-premium" style="display: none; padding: 8px 16px; font-size: 14px;" onclick="deleteSelectedEmails()">
            <i class="bi bi-trash"></i>
            <span>삭제</span>
        </button>
    </div>
</div>
```

- [ ] **Step 3: 삭제 및 선택 카운트 함수 추가**

HTML의 `<script>` 섹션에 추가:

```javascript
function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.email-checkbox');
    const checked = document.querySelectorAll('.email-checkbox:checked');
    const deleteBtn = document.getElementById('deleteBtn');
    const selectedCount = document.getElementById('selectedCount');
    
    selectedCount.innerText = `선택됨: ${checked.length}/${checkboxes.length}`;
    deleteBtn.style.display = checked.length > 0 ? 'inline-flex' : 'none';
}

function deleteSelectedEmails() {
    const checkboxes = document.querySelectorAll('.email-checkbox:checked');
    const indices = Array.from(checkboxes).map(cb => parseInt(cb.dataset.idx));
    
    if (indices.length === 0) {
        alert('삭제할 메일을 선택해주세요.');
        return;
    }
    
    if (!confirm(`${indices.length}개의 메일을 삭제하시겠습니까?`)) {
        return;
    }
    
    fetch('/api/delete-emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ indices: indices })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            // UI에서 카드 제거
            indices.forEach(idx => {
                const card = document.querySelector(`[data-idx="${idx}"]`);
                if (card) card.remove();
            });
            
            // 선택 카운트 업데이트
            updateSelectedCount();
            
            alert(`${data.deleted_count}개 메일이 삭제되었습니다.`);
        }
    })
    .catch(err => alert('삭제 실패: ' + err.message));
}
```

- [ ] **Step 4: CSS 업데이트**

`templates/index.html`의 `<style>` 섹션에서 이메일 카드 스타일 수정:

```css
.email-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 20px;
    display: grid;
    grid-template-columns: 40px 80px 1fr 1fr 200px;
    gap: 20px;
    align-items: center;
    animation: fadeIn 0.4s ease forwards;
}

@media (max-width: 1024px) {
    .email-card {
        grid-template-columns: 40px 50px 1fr;
        gap: 16px;
    }
    .email-summary-sec, .email-action-sec {
        grid-column: span 3;
        border-top: 1px solid var(--border-color);
        padding-top: 12px;
    }
}
```

- [ ] **Step 5: 테스트**

1. 메일 분석 완료 후 체크박스 표시 확인
2. 체크박스 클릭 → "선택됨: X/Y" 업데이트 확인
3. 삭제 버튼 클릭 → 메일 제거 확인

- [ ] **Step 6: 커밋**

```bash
git add templates/index.html
git commit -m "feat: Add checkboxes and delete button for manual email removal"
```

---

**모든 Task 완료!** 

이제 최종 검증을 하겠습니다.
