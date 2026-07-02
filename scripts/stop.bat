@echo off
setlocal

set CONTAINER_NAME=pm-app

docker ps -a --format "{{.Names}}" | findstr /b "%CONTAINER_NAME%" >nul
if %errorlevel% equ 0 (
  docker stop %CONTAINER_NAME%
  if errorlevel 1 exit /b 1
  docker rm %CONTAINER_NAME%
  if errorlevel 1 exit /b 1
  echo Stopped and removed %CONTAINER_NAME%
) else (
  echo %CONTAINER_NAME% is not running
)