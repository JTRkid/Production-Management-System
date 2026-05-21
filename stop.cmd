@echo off
chcp 936 >nul
echo  正在停止服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
    echo  后端已停止
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
    echo  前端已停止
)
echo  服务已停止
pause
