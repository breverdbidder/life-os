"""
Article Parser Agent V1.0 - Life OS LangGraph Orchestration
===========================================================
FREE article extraction and Life OS-aware summarization.

EXTRACTION STRATEGY (Smart Router Philosophy):
1. FREE Tier: Trafilatura (Python library - instant, no API key)
2. FREE Tier: BeautifulSoup + Readability (fallback parsing)
3. Paid Tier: AI Content Processor (Apify - if needed)

SUMMARIZATION:
- Analyzes content against Life OS domains (BUSINESS/MICHAEL/FAMILY/PERSONAL)
- Extracts key insights relevant to user's context
- Maps to actionable tasks if applicable

AUTO-TRIGGER: Claude detects article URLs and triggers this agent.

Author: Claude AI Architect (Life OS)
Version: 1.0.0
Date: 2025-12-30
"""

import os
import re
import json
import httpx
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import html2text


class ArticleSource(Enum):
    """Source of article extraction"""
    TRAFILATURA = "trafilatura"           # Primary FREE
    BEAUTIFULSOUP = "beautifulsoup"       # FREE fallback
    AI_CONTENT_PROCESSOR = "apify_ai"     # Paid fallback
    FAILED = "failed"


class LifeOSDomain(Enum):
    """Life OS categorization domains"""
    BUSINESS = "BUSINESS"
    MICHAEL = "MICHAEL"
    FAMILY = "FAMILY"
    PERSONAL = "PERSONAL"
    UNCATEGORIZED = "UNCATEGORIZED"


@dataclass
class ArticleResult:
    """Complete article extraction result"""
    url: str
    url_hash: str
    title: str
    author: Optional[str]
    publication_date: Optional[str]
    domain: str
    content_markdown: str
    content_text: str
    word_count: int
    extraction_source: str
    life_os_domain: str
    life_os_summary: str
    key_insights: List[str]
    actionable_tasks: List[str]
    relevance_score: int  # 1-10
    timestamp: str
    error: Optional[str] = None
    metadata: Optional[Dict] = None


# =============================================================================
# URL PARSING & VALIDATION
# =============================================================================

def is_article_url(text: str) -> bool:
    """Check if text contains a valid article URL"""
    # Exclude common video/media domains
    excluded_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
        'twitter.com', 'x.com', 'instagram.com', 'facebook.com',
        'tiktok.com', 'spotify.com', 'soundcloud.com'
    ]
    
    url_pattern = r'https?://[^\s<>"]+'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        if not any(excluded in domain for excluded in excluded_domains):
            return True
    return False


def extract_article_urls(text: str) -> List[str]:
    """Extract all valid article URLs from text"""
    url_pattern = r'https?://[^\s<>"]+'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    excluded_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com', 'twitter.com', 'x.com',
        'instagram.com', 'facebook.com', 'tiktok.com', 'spotify.com'
    ]
    
    valid_urls = []
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        if not any(excluded in domain for excluded in excluded_domains):
            valid_urls.append(url)
    
    return valid_urls


def generate_url_hash(url: str) -> str:
    """Generate unique hash for URL (for deduplication)"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


# =============================================================================
# STRATEGY 1: Trafilatura (PRIMARY FREE)
# =============================================================================

def extract_with_trafilatura(url: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Extract article content using Trafilatura.
    FASTEST and FREE for most articles.
    """
    try:
        import trafilatura
        
        print(f"🎯 Strategy 1: Trafilatura for {url}...")
        
        # Fetch the content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None, "Failed to download content"
        
        # Extract with metadata
        result = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format='json',
            with_metadata=True
        )
        
        if not result:
            return None, "No content extracted"
        
        # Parse JSON result
        data = json.loads(result) if isinstance(result, str) else result
        
        # Convert to markdown
        markdown_content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format='markdown'
        )
        
        return {
            'title': data.get('title', 'Untitled'),
            'author': data.get('author'),
            'date': data.get('date'),
            'domain': data.get('hostname', urlparse(url).netloc),
            'text': data.get('text', ''),
            'markdown': markdown_content or data.get('text', ''),
            'description': data.get('description'),
            'categories': data.get('categories', []),
            'tags': data.get('tags', []),
        }, None
        
    except ImportError:
        return None, "Trafilatura not installed (run: pip install trafilatura)"
    except Exception as e:
        return None, f"Trafilatura error: {str(e)}"


# =============================================================================
# STRATEGY 2: BeautifulSoup + html2text (FREE FALLBACK)
# =============================================================================

