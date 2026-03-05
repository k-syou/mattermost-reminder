# 프로덕션 API 설정 가이드

프론트엔드와 Firebase Functions를 연결하기 위한 설정 가이드입니다.

## 문제 상황

프로덕션 배포 후:
- "Unexpected token '<', "<!DOCTYPE "... is not valid JSON" 에러
- 웹훅/메시지 관리에서 API 호출 실패
- HTML 응답이 반환됨

## 원인

`VITE_API_BASE_URL` 환경 변수가 설정되지 않아 API 요청이 Vercel의 rewrite 규칙에 의해 `/index.html`로 리다이렉트되어 HTML이 반환됩니다.

## 해결 방법

### 방법 1: Vercel 환경 변수 설정 (권장)

#### 1단계: Firebase Functions URL 확인

Firebase Console에서:
1. Firebase Console → Functions
2. `api` 함수의 URL 확인
3. 예: `https://asia-northeast3-mattermost-reminder.cloudfunctions.net`

또는 명령어로:
```bash
firebase functions:list
```

#### 2단계: Vercel 환경 변수 추가

1. **Vercel Dashboard 접속:**
   - [Vercel Dashboard](https://vercel.com/dashboard)
   - 프로젝트 선택

2. **Settings → Environment Variables:**
   - "Add New" 클릭
   - Name: `VITE_API_BASE_URL`
   - Value: Firebase Functions URL (예: `https://asia-northeast3-mattermost-reminder.cloudfunctions.net`)
   - Environment: Production, Preview, Development 모두 선택
   - "Save" 클릭

3. **재배포:**
   - Deployments 탭 → 최신 배포의 "..." 메뉴 → "Redeploy"
   - 또는 코드를 다시 푸시하여 자동 재배포

### 방법 2: vercel.json에 API 프록시 설정

`vercel.json`에 API 요청을 Firebase Functions로 프록시하도록 설정:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://asia-northeast3-mattermost-reminder.cloudfunctions.net/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

**주의사항:**
- `destination`의 URL을 실제 Firebase Functions URL로 변경해야 합니다
- 이 방법을 사용하면 `VITE_API_BASE_URL`을 설정하지 않아도 됩니다 (빈 문자열 사용)

## 확인 방법

### 1. 브라우저 개발자 도구

1. 브라우저 개발자 도구 열기 (F12)
2. Network 탭 확인
3. API 요청 URL 확인:
   - 올바른 경우: `https://asia-northeast3-mattermost-reminder.cloudfunctions.net/api/webhooks`
   - 잘못된 경우: `https://your-vercel-domain.vercel.app/api/webhooks` (HTML 반환)

### 2. 환경 변수 확인

프론트엔드 코드에 임시로 추가:

```javascript
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL)
```

브라우저 콘솔에서 확인:
- 올바른 경우: Firebase Functions URL이 출력됨
- 잘못된 경우: `undefined` 또는 빈 문자열

### 3. API 응답 확인

Network 탭에서 응답 확인:
- 올바른 경우: JSON 응답
- 잘못된 경우: HTML 응답 (`<!DOCTYPE html>`)

## 추가 문제 해결

### CORS 에러

Firebase Functions의 CORS 설정 확인:

`functions/http_function.py`:
```python
@https_fn.on_request(
    cors=https_fn.CorsOptions(
        cors_origins=["*"],  # 또는 특정 도메인: ["https://your-domain.vercel.app"]
        cors_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        cors_allow_headers=["Authorization", "Content-Type"],
        cors_max_age=3600
    )
)
```

### 404 에러

1. Firebase Functions가 배포되었는지 확인:
   ```bash
   firebase functions:list
   ```

2. 함수 이름 확인:
   - `http_function.py`의 함수 이름이 `api`인지 확인

3. Firebase Functions URL 형식:
   - `https://{region}-{project-id}.cloudfunctions.net/{function-name}`
   - 예: `https://asia-northeast3-mattermost-reminder.cloudfunctions.net/api`

### 인증 에러

1. Firebase Auth 토큰이 올바르게 전송되는지 확인:
   - Network 탭 → Request Headers → `Authorization: Bearer ...` 확인

2. Firebase Auth 설정 확인:
   - Firebase Console → Authentication
   - Authorized domains에 Vercel 도메인 추가

## 로컬 개발 환경

로컬 개발 시 `vite.config.ts`의 proxy 설정 사용:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

로컬에서는 `VITE_API_BASE_URL`을 설정하지 않아도 됩니다.

## 참고

- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Firebase Functions HTTP Functions](https://firebase.google.com/docs/functions/http-events)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
