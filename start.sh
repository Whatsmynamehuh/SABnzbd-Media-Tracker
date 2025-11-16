#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        SABnzbd Media Tracker - Deployment Options         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Select deployment method:"
echo ""
echo "  1) 🚀 Start in Development Mode (Accessible from network)"
echo "  2) 🐳 Deploy with Docker Compose"
echo "  3) ❌ Exit"
echo ""
read -p "Enter your choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "  Starting in Development Mode..."
        echo "════════════════════════════════════════════════════════════"
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

        # Get local IP address
        if command -v hostname &> /dev/null; then
            LOCAL_IP=$(hostname -I | awk '{print $1}')
        else
            LOCAL_IP=$(ip route get 1 | awk '{print $7}' | head -n1)
        fi

        echo "════════════════════════════════════════════════════════════"
        echo "  🚀 Starting services..."
        echo "════════════════════════════════════════════════════════════"
        echo ""

        # Start backend in background
        echo "🔧 Starting backend API on port 3001..."
        python3 -m backend.main &
        BACKEND_PID=$!

        # Wait a bit for backend to start
        sleep 3

        # Start frontend
        echo "🎨 Starting frontend on port 3000..."
        echo ""
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..

        sleep 3

        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "  ✅ SABnzbd Media Tracker is RUNNING!"
        echo "════════════════════════════════════════════════════════════"
        echo ""
        echo "  📱 Access from this server:"
        echo "     http://localhost:3000"
        echo ""
        echo "  🌐 Access from other devices on your network:"
        echo "     http://$LOCAL_IP:3000"
        echo ""
        echo "  💡 Tip: Bookmark this URL on your phone/tablet!"
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo ""
        echo "Press Ctrl+C to stop all services"
        echo ""

        # Wait for user to stop
        trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
        ;;

    2)
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "  Deploying with Docker Compose..."
        echo "════════════════════════════════════════════════════════════"
        echo ""

        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "❌ Error: Docker is not installed!"
            echo "Please install Docker first: https://docs.docker.com/get-docker/"
            exit 1
        fi

        # Check if docker-compose is installed
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo "❌ Error: Docker Compose is not installed!"
            echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
            exit 1
        fi

        # Check if config.yml exists
        if [ ! -f "config.yml" ]; then
            echo "❌ Error: config.yml not found!"
            echo "Please copy config.example.yml to config.yml and configure it."
            echo ""
            echo "Run: cp config.example.yml config.yml"
            exit 1
        fi

        echo "🐳 Building and starting Docker containers..."
        echo ""

        # Use docker-compose or docker compose
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d --build
        else
            docker compose up -d --build
        fi

        # Get local IP address
        if command -v hostname &> /dev/null; then
            LOCAL_IP=$(hostname -I | awk '{print $1}')
        else
            LOCAL_IP=$(ip route get 1 | awk '{print $7}' | head -n1)
        fi

        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "  ✅ Docker containers are RUNNING!"
        echo "════════════════════════════════════════════════════════════"
        echo ""
        echo "  📱 Access from this server:"
        echo "     http://localhost:3000"
        echo ""
        echo "  🌐 Access from other devices on your network:"
        echo "     http://$LOCAL_IP:3000"
        echo ""
        echo "  📊 Backend API:"
        echo "     http://$LOCAL_IP:3001/api/downloads"
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo ""
        echo "Useful commands:"
        echo "  • View logs:    docker-compose logs -f"
        echo "  • Stop:         docker-compose down"
        echo "  • Restart:      docker-compose restart"
        echo ""
        ;;

    3)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;

    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
