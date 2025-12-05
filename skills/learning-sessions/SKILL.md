# Learning Sessions Skill

## Overview
System for extracting, analyzing, and storing insights from YouTube videos and other learning content.

## Components

### 1. YouTube Transcript Extraction
**Workflow:** `.github/workflows/youtube_transcript.yml`
**Trigger:** Manual dispatch with video URL
**Output:** Transcript JSON + Supabase logging

### 2. Transcript Analysis
When analyzing a transcript, Claude should:
1. Identify key concepts and takeaways
2. Extract actionable insights
3. Map applications to Ariel's businesses (BrevardBidderAI, Everest Capital, Life OS)
4. Note relevant quotes (with timestamps if available)
5. Suggest follow-up actions or research

### 3. Storage Locations

#### Supabase `insights` table
- `insight_type`: "learning_session"
- `title`: "YouTube: [Video Title]"
- `description`: Summary with channel, duration, key points

#### GitHub `skills/learning-sessions/` folder
- `transcripts/`: Raw transcript files
- `summaries/`: Analyzed summaries
- `LEARNINGS.md`: Consolidated key learnings

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
3. [Point 3]

### Application to My Business
- **BrevardBidderAI:** [How this applies]
- **Life OS:** [How this applies]
- **General:** [Broader insights]

### Actionable Items
- [ ] [Action 1]
- [ ] [Action 2]

### Notable Quotes
> "[Quote]" - [Timestamp]

### Tags
#[tag1] #[tag2] #[tag3]
```

## Usage

### Extract transcript from Claude.ai:
```
Share YouTube URL → Claude triggers GitHub Action → Transcript extracted → Analysis provided
```

### Manual trigger:
1. Go to: https://github.com/breverdbidder/life-os/actions/workflows/youtube_transcript.yml
2. Click "Run workflow"
3. Enter video URL
4. Download transcript artifact

### Store important learning:
```
"Log this learning session"
→ Claude saves to Supabase insights
→ If highly valuable, adds to skills/learning-sessions/LEARNINGS.md
```

