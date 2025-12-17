# Deployment Guide - Nx System Calculator

## 🚀 Quick Deployment Checklist

### ✅ **Pre-Deployment Requirements**

1. **Docker & Docker Compose** installed (for Docker deployment)
2. **Python 3.9+** installed (for manual deployment)
3. **Node.js 18+** and npm installed (for manual deployment)
4. **Config files** deployed to server
5. **Environment variables** configured

---

## 🐳 **Docker Deployment (Recommended)**

### **Quick Start**

```bash
# 1. Clone the repository
git clone https://github.com/your-org/nx_system_calc.git
cd nx_system_calc

# 2. Configure environment
cp .env.example .env
# Edit .env with your production settings

# 3. Deploy using the deployment script
chmod +x scripts/deploy-aws.sh
./scripts/deploy-aws.sh deploy
```

### **Manual Docker Deployment**

```bash
# Development mode
docker-compose up -d

# Production mode (recommended for AWS)
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### **Docker Files Overview**

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Development configuration |
| `docker-compose.prod.yml` | Production configuration (AWS/cloud) |
| `backend/Dockerfile` | Backend container image |
| `frontend/Dockerfile` | Frontend container with nginx |
| `frontend/nginx.conf` | Nginx configuration for SPA + API proxy |

### **Production Environment Variables**

Create a `.env` file in the project root:

```bash
# REQUIRED - Change these!
SECRET_KEY=your-secure-random-key-minimum-32-chars
DB_PASSWORD=your-secure-database-password

# CORS - Add your production domain
CORS_ORIGINS=["https://yourdomain.com"]

# Optional - Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Optional - Features
ENABLE_WEBHOOKS=false
LOG_LEVEL=INFO
```

---

## ☁️ **AWS Deployment Options**

### **Option 1: AWS EC2 with Docker Compose**

1. **Launch EC2 Instance**
   - Amazon Linux 2 or Ubuntu 22.04
   - t3.medium or larger recommended
   - Security Group: Allow ports 22, 80, 443

2. **Install Docker**
   ```bash
   # Amazon Linux 2
   sudo yum update -y
   sudo amazon-linux-extras install docker -y
   sudo systemctl start docker
   sudo usermod -aG docker ec2-user

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   git clone https://github.com/your-org/nx_system_calc.git
   cd nx_system_calc
   cp .env.example .env
   # Edit .env with production values
   ./scripts/deploy-aws.sh deploy
   ```

### **Option 2: AWS ECS with Fargate**

1. **Push images to ECR**
   ```bash
   # Authenticate with ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

   # Build and push backend
   docker build -t nx-calculator-backend ./backend
   docker tag nx-calculator-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-backend:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-backend:latest

   # Build and push frontend
   docker build -t nx-calculator-frontend ./frontend
   docker tag nx-calculator-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-frontend:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nx-calculator-frontend:latest
   ```

2. **Create ECS Task Definition** with environment variables
3. **Create ECS Service** with Application Load Balancer
4. **Configure RDS PostgreSQL** for database

### **Option 3: AWS Elastic Beanstalk**

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

## 📁 **Required Files & Directories**

```
nx_system_calc/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   │   ├── logo.webp      ⚠️ Required for branding
│   │   └── tile.png       ⚠️ Required for header
│   ├── Dockerfile
│   └── nginx.conf
├── config/                 ⚠️ CRITICAL - Must be deployed!
│   ├── resolutions.json
│   ├── codecs.json
│   ├── raid_types.json
│   └── server_specs.json
├── docker-compose.yml
├── docker-compose.prod.yml
└── .env
```

---

## 🐛 **Common Deployment Issues**

### **Issue 1: 500 Error - Config Files Not Found**

**Symptoms:**
```
GET /api/v1/config/raid-types - 500 (Internal Server Error)
```

**Solutions:**

1. **For Docker:** Ensure config volume is mounted correctly
   ```yaml
   volumes:
     - ./config:/app/config:ro
   ```

2. **Set CONFIG_DIR environment variable:**
   ```bash
   CONFIG_DIR=/app/config  # For Docker
   CONFIG_DIR=/path/to/config  # For manual deployment
   ```

3. **Verify JSON syntax:**
   ```bash
   python3 -m json.tool config/raid_types.json
   ```

### **Issue 2: CORS Errors**

**Solution:** Add your domain to CORS_ORIGINS:
```bash
CORS_ORIGINS=["https://yourdomain.com","http://localhost"]
```

### **Issue 3: Database Connection Errors**

**Solution:** For Docker, use the service name:
```bash
DATABASE_URL=postgresql://nx_user:password@db:5432/nx_calculator
```

### **Issue 4: Frontend Can't Reach Backend**

**Solution:** The nginx.conf proxies `/api/` to the backend. Ensure:
- Backend container is named `backend` (or update nginx.conf)
- Both containers are on the same Docker network

---

## 🔍 **Verification Steps**

```bash
# Using the deployment script
./scripts/deploy-aws.sh verify

# Manual verification
curl http://localhost/health           # Frontend
curl http://localhost:8000/health      # Backend
curl http://localhost:8000/api/v1/config/raid-types  # Config
```

---

## 📝 **Production Recommendations**

1. ✅ **Use PostgreSQL** - Configured by default in docker-compose.prod.yml
2. ✅ **Use HTTPS** - Add SSL certificates to nginx or use AWS ALB
3. ✅ **Set strong secrets** - SECRET_KEY and DB_PASSWORD
4. ✅ **Enable health checks** - Already configured in Docker
5. ✅ **Configure logging** - Set LOG_LEVEL=INFO or DEBUG
6. ✅ **Set up backups** - Use AWS RDS automated backups
7. ✅ **Monitor resources** - Use AWS CloudWatch

---

## 🆘 **Getting Help**

1. Run deployment verification: `./scripts/deploy-aws.sh verify`
2. Check container logs: `docker-compose logs backend`
3. Run config test: `cd backend && python3 test_deployment.py`
4. Verify JSON files: `python3 -m json.tool config/*.json`

