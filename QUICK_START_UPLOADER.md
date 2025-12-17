# 🚀 Quick Start - Automated YouTube Uploader

## TL;DR - Get Running in 60 Seconds

```bash
# 1. Install the background service
./scripts/service.sh install

# 2. Add a video
cp your-video.mp4 single-upload/

# 3. That's it! Check status:
./scripts/service.sh status
```

The uploader is now running in the background and will automatically:
- Upload 1 video every 8 hours
- Generate AI-powered titles
- Restart automatically on reboot
- Move uploaded videos to `single-upload/uploaded/`

---

## Commands Reference

### Service Management

```bash
# Install and start (first time)
./scripts/service.sh install

# Check if it's running
./scripts/service.sh status

# Watch uploads in real-time
./scripts/service.sh logs

# Stop the service
./scripts/service.sh stop

# Start the service
./scripts/service.sh start

# Restart (after config changes)
./scripts/service.sh restart

# Remove the service
./scripts/service.sh uninstall
```

### Manual Control (Advanced)

```bash
# Run manually (for testing)
python src/utils/auto_uploader.py

# Change upload interval
python src/utils/auto_uploader.py --interval 4  # Every 4 hours

# Change privacy setting
python src/utils/auto_uploader.py --privacy unlisted

# Disable AI titles (faster, but less engaging)
python src/utils/auto_uploader.py --no-vision
```

---

## How to Use

### Adding Videos

Just drop videos into the `single-upload` folder:

```bash
# Single video
cp my-video.mp4 single-upload/

# Multiple videos
cp video1.mp4 video2.mp4 video3.mp4 single-upload/

# From a folder
cp videos/*.mp4 single-upload/
```

**Supported formats:** `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

### Upload Order

Videos are uploaded **alphabetically**. To control order, name them:

```bash
001-first-video.mp4
002-second-video.mp4
003-third-video.mp4
```

### Checking Status

```bash
# Quick status check
./scripts/service.sh status

# Output shows:
# ✅ Service is RUNNING
# 📹 Videos in queue: 3
# ✅ Videos uploaded: 12
# ⏰ Last upload: 2024-12-17T14:30:00
```

### Monitoring Uploads

```bash
# Watch live logs (Ctrl+C to exit)
./scripts/service.sh logs

# Check for errors
./scripts/service.sh errors

# View upload history
cat single-upload/.upload_state.json
```

---

## Upload Schedule

**Default:** Every **8 hours**

### Typical Schedule Example

- **10:00 AM** - First upload
- **6:00 PM** - Second upload
- **2:00 AM** - Third upload
- **10:00 AM** - Fourth upload (repeat)

### Changing the Schedule

Edit `scripts/start_uploader.sh`:

```bash
# Change this line:
    --interval 8 \     # ← Change to 4, 6, 12, or 24

# Then restart:
./scripts/service.sh restart
```

**Popular intervals:**
- `4` - Every 4 hours (6 videos/day)
- `6` - Every 6 hours (4 videos/day)
- `8` - Every 8 hours (3 videos/day) **← DEFAULT**
- `12` - Every 12 hours (2 videos/day)
- `24` - Once per day (1 video/day)

---

## What Happens During Upload?

### 1. Video Selection
- Picks the next video (alphabetically)
- Skips already uploaded videos

### 2. AI Title Generation
- Extracts 10 key frames from video
- Analyzes with GPT-4o vision
- Generates engaging title with emoji and hashtag

### 3. Upload to YouTube
- Title: AI-generated
- Description: Auto-generated with hashtags
- Privacy: Public (default)
- Made for Kids: No

### 4. Post-Upload
- Moves video to `single-upload/uploaded/`
- Logs upload details
- Waits 8 hours for next upload

---

## Troubleshooting

### "Service is NOT running"

```bash
# Check for errors
./scripts/service.sh errors

# Try restarting
./scripts/service.sh restart

# If that fails, reinstall
./scripts/service.sh uninstall
./scripts/service.sh install
```

### "No videos uploading"

1. **Check service status:**
   ```bash
   ./scripts/service.sh status
   ```

2. **Verify video format:**
   ```bash
   file single-upload/your-video.mp4
   # Should show: "video/mp4" or similar
   ```

3. **Check logs:**
   ```bash
   ./scripts/service.sh logs
   ```

### "Upload failed"

Common causes:
- **YouTube quota exceeded** (wait 24 hours)
- **Video too large** (YouTube max: 256GB)
- **Invalid credentials** (regenerate token)
- **Network issues** (check connection)

Fix:
```bash
# Check errors
./scripts/service.sh errors

