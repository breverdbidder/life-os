#!/usr/bin/env python3
"""
Merge API findings from multiple sources and deduplicate against existing library
"""

import argparse
import json
import re
from datetime import datetime

def load_json_file(filepath: str) -> dict:
    """Load JSON file safely"""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {"actors": [], "servers": [], "repos": []}

def extract_existing_urls(library_path: str) -> set:
    """Extract all URLs already in the API_MEGA_LIBRARY.md"""
    urls = set()
    
    try:
        with open(library_path, "r") as f:
            content = f.read()
            
        # Find all URLs in markdown links and tables
        url_patterns = [
            r'https?://[^\s\)\]]+',
            r'\(https?://[^\)]+\)',
            r'\[https?://[^\]]+\]'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Clean up the URL
                url = match.strip("()[]")
                urls.add(url)
    except Exception as e:
        print(f"Error reading library: {e}")
    
    return urls

def main():
    parser = argparse.ArgumentParser(description="Merge and deduplicate API findings")
    parser.add_argument("--apify", type=str, help="Apify scan results JSON")
    parser.add_argument("--mcp", type=str, help="MCP scan results JSON")
    parser.add_argument("--github", type=str, help="GitHub scan results JSON")
    parser.add_argument("--existing", type=str, required=True, help="Existing API_MEGA_LIBRARY.md")
    parser.add_argument("--output", type=str, required=True, help="Output JSON for new APIs")
    args = parser.parse_args()
    
    # Load existing URLs
    existing_urls = extract_existing_urls(args.existing)
    print(f"Found {len(existing_urls)} existing URLs in library")
    
    # Load scan results
    new_apis = []
    categories_updated = set()
    
    if args.apify:
        apify_data = load_json_file(args.apify)
        for actor in apify_data.get("actors", []):
            if actor.get("url") not in existing_urls:
                actor["type"] = "apify_actor"
                new_apis.append(actor)
                categories_updated.add(actor.get("category", "other"))
    
    if args.mcp:
        mcp_data = load_json_file(args.mcp)
        for server in mcp_data.get("servers", []):
            if server.get("url") not in existing_urls:
                server["type"] = "mcp_server"
                new_apis.append(server)
                categories_updated.add("mcp")
    
    if args.github:
        github_data = load_json_file(args.github)
        for repo in github_data.get("repos", []):
            if repo.get("url") not in existing_urls:
                repo["type"] = "github_repo"
                new_apis.append(repo)
                categories_updated.add(repo.get("category", "other"))
    
    # Sort by relevance (stars, runs, etc.)
    new_apis.sort(key=lambda x: x.get("stars", 0) + x.get("stats", {}).get("runs", 0), reverse=True)
    
    # Save results
    output_data = {
        "scan_date": datetime.now().isoformat(),
        "new_count": len(new_apis),
        "categories": list(categories_updated),
        "apis": new_apis
    }
    
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nNew APIs to add: {len(new_apis)}")
    print(f"Categories: {', '.join(categories_updated)}")
    
    # GitHub Actions outputs
    print(f"::set-output name=new_count::{len(new_apis)}")
    print(f"::set-output name=categories::{', '.join(categories_updated)}")

if __name__ == "__main__":
    main()
