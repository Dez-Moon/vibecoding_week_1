@echo off
setlocal

cd /d "%~dp0\.."

docker build -t pm-app .
if errorlevel 1 exit /b 1

docker run -d --name pm-app -p 8000:8000 pm-app
if errorlevel 1 exit /b 1

echo Started pm-app on http://localhost:8000
