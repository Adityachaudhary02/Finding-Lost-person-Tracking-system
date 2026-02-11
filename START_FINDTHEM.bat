@echo off
REM Start FindThem application
REM This batch file starts MySQL and the backend server

echo.
echo ================================
echo  FindThem - Starting Services
echo ================================
echo.

REM Check if MySQL is running
echo Checking MySQL service...
sc query MySQL80 | find "RUNNING" > nul
if %errorlevel% neq 0 (
    echo Starting MySQL service...
    net start MySQL80
    timeout /t 3
) else (
    echo MySQL service is already running
)

echo.
echo Starting FindThem Backend...
cd /d "%~dp0backend"
python main.py

pause
