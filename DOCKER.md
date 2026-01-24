# 🐳 Docker Deployment Guide

## Quick Start (One Command!)

### Windows (PowerShell):

```powershell
.\docker-start.ps1
```

### Linux/Mac:

```bash
chmod +x docker-start.sh
./docker-start.sh
```

Or manually:

```bash
docker-compose up --build -d
```

## Prerequisites

1. **Install Docker Desktop**
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/

2. **Get Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Copy your API key

3. **Configure Environment**

   ```bash
   # Copy template
   cp .env.docker .env

   # Edit .env and add your GEMINI_API_KEY
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## What Gets Created

The Docker setup creates:

- ✅ **Backend Container** (Python FastAPI) - Port 8000
- ✅ **Frontend Container** (React + Vite) - Port 3000
- ✅ **SQLite Database** (Persistent volume)
- ✅ **Network** (All containers connected)

## Access the Application

After running `docker-compose up`:

- 🌐 **Dashboard**: http://localhost:3000
- 📚 **API Docs**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/health

## Useful Commands

### Start Application

```bash
docker-compose up -d                 # Start in background
docker-compose up --build           # Rebuild and start
```

### Monitor Application

```bash
docker-compose logs -f              # View all logs
docker-compose logs -f backend      # View backend logs only
docker-compose logs -f frontend     # View frontend logs only
```

### Manage Containers

```bash
docker-compose ps                   # List running containers
docker-compose stop                 # Stop containers
docker-compose start                # Start stopped containers
docker-compose restart              # Restart containers
docker-compose down                 # Stop and remove containers
docker-compose down -v              # Stop and remove with volumes
```

### Debugging

```bash
# Execute commands inside backend container
docker-compose exec backend python -c "from database import init_db; init_db()"

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Check container status
docker-compose ps
docker-compose logs backend
```

### Database Management

```bash
# Initialize database
docker-compose exec backend python -c "from database import init_db; init_db()"

# Backup database
docker cp intellidesk-backend:/app/backend/data/intellidesk.db ./backup.db

# Restore database
docker cp ./backup.db intellidesk-backend:/app/backend/data/intellidesk.db
```

## Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up --build -d
```

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Remove and rebuild
docker-compose down -v
docker-compose up --build
```

### Database Issues

```bash
# Reset database (removes all data!)
docker-compose down -v
docker-compose up --build
```

### Permission Issues (Linux)

```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

## Production Deployment

For production, update [docker-compose.yml](docker-compose.yml):

```yaml
services:
  backend:
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/intellidesk # Use PostgreSQL
      SECRET_KEY: long-random-secret-key-here
    restart: always

  frontend:
    build:
      target: production # Use production build
    restart: always
```

## Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Network                  │
│  ┌────────────┐         ┌─────────────┐    │
│  │  Frontend  │────────▶│   Backend   │    │
│  │  (Port     │         │  (Port      │    │
│  │   3000)    │         │   8000)     │    │
│  └────────────┘         └──────┬──────┘    │
│                                 │           │
│                         ┌───────▼───────┐   │
│                         │  SQLite DB    │   │
│                         │  (Volume)     │   │
│                         └───────────────┘   │
└─────────────────────────────────────────────┘
```

## Benefits

✅ **One Command Setup** - No manual dependency installation
✅ **Isolated Environment** - No conflicts with system packages
✅ **Consistent Across Machines** - Works on any OS with Docker
✅ **Easy Updates** - Just rebuild containers
✅ **Simple Backup** - Volume management for data persistence
✅ **Production Ready** - Easy to deploy to cloud platforms

## Cloud Deployment

### Deploy to DigitalOcean

```bash
# Install doctl
# Create app
doctl apps create --spec docker-compose.yml
```

### Deploy to AWS ECS

```bash
# Use ecs-cli
ecs-cli compose up
```

### Deploy to Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/intellidesk
gcloud run deploy --image gcr.io/PROJECT_ID/intellidesk
```

## Support

For issues or questions:

- Check logs: `docker-compose logs`
- Restart: `docker-compose restart`
- Clean rebuild: `docker-compose down -v && docker-compose up --build`
