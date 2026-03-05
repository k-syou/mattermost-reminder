# 로컬 개발 환경 설정 가이드

로컬에서 프론트엔드와 백엔드를 함께 개발하기 위한 설정 가이드입니다.

## 사전 준비

1. Python 3.11+ 설치
2. Node.js 18+ 설치
3. Firebase 프로젝트 설정 완료

## 로컬 개발 환경 실행

### 1. 백엔드 서버 실행

```bash
cd functions

# 가상환경 활성화 (Windows)
.\venv\Scripts\Activate.ps1

# 또는 가상환경이 없다면 생성
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 로컬 서버 실행
uvicorn main:app --reload --port 8000
```

백엔드 서버가 `http://localhost:8000`에서 실행됩니다.

### 2. 프론트엔드 개발 서버 실행

**새 터미널 창에서:**

```bash
cd frontend

# 환경 변수 설정 (선택사항)
# .env.local 파일 생성 또는 아래 명령어로 설정
# Windows PowerShell:
$env:VITE_API_BASE_URL=""
$env:VITE_FIREBASE_API_KEY="your_api_key"
$env:VITE_FIREBASE_AUTH_DOMAIN="your_project.firebaseapp.com"
$env:VITE_FIREBASE_PROJECT_ID="your_project_id"
$env:VITE_FIREBASE_STORAGE_BUCKET="your_project.appspot.com"
$env:VITE_FIREBASE_MESSAGING_SENDER_ID="your_sender_id"
$env:VITE_FIREBASE_APP_ID="your_app_id"

# 개발 서버 실행
npm run dev
```

프론트엔드가 `http://localhost:5173`에서 실행됩니다.

## 환경 변수 설정

### 프론트엔드 환경 변수

`frontend/.env.local` 파일 생성:

```env
# API Base URL (로컬 개발 시 빈 문자열 - Vite 프록시 사용)
VITE_API_BASE_URL=

# Firebase 설정
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

**중요:** `VITE_API_BASE_URL`을 빈 문자열로 설정하면 Vite 프록시가 자동으로 `/api` 요청을 `http://localhost:8000`으로 전달합니다.

### 백엔드 환경 변수

로컬 개발 시 `functions/serviceAccountKey.json` 파일이 필요합니다 (선택사항).

Firebase Functions에 배포된 경우에는 Application Default Credentials를 사용합니다.

## Vite 프록시 설정

`frontend/vite.config.ts`에 이미 프록시가 설정되어 있습니다:

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

이 설정으로 프론트엔드에서 `/api/*` 요청이 자동으로 `http://localhost:8000/api/*`로 프록시됩니다.

## 문제 해결

### 1. ECONNREFUSED 에러

**증상:**
```
http proxy error: /api/webhooks
AggregateError [ECONNREFUSED]
```

**해결:**
- 백엔드 서버가 실행 중인지 확인
- `uvicorn main:app --reload --port 8000` 명령어로 백엔드 서버 실행

### 2. CORS 에러

**증상:**
```
Access to fetch at 'http://localhost:8000/api/webhooks' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**해결:**
- `functions/main.py`에서 CORS 설정 확인:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 인증 토큰 오류

**증상:**
```
401 Unauthorized
```

**해결:**
- Firebase Auth 설정 확인
- 브라우저 콘솔에서 토큰 확인
- Firebase Console에서 사용자 생성 확인

## 개발 워크플로우

1. **백엔드 서버 실행** (터미널 1)
   ```bash
   cd functions
   .\venv\Scripts\Activate.ps1
   uvicorn main:app --reload --port 8000
   ```

2. **프론트엔드 서버 실행** (터미널 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **브라우저에서 접속**
   - 프론트엔드: http://localhost:5173
   - 백엔드 API 문서: http://localhost:8000/docs

## 프로덕션 배포와의 차이

### 로컬 개발
- 백엔드: `http://localhost:8000` (uvicorn)
- 프론트엔드: `http://localhost:5173` (Vite dev server)
- API 요청: Vite 프록시를 통해 백엔드로 전달

### 프로덕션
- 백엔드: Firebase Functions URL (예: `https://us-central1-project.cloudfunctions.net/api`)
- 프론트엔드: Vercel 등에 배포
- API 요청: `VITE_API_BASE_URL` 환경 변수로 설정된 URL 사용

## 빠른 시작 스크립트

### Windows PowerShell

**start-backend.ps1:**
```powershell
cd functions
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

**start-frontend.ps1:**
```powershell
cd frontend
npm run dev
```

두 터미널에서 각각 실행하세요.

## 참고사항

- 백엔드 코드 변경 시 자동으로 재시작됩니다 (`--reload` 옵션)
- 프론트엔드 코드 변경 시 Hot Module Replacement (HMR)로 자동 업데이트됩니다
- Firebase Functions에 배포하지 않아도 로컬에서 모든 기능을 테스트할 수 있습니다
