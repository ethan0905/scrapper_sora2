# 🖥️ AWS EC2 Deployment with Manual Login & Monitoring

## Overview

Deploy to AWS EC2 with:
- **Manual browser login** to avoid bot detection
- **VNC/Remote Desktop** to monitor Chrome in real-time
- **Session persistence** so scraper keeps running after login
- **Live monitoring** of scraping progress

## Why This Approach?

✅ **Manual login** - You handle ChatGPT authentication yourself  
✅ **Visual monitoring** - See Chrome window, verify it's working  
✅ **Debugging** - Watch for errors in real-time  
✅ **Session cookies** - Stays logged in between runs  
✅ **Safe** - No bot detection from automated logins  

## Setup Guide

### Step 1: Create AWS EC2 Instance

1. Go to [AWS EC2 Console](https://console.aws.amazon.com/ec2/)
2. Click "Launch Instance"
3. Configure:
   - **Name**: `sora-scraper`
   - **OS**: Ubuntu 22.04 LTS
   - **Instance type**: `t3.medium` (2 vCPU, 4GB RAM) - $30/month
   - **Region**: `us-east-1` (Virginia) or `us-west-2` (Oregon) - US IP
   - **Storage**: 100GB gp3 (adjust based on needs)
   - **Security Group**: Create new
     - SSH (22) - Your IP only
     - VNC (5901) - Your IP only
     - HTTP (8080) - Optional for web monitoring
4. Download key pair (e.g., `sora-scraper.pem`)
5. Launch instance

### Step 2: Connect to EC2

```bash
# Make key private
chmod 400 sora-scraper.pem

# SSH into instance
ssh -i sora-scraper.pem ubuntu@YOUR_EC2_IP
```

### Step 3: Install Desktop Environment & VNC

This lets you see Chrome visually and login manually:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install lightweight desktop (XFCE)
sudo apt install -y xfce4 xfce4-goodies

# Install VNC server
sudo apt install -y tightvncserver

# Install Chrome and dependencies
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
sudo apt install -y chromium-chromedriver

# Install Python and utilities
sudo apt install -y python3.11 python3.11-venv python3-pip git screen tmux
```

### Step 4: Setup VNC Server

```bash
# Start VNC server (first time - will ask for password)
vncserver :1 -geometry 1920x1080 -depth 24

# Enter a password (you'll use this to connect)
# Choose a view-only password (optional)

# Kill VNC to configure
vncserver -kill :1

# Configure VNC to use XFCE
nano ~/.vnc/xstartup
```

Add this content:

```bash
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
```

Make it executable:

```bash
chmod +x ~/.vnc/xstartup

# Start VNC
vncserver :1 -geometry 1920x1080 -depth 24
```

### Step 5: Connect via VNC from Your Mac

**Option A: SSH Tunnel (Recommended - Secure)**

```bash
# On your Mac - create SSH tunnel
ssh -i sora-scraper.pem -L 5901:localhost:5901 ubuntu@YOUR_EC2_IP -N -f

# Now connect with VNC viewer to: localhost:5901
```

**Option B: Direct VNC (Less secure)**

1. Make sure Security Group allows port 5901 from your IP
2. Connect to: `YOUR_EC2_IP:5901`

**Mac VNC Clients:**
- Built-in: Finder → Go → Connect to Server → `vnc://localhost:5901`
- RealVNC Viewer (free)
- TigerVNC Viewer

### Step 6: Deploy Scraper (In VNC Desktop)

Now you have a visual desktop! Open terminal in VNC:

```bash
# Clone project
cd ~
git clone https://github.com/ethan0905/scrapper_sora2.git
cd scrapper_sora2

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/requirements.txt
pip install -r requirements/requirements_selenium.txt
pip install -r requirements/requirements_vision.txt

# Create necessary directories
mkdir -p logs videos_batch single-upload

# Configure credentials
nano .env  # Add OPENAI_API_KEY
nano youtube_credentials.json  # Add YouTube credentials
nano batch_urls.txt  # Add your 500 URLs
```

### Step 7: Manual Login & Session Setup

This is the key part - you'll login manually once:

```bash
# Start Chrome in debugging mode (visible)
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-profile" &

# Chrome opens! Now manually:
# 1. Go to https://sora.chatgpt.com/
# 2. Login with your account
# 3. Complete any 2FA or verification
# 4. Browse a few pages normally (avoid bot detection)
# 5. Keep Chrome open
```

**Important**: Don't close Chrome! It stays open with your session.

### Step 8: Start Scraper (Uses Existing Chrome)

In VNC terminal:

```bash
# Start screen session
screen -S scraper

# Activate environment
cd ~/scrapper_sora2
source venv/bin/activate

# Run scraper connected to YOUR logged-in Chrome
python main.py \
  --batch batch_urls.txt \
  --max 999 \
  --slow \
  --use-existing \
  --output videos_batch

# You'll SEE Chrome navigating in real-time!
# Watch it work for a few minutes
# When happy, detach: Ctrl+A then D
```

### Step 9: Monitor Progress

**Via VNC (Visual):**
- Connect to VNC anytime
- See Chrome navigating
- Watch terminal output
- Check for errors visually

**Via SSH (Command Line):**

```bash
# SSH from Mac
ssh -i sora-scraper.pem ubuntu@YOUR_EC2_IP

# Reattach to scraper
screen -r scraper

# Or check logs
tail -f ~/scrapper_sora2/logs/scraper.log

# Count videos
ls ~/scrapper_sora2/videos_batch/*.mp4 | wc -l

# Disk space
df -h

# Memory usage
free -h

# Process status
ps aux | grep python
```

**Monitoring Dashboard (Optional):**

Create a simple monitoring script:

```bash
nano ~/monitor.sh
```

```bash
#!/bin/bash
# monitor.sh - Quick scraping status

clear
echo "=================================="
echo "🎬 SORA SCRAPER STATUS"
echo "=================================="
echo ""

echo "📹 Videos downloaded:"
ls ~/scrapper_sora2/videos_batch/*.mp4 2>/dev/null | wc -l

echo ""
echo "💾 Disk usage:"
df -h / | tail -1 | awk '{print "   Used: " $3 " / " $2 " (" $5 ")"}'

echo ""
echo "🧠 Memory:"
free -h | grep Mem | awk '{print "   Used: " $3 " / " $2}'

echo ""
echo "⏰ Scraper running:"
if ps aux | grep -q "[m]ain.py"; then
    echo "   ✅ YES"
    ps aux | grep "[m]ain.py" | awk '{print "   PID: " $2}'
else
    echo "   ❌ NO"
fi

echo ""
echo "📊 Recent log (last 10 lines):"
tail -10 ~/scrapper_sora2/logs/scraper.log 2>/dev/null || echo "   No logs yet"

echo ""
echo "=================================="
```

```bash
chmod +x ~/monitor.sh

# Run anytime
~/monitor.sh
```

### Step 10: Keep Chrome Session Alive

Chrome might close if you disconnect. Fix this:

**Create systemd service for Chrome:**

```bash
sudo nano /etc/systemd/system/chrome-session.service
```

```ini
[Unit]
Description=Chrome Session for Sora Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
Environment="DISPLAY=:1"
ExecStart=/usr/bin/google-chrome --remote-debugging-port=9222 --user-data-dir=/home/ubuntu/.chrome-profile --no-first-run --no-default-browser-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable chrome-session
sudo systemctl start chrome-session
sudo systemctl status chrome-session
```

Now Chrome auto-starts and stays running!

### Step 11: Auto-Restart Scraper on Crash

```bash
sudo nano /etc/systemd/system/sora-scraper.service
```

```ini
[Unit]
Description=Sora Video Scraper
After=chrome-session.service
Requires=chrome-session.service

[Service]
Type=simple
User=ubuntu
Environment="DISPLAY=:1"
WorkingDirectory=/home/ubuntu/scrapper_sora2
ExecStart=/home/ubuntu/scrapper_sora2/venv/bin/python main.py --batch batch_urls.txt --max 999 --slow --use-existing --output videos_batch
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable sora-scraper
sudo systemctl start sora-scraper
sudo systemctl status sora-scraper
```

## Monitoring Options

### Option 1: VNC (Visual - Best for Setup/Debugging)

✅ See Chrome window  
✅ Click around if needed  
✅ Debug visually  
❌ Requires VNC connection  

### Option 2: SSH + Screen (Command Line - Best for Daily Checks)

✅ Fast, lightweight  
✅ Works from phone  
✅ Low bandwidth  
❌ No visual feedback  

### Option 3: Web Monitoring (Optional - Best for Remote Teams)

Install a web dashboard:

```bash
# Install Cockpit (web dashboard)
sudo apt install -y cockpit
sudo systemctl enable --now cockpit.socket

# Access at: https://YOUR_EC2_IP:9090
# Monitor CPU, RAM, disk, processes
```

### Option 4: Logs + Alerts

Send alerts when issues occur:

```bash
# Install monitoring
pip install watchdog

# Create alert script
nano ~/alert.py
```

```python
#!/usr/bin/env python3
import time
import os
from pathlib import Path

last_count = 0
error_count = 0

while True:
    # Count videos
    videos = list(Path("/home/ubuntu/scrapper_sora2/videos_batch").glob("*.mp4"))
    current_count = len(videos)
    
    # Check if stuck (no new videos in 1 hour)
    if current_count == last_count:
        error_count += 1
        if error_count > 12:  # 12 * 5min = 1 hour
            print(f"⚠️ ALERT: No new videos in 1 hour! Count: {current_count}")
            # Could send email/SMS here
    else:
        error_count = 0
        print(f"✅ OK: {current_count} videos ({current_count - last_count} new)")
    
    last_count = current_count
    time.sleep(300)  # Check every 5 minutes
```

```bash
chmod +x ~/alert.py

# Run in screen
screen -S monitor
python3 ~/alert.py
# Ctrl+A, D to detach
```

## Troubleshooting

### Chrome Session Lost

```bash
# Check if Chrome is running
ps aux | grep chrome

# Restart Chrome with your profile
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-profile" &

# Re-login if needed (via VNC)
```

### Scraper Stuck

```bash
# Check logs
tail -100 ~/scrapper_sora2/logs/scraper.log

# Restart scraper
screen -r scraper
# Ctrl+C to stop
# Restart: python main.py ...
```

### Out of Disk Space

```bash
# Check space
df -h

# Sync videos to local, then delete from EC2
./scripts/sync_videos.sh YOUR_EC2_IP
ssh -i sora-scraper.pem ubuntu@YOUR_EC2_IP "rm ~/scrapper_sora2/videos_batch/*.mp4"

# Or resize disk in AWS Console
```

## Cost Optimization

### Development/Testing Phase ($10/month)

- **t3.small**: 2GB RAM, 1 vCPU
- Start/stop when not using
- Only pay for hours used

### Production Phase ($30-40/month)

- **t3.medium**: 4GB RAM, 2 vCPU
- Leave running 24/7
- Or use Spot Instances (70% cheaper!)

### Storage

- **EBS**: $0.10/GB/month (e.g., 100GB = $10/month)
- Sync to local and delete from EC2 regularly
- Or use S3 for long-term ($0.023/GB/month)

## Summary

**Manual Login Solution:**
1. ✅ Deploy EC2 with VNC desktop
2. ✅ Start Chrome manually in VNC
3. ✅ Login to Sora yourself (no bot detection)
4. ✅ Run scraper using `--use-existing` flag
5. ✅ Monitor via VNC or SSH anytime
6. ✅ Chrome session persists (systemd service)
7. ✅ Auto-restart on crash

**Benefits:**
- No automated login (bypasses bot detection)
- Visual monitoring available anytime
- Session persists between runs
- Auto-recovers from crashes
- Full control over the process

**Monitoring Options:**
- VNC: Visual Chrome window
- SSH: Command line, logs
- Web: Cockpit dashboard
- Alerts: Custom monitoring scripts

This gives you the best of both worlds: automated scraping with manual login control! 🚀
