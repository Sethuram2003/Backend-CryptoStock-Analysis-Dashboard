#!/bin/bash

# Stop on error
set -e

echo "🚀 Starting Hetzner VPS Setup..."

# 1. Update System
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker & Docker Compose
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    # Add current user to docker group to avoid sudo
    sudo usermod -aG docker $USER
    echo "✅ Docker installed."
else
    echo "✅ Docker already installed."
fi

# 3. Setup Project Directory
APP_DIR="/opt/crypto-stock-analysis"
echo "mb Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# 4. Instructions for next steps
echo ""
echo "🎉 Server setup complete!"
echo ""
echo "Next steps to deploy your app:"
echo "1. Copy your project files to this server:"
echo "   rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' ./ $USER@<YOUR_SERVER_IP>:$APP_DIR"
echo ""
echo "2. SSH into the server and go to the directory:"
echo "   ssh $USER@<YOUR_SERVER_IP>"
echo "   cd $APP_DIR"
echo ""
echo "3. Create your .env file (CRITICAL):"
echo "   nano .env  # Paste your environment variables here"
echo ""
echo "4. Start the application:"
echo "   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
echo ""