def extract_with_beautifulsoup(url: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Extract article content using BeautifulSoup + html2text.
    FREE fallback when Trafilatura fails.
    """
    try:
        print(f"🎯 Strategy 2: BeautifulSoup for {url}...")
        
        # Fetch content
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LifeOS-ArticleParser/1.0)'
        }
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata
        title = soup.find('title')
        title = title.get_text().strip() if title else 'Untitled'
        
        # Try to find author
        author = None
        author_meta = soup.find('meta', {'name': 'author'}) or \
                     soup.find('meta', {'property': 'article:author'})
        if author_meta:
            author = author_meta.get('content')
        
        # Try to find date
        date = None
        date_meta = soup.find('meta', {'property': 'article:published_time'}) or \
                   soup.find('time')
        if date_meta:
            date = date_meta.get('datetime') or date_meta.get('content') or date_meta.get_text()
        
        # Extract main content
        # Remove script, style, nav, footer
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # Look for main content area
        main_content = soup.find('article') or soup.find('main') or \
                      soup.find('div', class_=re.compile('content|article|post')) or \
                      soup.find('body')
        
        if not main_content:
            return None, "Could not find main content"
        
        # Convert to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        markdown_content = h.handle(str(main_content))
        
        # Get plain text
        text_content = main_content.get_text(separator='\n', strip=True)
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'domain': urlparse(url).netloc,
            'text': text_content,
            'markdown': markdown_content,
        }, None
        
    except Exception as e:
        return None, f"BeautifulSoup error: {str(e)}"


# =============================================================================
# STRATEGY 3: AI Content Processor (PAID FALLBACK)
# =============================================================================

def extract_with_apify_ai(url: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Extract and process article using Apify AI Content Processor.
    PAID tier - only used if free methods fail.
    """
    apify_token = os.getenv('APIFY_API_TOKEN')
    if not apify_token:
        return None, "APIFY_API_TOKEN not set"
    
    try:
        print(f"💰 Strategy 3: AI Content Processor (PAID) for {url}...")
        
        # This would call Apify actor
        # For now, return not implemented
        return None, "AI Content Processor not implemented yet"
        
    except Exception as e:
        return None, f"Apify AI error: {str(e)}"


# =============================================================================
# LIFE OS ANALYSIS
# =============================================================================

def analyze_for_life_os(content: str, title: str, url: str, metadata: Dict) -> Dict[str, Any]:
    """
    Analyze article against Life OS domains and extract actionable insights.
    Uses Smart Router for cost optimization.
    """
    # Keywords for domain classification
    business_keywords = [
        'startup', 'business', 'founder', 'company', 'investment', 'real estate',
        'foreclosure', 'auction', 'valuation', 'product', 'market', 'revenue',
        'entrepreneurship', 'ai', 'technology', 'saas', 'platform'
    ]
    
    michael_keywords = [
        'swimming', 'swim', 'athlete', 'training', 'd1', 'recruiting', 'college',
        'competition', 'nutrition', 'keto', 'diet', 'performance'
    ]
    
    family_keywords = [
        'family', 'parenting', 'shabbat', 'kosher', 'orthodox', 'judaism',
        'marriage', 'spouse', 'home', 'holiday'
    ]
    
    personal_keywords = [
        'adhd', 'productivity', 'health', 'fitness', 'learning', 'skill',
        'habit', 'focus', 'energy', 'sleep', 'meditation'
    ]
    
    # Combine title and content for analysis
    text = f"{title} {content}".lower()
    
    # Score each domain
    scores = {
        'BUSINESS': sum(1 for k in business_keywords if k in text),
        'MICHAEL': sum(1 for k in michael_keywords if k in text),
        'FAMILY': sum(1 for k in family_keywords if k in text),
        'PERSONAL': sum(1 for k in personal_keywords if k in text),
    }
    
    # Determine primary domain
    primary_domain = max(scores, key=scores.get)
    if scores[primary_domain] == 0:
        primary_domain = 'UNCATEGORIZED'
    
    # Generate summary (using Smart Router would happen here)
    # For V1.0, use simple extraction
    sentences = re.split(r'[.!?]\s+', content)
    summary_sentences = sentences[:3]  # First 3 sentences
    summary = '. '.join(summary_sentences) + '.'
    
    # Extract key insights (first occurrence of list items or numbers)
    insights = []
    for line in content.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            insights.append(line)
            if len(insights) >= 5:
                break
    
    # Actionable tasks (look for imperatives)
    actionable_verbs = ['create', 'build', 'implement', 'develop', 'design', 'test', 'validate', 'research']
    tasks = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(verb in sentence_lower for verb in actionable_verbs):
            tasks.append(sentence.strip())
            if len(tasks) >= 3:
                break
    
    # Calculate relevance score (1-10)
    relevance = min(10, max(1, scores[primary_domain]))
    
    return {
        'domain': primary_domain,
        'summary': summary,
        'insights': insights or ['No specific insights extracted'],
        'tasks': tasks or ['No actionable tasks identified'],
        'relevance_score': relevance,
    }


# =============================================================================
# MAIN EXTRACTION FUNCTION
# =============================================================================

async def extract_article(url: str) -> ArticleResult:
    """
    Main article extraction function with tiered strategy.
    Tries FREE methods first, falls back to PAID only if necessary.
    """
    url = url.strip()
    url_hash = generate_url_hash(url)
    
    print(f"\n📰 Extracting article: {url}")
    print(f"   Hash: {url_hash}")
    
    # Try Strategy 1: Trafilatura (FREE)
    content, error = extract_with_trafilatura(url)
    source = ArticleSource.TRAFILATURA.value
    
    # Try Strategy 2: BeautifulSoup (FREE)
    if not content:
        print(f"   ⚠️ Trafilatura failed: {error}")
        content, error = extract_with_beautifulsoup(url)
        source = ArticleSource.BEAUTIFULSOUP.value
    
    # Try Strategy 3: Apify AI (PAID)
    if not content:
        print(f"   ⚠️ BeautifulSoup failed: {error}")
        content, error = extract_with_apify_ai(url)
        source = ArticleSource.AI_CONTENT_PROCESSOR.value
    
    # If all strategies failed
    if not content:
        return ArticleResult(
            url=url,
            url_hash=url_hash,
            title="Extraction Failed",
            author=None,
            publication_date=None,
            domain=urlparse(url).netloc,
            content_markdown="",
            content_text="",
            word_count=0,
            extraction_source=ArticleSource.FAILED.value,
            life_os_domain=LifeOSDomain.UNCATEGORIZED.value,
            life_os_summary="",
            key_insights=[],
            actionable_tasks=[],
            relevance_score=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=error
        )
    
    # Analyze for Life OS
    print(f"   ✅ Extracted with {source}")
    print(f"   📊 Analyzing for Life OS domains...")
    
    analysis = analyze_for_life_os(
        content['text'],
        content['title'],
        url,
        content
    )
    
    # Calculate word count
    word_count = len(content['text'].split())
    
    result = ArticleResult(
        url=url,
        url_hash=url_hash,
        title=content['title'],
        author=content.get('author'),
        publication_date=content.get('date'),
        domain=content['domain'],
        content_markdown=content['markdown'],
        content_text=content['text'],
        word_count=word_count,
        extraction_source=source,
        life_os_domain=analysis['domain'],
        life_os_summary=analysis['summary'],
        key_insights=analysis['insights'],
        actionable_tasks=analysis['tasks'],
        relevance_score=analysis['relevance_score'],
        timestamp=datetime.now(timezone.utc).isoformat(),
        metadata={
            'description': content.get('description'),
            'categories': content.get('categories', []),
            'tags': content.get('tags', []),
        }
    )
    
    print(f"   ✅ Analysis complete: {analysis['domain']} (relevance: {analysis['relevance_score']}/10)")
    
    return result


# =============================================================================
# SUPABASE INTEGRATION
# =============================================================================

async def save_to_supabase(result: ArticleResult) -> bool:
    """Save article result to Supabase"""
    try:
        from lib.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        if not supabase:
            print("❌ Supabase client not available")
            return False
        
        # Insert into articles table
        data = {
            'url': result.url,
            'url_hash': result.url_hash,
            'title': result.title,
            'author': result.author,
            'publication_date': result.publication_date,
            'domain': result.domain,
            'content_markdown': result.content_markdown,
            'content_text': result.content_text,
            'word_count': result.word_count,
            'extraction_source': result.extraction_source,
            'life_os_domain': result.life_os_domain,
            'life_os_summary': result.life_os_summary,
            'key_insights': result.key_insights,
            'actionable_tasks': result.actionable_tasks,
            'relevance_score': result.relevance_score,
            'metadata': result.metadata,
            'created_at': result.timestamp,
        }
        
        response = supabase.table('articles').upsert(
            data,
            on_conflict='url_hash'
        ).execute()
        
        print(f"✅ Saved to Supabase: {result.title}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save to Supabase: {str(e)}")
        return False


# =============================================================================
# LangGraph Node Function
# =============================================================================

async def article_parser_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for article parsing.
    Integrates with Life OS orchestrator.
    """
    url = state.get('url')
    if not url:
        return {**state, 'error': 'No URL provided'}
    
    # Extract article
    result = await extract_article(url)
    
    # Save to Supabase
    await save_to_supabase(result)
    
    # Return updated state
    return {
        **state,
        'article_result': asdict(result),
        'life_os_domain': result.life_os_domain,
        'relevance_score': result.relevance_score,
        'summary': result.life_os_summary,
    }


# =============================================================================
# CLI Testing Interface
# =============================================================================

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def test_extraction():
        if len(sys.argv) < 2:
            print("Usage: python article_parser_agent.py <url>")
            sys.exit(1)
        
        url = sys.argv[1]
        result = await extract_article(url)
        
        print("\n" + "="*80)
        print("EXTRACTION RESULT")
        print("="*80)
        print(f"Title: {result.title}")
        print(f"Author: {result.author}")
        print(f"Date: {result.publication_date}")
        print(f"Domain: {result.domain}")
        print(f"Words: {result.word_count}")
        print(f"Source: {result.extraction_source}")
        print(f"\nLife OS Domain: {result.life_os_domain}")
        print(f"Relevance: {result.relevance_score}/10")
        print(f"\nSummary:\n{result.life_os_summary}")
        print(f"\nKey Insights:")
        for i, insight in enumerate(result.key_insights, 1):
            print(f"  {i}. {insight}")
        print(f"\nActionable Tasks:")
        for i, task in enumerate(result.actionable_tasks, 1):
            print(f"  {i}. {task}")
        
        if result.error:
            print(f"\n❌ Error: {result.error}")
    
    asyncio.run(test_extraction())
