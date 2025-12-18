#!/bin/bash
# aws_setup_vnc.sh - Setup AWS EC2 with VNC for manual Chrome control
# Run this after connecting to fresh Ubuntu EC2 instance

set -e

echo "🚀 Setting up AWS EC2 with VNC Desktop for Sora Scraper..."
echo "============================================================"
echo ""

# Update system
echo "📦 Step 1/7: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install desktop environment
echo "🖥️  Step 2/7: Installing XFCE desktop environment..."
sudo apt install -y xfce4 xfce4-goodies dbus-x11

# Install VNC server
echo "📺 Step 3/7: Installing VNC server..."
sudo apt install -y tightvncserver

# Install Chrome and dependencies
echo "🌐 Step 4/7: Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable chromium-chromedriver

# Install Python and tools
echo "🐍 Step 5/7: Installing Python 3.11 and tools..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git screen tmux wget curl

# Configure VNC
echo "🔧 Step 6/7: Configuring VNC..."

# Create VNC xstartup file
mkdir -p ~/.vnc
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF

chmod +x ~/.vnc/xstartup

# Clone project
echo "📥 Step 7/7: Cloning scrapper project..."
cd ~
if [ -d "scrapper_sora2" ]; then
    echo "⚠️  Directory already exists, pulling latest..."
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
pip install --upgrade pip
pip install -r requirements/requirements.txt
pip install -r requirements/requirements_selenium.txt
pip install -r requirements/requirements_vision.txt

# Create directories
mkdir -p logs videos_batch single-upload

echo ""
echo "✅ Setup complete!"
echo "============================================================"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  Start VNC server (will ask for password):"
echo "   vncserver :1 -geometry 1920x1080 -depth 24"
echo ""
echo "2️⃣  On your Mac, create SSH tunnel:"
echo "   ssh -i YOUR_KEY.pem -L 5901:localhost:5901 ubuntu@$HOSTNAME -N -f"
echo ""
echo "3️⃣  Connect with VNC viewer:"
echo "   macOS: Finder → Go → Connect to Server → vnc://localhost:5901"
echo "   Or use RealVNC/TigerVNC"
echo ""
echo "4️⃣  In VNC desktop, open terminal and:"
echo "   cd ~/scrapper_sora2"
echo "   google-chrome --remote-debugging-port=9222 --user-data-dir=\"\$HOME/.chrome-profile\" &"
echo ""
echo "5️⃣  Login to https://sora.chatgpt.com/ manually in Chrome"
echo ""
echo "6️⃣  Configure credentials:"
echo "   cd ~/scrapper_sora2"
echo "   nano .env  # Add OPENAI_API_KEY"
echo "   nano batch_urls.txt  # Add your URLs"
echo ""
echo "7️⃣  Start scraping:"
echo "   screen -S scraper"
echo "   cd ~/scrapper_sora2 && source venv/bin/activate"
echo "   python main.py --batch batch_urls.txt --max 999 --slow --use-existing"
echo ""
echo "8️⃣  Monitor with:"
echo "   ./scripts/monitor.sh"
echo ""
echo "💡 Tip: Keep Chrome open! It maintains your login session."
echo ""
