# 🔒 보안 설정 가이드

## API Key 보호

이 프로젝트는 민감한 정보(Gemini API Key, 이메일 계정)를 안전하게 보호합니다.

### ✅ 이미 설정된 보안

- `config.json` → `.gitignore`에 포함되어 GitHub에 업로드 안 됨
- Initial commit에 민감한 정보 미포함

### 🚀 권장사항: 환경 변수 사용

#### **Step 1: .env 파일 생성**

프로젝트 루트에 `.env` 파일 생성:

```
GEMINI_API_KEY=your_actual_api_key_here
EMAIL_SERVICE=naver
EMAIL_ID=your_email@naver.com
EMAIL_PW=your_password_here
```

#### **Step 2: 설치**

```bash
pip install python-dotenv
```

#### **Step 3: 확인**

`.gitignore`에 `.env` 포함되어 있는지 확인:

```
.env
config.json
```

### 📝 주의사항

1. **절대 .env를 Git에 커밋하지 마세요**
   ```bash
   git status  # .env가 리스트에 없어야 함
   ```

2. **이미 커밋된 민감한 정보 제거**
   ```bash
   git rm --cached config.json
   git commit -m "Remove config.json from tracking"
   git push
   ```

3. **GitHub 노출 확인**
   - https://github.com/YOUR_USERNAME/YOUR_REPO/settings/security
   - Dependabot alerts 모니터링

### 🔄 동작 방식

```
.env (환경 변수)
     ↓
config.json (대체 저장소) ← 환경 변수로 덮어씀
     ↓
코드 사용
```

환경 변수가 있으면 우선 사용, 없으면 `config.json` 사용 (호환성)
