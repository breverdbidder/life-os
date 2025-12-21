"""
YouTube Transcript Agent V3.0 - Life OS LangGraph Orchestration
================================================================
FREE transcript extraction for YouTube videos of all types:
- Regular videos, Shorts/Reels, Live streams, Playlists

EXTRACTION STRATEGY (Smart Router Philosophy):
1. FREE Tier: youtube-transcript-api (Python - instant, no API key)
2. FREE Tier: yt-dlp captions (VTT/SRT extraction)
3. Fallback: OpenAI Whisper (compute-intensive but FREE)

AUTO-TRIGGER: Claude detects YouTube URLs and triggers this agent.

Author: Claude AI Architect (Life OS)
Version: 3.0.0
Date: 2025-12-21
"""

import os
import re
import json
import subprocess
import glob
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class TranscriptSource(Enum):
    """Source of transcript extraction"""
    YOUTUBE_TRANSCRIPT_API = "youtube_transcript_api"  # Primary FREE
    YTDLP_CAPTIONS = "ytdlp_captions"                  # yt-dlp VTT/SRT
    WHISPER_BASE = "whisper_base"                      # OpenAI Whisper
    WHISPER_SMALL = "whisper_small"
    APIFY = "apify"                                    # Paid fallback
    FAILED = "failed"


@dataclass
class TranscriptResult:
    """Complete transcript extraction result"""
    video_id: str
    video_url: str
    video_type: str  # regular, short, live
    title: str
    channel: str
    duration_seconds: int
    transcript: str
    transcript_source: str
    language: str
    word_count: int
    char_count: int
    timestamp: str
    category: str = "learning"
    error: Optional[str] = None
    segments: Optional[List[Dict]] = None


# =============================================================================
# URL PARSING - Supports ALL YouTube URL formats
# =============================================================================

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from any URL format.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://youtube.com/live/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/v/VIDEO_ID
    """
    if not url:
        return None
    
    url = url.strip()
    
    patterns = [
        r'shorts/([a-zA-Z0-9_-]{11})',           # Shorts first
        r'live/([a-zA-Z0-9_-]{11})',             # Live streams
        r'(?:v=|/v/)([a-zA-Z0-9_-]{11})',        # Standard watch
        r'youtu\.be/([a-zA-Z0-9_-]{11})',        # Short URLs
        r'embed/([a-zA-Z0-9_-]{11})',            # Embed URLs
        r'(?:^|/)([a-zA-Z0-9_-]{11})(?:$|\?)',   # Just ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id
    
    return None


def get_video_type(url: str) -> str:
    """Detect video type from URL"""
    url_lower = url.lower()
    if '/shorts/' in url_lower:
        return 'short'
    elif '/live/' in url_lower:
        return 'live'
    return 'regular'


def is_youtube_url(text: str) -> bool:
    """Check if text contains a YouTube URL"""
    youtube_patterns = [
        r'youtube\.com/watch',
        r'youtube\.com/shorts/',
        r'youtube\.com/live/',
        r'youtu\.be/',
        r'youtube\.com/embed/',
        r'youtube\.com/v/',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in youtube_patterns)


def extract_youtube_urls(text: str) -> List[str]:
    """Extract all YouTube URLs from text"""
    url_pattern = r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s<>"\')\]]*'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    # Filter to only valid YouTube video URLs
    return [url for url in urls if extract_video_id(url)]


# =============================================================================
# STRATEGY 1: youtube-transcript-api (PRIMARY FREE)
# =============================================================================

def extract_with_transcript_api(video_id: str, languages: List[str] = None) -> Tuple[Optional[str], Optional[List[Dict]], Optional[str]]:
    """
    Extract transcript using youtube-transcript-api.
    FASTEST and FREE for videos with captions.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
        
        if languages is None:
            languages = ['en', 'en-US', 'en-GB', 'es', 'he', 'ru', 'fr', 'de']
        
        print(f"🎯 Strategy 1: youtube-transcript-api for {video_id}...")
        
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            
            full_text_parts = []
            segments = []
            
            for entry in transcript_list:
                text = entry.get('text', '').strip()
                if text:
                    full_text_parts.append(text)
                    segments.append({
                        'start': entry.get('start', 0),
                        'duration': entry.get('duration', 0),
                        'text': text
                    })
            
            full_text = ' '.join(full_text_parts)
            lang = 'en'  # Default
            
            try:
                transcript_info = YouTubeTranscriptApi.list_transcripts(video_id)
                for t in transcript_info:
                    lang = t.language_code
                    break
            except:
                pass
            
            print(f"✅ youtube-transcript-api SUCCESS: {len(full_text)} chars")
            return full_text, segments, lang
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"⚠️ No captions available: {type(e).__name__}")
            return None, None, None
            
    except ImportError:
        print("⚠️ youtube-transcript-api not installed")
        return None, None, None
    except Exception as e:
        print(f"❌ youtube-transcript-api error: {e}")
        return None, None, None


