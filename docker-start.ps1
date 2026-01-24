# IntelliDesk AI - Docker Quick Start
# This script builds and runs the entire application using Docker

Write-Host "Starting IntelliDesk AI with Docker..." -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.docker" ".env"
    Write-Host ""
    Write-Host "IMPORTANT: Edit .env file and add your GEMINI_API_KEY" -ForegroundColor Red
    Write-Host "Get your key from: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Press Enter when you've added your API key (or Ctrl+C to exit)"
}

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Cyan
$dockerCheck = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker is running!" -ForegroundColor Green
Write-Host ""

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor Cyan
Write-Host "This may take a few minutes on first run..." -ForegroundColor Yellow
Write-Host ""

docker-compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "IntelliDesk AI is starting!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "Application URLs:" -ForegroundColor Cyan
    Write-Host "  Dashboard:      http://localhost:3000" -ForegroundColor Green
    Write-Host "  API Docs:       http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "  Health Check:   http://localhost:8000/health" -ForegroundColor Green
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  View logs:      docker-compose logs -f" -ForegroundColor Gray
    Write-Host "  Stop:           docker-compose down" -ForegroundColor Gray
    Write-Host "  Restart:        docker-compose restart" -ForegroundColor Gray
    Write-Host "  Rebuild:        docker-compose up --build" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to start containers!" -ForegroundColor Red
    Write-Host "Check the error messages above." -ForegroundColor Yellow
    exit 1
}
