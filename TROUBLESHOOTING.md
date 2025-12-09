# 🚨 Quick Troubleshooting Guide

## Common Issues & Solutions

### Issue: Scraper navigates to login page

**Symptoms:**
- Browser shows login/signin page
- Console shows "Navigation inattendue"
- Scraper stops after 3 errors

**Solutions:**
1. ✅ Check if you're logged in to Sora
2. ✅ Verify the video URL is correct and accessible
3. ✅ Try manually navigating to the video first
4. ✅ Check if Sora's UI has changed (inspect button selectors)

**Code to check:**
```python
# In scraper_sora_advanced.py line ~690
if "login" in current.lower() or "auth" in current.lower():
    # This should NOT trigger if you're logged in
```

---

### Issue: No remix buttons found

**Symptoms:**
- Console shows "Aucun bouton de remix trouvé"
- Zero remixes found
- Scraper completes quickly

**Solutions:**
1. ✅ Verify video actually has remixes
2. ✅ Scroll manually to remix section
3. ✅ Check button selectors with DevTools
4. ✅ Run `INSTRUCTIONS_DEBUG.md` steps

**Code to check:**
```python
# In scraper_sora_advanced.py line ~735
if "h-8" in classes and "w-6" in classes and "shrink-0" in classes:
    # These classes must match current Sora UI
```

---

### Issue: Scraper clicks wrong buttons

**Symptoms:**
- Navigates to unexpected pages
- Clicks share/menu buttons
- Opens modals/dialogs

**Solutions:**
1. ✅ Add more skip keywords
2. ✅ Inspect button aria-labels
3. ✅ Check button filtering logic

**Code to update:**
```python
# In scraper_sora_advanced.py line ~742
skip_keywords = ["close", "login", "sign", "share", "like", "follow", "menu"]
# Add more keywords here if needed
```

---

### Issue: "Load more" doesn't work

**Symptoms:**
- Finds first 10 remixes only
- Never clicks "Load more"
- Console shows "Load more button introuvable"

**Solutions:**
1. ✅ Manually click "Load more" to see if it exists
2. ✅ Check button classes in DevTools
3. ✅ Verify selector matches current UI

**Code to check:**
```python
# In scraper_sora_advanced.py line ~752
elif "h-[21px]" in classes or ("w-4" in classes...):
    # This selector must match "Load more" button
```

---

### Issue: Scraper gets stuck in loop

**Symptoms:**
- Keeps clicking same buttons
- Never advances to new remixes
- Runs for very long time

**Solutions:**
1. ✅ Check `processed_button_count` logic
2. ✅ Verify `seen_urls` is tracking properly
3. ✅ Stop scraper and check browser state

**Code to check:**
```python
# In scraper_sora_advanced.py line ~775
buttons_to_process = remix_buttons[processed_button_count:]
# Must skip already processed buttons
```

---

### Issue: Chrome won't connect

**Symptoms:**
- "No Chrome with remote debugging found"
- Can't use --existing flag
- Connection refused errors

**Solutions:**
1. ✅ Start Chrome with debugging:
   ```bash
   open -a 'Google Chrome' --args --remote-debugging-port=9222
   ```
2. ✅ Check Chrome is running:
   ```bash
   ps aux | grep "remote-debugging-port=9222"
   ```
3. ✅ Try different port (9223, 9224, etc.)

---

### Issue: Selenium errors

**Symptoms:**
- "stale element reference"
- "element not interactable"
- "element not found"

**Solutions:**
1. ✅ Increase wait times (already in code)
2. ✅ Re-find elements after page changes
3. ✅ Use JavaScript click instead of regular click

**Already implemented:**
```python
# JavaScript click is used (more reliable)
self.driver.execute_script("arguments[0].click();", button)
```

---

## 🔍 Debug Commands

### Check Chrome Process
```bash
ps aux | grep -i "chrome.*remote-debugging-port=9222"
```

### View Current Selectors
```bash
# In browser console (F12):
document.querySelectorAll('button.h-8.w-6.shrink-0')  // Remix buttons
document.querySelectorAll('button.h-\\[21px\\].w-4')   // Load more
```

### Test URL Validation
```python
# In Python:
url = "https://sora.com/p/login"
is_valid = not any(kw in url.lower() for kw in ["login", "auth", "signin"])
print(f"Valid: {is_valid}")  # Should be False
```

### Check Button Count
```python
# Add after line ~771 in scraper_sora_advanced.py:
print(f"DEBUG: remix_buttons={len(remix_buttons)}, processed={processed_button_count}")
```

---

## 📞 Quick Help

1. **Read SAFETY_IMPROVEMENTS.md** - Understand what was fixed
2. **Read FINAL_STATUS.md** - See complete status
3. **Run validate_safety.sh** - Test safety features
4. **Check INSTRUCTIONS_DEBUG.md** - Manual selector inspection

---

## 🎯 Quick Test Checklist

Before reporting an issue, verify:

- [ ] Chrome is running with remote debugging (port 9222)
- [ ] You're logged in to Sora in that Chrome instance
- [ ] Video URL is correct and accessible
- [ ] Video actually has remixes
- [ ] You've scrolled to the remix section manually
- [ ] Button selectors match current Sora UI
- [ ] No other scripts are controlling the browser

---

## 🔧 Emergency Reset

If scraper is completely broken:

```bash
# 1. Close all Chrome instances
killall "Google Chrome"

# 2. Restart Chrome with debugging
open -a 'Google Chrome' --args --remote-debugging-port=9222

# 3. Manually navigate to video page

# 4. Test with fresh run
./validate_safety.sh "your-video-url"
```

---

## 📝 Getting More Help

Add debug logging:
```python
# Add to scraper_sora_advanced.py after line ~680:
import logging
logging.basicConfig(level=logging.DEBUG)
```

Capture screenshots:
```python
# Add when navigation error occurs:
self.driver.save_screenshot("/tmp/nav_error.png")
```

Export HTML:
```python
# Add to see current page structure:
with open("/tmp/page.html", "w") as f:
    f.write(self.driver.page_source)
```
