@echo off
echo Starting SABnzbd Media Tracker...
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
pip install -r requirements.txt

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
echo Starting services...
echo.

REM Start backend
echo Starting backend on http://localhost:3001...
start "SABnzbd Tracker Backend" python -m backend.main

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend on http://localhost:3000...
cd frontend
start "SABnzbd Tracker Frontend" npm run dev

echo.
echo SABnzbd Media Tracker is running!
echo.
echo Open your browser to: http://localhost:3000
echo.
echo Close the terminal windows to stop the services
echo.
pause
