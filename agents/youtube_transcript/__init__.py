"""
YouTube Transcript Agent - Life OS LangGraph Integration
=========================================================
FREE transcript extraction for any YouTube video.

Usage:
    from agents.youtube_transcript import extract_transcript, is_youtube_url
    
    # Check if URL is YouTube
    if is_youtube_url(user_message):
        result = extract_transcript(url, category="learning")
        print(result.transcript)
"""

from .youtube_transcript_agent_v3 import (
    extract_transcript,
    extract_video_id,
    is_youtube_url,
    extract_youtube_urls,
    get_video_type,
    TranscriptResult,
    TranscriptSource,
)

__all__ = [
    'extract_transcript',
    'extract_video_id',
    'is_youtube_url',
    'extract_youtube_urls',
    'get_video_type',
    'TranscriptResult',
    'TranscriptSource',
]

__version__ = '3.0.0'
