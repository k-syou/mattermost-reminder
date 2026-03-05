# Vercel 프론트엔드 배포 가이드

이 문서는 Mattermost Reminder 프론트엔드를 Vercel에 배포하는 방법을 설명합니다.

## 사전 준비

1. **Vercel 계정 생성**
   - [Vercel](https://vercel.com)에 가입
   - GitHub 계정으로 연동 권장

2. **프로젝트 준비**
   - Git 저장소에 코드 푸시 완료
   - Firebase Functions 배포 완료 (API URL 필요)

## 배포 방법

### 방법 1: Vercel CLI 사용

#### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

#### 2. Vercel 로그인
```bash
vercel login
```

#### 3. 프로젝트 배포
```bash
# 프로젝트 루트에서 실행
vercel

# 프로덕션 배포
vercel --prod
```

### 방법 2: Vercel 웹 대시보드 사용

1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. "Add New Project" 클릭
3. Git 저장소 선택 (GitHub, GitLab, Bitbucket)
4. 프로젝트 설정:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. 환경 변수 설정 (아래 참고)
6. "Deploy" 클릭

## 환경 변수 설정

Vercel 대시보드에서 다음 환경 변수를 설정해야 합니다:

### 필수 환경 변수

```
VITE_API_BASE_URL=https://asia-northeast3-{project-id}.cloudfunctions.net/api
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### 환경 변수 설정 방법

#### Vercel CLI 사용:
```bash
vercel env add VITE_API_BASE_URL
vercel env add VITE_FIREBASE_API_KEY
vercel env add VITE_FIREBASE_AUTH_DOMAIN
vercel env add VITE_FIREBASE_PROJECT_ID
vercel env add VITE_FIREBASE_STORAGE_BUCKET
vercel env add VITE_FIREBASE_MESSAGING_SENDER_ID
vercel env add VITE_FIREBASE_APP_ID
```

#### Vercel 대시보드 사용:
1. 프로젝트 → Settings → Environment Variables
2. 각 환경 변수 추가:
   - Name: `VITE_API_BASE_URL`
   - Value: Firebase Functions URL
   - Environment: Production, Preview, Development 모두 선택

### Firebase Functions URL 확인

Firebase Functions 배포 후 URL 확인:
```bash
firebase functions:list
```

또는 Firebase Console에서:
1. [Firebase Console](https://console.firebase.google.com/)
2. Functions 메뉴
3. `api` 함수 클릭
4. URL 확인: `https://asia-northeast3-{project-id}.cloudfunctions.net/api`

## 프로젝트 설정

### vercel.json 설정

프로젝트 루트에 `vercel.json` 파일이 있습니다:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Root Directory 설정 (대시보드 사용 시)

Vercel 대시보드에서 프로젝트 설정:
- **Root Directory**: `frontend`로 설정

또는 프로젝트 루트에서 배포하는 경우:
- `vercel.json`의 설정 사용

## 배포 후 확인

### 1. 배포 URL 확인
배포 완료 후 Vercel이 제공하는 URL:
- 프로덕션: `https://your-project.vercel.app`
- 프리뷰: `https://your-project-{hash}.vercel.app`

### 2. 기능 테스트
- [ ] 로그인/회원가입 동작 확인
- [ ] 웹훅 관리 기능 확인
- [ ] 메시지 관리 기능 확인
- [ ] API 요청 정상 동작 확인

### 3. 콘솔 확인
브라우저 개발자 도구에서:
- [ ] 에러 없음 확인
- [ ] API 요청 성공 확인
- [ ] Firebase Auth 정상 동작 확인

## 커스텀 도메인 설정 (선택사항)

1. Vercel 대시보드 → 프로젝트 → Settings → Domains
2. 도메인 추가
3. DNS 설정 (Vercel이 제공하는 값 사용)

## 문제 해결

### 빌드 실패

**에러: Module not found**
```bash
# 로컬에서 빌드 테스트
cd frontend
npm install
npm run build
```

**에러: Environment variable not found**
- Vercel 대시보드에서 환경 변수 확인
- 환경 변수 이름이 `VITE_`로 시작하는지 확인

### 런타임 에러

**API 요청 실패**
- `VITE_API_BASE_URL` 환경 변수 확인
- Firebase Functions URL이 올바른지 확인
- CORS 설정 확인 (백엔드)

**Firebase Auth 오류**
- Firebase 환경 변수 확인
- Firebase Console에서 Authentication 활성화 확인

### 배포 후 404 에러

Vue Router의 History 모드 사용 시 `vercel.json`의 `rewrites` 설정 확인:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

## 자동 배포 설정

Git 저장소와 연동하면:
- `main` 브랜치에 푸시 → 프로덕션 배포
- 다른 브랜치에 푸시 → 프리뷰 배포

## 배포 체크리스트

- [ ] Vercel 계정 생성 및 로그인
- [ ] Git 저장소에 코드 푸시
- [ ] Firebase Functions 배포 완료
- [ ] Firebase Functions URL 확인
- [ ] 환경 변수 설정 (7개)
- [ ] 프로젝트 배포
- [ ] 배포 URL 접속 확인
- [ ] 로그인 기능 테스트
- [ ] API 요청 테스트
- [ ] 모든 기능 동작 확인

## 다음 단계

배포 완료 후:
1. 프로덕션 환경에서 통합 테스트
2. 성능 모니터링 설정
3. 에러 추적 설정 (Sentry 등)
4. 사용자 피드백 수집
