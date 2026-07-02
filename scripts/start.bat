@echo off
setlocal

set IMAGE_NAME=pm-app
set CONTAINER_NAME=pm-app
set HOST_PORT=8000

cd /d "%~dp0\.."

docker ps -a --format "{{.Names}}" | findstr /b "%CONTAINER_NAME%" >nul
if %errorlevel% equ 0 (
  docker rm -f %CONTAINER_NAME% >nul
  if errorlevel 1 exit /b 1
)

docker build -t %IMAGE_NAME% .
if errorlevel 1 exit /b 1

docker run -d --name %CONTAINER_NAME% -p %HOST_PORT%:8000 %IMAGE_NAME%
if errorlevel 1 exit /b 1

set /a count=0
:wait_loop
set /a count+=1
curl -sf http://localhost:%HOST_PORT%/api/health >nul 2>&1
if %errorlevel% equ 0 (
  echo Started %CONTAINER_NAME% on http://localhost:%HOST_PORT%
  exit /b 0
)
if %count% geq 30 (
  echo ERROR: %CONTAINER_NAME% did not become ready within 15s
  exit /b 1
)
ping -n 2 127.0.0.1 >nul
goto wait_loop
