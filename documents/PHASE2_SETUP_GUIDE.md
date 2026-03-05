# Phase 2: Firebase 인프라 구축 가이드

이 문서는 Phase 2에서 진행해야 하는 Firebase 인프라 설정에 대한 단계별 가이드를 제공합니다.

## 목차
1. [Firestore 데이터베이스 초기화](#1-firestore-데이터베이스-초기화)
2. [Firebase Auth 설정](#2-firebase-auth-설정)
3. [Firebase Functions 배포 설정](#3-firebase-functions-배포-설정)

---

## 1. Firestore 데이터베이스 초기화

### 1.1 Firebase Console 접속
1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. 프로젝트 이름: `mattermost-reminder` (또는 원하는 이름)

### 1.2 Firestore Database 생성
1. Firebase Console 좌측 메뉴에서 **"Firestore Database"** 클릭
2. **"데이터베이스 만들기"** 버튼 클릭

### 1.3 프로덕션 모드 선택
1. **"프로덕션 모드에서 시작"** 선택
   - 보안 규칙은 이미 `firestore.rules` 파일에 작성되어 있음
   - 나중에 규칙을 배포할 예정

### 1.4 위치 선택
1. **위치 선택**: `asia-northeast3` (Seoul) 또는 `us-central1` 선택
   - 권장: `asia-northeast3` (서울 리전, 한국 사용자에게 빠름)
2. **"사용 설정"** 클릭

### 1.5 Firestore 보안 규칙 배포
1. Firebase CLI 설치 확인:
   ```bash
   npm install -g firebase-tools
   ```

2. Firebase 로그인:
   ```bash
   firebase login
   ```

3. 프로젝트 초기화 (이미 되어있다면 생략):
   ```bash
   firebase init firestore
   ```
   - 기존 `firestore.rules` 파일 사용 선택

4. 보안 규칙 배포:
   ```bash
   firebase deploy --only firestore:rules
   ```

### 1.6 Firestore 인덱스 설정 (필요시)
현재 스키마에서는 복합 인덱스가 필요하지 않지만, 향후 쿼리 최적화가 필요하면:

1. Firebase Console → Firestore Database → 인덱스 탭
2. 또는 `firestore.indexes.json` 파일 수정 후 배포:
   ```bash
   firebase deploy --only firestore:indexes
   ```

### 1.7 검증
Firebase Console에서 Firestore Database가 생성되었는지 확인:
- 데이터베이스가 활성화되어 있음
- 보안 규칙이 배포됨

---

## 2. Firebase Auth 설정

### 2.1 Authentication 활성화
1. Firebase Console 좌측 메뉴에서 **"Authentication"** 클릭
2. **"시작하기"** 버튼 클릭

### 2.2 이메일/비밀번호 인증 방법 활성화
1. **"Sign-in method"** 탭 클릭
2. **"이메일/비밀번호"** 클릭
3. **"사용 설정"** 토글 활성화
4. **"이메일/비밀번호(비밀번호 없이 로그인)"**는 선택 사항 (필요시 활성화)
5. **"저장"** 클릭

### 2.3 사용자 추가 (테스트용, 선택 사항)
1. **"Users"** 탭 클릭
2. **"사용자 추가"** 버튼 클릭
3. 이메일과 비밀번호 입력
4. 테스트 계정 생성

### 2.4 인증 도메인 설정
1. **"Settings"** (톱니바퀴 아이콘) → **"프로젝트 설정"** 클릭
2. **"일반"** 탭에서 **"승인된 도메인"** 확인
3. 개발 환경 도메인 추가 (예: `localhost`, `127.0.0.1`)
4. 프로덕션 도메인 추가 (예: Vercel 배포 URL)

### 2.5 Firebase 프로젝트 설정 정보 확인
프로젝트 설정에서 다음 정보를 확인하고 Frontend 환경 변수에 설정:

1. **"일반"** 탭에서:
   - 프로젝트 ID
   - 웹 API 키
   - 인증 도메인

2. **"서비스 계정"** 탭에서:
   - 서비스 계정 키 생성 (Backend용)
   - **"새 비공개 키 생성"** 클릭
   - `serviceAccountKey.json` 파일 다운로드
   - `functions/serviceAccountKey.json`에 저장 (로컬 개발용)
   - ⚠️ **주의**: 이 파일은 `.gitignore`에 포함되어 있어야 함

### 2.6 Frontend 환경 변수 설정
`frontend/.env.local` 파일 생성 (또는 `.env`):

```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

각 값은 Firebase Console → 프로젝트 설정 → 일반 → 앱 → 웹 앱에서 확인 가능

### 2.7 검증
1. Firebase Console에서 Authentication이 활성화되었는지 확인
2. 이메일/비밀번호 인증 방법이 활성화되었는지 확인
3. 환경 변수 파일이 올바르게 설정되었는지 확인

---

## 3. Firebase Functions 배포 설정

### 3.1 Firebase CLI 설치 및 로그인
```bash
# Firebase CLI 설치 (이미 설치되어 있다면 생략)
npm install -g firebase-tools

# Firebase 로그인
firebase login
```

### 3.2 프로젝트 연결 확인
`.firebaserc` 파일에서 프로젝트 ID 확인:
```json
{
  "projects": {
    "default": "mattermost-reminder"
  }
}
```

프로젝트 ID가 다르다면 수정하거나 다음 명령어로 설정:
```bash
firebase use --add
```

### 3.3 Firebase Functions 초기화 (이미 완료됨)
`firebase.json` 파일이 이미 설정되어 있으므로 생략 가능.

### 3.4 Python Functions 설정 확인
현재 프로젝트는 FastAPI를 사용하므로, Firebase Functions에 직접 배포하기보다는:

**옵션 1: Cloud Run 배포 (권장)**
- FastAPI 앱을 Cloud Run에 배포
- Cloud Scheduler로 스케줄러 엔드포인트 호출

**옵션 2: HTTP Functions로 래핑**
- FastAPI 앱을 HTTP Function으로 래핑

### 3.5 Cloud Run 배포 설정 (옵션 1 - 권장)

#### 3.5.1 Dockerfile 생성
`functions/Dockerfile` 생성:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 3.5.2 Cloud Run 배포
```bash
# Google Cloud SDK 설치 필요
gcloud auth login
gcloud config set project mattermost-reminder

# Cloud Run에 배포
cd functions
gcloud run deploy mattermost-scheduler-api \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated
```

#### 3.5.3 Cloud Scheduler 설정
스케줄러 엔드포인트를 1분마다 호출하도록 설정:

```bash
gcloud scheduler jobs create http send-scheduled-messages \
  --location=asia-northeast3 \
  --schedule="* * * * *" \
  --uri="https://your-cloud-run-url/scheduler/send-messages" \
  --http-method=POST \
  --time-zone="Asia/Seoul"
```

### 3.6 Firebase Functions 배포 설정 (옵션 2)

#### 3.6.1 Functions 런타임 설정
`firebase.json` 확인:
```json
{
  "functions": [
    {
      "source": "functions",
      "codebase": "default",
      "runtime": "python311"
    }
  ]
}
```

#### 3.6.2 HTTP Function 래퍼 생성
`functions/http_function.py` 생성:
```python
from firebase_functions import https_fn
from firebase_admin import initialize_app
import main

initialize_app()

@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    return main.app(req.scope, req.receive)
```

#### 3.6.3 배포
```bash
firebase deploy --only functions
```

### 3.7 환경 변수 설정 (Cloud Run)
Cloud Run 사용 시:
```bash
gcloud run services update mattermost-scheduler-api \
  --set-env-vars="ENV=production" \
  --region=asia-northeast3
```

### 3.8 검증
1. 배포된 API 엔드포인트 확인:
   ```bash
   curl https://your-api-url/health
   ```

2. 스케줄러 엔드포인트 테스트:
   ```bash
   curl -X POST https://your-api-url/scheduler/send-messages
   ```

---

## 4. 전체 검증 체크리스트

### Firestore
- [v] Firestore Database 생성 완료
- [v] 보안 규칙 배포 완료
- [v] 데이터베이스 위치 설정 확인

### Authentication
- [v] Authentication 활성화
- [v] 이메일/비밀번호 인증 방법 활성화
- [v] Frontend 환경 변수 설정 완료
- [v] 서비스 계정 키 다운로드 완료 (Backend용)

### Functions/API
- [ ] API 배포 완료 (Firebase Functions)
- [ ] 스케줄러 함수 배포 완료
- [ ] API 엔드포인트 접근 가능 확인
- [ ] Health check 엔드포인트 동작 확인

---

## 5. 문제 해결

### Firestore 보안 규칙 배포 실패
```bash
# 규칙 문법 확인
firebase deploy --only firestore:rules --dry-run

# 상세 로그 확인
firebase deploy --only firestore:rules --debug
```

### Authentication 설정 오류
- Firebase Console에서 Authentication 탭 확인
- 브라우저 콘솔에서 에러 메시지 확인
- 환경 변수 값이 올바른지 확인

### Functions 배포 실패
- `firebase.json` 설정 확인
- Python 버전 확인 (3.11 권장)
- 의존성 설치 확인: `pip install -r requirements.txt`

---

## 6. 다음 단계

Phase 2 설정이 완료되면:
1. Phase 3의 Backend API 테스트
2. Phase 4의 Frontend 개발 시작
3. 통합 테스트 진행

---

## 참고 자료
- [Firebase 공식 문서](https://firebase.google.com/docs)
- [Firestore 보안 규칙](https://firebase.google.com/docs/firestore/security/get-started)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Cloud Run 배포 가이드](https://cloud.google.com/run/docs/deploying)
- [Cloud Scheduler 가이드](https://cloud.google.com/scheduler/docs)
