# 스케줄러 설정 (예약 메시지 전송)

## ⚠️ Cloud Run 배포 시 필수: 스케줄이 안 돌면 여기부터 확인

**API를 Cloud Run(Docker/uvicorn)으로만 배포한 경우, 예약이 절대 실행되지 않습니다.**  
스케줄러는 **매분** 누군가가 `/scheduler/send-messages`를 호출해야 동작합니다. 그 역할을 **Google Cloud Scheduler**가 해야 합니다.

### 한 번만 설정하면 됨 (gcloud)

```bash
# 프로젝트/리전에 맞게 수정. 예: us-central1, api-tgjiwho2yq-uc.a.run.app
gcloud scheduler jobs create http mattermost-send-messages \
  --location=us-central1 \
  --schedule="* * * * *" \
  --time-zone="Asia/Seoul" \
  --uri="https://api-tgjiwho2yq-uc.a.run.app/scheduler/send-messages" \
  --http-method=POST
```

또는 스크립트 사용 (URL만 맞으면 됨):

```bash
API_URL=https://api-tgjiwho2yq-uc.a.run.app ./scripts/setup-cloud-scheduler.sh
```

### 수동 테스트

스케줄 작업 만들기 전에 동작 확인:

- 브라우저에서 `https://api-tgjiwho2yq-uc.a.run.app/scheduler/send-messages` (GET) 호출  
- 응답에 `processed`, `checkedAt` 등이 오면 스케줄러 로직은 정상. 이제 위 Cloud Scheduler 작업만 만들면 매분 자동 호출됨.

---

## 요일·시간 규칙

- **요일**: API/프론트와 동일하게 `0=일요일`, `1=월요일`, …, `6=토요일` 사용.
- **시간**: `Asia/Seoul` 기준. `sendTime`은 `HH:MM`(예: `13:50`). 스케줄러가 **해당 분**에 실행되면 전송.

## 배포 방식별 동작

### 1. Firebase Functions로 배포하는 경우

`firebase deploy --only functions` 시 `main.py`의 `@scheduler_fn.on_schedule`가 등록됩니다.

- **주기**: 1분마다 (`every 1 minutes`)
- **타임존**: `Asia/Seoul`
- **리전**: `asia-northeast3` (서울)

별도 설정 없이 배포만 하면 1분마다 자동 실행됩니다.

### 2. Cloud Run만 사용하는 경우 (현재 대부분의 설정)

API를 **Cloud Run**에만 올렸다면 (Docker/uvicorn), **반드시** 위처럼 **Cloud Scheduler 작업**을 한 번 생성해야 합니다.

1. [Google Cloud Console](https://console.cloud.google.com) → **Cloud Scheduler** → **작업 만들기**
2. **이름**: `mattermost-send-messages`
3. **지역**: API와 동일 (예: `us-central1`)
4. **빈도**: `* * * * *` (매분)
5. **타임존**: `Asia/Seoul`
6. **대상 유형**: HTTP
7. **URL**: `https://YOUR_CLOUD_RUN_URL/scheduler/send-messages`
8. **HTTP 메서드**: POST

## 전송이 안 될 때 확인할 것

1. **요일**: 오늘 요일이 메시지의 `daysOfWeek`에 포함되는지 (0=일, 6=토).
2. **시간**: `sendTime`이 `HH:MM` 형태이고, 스케줄러가 그 분에 실행되는지.
3. **활성 여부**: 메시지의 `isActive`가 `true`인지.
4. **스케줄 실행 여부**:  
   - Firebase: Functions 로그에서 `send_scheduled_messages` 호출 확인.  
   - Cloud Run: Cloud Scheduler 실행 기록과 `/scheduler/send-messages` 로그 확인.
