# 🛡️ Auto-Stop Safety Feature

## Overview

The automated uploader now includes a **safety mechanism** that automatically stops after **10 consecutive failed upload attempts**. This prevents the service from running indefinitely when there's a persistent issue.

---

## How It Works

### Failure Tracking

The uploader tracks every upload attempt:

- ✅ **Success** → Resets failure counter to 0
- ❌ **Failure** → Increments failure counter by 1

### Auto-Stop Threshold

After **10 consecutive failures**, the service will:

1. Log a critical error message
2. Show the last error
3. Provide instructions to fix and restart
4. **Exit with error code** (stops the service)

---

## What Triggers a Failure?

Common failure scenarios:

- YouTube API quota exceeded
- Invalid/expired credentials
- Network connection issues
- Video file corrupted or invalid format
- YouTube API errors (503, 500, etc.)
- Permission issues accessing files

---

## Monitoring Failures

### Check Current Status

```bash
./scripts/service.sh status
```

**Output shows failure count:**

```
✅ Videos uploaded: 12
⏰ Last upload: 2024-12-17T14:30:00
⚠️  Consecutive failures: 3
```

### Warning Levels

- **0-6 failures** → Normal operation
- **7-9 failures** → ⚠️ Warning displayed in status
- **10+ failures** → 🛑 Service stops automatically

---

## When Service Stops

### What You'll See in Logs

```
🛑 CRITICAL: Too many consecutive failures!
════════════════════════════════════════
   Failed attempts: 10
   Last error: YouTube API quota exceeded
   Stopping uploader for safety.

   To restart:
   1. Fix the issue
   2. Reset failures: rm single-upload/.upload_state.json
   3. Restart service: ./scripts/service.sh restart
════════════════════════════════════════
```

### Status Check Shows

```bash
$ ./scripts/service.sh status

🛑 CRITICAL: Service stopped due to too many failures!
   Consecutive failures: 10/10
   Last error: YouTube API quota exceeded

To fix:
   1. Check logs: ./scripts/service.sh errors
   2. Fix the issue (check YouTube quota, credentials, etc.)
   3. Reset failures: ./scripts/service.sh reset-failures
   4. Restart service: ./scripts/service.sh restart
```

---

## How to Fix and Restart

### Step 1: Check Errors

```bash
./scripts/service.sh errors
```

This shows the actual error messages to help diagnose the issue.

### Step 2: Fix the Problem

Common fixes:

**YouTube Quota Exceeded:**
- Wait 24 hours for quota to reset
- Or request quota increase from Google

**Invalid Credentials:**
```bash
rm youtube_token.json
# Re-authenticate when you run next upload
```

**Network Issues:**
- Check internet connection
- Verify firewall settings
- Test: `curl -I https://www.youtube.com`

**OpenAI API Issues:**
```bash
# Check API key
cat .env | grep OPENAI_API_KEY

# Test API key
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### Step 3: Reset Failure Counter

```bash
./scripts/service.sh reset-failures
```

This will prompt for confirmation and reset the counter to 0.

**Alternative (manual):**
```bash
# Backup state
cp single-upload/.upload_state.json single-upload/.upload_state.json.backup

# Reset manually
python3 << EOF
import json
with open('single-upload/.upload_state.json', 'r') as f:
    state = json.load(f)
state['consecutive_failures'] = 0
state['last_error'] = None
with open('single-upload/.upload_state.json', 'w') as f:
    json.dump(state, f, indent=2)
EOF
```

### Step 4: Restart Service

```bash
./scripts/service.sh restart
```

The service will now run normally with the failure counter reset to 0.

---

## Configuration

### Change Failure Threshold

Edit `scripts/start_uploader.sh`:

```bash
$PYTHON "$UPLOAD_SCRIPT" \
    --folder "single-upload" \
    --interval 8 \
    --privacy public \
    --max-failures 15 \    # ← Change from default 10
    --log "$LOG_FILE"