# =============================================================================
# STRATEGY 2: yt-dlp Captions
# =============================================================================

def extract_with_ytdlp(video_url: str) -> Tuple[Optional[str], Optional[Dict], Optional[str]]:
    """
    Extract subtitles using yt-dlp.
    Works for most videos with auto-generated captions.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, None, None
    
    print(f"🎯 Strategy 2: yt-dlp captions for {video_id}...")
    
    try:
        # Get metadata first
        metadata = {}
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', video_url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())
                metadata = {
                    'title': data.get('title', 'Unknown'),
                    'channel': data.get('channel', data.get('uploader', 'Unknown')),
                    'duration': int(data.get('duration', 0)),
                    'view_count': int(data.get('view_count', 0)),
                }
        except:
            pass
        
        # Download subtitles
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-auto-sub',
            '--write-sub',
            '--sub-lang', 'en,en-US,en-GB',
            '--sub-format', 'vtt',
            '--convert-subs', 'vtt',
            '-o', f'/tmp/{video_id}',
            '--no-warnings',
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        vtt_files = glob.glob(f'/tmp/{video_id}*.vtt')
        if not vtt_files:
            print("⚠️ No subtitle files found")
            return None, metadata if metadata else None, None
        
        with open(vtt_files[0], 'r', encoding='utf-8') as f:
            vtt_content = f.read()
        
        # Parse VTT format
        lines = []
        for line in vtt_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('WEBVTT') or '-->' in line:
                continue
            if line.startswith('Kind:') or line.startswith('Language:'):
                continue
            if re.match(r'^\d+$', line):
                continue
            # Remove VTT tags
            line = re.sub(r'<[^>]+>', '', line)
            if line and line not in lines[-1:]:
                lines.append(line)
        
        transcript = ' '.join(lines)
        
        # Cleanup
        for f in vtt_files:
            try:
                os.remove(f)
            except:
                pass
        
        print(f"✅ yt-dlp SUCCESS: {len(transcript)} chars")
        return transcript, metadata, 'en'
        
    except subprocess.TimeoutExpired:
        print("⚠️ yt-dlp timeout")
        return None, None, None
    except Exception as e:
        print(f"❌ yt-dlp error: {e}")
        return None, None, None


# =============================================================================
# STRATEGY 3: OpenAI Whisper (Fallback)
# =============================================================================

def extract_with_whisper(video_url: str, model: str = "base") -> Tuple[Optional[str], Optional[Dict], Optional[str]]:
    """
    Transcribe video using OpenAI Whisper.
    Compute-intensive but works on ANY video.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, None, None
    
    print(f"🎯 Strategy 3: Whisper {model} for {video_id}...")
    
    try:
        import whisper
        
        # Get metadata
        metadata = {}
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', video_url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                data = json.loads(result.stdout.strip())
                metadata = {
                    'title': data.get('title', 'Unknown'),
                    'channel': data.get('channel', 'Unknown'),
                    'duration': int(data.get('duration', 0)),
                }
        except:
            pass
        
        # Download audio
        print("🔊 Downloading audio...")
        audio_cmd = [
            'yt-dlp', '-x',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', '/tmp/audio.%(ext)s',
            '--no-warnings',
            video_url
        ]
        subprocess.run(audio_cmd, capture_output=True, timeout=300)
        
        audio_files = glob.glob('/tmp/audio.*')
        if not audio_files:
            print("⚠️ Audio download failed")
            return None, metadata if metadata else None, None
        
        # Transcribe
        print(f"🎤 Transcribing with Whisper {model}...")
        whisper_model = whisper.load_model(model)
        result = whisper_model.transcribe(audio_files[0])
        
        transcript = result['text']
        language = result.get('language', 'unknown')
        
        # Cleanup
        for f in audio_files:
            try:
                os.remove(f)
            except:
                pass
        
        print(f"✅ Whisper SUCCESS: {len(transcript)} chars, lang: {language}")
        return transcript, metadata, language
        
    except ImportError:
        print("⚠️ Whisper not installed")
        return None, None, None
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return None, None, None


