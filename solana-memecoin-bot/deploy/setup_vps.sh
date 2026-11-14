#!/bin/bash
set -e
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip git
cd /opt/solana-bot 2>/dev/null || (sudo mkdir -p /opt/solana-bot && sudo chown $USER:$USER /opt/solana-bot && cd /opt/solana-bot)
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
echo "Edit /opt/solana-bot/.env then: sudo systemctl enable --now solana-bot"
