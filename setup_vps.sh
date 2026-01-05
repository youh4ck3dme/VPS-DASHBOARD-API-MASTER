#!/bin/bash
# VPS Initial Setup Script for CarScraper Pro
# Run this ONCE on the VPS to set up the environment
# Server: tapfast (194.182.87.6)
# Domain: app.h4ck3d.cloud

set -e

echo "🚀 CarScraper Pro - VPS Initial Setup"
echo "======================================"

# 1. Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# 2. Install required packages
echo "📦 Installing Python, Nginx, Certbot..."
apt install -y python3 python3-pip python3.10-venv nginx certbot python3-certbot-nginx

# 3. Create application directory
echo "📁 Creating application directory..."
mkdir -p /var/www/carscraper
cd /var/www/carscraper

# 4. Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 5. Install Python dependencies (if requirements.txt exists)
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# 6. Create .env file
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cat > .env << 'EOF'
SECRET_KEY=CHANGE_THIS_TO_A_SECURE_RANDOM_STRING
DATABASE_URL=sqlite:///carscraper.db
SCRAPER_ENABLED=True
FLASK_ENV=production
EOF
    echo "⚠️ IMPORTANT: Update .env with secure secrets!"
fi

# 7. Create Nginx configuration
echo "🌐 Configuring Nginx for app.h4ck3d.cloud..."
cat > /etc/nginx/sites-available/carscraper << 'EOF'
server {
    listen 80;
    server_name app.h4ck3d.cloud;

    # Frontend (static files)
    location / {
        root /var/www/carscraper/static/carscraper;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend Admin routes
    location ~ ^/(login|dashboard|settings|projects|payments|automation|ai|landing|carscraper) {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/carscraper /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload nginx
nginx -t && systemctl reload nginx

# 8. Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/carscraper.service << 'EOF'
[Unit]
Description=CarScraper Pro Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/carscraper
Environment="PATH=/var/www/carscraper/venv/bin"
ExecStart=/var/www/carscraper/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable carscraper

# 9. SSL with Let's Encrypt
echo "🔒 Setting up SSL certificate..."
echo ""
echo "⚠️ BEFORE running certbot, make sure:"
echo "   1. DNS A record for app.h4ck3d.cloud points to 194.182.87.6"
echo "   2. Port 80 is open in firewall"
echo ""
read -p "Is DNS configured? (y/n): " dns_ready

if [ "$dns_ready" = "y" ]; then
    certbot --nginx -d app.h4ck3d.cloud --non-interactive --agree-tos -m admin@h4ck3d.cloud
    echo "✅ SSL certificate installed!"
else
    echo "⚠️ Skipping SSL. Run manually later:"
    echo "   certbot --nginx -d app.h4ck3d.cloud"
fi

# 10. Start service
echo "🚀 Starting CarScraper service..."
systemctl start carscraper
systemctl status carscraper

echo ""
echo "=============================================="
echo "✅ VPS Setup Complete!"
echo "=============================================="
echo ""
echo "📍 URLs:"
echo "   Frontend: https://app.h4ck3d.cloud"
echo "   Backend Admin: https://app.h4ck3d.cloud/dashboard"
echo "   API: https://app.h4ck3d.cloud/api/"
echo ""
echo "⚙️ Commands:"
echo "   Logs: journalctl -u carscraper -f"
echo "   Restart: systemctl restart carscraper"
echo "   Status: systemctl status carscraper"
echo ""
