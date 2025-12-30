"""
MCP Nodes for Life OS LangGraph Orchestration
Includes Playwright integration for JS-rendered sites
Date: 2025-12-30
"""

import json
import asyncio
from typing import Dict, Any


async def playwright_fetch(url: str) -> Dict[str, Any]:
    """
    Fetch JS-rendered content using Playwright MCP.
    Solves: React SPAs like PathForge that render via JavaScript.
    
    Args:
        url: Article URL to fetch
        
    Returns:
        {
            'html': str,  # Rendered HTML after JS execution
            'title': str,
            'url': str
        }
    """
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "playwright_navigate",
            "arguments": {"url": url}
        },
        "id": 1
    }
    
    try:
        proc = await asyncio.create_subprocess_exec(
            'npx', '@modelcontextprotocol/server-playwright',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate(json.dumps(mcp_request).encode())
        
        if proc.returncode != 0:
            raise Exception(f"MCP Playwright error: {stderr.decode()}")
        
        response = json.loads(stdout.decode())
        result = response.get('result', {})
        
        return {
            'html': result.get('content', ''),
            'title': result.get('title', 'Untitled'),
            'url': url
        }
        
    except Exception as e:
        print(f"⚠️  MCP Playwright error: {str(e)}")
        raise
