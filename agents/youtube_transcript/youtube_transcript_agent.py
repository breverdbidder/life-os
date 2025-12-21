#!/usr/bin/env python3
"""
YOUTUBE TRANSCRIPTION AGENT - LIFE OS LANGGRAPH
================================================
Transcribes YouTube videos (shorts, regular, live) from URL.
Supports multiple transcription backends for reliability.

Author: Claude Sonnet 4.5 (AI Architect)
Owner: Ariel Shapira, Everest Capital USA
Created: December 21, 2025

Stack: yt-dlp + Whisper (FREE) | Apify (PAID fallback)
Repository: breverdbidder/life-os
"""

import os
import re
import json
import asyncio
import httpx
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import subprocess
import tempfile
import glob

# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")  # Optional paid fallback

# Apify Actors from API_MEGA_LIBRARY (paid backup options)
APIFY_ACTORS = {
    "youtube_transcript": "topaz_sharingan/youtube-transcript-scraper",
    "video_transcript": "invideoiq/video-transcript-scraper",  # Multi-platform
    "youtube_channel": "karamelo/youtube-full-channel-transcripts-extractor"
}

# ============================================================
# DATA STRUCTURES
# ============================================================

class TranscriptSource(str, Enum):
    YOUTUBE_CAPTIONS = "youtube_captions"  # Free - built-in captions
    WHISPER_LOCAL = "whisper_local"        # Free - OpenAI Whisper
    APIFY_TRANSCRIPT = "apify_transcript"  # Paid - Apify actors
    FAILED = "failed"

class VideoType(str, Enum):
    SHORT = "short"      # YouTube Shorts (< 60s)
    REGULAR = "regular"  # Standard YouTube video
    LIVE = "live"        # Ended livestream
    PLAYLIST = "playlist"

@dataclass
class VideoMetadata:
    """Video metadata from yt-dlp"""
    video_id: str
    url: str
    title: str = "Unknown"
    channel: str = "Unknown"
    duration_seconds: int = 0
    upload_date: str = ""
    view_count: int = 0
    video_type: str = "regular"
    thumbnail_url: str = ""
    
@dataclass
class TranscriptResult:
    """Complete transcript result"""
    video: VideoMetadata
    transcript: str = ""
    transcript_length: int = 0
    source: str = "none"
    language: str = "unknown"
    has_timestamps: bool = False
    segments: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    processing_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_id": self.video.video_id,
            "video_url": self.video.url,
            "title": self.video.title,
            "channel": self.video.channel,
            "duration_seconds": self.video.duration_seconds,
            "video_type": self.video.video_type,
            "transcript": self.transcript[:50000],  # Limit for storage
            "transcript_length": self.transcript_length,
            "source": self.source,
            "language": self.language,
            "has_timestamps": self.has_timestamps,
            "error": self.error,
            "processing_time_seconds": self.processing_time_seconds
        }

# ============================================================
# URL PARSER
# ============================================================

