# Frontend 개발 서버 시작 스크립트
Write-Host "Frontend 개발 서버를 시작합니다..." -ForegroundColor Green

cd frontend

# 환경 변수 확인
if (-not (Test-Path .env.local)) {
    Write-Host "경고: .env.local 파일이 없습니다." -ForegroundColor Yellow
    Write-Host "frontend/.env.local 파일을 생성하고 Firebase 설정을 추가하세요." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "예시:" -ForegroundColor Cyan
    Write-Host "VITE_API_BASE_URL=" -ForegroundColor Cyan
    Write-Host "VITE_FIREBASE_API_KEY=your_api_key" -ForegroundColor Cyan
    Write-Host "VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com" -ForegroundColor Cyan
    Write-Host "VITE_FIREBASE_PROJECT_ID=your_project_id" -ForegroundColor Cyan
    Write-Host "VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com" -ForegroundColor Cyan
    Write-Host "VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id" -ForegroundColor Cyan
    Write-Host "VITE_FIREBASE_APP_ID=your_app_id" -ForegroundColor Cyan
    Write-Host ""
}

# 개발 서버 실행
Write-Host "Frontend 개발 서버 실행 중 (http://localhost:5173)..." -ForegroundColor Green
npm run dev
