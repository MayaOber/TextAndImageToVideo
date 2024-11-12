@echo off
echo Starting Text to Video Generator Demo...
echo.
echo Please make sure Docker Desktop is running!
echo.
echo Checking Docker status...
docker --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running or not installed!
    echo Please make sure Docker Desktop is installed and running.
    echo You can download it from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo Docker is running!
echo.
echo Starting the application...
docker-compose up --build
