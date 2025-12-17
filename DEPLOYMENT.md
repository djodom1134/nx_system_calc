# Deployment Guide - Nx System Calculator

## 🚀 Quick Deployment Checklist

### ✅ **Pre-Deployment Requirements**

1. **Python 3.9+** installed
2. **Node.js 18+** and npm installed
3. **Config files** deployed to server
4. **Environment variables** configured
5. **Dependencies** installed

---

## 📁 **Required Files & Directories**

### **Backend Files**
```
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
└── requirements.txt

config/                    ⚠️ CRITICAL - Must be deployed!
├── resolutions.json
├── codecs.json
├── raid_types.json
└── server_specs.json
```

### **Frontend Files**
```
frontend/
├── src/
├── public/
│   ├── logo.webp        ⚠️ Required for branding
│   └── tile.png         ⚠️ Required for header background
├── package.json
└── vite.config.ts
```

---

## 🔧 **Environment Variables**

Create a `.env` file in the `backend/` directory:

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false  # Set to false in production

# Security
SECRET_KEY=your-secure-random-key-here-change-this

# Database
DATABASE_URL=sqlite:///./nx_calculator.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/nx_calculator

# CORS - Add your production domain
CORS_ORIGINS=["https://yourdomain.com","http://localhost:5173"]

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@networkoptix.com
SMTP_BCC=sales@networkoptix.com

# Webhooks (Optional)
ENABLE_WEBHOOKS=false

# Configuration Directory (IMPORTANT for deployment)
CONFIG_DIR=/path/to/config
# If not set, will use relative path: ../config from backend/app/core/
```

---

## 🐛 **Common Deployment Issues**

### **Issue 1: 500 Error - Config Files Not Found**

**Symptoms:**
```
GET /api/v1/config/raid-types - 500 (Internal Server Error)
GET /api/v1/config/codecs - 500 (Internal Server Error)
GET /api/v1/config/resolutions - 500 (Internal Server Error)
```

**Cause:** Config directory not found or not in expected location

**Solutions:**

1. **Set CONFIG_DIR environment variable:**
   ```bash
   export CONFIG_DIR=/absolute/path/to/config
   ```

2. **Verify config files exist:**
   ```bash
   ls -la /path/to/config/
   # Should show: resolutions.json, codecs.json, raid_types.json, server_specs.json
   ```

3. **Check file permissions:**
   ```bash
   chmod 644 /path/to/config/*.json
   ```

4. **Verify JSON syntax:**
   ```bash
   python3 -m json.tool config/raid_types.json
   ```

### **Issue 2: CORS Errors**

**Symptoms:**
```
Access to fetch at 'http://api.example.com' from origin 'http://frontend.example.com' 
has been blocked by CORS policy
```

**Solution:**
Add your frontend domain to `CORS_ORIGINS` in `.env`:
```bash
CORS_ORIGINS=["https://frontend.example.com","http://localhost:5173"]
```

### **Issue 3: Database Connection Errors**

**Solution:**
Ensure `DATABASE_URL` is correctly set and database is accessible:
```bash
# For SQLite (default)
DATABASE_URL=sqlite:///./nx_calculator.db

# For PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/nx_calculator
```

---

## 📦 **Deployment Steps**

### **Option 1: Docker Deployment (Recommended)**

Coming soon - Docker configuration will be added.

### **Option 2: Manual Deployment**

#### **Backend Deployment**

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export CONFIG_DIR=/absolute/path/to/config
export DATABASE_URL=sqlite:///./nx_calculator.db
# ... other variables

# 5. Initialize database
python3 -c "from app.models.base import init_db; init_db()"

# 6. Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### **Frontend Deployment**

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Build for production
npm run build

# 4. Serve with nginx or other web server
# The build output will be in frontend/dist/
```

---

## 🔍 **Verification Steps**

After deployment, verify everything works:

```bash
# 1. Check backend health
curl http://localhost:8000/docs

# 2. Test config endpoints
curl http://localhost:8000/api/v1/config/raid-types
curl http://localhost:8000/api/v1/config/codecs
curl http://localhost:8000/api/v1/config/resolutions

# 3. Test calculation endpoint
curl -X POST http://localhost:8000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d @test_calculation.json
```

---

## 📝 **Production Recommendations**

1. **Use PostgreSQL** instead of SQLite for production
2. **Set API_RELOAD=false** in production
3. **Use a reverse proxy** (nginx, Apache) in front of the API
4. **Enable HTTPS** with SSL certificates
5. **Set up monitoring** and logging
6. **Configure backups** for the database
7. **Use environment-specific .env files**
8. **Never commit .env files** to version control

---

## 🆘 **Getting Help**

If you encounter issues:

1. Check backend logs for detailed error messages
2. Verify all config files are present and valid JSON
3. Ensure CONFIG_DIR environment variable is set correctly
4. Check file permissions
5. Verify Python and Node.js versions

For more help, contact the development team.

