# 🎉 Automated YouTube Uploader - Setup Complete!

## What We Built

You now have a **fully automated YouTube upload system** that runs 24/7 in the background without any manual intervention!

### Key Features

✅ **Automatic uploads** - Every 8 hours, picks a video and uploads to YouTube  
✅ **AI-powered titles** - GPT-4o vision analyzes video for perfect titles  
✅ **Smart descriptions** - Auto-generated with SEO hashtags  
✅ **Background service** - Runs 24/7, auto-starts on reboot  
✅ **Easy management** - Simple CLI commands to control everything  
✅ **Complete logging** - Track every upload, catch every error  
✅ **State tracking** - Never uploads the same video twice  
✅ **Auto-organization** - Moves uploaded videos automatically  

---

## 🚀 Quick Start - Get Running in 60 Seconds

### Step 1: Install the Service

```bash
./scripts/service.sh install
```

This will:
- Install the background service
- Load it into macOS LaunchAgent
- Start the uploader automatically
- Configure it to start on reboot

### Step 2: Add Videos

```bash
# Copy videos to the upload folder
cp your-videos/*.mp4 single-upload/
```

### Step 3: Check Status

```bash
./scripts/service.sh status
```

**That's it!** The system is now running and will automatically upload videos every 8 hours.

---

## 📋 Service Management Commands

### Essential Commands

```bash
# Check if service is running
./scripts/service.sh status

# Watch uploads in real-time
./scripts/service.sh logs

# View error log
./scripts/service.sh errors

# Restart the service
./scripts/service.sh restart

# Stop the service
./scripts/service.sh stop

# Start the service
./scripts/service.sh start

# Remove the service
./scripts/service.sh uninstall
```

### What Each Command Does

- **`status`** - Shows service state, queue size, upload history, next upload time
- **`logs`** - Live streaming of upload logs (Ctrl+C to exit)
- **`errors`** - Shows error log if any issues occurred
- **`restart`** - Restarts the service (use after config changes)
- **`stop`** - Stops the uploader (videos stay in queue)
- **`start`** - Starts the uploader
- **`uninstall`** - Completely removes the service

---

## 📁 File Structure

```
scrapper_sora2/
│
├── single-upload/               # 📤 Drop videos here!
│   ├── your-video.mp4          # ← Videos ready to upload
│   ├── .upload_state.json      # Upload history & schedule
│   ├── upload_scheduler.log    # Detailed logs
│   └── uploaded/               # ✅ Completed uploads
│       └── done-video.mp4
│
├── scripts/
│   ├── service.sh              # 🎯 Main CLI tool (USE THIS!)
│   ├── start_uploader.sh       # Startup script
│   └── com.sora.youtube.uploader.plist  # LaunchAgent config
│
├── src/utils/
│   ├── auto_uploader.py        # 🤖 Background uploader
│   └── vision_title_generator.py  # 🎥 AI vision titles
│
├── docs/
│   ├── AUTOMATED_UPLOADER.md   # Full documentation
│   └── ...
│
├── QUICK_START_UPLOADER.md     # This guide
└── README.md                   # Project overview
```

---

## 🎬 How It Works

### Upload Cycle (Every 8 Hours)

```
1. ⏰ Wait for scheduled time
   │
2. 📁 Check single-upload/ for videos
   │
3. 🎥 Pick next video (alphabetically)
   │
4. 🖼️  Extract 4 frames from video
   │
5. 🤖 Send frames to GPT-4o vision
   │
6. 📝 Generate engaging title
   │
7. 📄 Create description with hashtags
   │
8. ⬆️  Upload to YouTube
   │
9. ✅ Move to uploaded/ folder
   │
10. 💾 Save state and log results
    │
11. ⏰ Wait 8 hours and repeat
```

### Example Upload

**Video:** `cat-playing-piano.mp4`

**AI Title:** "Cat Plays Beethoven on Piano with Perfect Technique 🐱🎹 #SoraAI"

