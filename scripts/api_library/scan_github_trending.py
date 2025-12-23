#!/usr/bin/env python3
"""
Scan GitHub trending repos and search for API-related projects
"""

import argparse
import json
import requests
from datetime import datetime, timedelta

GITHUB_API = "https://api.github.com"

# Topics we care about
RELEVANT_TOPICS = [
    "api", "mcp", "model-context-protocol",
    "scraper", "web-scraping", "automation",
    "real-estate", "ecommerce", "grocery",
    "langchain", "langgraph", "ai-agent"
]

def search_github_repos(topic: str, min_stars: int = 10, days_back: int = 90) -> list:
    """Search GitHub for repos with specific topic"""
    repos = []
    
    date_filter = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    try:
        response = requests.get(
            f"{GITHUB_API}/search/repositories",
            params={
                "q": f"topic:{topic} pushed:>{date_filter} stars:>={min_stars}",
                "sort": "stars",
                "order": "desc",
                "per_page": 30
            },
            headers={
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            for repo in data.get("items", []):
                repos.append({
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "url": repo.get("html_url"),
                    "description": (repo.get("description") or "")[:200],
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "updated": repo.get("updated_at"),
                    "source": "github_topic_search",
                    "search_topic": topic
                })
        elif response.status_code == 403:
            print(f"Rate limited. Skipping {topic}")
    except Exception as e:
        print(f"Error searching {topic}: {e}")
    
    return repos

def get_trending_repos() -> list:
    """Get trending repos from GitHub (unofficial)"""
    repos = []
    
    # GitHub doesn't have official trending API, use search as proxy
    queries = [
        "mcp server created:>2024-06-01",
        "api integration stars:>50 pushed:>2024-01-01",
        "web scraper stars:>100 pushed:>2024-01-01"
    ]
    
    for query in queries:
        try:
            response = requests.get(
                f"{GITHUB_API}/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 20
                },
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                for repo in data.get("items", []):
                    repos.append({
                        "name": repo.get("name"),
                        "full_name": repo.get("full_name"),
                        "url": repo.get("html_url"),
                        "description": (repo.get("description") or "")[:200],
                        "stars": repo.get("stargazers_count", 0),
                        "language": repo.get("language"),
                        "updated": repo.get("updated_at"),
                        "source": "github_trending"
                    })
        except Exception as e:
            print(f"Error with query '{query}': {e}")
    
    return repos

def main():
    parser = argparse.ArgumentParser(description="Scan GitHub for trending API repos")
    parser.add_argument("--topics", type=str, default="all", help="Comma-separated topics")
    parser.add_argument("--output", type=str, required=True, help="Output JSON file")
    parser.add_argument("--min-stars", type=int, default=10, help="Minimum stars")
    args = parser.parse_args()
    
    all_repos = []
    
    # Search by topics
    topics = RELEVANT_TOPICS if args.topics == "all" else args.topics.split(",")
    
    for topic in topics:
        print(f"Searching topic: {topic}")
        repos = search_github_repos(topic, args.min_stars)
        all_repos.extend(repos)
        print(f"  Found {len(repos)} repos")
    
    # Get trending
    print("Fetching trending repos...")
    trending = get_trending_repos()
    all_repos.extend(trending)
    print(f"  Found {len(trending)} trending repos")
    
    # Deduplicate
    seen = set()
    unique_repos = []
    for repo in all_repos:
        url = repo.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique_repos.append(repo)
    
    # Sort by stars
    unique_repos.sort(key=lambda x: x.get("stars", 0), reverse=True)
    
    # Save results
    with open(args.output, "w") as f:
        json.dump({
            "scan_date": datetime.now().isoformat(),
            "total_found": len(unique_repos),
            "repos": unique_repos
        }, f, indent=2)
    
    print(f"\nTotal: {len(unique_repos)} repos saved to {args.output}")
    print(f"::set-output name=count::{len(unique_repos)}")

if __name__ == "__main__":
    main()