# =============================================================================
# MAIN EXTRACTION FUNCTION
# =============================================================================

def extract_transcript(
    video_url: str,
    use_whisper_fallback: bool = True,
    whisper_model: str = "base",
    category: str = "learning",
    log_to_supabase: bool = True
) -> TranscriptResult:
    """
    Extract transcript from YouTube video using multi-strategy approach.
    
    Args:
        video_url: Any YouTube URL (regular, shorts, live, etc.)
        use_whisper_fallback: Use Whisper if captions unavailable
        whisper_model: Whisper model size (tiny, base, small, medium)
        category: Category for Supabase logging
        log_to_supabase: Whether to log to Supabase insights table
    
    Returns:
        TranscriptResult with transcript and metadata
    """
    print(f"\n{'='*70}")
    print(f"📺 YOUTUBE TRANSCRIPT AGENT V3")
    print(f"{'='*70}")
    print(f"URL: {video_url}")
    print(f"Category: {category}")
    
    video_id = extract_video_id(video_url)
    if not video_id:
        return TranscriptResult(
            video_id="",
            video_url=video_url,
            video_type="unknown",
            title="Invalid URL",
            channel="",
            duration_seconds=0,
            transcript="",
            transcript_source=TranscriptSource.FAILED.value,
            language="",
            word_count=0,
            char_count=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=f"Could not extract video ID from: {video_url}"
        )
    
    video_type = get_video_type(video_url)
    print(f"Video ID: {video_id}")
    print(f"Type: {video_type}")
    
    transcript = None
    segments = None
    metadata = {}
    language = "unknown"
    source = TranscriptSource.FAILED
    
    # Strategy 1: youtube-transcript-api (FREE, instant)
    transcript, segments, language = extract_with_transcript_api(video_id)
    if transcript and len(transcript) > 20:
        source = TranscriptSource.YOUTUBE_TRANSCRIPT_API
    
    # Strategy 2: yt-dlp captions
    if not transcript or len(transcript) < 20:
        transcript, metadata, language = extract_with_ytdlp(video_url)
        if transcript and len(transcript) > 20:
            source = TranscriptSource.YTDLP_CAPTIONS
    
    # Strategy 3: Whisper (if enabled)
    if (not transcript or len(transcript) < 20) and use_whisper_fallback:
        transcript, meta, language = extract_with_whisper(video_url, whisper_model)
        if transcript and len(transcript) > 20:
            source = TranscriptSource.WHISPER_BASE if whisper_model == "base" else TranscriptSource.WHISPER_SMALL
            metadata = meta or metadata
    
    # Get metadata if missing
    if not metadata.get('title'):
        try:
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', video_url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                data = json.loads(result.stdout.strip())
                metadata = {
                    'title': data.get('title', 'Unknown'),
                    'channel': data.get('channel', data.get('uploader', 'Unknown')),
                    'duration': int(data.get('duration', 0)),
                }
        except:
            metadata = {'title': 'Unknown', 'channel': 'Unknown', 'duration': 0}
    
    if not transcript:
        transcript = ""
    
    # Build result
    result = TranscriptResult(
        video_id=video_id,
        video_url=video_url,
        video_type=video_type,
        title=metadata.get('title', 'Unknown'),
        channel=metadata.get('channel', 'Unknown'),
        duration_seconds=metadata.get('duration', 0),
        transcript=transcript,
        transcript_source=source.value,
        language=language or 'unknown',
        word_count=len(transcript.split()) if transcript else 0,
        char_count=len(transcript),
        timestamp=datetime.now(timezone.utc).isoformat(),
        category=category,
        segments=segments
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 RESULT")
    print(f"{'='*60}")
    print(f"Title: {result.title[:60]}...")
    print(f"Channel: {result.channel}")
    print(f"Duration: {result.duration_seconds // 60}m {result.duration_seconds % 60}s")
    print(f"Source: {result.transcript_source}")
    print(f"Language: {result.language}")
    print(f"Words: {result.word_count}")
    
    if transcript:
        print(f"\n📝 TRANSCRIPT PREVIEW:")
        print(transcript[:500])
    
    # Log to Supabase
    if log_to_supabase and transcript and len(transcript) > 20:
        _log_to_supabase(result)
    
    return result


def _log_to_supabase(result: TranscriptResult) -> bool:
    """Log transcript to Supabase insights table"""
    try:
        import requests
        
        supabase_url = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
        supabase_key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_KEY')
        
        if not supabase_key:
            print("⚠️ No Supabase key - skipping log")
            return False
        
        insight_data = {
            "user_id": 1,
            "insight_type": "youtube_transcript",
            "title": f"📺 {result.title[:80]}",
            "description": json.dumps({
                "video_id": result.video_id,
                "video_url": result.video_url,
                "video_type": result.video_type,
                "channel": result.channel,
                "duration_min": result.duration_seconds // 60,
                "transcript_chars": result.char_count,
                "transcript_words": result.word_count,
                "source": result.transcript_source,
                "language": result.language,
                "category": result.category,
                "transcript_preview": result.transcript[:5000]
            }, ensure_ascii=False),
            "source": "youtube_transcript_agent_v3",
            "priority": 2,
            "status": "Active"
        }
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{supabase_url}/rest/v1/insights",
            headers=headers,
            json=insight_data,
            timeout=30
        )
        
        print(f"📤 Supabase: {response.status_code}")
        return response.status_code in [200, 201, 204]
        
    except Exception as e:
        print(f"⚠️ Supabase error: {e}")
        return False


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcript_agent_v3.py <youtube_url> [options]")
        print("\nOptions:")
        print("  --no-whisper     Skip Whisper fallback")
        print("  --no-supabase    Skip Supabase logging")
        print("  --whisper=MODEL  Whisper model: tiny, base, small, medium")
        print("  --category=CAT   Category: learning, michael_swim, business")
        print("\nExamples:")
        print("  python youtube_transcript_agent_v3.py 'https://youtube.com/shorts/C2Dl6P7diHw'")
        print("  python youtube_transcript_agent_v3.py 'https://youtu.be/dQw4w9WgXcQ' --no-whisper")
        sys.exit(1)
    
    url = sys.argv[1]
    use_whisper = '--no-whisper' not in sys.argv
    log_supabase = '--no-supabase' not in sys.argv
    
    whisper_model = "base"
    category = "learning"
    
    for arg in sys.argv:
        if arg.startswith('--whisper='):
            whisper_model = arg.split('=')[1]
        if arg.startswith('--category='):
            category = arg.split('=')[1]
    
    result = extract_transcript(
        url,
        use_whisper_fallback=use_whisper,
        whisper_model=whisper_model,
        log_to_supabase=log_supabase,
        category=category
    )
    
    # Save result
    with open('transcript_result.json', 'w', encoding='utf-8') as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to: transcript_result.json")
