#!/usr/bin/env bash

cwd=$(pwd)

cd ../

# Deploy to Hetzner VPS
rsync -avz --exclude '.git' --exclude 'venv' --exclude '__pycache__' ./ root@178.156.209.160:/opt/app

cd "$

# Launch:
#  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
# 
# Check if running (on VPS):
# docker compose ps
# 
# View on (local) web browser:
# http://178.156.209.160:8080