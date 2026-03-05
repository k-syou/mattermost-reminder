# Firebase Service Account 권한 설정 가이드

Firebase Functions 배포를 위한 Service Account 권한 설정 방법입니다.

## 문제 상황

```
Error: Missing permissions required for functions deploy. 
You must have permission iam.serviceAccounts.ActAs on service account 
mattermost-reminder@appspot.gserviceaccount.com.
```

## 해결 방법

### 1단계: Google Cloud Console 접속

1. [Google Cloud Console IAM 페이지](https://console.cloud.google.com/iam-admin/iam) 접속
2. 프로젝트 선택: `mattermost-reminder` (또는 사용 중인 프로젝트)

### 2단계: Service Account 찾기

IAM 페이지에서 다음 중 하나를 찾습니다:

1. **App Engine 기본 Service Account:**
   - 이메일: `{project-id}@appspot.gserviceaccount.com`
   - 예: `mattermost-reminder@appspot.gserviceaccount.com`

2. **Firebase에서 생성한 Service Account:**
   - Firebase Console → Project Settings → Service Accounts에서 확인
   - "Manage service account permissions" 클릭하여 Google Cloud Console로 이동

### 3단계: 권한 부여

#### 방법 1: Google Cloud Console에서 직접 추가

1. IAM 페이지에서 Service Account 행 찾기
2. 행 끝의 "편집" (연필 아이콘) 클릭
3. "역할 추가" 클릭
4. 다음 역할 선택:
   - **Service Account User** (필수)
   - **Cloud Functions Admin** (권장)
5. "저장" 클릭

#### 방법 2: Firebase Console에서 이동

1. Firebase Console → Project Settings → Service Accounts
2. "Manage service account permissions" 클릭
3. Google Cloud Console IAM 페이지로 이동
4. 위의 방법 1과 동일하게 권한 추가

### 4단계: 필요한 역할

Firebase Functions 배포를 위해 다음 역할이 필요합니다:

#### 필수 역할

1. **Service Account User**
   - 역할 ID: `roles/iam.serviceAccountUser`
   - Service Account를 대신하여 작업 수행

#### 권장 역할

2. **Cloud Functions Admin**
   - 역할 ID: `roles/cloudfunctions.admin`
   - Cloud Functions 생성, 업데이트, 삭제

3. **Storage Admin** (선택사항)
   - 역할 ID: `roles/storage.admin`
   - Functions 소스 코드 업로드용

#### 간단한 방법 (개발 환경용)

**Editor** 역할 부여:
- 역할 ID: `roles/editor`
- 모든 리소스에 대한 편집 권한 (개발 환경에 적합)

### 5단계: 권한 확인

권한 부여 후 몇 분 정도 기다린 후 다시 배포 시도:

```bash
firebase deploy --only functions
```

## Service Account Key 생성 방법

### Firebase Console에서 생성

1. Firebase Console → Project Settings → Service Accounts
2. "Generate new private key" 버튼 클릭
3. 경고 확인 후 "키 생성" 클릭
4. JSON 파일 다운로드
5. GitHub Secrets에 `GCP_SA_KEY`로 추가

### Google Cloud Console에서 생성

1. Google Cloud Console → IAM & Admin → Service Accounts
2. Service Account 선택 (또는 새로 생성)
3. "Keys" 탭 → "Add Key" → "Create new key"
4. JSON 형식 선택
5. 다운로드한 JSON 파일을 GitHub Secrets에 추가

## 권한 부여 대상

### App Engine 기본 Service Account

- 이메일: `{project-id}@appspot.gserviceaccount.com`
- Firebase Functions 배포 시 기본으로 사용되는 Service Account

### 사용자 생성 Service Account

- Firebase Console에서 생성한 Service Account
- 이메일 형식: `{service-account-name}@{project-id}.iam.gserviceaccount.com`

## 문제 해결

### ⚠️ 중요: 권한 부여 대상 확인

**에러 메시지가 `mattermost-reminder@appspot.gserviceaccount.com`에 대한 권한을 요구하는 경우:**

이것은 **App Engine 기본 Service Account**입니다. 이 계정에 역할을 부여하는 것이 아니라, **GitHub Actions에서 사용하는 Service Account**가 이 계정을 사용할 수 있도록 권한을 부여해야 합니다.

#### 올바른 권한 부여 방법

1. **GitHub Actions에서 사용하는 Service Account 확인:**
   - `GCP_SA_KEY`에 저장된 JSON 파일을 열어서 `client_email` 필드 확인
   - 예: `firebase-adminsdk-xxxxx@mattermost-reminder.iam.gserviceaccount.com`

2. **Google Cloud Console IAM 페이지 접속:**
   - [IAM 페이지](https://console.cloud.google.com/iam-admin/iam?project=mattermost-reminder)

3. **올바른 Service Account 찾기:**
   - `GCP_SA_KEY`의 `client_email`에 해당하는 Service Account 찾기
   - **이 Service Account에** 권한을 부여해야 합니다

4. **권한 부여:**
   - Service Account 행의 "편집" (연필 아이콘) 클릭
   - "역할 추가" 클릭
   - 다음 역할 선택:
     - **Service Account User** (필수) - `mattermost-reminder@appspot.gserviceaccount.com`을 사용할 수 있도록
     - **Cloud Functions Admin** (권장)
   - "저장" 클릭

#### 잘못된 방법 (현재 시도한 방법)

❌ `mattermost-reminder@appspot.gserviceaccount.com`에 소유자 역할 부여
- 이 계정은 App Engine 기본 Service Account로, Firebase Functions 배포 시 사용되는 계정입니다
- 이 계정에 역할을 부여하는 것은 의미가 없습니다

#### 올바른 방법

✅ GitHub Actions에서 사용하는 Service Account에 권한 부여
- `GCP_SA_KEY`의 `client_email`에 해당하는 Service Account
- 이 Service Account가 `mattermost-reminder@appspot.gserviceaccount.com`을 사용할 수 있도록 권한 부여

### 권한 부여 후에도 에러가 발생하는 경우

1. **권한 전파 대기:**
   - 권한 변경 후 최대 5-10분 정도 기다림
   - Google Cloud IAM 변경사항이 전파되는데 시간이 걸림

2. **Service Account 확인:**
   - `GCP_SA_KEY`의 `client_email`과 IAM에서 찾은 Service Account가 일치하는지 확인
   - 올바른 Service Account에 권한을 부여했는지 확인

3. **프로젝트 확인:**
   - `.firebaserc`의 프로젝트 ID와 Google Cloud Console의 프로젝트가 일치하는지 확인

4. **권한 재확인:**
   - IAM 페이지에서 Service Account의 역할 목록 확인
   - **Service Account User** 역할이 있는지 확인

5. **Service Account Key 재생성 (최후의 수단):**
   - Firebase Console → Project Settings → Service Accounts
   - 기존 키 삭제 후 새 키 생성
   - GitHub Secrets의 `GCP_SA_KEY` 업데이트

## 참고 링크

- [Google Cloud IAM 역할](https://cloud.google.com/iam/docs/understanding-roles)
- [Firebase Functions 권한](https://firebase.google.com/docs/functions/deploy#required_iam_permissions)
- [Service Account 사용](https://cloud.google.com/iam/docs/service-accounts)