**Description:**
```
AI-generated video created with Sora.

Follow for more AI content!

#SoraAI #AIVideo #GenerativeAI #OpenAI #ArtificialIntelligence
```

**Upload:** Public, Not for kids

**Result:** Video uploaded, moved to `uploaded/`, state saved

---

## ⚙️ Configuration

### Change Upload Interval

Edit `scripts/start_uploader.sh`:

```bash
--interval 8     # ← Change to: 4, 6, 12, or 24 hours
```

Then restart:
```bash
./scripts/service.sh restart
```

**Popular intervals:**
- `4` hours = 6 videos/day
- `6` hours = 4 videos/day
- `8` hours = 3 videos/day ← **DEFAULT**
- `12` hours = 2 videos/day
- `24` hours = 1 video/day

### Change Privacy Setting

Edit `scripts/start_uploader.sh`:

```bash
--privacy public    # ← Change to: unlisted, private
```

### Disable AI Titles (Faster but less engaging)

Edit `scripts/start_uploader.sh`:

```bash
--no-vision         # ← Add this flag
```

### Control Upload Order

Videos upload alphabetically. To control order, name them:

```bash
001-first.mp4
002-second.mp4
003-third.mp4
```

---

## 📊 Monitoring

### Check Current Status

```bash
$ ./scripts/service.sh status

╔════════════════════════════════════════════════════════════╗
║     🤖 Automated YouTube Uploader - Service Manager       ║
╚════════════════════════════════════════════════════════════╝

✅ Service is installed
✅ Service is RUNNING
   PID: 12345

📹 Videos in queue: 5
✅ Videos uploaded: 12
⏰ Last upload: 2024-12-17T14:30:00

📋 Recent log entries:
   2024-12-17 14:30:00 - INFO - ✅ Upload complete!
   2024-12-17 14:30:00 - INFO - Video ID: abc123xyz
   2024-12-17 14:29:45 - INFO - ⬆️  Uploading to YouTube...
```

### Watch Live Logs

```bash
$ ./scripts/service.sh logs

⏰ Waiting for next upload...
   Time remaining: 5.2 hours

📹 Videos in queue: 5
✅ Videos uploaded: 12
⏰ Next upload: 2024-12-17 22:00:00

[Live streaming... Press Ctrl+C to exit]
```

### Check Upload History

```bash
$ cat single-upload/.upload_state.json

{
  "last_upload_time": "2024-12-17T14:30:00",
  "uploaded_videos": [
    "/Users/ethan/Desktop/scrapper_sora2/single-upload/video1.mp4",
    "/Users/ethan/Desktop/scrapper_sora2/single-upload/video2.mp4"
  ],
  "queue": []
}
```

---

## 🐛 Troubleshooting

### Problem: Service won't start

**Solution:**
```bash
# Check for errors
./scripts/service.sh errors

# Try reinstalling
./scripts/service.sh uninstall
./scripts/service.sh install
```

### Problem: Videos not uploading

**Check:**
1. Is service running? `./scripts/service.sh status`
2. Are videos in correct format? `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
3. Check logs: `./scripts/service.sh logs`
4. Check errors: `./scripts/service.sh errors`

### Problem: Upload failed

**Common causes:**
- YouTube quota exceeded (wait 24 hours)
- Video too large (max 256GB)
- Invalid credentials (regenerate token)
- Network issues (check connection)

**Solution:**
```bash
# Check error details
./scripts/service.sh errors

# Restart service
./scripts/service.sh restart
```

### Problem: AI title generation failed

**Check:**
1. OpenAI API key: `cat .env | grep OPENAI_API_KEY`
2. API key valid: Visit https://platform.openai.com/usage
3. Check logs: `./scripts/service.sh logs`

**Fallback:** System uses basic titles if AI fails

### Problem: Service running but not uploading

**Check schedule:**
```bash
# View last upload and next scheduled time
./scripts/service.sh status
```

**Manually trigger upload (testing):**
```bash
# Stop service
./scripts/service.sh stop

# Run manually with instant upload
python src/utils/auto_uploader.py --interval 0.001

