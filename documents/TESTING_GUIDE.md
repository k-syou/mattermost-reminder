# 테스트 및 검증 가이드

이 문서는 Mattermost Reminder 프로젝트의 테스트 및 검증 방법을 설명합니다.

## 테스트 구조

```
functions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # 공통 fixtures
│   ├── test_dependencies.py # 인증 테스트
│   ├── test_webhooks.py     # Webhook API 테스트
│   ├── test_messages.py     # Message API 테스트
│   └── test_scheduler.py    # 스케줄러 테스트
└── pytest.ini              # Pytest 설정
```

## Backend API 테스트

### 테스트 실행

```bash
cd functions
pip install -r requirements.txt
pytest
```

### 특정 테스트 실행

```bash
# 특정 파일만 실행
pytest tests/test_webhooks.py

# 특정 테스트만 실행
pytest tests/test_webhooks.py::test_create_webhook

# 상세 출력
pytest -v

# 커버리지 확인
pytest --cov=. --cov-report=html
```

### 테스트 항목

#### 1. 인증 테스트 (`test_dependencies.py`)
- ✅ 유효한 토큰으로 인증 성공
- ✅ 헤더 없이 인증 실패
- ✅ 잘못된 헤더 형식 처리
- ✅ 유효하지 않은 토큰 처리
- ✅ 만료된 토큰 처리

#### 2. Webhook API 테스트 (`test_webhooks.py`)
- ✅ Webhook 생성
- ✅ Webhook 목록 조회
- ✅ Webhook 수정
- ✅ Webhook 삭제
- ✅ 인증 없이 접근 차단

#### 3. Message API 테스트 (`test_messages.py`)
- ✅ Message 생성
- ✅ Message 목록 조회
- ✅ Message 수정
- ✅ Message 삭제
- ✅ 즉시 전송 기능
- ✅ 잘못된 요일 값 검증

#### 4. 스케줄러 테스트 (`test_scheduler.py`)
- ✅ 조건에 맞는 메시지 전송
- ✅ 조건에 맞지 않는 경우 처리
- ✅ HTTP 요청 실패 처리

## Frontend 테스트

### 테스트 환경 설정

```bash
cd frontend
npm install --save-dev @vue/test-utils vitest @testing-library/vue
```

### 테스트 실행

```bash
npm run test
```

## 통합 테스트

### 수동 테스트 시나리오

#### 1. 인증 플로우
1. 회원가입
2. 로그인
3. 로그아웃
4. 토큰 만료 시 재로그인

#### 2. Webhook 관리 플로우
1. 웹훅 추가
2. 웹훅 목록 확인
3. 웹훅 수정
4. 웹훅 삭제

#### 3. Message 관리 플로우
1. 메시지 추가
2. 요일 및 시간 설정
3. 웹훅 선택
4. 메시지 활성화/비활성화
5. 즉시 전송 테스트
6. 메시지 수정
7. 메시지 삭제

#### 4. 스케줄러 검증
1. 활성 메시지 생성
2. 현재 시간과 요일이 일치하도록 설정
3. 1분 대기
4. Mattermost 채널에서 메시지 수신 확인

## Mattermost 웹훅 전송 검증

### 테스트 웹훅 생성

1. Mattermost 채널 설정 → 통합 → 인커밍 웹훅
2. 웹훅 URL 복사
3. 프론트엔드에서 웹훅 등록

### 전송 테스트

#### 방법 1: 즉시 전송 기능 사용
1. 메시지 생성
2. "즉시 전송" 버튼 클릭
3. Mattermost 채널에서 메시지 확인

#### 방법 2: 스케줄러 테스트
1. 현재 시간의 1분 후로 설정
2. 해당 요일 선택
3. 메시지 활성화
4. 1분 대기 후 Mattermost 채널 확인

### 검증 체크리스트

- [ ] 웹훅 URL이 올바르게 저장되는가?
- [ ] 메시지 내용이 정확히 전송되는가?
- [ ] JSON 형식이 올바른가? (`{"text": "메시지"}`)
- [ ] 요일과 시간이 정확히 매칭되는가?
- [ ] 비활성 메시지는 전송되지 않는가?
- [ ] HTTP 에러가 발생하면 적절히 처리되는가?

## API 엔드포인트 테스트

### Health Check

```bash
curl https://your-api-url/health
```

### 인증 테스트

```bash
# 토큰 없이 접근 (실패해야 함)
curl https://your-api-url/api/webhooks

# 토큰과 함께 접근
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-api-url/api/webhooks
```

### Webhook CRUD 테스트

```bash
# 생성
curl -X POST https://your-api-url/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"alias": "Test", "url": "https://example.com/webhook"}'

# 조회
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-api-url/api/webhooks

# 수정
curl -X PUT https://your-api-url/api/webhooks/WEBHOOK_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"alias": "Updated"}'

# 삭제
curl -X DELETE https://your-api-url/api/webhooks/WEBHOOK_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Message CRUD 테스트

```bash
# 생성
curl -X POST https://your-api-url/api/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test message",
    "daysOfWeek": [1, 3, 5],
    "sendTime": "09:00",
    "webhookUrl": "https://example.com/webhook",
    "isActive": true
  }'

# 즉시 전송
curl -X POST https://your-api-url/api/messages/MESSAGE_ID/send \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 성능 테스트

### 부하 테스트 (선택사항)

```bash
# Apache Bench 사용 예시
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-api-url/api/webhooks
```

## 보안 테스트

### 체크리스트

- [ ] 인증 없이 API 접근 차단
- [ ] 다른 사용자의 데이터 접근 차단
- [ ] SQL Injection 방지 (Firestore 사용으로 자동 방지)
- [ ] XSS 방지 (입력값 검증)
- [ ] CORS 설정 확인
- [ ] 토큰 만료 처리

## 문제 해결

### 테스트 실패 시

1. **Firebase 초기화 오류**
   - `serviceAccountKey.json` 파일 확인
   - 환경 변수 설정 확인

2. **Mock 오류**
   - `conftest.py`의 fixtures 확인
   - Mock 객체 설정 확인

3. **Import 오류**
   - Python 경로 확인
   - `sys.path` 설정 확인

## 다음 단계

테스트가 모두 통과하면:
1. Phase 6: 배포 진행
2. 프로덕션 환경에서 최종 검증
3. 모니터링 설정
