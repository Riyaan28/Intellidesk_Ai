#!/bin/bash
# IntelliDesk AI - Docker Quick Start
# This script builds and runs the entire application using Docker

echo "🚀 Starting IntelliDesk AI with Docker..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.docker .env
    echo ""
    echo "❗ IMPORTANT: Edit .env file and add your GEMINI_API_KEY"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter when you've added your API key (or Ctrl+C to exit)"
fi

# Check if Docker is running
echo "🔍 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running!"
    echo "   Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running!"
echo ""

# Build and start containers
echo "🔨 Building and starting containers..."
echo "   This may take a few minutes on first run..."
echo ""

docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ IntelliDesk AI is starting!"
    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "📊 Application URLs:"
    echo "  🌐 Dashboard:      http://localhost:3000"
    echo "  📚 API Docs:       http://localhost:8000/docs"
    echo "  🏥 Health Check:   http://localhost:8000/health"
    echo ""
    echo "💡 Useful commands:"
    echo "  📋 View logs:      docker-compose logs -f"
    echo "  🛑 Stop:           docker-compose down"
    echo "  🔄 Restart:        docker-compose restart"
    echo "  🔨 Rebuild:        docker-compose up --build"
    echo ""
else
    echo ""
    echo "❌ ERROR: Failed to start containers!"
    echo "   Check the error messages above."
    exit 1
fi
