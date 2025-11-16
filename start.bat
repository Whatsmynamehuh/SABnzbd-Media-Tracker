@echo off
cls
echo ================================================================
echo         SABnzbd Media Tracker - Deployment Options
echo ================================================================
echo.
echo Select deployment method:
echo.
echo   1. Start in Development Mode (Accessible from network)
echo   2. Deploy with Docker Compose
echo   3. Exit
echo.
set /p choice="Enter your choice [1-3]: "

if "%choice%"=="1" goto devmode
if "%choice%"=="2" goto docker
if "%choice%"=="3" goto exit
goto invalid

:devmode
echo.
echo ================================================================
echo   Starting in Development Mode...
echo ================================================================
echo.

REM Check if config.yml exists
if not exist "config.yml" (
    echo Error: config.yml not found!
    echo Please copy config.example.yml to config.yml and configure it.
    echo.
    echo Run: copy config.example.yml config.yml
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed!
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed!
    pause
    exit /b 1
)

REM Install backend dependencies
echo Installing backend dependencies...
pip install -q -r requirements.txt

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo All dependencies installed!
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP:~1%

echo ================================================================
echo   Starting services...
echo ================================================================
echo.

REM Start backend
echo Starting backend API on port 3001...
start "SABnzbd Tracker Backend" python -m backend.main

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend on port 3000...
cd frontend
start "SABnzbd Tracker Frontend" npm run dev

timeout /t 3 /nobreak >nul

echo.
echo ================================================================
echo   SABnzbd Media Tracker is RUNNING!
echo ================================================================
echo.
echo   Access from this computer:
echo      http://localhost:3000
echo.
echo   Access from other devices on your network:
echo      http://%LOCAL_IP%:3000
echo.
echo   Tip: Bookmark this URL on your phone/tablet!
echo.
echo ================================================================
echo.
echo Close the terminal windows to stop the services
echo.
pause
exit /b 0

:docker
echo.
echo ================================================================
echo   Deploying with Docker Compose...
echo ================================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed!
    echo Please install Docker Desktop: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if config.yml exists
if not exist "config.yml" (
    echo Error: config.yml not found!
    echo Please copy config.example.yml to config.yml and configure it.
    echo.
    echo Run: copy config.example.yml config.yml
    pause
    exit /b 1
)

echo Building and starting Docker containers...
echo.
docker-compose up -d --build

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP:~1%

echo.
echo ================================================================
echo   Docker containers are RUNNING!
echo ================================================================
echo.
echo   Access from this computer:
echo      http://localhost:3000
echo.
echo   Access from other devices on your network:
echo      http://%LOCAL_IP%:3000
echo.
echo   Backend API:
echo      http://%LOCAL_IP%:3001/api/downloads
echo.
echo ================================================================
echo.
echo Useful commands:
echo   - View logs:    docker-compose logs -f
echo   - Stop:         docker-compose down
echo   - Restart:      docker-compose restart
echo.
pause
exit /b 0

:exit
echo.
echo Goodbye!
exit /b 0

:invalid
echo.
echo Invalid choice. Please run the script again.
pause
exit /b 1
