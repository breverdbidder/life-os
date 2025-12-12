# Learning Sessions Skill

## Overview
System for extracting, analyzing, and storing insights from YouTube videos and other learning content.

## Components

### 1. YouTube Transcript Extraction
**Workflow:** `.github/workflows/youtube_transcript.yml`
**Trigger:** Manual dispatch or Claude-triggered
**Output:** Transcript JSON + Supabase logging

### 2. Fallback Strategy
When transcripts are unavailable (no captions, Hebrew videos, etc.):
1. Claude uses `noembed.com` API to get video title/channel
2. Claude uses web search to find content about the topic
3. Claude analyzes based on available information
4. User can provide manual context if needed

### 3. Storage Locations

| Location | Purpose |
|----------|---------|
| `skills/learning-sessions/summaries/` | Full analysis files |
| `skills/learning-sessions/LEARNINGS.md` | Quick reference consolidated |
| Supabase `insights` table | Searchable metadata |

### 4. Analysis Template

```markdown
## [Video Title]
**Source:** [URL]
**Channel:** [Channel Name]
**Duration:** [X minutes]
**Date Watched:** [Date]

### Key Takeaways
1. [Point 1]
2. [Point 2]

### Application to My Business
- **BidDeed.AI:** [How this applies]
- **Life OS:** [How this applies]

### Actionable Items
- [ ] [Action 1]

### Tags
#tag1 #tag2
```

## Usage

### From Claude.ai:
1. Share YouTube URL
2. Claude extracts metadata + searches for context
3. Claude provides analysis
4. Say "Log this" to save important sessions

### Manual Trigger:
1. Go to: https://github.com/breverdbidder/life-os/actions/workflows/youtube_transcript.yml
2. Click "Run workflow"
3. Enter video URL
4. Download transcript artifact (if available)

## Known Limitations
- Videos without captions return "Transcript unavailable"
- Hebrew videos may not have auto-generated captions
- Private/unlisted videos cannot be accessed
- Claude.ai environment has network restrictions; GitHub Actions can access YouTube

## Workarounds
For videos without transcripts:
1. Watch the video manually
2. Share key points with Claude
3. Claude will structure and store the learning session
