# GitHub Actions 문제 해결 가이드

## 에러: google-github-actions/auth failed

### 에러 메시지
```
Error: google-github-actions/auth failed with: the GitHub Action workflow must specify exactly one of "workload_identity_provider" or "credentials_json"!
```

### 원인

`deploy.yml`에서 `google-github-actions/auth@v2`를 사용하고 있지만:
1. `GCP_SA_KEY` secret이 설정되지 않았거나
2. Secret이 비어있거나
3. Firebase Functions 배포에는 Google Cloud 인증이 실제로 필요하지 않음

**중요:** Firebase Functions 배포는 **Firebase Token만으로도 가능**합니다. Google Cloud Service Account는 선택사항입니다.

### 해결 방법

#### 방법 1: Google Cloud 인증 제거 (권장)

Firebase Functions 배포에는 Firebase Token만 필요하므로 Google Cloud 인증 단계를 제거합니다.

`deploy.yml`에서 다음 부분을 제거:
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}

- name: Set up Cloud SDK
  uses: google-github-actions/setup-gcloud@v2
```

#### 방법 2: GCP_SA_KEY Secret 설정 (필요한 경우만)

Google Cloud 인증이 필요한 경우에만 설정:

1. **Firebase Console에서 Service Account Key 생성:**
   - Firebase Console → Project Settings → Service Accounts
   - "Generate new private key" 클릭
   - JSON 파일 다운로드

2. **GitHub Secrets에 추가:**
   - Repository → Settings → Secrets and variables → Actions
   - "New repository secret" 클릭
   - Name: `GCP_SA_KEY`
   - Value: 다운로드한 JSON 파일의 전체 내용을 복사하여 붙여넣기

### 권장 설정

Firebase Functions 배포는 `ci.yml`처럼 Firebase Token만 사용하는 것이 더 간단합니다:

```yaml
- name: Install Firebase CLI
  run: npm install -g firebase-tools

- name: Deploy to Firebase Functions
  run: |
    firebase deploy --only functions --token "${{ secrets.FIREBASE_TOKEN }}"
```

## Firebase에서 필요한 설정

### 필수 설정

1. **Firebase 프로젝트 생성** ✅
2. **Firebase Functions 활성화** ✅
3. **Firebase CLI Token 생성** (GitHub Actions용)

### Firebase CLI Token 생성 방법

```bash
# 로컬에서 실행
firebase login:ci

# 출력 예시:
# ✔  Success! Use this token to login on a CI server:
# 
# 1/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 이 토큰을 GitHub Secrets의 FIREBASE_TOKEN에 추가
```

### GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions에서:

1. **FIREBASE_TOKEN** (필수)
   - `firebase login:ci` 명령어로 생성
   - Firebase Functions 배포에 사용

2. **GCP_SA_KEY** (선택사항)
   - Google Cloud Service Account JSON 키
   - Google Cloud 인증이 필요한 경우만 설정
   - Firebase Functions 배포에는 불필요

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
