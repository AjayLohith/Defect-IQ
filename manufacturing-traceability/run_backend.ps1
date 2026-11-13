# PowerShell script to run the Python backend directly on Windows
Write-Host "=== Starting TraceFlow Python Backend (FastAPI) ===" -ForegroundColor Cyan

if (Test-Path ".\backend\requirements.txt") {
    Write-Host "Checking / installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install -r backend/requirements.txt
}

$env:DATABASE_URL = "postgresql://traceflow_user:traceflow_secure_password@localhost:5432/traceflow_db"
$env:ENVIRONMENT = "development"
$env:GENERATOR_SEED = "20261022"
$env:GENERATOR_PROFILE = "full"
$env:ARTIFACTS_DIR = "artifacts"
$env:PYTHONPATH = "."

Write-Host "Starting Uvicorn on http://localhost:8000 (Swagger: http://localhost:8000/docs)..." -ForegroundColor Green
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

