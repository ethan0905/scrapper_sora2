# 🚀 Quick Start: Deploy to Cloud for Large-Scale Scraping

## TL;DR - Fast Setup

```bash
# 1. Create DigitalOcean Droplet (Ubuntu 22.04, US datacenter)
# 2. SSH into it
ssh root@YOUR_DROPLET_IP

# 3. Run deployment script
curl -sSL https://raw.githubusercontent.com/ethan0905/scrapper_sora2/main/scripts/deploy.sh | bash

# 4. Configure
cd /root/scrapper_sora2
nano .env  # Add: OPENAI_API_KEY=your-key
nano batch_urls.txt  # Add your 500 URLs

# 5. Start scraping
screen -S scraper
source venv/bin/activate
python main.py --batch batch_urls.txt --max 999 --slow --output videos_batch

# 6. Detach: Ctrl+A then D
# It keeps running! Come back anytime: screen -r scraper
```

## Why Cloud VM?

✅ **Runs for days/weeks** - No timeout limits  
✅ **US IP address** - Works with Sora (choose US datacenter)  
✅ **Browser support** - Chrome/Selenium works  
✅ **Persistent** - Survives disconnects  
✅ **Cheap** - $12-30/month  

❌ **Not Vercel** - Has 60s timeout, no browser, no storage

## Features

- ✅ **Automated deployment** - One-command setup
- ✅ **OpenAI rate limiting** - Prevents API bans (20 RPM)
- ✅ **Video sync script** - Download to local machine
- ✅ **Screen sessions** - Persistent execution
- ✅ **US location** - Built-in if using US datacenter
- ✅ **Logs** - Full monitoring and error tracking

## Cost Breakdown

| Item | Cost/Month | Notes |
|------|------------|-------|
| DigitalOcean VM | $12 | 2GB RAM, 50GB disk |
| OpenAI API | $5-20 | Tier 1 ($5 spent) = 500 RPM |
| **Total** | **$17-32** | All-inclusive |

Optional:
- VPN: $10/month (NordVPN) - Only if needed for extra safety
- Extra storage: $5/month (DigitalOcean Spaces)

## Sync Videos to Local

Run daily from your local machine:

```bash
./scripts/sync_videos.sh YOUR_DROPLET_IP
```

This backs up all videos to `./videos_synced/`

## Monitor Progress

```bash
# Reattach to scraper
screen -r scraper

# Check logs
tail -f logs/scraper.log

# Count videos
ls -lh videos_batch/*.mp4 | wc -l

# Check disk space
df -h
```

## Full Documentation

See [docs/DEPLOY_CLOUD_VM.md](./DEPLOY_CLOUD_VM.md) for complete guide including:
- VPN setup
- Auto-restart on crash
- S3 storage options
- Monitoring tools
- Troubleshooting

## Questions Answered

**Q: Where to store videos?**  
A: On the VM (50GB included), sync to local daily, or use S3 for unlimited

**Q: How to prevent OpenAI ban?**  
A: Rate limiting built-in (20 RPM), spend $5 for Tier 1 access

**Q: Sora only works in US, I'm in France?**  
A: Use US datacenter (NY/SF) = instant US IP, or add VPN for extra safety

**Q: How long can it run?**  
A: Days, weeks, months - no timeout limits on cloud VMs

**Q: What if it crashes?**  
A: Use systemd service for auto-restart (see full guide)

## Ready to Deploy?

1. Create [DigitalOcean account](https://www.digitalocean.com/) (US datacenter)
2. Run the deployment script (takes 5 minutes)
3. Start scraping your 500 URLs
4. Sync videos to local machine daily

That's it! 🎉
