#!/bin/bash

echo "🚀 Starting SABnzbd Media Tracker..."
echo ""

# Check if config.yml exists
if [ ! -f "config.yml" ]; then
    echo "❌ Error: config.yml not found!"
    echo "Please copy config.example.yml to config.yml and configure it."
    echo ""
    echo "Run: cp config.example.yml config.yml"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed!"
    exit 1
fi

# Check if backend dependencies are installed
echo "📦 Checking backend dependencies..."
pip3 install -q -r requirements.txt

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "Starting services..."
echo ""

# Start backend in background
echo "🔧 Starting backend on http://localhost:3001..."
python3 -m backend.main &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ SABnzbd Media Tracker is running!"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