class YouTubeURLParser:
    """Parse and normalize YouTube URLs"""
    
    # Regex patterns for different YouTube URL formats
    PATTERNS = [
        # Standard watch URL
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        # Shorts URL
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        # Embed URL
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        # Live URL
        r'youtube\.com/live/([a-zA-Z0-9_-]{11})',
        # Mobile URL
        r'm\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    ]
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """Extract video ID from any YouTube URL format"""
        for pattern in cls.PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def detect_video_type(cls, url: str) -> VideoType:
        """Detect video type from URL"""
        if '/shorts/' in url:
            return VideoType.SHORT
        elif '/live/' in url:
            return VideoType.LIVE
        elif 'list=' in url:
            return VideoType.PLAYLIST
        return VideoType.REGULAR
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL to standard format"""
        video_id = cls.extract_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url

# ============================================================
# TRANSCRIPTION BACKENDS
# ============================================================

class YouTubeCaptionsBackend:
    """Extract YouTube's built-in captions (FREE)"""
    
    @staticmethod
    async def get_transcript(video_id: str) -> Optional[Dict]:
        """Try to get YouTube's auto-generated or manual captions"""
        try:
            # Use yt-dlp to extract subtitles
            cmd = [
                'yt-dlp',
                '--skip-download',
                '--write-auto-sub',
                '--write-sub',
                '--sub-lang', 'en,en-US,en-GB',
                '--sub-format', 'json3',
                '--output', f'/tmp/{video_id}',
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Look for subtitle files
            sub_files = glob.glob(f'/tmp/{video_id}*.json3')
            if sub_files:
                with open(sub_files[0], 'r', encoding='utf-8') as f:
                    subs_data = json.load(f)
                
                # Extract text from json3 format
                segments = []
                full_text = []
                
                for event in subs_data.get('events', []):
                    if 'segs' in event:
                        text = ''.join(seg.get('utf8', '') for seg in event['segs'])
                        if text.strip():
                            start_ms = event.get('tStartMs', 0)
                            segments.append({
                                'start': start_ms / 1000,
                                'text': text.strip()
                            })
                            full_text.append(text.strip())
                
                # Cleanup
                for f in sub_files:
                    os.remove(f)
                
                if full_text:
                    return {
                        'transcript': ' '.join(full_text),
                        'segments': segments,
                        'has_timestamps': True,
                        'language': 'en'
                    }
            
            return None
            
        except Exception as e:
            print(f"⚠️ YouTube captions failed: {e}")
            return None


class WhisperBackend:
    """Local Whisper transcription (FREE)"""
    
    @staticmethod
    async def transcribe(video_url: str, model_size: str = "base") -> Optional[Dict]:
        """Download audio and transcribe with Whisper"""
        try:
            import whisper
            
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, "audio.mp3")
                
                # Download audio
                print("🔊 Downloading audio...")
                cmd = [
                    'yt-dlp',
                    '-x',
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',
                    '-o', audio_path.replace('.mp3', '.%(ext)s'),
                    '--no-warnings',
                    video_url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                # Find downloaded file
                audio_files = glob.glob(os.path.join(tmpdir, "audio.*"))
                if not audio_files:
                    print(f"❌ No audio file downloaded. stderr: {result.stderr[:500]}")
                    return None
                
                audio_file = audio_files[0]
                print(f"✅ Downloaded: {audio_file}")
                
                # Transcribe
                print(f"🎤 Transcribing with Whisper ({model_size})...")
                model = whisper.load_model(model_size)
                result = model.transcribe(audio_file)
                
                segments = [
                    {'start': seg['start'], 'end': seg['end'], 'text': seg['text'].strip()}
                    for seg in result.get('segments', [])
                ]
                
                return {
                    'transcript': result['text'],
                    'segments': segments,
                    'has_timestamps': True,
                    'language': result.get('language', 'unknown')
                }
                
        except ImportError:
            print("⚠️ Whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"❌ Whisper transcription failed: {e}")
            return None


class ApifyBackend:
    """Apify YouTube Transcript Scraper (PAID - backup)"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.apify.com/v2"
    
    async def transcribe(self, video_url: str, actor: str = "youtube_transcript") -> Optional[Dict]:
        """Use Apify actor for transcription"""
        if not self.token:
            print("⚠️ APIFY_TOKEN not set - skipping paid backend")
            return None
        
        actor_id = APIFY_ACTORS.get(actor, APIFY_ACTORS["youtube_transcript"])
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                # Start actor run
                run_url = f"{self.base_url}/acts/{actor_id}/runs?token={self.token}"
                
                input_data = {
                    "videoUrls": [video_url],
                    "outputFormat": "TEXT"
                }
                
                print(f"🚀 Starting Apify actor: {actor_id}")
                resp = await client.post(run_url, json=input_data)
                
                if resp.status_code != 201:
                    print(f"❌ Apify start failed: {resp.status_code} - {resp.text[:200]}")
                    return None
                
                run_data = resp.json()
                run_id = run_data['data']['id']
                
                # Wait for completion
                status_url = f"{self.base_url}/actor-runs/{run_id}?token={self.token}"
                for _ in range(60):  # 2 minute timeout
                    await asyncio.sleep(2)
                    status_resp = await client.get(status_url)
                    status = status_resp.json()['data']['status']
                    
                    if status == 'SUCCEEDED':
                        break
                    elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                        print(f"❌ Apify run {status}")
                        return None
                
                # Get results
                dataset_id = run_data['data']['defaultDatasetId']
                items_url = f"{self.base_url}/datasets/{dataset_id}/items?token={self.token}"
                items_resp = await client.get(items_url)
                items = items_resp.json()
                
                if items and len(items) > 0:
                    item = items[0]
                    return {
                        'transcript': item.get('transcript', item.get('text', '')),
                        'segments': [],
                        'has_timestamps': False,
                        'language': item.get('language', 'unknown')
                    }
                
                return None
                
        except Exception as e:
            print(f"❌ Apify transcription failed: {e}")
            return None

# ============================================================
# MAIN TRANSCRIPTION AGENT
# ============================================================

class YouTubeTranscriptAgent:
    """
    Main agent that orchestrates transcription from multiple backends.
    
    Priority order (cost-optimized):
    1. YouTube Captions (FREE) - Try built-in captions first
    2. Whisper Local (FREE) - Download + transcribe locally
    3. Apify (PAID) - Last resort for problematic videos
    """
    
    def __init__(self):
        self.parser = YouTubeURLParser()
        self.captions_backend = YouTubeCaptionsBackend()
        self.whisper_backend = WhisperBackend()
        self.apify_backend = ApifyBackend(APIFY_TOKEN) if APIFY_TOKEN else None
        
    async def get_video_metadata(self, url: str) -> VideoMetadata:
        """Extract video metadata using yt-dlp"""
        video_id = self.parser.extract_video_id(url)
        video_type = self.parser.detect_video_type(url)
        normalized_url = self.parser.normalize_url(url)
        
        metadata = VideoMetadata(
            video_id=video_id or "unknown",
            url=normalized_url,
            video_type=video_type.value
        )
        
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--no-warnings',
                normalized_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())
                metadata.title = data.get('title', 'Unknown')
                metadata.channel = data.get('channel', data.get('uploader', 'Unknown'))
                metadata.duration_seconds = int(data.get('duration', 0))
                metadata.upload_date = data.get('upload_date', '')
                metadata.view_count = int(data.get('view_count', 0))
                metadata.thumbnail_url = data.get('thumbnail', '')
                
                # Detect shorts by duration
                if metadata.duration_seconds <= 60:
                    metadata.video_type = VideoType.SHORT.value
                    
        except Exception as e:
            print(f"⚠️ Metadata extraction failed: {e}")
        
        return metadata
    
    async def transcribe(
        self, 
        url: str, 
        force_whisper: bool = False,
        whisper_model: str = "base"
    ) -> TranscriptResult:
        """
        Transcribe YouTube video with fallback chain.
        
        Args:
            url: YouTube video URL (shorts, regular, live supported)
            force_whisper: Skip captions and go straight to Whisper
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        
        Returns:
            TranscriptResult with transcript and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        # Parse and validate URL
        video_id = self.parser.extract_video_id(url)
        if not video_id:
            return TranscriptResult(
                video=VideoMetadata(video_id="invalid", url=url),
                error="Invalid YouTube URL"
            )
        
        print(f"\n{'='*60}")
        print(f"📺 YOUTUBE TRANSCRIPTION AGENT")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"Video ID: {video_id}")
        
        # Get metadata
        metadata = await self.get_video_metadata(url)
        print(f"📝 Title: {metadata.title}")
        print(f"👤 Channel: {metadata.channel}")
        print(f"⏱️ Duration: {metadata.duration_seconds}s ({metadata.video_type})")
        
        result = TranscriptResult(video=metadata)
        
        # Backend priority chain
        transcript_data = None
        
        # 1. Try YouTube Captions (FREE)
        if not force_whisper:
            print(f"\n🔍 Trying YouTube captions...")
            transcript_data = await self.captions_backend.get_transcript(video_id)
            if transcript_data:
                result.source = TranscriptSource.YOUTUBE_CAPTIONS.value
                print(f"✅ Got YouTube captions ({len(transcript_data['transcript'])} chars)")
        
        # 2. Try Whisper (FREE)
        if not transcript_data:
            print(f"\n🎤 Trying Whisper transcription ({whisper_model})...")
            transcript_data = await self.whisper_backend.transcribe(
                metadata.url, 
                model_size=whisper_model
            )
            if transcript_data:
                result.source = TranscriptSource.WHISPER_LOCAL.value
                print(f"✅ Whisper transcription complete ({len(transcript_data['transcript'])} chars)")
        
        # 3. Try Apify (PAID - last resort)
        if not transcript_data and self.apify_backend:
            print(f"\n💰 Trying Apify (paid)...")
            transcript_data = await self.apify_backend.transcribe(metadata.url)
            if transcript_data:
                result.source = TranscriptSource.APIFY_TRANSCRIPT.value
                print(f"✅ Apify transcription complete ({len(transcript_data['transcript'])} chars)")
        
        # Process result
        if transcript_data:
            result.transcript = transcript_data.get('transcript', '')
            result.transcript_length = len(result.transcript)
            result.segments = transcript_data.get('segments', [])
            result.has_timestamps = transcript_data.get('has_timestamps', False)
            result.language = transcript_data.get('language', 'unknown')
        else:
            result.error = "All transcription backends failed"
            result.source = TranscriptSource.FAILED.value
            print(f"\n❌ Transcription failed for {video_id}")
        
        # Calculate processing time
        end_time = datetime.now(timezone.utc)
        result.processing_time_seconds = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️ Processing time: {result.processing_time_seconds:.1f}s")
        print(f"📊 Source: {result.source}")
        
        return result

# ============================================================
# SUPABASE LOGGING
# ============================================================

class TranscriptLogger:
    """Log transcripts to Supabase insights table"""
    
    def __init__(self):
        self.url = SUPABASE_URL
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def log_transcript(self, result: TranscriptResult, category: str = "learning") -> bool:
        """Log transcript to Supabase"""
        if not SUPABASE_KEY:
            print("⚠️ SUPABASE_KEY not set - skipping logging")
            return False
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=30) as client:
                # Prepare insight data
                insight_data = {
                    "user_id": 1,
                    "insight_type": "youtube_transcript",
                    "title": f"📺 {result.video.title[:80]}",
                    "description": json.dumps({
                        "video_id": result.video.video_id,
                        "channel": result.video.channel,
                        "duration_min": result.video.duration_seconds // 60,
                        "video_type": result.video.video_type,
                        "transcript_chars": result.transcript_length,
                        "source": result.source,
                        "language": result.language,
                        "transcript_preview": result.transcript[:3000],
                        "category": category
                    }, ensure_ascii=False),
                    "source": "youtube_transcript_agent",
                    "priority": 2,
                    "status": "Active"
                }
                
                resp = await client.post(
                    f"{self.url}/rest/v1/insights",
                    headers=self.headers,
                    json=insight_data
                )
                
                if resp.status_code in [200, 201]:
                    print(f"📤 Logged to Supabase: {resp.status_code}")
                    return True
                else:
                    print(f"⚠️ Supabase log failed: {resp.status_code} - {resp.text[:200]}")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Supabase logging error: {e}")
            return False

# ============================================================
# CLI / MAIN ENTRY POINT
# ============================================================

async def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcript_agent.py <youtube_url> [whisper_model] [category]")
        print("Example: python youtube_transcript_agent.py https://youtube.com/shorts/C2Dl6P7diHw base learning")
        sys.exit(1)
    
    url = sys.argv[1]
    whisper_model = sys.argv[2] if len(sys.argv) > 2 else "base"
    category = sys.argv[3] if len(sys.argv) > 3 else "learning"
    
    # Run transcription
    agent = YouTubeTranscriptAgent()
    result = await agent.transcribe(url, whisper_model=whisper_model)
    
    # Print transcript
    print(f"\n{'='*60}")
    print(f"TRANSCRIPT ({result.source})")
    print(f"{'='*60}")
    print(result.transcript[:5000] if result.transcript else "No transcript available")
    
    # Log to Supabase
    if result.transcript:
        logger = TranscriptLogger()
        await logger.log_transcript(result, category=category)
    
    # Save to JSON
    output_file = f"transcript_{result.video.video_id}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to: {output_file}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
