# Quick Start: Ariel's Facebook Video

**URL:** https://www.facebook.com/share/r/1EVegyZC3N/

## Option 1: GitHub Actions (Recommended)

1. **Go to GitHub Actions:**
   ```
   https://github.com/breverdbidder/life-os/actions/workflows/media_transcript.yml
   ```

2. **Click "Run workflow"**

3. **Enter URL:**
   ```
   https://www.facebook.com/share/r/1EVegyZC3N/
   ```

4. **Check "Save to Supabase"** ✅

5. **Click "Run workflow"** 🚀

6. **Wait ~30 seconds**

7. **View results:**
   - In workflow logs
   - In Supabase `insights` table (category: `media_transcript`)

## Option 2: Local Testing

```bash
# From life-os directory
export ANTHROPIC_API_KEY="your_key"
export SUPABASE_URL="https://mocerqjnksmhcjzxrewo.supabase.co"
export SUPABASE_KEY="your_key"

python agents/media/media_transcript_node.py "https://www.facebook.com/share/r/1EVegyZC3N/"
```

## Expected Output

```json
{
  "url": "https://www.facebook.com/share/r/1EVegyZC3N/",
  "platform": "facebook",
  "method": "tier2_ytdlp",
  "language": "he",
  "transcript": "[Original Hebrew transcript from video]",
  "translation": "[English translation]",
  "translation_method": "deepseek_v3.2"
}
```

## What Gets Saved to Supabase

**Table:** `insights`

**Row:**
```json
{
  "category": "media_transcript",
  "subcategory": "auto_extraction",
  "content": "[Full transcript + translation]",
  "source": "media_transcript_agent_v8",
  "metadata": {
    "url": "https://www.facebook.com/share/r/1EVegyZC3N/",
    "platform": "facebook",
    "language": "he",
    "translation_method": "deepseek_v3.2"
  }
}
```

## Troubleshooting Facebook Videos

### Issue: "403 Forbidden" or "Private video"

**Solutions:**
1. Make sure video is **public** (not friends-only)
2. Try alternative Facebook URL formats:
   ```
   https://www.facebook.com/watch?v=VIDEO_ID
   https://fb.watch/SHORT_ID
   ```
3. If video is from a page, try the page's direct URL

### Issue: "No subtitles found"

This is normal for Facebook. The agent will:
1. Try Tier 1: yt-dlp subtitle extraction (usually fails for FB)
2. Fall to Tier 2: yt-dlp video download → audio extraction
3. Fall to Tier 3: Whisper transcription (coming soon)

**Workaround:** For now, if subtitles aren't embedded, you may need to wait for Tier 3 (Whisper) implementation.

## Cost Estimate

For this single Facebook video:
- Extraction: FREE (yt-dlp)
- Translation (if Hebrew): ~$0.001 (DeepSeek V3.2)
- **Total: ~$0.001** ✅

## Integration with Life OS

This transcript will automatically be available in:
- ✅ Supabase `insights` table
- ✅ Life OS learning tracking
- ✅ Can be referenced by other agents

Query in Supabase:
```sql
SELECT * FROM insights 
WHERE category = 'media_transcript' 
AND metadata->>'url' = 'https://www.facebook.com/share/r/1EVegyZC3N/';
```

---

**Note:** If this specific Facebook video is private or region-restricted, you may need to:
1. Download it manually
2. Upload to YouTube (unlisted)
3. Use the YouTube URL instead

YouTube has better subtitle support and higher success rate.
