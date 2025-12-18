# 🔐 Fix: macOS Permission Denied Error

## Problem
The LaunchAgent service can't access the Desktop folder due to macOS security restrictions.

Error: `Operation not permitted` when accessing `/Users/ethan/Desktop/scrapper_sora2`

## Solution: Grant Full Disk Access

### Step 1: Open System Settings

1. Click Apple menu (top-left)
2. Go to **System Settings** (or **System Preferences** on older macOS)
3. Click **Privacy & Security**
4. Scroll down and click **Full Disk Access**

### Step 2: Add Terminal/LaunchAgent Access

#### Option A: Add `launchd` (Recommended)
1. Click the **+** button
2. Press `Cmd + Shift + G` to open "Go to folder"
3. Type: `/sbin/launchd`
4. Click **Go**, then **Open**
5. Enable the toggle for `launchd`

#### Option B: Add `bash` (Alternative)
1. Click the **+** button
2. Press `Cmd + Shift + G`
3. Type: `/bin/bash`
4. Click **Go**, then **Open**
5. Enable the toggle for `bash`

### Step 3: Restart the Service

```bash
cd /Users/ethan/Desktop/scrapper_sora2

# Restart the service
./scripts/service.sh restart

# Check status
./scripts/service.sh status

# Watch logs (should work now)
./scripts/service.sh logs
```

---

## Alternative: Move Project Out of Desktop (Easier)

macOS has stricter permissions for Desktop and Documents folders. Moving the project elsewhere avoids permission issues entirely.

### Step 1: Move Project

```bash
# Move to home directory
mv /Users/ethan/Desktop/scrapper_sora2 ~/scrapper_sora2

# Or move to Applications
mv /Users/ethan/Desktop/scrapper_sora2 /Applications/scrapper_sora2
```

### Step 2: Update LaunchAgent

```bash
cd ~/scrapper_sora2  # or wherever you moved it

# Uninstall old service
./scripts/service.sh uninstall

# The plist file automatically uses the correct path
# based on where start_uploader.sh is located

# Reinstall service
./scripts/service.sh install

# Check status
./scripts/service.sh status
```

The service will now work without needing Full Disk Access!

---

## Temporary Solution: Run Manually (For Testing)

If you don't want to use the LaunchAgent, you can run it manually:

```bash
cd /Users/ethan/Desktop/scrapper_sora2

# Run in foreground (see output live)
python src/utils/auto_uploader.py

# Run in background (using nohup)
nohup python src/utils/auto_uploader.py > single-upload/manual.log 2>&1 &

# Check if it's running
ps aux | grep auto_uploader
```

This will work because you're running it as your user, not through LaunchAgent.

---

## Verify It's Working

After applying any solution:

```bash
# Check service status
./scripts/service.sh status

# Watch logs (should show activity now)
./scripts/service.sh logs

# Check for new errors
./scripts/service.sh errors
```

You should see:
```
✅ Service is RUNNING
📹 Videos in queue: 3
⏰ Next upload: [timestamp]
```

And logs should show the uploader starting up.

---

## Recommended Approach

**Best option:** Move the project out of Desktop to `~/scrapper_sora2` or `/Applications/scrapper_sora2`

This avoids all permission issues and the LaunchAgent will work perfectly!

```bash
# Quick fix (5 seconds)
cd /Users/ethan/Desktop
mv scrapper_sora2 ~/
cd ~/scrapper_sora2
./scripts/service.sh uninstall
./scripts/service.sh install
./scripts/service.sh status
```

Done! 🎉
