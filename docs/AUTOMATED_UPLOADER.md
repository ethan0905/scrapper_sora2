# 🤖 Automated YouTube Upload Scheduler

## Overview

The automated uploader runs in the background and **automatically uploads 1 video every 8 hours** from the `single-upload` folder. No manual intervention needed!

### Features

- ⏰ **Scheduled uploads** - Uploads every 8 hours automatically
- 🎥 **Vision AI titles** - Generates engaging titles by analyzing video
- 📝 **Auto-descriptions** - Creates SEO-optimized descriptions
- 📊 **State tracking** - Never uploads the same video twice
- 📁 **Auto-organization** - Moves uploaded videos to `uploaded/` folder
- 🔄 **Self-recovering** - Continues running even after errors
- 📋 **Detailed logging** - Track all uploads and errors

## Quick Start

### 1. Create the Upload Folder

```bash
mkdir -p single-upload
```

### 2. Add Videos

Simply drop videos into the `single-upload` folder:

```bash
cp your-video.mp4 single-upload/
```

### 3. Start the Uploader

#### Option A: Run Manually (Testing)

```bash
python src/utils/auto_uploader.py
```

#### Option B: Run as Background Service (Production)

See [Installation](#installation) section below.

## Installation (Auto-Start on macOS)

### Step 1: Install the LaunchAgent

```bash
# Copy the plist file to LaunchAgents
cp scripts/com.sora.youtube.uploader.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.sora.youtube.uploader.plist
```

### Step 2: Start the Service

```bash
launchctl start com.sora.youtube.uploader
```

### Step 3: Verify It's Running

```bash
# Check if service is loaded
launchctl list | grep sora

# View logs
tail -f single-upload/upload_scheduler.log
```

**That's it!** The uploader is now running in the background and will automatically start when you restart your Mac.

## How It Works

### Workflow

```
1. Monitor single-upload folder
   ↓
2. Every 8 hours, check for videos
   ↓
3. Pick next video (alphabetically)
   ↓
4. Extract video frames
   ↓
5. Generate title with GPT-4o vision
   ↓
6. Generate description
   ↓
7. Upload to YouTube
   ↓
8. Move to uploaded/ folder
   ↓
9. Wait 8 hours and repeat
```

### File Structure

```
single-upload/
├── video1.mp4              # Waiting to upload
├── video2.mp4              # Waiting to upload
├── .upload_state.json      # Tracks upload schedule
├── upload_scheduler.log    # Main log file
├── uploader_stdout.log     # Standard output
├── uploader_stderr.log     # Error output
└── uploaded/               # Uploaded videos moved here
    ├── video0.mp4
    └── video0_metadata.json
```

## Configuration

### Change Upload Interval

Edit the service:

```bash
# Option 1: Edit plist file
nano ~/Library/LaunchAgents/com.sora.youtube.uploader.plist

# Option 2: Run manually with custom interval
python src/utils/auto_uploader.py --interval 12  # 12 hours
```

### Change Privacy Setting

```bash
# Public (default)
python src/utils/auto_uploader.py --privacy public

# Unlisted
python src/utils/auto_uploader.py --privacy unlisted

# Private
python src/utils/auto_uploader.py --privacy private
```

### Disable Vision Titles

Save money by using basic titles:

```bash
python src/utils/auto_uploader.py --no-vision
```

## Managing the Service

### Check Status

```bash
# Is it running?
launchctl list | grep sora

# View live logs
tail -f single-upload/upload_scheduler.log
```

### Stop the Service

```bash
launchctl stop com.sora.youtube.uploader
```

### Restart the Service

```bash
launchctl kickstart -k gui/$(id -u)/com.sora.youtube.uploader
```

### Uninstall the Service

```bash
# Stop and unload
launchctl unload ~/Library/LaunchAgents/com.sora.youtube.uploader.plist

# Remove plist file
rm ~/Library/LaunchAgents/com.sora.youtube.uploader.plist
```

## Monitoring

### View Logs

```bash
# Main scheduler log
tail -f single-upload/upload_scheduler.log

# Standard output
tail -f single-upload/uploader_stdout.log

# Errors
tail -f single-upload/uploader_stderr.log
```

### Check Upload State

```bash
# View current state
cat single-upload/.upload_state.json | jq '.'
```

### Example Log Output

```
2025-12-17 14:00:00 - INFO - 🚀 Automated uploader initialized
2025-12-17 14:00:00 - INFO - 📁 Source folder: single-upload
2025-12-17 14:00:00 - INFO - ⏰ Upload interval: 8 hours
2025-12-17 14:00:00 - INFO - 🎬 Vision titles: Enabled
2025-12-17 14:00:00 - INFO - ✅ Vision title generator initialized
2025-12-17 14:00:05 - INFO - 
============================================================
2025-12-17 14:00:05 - INFO - ⏰ Upload time! 2025-12-17 14:00:05
2025-12-17 14:00:05 - INFO - ============================================================
2025-12-17 14:00:05 - INFO - 📤 Preparing to upload: video1.mp4
2025-12-17 14:00:05 - INFO - 🎥 Analyzing video with AI vision...
2025-12-17 14:00:10 - INFO - ✅ Generated title: Gorilla Breaks Through Glass Wall 🦍 #SoraAI
2025-12-17 14:00:10 - INFO - ⬆️  Uploading to YouTube...
2025-12-17 14:00:10 - INFO -    Title: Gorilla Breaks Through Glass Wall 🦍 #SoraAI
2025-12-17 14:00:10 - INFO -    Privacy: public
2025-12-17 14:00:45 - INFO - ✅ Upload successful!
2025-12-17 14:00:45 - INFO -    Video ID: dQw4w9WgXcQ
2025-12-17 14:00:45 - INFO -    URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
2025-12-17 14:00:45 - INFO - 📦 Moved to: single-upload/uploaded/video1.mp4
2025-12-17 14:00:45 - INFO - ✅ Upload complete!
2025-12-17 14:00:45 - INFO - ⏰ Next upload: 2025-12-17 22:00:45
2025-12-17 14:05:45 - INFO - ⏳ Waiting for next upload...
2025-12-17 14:05:45 - INFO -    Time remaining: 7.9 hours
```

## Advanced Usage

### Custom Upload Schedule

Edit `src/utils/auto_uploader.py` to customize the upload logic:

```python
def _should_upload_now(self) -> bool:
    """Customize when to upload."""
    # Example: Only upload between 9 AM and 5 PM
    current_hour = datetime.now().hour
    if current_hour < 9 or current_hour > 17:
        return False
    
    # ... rest of logic
```

### Priority Queue

Rename files to control upload order:

```bash
# These will upload in this order:
single-upload/
├── 001_important.mp4   # Uploads first
├── 002_next.mp4        # Uploads second
└── 003_later.mp4       # Uploads third
```

### Notification on Upload

Add webhook or email notification:

```python
def _upload_video(self, video_path: Path) -> bool:
    # ... upload code ...
    
    if success:
        # Send notification
        self._send_notification(f"Uploaded: {title}")
```

## Troubleshooting

### Service Won't Start

```bash
# Check for errors
tail -50 single-upload/uploader_stderr.log

# Verify plist is valid
plutil -lint ~/Library/LaunchAgents/com.sora.youtube.uploader.plist

# Check permissions
ls -la scripts/start_uploader.sh
```

### No Videos Uploading

```bash
# Check if videos are in folder
ls -la single-upload/

# Check state file
cat single-upload/.upload_state.json

# Verify it's not waiting
tail single-upload/upload_scheduler.log
```

### Upload Fails

```bash
# Check YouTube credentials
ls -la youtube_credentials.json
ls -la youtube_token.json

# Check OpenAI API key
grep OPENAI_API_KEY .env

# View detailed error
grep ERROR single-upload/upload_scheduler.log
```

### Service Keeps Crashing

```bash
# View crash log
tail -100 single-upload/uploader_stderr.log

# Run manually to see errors
python src/utils/auto_uploader.py

# Check system logs
log show --predicate 'subsystem == "com.sora.youtube.uploader"' --last 1h
```

## Cost Considerations

### Vision Title Generation

- **Cost:** ~$0.002 per video (4 frames)
- **Per day (3 uploads):** ~$0.006
- **Per month (90 uploads):** ~$0.18

### No Vision (Free)

```bash
python src/utils/auto_uploader.py --no-vision
```

Uses basic titles from metadata - completely free!

## Safety Features

### What Happens If...

**Computer restarts?**
- ✅ Service auto-starts on boot
- ✅ Resumes from last upload time

**Upload fails?**
- ✅ Retries on next cycle
- ✅ Logs error for debugging
- ✅ Continues with next video

**No videos in folder?**
- ✅ Waits patiently
- ✅ Checks again every hour
- ✅ Uploads when videos added

**API rate limit?**
- ✅ Logs the error
- ✅ Waits for next cycle
- ✅ Automatically retries

## Tips & Best Practices

### 1. Prepare Videos in Advance

```bash
# Add multiple videos at once
cp videos/batch/*.mp4 single-upload/

# They'll upload one every 8 hours automatically
```

### 2. Monitor First Few Uploads

```bash
# Watch logs for first 24 hours
tail -f single-upload/upload_scheduler.log
```

### 3. Backup Your Uploads

```bash
# The uploaded/ folder keeps your videos
# Backup periodically
rsync -av single-upload/uploaded/ ~/Backups/youtube-uploads/
```

### 4. Test Before Production

```bash
# Test with short interval first
python src/utils/auto_uploader.py --interval 1  # 1 hour

# Then switch to production
launchctl load ~/Library/LaunchAgents/com.sora.youtube.uploader.plist
```

### 5. Use Consistent Naming

```bash
# Good naming pattern
single-upload/
├── 2025-12-17_video1.mp4
├── 2025-12-17_video2.mp4
└── 2025-12-18_video1.mp4

# Makes tracking easier in logs
```

## Complete Workflow Example

```bash
# 1. Setup (one-time)
mkdir -p single-upload
cp scripts/com.sora.youtube.uploader.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.sora.youtube.uploader.plist

# 2. Add videos whenever you want
python main.py --batch urls.txt --max 10 --output single-upload

# 3. Monitor (optional)
tail -f single-upload/upload_scheduler.log

# 4. Sit back and relax! 🎉
# Videos upload automatically every 8 hours
```

## FAQ

**Q: Can I change the upload interval?**

A: Yes! Edit the plist file or run manually with `--interval X`.

**Q: Will it upload while I'm asleep?**

A: Yes! That's the point. Set it and forget it.

**Q: What if I want to pause uploads?**

A: Just stop the service: `launchctl stop com.sora.youtube.uploader`

**Q: Can I upload multiple videos at once?**

A: No, it uploads one video per interval. This prevents spam and rate limits.

**Q: What happens to old videos?**

A: They're moved to `single-upload/uploaded/` folder automatically.

**Q: Can I run multiple uploaders?**

A: Yes! Create different folders and services for different channels.

---

**You now have a fully automated YouTube upload system!** 🚀

Just drop videos in `single-upload/` and they'll upload automatically. Set it once, let it run forever!
