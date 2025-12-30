# Article Parser Agent V1.0

## Overview

The Article Parser Agent automatically extracts, parses, and analyzes web articles with Life OS domain classification.

**Purpose:** Convert article URLs into structured, actionable insights mapped to Life OS domains (BUSINESS/MICHAEL/FAMILY/PERSONAL).

## Features

### 🆓 FREE Extraction Strategy
1. **Trafilatura** (Primary) - Python library, instant, no API key
2. **BeautifulSoup + html2text** (Fallback) - Free HTML parsing
3. **AI Content Processor** (Paid) - Apify integration only if needed

### 📊 Life OS Analysis
- **Domain Classification:** Maps content to BUSINESS, MICHAEL, FAMILY, PERSONAL, or UNCATEGORIZED
- **Relevance Scoring:** 1-10 scale based on keyword analysis
- **Summary Generation:** Concise 3-sentence summary
- **Key Insights:** Extracts numbered/bulleted points
- **Actionable Tasks:** Identifies action-oriented sentences

### 💾 Data Storage
- Saves to Supabase `articles` table
- Full-text search indexing
- Deduplication via URL hash
- Markdown + plain text formats

## Installation

```bash
# Install dependencies
pip install trafilatura beautifulsoup4 html2text httpx lxml

# Or use requirements.txt
pip install -r requirements.txt
```

## Usage

### CLI Testing
```bash
python agents/article_parser/article_parser_agent.py "https://example.com/article"
```

### GitHub Actions Workflow
```bash
# Manual trigger
gh workflow run article_parser.yml -f url="https://example.com/article"

# API trigger
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/breverdbidder/life-os/dispatches \
  -d '{"event_type":"article_parse","client_payload":{"url":"https://example.com/article"}}'
```

### LangGraph Integration
```python
from agents.article_parser.article_parser_agent import article_parser_node

# Use in LangGraph workflow
graph.add_node("parse_article", article_parser_node)
```

## Life OS Domain Classification

### Keyword Mapping

**BUSINESS:**
- startup, business, founder, company, investment, real estate
- foreclosure, auction, valuation, product, market, revenue
- entrepreneurship, ai, technology, saas, platform

**MICHAEL:**
- swimming, swim, athlete, training, d1, recruiting, college
- competition, nutrition, keto, diet, performance

**FAMILY:**
- family, parenting, shabbat, kosher, orthodox, judaism
- marriage, spouse, home, holiday

**PERSONAL:**
- adhd, productivity, health, fitness, learning, skill
- habit, focus, energy, sleep, meditation

## Output Structure

```python
ArticleResult(
    url: str,
    url_hash: str,              # MD5 hash for deduplication
    title: str,
    author: Optional[str],
    publication_date: Optional[str],
    domain: str,                # example.com
    content_markdown: str,      # Full markdown content
    content_text: str,          # Plain text content
    word_count: int,
    extraction_source: str,     # trafilatura, beautifulsoup, apify_ai
    life_os_domain: str,        # BUSINESS, MICHAEL, FAMILY, PERSONAL
    life_os_summary: str,       # 3-sentence summary
    key_insights: List[str],    # Extracted bullet points
    actionable_tasks: List[str], # Action-oriented sentences
    relevance_score: int,       # 1-10 relevance to Life OS
    timestamp: str,
    error: Optional[str],
    metadata: Optional[Dict]
)
```

## Supabase Schema

```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    url TEXT NOT NULL,
    url_hash TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author TEXT,
    publication_date TEXT,
    domain TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    content_text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    extraction_source TEXT NOT NULL,
    life_os_domain TEXT NOT NULL,
    life_os_summary TEXT NOT NULL,
    key_insights JSONB,
    actionable_tasks JSONB,
    relevance_score INTEGER CHECK (relevance_score >= 0 AND relevance_score <= 10),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## API Library Integration

From `docs/API_MEGA_LIBRARY.md`:

- **AI Content Processor** - GPT-4o summarization (Apify)
- **AI Markdown Maker** - Bulk web to markdown (Apify)
- **AI Web Scraper** - LLM-optimized scraping (Crawl4AI)

## Cost Optimization

- **FREE Tier:** Trafilatura + BeautifulSoup (99% of cases)
- **PAID Tier:** AI Content Processor only when free methods fail
- **Target:** $0/month for typical usage

## Examples

### Startup Validation Article
```bash
python article_parser_agent.py "https://getpathforge.web.app/blog/how-to-validate-your-startup-idea-before-writing-any-code"

# Expected Output:
Domain: BUSINESS
Relevance: 8/10
Summary: Article discusses pre-build validation methods to avoid building products without market need...
Insights:
  - 42% of startups fail due to no market need
  - Validate with customer interviews first
  - Use landing pages for pre-sales testing
Tasks:
  - Create customer interview script
  - Build validation landing page
  - Test pricing hypotheses
```

### Swimming Article
```bash
python article_parser_agent.py "https://example.com/d1-swimming-recruiting-guide"

# Expected Output:
Domain: MICHAEL
Relevance: 9/10
Summary: Guide covers D1 recruiting timeline, coach contact strategies, and video submission best practices...
```

## Integration with Orchestrator

The Article Parser Agent integrates with Life OS LangGraph orchestrator:

```python
# In orchestrator graph
graph.add_node("detect_url", url_detection_node)
graph.add_node("parse_article", article_parser_node)
graph.add_edge("detect_url", "parse_article")
```

Auto-trigger when Claude detects article URLs in conversation.

## Troubleshooting

### Trafilatura Installation
```bash
pip install --upgrade trafilatura
# If lxml issues:
pip install lxml --upgrade
```

### BeautifulSoup Issues
```bash
pip install beautifulsoup4 lxml html5lib
```

### Supabase Connection
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python -c "from lib.supabase_client import get_supabase_client; print(get_supabase_client())"
```

## Future Enhancements

- [ ] Smart Router integration for AI summarization
- [ ] Multi-language support
- [ ] PDF article extraction
- [ ] Paywalled content handling (via Apify)
- [ ] Topic clustering across articles
- [ ] Automatic task creation in Life OS
- [ ] Citation extraction and linking

## Version History

- **V1.0.0** (2025-12-30) - Initial release
  - Trafilatura + BeautifulSoup extraction
  - Life OS domain classification
  - Supabase storage
  - GitHub Actions workflow

## Author

Claude AI Architect - Life OS  
Date: December 30, 2025
