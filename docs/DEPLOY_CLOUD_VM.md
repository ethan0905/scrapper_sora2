# 🚀 Deploy Scraper on Cloud VM

## Overview

Deploy the scraper on a cloud VM to run automated batch scraping for days/weeks with proper US VPN routing.

## Recommended: DigitalOcean Droplet

### Step 1: Create VM

1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Create a Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($12/month - 2GB RAM, 1 CPU)
   - **Datacenter**: New York or San Francisco (for US IP)
   - **Add SSH key** for secure access

### Step 2: Connect and Setup

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Chrome and dependencies
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt update
apt install -y google-chrome-stable

# Install ChromeDriver
apt install -y chromium-chromedriver

# Install screen (for persistent sessions)
apt install -y screen tmux
```

### Step 3: Deploy Project

```bash
# Clone your project
cd /root
git clone git@github.com:ethan0905/scrapper_sora2.git
cd scrapper_sora2

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/requirements.txt
pip install -r requirements/requirements_selenium.txt
pip install -r requirements/requirements_vision.txt

# Setup credentials
nano youtube_credentials.json  # Paste your credentials
nano .env  # Add your OPENAI_API_KEY
```

### Step 4: Configure for US Location

The VM is already in the US (if you chose NY/SF datacenter), but for extra safety:

```bash
# Install and configure NordVPN or similar
# Or use a US proxy
```

### Step 5: Prepare Batch File

```bash
# Create your URLs file
nano batch_urls.txt
# Paste your 500 URLs (one per line)
```

### Step 6: Run in Background

```bash
# Start a screen session (persists after disconnect)
screen -S scraper

# Run the scraper
python main.py \
  --batch batch_urls.txt \
  --max 999 \
  --slow \
  --output videos_batch

# Detach from screen: Press Ctrl+A then D
# Reattach later: screen -r scraper
```

### Step 7: Monitor Progress

```bash
# Check logs
tail -f logs/scraper.log

# Check videos downloaded
ls -lh videos_batch/

# Check disk space
df -h

# Reattach to screen session
screen -r scraper
```

## Video Storage Options

### Option A: Store on VM (Simple)

- **Pros**: Easy, fast access
- **Cons**: Limited by VM disk size (usually 25-100GB)
- **Cost**: Included in VM price

```bash
# Check available space
df -h

# If needed, resize disk in DigitalOcean console
```

### Option B: AWS S3 (Scalable)

- **Pros**: Unlimited storage, cheap ($0.023/GB/month)
- **Cons**: Requires AWS setup, transfer costs
- **Good for**: Long-term storage, backup

```bash
# Install AWS CLI
pip install boto3 awscli

# Configure AWS
aws configure

# Auto-upload after each scrape
python scripts/upload_to_s3.py
```

### Option C: DigitalOcean Spaces (Easy S3 Alternative)

- **Pros**: Simpler than AWS, $5/month for 250GB
- **Cons**: Slightly more expensive than S3

```bash
# Same as S3, but easier setup
# Compatible with boto3/awscli
```

### Option D: Rsync to Local Machine

- **Pros**: Keep videos on your local machine
- **Cons**: Requires stable connection

```bash
# From your local machine (run daily)
rsync -avz --progress root@YOUR_DROPLET_IP:/root/scrapper_sora2/videos_batch/ ./local_videos/
```

## Prevent OpenAI Ban

### 1. Rate Limiting

Edit `src/utils/vision_title_generator.py`:

```python
import time
from datetime import datetime, timedelta

class VisionTitleGenerator:
    def __init__(self):
        # ...existing code...
        self.last_call_time = None
        self.min_delay = 2  # Minimum 2 seconds between calls
        self.calls_per_minute = 20  # Max 20 calls per minute
        self.call_times = []
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        now = datetime.now()
        
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if now - t < timedelta(minutes=1)]
        
        # If we've hit the limit, wait
        if len(self.call_times) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.call_times[0]).seconds
            if sleep_time > 0:
                print(f"⏳ Rate limit reached, waiting {sleep_time}s...")
                time.sleep(sleep_time)
        
        # Enforce minimum delay
        if self.last_call_time:
            elapsed = (now - self.last_call_time).total_seconds()
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        
        self.last_call_time = now
        self.call_times.append(now)
    
    def generate_title(self, video_path, ...):
        self._rate_limit()  # Call before API request
        # ...existing code...