# Restart service
./scripts/service.sh restart
```

### "AI title generation failed"

The uploader will fall back to basic titles. To fix:

1. **Check OpenAI API key:**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. **Verify API key is valid:**
   ```bash
   python -c "from openai import OpenAI; OpenAI().models.list()"
   ```

3. **Check quota:**
   Visit: https://platform.openai.com/usage

---

## File Locations

```
scrapper_sora2/
├── single-upload/               # Drop videos here
│   ├── your-video.mp4          # Ready to upload
│   ├── .upload_state.json      # Upload history
│   ├── upload_scheduler.log    # Main log file
│   └── uploaded/               # Uploaded videos moved here
│       └── completed-video.mp4
│
├── scripts/
│   ├── service.sh              # Service manager (USE THIS!)
│   └── start_uploader.sh       # Startup script
│
├── youtube_credentials.json    # YouTube API creds
├── youtube_token.json          # OAuth token
└── .env                        # OpenAI API key
```

---

## Advanced Configuration

### Change Privacy Setting

Edit `scripts/start_uploader.sh`:

```bash
    --privacy public \    # ← Change to: unlisted, private
```

### Disable AI Titles (Faster)

Edit `scripts/start_uploader.sh`:

```bash
    --log "$LOG_FILE" \
    --no-vision          # ← Add this line
```

### Custom Log Location

Edit `scripts/start_uploader.sh`:

```bash
LOG_FILE="$PROJECT_DIR/my-custom-logs/upload.log"  # ← Change this
```

---

## System Requirements

### Required
- macOS (LaunchAgent support)
- Python 3.8+
- YouTube API credentials
- OpenAI API key (for AI titles)
- Internet connection

### Optional
- FFmpeg (for advanced video processing)
- GPU (for faster frame extraction)

---

## Getting Help

### Documentation
- **Full guide:** `docs/AUTOMATED_UPLOADER.md`
- **Vision titles:** `docs/VISION_TITLE_GENERATOR.md`
- **Manual upload:** `docs/YOUTUBE_UPLOADER.md`

### Logs
- **Main log:** `single-upload/upload_scheduler.log`
- **System log:** `single-upload/uploader_stdout.log`
- **Error log:** `single-upload/uploader_stderr.log`

### Common Commands
```bash
# See all service commands
./scripts/service.sh help

# Check status
./scripts/service.sh status

# Watch logs
./scripts/service.sh logs

# View errors
./scripts/service.sh errors
```

---

## Tips & Best Practices

### 🎯 Optimize Upload Success
1. **Name videos clearly** - Helps with organization
2. **Use consistent formats** - Stick to MP4 when possible
3. **Monitor quota** - YouTube has daily upload limits
4. **Check logs regularly** - Catch issues early

### ⚡ Speed Up Processing
1. **Disable vision** - Use `--no-vision` for faster uploads
2. **Reduce interval** - Upload more frequently (4-6 hours)
3. **Pre-process videos** - Ensure optimal encoding

### 📊 Track Performance
1. **Monitor upload history** - Check `.upload_state.json`
2. **Review logs** - Identify patterns and issues
3. **Check YouTube Analytics** - Track video performance

---

## What's Next?

✅ Service is running  
✅ Videos are uploading  
✅ Everything is automated  

### Now you can:

1. **Add more videos** to `single-upload/`
2. **Monitor progress** with `./scripts/service.sh status`
3. **Check YouTube** for your published videos
4. **Relax** - The system handles everything!

### Optional Enhancements:

- **Customize titles** - Edit `src/utils/vision_title_generator.py`
- **Add thumbnails** - Generate custom thumbnails
- **Schedule posts** - Use unlisted + manual publish
- **Track analytics** - Monitor performance metrics

---

## Support

For issues or questions:
1. Check `./scripts/service.sh status`
2. Review logs: `./scripts/service.sh logs`
3. Read docs: `docs/AUTOMATED_UPLOADER.md`
4. Check errors: `./scripts/service.sh errors`

**Happy uploading! 🚀📹**
