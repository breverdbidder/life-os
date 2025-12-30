"""
Article Parser Node for Life OS LangGraph
Parses JS-rendered articles and summarizes based on Life OS domains.

Uses Jina AI Reader (FREE) for article extraction.
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Life OS Domain Classifications
LIFE_OS_DOMAINS = {
    "BUSINESS": [
        "startup", "foreclosure", "real estate", "investment", "auction",
        "business", "revenue", "profit", "customer", "product", "market",
        "fundraising", "valuation", "SaaS", "AI", "agentic", "platform",
        "BidDeed", "Everest Capital", "insurance", "property"
    ],
    "MICHAEL": [
        "swimming", "D1", "recruiting", "college", "athlete", "training",
        "competition", "meet", "times", "swimmer", "keto", "diet", "nutrition",
        "kosher", "Shabbat", "SwimCloud", "University of Florida", "UF"
    ],
    "FAMILY": [
        "Mariam", "family", "Shabbat", "Orthodox", "Jewish", "holiday",
        "observance", "kosher", "synagogue", "community"
    ],
    "PERSONAL": [
        "ADHD", "productivity", "health", "learning", "focus", "sleep",
        "energy", "task management", "Life OS"
    ]
}


class ArticleParserNode:
    """
    LangGraph node for parsing articles and summarizing by Life OS domains.
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.jina_base = "https://r.jina.ai"
        
    async def parse_article(self, url: str) -> Dict[str, Any]:
        """
        Parse article using Jina AI Reader.
        
        Args:
            url: Article URL to parse
            
        Returns:
            Dict with parsed content
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Jina AI Reader converts any URL to LLM-friendly markdown
                response = await client.get(f"{self.jina_base}/{url}")
                
                if response.status_code == 200:
                    markdown_content = response.text
                    
                    # Check if content is actually valid
                    if not markdown_content or len(markdown_content.strip()) < 100:
                        return {
                            "success": False,
                            "url": url,
                            "error": "Empty or invalid content returned",
                            "parser": "jina_ai_reader"
                        }
                    
                    return {
                        "success": True,
                        "url": url,
                        "content": markdown_content,
                        "parsed_at": datetime.utcnow().isoformat(),
                        "parser": "jina_ai_reader",
                        "word_count": len(markdown_content.split())
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP {response.status_code}: {response.text[:200]}",
                        "parser": "jina_ai_reader"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "parser": "jina_ai_reader"
            }
    
    def classify_domain(self, content: str) -> Dict[str, float]:
        """
        Classify content by Life OS domain using keyword matching.
        
        Args:
            content: Article content
            
        Returns:
            Dict with domain scores
        """
        content_lower = content.lower()
        scores = {}
        
        for domain, keywords in LIFE_OS_DOMAINS.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            scores[domain] = matches / len(keywords)  # Normalize
        
        return scores
    
    def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """
        Extract key points from content (simple sentence extraction).
        
        Args:
            content: Article content
            max_points: Maximum points to extract
            
        Returns:
            List of key sentences
        """
        # Split into sentences
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 50]
        
        # Prioritize sentences with numbers, quotes, or key phrases
        priority_phrases = ['validation', 'market', 'customer', 'research', 
                          'strategy', 'approach', 'framework', 'method']
        
        scored = []
        for sent in sentences:
            score = sum(1 for phrase in priority_phrases if phrase in sent.lower())
            score += len([w for w in sent.split() if w.isupper()]) * 0.5  # Acronyms
            scored.append((score, sent))
        
        # Get top sentences
        scored.sort(reverse=True)
        return [sent for _, sent in scored[:max_points]]
    
    def generate_summary(self, content: str, domain_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate domain-specific summary.
        
        Args:
            content: Article content
            domain_scores: Domain classification scores
            
        Returns:
            Summary dict with domain-specific insights
        """
        # Determine primary domains (score > 0.1)
        primary_domains = [d for d, s in domain_scores.items() if s > 0.1]
        
        # Extract key points
        key_points = self.extract_key_points(content)
        
        # Generate domain-specific insights
        insights = {}
        
        if "BUSINESS" in primary_domains:
            business_keywords = ["validation", "market", "customer", "revenue", 
                               "product", "startup", "founder"]
            business_sentences = [s for s in content.split('.') 
                                if any(k in s.lower() for k in business_keywords)]
            insights["BUSINESS"] = {
                "relevance": "HIGH",
                "key_concepts": business_keywords,
                "actionable_items": business_sentences[:3]
            }
        
        if "MICHAEL" in primary_domains:
            insights["MICHAEL"] = {
                "relevance": "MEDIUM",
                "connection": "Training/discipline principles applicable"
            }
        
        return {
            "primary_domains": primary_domains,
            "key_points": key_points,
            "domain_insights": insights,
            "word_count": len(content.split()),
            "reading_time_minutes": len(content.split()) / 200  # Avg reading speed
        }
    
    async def process_article(self, url: str) -> Dict[str, Any]:
        """
        Complete article processing pipeline.
        
        Args:
            url: Article URL
            
        Returns:
            Complete processing result
        """
        # Parse article
        parse_result = await self.parse_article(url)
        
        if not parse_result["success"]:
            return parse_result
        
        # Classify and summarize
        content = parse_result["content"]
        domain_scores = self.classify_domain(content)
        summary = self.generate_summary(content, domain_scores)
        
        # Combine results
        return {
            "success": True,
            "url": url,
            "parsed_at": parse_result["parsed_at"],
            "parser": "jina_ai_reader",
            "content": content,
            "domain_scores": domain_scores,
            "summary": summary,
            "metadata": {
                "word_count": parse_result["word_count"],
                "reading_time": summary["reading_time_minutes"]
            }
        }
    
    async def store_to_supabase(self, result: Dict[str, Any]) -> bool:
        """
        Store parsed article to Supabase.
        
        Args:
            result: Processing result
            
        Returns:
            Success boolean
        """
        if not self.supabase_url or not self.supabase_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/parsed_articles",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "url": result["url"],
                        "content": result["content"],
                        "domain_scores": result["domain_scores"],
                        "summary": result["summary"],
                        "parsed_at": result["parsed_at"],
                        "metadata": result["metadata"]
                    }
                )
                
                return response.status_code in [200, 201]
                
        except Exception as e:
            print(f"Supabase storage error: {e}")
            return False


# LangGraph Node Function
async def article_parser_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node wrapper for article parsing.
    
    Expected state keys:
        - article_url: URL to parse
        
    Returns updated state with:
        - parsed_article: Processing result
        - next_action: "summarize" or "error"
    """
    parser = ArticleParserNode()
    
    url = state.get("article_url")
    if not url:
        return {
            **state,
            "error": "No article_url provided",
            "next_action": "error"
        }
    
    # Process article
    result = await parser.process_article(url)
    
    # Store to Supabase
    if result["success"]:
        await parser.store_to_supabase(result)
    
    return {
        **state,
        "parsed_article": result,
        "next_action": "summarize" if result["success"] else "error"
    }


# CLI Interface
if __name__ == "__main__":
    import asyncio
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python article_parser_node.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    async def main():
        parser = ArticleParserNode()
        result = await parser.process_article(url)
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())
