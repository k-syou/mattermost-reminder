# Mattermost 메시지 스케줄러 개발 계획서

## 프로젝트 개요
Vue 3, Firebase, FastAPI를 활용한 Mattermost 웹훅 기반 반복 메시지 스케줄링 서비스

## 기술 스택
- **Frontend**: Vue 3 (Composition API), Vite, Tailwind CSS, Pinia
- **Backend**: FastAPI (Python) on Firebase Functions
- **Database**: Google Cloud Firestore
- **Authentication**: Firebase Auth
- **Deployment**: 
  - Frontend: Vercel
  - Backend: Firebase Functions

## 개발 단계

### Phase 1: 프로젝트 초기 설정
- [x] Firebase 프로젝트 초기화 및 설정
- [x] Frontend (Vue 3) 프로젝트 생성
- [x] Backend (FastAPI) 프로젝트 생성
- [x] Firebase Functions 설정
- [x] 환경 변수 설정 파일 생성

### Phase 2: Firebase 인프라 구축
- [x] Firestore 데이터베이스 초기화
- [x] Firebase Auth 설정
- [x] Firestore Security Rules 작성
- [x] Firebase Functions 배포 설정

### Phase 3: Backend API 개발
- [x] FastAPI 기본 구조 설정
- [x] Firebase Auth 미들웨어 구현
- [x] Webhook CRUD API 구현
  - [x] Webhook 생성
  - [x] Webhook 조회 (사용자별)
  - [x] Webhook 수정
  - [x] Webhook 삭제
- [x] Message CRUD API 구현
  - [x] Message 생성
  - [x] Message 조회 (사용자별)
  - [x] Message 수정
  - [x] Message 삭제
  - [x] Message 즉시 전송 (테스트용)
- [x] 스케줄러 함수 구현 (1분마다 실행)
- [x] Mattermost 웹훅 전송 로직 구현

### Phase 4: Frontend 개발
- [x] Vue 3 프로젝트 기본 구조
- [x] Firebase Auth 통합
- [x] Router 설정 및 Guard 구현
- [x] Pinia Store 설정
  - [x] Auth Store
  - [x] Webhook Store
  - [x] Message Store
- [x] 로그인/회원가입 페이지
- [x] 대시보드 페이지
- [x] Webhook 관리 페이지
  - [x] Webhook 목록
  - [x] Webhook 등록/수정 폼
- [x] Message 관리 페이지
  - [x] Message 목록
  - [x] Message 등록/수정 폼
  - [x] 요일 선택 컴포넌트
  - [x] 시간 선택 컴포넌트
  - [x] WebhookSelector 컴포넌트
- [x] UI/UX 스타일링 (Tailwind CSS)

### Phase 5: 테스트 및 검증
- [x] Backend API 단위 테스트
- [x] Frontend 컴포넌트 테스트
- [x] 통합 테스트
- [x] 스케줄러 동작 검증
- [x] Mattermost 웹훅 전송 검증

### Phase 6: 배포
- [ ] Frontend Vercel 배포
- [ ] Backend Firebase Functions 배포
- [ ] 환경 변수 설정
- [ ] 프로덕션 검증

## 데이터 스키마

### `webhooks` Collection
```typescript
{
  userId: string,
  alias: string,
  url: string,
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

### `messages` Collection
```typescript
{
  userId: string,
  content: string,
  daysOfWeek: number[], // [0-6]
  sendTime: string, // "HH:mm"
  webhookUrl: string,
  isActive: boolean,
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

## 주요 기능 명세

### 1. 인증
- Firebase Auth를 통한 이메일/비밀번호 로그인
- 미인증 사용자는 `/login`으로 리다이렉트
- 모든 API 요청에 인증 토큰 포함

### 2. Webhook 관리
- 사용자별 여러 웹훅 등록 가능
- 웹훅 별칭(alias) 설정
- 드롭다운으로 선택 가능

### 3. Message 스케줄링
- 요일 선택 (0=일요일, 6=토요일)
- 시간 선택 (24시간 형식, Asia/Seoul 타임존)
- Markdown 형식 메시지 지원
- 활성화/비활성화 토글

### 4. 자동 전송
- Firebase Scheduler로 1분마다 실행
- 현재 시간과 요일이 일치하는 활성 메시지 검색
- Mattermost 웹훅으로 JSON 전송: `{"text": "메시지 내용"}`

## 다음 단계
Phase 1부터 순차적으로 진행하며, 각 단계마다 테스트 코드를 작성하고 사용자 승인 후 적용합니다.
