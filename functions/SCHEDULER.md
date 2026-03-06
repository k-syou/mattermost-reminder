# 스케줄러 설정 (예약 메시지 전송)

## 요일·시간 규칙

- **요일**: API/프론트와 동일하게 `0=일요일`, `1=월요일`, …, `6=토요일` 사용.
- **시간**: `Asia/Seoul` 기준. `sendTime`은 `HH:MM`(예: `09:00`). 스케줄러가 해당 분에 실행되면 전송.

## 배포 방식별 동작

### 1. Firebase Functions로 배포하는 경우

`firebase deploy --only functions` 시 `main.py`의 `@scheduler_fn.on_schedule`가 등록됩니다.

- **주기**: 1분마다 (`every 1 minutes`)
- **타임존**: `Asia/Seoul`
- **리전**: `asia-northeast3` (서울)

별도 설정 없이 배포만 하면 1분마다 자동 실행됩니다.

### 2. Cloud Run만 사용하는 경우 (HTTP로만 서비스)

API를 Cloud Run에만 올렸다면, **Google Cloud Scheduler**로 1분마다 스케줄 엔드포인트를 호출해야 합니다.

1. [Google Cloud Console](https://console.cloud.google.com) → **Cloud Scheduler**로 이동.
2. **작업 만들기** 선택.
3. 설정 예:
   - **이름**: `mattermost-send-messages`
   - **지역**: API와 동일 리전 (예: `asia-northeast3`)
   - **빈도**: `* * * * *` (매분)
   - **타임존**: `Asia/Seoul`
   - **대상 유형**: HTTP
   - **URL**: `https://YOUR_CLOUD_RUN_URL/scheduler/send-messages`  
     (예: `https://api-xxxxx-uc.a.run.app/scheduler/send-messages`)
   - **HTTP 메서드**: POST
   - **본문**: 비워두거나 `{}`

4. Cloud Run URL에 인증이 필요하면 **OIDC 토큰** 또는 **Auth 헤더**를 설정합니다.

gcloud 예시:

```bash
gcloud scheduler jobs create http mattermost-send-messages \
  --location=asia-northeast3 \
  --schedule="* * * * *" \
  --time-zone="Asia/Seoul" \
  --uri="https://YOUR_CLOUD_RUN_URL/scheduler/send-messages" \
  --http-method=POST
```

## 전송이 안 될 때 확인할 것

1. **요일**: 오늘 요일이 메시지의 `daysOfWeek`에 포함되는지 (0=일, 6=토).
2. **시간**: `sendTime`이 `HH:MM` 형태이고, 스케줄러가 그 분에 실행되는지.
3. **활성 여부**: 메시지의 `isActive`가 `true`인지.
4. **스케줄 실행 여부**:  
   - Firebase: Functions 로그에서 `send_scheduled_messages` 호출 확인.  
   - Cloud Run: Cloud Scheduler 실행 기록과 `/scheduler/send-messages` 로그 확인.
