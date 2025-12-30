"""
MCP Nodes for Life OS LangGraph Orchestration
Includes Playwright integration for JS-rendered sites
"""

import json
import asyncio
from typing import Dict, Any


async def playwright_fetch(url: str) -> Dict[str, Any]:
    """
    Fetch JS-rendered content using Playwright MCP.
    Integrates with existing .mcp.json configuration.
    
    Args:
        url: Article URL to fetch (e.g., PathForge blog)
        
    Returns:
        {
            'html': str,  # Rendered HTML after JS execution
            'title': str,
            'url': str
        }
    """
    # Create MCP request for Playwright
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "playwright_navigate",
            "arguments": {
                "url": url
            }
        },
        "id": 1
    }
    
    try:
        # Call Playwright MCP server (uses .mcp.json config)
        proc = await asyncio.create_subprocess_exec(
            'npx', '@modelcontextprotocol/server-playwright',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate(json.dumps(mcp_request).encode())
        
        if proc.returncode != 0:
            raise Exception(f"MCP Playwright error: {stderr.decode()}")
        
        # Parse MCP response
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


# Optional: Alternative implementation if MCP client library available
async def playwright_fetch_with_client(url: str) -> Dict[str, Any]:
    """
    Alternative using MCP Python client library.
    Use this if you have mcp-client installed.
    """
    try:
        from mcp.client import MCPClient
        
        client = MCPClient()
        await client.connect_to_server("playwright")
        
        result = await client.call_tool(
            "playwright_navigate",
            url=url
        )
        
        return {
            'html': result.get('content', ''),
            'title': result.get('title', 'Untitled'),
            'url': url
        }
    except ImportError:
        # Fallback to subprocess method
        return await playwright_fetch(url)
