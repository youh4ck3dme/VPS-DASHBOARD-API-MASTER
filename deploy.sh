#!/bin/bash
# VPS Deployment Script for CarScraper Pro
# Server: tapfast (194.182.87.6)
# Ubuntu 22.04

set -e

VPS_USER="root"
VPS_HOST="194.182.87.6"
VPS_PATH="/var/www/carscraper"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"

echo "🚀 CarScraper Pro - VPS Deployment"
echo "=================================="
echo "Target: $VPS_USER@$VPS_HOST:$VPS_PATH"
echo ""

# 1. Build Frontend
echo "📦 Building frontend..."
cd frontend
pnpm install
pnpm run build
cd ..

# 2. Sync files to VPS
echo "📤 Syncing files to VPS..."
rsync -avz --delete \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude 'venv' \
    --exclude 'frontend/node_modules' \
    -e "ssh -i $SSH_KEY" \
    ./ "$VPS_USER@$VPS_HOST:$VPS_PATH/"

# 3. Remote setup & restart
echo "🔧 Setting up on VPS..."
ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" << 'ENDSSH'
cd /var/www/carscraper

# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install deps
source venv/bin/activate
pip install -r requirements.txt --quiet

# Create .env if not exists
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///carscraper.db
SCRAPER_ENABLED=True
FLASK_ENV=production
EOF
    echo "⚠️ Created default .env - please update secrets!"
fi

# Database migration
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Restart service
if systemctl is-active --quiet carscraper; then
    sudo systemctl restart carscraper
    echo "✅ Service restarted"
else
    echo "⚠️ Service 'carscraper' not found. Create systemd service:"
    echo "   sudo nano /etc/systemd/system/carscraper.service"
fi
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo "🌐 Backend should be running at http://$VPS_HOST:5000"