```

Then restart:
```bash
./scripts/service.sh restart
```

**Recommended values:**
- `10` - Default (stops after 10 failures)
- `5` - Strict (stops quickly if issues)
- `20` - Lenient (more retries before stopping)
- `999` - Effectively unlimited (not recommended)

### Run Manually Without Limit

```bash
# For testing - no auto-stop
python src/utils/auto_uploader.py --max-failures 999
```

---

## State File Format

The `.upload_state.json` file tracks everything:

```json
{
  "last_upload_time": "2024-12-17T14:30:00",
  "uploaded_videos": [
    "/Users/ethan/Desktop/scrapper_sora2/single-upload/video1.mp4",
    "/Users/ethan/Desktop/scrapper_sora2/single-upload/video2.mp4"
  ],
  "queue": [],
  "consecutive_failures": 3,
  "last_error": "YouTube API quota exceeded"
}
```

**Fields:**
- `consecutive_failures` - Current failure count
- `last_error` - Most recent error message
- Reset to 0 on successful upload

---

## Best Practices

### Monitor Regularly

```bash
# Quick status check
./scripts/service.sh status

# Watch for issues
tail -f single-upload/upload_scheduler.log | grep -E "(ERROR|WARN|CRITICAL)"
```

### Set Up Alerts (Advanced)

Create a cron job to alert you:

```bash
# Check every hour for failures
0 * * * * /Users/ethan/Desktop/scrapper_sora2/scripts/check_failures.sh
```

**`scripts/check_failures.sh`:**
```bash
#!/bin/bash
FAILURES=$(grep -o '"consecutive_failures": [0-9]*' single-upload/.upload_state.json | grep -o '[0-9]*$')
if [ "$FAILURES" -ge 7 ]; then
    # Send notification (macOS)
    osascript -e "display notification \"Upload failures: $FAILURES\" with title \"YouTube Uploader Warning\""
fi
```

### Preventive Measures

1. **Check quota regularly** - Visit https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
2. **Monitor credentials** - Ensure YouTube token doesn't expire
3. **Test videos first** - Upload a test video manually before batch
4. **Keep logs** - Archive logs periodically for troubleshooting

---

## Troubleshooting

### "Service stopped but I didn't see any errors"

Check all log files:
```bash
# Main log
cat single-upload/upload_scheduler.log

# System errors
cat single-upload/uploader_stderr.log

# System output
cat single-upload/uploader_stdout.log
```

### "Counter keeps resetting unexpectedly"

This is normal! The counter resets to 0 on **any successful upload**. If you see intermittent failures, the counter will go up and down.

### "Want to disable auto-stop"

Not recommended, but you can:
```bash
# Set very high threshold
--max-failures 9999
```

### "Service stopped but failure count is less than 10"

Check if someone manually stopped it:
```bash
launchctl list | grep sora
```

---

## Examples

### Scenario 1: Temporary Network Issue

```
Attempt 1: ❌ Network timeout (failures: 1)
Attempt 2: ❌ Network timeout (failures: 2)
Attempt 3: ✅ Success!      (failures: 0) ← Reset
Attempt 4: ✅ Success!      (failures: 0)
```

Service continues normally.

### Scenario 2: YouTube Quota Exceeded

```
Attempt 1: ❌ Quota exceeded (failures: 1)
Attempt 2: ❌ Quota exceeded (failures: 2)
...
Attempt 10: ❌ Quota exceeded (failures: 10)
🛑 Service stops
```

Fix: Wait 24 hours, reset counter, restart.

### Scenario 3: Mixed Results

```
Attempt 1: ❌ Network error  (failures: 1)
Attempt 2: ❌ Network error  (failures: 2)
Attempt 3: ✅ Success!       (failures: 0) ← Reset
Attempt 4: ❌ API error      (failures: 1)
Attempt 5: ✅ Success!       (failures: 0) ← Reset
```

Service continues because never reached 10 consecutive failures.

---

## Summary

✅ **Automatic safety mechanism** prevents runaway failures  
✅ **10 consecutive failures** → Service stops automatically  
✅ **Warning at 7 failures** → Early alert in status  
✅ **Easy reset** → One command to clear and restart  
✅ **Configurable** → Adjust threshold to your needs  
✅ **Transparent** → All failures logged and tracked  

**The service will protect itself and make issues obvious!** 🛡️

---

## Commands Reference

```bash
# Check status (shows failure count)
./scripts/service.sh status

# View errors
./scripts/service.sh errors

# Reset failure counter
./scripts/service.sh reset-failures

# Restart service
./scripts/service.sh restart

# Change threshold (edit script)
nano scripts/start_uploader.sh
# Add: --max-failures 15
```

---

**Stay safe and keep uploading! 🚀**
