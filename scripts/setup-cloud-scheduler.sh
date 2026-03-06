#!/usr/bin/env bash
# Cloud Run 사용 시 스케줄 전송이 동작하려면 이 작업을 한 번 생성해야 합니다.
# API_URL을 본인 Cloud Run URL로 바꾼 뒤 실행하세요.
#
# 사용 예: ./scripts/setup-cloud-scheduler.sh
# 또는:   API_URL=https://api-xxxxx.run.app ./scripts/setup-cloud-scheduler.sh

set -e
API_URL="${API_URL:-https://api-tgjiwho2yq-uc.a.run.app}"
JOB_NAME="${JOB_NAME:-mattermost-send-messages}"
LOCATION="${LOCATION:-us-central1}"

echo "Creating Cloud Scheduler job: $JOB_NAME"
echo "  URL: $API_URL/scheduler/send-messages"
echo "  Location: $LOCATION"
echo "  Schedule: every minute (Asia/Seoul)"

gcloud scheduler jobs create http "$JOB_NAME" \
  --location="$LOCATION" \
  --schedule="* * * * *" \
  --time-zone="Asia/Seoul" \
  --uri="$API_URL/scheduler/send-messages" \
  --http-method=POST \
  --attempt-deadline=60s \
  --description="Mattermost reminder: run scheduler every minute" \
  || echo "Job may already exist. Update with: gcloud scheduler jobs update http $JOB_NAME --location=$LOCATION --uri=$API_URL/scheduler/send-messages"

echo "Done. Check: gcloud scheduler jobs list --location=$LOCATION"
