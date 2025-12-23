#!/usr/bin/env python3
"""
Scan MCP Server registries for new servers
Sources: Glama, PulseMCP, MCP Market, GitHub awesome-mcp-servers
"""

import argparse
import json
import re
import requests
from datetime import datetime

MCP_SOURCES = {
    "glama": {
        "url": "https://glama.ai/mcp/servers",
        "api": "https://glama.ai/api/mcp/servers"
    },
    "pulsemcp": {
        "url": "https://www.pulsemcp.com/servers",
        "api": None  # Requires scraping
    },
    "mcpmarket": {
        "url": "https://mcpmarket.com",
        "api": None
    },
    "github": {
        "url": "https://github.com/punkpeye/awesome-mcp-servers",
        "raw": "https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/README.md"
    }
}

# Categories we prioritize
PRIORITY_CATEGORIES = [
    "e-commerce", "ecommerce", "shopping", "grocery",
    "real-estate", "property",
    "automation", "workflow",
    "database", "supabase", "postgresql",
    "google", "drive", "calendar",
    "ai", "llm", "agent"
]

def fetch_github_awesome_list() -> list:
    """Parse awesome-mcp-servers README for MCP servers"""
    servers = []
    
    try:
        response = requests.get(MCP_SOURCES["github"]["raw"])
        if response.status_code == 200:
            content = response.text
            
            # Find markdown links: [name](url) - description
            pattern = r'\[([^\]]+)\]\(([^)]+)\)\s*[-–]\s*(.+?)(?=\n|$)'
            matches = re.findall(pattern, content)
            
            for name, url, description in matches:
                if "github.com" in url or "npmjs.com" in url:
                    # Check if relevant to our categories
                    text_lower = (name + description).lower()
                    for cat in PRIORITY_CATEGORIES:
                        if cat in text_lower:
                            servers.append({
                                "name": name,
                                "url": url,
                                "description": description[:200],
                                "source": "github_awesome",
                                "category": cat
                            })
                            break
    except Exception as e:
        print(f"Error fetching GitHub awesome list: {e}")
    
    return servers

def fetch_glama_servers() -> list:
    """Fetch from Glama MCP registry"""
    servers = []
    
    try:
        # Try API first, fall back to scraping
        response = requests.get(
            "https://glama.ai/api/mcp/servers",
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            for server in data.get("servers", []):
                servers.append({
                    "name": server.get("name"),
                    "url": server.get("url") or server.get("github"),
                    "description": server.get("description", "")[:200],
                    "source": "glama",
                    "category": server.get("category", "other")
                })
    except Exception as e:
        print(f"Error fetching Glama: {e}")
    
    return servers

def search_github_mcp_repos() -> list:
    """Search GitHub for new MCP server repos"""
    servers = []
    
    search_queries = [
        "mcp server in:name,description created:>2024-01-01",
        "model context protocol server in:readme created:>2024-01-01",
        "fastmcp in:name,description"
    ]
    
    for query in search_queries:
        try:
            response = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": 30
                },
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                for repo in data.get("items", []):
                    # Filter by stars
                    if repo.get("stargazers_count", 0) >= 5:
                        servers.append({
                            "name": repo.get("name"),
                            "url": repo.get("html_url"),
                            "description": (repo.get("description") or "")[:200],
                            "source": "github_search",
                            "stars": repo.get("stargazers_count"),
                            "updated": repo.get("updated_at")
                        })
        except Exception as e:
            print(f"Error searching GitHub: {e}")
    
    return servers

def main():
    parser = argparse.ArgumentParser(description="Scan MCP registries for new servers")
    parser.add_argument("--sources", type=str, default="all", help="Comma-separated sources")
    parser.add_argument("--output", type=str, required=True, help="Output JSON file")
    args = parser.parse_args()
    
    all_servers = []
    
    # Fetch from each source
    print("Scanning GitHub awesome-mcp-servers...")
    all_servers.extend(fetch_github_awesome_list())
    
    print("Scanning Glama registry...")
    all_servers.extend(fetch_glama_servers())
    
    print("Searching GitHub for MCP repos...")
    all_servers.extend(search_github_mcp_repos())
    
    # Deduplicate by URL
    seen = set()
    unique_servers = []
    for server in all_servers:
        url = server.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique_servers.append(server)
    
    # Sort by stars if available
    unique_servers.sort(key=lambda x: x.get("stars", 0), reverse=True)
    
    # Save results
    with open(args.output, "w") as f:
        json.dump({
            "scan_date": datetime.now().isoformat(),
            "total_found": len(unique_servers),
            "servers": unique_servers
        }, f, indent=2)
    
    print(f"\nTotal: {len(unique_servers)} MCP servers saved to {args.output}")
    print(f"::set-output name=count::{len(unique_servers)}")

if __name__ == "__main__":
    main()
