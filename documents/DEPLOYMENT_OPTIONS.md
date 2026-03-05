# 배포 옵션 가이드

Google Cloud 서비스 없이도 배포할 수 있는 여러 옵션을 제공합니다.

## 옵션 비교

| 옵션 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **옵션 1: Firebase Functions만 사용** | Firebase Functions에 FastAPI 배포 | Firebase 통합, 무료 할당량 | Python 지원 제한적 |
| **옵션 2: Vercel** | Vercel에 FastAPI 배포 | 간단한 배포, 무료 티어 | 스케줄러는 별도 필요 |
| **옵션 3: Railway/Render** | PaaS에 배포 | 쉬운 배포, 무료 티어 | 스케줄러는 별도 필요 |
| **옵션 4: 자체 서버** | VPS/서버에 직접 배포 | 완전한 제어 | 관리 필요 |

---

## 옵션 1: Firebase Functions만 사용 (권장)

Firebase Functions는 Firebase의 일부이므로 추가 Google Cloud 서비스 없이 사용 가능합니다.

### 장점
- Firebase와 완전 통합
- Firestore, Auth와 같은 서비스와 자연스러운 연동
- 무료 할당량 제공
- 스케줄러 함수 내장 지원

### 단점
- Python 지원이 Node.js보다 제한적
- Cold start 시간

### 구현 방법
이미 설정되어 있습니다:
- `functions/http_function.py` - HTTP Function
- `functions/scheduled_function.py` - Scheduled Function (1분마다 자동 실행)

### 배포
```bash
firebase deploy --only functions
```

스케줄러는 Firebase Functions의 `scheduler_fn`을 사용하므로 Cloud Scheduler 설정이 자동으로 됩니다.

---

## 옵션 2: Vercel 배포

Vercel은 FastAPI를 직접 지원하며, 무료 티어가 있습니다.

### 설정

#### 1. `vercel.json` 생성
```json
{
  "version": 2,
  "builds": [
    {
      "src": "functions/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "functions/main.py"
    }
  ]
}
```

#### 2. Vercel 배포
```bash
npm i -g vercel
vercel
```

#### 3. 스케줄러 설정
Vercel Cron Jobs 사용 (Pro 플랜 필요) 또는 외부 서비스 사용:
- [cron-job.org](https://cron-job.org/) (무료)
- [EasyCron](https://www.easycron.com/) (무료 티어)
- [UptimeRobot](https://uptimerobot.com/) (무료)

---

## 옵션 3: Railway 배포

Railway는 Python 앱을 쉽게 배포할 수 있는 PaaS입니다.

### 설정

#### 1. `Procfile` 생성
```
web: cd functions && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 2. `railway.json` 생성 (선택)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd functions && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 3. 배포
1. [Railway](https://railway.app/) 가입
2. GitHub 저장소 연결
3. 자동 배포

#### 4. 스케줄러
Railway Cron Jobs 또는 외부 서비스 사용

---

## 옵션 4: Render 배포

Render도 Python 앱을 쉽게 배포할 수 있습니다.

### 설정

#### 1. `render.yaml` 생성
```yaml
services:
  - type: web
    name: mattermost-scheduler-api
    env: python
    buildCommand: cd functions && pip install -r requirements.txt
    startCommand: cd functions && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### 2. 배포
1. [Render](https://render.com/) 가입
2. GitHub 저장소 연결
3. 자동 배포

#### 3. 스케줄러
Render Cron Jobs 또는 외부 서비스 사용

---

## 옵션 5: 자체 서버 배포

VPS나 자체 서버에 직접 배포할 수 있습니다.

### 설정

#### 1. 서버 설정
```bash
# Ubuntu/Debian 예시
sudo apt update
sudo apt install python3.11 python3-pip nginx

# 프로젝트 클론
git clone <your-repo>
cd mattermost_reminder/functions
pip install -r requirements.txt
```

#### 2. systemd 서비스 생성
`/etc/systemd/system/mattermost-api.service`:
```ini
[Unit]
Description=Mattermost Scheduler API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/mattermost_reminder/functions
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. Nginx 리버스 프록시
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. 스케줄러
cron 사용:
```bash
# crontab -e
* * * * * curl -X POST http://localhost:8000/scheduler/send-messages
```

---

## 스케줄러 대안 (외부 서비스)

Firebase Functions의 스케줄러를 사용하지 않는 경우:

### 무료 옵션
1. **cron-job.org**
   - 무료
   - 1분 간격 지원
   - HTTP 요청 가능

2. **EasyCron**
   - 무료 티어: 월 100회
   - 1분 간격 지원

3. **UptimeRobot**
   - 무료: 50개 모니터
   - HTTP 요청 가능

### 사용 예시
```bash
# cron-job.org에서 설정
URL: https://your-api-url/scheduler/send-messages
Method: POST
Schedule: Every minute
```

---

## 권장 사항

### Firebase를 계속 사용하는 경우
**옵션 1 (Firebase Functions)** 권장
- 이미 설정되어 있음
- Firebase 서비스와 완전 통합
- 스케줄러 내장

### Firebase를 사용하지 않는 경우
**옵션 2 (Vercel)** 또는 **옵션 3 (Railway)** 권장
- 배포가 간단함
- 무료 티어 제공
- 스케줄러는 외부 서비스 사용

---

## 마이그레이션 가이드

### Firebase Functions → Vercel
1. `vercel.json` 생성
2. `functions/main.py`를 루트로 이동하거나 경로 수정
3. Vercel 배포
4. 외부 스케줄러 설정

### Firebase Functions → Railway/Render
1. `Procfile` 또는 `render.yaml` 생성
2. 환경 변수 설정
3. 배포
4. 외부 스케줄러 설정

---

## 비용 비교

| 옵션 | 무료 티어 | 유료 시작 |
|------|----------|----------|
| Firebase Functions | 2M 호출/월 | $0.40/1M 호출 |
| Vercel | 무제한 (제한 있음) | $20/월 |
| Railway | $5 크레딧/월 | $5/월 |
| Render | 무료 (제한 있음) | $7/월 |
| 자체 서버 | 서버 비용 | $5-20/월 |

---

## 다음 단계

원하는 옵션을 선택하면 해당 옵션의 상세 설정 가이드를 제공하겠습니다.
