# GitHub Actions CI/CD 설정 가이드

이 문서는 GitHub Actions를 사용하여 테스트부터 배포까지 자동화하는 방법을 설명합니다.

## Workflow 구조

프로젝트에는 3개의 주요 workflow가 있습니다:

1. **`test.yml`** - 테스트 실행 (모든 브랜치)
2. **`deploy.yml`** - 배포 실행 (main 브랜치 또는 수동)
3. **`ci.yml`** - 통합 CI/CD 파이프라인

## 필요한 GitHub Secrets

GitHub Repository Settings → Secrets and variables → Actions에서 다음 secrets를 추가해야 합니다:

### Firebase 배포용

1. **`GCP_SA_KEY`** (필수)
   - Google Cloud Service Account JSON 키
   - Firebase Console → Project Settings → Service Accounts에서 생성
   - "Generate new private key" 클릭하여 JSON 파일 다운로드
   - JSON 파일 전체 내용을 GitHub Secrets에 추가

2. **`FIREBASE_PROJECT_ID`** (선택사항)
   - Firebase 프로젝트 ID (예: `mattermost-reminder`)
   - `.firebaserc` 파일에 이미 설정되어 있으면 불필요

3. **`FIREBASE_TOKEN`** (deprecated)
   - `firebase login:ci` 명령어로 생성
   - `--token` 방식이 deprecated 되었으므로 Service Account Key 사용 권장

### Vercel 배포용

1. **`VERCEL_TOKEN`**
   ```bash
   # Vercel CLI로 로그인 후
   vercel whoami
   # Vercel Dashboard → Settings → Tokens에서 생성
   ```

2. **`VERCEL_ORG_ID`**
   - Vercel Dashboard → Settings → General에서 확인

3. **`VERCEL_PROJECT_ID`**
   - Vercel Dashboard → 프로젝트 → Settings → General에서 확인

## Workflow 설명

### 1. test.yml - 테스트 실행

**트리거:**
- `main`, `develop`, `feature/**` 브랜치에 push
- Pull Request 생성 시

**작업:**
- Backend 테스트 실행 (pytest)
- Frontend 테스트 실행 (vitest)
- 코드 커버리지 수집 및 업로드
- Linter 실행

**실행 시간:** 약 2-3분

### 2. deploy.yml - 배포 실행

**트리거:**
- `main` 브랜치에 push
- 수동 실행 (workflow_dispatch)

**작업:**
- Backend를 Firebase Functions에 배포
- Frontend를 Vercel에 배포

**실행 시간:** 약 5-10분

### 3. ci.yml - 통합 CI/CD 파이프라인

**트리거:**
- `main`, `develop` 브랜치에 push
- Pull Request 생성 시

**작업:**
- 테스트 실행
- 테스트 통과 시 자동 배포 (main 브랜치만)

## Secrets 설정 방법

### Firebase Token 생성

```bash
# Firebase CLI 설치 (이미 설치되어 있다면 생략)
npm install -g firebase-tools

# CI용 토큰 생성
firebase login:ci

# 출력된 토큰을 복사하여 GitHub Secrets에 추가
# Name: FIREBASE_TOKEN
# Value: [출력된 토큰]
```

### Vercel Token 생성

1. [Vercel Dashboard](https://vercel.com/account/tokens) 접속
2. "Create Token" 클릭
3. Token 이름 입력 (예: "GitHub Actions")
4. Scope: Full Account 선택
5. 생성된 토큰을 복사하여 GitHub Secrets에 추가

### Vercel Org ID 및 Project ID 확인

1. Vercel Dashboard 접속
2. 프로젝트 선택
3. Settings → General
4. **Org ID**: Organization ID 확인
5. **Project ID**: Project ID 확인

## Workflow 실행 확인

### GitHub에서 확인

1. Repository → Actions 탭
2. 실행 중인 workflow 확인
3. 각 job의 로그 확인

### 로컬에서 테스트

```bash
# Act (GitHub Actions 로컬 실행 도구) 사용
# https://github.com/nektos/act

# 테스트만 실행
act -j backend-test
act -j frontend-test

# 배포 시뮬레이션 (실제 배포는 안 됨)
act -j deploy-backend --dry-run
```

## 브랜치 전략

### main 브랜치
- 테스트 통과 후 자동 배포
- 프로덕션 환경

### develop 브랜치
- 테스트만 실행 (배포 안 함)
- 개발 환경

### feature/** 브랜치
- 테스트만 실행
- Pull Request 생성 시 테스트 실행

## 문제 해결

### Firebase 배포 실패

**에러: `Firebase CLI authentication failed`**
- `FIREBASE_TOKEN`이 만료되었을 수 있음
- 새 토큰 생성: `firebase login:ci`

**에러: `Project not found`**
- `FIREBASE_PROJECT_ID` 확인
- `.firebaserc` 파일의 프로젝트 ID와 일치하는지 확인

### Vercel 배포 실패

**에러: `Invalid token`**
- `VERCEL_TOKEN` 확인
- Vercel Dashboard에서 토큰 재생성

**에러: `Project not found`**
- `VERCEL_ORG_ID`와 `VERCEL_PROJECT_ID` 확인
- Vercel Dashboard에서 정확한 값 확인

### 테스트 실패

**Backend 테스트 실패:**
- 로컬에서 테스트 실행: `cd functions && pytest`
- 의존성 문제 확인: `pip install -r requirements.txt`

**Frontend 테스트 실패:**
- 로컬에서 테스트 실행: `cd frontend && npm run test`
- 의존성 문제 확인: `npm install`

## 커스터마이징

### 테스트 커버리지 임계값 설정

`test.yml`에 커버리지 임계값 추가:

```yaml
- name: Run backend tests
  run: |
    pytest --cov=. --cov-fail-under=80
```

### 배포 조건 변경

`deploy.yml`에서 배포 조건 수정:

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### 환경별 배포

스테이징/프로덕션 환경 분리:

```yaml
- name: Deploy to Staging
  if: github.ref == 'refs/heads/develop'
  run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}

- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

## 모니터링

### GitHub Actions 상태 배지

README.md에 추가:

```markdown
![CI](https://github.com/username/repo/workflows/CI/badge.svg)
![Tests](https://github.com/username/repo/workflows/Tests/badge.svg)
```

### 알림 설정

GitHub Repository Settings → Notifications에서:
- Workflow runs 실패 시 이메일 알림
- Slack/Discord 웹훅 연동 (선택사항)

## 다음 단계

1. Secrets 설정 완료
2. 첫 번째 workflow 실행 확인
3. 배포 자동화 검증
4. 모니터링 설정
