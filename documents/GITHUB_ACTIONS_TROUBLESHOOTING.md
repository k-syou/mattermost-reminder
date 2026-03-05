# GitHub Actions 문제 해결 가이드

## 에러 1: google-github-actions/auth failed

### 에러 메시지
```
Error: google-github-actions/auth failed with: the GitHub Action workflow must specify exactly one of "workload_identity_provider" or "credentials_json"!
```

### 원인

`google-github-actions/auth@v2`를 사용할 때:
1. `GCP_SA_KEY` secret이 설정되지 않았거나
2. Secret이 비어있거나
3. `credentials_json` 파라미터가 올바르게 전달되지 않음

## 에러 2: Missing virtual environment at venv directory

### 에러 메시지
```
Error: Failed to find location of Firebase Functions SDK: Missing virtual environment at venv directory. Did you forget to run 'python3.11 -m venv venv'?
```

### 원인

Firebase Functions는 Python Functions를 배포할 때 가상환경(`venv`)을 찾습니다. GitHub Actions에서 가상환경을 생성하지 않으면 이 에러가 발생합니다.

### 해결 방법

GitHub Actions workflow에서 가상환경을 생성해야 합니다:

```yaml
- name: Create virtual environment
  working-directory: ./functions
  run: |
    python3.11 -m venv venv

- name: Install dependencies
  working-directory: ./functions
  run: |
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

## Firebase Functions 배포 인증 방법

### 방법 1: Service Account Key 사용 (권장)

`--token` 방식이 deprecated 되었으므로 Service Account Key를 사용하는 것이 권장됩니다.

### 해결 방법

#### Service Account Key 설정 (필수)

Firebase Functions 배포를 위해 Service Account Key가 필요합니다:

1. **Firebase Console에서 Service Account Key 생성:**
   - Firebase Console → Project Settings → Service Accounts
   - "Generate new private key" 클릭
   - JSON 파일 다운로드

2. **GitHub Secrets에 추가:**
   - Repository → Settings → Secrets and variables → Actions
   - "New repository secret" 클릭
   - Name: `GCP_SA_KEY`
   - Value: 다운로드한 JSON 파일의 전체 내용을 복사하여 붙여넣기
   - ⚠️ **주의**: JSON 전체 내용을 한 줄로 붙여넣어야 합니다

### 권장 설정

가상환경 생성 + Service Account Key 인증:

```yaml
- name: Create virtual environment
  working-directory: ./functions
  run: |
    python3.11 -m venv venv

- name: Install dependencies
  working-directory: ./functions
  run: |
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt

- name: Install Firebase CLI
  run: npm install -g firebase-tools

- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}

- name: Deploy to Firebase Functions
  working-directory: ./functions
  run: |
    firebase deploy --only functions
```

## Firebase에서 필요한 설정

### 필수 설정

1. **Firebase 프로젝트 생성** ✅
2. **Firebase Functions 활성화** ✅
3. **Service Account Key 생성** (GitHub Actions용)

### Service Account Key 생성 방법

1. **Firebase Console 접속:**
   - [Firebase Console](https://console.firebase.google.com/)
   - 프로젝트 선택

2. **Service Account 페이지로 이동:**
   - 좌측 메뉴 → ⚙️ Project Settings
   - "Service accounts" 탭 클릭

3. **새 비공개 키 생성:**
   - "Generate new private key" 버튼 클릭
   - 경고 확인 후 "키 생성" 클릭
   - JSON 파일이 자동으로 다운로드됨

4. **GitHub Secrets에 추가:**
   - Repository → Settings → Secrets and variables → Actions
   - "New repository secret" 클릭
   - Name: `GCP_SA_KEY`
   - Value: 다운로드한 JSON 파일의 전체 내용 복사/붙여넣기

### GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions에서:

1. **GCP_SA_KEY** (필수)
   - Firebase Console에서 생성한 Service Account JSON 키
   - Google Cloud 인증 및 Firebase Functions 배포에 사용

2. **FIREBASE_TOKEN** (선택사항, deprecated)
   - `firebase login:ci` 명령어로 생성
   - `--token` 방식이 deprecated 되었으므로 Service Account Key 사용 권장

## 수정된 deploy.yml

Google Cloud 인증을 제거한 버전:

```yaml
deploy-backend:
  name: Deploy Backend to Firebase Functions
  runs-on: ubuntu-latest
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      working-directory: ./functions
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install Firebase CLI
      run: npm install -g firebase-tools
    
    - name: Deploy to Firebase Functions
      run: |
        firebase deploy --only functions --token "${{ secrets.FIREBASE_TOKEN }}"
