# Mattermost Reminder

Mattermost 웹훅을 통한 반복 메시지 스케줄링 서비스

![CI](https://github.com/your-username/mattermost-reminder/workflows/CI/badge.svg)
![Tests](https://github.com/your-username/mattermost-reminder/workflows/Tests/badge.svg)

## 📋 프로젝트 소개

Mattermost Reminder는 Vue 3, FastAPI, Firebase를 활용하여 Mattermost 채널에 반복 메시지를 자동으로 전송하는 서비스입니다. 웹 인터페이스를 통해 메시지 스케줄을 관리하고, 지정된 요일과 시간에 자동으로 Mattermost 웹훅을 통해 메시지를 전송합니다.

## ✨ 주요 기능

- 🔐 **Firebase Authentication** - 이메일/비밀번호 기반 사용자 인증
- 🔗 **웹훅 관리** - 여러 Mattermost 웹훅 등록 및 관리
- 📅 **스케줄 관리** - 요일 및 시간 선택을 통한 메시지 스케줄링
- ⚡ **자동 전송** - Firebase Cloud Scheduler를 통한 자동 메시지 전송
- 📱 **반응형 UI** - Tailwind CSS 기반 모던한 사용자 인터페이스

## 🛠 기술 스택

### Frontend
- **Vue 3** (Composition API)
- **TypeScript**
- **Vite**
- **Pinia** (상태 관리)
- **Vue Router**
- **Tailwind CSS**
- **Vitest** (테스트)

### Backend
- **FastAPI** (Python)
- **Firebase Functions** (배포)
- **Firestore** (데이터베이스)
- **Firebase Auth** (인증)
- **pytest** (테스트)

### DevOps
- **GitHub Actions** (CI/CD)
- **Vercel** (Frontend 배포)
- **Firebase Functions** (Backend 배포)

## 🚀 빠른 시작

### 사전 요구사항

- Node.js 18+
- Python 3.11+
- Firebase 계정
- Git

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/mattermost-reminder.git
cd mattermost-reminder
```

### 2. Frontend 설정

```bash
cd frontend
npm install

# 환경 변수 설정
cp .env.example .env.local
# .env.local 파일을 편집하여 Firebase 설정 추가

# 개발 서버 실행
npm run dev
```

### 3. Backend 설정

```bash
cd functions

# 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn main:app --reload --port 8000
```

### 4. Firebase 설정

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. Firestore Database 활성화
3. Authentication 활성화 (이메일/비밀번호)
4. `.firebaserc` 파일의 프로젝트 ID 확인/수정

자세한 설정은 [`documents/PHASE2_SETUP_GUIDE.md`](documents/PHASE2_SETUP_GUIDE.md)를 참고하세요.

## 📚 문서

프로젝트 관련 상세 문서는 `documents/` 폴더를 참고하세요:

- **[개발 계획서](documents/DEVELOPMENT_PLAN.md)** - 프로젝트 개발 계획 및 진행 상황
- **[로컬 개발 가이드](documents/LOCAL_DEVELOPMENT.md)** - 로컬 개발 환경 설정
- **[배포 가이드](documents/VERCEL_DEPLOY.md)** - Vercel 프론트엔드 배포
- **[Firebase Functions 배포](documents/FIREBASE_FUNCTIONS_DEPLOY.md)** - Firebase Functions 배포
- **[GitHub Actions 설정](documents/GITHUB_ACTIONS_SETUP.md)** - CI/CD 자동화 설정
- **[테스트 가이드](documents/TESTING_GUIDE.md)** - 테스트 실행 및 작성 가이드
- **[프론트엔드 테스트](documents/FRONTEND_TESTING.md)** - 프론트엔드 테스트 가이드
- **[통합 테스트](documents/INTEGRATION_TEST.md)** - 통합 테스트 시나리오
- **[에러 수정 내역](documents/ERROR_FIXES.md)** - 발생한 에러 및 해결 방법

## 🧪 테스트

### Backend 테스트

```bash
cd functions
pytest
```

### Frontend 테스트

```bash
cd frontend
npm run test
```

### 테스트 커버리지

```bash
# Backend
cd functions
pytest --cov=. --cov-report=html

# Frontend
cd frontend
npm run test:coverage
```

## 🚢 배포

### 자동 배포 (GitHub Actions)

`main` 브랜치에 push하면 자동으로 테스트 후 배포됩니다.

### 수동 배포

#### Frontend (Vercel)

```bash
vercel --prod
```

#### Backend (Firebase Functions)

```bash
firebase deploy --only functions
```

자세한 배포 방법은 [`documents/GITHUB_ACTIONS_SETUP.md`](documents/GITHUB_ACTIONS_SETUP.md)를 참고하세요.

## 📁 프로젝트 구조

```
mattermost_reminder/
├── frontend/                 # Vue 3 프론트엔드
│   ├── src/
│   │   ├── components/      # Vue 컴포넌트
│   │   ├── views/          # 페이지 컴포넌트
│   │   ├── stores/         # Pinia 스토어
│   │   ├── router/         # Vue Router 설정
│   │   └── test/           # 테스트 파일
│   └── package.json
├── functions/               # FastAPI 백엔드
│   ├── routers/           # API 라우터
│   ├── tests/             # 테스트 파일
│   └── requirements.txt
├── documents/             # 프로젝트 문서
├── .github/workflows/     # GitHub Actions
├── firebase.json          # Firebase 설정
└── vercel.json            # Vercel 설정
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🔗 관련 링크

- [Firebase Console](https://console.firebase.google.com/)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Mattermost Documentation](https://docs.mattermost.com/)

## 📧 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
