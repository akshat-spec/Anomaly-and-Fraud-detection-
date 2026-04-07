#!/bin/bash
set -e

# ==============================================================================
# AWS EC2 Automate Deployment Script for Antigravity Fraud Pipeline
# Base Image: Amazon Linux 2023
# ==============================================================================

DOMAIN="fraud-demo.antigravity.dev"
REPO_URL="https://github.com/username/fraud-detection.git"
APP_DIR="/opt/fraud-detection"

# 1. System Update & Dependencies natively mapping components gracefully
echo "Updating systems matching requirements explicitly..."
dnf update -y
dnf install -y git jq curl

# 2. Install Docker & Docker Compose natively dynamically
echo "Installing Docker Engine natively securely..."
dnf install -y docker
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Code Checkout securely
echo "Cloning Repository safely smoothly..."
if [ ! -d "$APP_DIR" ]; then
    git clone $REPO_URL $APP_DIR
else
    cd $APP_DIR && git pull origin main
fi
cd $APP_DIR

# 4. Environment Variables organically mapping bounds exclusively
echo "Initializing environments securely..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env seamlessly mapping default limits dynamically instantiated"
fi

# 5. Execute Core Containers explicitly deploying seamlessly 
echo "Launching Core Analytics Matrix safely gracefully..."
docker-compose up -d --build

# 6. Certbot / SSL Generation
echo "Requesting SSL bindings intrinsically mapping configurations securely..."
dnf install -y certbot
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

# 7. Systemd Persistence explicit configuration mapped gracefully bounds completely
cat <<EOF > /etc/systemd/system/fraud-pipeline.service
[Unit]
Description=Antigravity Fraud Intelligence Pipeline
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable fraud-pipeline.service

echo "Deployment mapping conclusively completed dynamically!"
