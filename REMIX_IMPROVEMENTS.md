# Remix Mode Improvements - Handling 10+ Videos

## Issues Fixed

### 1. ✅ "Log in to Sora" Modal/Popup Handling
**Problem**: During scraping, Sora shows login prompts that block the page.

**Solution**: 
- Detects and closes modal/overlay windows automatically
- Looks for close buttons with `aria-label="Close"`
- Runs before trying to find remixes on each page

### 2. ✅ Better Page Load Waiting
**Problem**: Dynamic content wasn't fully loaded before trying to find remixes.

**Solution**:
- Increased wait times (3 seconds after page load)
- Added scroll to middle of page to trigger lazy loading
- Increased WebDriverWait timeout to 15 seconds

### 3. ✅ Improved Remix Detection Strategy
**Problem**: Clicking thumbnails was unreliable and slow.

**Solution**: Changed to URL extraction approach:
- **Strategy 1**: Find all `<a href="/p/...">` links in the page
- **Strategy 2**: Extract URLs from button onclick attributes
- **No clicking needed** - much faster and more reliable!

### 4. ✅ More Aggressive "Load More" Detection
**Problem**: "Load more" button wasn't always found.

**Solution**:
- Multiple detection strategies (XPath + CSS)
- Case-insensitive text matching
- Scrolls button into view before clicking
- Increased wait time after click (3 seconds)
- Default max clicks increased to 10

### 5. ✅ Better Load More Loop Logic
**Problem**: Stopped too early, didn't get all remixes.

**Solution**:
- Continues clicking "Load more" up to 10 times (configurable)
- Only stops when both:
  - No new remixes found AND
  - No "Load more" button found AND
  - At least 2 cycles completed
- Reports progress at each cycle

## How It Works Now

### Remix Detection Flow

```
1. Navigate to video page
   ↓
2. Wait for page load (15s timeout)
   ↓
3. Close any login modals
   ↓
4. Wait 3s for dynamic content
   ↓
5. Scroll to middle of page
   ↓
6. CYCLE START (up to 10 times):
   │
   ├─→ Find all <a href="/p/..."> links
   │   └─→ Add to remix list
   │
   ├─→ Find buttons with onclick="/p/..."
   │   └─→ Extract and add URLs
   │
   ├─→ Look for "Load more" button
   │   ├─→ Found? Click it, wait 3s, continue cycle
   │   └─→ Not found? Stop if 2+ cycles done
   │
   └─→ Report: X new remixes found (Y total)
```

### Expected Output

```
[Profondeur 0] 🎬 Analyse: https://sora.chatgpt.com/p/s_xxx
      🔍 Recherche des remixes...
         ✓ Remix trouvé: s_abc123...
         ✓ Remix trouvé: s_def456...
         ✓ Remix trouvé: s_ghi789...
      📊 Cycle 1: 3 nouveau(x) remix trouvé(s) (3 total)
      🔄 Clic sur 'Load more' (tentative 1/10)
         ✓ Remix trouvé: s_jkl012...
         ✓ Remix trouvé: s_mno345...
      📊 Cycle 2: 2 nouveau(x) remix trouvé(s) (5 total)
      🔄 Clic sur 'Load more' (tentative 2/10)
         ✓ Remix trouvé: s_pqr678...
         ✓ Remix trouvé: s_stu901...
         ✓ Remix trouvé: s_vwx234...
      📊 Cycle 3: 3 nouveau(x) remix trouvé(s) (8 total)
      🔄 Clic sur 'Load more' (tentative 3/10)
         ✓ Remix trouvé: s_yza567...
         ✓ Remix trouvé: s_bcd890...
      📊 Cycle 4: 2 nouveau(x) remix trouvé(s) (10 total)
      ✓ Plus de remixes à charger
   ✅ Trouvé 10 remix(s)
```

## Testing for 10+ Remixes

### Option 1: Use Test Script

```bash
source venv/bin/activate
python test_remix.py
```

Enter your video URL when prompted. The script will:
- Use depth 1 (only direct remixes)
- Click "Load more" up to 10 times
- Should find 10+ remixes if they exist

### Option 2: Manual Command

```bash
python scraper_sora_advanced.py \
  --mode remix \
  --video-url "https://sora.chatgpt.com/p/s_6932520ddd548191b4ddede8695d361a" \
  --max-depth 1 \
  --metadata-mode \
  --use-existing-chrome \
  --slow
```

### Option 3: Interactive Mode

```bash
python interactive_scraper.py
```

1. Choose "3. Remix Chain"
2. Enter video URL
3. Choose "n" for unlimited depth (or limit to 1-2 for testing)
4. Select metadata mode
5. Enable slow mode
6. Use existing Chrome

## Configuration Options

### In Code
Edit `_find_remix_links()` parameters:

```python
# In scraper_sora_advanced.py, line ~630
def _find_remix_links(self, max_load_more_clicks=10):
    # Change max_load_more_clicks to control how many times
    # the "Load more" button is clicked
```

### Command Line
```bash
# Limit depth to control how deep to follow remix chains
--max-depth 1      # Only direct remixes (recommended for testing)
--max-depth 2      # Direct remixes + their remixes
--max-depth 3      # 3 levels deep
# (no flag)        # Unlimited depth (follows entire chain)
```

## Troubleshooting

### If still getting < 10 remixes:

1. **Check if video actually has 10+ remixes**
   - Look at the page manually
   - Count how many times "Load more" appears
   - Some videos may have fewer remixes

2. **Increase wait times**
   - Edit line ~590: `time.sleep(3)` → `time.sleep(5)`
   - Edit line ~720: `time.sleep(3)` → `time.sleep(5)`

3. **Check page_backup.html**
   - After running, check this file
   - Search for "Load" or "more" to see if button exists
   - Look at the HTML structure of remix section

4. **Try without headless mode**
   - Remove `--headless` flag to see what's happening
   - Watch the browser to see if modals are blocking

5. **Increase max_load_more_clicks**
   - Edit `_find_remix_links(self, max_load_more_clicks=10)`
   - Change 10 to 15 or 20

### If getting "Log in to Sora" errors:

1. **Make sure you're logged in**
   - Use `--use-existing-chrome` flag
   - Run `./launch_chrome.sh` first
   - Log in to Sora manually
   - Then run the scraper

2. **Check modal closing**
   - The scraper tries to close modals automatically
   - If it fails, you may need to adjust the selector
   - Look for the close button's HTML in page_backup.html

## Expected Results for Test

With a popular video that has many remixes:
- ✅ Should find **10-20+ remixes** (depends on video)
- ✅ Should take **5-10 minutes** (with slow mode)
- ✅ Each remix downloaded to `videos/` folder
- ✅ All metadata in `metadata.json`
- ✅ Each video named `video_001_xxx.mp4`, `video_002_xxx.mp4`, etc.

## Files Modified

1. `scraper_sora_advanced.py`:
   - `_find_remix_links()`: Complete rewrite with better detection
   - `scrape_remix_chain()`: Added modal closing and better waits

2. `test_remix.py`:
   - Updated to target 10+ remixes
   - Better instructions and output

All changes are backward compatible!
