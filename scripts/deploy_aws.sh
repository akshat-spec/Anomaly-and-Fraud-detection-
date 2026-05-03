#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/akshat-spec/Anomaly-and-Fraud-detection-.git"
APP_DIR="/opt/fraud-detection"
DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"

echo "Starting deployment for Amazon Linux 2023..."

# 1. System Updates and Dependencies
sudo dnf update -y
sudo dnf install -y git jq wget curl certbot

# 2. Install Docker
if ! command -v docker &> /dev/null; then
    sudo dnf install -y docker
    sudo systemctl enable --now docker
    sudo usermod -aG docker ec2-user
fi

# 3. Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 4. Clone Repository
if [ ! -d "$APP_DIR" ]; then
    sudo git clone "$REPO_URL" "$APP_DIR"
    sudo chown -R ec2-user:ec2-user "$APP_DIR"
else
    cd "$APP_DIR"
    git pull origin main
fi

cd "$APP_DIR"

# 5. Environment Variables
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file. Please update the variables if necessary."
fi

# 6. SSL Configuration (Let's Encrypt)
# Assuming Nginx proxy container or standalone Certbot if port 80 is free
if [ "$DOMAIN" != "yourdomain.com" ]; then
    sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL"
    # Copy certs to a location accessible by docker
    sudo mkdir -p "$APP_DIR/certs"
    sudo cp /etc/letsencrypt/live/"$DOMAIN"/fullchain.pem "$APP_DIR/certs/"
    sudo cp /etc/letsencrypt/live/"$DOMAIN"/privkey.pem "$APP_DIR/certs/"
    sudo chown -R ec2-user:ec2-user "$APP_DIR/certs"
    echo "SSL Certificates generated."
fi

# 7. Start Application
docker-compose build
docker-compose up -d

# 8. Setup Systemd Service for Auto-Restart
SERVICE_FILE="/etc/systemd/system/fraud-detection.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Fraud Detection System
Requires=docker.service
After=docker.service

[Service]
Restart=always
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable fraud-detection.service

echo "Deployment complete! Application is running."
