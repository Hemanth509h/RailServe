# RailServe Deployment Guide

## Overview
This guide covers deploying RailServe in production environments outside of Replit.

## Prerequisites

### System Requirements
- Python 3.11 or higher
- PostgreSQL 12 or higher
- Nginx (recommended for reverse proxy)
- Systemd (for service management)

### Dependencies
```bash
pip install -r requirements.txt
```

## Environment Configuration

### Required Environment Variables
Create a `.env` file in your project root:

```bash
# Application Configuration
SESSION_SECRET=your_secure_random_key_here
FLASK_ENV=production

# Database Configuration  
DATABASE_URL=postgresql://username:password@localhost:5432/railserve

# Server Configuration
GUNICORN_WORKERS=4
```

### Generate Secure Session Secret
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Database Setup

### 1. Create PostgreSQL Database
```sql
CREATE DATABASE railserve;
CREATE USER railserve_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE railserve TO railserve_user;
```

### 2. Populate Database
Use the standalone population script:

```bash
# Set environment variables
export DATABASE_URL="postgresql://railserve_user:secure_password@localhost:5432/railserve"
export SESSION_SECRET="your_generated_secret_key"

# Populate all data
python scripts/populate_db.py --all

# Or populate selectively
python scripts/populate_db.py --stations --trains 150 --create-admin
```

## Production Server Configuration

### Gunicorn Configuration
The project includes `gunicorn.conf.py` with production-ready settings:

- **Workers**: CPU cores × 2 + 1
- **Timeouts**: 30 seconds request timeout
- **Security**: Request size limits
- **Logging**: Structured logging to stdout

### Start Production Server
```bash
# Using the configuration file
gunicorn --config gunicorn.conf.py main:app

# Or directly with environment variables
GUNICORN_WORKERS=4 gunicorn --config gunicorn.conf.py main:app
```

## Nginx Reverse Proxy Configuration

### Site Configuration
Create `/etc/nginx/sites-available/railserve`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    # Security Headers
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Static files (optional optimization)
    location /static/ {
        alias /path/to/railserve/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/railserve /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Systemd Service Configuration

### Create Service File
Create `/etc/systemd/system/railserve.service`:

```ini
[Unit]
Description=RailServe Railway Reservation System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=railserve
Group=railserve
WorkingDirectory=/opt/railserve
ExecStart=/opt/railserve/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/railserve/logs
NoNewPrivileges=true

# Environment
EnvironmentFile=/opt/railserve/.env

# Restart configuration
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Service Management
```bash
# Enable and start service
sudo systemctl enable railserve.service
sudo systemctl start railserve.service

# Check status
sudo systemctl status railserve.service

# View logs
sudo journalctl -u railserve.service -f
```

## Security Hardening

### Application Security
- ✅ CSRF protection enabled
- ✅ Secure session cookies (HTTPS only)
- ✅ Password hashing with Werkzeug
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (Jinja2 auto-escaping)

### Server Security
```bash
# Firewall (allow only HTTP/HTTPS and SSH)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban

# Regular updates
sudo apt update && sudo apt upgrade -y
```

### Database Security
```sql
-- Restrict database user permissions
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM railserve_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO railserve_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO railserve_user;
```

## Monitoring & Logging

### Application Logs
Logs are output to stdout/stderr and captured by systemd:

```bash
# View application logs
sudo journalctl -u railserve.service -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Checks
Add health check endpoint to your application:

```python
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check database connectivity
        db.session.execute(text("SELECT 1"))
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503
```

## Backup & Recovery

### Database Backup
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/opt/backups/railserve"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump railserve > "$BACKUP_DIR/railserve_$DATE.sql"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "railserve_*.sql" -mtime +7 -delete
```

### Recovery
```bash
# Restore from backup
psql railserve < /opt/backups/railserve/railserve_20250916_120000.sql
```

## Performance Tuning

### PostgreSQL Configuration
```sql
-- Optimize for web application workload
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

### Gunicorn Tuning
```python
# gunicorn.conf.py adjustments for high traffic
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

## SSL/TLS Configuration

### Let's Encrypt (Certbot)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status railserve.service

# Check logs
sudo journalctl -u railserve.service --lines=50

# Verify environment variables
sudo -u railserve env | grep -E "(DATABASE_URL|SESSION_SECRET)"
```

#### Database Connection Issues
```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT version();"

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Performance Issues
```bash
# Monitor system resources
htop

# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Monitor application logs for slow queries
sudo journalctl -u railserve.service | grep -i slow
```

## Scaling Considerations

### Horizontal Scaling
- Load balancer (HAProxy/Nginx)
- Multiple application servers
- Database read replicas
- Redis for session storage

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Enable connection pooling
- Use CDN for static assets

## Maintenance

### Regular Tasks
1. **Daily**: Check service status and logs
2. **Weekly**: Database vacuum and analyze
3. **Monthly**: Security updates
4. **Quarterly**: Performance review and optimization

### Update Procedure
```bash
# 1. Backup database
pg_dump railserve > backup_before_update.sql

# 2. Stop service
sudo systemctl stop railserve.service

# 3. Update code
git pull origin main
pip install -r requirements.txt

# 4. Run database migrations (if any)
python scripts/populate_db.py --help

# 5. Start service
sudo systemctl start railserve.service

# 6. Verify deployment
curl -f http://localhost:5000/health
```

This deployment guide ensures a production-ready, secure, and scalable RailServe installation.