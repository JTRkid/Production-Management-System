@echo off
echo.
echo  Cleaning up old processes ...
powershell -NoProfile -Command "Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-NetTCPConnection -State Listen -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
timeout /t 2 /nobreak >nul
echo  [1/2] Starting backend  http://localhost:8000 ...
cd /d "%~dp0backend"
start "Backend" "%~dp0venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
echo  [2/2] Starting frontend http://localhost:3000 ...
cd /d "%~dp0frontend"
start "Frontend" cmd /c "npm run dev"
echo.
echo  Waiting ...
timeout /t 6 /nobreak >nul
start "" http://localhost:3000
echo.
echo  ================================
echo   http://localhost:3000
echo   admin / 123456
echo   Close Backend/Frontend windows to stop.
echo  ================================
echo.
pause