# Restart service when done
./scripts/service.sh start
```

---

## 📖 Documentation

### Quick References
- **[This Guide](QUICK_START_UPLOADER.md)** - Quick start and commands
- **[Upload Folder Guide](single-upload/README.md)** - Using the upload folder
- **[Service CLI Help](scripts/service.sh)** - Run `./scripts/service.sh help`

### Detailed Documentation
- **[Full Automated Uploader Guide](docs/AUTOMATED_UPLOADER.md)** - Complete documentation
- **[Vision Title Generator](docs/VISION_TITLE_GENERATOR.md)** - How AI titles work
- **[Customize Vision Prompts](docs/CUSTOMIZE_VISION_PROMPT.md)** - Edit title style

---

## 🎯 Tips & Best Practices

### Optimize Success Rate
1. **Use MP4 format** - Most reliable for YouTube
2. **Name videos clearly** - Helps with organization
3. **Monitor logs regularly** - Catch issues early
4. **Check quota** - YouTube has daily upload limits

### Speed Up Processing
1. **Reduce interval** - Upload more frequently (4-6 hours)
2. **Disable vision** - Use `--no-vision` for faster uploads
3. **Pre-process videos** - Ensure optimal encoding

### Track Performance
1. **Monitor state file** - Check `.upload_state.json`
2. **Review logs** - Identify patterns and issues
3. **Check YouTube Analytics** - Track video performance

---

## 🚦 Next Steps

Now that your automated uploader is running, you can:

### 1. Add More Videos
```bash
# Add videos anytime
cp more-videos/*.mp4 single-upload/

# Check queue
./scripts/service.sh status
```

### 2. Monitor Performance
```bash
# Watch uploads happen
./scripts/service.sh logs

# Check upload history
cat single-upload/.upload_state.json
```

### 3. Customize Titles
Edit `src/utils/vision_title_generator.py` to customize:
- System prompt (line 26)
- Style prompts (line 52)
- Title format

### 4. Check YouTube
Visit https://youtube.com to see your uploaded videos!

---

## 💡 Advanced Usage

### Manual Upload (Testing)

```bash
# Run manually with custom settings
python src/utils/auto_uploader.py \
  --folder single-upload \
  --interval 4 \
  --privacy unlisted \
  --no-vision
```

### Change Log Location

Edit `scripts/start_uploader.sh`:
```bash
LOG_FILE="$PROJECT_DIR/my-logs/upload.log"
```

### Generate Titles Separately

```bash
# Test title generation
python src/utils/vision_title_generator.py single-upload/video.mp4

# Batch generate
python src/utils/vision_title_generator.py single-upload/ -o titles.json
```

---

## ✅ System Requirements

### Required
- macOS (for LaunchAgent)
- Python 3.8+
- YouTube API credentials
- OpenAI API key
- Internet connection

### Verified Working On
- macOS Monterey (12.x)
- macOS Ventura (13.x)
- macOS Sonoma (14.x)
- macOS Sequoia (15.x)

---

## 🎉 You're All Set!

Your automated YouTube uploader is now running in the background!

### What's Happening Now:
- ✅ Service is running 24/7
- ✅ Will auto-start on reboot
- ✅ Uploading videos every 8 hours
- ✅ Generating AI titles automatically
- ✅ Organizing uploaded videos
- ✅ Logging everything

### You can:
- Drop videos in `single-upload/` anytime
- Check status with `./scripts/service.sh status`
- Monitor with `./scripts/service.sh logs`
- Relax - it's all automatic! 🎉

---

## 📞 Getting Help

### Check Status First
```bash
./scripts/service.sh status
```

### View Logs
```bash
./scripts/service.sh logs
./scripts/service.sh errors
```

### Read Documentation
- `QUICK_START_UPLOADER.md` (this file)
- `docs/AUTOMATED_UPLOADER.md`
- `single-upload/README.md`

---

**Happy Uploading! 🚀📹**

Generated: December 17, 2024
Version: 1.0
