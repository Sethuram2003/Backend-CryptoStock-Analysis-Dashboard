#!/usr/bin/env bash

cwd=$(pwd)
scripts_dir=$(dirname $(realpath "${0}"))
parent_dir=$(dirname "${scripts_dir}")

# echo "${parent_dir}"

cd "${parent_dir}"

# Deploy to Hetzner VPS
rsync -avz --exclude '.git' --exclude 'venv' --exclude '__pycache__' ./ root@178.156.209.160:/opt/app

cd "${cwd}"

# Launch:
#  cd /opt/app
#  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
# 
# Check if running (on VPS):
# docker compose ps
# 
# View on (local) web browser:
# http://178.156.209.160:8080
# 
# Docker stop containers (on VPS):
# docker compose down 
# # OR
# docker stop $(docker ps -q)
