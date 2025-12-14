"""
Hybrid News Aggregator & Viral Post Creator
BidDeed.AI + Life OS Integration

Aggregates news from:
- AI/ML/Tech (Life OS learning)
- Real Estate Tech/PropTech (BidDeed.AI marketing)
- Foreclosure/Distressed Properties (BidDeed.AI core)
- Web Scraping/Automation (Technical learning)

Creates viral social media posts and logs insights to Supabase.
"""

import feedparser
import requests
from datetime import datetime, timezone
import json
import time
from typing import List, Dict, Optional
import os
from dataclasses import dataclass, asdict
import re
from urllib.parse import urlparse

@dataclass
class Article:
    title: str
    link: str
    published: str
    summary: str
    source: str
    category: str  # AI_ML, REAL_ESTATE, FORECLOSURE, SCRAPING, PROPTECH

class RSSFeedCollector:
    """Collects articles from categorized RSS feeds"""
    
    FEEDS = {
        # AI/ML News (Life OS Learning)
        'AI_ML': {
            'TechCrunch AI': 'https://techcrunch.com/tag/artificial-intelligence/feed/',
            'VentureBeat AI': 'https://venturebeat.com/category/ai/feed/',
            'MIT Tech Review': 'https://www.technologyreview.com/topic/artificial-intelligence/feed',
            'The Verge AI': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
            'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/technology-lab',
            'Wired AI': 'https://www.wired.com/feed/tag/ai/latest/rss',
        },
        # Real Estate Tech / PropTech (BidDeed.AI Marketing)
        'PROPTECH': {
            'Inman': 'https://www.inman.com/feed/',
            'HousingWire': 'https://www.housingwire.com/feed/',
            'The Real Deal': 'https://therealdeal.com/feed/',
            'GlobeSt': 'https://www.globest.com/feed/',
            'Propmodo': 'https://www.propmodo.com/feed/',
        },
        # Foreclosure & Distressed (BidDeed.AI Core)
        'FORECLOSURE': {
            'DS News': 'https://dsnews.com/feed/',
            'National Mortgage News': 'https://www.nationalmortgagenews.com/feed',
            'Mortgage Orb': 'https://mortgageorb.com/feed/',
            'RealtyTrac Blog': 'https://www.realtytrac.com/blog/feed/',
        },
        # Web Scraping & Automation (Technical)
        'SCRAPING': {
            'Hacker News': 'https://hnrss.org/frontpage',
            'Dev.to Python': 'https://dev.to/feed/tag/python',
            'Dev.to Automation': 'https://dev.to/feed/tag/automation',
            'Reddit Python': 'https://www.reddit.com/r/Python/.rss',
        },
    }
    
    # Keywords to filter relevant articles
    RELEVANCE_KEYWORDS = {
        'AI_ML': ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 'claude', 
                  'neural', 'deep learning', 'automation', 'chatbot', 'generative'],
        'PROPTECH': ['proptech', 'real estate tech', 'realestate', 'property technology',
                     'mls', 'zillow', 'redfin', 'realtor', 'housing market'],
        'FORECLOSURE': ['foreclosure', 'distressed', 'auction', 'reo', 'short sale', 
                        'default', 'delinquent', 'mortgage crisis', 'housing crisis'],
        'SCRAPING': ['scraping', 'selenium', 'beautifulsoup', 'automation', 'bot', 
                     'crawler', 'data extraction', 'web scraping'],
    }

    def fetch_feed(self, feed_url: str, source_name: str, category: str) -> List[Article]:
        """Fetch articles from a single RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:10]:  # Get latest 10 per source
                title = entry.get('title', '')
                summary = entry.get('summary', '')[:500]
                
                # Check relevance
                if self._is_relevant(title, summary, category):
                    article = Article(
                        title=title,
                        link=entry.get('link', ''),
                        published=entry.get('published', datetime.now().isoformat()),
                        summary=self._clean_html(summary),
                        source=source_name,
                        category=category
                    )
                    articles.append(article)
            
            print(f"✓ {source_name}: {len(articles)} relevant articles")
            return articles
        except Exception as e:
            print(f"✗ {source_name}: {str(e)[:50]}")
            return []
    
    def _is_relevant(self, title: str, summary: str, category: str) -> bool:
        """Check if article matches category keywords"""
        text = f"{title} {summary}".lower()
        keywords = self.RELEVANCE_KEYWORDS.get(category, [])
        
        # For AI_ML and SCRAPING, require keyword match
        # For PROPTECH and FORECLOSURE, accept all from those feeds
        if category in ['PROPTECH', 'FORECLOSURE']:
            return True
        
        return any(kw in text for kw in keywords)
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def collect_all(self) -> Dict[str, List[Article]]:
        """Collect articles from all RSS feeds, organized by category"""
        results = {cat: [] for cat in self.FEEDS.keys()}
        
        for category, feeds in self.FEEDS.items():
            print(f"\n📰 Collecting {category}...")
            for source_name, feed_url in feeds.items():
                articles = self.fetch_feed(feed_url, source_name, category)
                results[category].extend(articles)
                time.sleep(0.5)  # Rate limiting
        
        return results
    
    def collect_category(self, category: str) -> List[Article]:
        """Collect articles from a specific category only"""
        if category not in self.FEEDS:
            return []
        
        articles = []
        for source_name, feed_url in self.FEEDS[category].items():
            articles.extend(self.fetch_feed(feed_url, source_name, category))
            time.sleep(0.5)
        
        return articles


class ArticleAggregator:
    """Aggregates and deduplicates articles"""
    
    def aggregate(self, articles_by_category: Dict[str, List[Article]]) -> Dict:
        """Aggregate articles and extract key information"""
        
        all_articles = []
        for category, articles in articles_by_category.items():
            all_articles.extend(articles)
        
        # Deduplicate by title similarity
        seen_titles = set()
        unique_articles = []
        
        for article in all_articles:
            title_key = article.title.lower()[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        # Sort by category priority for BidDeed.AI
        priority_order = ['FORECLOSURE', 'PROPTECH', 'AI_ML', 'SCRAPING']
        unique_articles.sort(key=lambda a: priority_order.index(a.category) if a.category in priority_order else 99)
        
        aggregated = {
            'total_articles': len(unique_articles),
            'by_category': {cat: len([a for a in unique_articles if a.category == cat]) 
                          for cat in articles_by_category.keys()},
            'articles': [asdict(a) for a in unique_articles],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return aggregated


class GeminiPostCreator:
    """Creates viral social media posts using Google Gemini"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = 'gemini-2.5-flash'
    
    def create_biddeed_prompt(self, aggregated_data: Dict) -> str:
        """Create prompt for BidDeed.AI focused viral post"""
        
        # Separate articles by focus
        foreclosure_articles = [a for a in aggregated_data['articles'] if a['category'] == 'FORECLOSURE'][:5]
        proptech_articles = [a for a in aggregated_data['articles'] if a['category'] == 'PROPTECH'][:5]
        ai_articles = [a for a in aggregated_data['articles'] if a['category'] == 'AI_ML'][:5]
        
        foreclosure_text = "\n".join([f"- {a['title']}" for a in foreclosure_articles]) or "No foreclosure news today"
        proptech_text = "\n".join([f"- {a['title']}" for a in proptech_articles]) or "No proptech news today"
        ai_text = "\n".join([f"- {a['title']}" for a in ai_articles]) or "No AI news today"
        
        prompt = f"""You are a content strategist for BidDeed.AI, an AI-powered foreclosure auction intelligence platform.

FORECLOSURE & DISTRESSED PROPERTY NEWS:
{foreclosure_text}

PROPTECH & REAL ESTATE TECH NEWS:
{proptech_text}

AI & MACHINE LEARNING NEWS:
{ai_text}

Create 3 different viral social media posts:

1. LINKEDIN POST (Professional, thought leadership)
- Hook: Start with a surprising stat or bold claim about AI in real estate
- Body: Connect the news to how AI is transforming foreclosure investing
- CTA: Subtle mention of staying ahead with AI-powered tools
- Length: 150-200 words
- Include 3-5 relevant hashtags

2. TWITTER/X POST (Punchy, engagement-focused)
- Hook that stops the scroll
- Key insight in 1-2 sentences
- Under 280 characters
- 2-3 hashtags

3. INSTAGRAM CAPTION (Story-driven, relatable)
- Start with emoji hook
- Share a mini-story or insight
- End with question to drive comments
- 5-10 hashtags at end

Format as JSON:
{{
  "linkedin": {{
    "hook": "...",
    "body": "...",
    "cta": "...",
    "hashtags": ["#...", "..."],
    "full_post": "..."
  }},
  "twitter": {{
    "post": "...",
    "hashtags": ["..."]
  }},
  "instagram": {{
    "caption": "...",
    "hashtags": ["..."]
  }},
  "key_insight": "One sentence summary of today's most important trend",
  "category_focus": "FORECLOSURE or PROPTECH or AI_ML"
}}
"""
        return prompt
    
    def create_lifeos_prompt(self, aggregated_data: Dict) -> str:
        """Create prompt for Life OS learning summary"""
        
        ai_articles = [a for a in aggregated_data['articles'] if a['category'] in ['AI_ML', 'SCRAPING']][:10]
        
        articles_text = "\n".join([f"- {a['title']} ({a['source']})\n  {a['summary'][:150]}..." 
                                   for a in ai_articles])
        
        prompt = f"""Summarize today's AI/ML and automation news for a developer building AI-powered real estate tools.

TODAY'S ARTICLES:
{articles_text}

Create a learning digest:

1. TOP 3 INSIGHTS - What's most relevant for someone building agentic AI systems?
2. TOOLS/TECHNIQUES - Any new tools, libraries, or techniques mentioned?
3. INDUSTRY TRENDS - What patterns are emerging?
4. ACTION ITEMS - What should I explore or implement?

Format as JSON:
{{
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "top_insights": ["...", "...", "..."],
  "tools_mentioned": ["..."],
  "industry_trends": ["..."],
  "action_items": ["..."],
  "one_line_summary": "...",
  "relevance_to_biddeed": "How this connects to foreclosure AI platform"
}}
"""
        return prompt
    
    def generate_post(self, aggregated_data: Dict, post_type: str = 'biddeed') -> Dict:
        """Generate post using Gemini API"""
        
        if not self.api_key:
            print("⚠ No GOOGLE_API_KEY - using fallback")
            return self._generate_fallback(aggregated_data, post_type)
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            
            prompt = self.create_biddeed_prompt(aggregated_data) if post_type == 'biddeed' else self.create_lifeos_prompt(aggregated_data)
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2000,
                    "responseMimeType": "application/json"
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON response
                try:
                    # Clean potential markdown code blocks
                    text = re.sub(r'^```json\s*', '', text)
                    text = re.sub(r'\s*```$', '', text)
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {'raw_response': text, 'parse_error': True}
            else:
                print(f"✗ Gemini API error: {response.status_code}")
                return self._generate_fallback(aggregated_data, post_type)
                
        except Exception as e:
            print(f"✗ Gemini error: {str(e)}")
            return self._generate_fallback(aggregated_data, post_type)
    
    def _generate_fallback(self, aggregated_data: Dict, post_type: str) -> Dict:
        """Generate simple post without AI"""
        
        top_article = aggregated_data['articles'][0] if aggregated_data['articles'] else None
        
        if not top_article:
            return {'error': 'No articles to process'}
        
        if post_type == 'biddeed':
            return {
                'linkedin': {
                    'hook': f"🏠 Today in Real Estate AI",
                    'body': f"Latest: {top_article['title']}",
                    'cta': "AI is transforming how investors analyze foreclosure auctions.",
                    'hashtags': ['#RealEstateAI', '#Foreclosure', '#PropTech', '#BidDeedAI'],
                    'full_post': f"🏠 Today in Real Estate AI\n\n{top_article['title']}\n\nAI is transforming how investors analyze foreclosure auctions.\n\n#RealEstateAI #Foreclosure #PropTech"
                },
                'twitter': {
                    'post': f"🏠 {top_article['title'][:200]}\n\n#RealEstateAI #Foreclosure",
                    'hashtags': ['#RealEstateAI', '#Foreclosure']
                },
                'instagram': {
                    'caption': f"🏠 {top_article['title']}\n\nWhat do you think about AI in real estate?",
                    'hashtags': ['#realestate', '#ai', '#foreclosure', '#investing', '#proptech']
                },
                'key_insight': top_article['title'],
                'category_focus': top_article['category']
            }
        else:
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'top_insights': [top_article['title']],
                'tools_mentioned': [],
                'industry_trends': [],
                'action_items': ['Review this article'],
                'one_line_summary': top_article['title'],
                'relevance_to_biddeed': 'Potential application to foreclosure analysis'
            }


