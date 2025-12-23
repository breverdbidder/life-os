#!/usr/bin/env python3
"""Discover new MCP servers from multiple sources."""
import httpx
import json
import os
import base64
from datetime import datetime

MCP_SOURCES = [
    {"name": "awesome-mcp-servers", "url": "https://api.github.com/repos/punkpeye/awesome-mcp-servers/contents/README.md", "type": "github_readme"}
]

RELEVANT_CATEGORIES = ["real-estate", "property", "shopping", "grocery", "ecommerce", "finance", "calendar", "ai", "database", "scraping"]
KNOWN_SERVERS = {"instacart", "kroger", "amazon-shopping", "google-drive", "slack", "notion", "github", "filesystem"}

def fetch_github_readme(url):
    headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}"}
    try:
        resp = httpx.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            return []
        content = base64.b64decode(resp.json()["content"]).decode("utf-8")
        servers = []
        for line in content.split("\n"):
            if line.strip().startswith("- [") and "](http" in line:
                try:
                    name = line[line.index("[")+1:line.index("]")].lower().replace(" ", "-")
                    url_start = line.index("](") + 2
                    url_end = line.index(")", url_start)
                    url = line[url_start:url_end]
                    desc = line[url_end+1:].strip(" -")[:200]
                    if name not in KNOWN_SERVERS and any(c in name.lower() or c in desc.lower() for c in RELEVANT_CATEGORIES):
                        servers.append({"name": name, "url": url, "description": desc, "source": "awesome-mcp-servers", "discovered": datetime.now().isoformat()})
                except:
                    pass
        return servers
    except:
        return []

def discover_new_mcp_servers():
    all_servers = []
    for src in MCP_SOURCES:
        if src["type"] == "github_readme":
            all_servers.extend(fetch_github_readme(src["url"]))
    seen = set()
    return [s for s in all_servers if s["name"] not in seen and not seen.add(s["name"])]

if __name__ == "__main__":
    print(json.dumps(discover_new_mcp_servers(), indent=2))
