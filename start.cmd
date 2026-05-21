@echo off
chcp 936 >nul
echo.
echo  [1/2] Starting backend  http://localhost:8000 ...
cd /d "%~dp0backend"
start "Backend" "%~dp0venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
echo  [2/2] Starting frontend http://localhost:3000 ...
cd /d "%~dp0frontend"
start "Frontend" npm run dev
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
