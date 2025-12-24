# Media Transcript Agent V8 🎬🌍

**Multi-platform transcript extraction with automatic Hebrew→English translation**

## Supported Platforms
- ✅ YouTube
- ✅ Facebook
- ✅ Instagram  
- ✅ TikTok

## Features

### 4-Tier Extraction System
```
Tier 1: Platform API (YouTube Transcript API)
   ↓ (if fails)
Tier 2: yt-dlp subtitle extraction (all platforms)
   ↓ (if fails)
Tier 3: Whisper transcription (audio→text)
   ↓ (if fails)
Tier 4: Apify scraper fallback
```

### 2-Tier Translation System (Hebrew→English)
```
Tier 1: DeepSeek V3.2 ($0.28/1M tokens)
   ↓ (if fails)
Tier 2: Google Translate (FREE)
```

## Quick Start

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your_key"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"

# Test with YouTube (Hebrew video)
python agents/media/media_transcript_node.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Test with Facebook video
python agents/media/media_transcript_node.py "https://www.facebook.com/watch?v=VIDEO_ID"

# Test with Instagram
python agents/media/media_transcript_node.py "https://www.instagram.com/reel/REEL_ID"
```

### GitHub Actions Deployment

1. **Push to repository:**
```bash
git add agents/media/media_transcript_node.py
git add .github/workflows/media_transcript.yml
git add requirements.txt
git commit -m "feat: Media Transcript Agent V8 - multi-platform + Hebrew translation"
git push origin main
```

2. **Run workflow:**
   - Go to Actions tab in GitHub
   - Select "Media Transcript Agent V8"
   - Click "Run workflow"
   - Enter URL
   - Check "Save to Supabase" if desired

## Usage Examples

### Example 1: YouTube Hebrew Video

**Input:**
```
URL: https://www.youtube.com/watch?v=EXAMPLE_HE
```

**Output:**
```json
{
  "url": "https://www.youtube.com/watch?v=EXAMPLE_HE",
  "platform": "youtube",
  "method": "tier1_youtube_api",
  "language": "he",
  "transcript": "שלום, היום נדבר על...",
  "translation": "Hello, today we'll talk about...",
  "translation_method": "deepseek_v3.2"
}
```

### Example 2: Facebook Video (English)

**Input:**
```
URL: https://www.facebook.com/watch?v=12345
```

**Output:**
```json
{
  "url": "https://www.facebook.com/watch?v=12345",
  "platform": "facebook",
  "method": "tier2_ytdlp",
  "language": "en",
  "transcript": "Welcome to today's video...",
  "translation": null,
  "translation_method": null
}
```

### Example 3: Instagram Reel (Hebrew)

**Input:**
```
URL: https://www.instagram.com/reel/ABC123
```

**Output:**
```json
{
  "url": "https://www.instagram.com/reel/ABC123",
  "platform": "instagram",
  "method": "tier2_ytdlp",
  "language": "he",
  "transcript": "היי חברים, הנה טיפ מהיר...",
  "translation": "Hey friends, here's a quick tip...",
  "translation_method": "google_translate"
}
```

## Integration with LangGraph

```python
from langgraph.graph import StateGraph
from agents.media.media_transcript_node import media_transcript_node

# Define workflow
workflow = StateGraph(dict)

# Add media transcript node
workflow.add_node("extract_transcript", media_transcript_node)

# Example state
initial_state = {
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "options": {
        "translate": True,
        "save_to_db": True
    }
}

# Run
app = workflow.compile()
result = await app.ainvoke(initial_state)

print(f"Original: {result['transcript_result']['transcript']}")
print(f"Translation: {result['transcript_result']['translation']}")
```

## API Reference

### `MediaTranscriptAgent.extract_transcript(url: str) -> Dict`

**Parameters:**
- `url` (str): Video URL from YouTube, Facebook, Instagram, or TikTok

**Returns:**
```python
{
    'url': str,              # Input URL
    'platform': str,         # Detected platform
    'method': str,           # Extraction tier used
    'language': str,         # Detected language (he/en)
    'transcript': str,       # Original transcript
    'translation': str,      # English translation (if Hebrew)
    'translation_method': str,  # Translation tier used
    'error': str            # Error message (if failed)
}
```

## Cost Analysis

### Per 1,000 Videos

**Assumptions:**
- 50% Hebrew content
- Average 10-minute videos
- ~5,000 tokens per transcript

**Extraction Costs:**
- Tier 1 (YouTube API): FREE
- Tier 2 (yt-dlp): FREE
- Tier 3 (Whisper): $0.006/minute × 10min = $0.06/video
- Tier 4 (Apify): ~$0.10/video

**Translation Costs (Hebrew only):**
- Tier 1 (DeepSeek V3.2): $0.28/1M × 5K tokens = $0.0014/video
- Tier 2 (Google Translate): FREE

**Expected Cost:** ~$0.001/video (assuming 90% hit Tier 1/2)

**1,000 videos = ~$1.00 total** ✅

## Platform-Specific Notes

### YouTube
- ✅ Best support (native API)
- ✅ Automatic captions available for most videos
- ✅ Multiple language support

### Facebook
- ⚠️ Limited subtitle availability
- ✅ yt-dlp works for public videos
- ⚠️ Requires video to be public

### Instagram
- ⚠️ No native subtitle support
- ✅ yt-dlp can extract audio
- ⚠️ May require Tier 3 (Whisper) more often

### TikTok
- ⚠️ No native subtitle support
- ✅ yt-dlp works for public videos
- ⚠️ May have rate limiting

## Troubleshooting

### "All tiers failed"
1. Check if video is public/accessible
2. Verify URL format is correct
3. Try adding `/watch?v=` for YouTube short links
4. Check API keys are set correctly

### "Translation failed"
1. Verify ANTHROPIC_API_KEY is set
2. Check Google Translate isn't blocked
3. Try shorter text chunks

### Facebook "403 Forbidden"
1. Ensure video is public (not friends-only)
2. Try using fb.watch short link format
3. Check if region-restricted

## Roadmap

- [x] Multi-platform support
- [x] Hebrew→English translation
- [ ] Tier 3 Whisper implementation
- [ ] Tier 4 Apify integration
- [ ] Support for additional languages (Arabic, Russian)
- [ ] Real-time streaming transcript extraction
- [ ] Subtitle timing preservation
- [ ] Multi-language output (original + multiple translations)

## License

MIT

---

**Built with:**
- yt-dlp for universal video extraction
- YouTube Transcript API for optimal YouTube support
- DeepSeek V3.2 for cost-effective translation
- Google Translate for free fallback
- Anthropic Claude for orchestration