```

### 2. Use Vision Only When Needed

Don't use vision titles for scraping - only for YouTube uploads:

```bash
# Scraping: NO vision calls
python main.py --batch batch_urls.txt --max 999 --slow --metadata-only

# Later: Upload with vision titles (rate-limited)
python src/utils/auto_uploader.py
```

### 3. OpenAI API Limits

- **Free tier**: 3 RPM (requests per minute)
- **Tier 1** ($5 spent): 500 RPM
- **Tier 2** ($50 spent): 5,000 RPM

**Recommendation**: Spend $5 to unlock Tier 1, then rate-limit to 20 RPM to be safe.

### 4. Separate Keys

Use different API keys for different tasks:
- One for vision title generation
- One for other OpenAI tasks (if any)

## US Location / VPN

### Option 1: Use US Datacenter (Easiest)

When creating your VM, choose a US region:
- **DigitalOcean**: New York, San Francisco
- **AWS**: us-east-1, us-west-2
- **Google Cloud**: us-central1

**Pros**: Built-in US IP, no VPN needed
**Cons**: None for this use case

### Option 2: VPN on VM (Extra Layer)

If you want extra protection:

```bash
# Install OpenVPN
apt install -y openvpn

# Or NordVPN
wget https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn-release_1.0.0_all.deb
dpkg -i nordvpn-release_1.0.0_all.deb
apt update
apt install -y nordvpn

# Connect to US server
nordvpn login
nordvpn connect United_States

# Verify location
curl ifconfig.me
curl https://ipapi.co/json/
```

### Option 3: Residential Proxy (Most Reliable)

For maximum safety from Sora detection:

**Providers:**
- **Bright Data** (expensive but best)
- **Smartproxy** (good balance)
- **Oxylabs** (enterprise)

```bash
# Configure Selenium to use proxy
# Edit src/scraper/scraper.py
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--proxy-server=http://PROXY_IP:PORT')
```

## Complete Deployment Script

```bash
#!/bin/bash
# deploy.sh - Complete deployment on fresh Ubuntu VM

set -e

echo "🚀 Deploying Sora Scraper..."

# Update system
apt update && apt upgrade -y

# Install Python
apt install -y python3.11 python3.11-venv python3-pip

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt update
apt install -y google-chrome-stable chromium-chromedriver

# Install utilities
apt install -y screen tmux git curl

# Clone project
cd /root
git clone git@github.com:ethan0905/scrapper_sora2.git
cd scrapper_sora2

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements/requirements.txt
pip install -r requirements/requirements_selenium.txt
pip install -r requirements/requirements_vision.txt

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Add credentials: nano youtube_credentials.json"
echo "2. Add API key: nano .env"
echo "3. Add URLs: nano batch_urls.txt"
echo "4. Start scraping: screen -S scraper"
echo "   python main.py --batch batch_urls.txt --max 999 --slow"
```

## Monitoring & Maintenance

### Daily Checks

```bash
# Check scraper status
screen -r scraper

# Check disk space
df -h

# Check logs
tail -100 logs/scraper.log

# Check progress
ls -lh videos_batch/ | wc -l
```

### Auto-Restart on Crash

Create a systemd service:

```bash
# Create service file
nano /etc/systemd/system/sora-scraper.service
```

```ini
[Unit]
Description=Sora Video Scraper
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/scrapper_sora2
Environment="PATH=/root/scrapper_sora2/venv/bin"
ExecStart=/root/scrapper_sora2/venv/bin/python main.py --batch batch_urls.txt --max 999 --slow
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
systemctl enable sora-scraper
systemctl start sora-scraper
systemctl status sora-scraper
```

## Cost Estimate (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| DigitalOcean VM | $12 | 2GB RAM, 50GB disk |
| Extra Storage (optional) | $5 | DigitalOcean Spaces (250GB) |
| VPN (optional) | $10 | NordVPN or similar |
| OpenAI API | $5-20 | Depends on usage |
| **Total** | **$27-47** | Per month |

## Summary

1. **✅ Use DigitalOcean VM** in US datacenter (NY/SF)
2. **✅ Store videos on VM** (upgrade disk if needed) or sync to local
3. **✅ Rate-limit OpenAI calls** to 20 RPM, spend $5 for Tier 1
4. **✅ US location built-in** (VM in US datacenter)
5. **✅ Run in `screen`** for persistent sessions
6. **✅ Monitor daily** and sync videos to local machine

This setup will let you run batch scraping for days/weeks reliably! 🚀
