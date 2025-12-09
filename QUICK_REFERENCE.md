# 🚀 Quick Reference - Sora Scraper v2.3

A one-page reference for the most common commands and workflows.

---

## 🎯 Common Commands

### Test Navigation (Always test first!)

```bash
./test_navigation.sh "https://sora.chatgpt.com/video/YOUR_VIDEO_ID"
```

### Scrape Remix Chain (Metadata Only)

```bash
python scraper_sora_advanced.py \
  --mode remix \
  --video-url "https://sora.chatgpt.com/video/YOUR_VIDEO_ID" \
  --use-existing-chrome \
  --slow \
  --metadata-mode
```

### Scrape Profile (Download Videos)

```bash
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 20 \
  --use-existing-chrome \
  --slow
```

### Interactive Mode (Beginner-Friendly)

```bash
./start.sh
```

### Remove Watermarks (After Scraping)

```bash
# Single video
./quick_remove.sh 1

# All videos in folder
./quick_remove.sh videos/
```

---

## 🛡️ Anti-Detection Best Practices

### ✅ DO:
- Use `--slow` mode for large scraping jobs
- Use `--use-existing-chrome` to maintain session
- Add `--delay 5` for extra caution
- Take breaks between batch operations
- Test with small numbers first (`--num-videos 5`)

### ❌ DON'T:
- Scrape too fast (avoid default delays)
- Use `--headless` mode (easier to detect)
- Scrape hundreds of videos in one session
- Ignore rate limiting or errors

---

## 🔧 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| **Stale element errors** | ✅ Fixed in v2.3! Update to latest version |
| **Back-and-forth navigation** | ✅ Fixed in v2.3! Use strictly forward navigation |
| **403 Forbidden** | Use `--use-existing-chrome --slow` |
| **Login required** | Run `./launch_chrome.sh` and log in manually |
| **No remixes found** | Verify video has remixes, check page manually |
| **"Load more" not working** | ✅ Fixed in v2.3! Re-fetches buttons correctly |
| **Chrome won't connect** | Check if port 9222 is free: `lsof -ti:9222` |

---

## 📊 Recommended Workflows

### Workflow 1: Quick Test

```bash
# 1. Test navigation
./test_navigation.sh "YOUR_VIDEO_URL"

# 2. Scrape 5 videos (metadata only)
python scraper_sora_advanced.py \
  --mode remix \
  --video-url "YOUR_VIDEO_URL" \
  --max-depth 2 \
  --metadata-mode \
  --slow
```

### Workflow 2: Production Scraping

```bash
# 1. Start Chrome with debugging
./launch_chrome.sh

# 2. Log in to Sora manually

# 3. Scrape with maximum safety
python scraper_sora_advanced.py \
  --mode remix \
  --video-url "YOUR_VIDEO_URL" \
  --use-existing-chrome \
  --slow \
  --metadata-mode

# 4. Review metadata
cat metadata.json | jq '.'
```

### Workflow 3: Complete Extraction + Watermark Removal

```bash
# 1. Scrape videos
python scraper_sora_advanced.py \
  --mode profile \
  --profile-url "https://sora.chatgpt.com/user/USERNAME" \
  --num-videos 10 \
  --use-existing-chrome \
  --slow

# 2. Remove watermarks from all videos
./quick_remove.sh videos/

# 3. Check results
open videos_cleaned/
```

---

## 🎓 Command Flags Cheat Sheet

### Essential Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--mode remix` | Follow remix chain | Required for remix mode |
| `--video-url URL` | Starting video | Required for remix mode |
| `--use-existing-chrome` | Connect to existing Chrome | Recommended |
| `--slow` | Enable anti-detection delays | Recommended for large jobs |
| `--metadata-mode` | Extract metadata only | Faster, no downloads |

### Optional Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--max-depth N` | Limit remix chain depth | Unlimited |
| `--num-videos N` | Number of videos to scrape | 10 |
| `--delay N` | Delay between scrolls (seconds) | 2.0 |
| `--output-dir DIR` | Output directory | `videos/` |
| `--metadata-output FILE` | Metadata filename | `metadata.json` |
| `--metadata-per-file` | One JSON per video | Disabled |

---

## 📖 Documentation Index

### Getting Started
- [README.md](README.md) - Full documentation
- [RELEASE_NOTES_v2.3.md](RELEASE_NOTES_v2.3.md) - What's new in v2.3

### Technical Details
- [FINAL_FIX_STRICTLY_FORWARD.md](FINAL_FIX_STRICTLY_FORWARD.md) - Navigation improvements
- [STRICTLY_FORWARD_NAVIGATION_FIX.md](STRICTLY_FORWARD_NAVIGATION_FIX.md) - Technical explanation
- [ANTI_DETECTION_FIXES.md](ANTI_DETECTION_FIXES.md) - Anti-detection strategies

### Help
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues & solutions

---

## 🎯 Real-World Examples

### Example 1: Metadata Extraction

```bash
# Extract metadata from a remix chain
python scraper_sora_advanced.py \
  --mode remix \
  --video-url "https://sora.chatgpt.com/video/abc123" \
  --use-existing-chrome \
  --slow \
  --metadata-mode \
  --metadata-output viral_trend.json

# Result: viral_trend.json with all remix metadata
```

### Example 2: Build Video Database

```bash
# Scrape multiple profiles
for username in user1 user2 user3; do
  python scraper_sora_advanced.py \
    --mode profile \
    --profile-url "https://sora.chatgpt.com/user/$username" \
    --all \
    --metadata-mode \
    --metadata-output "${username}_data.json" \
    --use-existing-chrome \
    --slow
  
  echo "✅ Completed $username"
  sleep 60  # Break between profiles
done
```

### Example 3: Archive and Clean

```bash
# 1. Download videos from a trend
python scraper_sora_advanced.py \
  --mode remix \
  --video-url "https://sora.chatgpt.com/video/trending" \
  --use-existing-chrome \
  --slow \
  --output-dir trend_archive

# 2. Remove all watermarks
./quick_remove.sh trend_archive/

# 3. Result: Clean videos in trend_archive_cleaned/
```

---

## 💡 Pro Tips

1. **Always test first:** Use `test_navigation.sh` before scraping
2. **Use existing Chrome:** Faster and maintains login session
3. **Enable slow mode:** Especially for large jobs or download mode
4. **Metadata first:** Extract metadata, then decide what to download
5. **Batch watermark removal:** Process all videos at once with `./quick_remove.sh videos/`
6. **Monitor logs:** Watch for errors or unexpected behavior
7. **Take breaks:** Don't scrape continuously for hours
8. **Backup metadata:** Save JSON files regularly

---

## 🚨 When to Use Each Mode

### Home Mode
- **Use when:** Exploring trending content
- **Best for:** Discovery and quick tests
- **Command:** `--mode home --num-videos 20`

### Profile Mode
- **Use when:** Archiving a specific creator's content
- **Best for:** Complete profile extraction
- **Command:** `--mode profile --profile-url "URL" --all`

### Remix Mode
- **Use when:** Following viral trends or remix chains
- **Best for:** Trend analysis and complete chain capture
- **Command:** `--mode remix --video-url "URL"`

---

## 📞 Need Help?

1. **Read the docs:** Check [README.md](README.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Test your setup:** Run `./test_navigation.sh` with a known video
3. **Check logs:** Look for error messages in terminal output
4. **Try slow mode:** Add `--slow` flag if having issues
5. **Review this guide:** Most common solutions are here

---

**Remember: v2.3 has fixed all major navigation issues! If you encounter problems, make sure you're using the latest version.** 🚀