```

## 확인 사항

### Firebase에서 확인할 것

1. ✅ Firebase 프로젝트가 생성되어 있음
2. ✅ Firebase Functions가 활성화되어 있음
3. ✅ `.firebaserc` 파일의 프로젝트 ID가 올바름
4. ✅ `firebase.json`에 Functions 설정이 있음

### GitHub에서 확인할 것

1. ✅ `FIREBASE_TOKEN` secret이 설정되어 있음
2. ✅ Secret 값이 올바른지 확인 (토큰이 만료되지 않았는지)

## 에러 3: Vercel token not supplied

### 에러 메시지
```
Error: Input required and not supplied: vercel-token
```

### 원인

`amondnet/vercel-action@v25`를 사용할 때:
1. `VERCEL_TOKEN` secret이 설정되지 않았거나
2. Secret이 비어있거나
3. Secret이 workflow에 전달되지 않음

### 해결 방법

#### 방법 1: Vercel Secrets 설정 (권장)

1. **Vercel Token 생성:**
   - [Vercel Dashboard](https://vercel.com/account/tokens) 접속
   - "Create Token" 클릭
   - Token 이름 입력 (예: "GitHub Actions")
   - Scope: Full Account 선택
   - 생성된 토큰 복사

2. **GitHub Secrets에 추가:**
   - Repository → Settings → Secrets and variables → Actions
   - "New repository secret" 클릭
   - Name: `VERCEL_TOKEN`
   - Value: 생성한 토큰 붙여넣기

3. **Vercel Org ID 및 Project ID 확인:**
   - Vercel Dashboard → 프로젝트 → Settings → General
   - Org ID와 Project ID 확인
   - 각각 `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`로 GitHub Secrets에 추가

#### 방법 2: 조건부 배포 (Secrets가 없을 때 스킵)

Secrets가 설정되지 않은 경우 배포를 스킵하도록 설정:

```yaml
deploy-frontend:
  name: Deploy Frontend to Vercel
  runs-on: ubuntu-latest
  if: secrets.VERCEL_TOKEN != ''
  
  steps:
    # ... 배포 steps
```

이렇게 하면 `VERCEL_TOKEN`이 없을 때 job이 스킵됩니다.

## 에러 4: Missing permissions for functions deploy (소유자 역할 부여해도 실패)

### 에러 메시지
```
Error: Missing permissions required for functions deploy. 
You must have permission iam.serviceAccounts.ActAs on service account 
mattermost-reminder@appspot.gserviceaccount.com.
```

### ⚠️ 중요: 올바른 Service Account에 권한 부여

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
- 소유자 역할을 부여해도 `iam.serviceAccounts.ActAs` 권한이 해결되지 않습니다

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

3. **Service Account Key 재생성 (최후의 수단):**
   - Firebase Console → Project Settings → Service Accounts
   - 기존 키 삭제 후 새 키 생성
   - GitHub Secrets의 `GCP_SA_KEY` 업데이트

자세한 내용은 [`FIREBASE_SERVICE_ACCOUNT_SETUP.md`](FIREBASE_SERVICE_ACCOUNT_SETUP.md)를 참고하세요.

## 추가 참고사항

- Firebase Token은 만료되지 않지만, 필요시 재생성 가능
- Google Cloud Service Account는 Firebase Functions 배포에 필수
- Service Account에 적절한 IAM 역할이 부여되어야 함
- Vercel 배포는 Secrets가 설정되지 않으면 자동으로 스킵됩니다