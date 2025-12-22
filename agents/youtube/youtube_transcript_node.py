"""
YouTube Transcript LangGraph Node
Production V7 - Apify Fallback Strategy
"""
import os
import re
import json
import httpx
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class YouTubeTranscriptNode:
    """LangGraph node for YouTube transcript extraction"""
    
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
        self.supabase_key = os.environ.get('SUPABASE_KEY', '')
        self.apify_token = os.environ.get('APIFY_API_TOKEN', '')
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from any YouTube URL format"""
        patterns = [
            r'shorts/([a-zA-Z0-9_-]{11})',
            r'(?:v=|/v/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'embed/([a-zA-Z0-9_-]{11})',
            r'/live/([a-zA-Z0-9_-]{11})',
            r'watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        for p in patterns:
            m = re.search(p, url)
            if m:
                return m.group(1)
        return None
    
    async def trigger_workflow(self, video_url: str, category: str = 'learning') -> Dict[str, Any]:
        """Trigger the YouTube transcript workflow via GitHub API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.github.com/repos/breverdbidder/life-os/actions/workflows/youtube_transcript.yml/dispatches",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "ref": "main",
                    "inputs": {
                        "video_url": video_url,
                        "category": category
                    }
                },
                timeout=30
            )
            
            if response.status_code == 204:
                return {"status": "triggered", "video_url": video_url}
            else:
                return {"status": "error", "code": response.status_code}
    
    async def get_transcript_from_supabase(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve transcript from Supabase if already processed"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/insights",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}"
                },
                params={
                    "select": "*",
                    "metadata->>video_id": f"eq.{video_id}",
                    "limit": 1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]
        return None
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main LangGraph node processing function"""
        video_url = state.get('video_url', '')
        category = state.get('category', 'learning')
        
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return {**state, "error": "Invalid YouTube URL", "transcript": None}
        
        # Check if already processed
        existing = await self.get_transcript_from_supabase(video_id)
        if existing:
            return {
                **state,
                "video_id": video_id,
                "transcript": existing.get('content'),
                "title": existing.get('title'),
                "source": "supabase_cache",
                "cached": True
            }
        
        # Trigger workflow
        result = await self.trigger_workflow(video_url, category)
        
        return {
            **state,
            "video_id": video_id,
            "workflow_status": result.get('status'),
            "message": "Workflow triggered - transcript will be available in Supabase shortly"
        }


# LangGraph node function
async def youtube_transcript_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph compatible node function"""
    node = YouTubeTranscriptNode()
    return await node.process(state)
