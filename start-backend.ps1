# Backend 서버 시작 스크립트
Write-Host "Backend 서버를 시작합니다..." -ForegroundColor Green

cd functions

# 가상환경 활성화
if (Test-Path venv\Scripts\Activate.ps1) {
    Write-Host "가상환경 활성화 중..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "가상환경이 없습니다. 생성 중..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    Write-Host "의존성 설치 중..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 서버 실행
Write-Host "Backend 서버 실행 중 (http://localhost:8000)..." -ForegroundColor Green
uvicorn main:app --reload --port 8000
