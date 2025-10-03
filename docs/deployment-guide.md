# Deployment Guide

**Nx System Calculator - Production Deployment**

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Production Checklist](#production-checklist)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying the Nx System Calculator in various environments:

- **Local Development**: Quick setup for development
- **Docker**: Containerized deployment with Docker Compose
- **Cloud Platforms**: AWS, Azure, Google Cloud Platform
- **Traditional Servers**: Ubuntu/Debian, CentOS/RHEL

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- OS: Ubuntu 20.04+, Debian 11+, CentOS 8+, or Docker

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- **Python**: 3.11 or higher
- **Node.js**: 20 LTS or higher
- **PostgreSQL**: 15+ (production)
- **Nginx**: Latest stable (reverse proxy)
- **Docker**: 24+ and Docker Compose 2+ (for containerized deployment)

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/networkoptix/nx_system_calc.git
cd nx_system_calc

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Install dependencies and start
./run.sh setup
./run.sh dev
```

### Manual Setup

**Backend:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Using Docker Compose (Recommended)

**1. Prepare Environment**

```bash
# Clone repository
git clone https://github.com/networkoptix/nx_system_calc.git
cd nx_system_calc

# Create environment file
cp .env.example .env
```

**2. Configure Environment**

Edit `.env`:
```bash
# Database
DATABASE_URL=postgresql://nx_user:nx_password@db:5432/nx_calculator

# Email (required for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@networkoptix.com
SMTP_BCC=sales@networkoptix.com

# Security
SECRET_KEY=$(openssl rand -hex 32)

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**3. Start Services**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

**4. Access Application**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Docker Compose

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: nx-calculator-backend
    restart: always
    environment:
      - DATABASE_URL=postgresql://nx_user:${DB_PASSWORD}@db:5432/nx_calculator
      - SECRET_KEY=${SECRET_KEY}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./uploads:/app/uploads
      - ./reports:/app/reports
    depends_on:
      - db
    networks:
      - nx-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - VITE_API_URL=https://api.yourdomain.com
    container_name: nx-calculator-frontend
    restart: always
    networks:
      - nx-network

  db:
    image: postgres:15-alpine
    container_name: nx-calculator-db
    restart: always
    environment:
      - POSTGRES_USER=nx_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=nx_calculator
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - nx-network

  nginx:
    image: nginx:alpine
    container_name: nx-calculator-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - nx-network

volumes:
  postgres_data:

networks:
  nx-network:
    driver: bridge
```

**Start Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 with Docker

**1. Launch EC2 Instance**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium (2 vCPU, 4 GB RAM)
- Storage: 30 GB gp3
- Security Group: Allow ports 22, 80, 443

**2. Install Docker**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**3. Deploy Application**
```bash
# Clone repository
git clone https://github.com/networkoptix/nx_system_calc.git
cd nx_system_calc

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

**4. Configure Domain & SSL**
```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d calculator.yourdomain.com
```

#### Option 2: ECS (Elastic Container Service)

**1. Create ECR Repositories**
```bash
aws ecr create-repository --repository-name nx-calculator-backend
aws ecr create-repository --repository-name nx-calculator-frontend
```

**2. Build and Push Images**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t nx-calculator-backend .
docker tag nx-calculator-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-backend:latest

# Build and push frontend
cd ../frontend
docker build -t nx-calculator-frontend .
docker tag nx-calculator-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-frontend:latest
```

**3. Create ECS Task Definition**
- Use AWS Console or CLI
- Configure environment variables
- Set up RDS PostgreSQL database
- Configure Application Load Balancer

#### Option 3: AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker nx-calculator

# Create environment
eb create nx-calculator-prod

# Deploy
eb deploy
```

---

### Azure Deployment

#### Azure Container Instances

**1. Create Resource Group**
```bash
az group create --name nx-calculator-rg --location eastus
```

**2. Create Azure Container Registry**
```bash
az acr create --resource-group nx-calculator-rg --name nxcalculatoracr --sku Basic
```

**3. Build and Push Images**
```bash
az acr build --registry nxcalculatoracr --image nx-calculator-backend:latest ./backend
az acr build --registry nxcalculatoracr --image nx-calculator-frontend:latest ./frontend
```

**4. Deploy Container Instances**
```bash
az container create \
  --resource-group nx-calculator-rg \
  --name nx-calculator-backend \
  --image nxcalculatoracr.azurecr.io/nx-calculator-backend:latest \
  --dns-name-label nx-calculator-api \
  --ports 8000
```

---

### Google Cloud Platform

#### Cloud Run Deployment

**1. Build and Push to Container Registry**
```bash
# Configure gcloud
gcloud config set project YOUR_PROJECT_ID

# Build backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/nx-calculator-backend ./backend

# Build frontend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/nx-calculator-frontend ./frontend
```

**2. Deploy to Cloud Run**
```bash
# Deploy backend
gcloud run deploy nx-calculator-backend \
  --image gcr.io/YOUR_PROJECT_ID/nx-calculator-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy nx-calculator-frontend \
  --image gcr.io/YOUR_PROJECT_ID/nx-calculator-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Production Checklist

### Security

- [ ] Change default `SECRET_KEY` to secure random value
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL with valid certificates
- [ ] Configure firewall rules (allow only 80, 443)
- [ ] Set `API_RELOAD=false` in production
- [ ] Configure CORS with specific origins (no wildcards)
- [ ] Enable rate limiting
- [ ] Set up fail2ban for SSH protection
- [ ] Regular security updates

### Performance

- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure database connection pooling
- [ ] Enable Nginx gzip compression
- [ ] Set up CDN for static assets
- [ ] Configure caching headers
- [ ] Use production builds (not dev mode)
- [ ] Optimize Docker images (multi-stage builds)

### Monitoring

- [ ] Set up health check endpoints
- [ ] Configure log aggregation
- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring
- [ ] Set up performance monitoring
- [ ] Configure alerts for errors/downtime

### Backup

- [ ] Automated database backups
- [ ] Backup uploaded files (logos)
- [ ] Backup configuration files
- [ ] Test restore procedures
- [ ] Document backup schedule

### Documentation

- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document environment variables
- [ ] Create disaster recovery plan

---

## Monitoring & Maintenance

### Health Checks

**Endpoint:** `GET /health`

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response
{"status": "healthy", "timestamp": "2025-10-03T12:34:56Z"}
```

### Log Management

**Docker Logs:**
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

**Production Logging:**
- Use centralized logging (ELK stack, CloudWatch, Stackdriver)
- Set appropriate log levels
- Rotate logs to prevent disk fill

### Database Maintenance

**PostgreSQL:**
```bash
# Backup
docker-compose exec db pg_dump -U nx_user nx_calculator > backup.sql

# Restore
docker-compose exec -T db psql -U nx_user nx_calculator < backup.sql

# Vacuum (optimize)
docker-compose exec db psql -U nx_user -d nx_calculator -c "VACUUM ANALYZE;"
```

---

## Backup & Recovery

### Automated Backups

**Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T db pg_dump -U nx_user nx_calculator > "$BACKUP_DIR/db_$DATE.sql"

# Backup uploads
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# Backup config
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" config/ .env

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

**Cron Job:**
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Common Issues

**Issue: Container won't start**
```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

**Issue: Database connection failed**
```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.connect())"
```

**Issue: Out of disk space**
```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a

# Clean old logs
docker-compose logs --tail=0 -f
```

---

## Support

**Technical Support:**
- Email: support@networkoptix.com
- Documentation: https://docs.networkoptix.com
- GitHub Issues: https://github.com/networkoptix/nx_system_calc/issues

