# FindThem Deployment Guide

Complete guide for deploying FindThem to production environments.

## Pre-Deployment Checklist

- [ ] All environment variables set securely
- [ ] Admin password changed from default
- [ ] Database credentials updated
- [ ] HTTPS/SSL certificates obtained
- [ ] Firewall rules configured
- [ ] Database backups enabled
- [ ] Monitoring and logging set up
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation tested

## Local to Production Steps

### 1. Database Setup

#### Option A: Managed MySQL (Recommended)

Use services like:
- Amazon RDS
- Google Cloud SQL
- DigitalOcean Managed Databases
- Azure Database for MySQL

Steps:
1. Create managed MySQL instance
2. Run schema.sql on the remote database
3. Update connection string in `.env`

#### Option B: Self-Hosted MySQL

```bash
# SSH into server
ssh user@your-server.com

# Install MySQL
sudo apt-get install mysql-server

# Secure MySQL
sudo mysql_secure_installation

# Create database
mysql -u root -p < schema.sql
```

### 2. Backend Deployment

#### Option A: Docker (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t findthem-api .
docker run -p 8000:8000 --env-file .env findthem-api
```

#### Option B: Traditional Server (Linux/Ubuntu)

```bash
# SSH into server
ssh user@your-server.com

# Update system
sudo apt-get update
sudo apt-get upgrade

# Install Python and dependencies
sudo apt-get install python3 python3-pip python3-venv

# Clone repository
git clone https://github.com/yourusername/findthem.git
cd findthem/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your production environment variables

# Install systemd service
sudo nano /etc/systemd/system/findthem.service
```

`/etc/systemd/system/findthem.service`:

```ini
[Unit]
Description=FindThem API Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/user/findthem/backend
Environment="PATH=/home/user/findthem/backend/venv/bin"
EnvironmentFile=/home/user/findthem/backend/.env
ExecStart=/home/user/findthem/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable findthem
sudo systemctl start findthem
sudo systemctl status findthem
```

### 3. Frontend Deployment

#### Option A: Static File Server (Nginx)

```bash
# Install Nginx
sudo apt-get install nginx

# Copy frontend files
sudo cp -r frontend/* /var/www/html/findthem/

# Create Nginx config
sudo nano /etc/nginx/sites-available/findthem
```

`/etc/nginx/sites-available/findthem`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    root /var/www/html/findthem;
    index index.html;

    # Frontend routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Uploads
    location /uploads {
        proxy_pass http://localhost:8000/uploads;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/findthem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Option B: Cloud Storage (AWS S3, Google Cloud Storage)

1. Upload frontend files to S3
2. Configure CloudFront for CDN
3. Update API_BASE_URL in script.js

### 4. SSL/HTTPS Setup

Using Let's Encrypt (Free):

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot renew --dry-run  # Test auto-renewal
```

### 5. Environment Configuration

Production `.env` example:

```env
# Database (Use managed service!)
DB_HOST=db.yourdomain.com
DB_USER=produser
DB_PASSWORD=very_secure_password_here
DB_NAME=findthem_prod
DB_PORT=3306

# API
API_HOST=0.0.0.0
API_PORT=8000
RELOAD=False

# Face Recognition
SIMILARITY_THRESHOLD=0.6

# Security
SECRET_KEY=generate_with_secrets.token_urlsafe(32)
ADMIN_PASSWORD=change_this_to_secure_password
```

### 6. Monitoring and Logging

#### Application Logging

Install and configure Sentry:

```bash
pip install sentry-sdk
```

In `main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

#### Database Monitoring

Enable MySQL query logs:

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

#### Server Monitoring

Use Prometheus + Grafana:

```bash
# Install Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Install Grafana
docker run -d -p 3000:3000 grafana/grafana
```

### 7. Performance Optimization

#### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_status ON cases(status);
CREATE INDEX idx_created_at ON cases(created_at);
CREATE INDEX idx_is_resolved ON cases(is_resolved);

-- Run analysis
ANALYZE TABLE cases;
```

#### Caching

Add Redis for caching:

```python
# In config.py
REDIS_URL = "redis://localhost:6379"
```

#### CDN Integration

Use Cloudflare or CloudFront for static assets.

### 8. Backup Strategy

#### Daily Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DB_NAME="findthem_db"
DATE=$(date +%Y%m%d_%H%M%S)

mysqldump -u root -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/findthem_$DATE.sql
gzip $BACKUP_DIR/findthem_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/findthem_$DATE.sql.gz s3://your-backup-bucket/
```

Cron job:

```bash
# Run daily at 2 AM
0 2 * * * /home/user/backup.sh
```

### 9. Security Hardening

#### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

#### Rate Limiting

Add to `main.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/upload-case")
@limiter.limit("5/minute")
async def upload_case(...):
    ...
```

#### Input Validation

Already implemented in backend, ensure CORS is restricted:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=["*"],
)
```

#### Database Security

```sql
-- Create limited user
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON findthem_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### 10. Testing Production Setup

```bash
# Test API endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/api/stats

# Check SSL
openssl s_client -connect yourdomain.com:443

# Monitor logs
tail -f /var/log/syslog
```

## Scaling Strategies

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or AWS ALB
2. **Multiple API Instances**: Run API on multiple servers
3. **Database Replication**: Master-slave setup

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Enable caching

## Maintenance

### Regular Updates

```bash
# Update packages
pip install --upgrade -r requirements.txt

# Update system
sudo apt-get update && sudo apt-get upgrade

# Restart services
sudo systemctl restart findthem
sudo systemctl restart nginx
```

### Database Maintenance

```sql
-- Optimize tables
OPTIMIZE TABLE cases;
OPTIMIZE TABLE search_history;

-- Check table health
CHECK TABLE cases;
REPAIR TABLE cases;
```

## Monitoring Checklist

- [ ] CPU usage < 80%
- [ ] Memory usage < 80%
- [ ] Disk space > 20% free
- [ ] API response time < 1 second
- [ ] Database connections < max limit
- [ ] Backup completion successful
- [ ] SSL certificate valid
- [ ] No error spikes in logs

## Troubleshooting Production Issues

### High CPU Usage
- Check slow queries in MySQL
- Optimize database indexes
- Scale horizontally

### Database Connection Errors
- Check connection pool size
- Verify credentials
- Check network connectivity

### Slow API Responses
- Check database query performance
- Enable caching
- Add load balancing

### SSL Certificate Issues
- Check expiration: `openssl x509 -in cert.pem -noout -dates`
- Renew if needed: `certbot renew`

## Support Resources

- Production Deployment: See this guide
- API Documentation: API_DOCUMENTATION.md
- Troubleshooting: README.md
- Architecture: System design documentation

---

**Important**: Always test deployment in staging environment first!
