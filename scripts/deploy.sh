#!/bin/bash
# deploy.sh - Complete deployment on fresh Ubuntu VM
# Usage: curl -sSL https://raw.githubusercontent.com/ethan0905/scrapper_sora2/main/scripts/deploy.sh | bash

set -e

echo "🚀 Deploying Sora Scraper on Cloud VM..."
echo "========================================"
echo ""

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3-pip

# Install Chrome
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt update
apt install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
apt install -y chromium-chromedriver

# Install utilities
echo "🛠️  Installing utilities..."
apt install -y screen tmux git curl wget unzip rsync

# Clone project
echo "📥 Cloning project from GitHub..."
cd /root
if [ -d "scrapper_sora2" ]; then
    echo "⚠️  Directory already exists, pulling latest changes..."
    cd scrapper_sora2
    git pull
else
    git clone https://github.com/ethan0905/scrapper_sora2.git
    cd scrapper_sora2
fi

# Setup Python environment
echo "🐍 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements/requirements.txt
pip install -r requirements/requirements_selenium.txt
pip install -r requirements/requirements_vision.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p single-upload/uploaded
mkdir -p videos_batch

echo ""
echo "✅ Deployment complete!"
echo "========================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "1️⃣  Add your credentials:"
echo "   nano youtube_credentials.json"
echo ""
echo "2️⃣  Add your OpenAI API key:"
echo "   nano .env"
echo "   # Add: OPENAI_API_KEY=your-key-here"
echo ""
echo "3️⃣  Create your batch URLs file:"
echo "   nano batch_urls.txt"
echo "   # Add one URL per line"
echo ""
echo "4️⃣  Start scraping in a screen session:"
echo "   screen -S scraper"
echo "   source venv/bin/activate"
echo "   python main.py --batch batch_urls.txt --max 999 --slow --output videos_batch"
echo ""
echo "5️⃣  Detach from screen: Ctrl+A then D"
echo "   Reattach later: screen -r scraper"
echo ""
echo "6️⃣  Monitor progress:"
echo "   tail -f logs/scraper.log"
echo "   ls -lh videos_batch/ | wc -l"
echo ""
echo "💡 Tip: The VM will keep running even if you disconnect!"
echo ""
