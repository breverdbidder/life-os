# Hybrid News Aggregator

AI-powered news aggregation and viral post creation for **BidDeed.AI** and **Life OS**.

## Overview

This system aggregates news from multiple categories and creates viral social media posts using Google Gemini AI.

### Categories

| Category | Purpose | Sources |
|----------|---------|---------|
| **FORECLOSURE** | BidDeed.AI core content | DS News, National Mortgage News, Mortgage Orb, RealtyTrac |
| **PROPTECH** | Real estate tech marketing | Inman, HousingWire, The Real Deal, GlobeSt, Propmodo |
| **AI_ML** | Learning & thought leadership | TechCrunch, VentureBeat, MIT Tech Review, Wired, Ars Technica |
| **SCRAPING** | Technical learning | Hacker News, Dev.to Python, Dev.to Automation |

### Outputs

1. **BidDeed.AI Viral Posts**
   - LinkedIn (professional thought leadership)
   - Twitter/X (punchy, engagement-focused)
   - Instagram (story-driven, relatable)

2. **Life OS Learning Digest**
   - Top 3 AI/ML insights
   - Tools & techniques mentioned
   - Industry trends
   - Action items

3. **Supabase Logging**
   - `insights` table with category `biddeed_viral_posts`
   - `insights` table with category `learning`
   - `insights` table with category `news_aggregation`

4. **Telegram Notifications**
   - Daily digest summaries
   - Ready-to-post content

## Architecture

```
RSS Feeds → RSSFeedCollector → ArticleAggregator → GeminiPostCreator
                                      ↓
                              TelegramNotifier
                              SupabaseLogger
```

## Usage

### Manual Run

```bash
# Full mode (both BidDeed.AI and Life OS)
python hybrid_news_aggregator.py --mode full

# BidDeed.AI only (foreclosure, proptech, AI)
python hybrid_news_aggregator.py --mode biddeed

# Life OS only (AI/ML learning)
python hybrid_news_aggregator.py --mode lifeos
```

### GitHub Actions

Automated runs:
- 6 AM EST - Morning digest
- 12 PM EST - Midday update
- 6 PM EST - Evening summary

Manual trigger: Actions → Hybrid News Aggregator → Run workflow

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini 2.5 Flash API key |
| `SUPABASE_KEY` | Yes | Supabase service role key |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Optional | Telegram chat ID for notifications |

## File Structure

```
agents/news_aggregator/
├── hybrid_news_aggregator.py  # Main application
├── requirements.txt           # Python dependencies
└── README.md                  # This file

.github/workflows/
└── hybrid_news_aggregator.yml # GitHub Actions workflow
```

## Feeds

### Foreclosure & Distressed
- DS News: https://dsnews.com/feed/
- National Mortgage News: https://www.nationalmortgagenews.com/feed
- Mortgage Orb: https://mortgageorb.com/feed/
- RealtyTrac Blog: https://www.realtytrac.com/blog/feed/

### PropTech
- Inman: https://www.inman.com/feed/
- HousingWire: https://www.housingwire.com/feed/
- The Real Deal: https://therealdeal.com/feed/
- GlobeSt: https://www.globest.com/feed/
- Propmodo: https://www.propmodo.com/feed/

### AI/ML
- TechCrunch AI: https://techcrunch.com/tag/artificial-intelligence/feed/
- VentureBeat AI: https://venturebeat.com/category/ai/feed/
- MIT Tech Review: https://www.technologyreview.com/topic/artificial-intelligence/feed
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence/rss/index.xml
- Wired AI: https://www.wired.com/feed/tag/ai/latest/rss

### Scraping/Automation
- Hacker News: https://hnrss.org/frontpage
- Dev.to Python: https://dev.to/feed/tag/python
- Dev.to Automation: https://dev.to/feed/tag/automation

## Customization

### Add New Feeds

Edit `RSSFeedCollector.FEEDS` in `hybrid_news_aggregator.py`:

```python
FEEDS = {
    'AI_ML': {
        # ... existing feeds
        'New Source': 'https://example.com/feed/',
    },
}
```

### Modify Relevance Keywords

Edit `RSSFeedCollector.RELEVANCE_KEYWORDS`:

```python
RELEVANCE_KEYWORDS = {
    'AI_ML': ['ai', 'machine learning', 'your_keyword'],
}
```

### Customize Post Format

Edit the prompt templates in `GeminiPostCreator`:
- `create_biddeed_prompt()` - BidDeed.AI viral posts
- `create_lifeos_prompt()` - Learning digest

## Deployment

### To life-os repo

```bash
# Copy files to repo
cp hybrid_news_aggregator.py ../life-os/agents/news_aggregator/
cp hybrid_news_aggregator.yml ../life-os/.github/workflows/

# Commit and push
cd ../life-os
git add .
git commit -m "feat: Add hybrid news aggregator for BidDeed.AI + Life OS"
git push
```

### Required Secrets (GitHub)

1. Go to repo Settings → Secrets and variables → Actions
2. Add:
   - `GOOGLE_API_KEY` - Your Gemini API key
   - `SUPABASE_KEY` - Supabase service role key
   - `TELEGRAM_BOT_TOKEN` - (Optional) Telegram bot token
   - `TELEGRAM_CHAT_ID` - (Optional) Your Telegram chat ID

## Output Examples

### BidDeed.AI LinkedIn Post

```
🏠 AI is eating real estate—and foreclosure investing is next.

While most investors still manually scan auction lists, AI-powered platforms 
are analyzing 1000s of properties in minutes, predicting third-party purchase 
probability, and calculating optimal max bids.

The edge isn't information anymore. It's intelligence.

#RealEstateAI #Foreclosure #PropTech #AIInvesting #BidDeedAI
```

### Life OS Digest

```json
{
  "date": "2024-12-14",
  "top_insights": [
    "LangGraph adds checkpoint persistence for production agents",
    "DeepSeek V3.2 achieves GPT-4 level at 10x lower cost",
    "Anthropic releases Claude computer use API"
  ],
  "tools_mentioned": ["LangGraph", "DeepSeek", "pdfplumber"],
  "action_items": ["Evaluate DeepSeek for ULTRA_CHEAP tier"],
  "relevance_to_biddeed": "LangGraph checkpointing could improve BECA reliability"
}
```

## Maintenance

- Feeds may change URLs - check failed runs and update
- Gemini API limits: 60 RPM free tier
- Review generated posts before publishing

---

**Stack:** Python 3.11 | Gemini 2.5 Flash | Supabase | GitHub Actions | Telegram
