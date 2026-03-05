# 빠른 배포 가이드

## Vercel CLI로 빠르게 배포하기

### 1단계: Vercel CLI 설치 및 로그인

```powershell
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login
```

### 2단계: Firebase Functions URL 확인

Firebase Functions가 배포되어 있다면:
```powershell
firebase functions:list
```

또는 Firebase Console에서 Functions → `api` 함수의 URL 확인
예: `https://asia-northeast3-mattermost-reminder.cloudfunctions.net/api`

### 3단계: 환경 변수 설정

```powershell
# 프로젝트 루트에서 실행
vercel env add VITE_API_BASE_URL production
# 값 입력: https://asia-northeast3-{project-id}.cloudfunctions.net/api

vercel env add VITE_FIREBASE_API_KEY production
vercel env add VITE_FIREBASE_AUTH_DOMAIN production
vercel env add VITE_FIREBASE_PROJECT_ID production
vercel env add VITE_FIREBASE_STORAGE_BUCKET production
vercel env add VITE_FIREBASE_MESSAGING_SENDER_ID production
vercel env add VITE_FIREBASE_APP_ID production
```

### 4단계: 배포

```powershell
# 프로젝트 루트에서 실행
vercel --prod
```

## Vercel 웹 대시보드로 배포하기

### 1단계: 프로젝트 연결

1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. "Add New Project" 클릭
3. Git 저장소 선택

### 2단계: 프로젝트 설정

- **Framework Preset**: Vite
- **Root Directory**: `frontend` (또는 프로젝트 루트에서 `vercel.json` 사용)
- **Build Command**: `npm run build` (Root Directory가 frontend인 경우)
- **Output Directory**: `dist`

### 3단계: 환경 변수 추가

Settings → Environment Variables에서 다음 추가:

```
VITE_API_BASE_URL=https://asia-northeast3-{project-id}.cloudfunctions.net/api
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

### 4단계: 배포

"Deploy" 버튼 클릭

## 배포 후 확인

1. 배포된 URL 접속
2. 로그인 테스트
3. 브라우저 콘솔에서 에러 확인
4. API 요청 정상 동작 확인