class TelegramNotifier:
    """Sends notifications via Telegram"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    def send(self, message: str) -> bool:
        """Send message to Telegram"""
        if not self.token or not self.chat_id:
            print("⚠ Telegram not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✓ Telegram notification sent")
                return True
            else:
                print(f"✗ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Telegram error: {str(e)}")
            return False
    
    def format_biddeed_summary(self, aggregated: Dict, posts: Dict) -> str:
        """Format BidDeed.AI summary for Telegram"""
        
        msg = f"""<b>🏠 BidDeed.AI Daily Digest</b>
<i>{datetime.now().strftime('%B %d, %Y')}</i>

<b>📊 Articles Collected:</b>
• Foreclosure: {aggregated['by_category'].get('FORECLOSURE', 0)}
• PropTech: {aggregated['by_category'].get('PROPTECH', 0)}
• AI/ML: {aggregated['by_category'].get('AI_ML', 0)}
• Scraping: {aggregated['by_category'].get('SCRAPING', 0)}

<b>💡 Key Insight:</b>
{posts.get('key_insight', 'No insight generated')}

<b>📱 LinkedIn Post Ready:</b>
{posts.get('linkedin', {}).get('hook', 'N/A')[:100]}...

<b>🐦 Twitter Post Ready:</b>
{posts.get('twitter', {}).get('post', 'N/A')[:100]}...

