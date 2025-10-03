# Configuration Guide

**Nx System Calculator - Configuration & Customization**

---

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Configuration Files](#configuration-files)
4. [Customizing Presets](#customizing-presets)
5. [Email Configuration](#email-configuration)
6. [Database Configuration](#database-configuration)
7. [Security Settings](#security-settings)
8. [Performance Tuning](#performance-tuning)
9. [Feature Flags](#feature-flags)

---

## Overview

The Nx System Calculator is highly configurable through:
- **Environment Variables**: Runtime configuration (`.env` file)
- **JSON Configuration Files**: Presets for resolutions, codecs, RAID types, server specs
- **Database Settings**: SQLite (dev) or PostgreSQL (production)
- **Feature Flags**: Enable/disable optional features

---

## Environment Variables

### Configuration File Location

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your specific settings.

---

### Backend Configuration

#### API Settings

```bash
# API Server
API_HOST=0.0.0.0              # Listen on all interfaces
API_PORT=8000                  # API port
API_RELOAD=true                # Auto-reload on code changes (dev only)

# Security
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256                # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token expiration
```

**Generate Secure Secret Key:**
```bash
openssl rand -hex 32
```

#### Database Settings

```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./nx_calculator.db

# Production (PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/nx_calculator

# Production (PostgreSQL with SSL)
DATABASE_URL=postgresql://username:password@host:5432/dbname?sslmode=require
```

**PostgreSQL Connection String Format:**
```
postgresql://[user[:password]@][host][:port][/dbname][?param1=value1&...]
```

#### CORS Configuration

```bash
# Allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com

# For development (allow all - NOT for production)
CORS_ORIGINS=*
```

---

### Email Configuration

#### SMTP Settings

```bash
# Gmail Example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
SMTP_FROM=noreply@networkoptix.com
SMTP_BCC=sales@networkoptix.com  # Auto-BCC for all reports

# Office 365 Example
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your-email@company.com
SMTP_PASSWORD=your-password
```

#### Gmail Setup

1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password in `SMTP_PASSWORD`

#### SendGrid Example

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

---

### File Storage

```bash
# Upload directory for logos
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes

# Report storage
REPORTS_DIR=./reports
```

**Production Recommendations:**
- Use absolute paths: `/var/www/nx-calculator/uploads`
- Mount persistent volumes in Docker
- Consider S3/Azure Blob for cloud deployments

---

### Rate Limiting

```bash
# Requests per minute per IP
RATE_LIMIT_PER_MINUTE=60

# For high-traffic production
RATE_LIMIT_PER_MINUTE=300
```

---

### Frontend Configuration

```bash
# API endpoint
VITE_API_URL=http://localhost:8000

# Production
VITE_API_URL=https://api.yourdomain.com

# Application metadata
VITE_APP_NAME=Nx System Calculator
VITE_APP_VERSION=1.0.0
```

---

### Feature Flags

```bash
# Enable/disable features
ENABLE_WEBHOOKS=false
ENABLE_ANALYTICS=false
ENABLE_MULTI_SITE=true
ENABLE_OEM_BRANDING=true
```

---

### Logging

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Production
LOG_LEVEL=WARNING

# Development/Debugging
LOG_LEVEL=DEBUG
```

---

## Configuration Files

Configuration files are located in `/config/` directory.

### File Structure

```
config/
├── resolutions.json    # Camera resolution presets
├── codecs.json         # Video codec configurations
├── raid_types.json     # RAID type specifications
└── server_specs.json   # Server hardware presets
```

---

### Resolutions Configuration

**File:** `config/resolutions.json`

```json
[
  {
    "id": "2mp_1080p",
    "name": "2MP (1920x1080)",
    "width": 1920,
    "height": 1080,
    "megapixels": 2.07,
    "common_name": "Full HD / 1080p"
  }
]
```

**Fields:**
- `id`: Unique identifier (used in API)
- `name`: Display name
- `width`: Horizontal pixels
- `height`: Vertical pixels
- `megapixels`: Calculated megapixels
- `common_name`: Marketing name (optional)

**Adding Custom Resolution:**

```json
{
  "id": "custom_6mp",
  "name": "6MP (3072x2048)",
  "width": 3072,
  "height": 2048,
  "megapixels": 6.29,
  "common_name": "6 Megapixel"
}
```

---

### Codecs Configuration

**File:** `config/codecs.json`

```json
[
  {
    "id": "h264",
    "name": "H.264",
    "compression_ratio": 0.5,
    "quality_factor": 1.0,
    "cpu_load_multiplier": 1.0
  }
]
```

**Fields:**
- `id`: Unique identifier
- `name`: Display name
- `compression_ratio`: Compression efficiency (0.0-1.0)
- `quality_factor`: Quality multiplier
- `cpu_load_multiplier`: Server CPU impact

**Example: Adding AV1 Codec:**

```json
{
  "id": "av1",
  "name": "AV1",
  "compression_ratio": 0.3,
  "quality_factor": 1.0,
  "cpu_load_multiplier": 2.5
}
```

---

### RAID Types Configuration

**File:** `config/raid_types.json`

```json
[
  {
    "id": "raid5",
    "name": "RAID 5",
    "min_drives": 3,
    "overhead_percent": 33.3,
    "fault_tolerance": 1,
    "read_performance": "high",
    "write_performance": "medium"
  }
]
```

**Fields:**
- `id`: Unique identifier
- `name`: Display name
- `min_drives`: Minimum drives required
- `overhead_percent`: Storage overhead (0-100)
- `fault_tolerance`: Number of drive failures tolerated
- `read_performance`: Read speed (low/medium/high)
- `write_performance`: Write speed (low/medium/high)

---

### Server Specifications Configuration

**File:** `config/server_specs.json`

```json
{
  "specs": [
    {
      "id": "mid_range",
      "name": "Mid-Range Server",
      "max_cameras": 256,
      "cpu_cores": 8,
      "cpu_model": "Intel Xeon E-2288G",
      "ram_gb": 32,
      "storage_bays": 8,
      "nic_ports": 2,
      "nic_speed_gbps": 1,
      "estimated_cost_usd": 3500,
      "recommended_for": "100-200 cameras"
    }
  ],
  "constraints": {
    "max_cameras_per_server": 256,
    "max_servers_per_site": 10,
    "max_cameras_per_site": 2560,
    "min_ram_per_camera_mb": 40,
    "base_os_ram_mb": 4096,
    "client_ram_mb": 3072
  }
}
```

**Adding Custom Server Spec:**

```json
{
  "id": "custom_ultra",
  "name": "Ultra Performance Server",
  "max_cameras": 512,
  "cpu_cores": 32,
  "cpu_model": "AMD EPYC 7543",
  "ram_gb": 256,
  "storage_bays": 24,
  "nic_ports": 4,
  "nic_speed_gbps": 10,
  "estimated_cost_usd": 15000,
  "recommended_for": "400+ cameras, high-resolution"
}
```

---

## Customizing Presets

### Best Practices

1. **Backup Original Files**
   ```bash
   cp config/resolutions.json config/resolutions.json.backup
   ```

2. **Validate JSON Syntax**
   ```bash
   python -m json.tool config/resolutions.json
   ```

3. **Test Changes**
   - Restart backend server
   - Verify presets load correctly
   - Test calculations with new presets

4. **Version Control**
   - Commit configuration changes
   - Document reasons in commit message

---

### Reloading Configuration

**Development:**
- Backend auto-reloads with `API_RELOAD=true`
- Frontend: Refresh browser

**Production:**
```bash
# Restart backend
docker-compose restart backend

# Or with systemd
sudo systemctl restart nx-calculator-backend
```

---

## Email Configuration

### Testing Email Setup

```bash
# Test SMTP connection
python -c "
import smtplib
from email.mime.text import MIMEText

smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('your-email@gmail.com', 'your-app-password')
print('✅ SMTP connection successful')
smtp.quit()
"
```

### Email Templates

Email templates are embedded in the application. To customize:

1. Edit `backend/app/services/email/templates.py`
2. Modify HTML templates
3. Test with sample emails

---

## Database Configuration

### SQLite (Development)

**Advantages:**
- Zero configuration
- File-based, portable
- Perfect for development

**Limitations:**
- Single writer
- Not suitable for production

**Location:** `./nx_calculator.db`

### PostgreSQL (Production)

**Setup:**

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE nx_calculator;
CREATE USER nx_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nx_calculator TO nx_user;
\q

# Update .env
DATABASE_URL=postgresql://nx_user:secure_password@localhost:5432/nx_calculator
```

**Connection Pooling:**

For high-traffic deployments, configure connection pooling in `backend/app/core/database.py`.

---

## Security Settings

### HTTPS/SSL Configuration

**Nginx Reverse Proxy:**

```nginx
server {
    listen 443 ssl http2;
    server_name calculator.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Headers

Add to Nginx configuration:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

---

## Performance Tuning

### Backend Optimization

```bash
# Increase worker processes
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000

# Production with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Database Optimization

**PostgreSQL:**

```sql
-- Add indexes for common queries
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_creator_email ON projects(creator_email);
```

### Caching

Consider adding Redis for:
- Configuration caching
- Rate limiting
- Session storage

---

## Feature Flags

### Enabling Webhooks

```bash
ENABLE_WEBHOOKS=true
WEBHOOK_SECRET=your-webhook-secret
```

### Enabling Analytics

```bash
ENABLE_ANALYTICS=true
ANALYTICS_PROVIDER=google
ANALYTICS_ID=UA-XXXXXXXXX-X
```

---

## Troubleshooting

**Issue: Configuration not loading**
- Check JSON syntax with `python -m json.tool config/file.json`
- Verify file permissions
- Check backend logs

**Issue: Email not sending**
- Test SMTP connection
- Check firewall rules (port 587)
- Verify credentials

**Issue: Database connection failed**
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Test connection with `psql`

---

## Support

For configuration assistance:
- **Email**: support@networkoptix.com
- **Documentation**: https://docs.networkoptix.com
- **GitHub Issues**: https://github.com/networkoptix/nx_system_calc/issues

