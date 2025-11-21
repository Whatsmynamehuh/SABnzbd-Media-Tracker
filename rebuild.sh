#!/bin/bash
echo "🛑 Stopping containers..."
docker-compose down

echo "🧹 Removing old images..."
docker-compose rm -f

echo "📁 Ensuring data directory exists..."
mkdir -p data

echo "🔨 Rebuilding images..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

echo ""
echo "✅ Done! Check status with:"
echo "   docker-compose ps"
echo "   docker-compose logs -f backend"
