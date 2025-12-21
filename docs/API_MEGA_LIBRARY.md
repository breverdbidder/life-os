


## 🎬 VIDEO & TRANSCRIPT APIs - Life OS Learning Integration

### YouTube Transcript Extraction (Priority Order)

| Method | Cost | Speed | Accuracy | Use Case |
|--------|------|-------|----------|----------|
| `youtube-transcript-api` | FREE | Instant | 95%+ | Videos WITH captions |
| `yt-dlp` captions | FREE | Fast | 95%+ | All caption formats (VTT, SRT) |
| Whisper base | FREE* | Slow | 90% | Videos without captions |
| Whisper small | FREE* | Medium | 95% | Better quality fallback |
| Apify YouTube Scraper | $0.01/run | Fast | 99% | Premium/bulk extraction |

*Whisper is free but compute-intensive (requires GPU/CPU time)

### YouTube Scrapers on Apify (979 Total APIs)

| Actor | ID | Use Case | Pricing |
|-------|----|---------:|---------|
| [YouTube Transcript Scraper](https://apify.com/topaz_sharingan/youtube-transcript-scraper) | topaz_sharingan/youtube-transcript-scraper | Full transcripts + metadata | Per run |
| [Video Transcript Scraper](https://apify.com/invideoiq/video-transcript-scraper) | invideoiq/video-transcript-scraper | YouTube, X, TikTok, Facebook | Per run |
| [Best Youtube Transcripts](https://apify.com/scrape-creators/best-youtube-transcripts-scraper) | scrape-creators/best-youtube-transcripts-scraper | Bulk extraction, multiple formats | Per run |
| [YouTube Video Details](https://apify.com/memo23/youtube-video-details-scraper) | memo23/youtube-video-details-scraper | Metadata + transcripts | Per run |
| [YouTube Subtitles Scraper](https://apify.com/scraper-engine/youtube-video-subtitles-scraper) | scraper-engine/youtube-video-subtitles-scraper | Multi-language support | Per run |

### Life OS YouTube Transcript Agent

**Location:** `breverdbidder/life-os/agents/youtube_transcript/youtube_transcript_agent.py`

**Workflow:** `.github/workflows/youtube_transcript_v2.yml`

**Supported URL Formats:**
- Regular: `https://youtube.com/watch?v=VIDEO_ID`
- Shorts: `https://youtube.com/shorts/VIDEO_ID`
- Short URL: `https://youtu.be/VIDEO_ID`
- Embed: `https://youtube.com/embed/VIDEO_ID`

**Extraction Strategy (Smart Router Philosophy):**
```
┌─────────────────────────────────────────────────────────────┐
│                 YouTube Transcript Agent                    │
├─────────────────────────────────────────────────────────────┤
│  1. TRY CAPTIONS (FREE, instant)                           │
│     └── yt-dlp --write-subs --write-auto-subs              │
│                                                             │
│  2. IF NO CAPTIONS → WHISPER FALLBACK                      │
│     └── yt-dlp -x → whisper.load_model("base")             │
│                                                             │
│  3. SAVE TO SUPABASE                                       │
│     └── insights table (youtube_transcript type)            │
└─────────────────────────────────────────────────────────────┘
```

**Usage - GitHub Actions:**
```bash
gh workflow run youtube_transcript_v2.yml \
  -f video_url="https://youtube.com/shorts/C2Dl6P7diHw" \
  -f use_whisper=true \
  -f log_to_supabase=true
```

**Usage - Python:**
```python
from agents.youtube_transcript.youtube_transcript_agent import extract_transcript

result = extract_transcript(
    "https://youtube.com/shorts/C2Dl6P7diHw",
    use_whisper_fallback=True,
    log_to_supabase=True
)
print(result['transcript'])
```

### Integration with Life OS Learning

Transcripts are saved to Supabase `insights` table:
- `insight_type`: "youtube_transcript"
- `title`: "YT: {video_title}"
- `description`: JSON with video_id, channel, duration, source, transcript_preview
- `priority`: 2 (learning content)

Query learning sessions:
```sql
SELECT * FROM insights 
WHERE insight_type = 'youtube_transcript'
ORDER BY created_at DESC
LIMIT 20;
```

---

**Updated:** December 21, 2025 | **Version:** V2.0.0
