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

## 추가 참고사항

- Firebase Token은 만료되지 않지만, 필요시 재생성 가능
- Google Cloud Service Account는 Cloud Run 배포나 다른 GCP 서비스 사용 시에만 필요
- Firebase Functions는 Firebase 자체 인증 시스템을 사용하므로 GCP 인증 불필요
