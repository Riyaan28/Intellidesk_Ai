# IntelliDesk AI - Quick Start Script
# Run this script to start the entire application

Write-Host "Starting IntelliDesk AI..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    Write-Host "Running: python -m venv backend\venv" -ForegroundColor Gray
    python -m venv backend\venv
    
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    & backend\venv\Scripts\Activate.ps1
    pip install -r backend\requirements.txt
    pip install -r ai\requirements.txt
    deactivate
}

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host ".env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host ""
    Write-Host "IMPORTANT: Edit backend\.env and add your GEMINI_API_KEY" -ForegroundColor Red
    Write-Host "   Get your key from: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Press Enter when you've added your API key (or Ctrl+C to exit)"
}

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    Pop-Location
}

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Cyan
& backend\venv\Scripts\Activate.ps1
Set-Location backend
python -c "from database import init_db; init_db(); print('Database initialized')"
Set-Location ..
deactivate

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host ""

# Start backend in new window
Write-Host "Starting Backend (http://localhost:8000)..." -ForegroundColor Yellow
$backendScript = @"
Set-Location '$PWD'
Write-Host 'Backend Server Running' -ForegroundColor Green
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan
& .\backend\venv\Scripts\python.exe run_backend.py
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window  
Write-Host "Starting Frontend (http://localhost:3000)..." -ForegroundColor Yellow
$frontendScript = @"
Set-Location '$PWD\frontend'
Write-Host 'Frontend Server Running' -ForegroundColor Green
Write-Host 'Dashboard: http://localhost:3000' -ForegroundColor Cyan
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "IntelliDesk AI is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard:      http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs:       http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test the system:" -ForegroundColor Yellow
Write-Host "   1. Go to http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   2. Try the /api/test-email endpoint" -ForegroundColor Gray
Write-Host "   3. Check dashboard at http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C in the backend/frontend windows to stop servers" -ForegroundColor Gray
