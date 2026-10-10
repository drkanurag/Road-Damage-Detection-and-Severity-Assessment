@echo off
setlocal
cd /d "%~dp0"
echo ============================================================================
echo   ROADVISION ENTERPRISE - 1-CLICK WEBSITE LAUNCHER
echo ============================================================================

REM Check if local server on port 8000 is already listening
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Local Microservices Gateway is already running on http://127.0.0.1:8000
    start "" "http://127.0.0.1:8000"
    exit /b 0
)

REM Try virtual environment Python first, then system Python
set "VENV_PY=C:\Users\anura\OneDrive - Manipal Academy of Higher Education\Desktop\Road Damage Detection and Severity Assessment\.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    echo [INFO] Starting 5-Service Microservices Cluster in background...
    start "RoadVision Microservices" /MIN "%VENV_PY%" run_microservices.py
    timeout /t 4 /nobreak >nul
    start "" "http://127.0.0.1:8000"
    exit /b 0
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Starting RoadVision Microservices Cluster with system Python...
    start "RoadVision Microservices" /MIN python run_microservices.py
    timeout /t 4 /nobreak >nul
    start "" "http://127.0.0.1:8000"
    exit /b 0
)

REM Fallback: Open static/index.html directly in Instant Browser Mode
echo [INFO] Opening RoadVision Command Center in Instant Browser Mode...
start "" "%~dp0static\index.html"
exit /b 0

