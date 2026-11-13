# Run from inside the backend directory
Write-Host "=== Starting TraceFlow Python Backend ===" -ForegroundColor Cyan

if (Test-Path ".\requirements.txt") {
    Write-Host "Checking / installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

$env:DATABASE_URL = "postgresql://traceflow_user:traceflow_secure_password@localhost:5432/traceflow_db"
$env:ENVIRONMENT = "development"
$env:GENERATOR_SEED = "20261022"
$env:GENERATOR_PROFILE = "full"
$env:ARTIFACTS_DIR = "..\artifacts"
$env:PYTHONPATH = ".."

Write-Host "Starting Uvicorn on http://localhost:8000 (Swagger: http://localhost:8000/docs)..." -ForegroundColor Green
cd ..
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