<i>Posts saved to Supabase ✓</i>
"""
        return msg
    
    def format_lifeos_summary(self, digest: Dict) -> str:
        """Format Life OS learning summary for Telegram"""
        
        insights = digest.get('top_insights', [])[:3]
        insights_text = "\n".join([f"• {i}" for i in insights]) or "No insights"
        
        msg = f"""<b>🧠 Life OS Learning Digest</b>
<i>{digest.get('date', datetime.now().strftime('%Y-%m-%d'))}</i>

<b>🔝 Top Insights:</b>
{insights_text}

<b>🛠 Tools Mentioned:</b>
{', '.join(digest.get('tools_mentioned', [])[:5]) or 'None'}

<b>📈 Trends:</b>
{', '.join(digest.get('industry_trends', [])[:3]) or 'None'}

<b>✅ Action Items:</b>
{chr(10).join(['• ' + a for a in digest.get('action_items', [])[:3]]) or 'None'}

<b>🎯 BidDeed Relevance:</b>
{digest.get('relevance_to_biddeed', 'N/A')}
"""
        return msg


class SupabaseLogger:
    """Logs insights and posts to Supabase"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
        self.key = os.getenv('SUPABASE_KEY')
    
    def log_insight(self, category: str, content: Dict, source: str = 'hybrid_news_aggregator') -> bool:
        """Log insight to Supabase insights table"""
        
        if not self.key:
            print("⚠ SUPABASE_KEY not configured")
            return False
        
        try:
            url = f"{self.url}/rest/v1/insights"
            headers = {
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            
            payload = {
                "category": category,
                "content": json.dumps(content),
                "source": source,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"✓ Logged to Supabase: {category}")
                return True
            else:
                print(f"✗ Supabase error: {response.status_code} - {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"✗ Supabase error: {str(e)}")
            return False


class HybridNewsWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self):
        self.collector = RSSFeedCollector()
        self.aggregator = ArticleAggregator()
        self.post_creator = GeminiPostCreator()
        self.telegram = TelegramNotifier()
        self.supabase = SupabaseLogger()
    
    def run_full(self) -> Dict:
        """Execute complete workflow for both BidDeed.AI and Life OS"""
        
        print("\n" + "="*60)
        print(f"🚀 Hybrid News Aggregator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Step 1: Collect all articles
        print("\n📰 STEP 1: Collecting articles from all feeds...")
        articles_by_category = self.collector.collect_all()
        
        total = sum(len(arts) for arts in articles_by_category.values())
        print(f"\n✓ Total articles collected: {total}")
        
        if total == 0:
            return {'error': 'No articles collected', 'timestamp': datetime.now().isoformat()}
        
        # Step 2: Aggregate and deduplicate
        print("\n📊 STEP 2: Aggregating articles...")
        aggregated = self.aggregator.aggregate(articles_by_category)
        print(f"✓ Unique articles: {aggregated['total_articles']}")
        
        # Step 3: Generate BidDeed.AI viral posts
        print("\n✨ STEP 3: Generating BidDeed.AI viral posts...")
        biddeed_posts = self.post_creator.generate_post(aggregated, 'biddeed')
        print(f"✓ Generated posts for LinkedIn, Twitter, Instagram")
        
        # Step 4: Generate Life OS learning digest
        print("\n🧠 STEP 4: Generating Life OS learning digest...")
        lifeos_digest = self.post_creator.generate_post(aggregated, 'lifeos')
        print(f"✓ Generated learning digest")
        
        # Step 5: Log to Supabase
        print("\n💾 STEP 5: Logging to Supabase...")
        self.supabase.log_insight('biddeed_viral_posts', biddeed_posts, 'hybrid_news_aggregator')
        self.supabase.log_insight('learning', lifeos_digest, 'hybrid_news_aggregator')
        self.supabase.log_insight('news_aggregation', {
            'total_articles': aggregated['total_articles'],
            'by_category': aggregated['by_category'],
            'top_articles': aggregated['articles'][:10]
        }, 'hybrid_news_aggregator')
        
        # Step 6: Send Telegram notifications
        print("\n📱 STEP 6: Sending Telegram notifications...")
        self.telegram.send(self.telegram.format_biddeed_summary(aggregated, biddeed_posts))
        self.telegram.send(self.telegram.format_lifeos_summary(lifeos_digest))
        
        # Step 7: Save results
        print("\n💾 STEP 7: Saving results...")
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'aggregated': aggregated,
            'biddeed_posts': biddeed_posts,
            'lifeos_digest': lifeos_digest,
            'status': 'success'
        }
        
        # Save to file
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved to: {filename}")
        
        print("\n" + "="*60)
        print("✅ WORKFLOW COMPLETE!")
        print("="*60)
        
        return results
    
    def run_biddeed_only(self) -> Dict:
        """Run only BidDeed.AI focused aggregation"""
        
        print("\n🏠 BidDeed.AI News Aggregation")
        
        # Collect only relevant categories
        foreclosure = self.collector.collect_category('FORECLOSURE')
        proptech = self.collector.collect_category('PROPTECH')
        ai = self.collector.collect_category('AI_ML')
        
        articles_by_category = {
            'FORECLOSURE': foreclosure,
            'PROPTECH': proptech,
            'AI_ML': ai
        }
        
        aggregated = self.aggregator.aggregate(articles_by_category)
        posts = self.post_creator.generate_post(aggregated, 'biddeed')
        
        self.supabase.log_insight('biddeed_viral_posts', posts)
        self.telegram.send(self.telegram.format_biddeed_summary(aggregated, posts))
        
        return {'aggregated': aggregated, 'posts': posts}
    
    def run_lifeos_only(self) -> Dict:
        """Run only Life OS learning aggregation"""
        
        print("\n🧠 Life OS Learning Aggregation")
        
        # Collect learning-focused categories
        ai = self.collector.collect_category('AI_ML')
        scraping = self.collector.collect_category('SCRAPING')
        
        articles_by_category = {
            'AI_ML': ai,
            'SCRAPING': scraping
        }
        
        aggregated = self.aggregator.aggregate(articles_by_category)
        digest = self.post_creator.generate_post(aggregated, 'lifeos')
        
        self.supabase.log_insight('learning', digest)
        self.telegram.send(self.telegram.format_lifeos_summary(digest))
        
        return {'aggregated': aggregated, 'digest': digest}


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid News Aggregator')
    parser.add_argument('--mode', choices=['full', 'biddeed', 'lifeos'], 
                       default='full', help='Run mode')
    
    args = parser.parse_args()
    
    workflow = HybridNewsWorkflow()
    
    if args.mode == 'full':
        workflow.run_full()
    elif args.mode == 'biddeed':
        workflow.run_biddeed_only()
    elif args.mode == 'lifeos':
        workflow.run_lifeos_only()
