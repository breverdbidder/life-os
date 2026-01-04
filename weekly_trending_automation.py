#!/usr/bin/env python3
"""
GitHub Trending Weekly Automation Script
Fetches trending repositories and updates GITHUB_REPO_MEGA_LIBRARY.md

Schedule: Every Sunday 11 PM EST via GitHub Actions
"""

import requests
from datetime import datetime, timedelta
import json
import os

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"

# Categories to track
CATEGORIES = [
    "python",
    "typescript", 
    "javascript",
    "ai",
    "agents",
    "langgraph",
    "web-scraping"
]

def fetch_trending_repos(language=None, since="daily"):
    """
    Fetch trending repos from GitHub
    Uses Trendshift API as alternative to scraping github.com/trending
    """
    url = "https://trendshift.io/api/repos"
    params = {
        "language": language,
        "since": since
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching trending repos: {e}")
        return []

def analyze_repo_quality(repo_full_name):
    """
    Analyze repository quality using GitHub API
    Returns quality score (0-100)
    """
    if not GITHUB_TOKEN:
        return None
        
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{repo_full_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Quality scoring algorithm
        score = 0
        
        # Stars (max 30 points)
        stars = data.get('stargazers_count', 0)
        if stars > 10000:
            score += 30
        elif stars > 1000:
            score += 20
        elif stars > 100:
            score += 10
        
        # Activity (max 20 points)
        updated = datetime.fromisoformat(data.get('updated_at', '').replace('Z', '+00:00'))
        days_since_update = (datetime.now(updated.tzinfo) - updated).days
        if days_since_update < 7:
            score += 20
        elif days_since_update < 30:
            score += 15
        elif days_since_update < 90:
            score += 10
        
        # Documentation (max 15 points)
        if data.get('has_wiki'):
            score += 5
        if data.get('description'):
            score += 10
            
        # Community (max 15 points)
        if data.get('forks_count', 0) > 100:
            score += 10
        if data.get('open_issues_count', 0) < 50:
            score += 5
            
        # License (max 10 points)
        if data.get('license'):
            score += 10
            
        # Tests/CI (max 10 points)
        if data.get('has_pages'):  # Proxy for CI/CD setup
            score += 10
            
        return {
            'score': score,
            'stars': stars,
            'forks': data.get('forks_count', 0),
            'issues': data.get('open_issues_count', 0),
            'updated': data.get('updated_at'),
            'license': data.get('license', {}).get('name') if data.get('license') else None
        }
        
    except Exception as e:
        print(f"Error analyzing {repo_full_name}: {e}")
        return None

def categorize_repo(repo):
    """
    Categorize repository based on topics and description
    """
    topics = repo.get('topics', [])
    description = (repo.get('description') or '').lower()
    
    if any(term in topics or term in description for term in ['agent', 'langgraph', 'langchain', 'ai-agent']):
        return 'AI Agents'
    elif any(term in topics or term in description for term in ['scraper', 'scraping', 'crawler']):
        return 'Web Scraping'
    elif any(term in topics or term in description for term in ['llm', 'gpt', 'claude', 'ai']):
        return 'AI & ML'
    elif any(term in topics or term in description for term in ['real-estate', 'property']):
        return 'Real Estate'
    else:
        return 'Infrastructure'

def store_trending_data(repos_data):
    """
    Store trending data in Supabase
    """
    if not SUPABASE_KEY:
        print("No Supabase key - skipping storage")
        return
        
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/github_trending"
    
    for repo in repos_data:
        payload = {
            "repo_name": repo['name'],
            "category": repo['category'],
            "stars": repo['stars'],
            "trend": repo['trend'],
            "quality_score": repo.get('quality_score'),
            "discovered_at": datetime.now().isoformat(),
            "metadata": json.dumps(repo.get('metadata', {}))
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Stored: {repo['name']}")
        except Exception as e:
            print(f"❌ Error storing {repo['name']}: {e}")

def update_library_markdown(trending_repos):
    """
    Update GITHUB_REPO_MEGA_LIBRARY.md with new trending data
    """
    library_path = "/home/claude/GITHUB_REPO_MEGA_LIBRARY.md"
    
    try:
        with open(library_path, 'r') as f:
            content = f.read()
        
        # Find the trending section
        trending_section_start = content.find("## 📈 TOP TRENDING PROJECTS")
        trending_section_end = content.find("## 🎯 BIDDEED.AI PRIORITY QUEUE")
        
        if trending_section_start == -1 or trending_section_end == -1:
            print("Could not find trending section in markdown")
            return
            
        # Build new trending section
        new_section = f"""## 📈 TOP TRENDING PROJECTS ({datetime.now().strftime('%B %Y')})

### Agentic AI & Agents
"""
        
        # Group by category
        by_category = {}
        for repo in trending_repos:
            category = repo['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(repo)
        
        # Write categorized repos
        for category, repos in by_category.items():
            new_section += f"\n### {category}\n"
            for repo in repos[:5]:  # Top 5 per category
                quality = repo.get('quality_score', 'N/A')
                new_section += f"- **{repo['name']}**: {repo['stars']} stars, {repo['trend']} (Quality: {quality})\n"
        
        new_section += "\n"
        
        # Replace old section with new
        updated_content = (
            content[:trending_section_start] +
            new_section +
            content[trending_section_end:]
        )
        
        with open(library_path, 'w') as f:
            f.write(updated_content)
            
        print(f"✅ Updated {library_path}")
        
    except Exception as e:
        print(f"❌ Error updating markdown: {e}")

def send_notification(summary):
    """
    Send notification with trending summary
    Could integrate with Slack, email, etc.
    """
    print("\n" + "="*60)
    print("WEEKLY TRENDING UPDATE SUMMARY")
    print("="*60)
    print(summary)
    print("="*60 + "\n")

def main():
    """
    Main automation workflow
    """
    print(f"🚀 GitHub Trending Weekly Update - {datetime.now().isoformat()}")
    
    all_trending = []
    
    # Fetch trending for each category
    for category in CATEGORIES:
        print(f"\n📊 Fetching trending {category} repos...")
        repos = fetch_trending_repos(language=category, since="week")
        
        for repo_data in repos[:10]:  # Top 10 per category
            repo_name = repo_data.get('full_name')
            if not repo_name:
                continue
                
            print(f"  Analyzing {repo_name}...")
            
            # Analyze quality
            quality = analyze_repo_quality(repo_name)
            
            # Categorize
            category_name = categorize_repo(repo_data)
            
            trending_item = {
                'name': repo_data.get('name'),
                'full_name': repo_name,
                'category': category_name,
                'stars': f"{repo_data.get('stargazers_count', 0)/1000:.1f}K" if repo_data.get('stargazers_count', 0) > 1000 else str(repo_data.get('stargazers_count', 0)),
                'trend': f"+{repo_data.get('trend_count', 0)}",
                'quality_score': quality['score'] if quality else None,
                'metadata': quality
            }
            
            all_trending.append(trending_item)
    
    # Sort by quality score
    all_trending.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
    
    # Store in Supabase
    print("\n💾 Storing trending data...")
    store_trending_data(all_trending[:20])  # Top 20 overall
    
    # Update markdown file
    print("\n📝 Updating GITHUB_REPO_MEGA_LIBRARY.md...")
    update_library_markdown(all_trending[:20])
    
    # Send summary notification
    summary = f"""
Found {len(all_trending)} trending repositories this week.

Top 5 by Quality Score:
{chr(10).join([f"{i+1}. {r['name']} (Score: {r.get('quality_score', 'N/A')}, Category: {r['category']})" for i, r in enumerate(all_trending[:5])])}

High-quality finds (Score 80+):
{chr(10).join([f"- {r['name']} ({r['category']})" for r in all_trending if r.get('quality_score', 0) >= 80])}

Next update: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
"""
    send_notification(summary)
    
    print("\n✅ Weekly update complete!")

if __name__ == "__main__":
    main()
