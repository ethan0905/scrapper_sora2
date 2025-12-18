# 🎯 AWS EC2 Manual Login - Quick Reference

## One-Line Setup

```bash
# On EC2 (after SSH connection)
curl -sSL https://raw.githubusercontent.com/ethan0905/scrapper_sora2/main/scripts/aws_setup_vnc.sh | bash
```

## Connect to VNC

```bash
# From your Mac - Create SSH tunnel
ssh -i YOUR_KEY.pem -L 5901:localhost:5901 ubuntu@YOUR_EC2_IP -N -f

# Open VNC viewer
# macOS: Finder → Go → Connect to Server
# Enter: vnc://localhost:5901
```

## Manual Login Flow

```bash
# In VNC desktop terminal:

# 1. Start Chrome with debugging
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-profile" &

# 2. Login to Sora manually (Chrome window appears)
# Go to: https://sora.chatgpt.com/
# Complete login, 2FA, etc.
# Browse normally to avoid bot detection

# 3. Keep Chrome open!

# 4. Configure scraper
cd ~/scrapper_sora2
nano .env  # Add OPENAI_API_KEY
nano batch_urls.txt  # Add 500 URLs

# 5. Start scraping (uses your logged-in Chrome)
screen -S scraper
source venv/bin/activate
python main.py --batch batch_urls.txt --max 999 --slow --use-existing --output videos_batch

# 6. Detach: Ctrl+A then D
```

## Monitor Progress

### Via VNC (Visual)
- Connect anytime
- See Chrome navigating
- Watch terminal output

### Via SSH (Command Line)

```bash
# Real-time dashboard
~/scrapper_sora2/scripts/monitor.sh

# Or manually check
screen -r scraper  # Reattach
tail -f ~/scrapper_sora2/logs/scraper.log  # Logs
ls ~/scrapper_sora2/videos_batch/*.mp4 | wc -l  # Count videos
```

## Key Benefits

✅ **No bot detection** - You login manually  
✅ **Visual monitoring** - See Chrome working  
✅ **Session persists** - Chrome stays logged in  
✅ **Auto-recovery** - Systemd restarts on crash  
✅ **Full control** - Intervene anytime via VNC  

## Costs

- **t3.medium**: ~$30/month (4GB RAM, 2 vCPU)
- **t3.small**: ~$15/month (2GB RAM, 1 vCPU) - for testing
- **Storage**: ~$10/month for 100GB
- **Total**: ~$25-40/month

## Troubleshooting

```bash
# Chrome not running?
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-profile" &

# Scraper stopped?
screen -r scraper
# Ctrl+C, then restart:
python main.py --batch batch_urls.txt --max 999 --slow --use-existing

# VNC not working?
vncserver -kill :1
vncserver :1 -geometry 1920x1080 -depth 24

# Check SSH tunnel
ps aux | grep "ssh.*5901"
```

## Sync Videos to Local

```bash
# From your Mac
./scripts/sync_videos.sh YOUR_EC2_IP
```

## Full Documentation

- **Complete Guide**: [docs/AWS_MANUAL_LOGIN.md](AWS_MANUAL_LOGIN.md)
- **Cloud Deployment**: [docs/DEPLOY_CLOUD_VM.md](DEPLOY_CLOUD_VM.md)
- **Quick Start**: [docs/QUICK_START_CLOUD.md](QUICK_START_CLOUD.md)

---

**This is the best approach for avoiding bot detection while scraping at scale!** 🚀
