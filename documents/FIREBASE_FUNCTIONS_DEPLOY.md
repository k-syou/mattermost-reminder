# Firebase Functions 배포 가이드

이 문서는 Firebase Functions에 FastAPI 애플리케이션을 배포하는 방법을 설명합니다.

## 사전 준비

### 1. Firebase CLI 설치 및 로그인
```bash
# Firebase CLI 설치 (이미 설치되어 있다면 생략)
npm install -g firebase-tools

# Firebase 로그인
firebase login
```

### 2. 프로젝트 확인
`.firebaserc` 파일에서 프로젝트 ID 확인:
```json
{
  "projects": {
    "default": "mattermost-reminder"
  }
}
```

프로젝트가 다르다면:
```bash
firebase use --add
```

### 3. 의존성 설치
```bash
cd functions
pip install -r requirements.txt
```

## 배포 구조

### 파일 구조
```
functions/
├── main.py              # FastAPI 애플리케이션
├── http_function.py     # Firebase HTTP Function 래퍼
├── scheduled_function.py # Firebase Scheduled Function
├── dependencies.py      # Auth 미들웨어
├── models.py            # Pydantic 모델
├── routers/             # API 라우터
│   ├── webhooks.py
│   └── messages.py
└── requirements.txt     # Python 의존성
```

### 주요 구성 요소

1. **http_function.py**: FastAPI 앱을 Firebase HTTP Function으로 래핑
   - Mangum을 사용하여 ASGI 어댑터 제공
   - CORS 설정 포함

2. **scheduled_function.py**: 1분마다 실행되는 스케줄러
   - Cloud Scheduler로 자동 트리거
   - 활성 메시지 검색 및 Mattermost 웹훅 전송

## 배포 단계

### 1. 배포 전 확인
```bash
# Firebase 프로젝트 확인
firebase projects:list

# 현재 프로젝트 확인
firebase use
```

### 2. Functions 배포
```bash
# 전체 Functions 배포
firebase deploy --only functions

# 특정 함수만 배포
firebase deploy --only functions:api
firebase deploy --only functions:send_scheduled_messages
```

### 3. 배포 확인
배포가 완료되면 다음과 같은 URL이 제공됩니다:
- API 엔드포인트: `https://asia-northeast3-{project-id}.cloudfunctions.net/api`
- 스케줄러: 자동으로 Cloud Scheduler에 등록됨

### 4. API 테스트
```bash
# Health check
curl https://asia-northeast3-{project-id}.cloudfunctions.net/api/health

# Root endpoint
curl https://asia-northeast3-{project-id}.cloudfunctions.net/api/
```

## 환경 변수 설정

### 로컬 개발
`functions/.env` 파일 생성:
```env
# Firebase는 자동으로 Application Default Credentials 사용
# 로컬 개발 시에만 serviceAccountKey.json 필요
```

### 프로덕션
Firebase Functions는 자동으로 Application Default Credentials를 사용하므로 별도 설정 불필요.

## 스케줄러 확인

### Cloud Scheduler 확인
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Cloud Scheduler 메뉴로 이동
3. `send-scheduled-messages` 작업 확인
4. 스케줄: `every 1 minutes`
5. 타임존: `Asia/Seoul`

### 스케줄러 수동 실행 (테스트)
```bash
# Cloud Scheduler 작업 목록
gcloud scheduler jobs list --location=asia-northeast3

# 수동 실행
gcloud scheduler jobs run send-scheduled-messages --location=asia-northeast3
```

## 문제 해결

### 배포 실패 시

1. **의존성 오류**
   ```bash
   cd functions
   pip install -r requirements.txt --upgrade
   ```

2. **Python 버전 확인**
   - `firebase.json`에서 `runtime: "python311"` 확인
   - 로컬 Python 버전 확인: `python --version`

3. **Firebase CLI 버전 확인**
   ```bash
   firebase --version
   npm update -g firebase-tools
   ```

### 함수 실행 오류

1. **로그 확인**
   ```bash
   firebase functions:log
   ```

2. **Cloud Console에서 확인**
   - [Firebase Console](https://console.firebase.google.com/) → Functions → Logs

3. **로컬 테스트**
   ```bash
   cd functions
   firebase emulators:start --only functions
   ```

## 로컬 개발

### Firebase Emulators 사용
```bash
# Emulators 시작
firebase emulators:start

# Functions만 시작
firebase emulators:start --only functions
```

### 로컬에서 FastAPI 직접 실행
```bash
cd functions
uvicorn main:app --reload --port 8000
```

## 배포 후 체크리스트

- [ ] Functions 배포 완료
- [ ] API 엔드포인트 접근 가능
- [ ] Health check 엔드포인트 동작 확인
- [ ] Cloud Scheduler 작업 생성 확인
- [ ] 스케줄러 함수 로그 확인
- [ ] CORS 설정 확인 (필요시)

## API 엔드포인트

배포 후 사용 가능한 엔드포인트:

- `GET /` - API 정보
- `GET /health` - Health check
- `POST /api/webhooks` - Webhook 생성
- `GET /api/webhooks` - Webhook 목록
- `GET /api/webhooks/{id}` - Webhook 조회
- `PUT /api/webhooks/{id}` - Webhook 수정
- `DELETE /api/webhooks/{id}` - Webhook 삭제
- `POST /api/messages` - Message 생성
- `GET /api/messages` - Message 목록
- `GET /api/messages/{id}` - Message 조회
- `PUT /api/messages/{id}` - Message 수정
- `DELETE /api/messages/{id}` - Message 삭제
- `POST /api/messages/{id}/send` - Message 즉시 전송

모든 API 엔드포인트는 `Authorization: Bearer {token}` 헤더가 필요합니다.

## 다음 단계

1. Frontend에서 API 엔드포인트 연결
2. 통합 테스트 진행
3. 프로덕션 모니터링 설정
