"""
YouTube Transcript Agent V2.0 - Life OS LangGraph Orchestration
=================================================================
Enhanced transcript extraction with youtube-transcript-api as primary FREE source.

EXTRACTION STRATEGY (Smart Router Philosophy):
1. FREE Tier A: youtube-transcript-api (Python - instant, 95%+ accuracy)
2. FREE Tier B: yt-dlp captions extraction (faster than Whisper)
3. Fallback: OpenAI Whisper base/small (compute-intensive)
4. Premium: Apify actors (if all FREE fails)

Supports ALL YouTube URL formats:
- Regular videos: https://youtube.com/watch?v=VIDEO_ID
- Shorts/Reels: https://youtube.com/shorts/VIDEO_ID
- Short URLs: https://youtu.be/VIDEO_ID
- Embed URLs: https://youtube.com/embed/VIDEO_ID
- Live streams: https://youtube.com/live/VIDEO_ID
- Playlists: Extracts first video or all videos

Author: Claude AI Architect
Version: 2.0.0
Date: 2025-12-21
"""

import os
import re
import json
import subprocess
import glob
from datetime import datetime, timezone
from typing import TypedDict, Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

# LangGraph imports (optional)
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class TranscriptSource(Enum):
    """Source of transcript extraction"""
    YOUTUBE_TRANSCRIPT_API = "youtube_transcript_api"  # Primary FREE (Python)
    YOUTUBE_CAPTIONS = "youtube_captions"              # yt-dlp captions
    WHISPER_BASE = "whisper_base"                      # OpenAI Whisper base
    WHISPER_SMALL = "whisper_small"                    # OpenAI Whisper small
    APIFY = "apify"                                     # Apify actor (paid)
    NONE = "none"                                       # Failed


@dataclass
class VideoMetadata:
    """YouTube video metadata"""
    video_id: str
    title: str
    channel: str
    duration_seconds: int
    view_count: int = 0
    upload_date: str = ""
    description: str = ""
    is_short: bool = False
    is_live: bool = False


@dataclass
class TranscriptResult:
    """Complete transcript extraction result"""
    video_id: str
    video_url: str
    video_type: str
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
    segments: Optional[List[Dict]] = None  # Timestamped segments


class AgentState(TypedDict):
    """LangGraph agent state"""
    video_url: str
    video_id: Optional[str]
    video_type: str
    metadata: Optional[dict]
    transcript: Optional[str]
    segments: Optional[List[Dict]]
    transcript_source: Optional[str]
    language: Optional[str]
    error: Optional[str]
    stage: str
    attempts: int
    log_to_supabase: bool
    category: str


# =============================================================================
# URL PARSING
# =============================================================================

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from any URL format.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID  
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://youtube.com/v/VIDEO_ID
    - https://youtube.com/live/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    """
    if not url:
        return None
        
    url = url.strip()
    
    patterns = [
        r'shorts/([a-zA-Z0-9_-]{11})',           # Shorts (check first)
        r'live/([a-zA-Z0-9_-]{11})',             # Live streams
        r'(?:v=|/v/)([a-zA-Z0-9_-]{11})',        # Standard watch or /v/
        r'youtu\.be/([a-zA-Z0-9_-]{11})',        # Short URLs  
        r'embed/([a-zA-Z0-9_-]{11})',            # Embed URLs
        r'(?:^|/)([a-zA-Z0-9_-]{11})(?:$|\?)',   # Just the ID
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
    else:
        return 'regular'


# =============================================================================
# METHOD 1: youtube-transcript-api (PRIMARY FREE)
# =============================================================================

def extract_with_transcript_api(video_id: str, languages: List[str] = None) -> tuple[Optional[str], Optional[List[Dict]], Optional[str]]:
    """
    Extract transcript using youtube-transcript-api (Python library).
    FASTEST and most reliable for videos WITH captions.
    
    Args:
        video_id: YouTube video ID
        languages: List of language codes to try (default: ['en', 'en-US', 'en-GB'])
    
    Returns:
        (transcript_text, segments_with_timestamps, language) or (None, None, None)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
        
        if languages is None:
            languages = ['en', 'en-US', 'en-GB', 'es', 'fr', 'de', 'pt', 'it', 'ru', 'ja', 'ko', 'zh-Hans', 'zh-Hant']
        
        print(f"🎯 Trying youtube-transcript-api for {video_id}...")
        
        try:
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            
            # Build full text and segments
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
            
            # Detect language
            transcript_info = YouTubeTranscriptApi.list_transcripts(video_id)
            lang = 'en'
            for transcript in transcript_info:
                if transcript.is_generated or transcript.is_translatable:
                    lang = transcript.language_code
                    break
            
            print(f"✅ youtube-transcript-api SUCCESS: {len(full_text)} chars, lang={lang}")
            return full_text, segments, lang
            
        except TranscriptsDisabled:
            print("⚠️ Transcripts disabled for this video")
            return None, None, None
        except NoTranscriptFound:
            print("⚠️ No transcript found in requested languages")
            return None, None, None
        except VideoUnavailable:
            print("⚠️ Video unavailable")
            return None, None, None
            
    except ImportError:
        print("⚠️ youtube-transcript-api not installed")
        return None, None, None
    except Exception as e:
        print(f"❌ youtube-transcript-api error: {e}")
        return None, None, None


# =============================================================================
# METHOD 2: yt-dlp Captions (SECONDARY FREE)
# =============================================================================

def extract_with_ytdlp(video_url: str) -> tuple[Optional[str], Optional[dict], Optional[str]]:
    """
    Extract transcript using yt-dlp captions (FREE, fast).
    
    Returns:
        (transcript_text, metadata_dict, language) or (None, None, None)
    """
    try:
        import tempfile
        import shutil
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix='ytdlp_')
        
        print(f"🔍 Trying yt-dlp captions extraction...")
        
        # First get metadata
        metadata = None
        try:
            meta_cmd = ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', video_url]
            result = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                metadata = json.loads(result.stdout.strip())
        except Exception as e:
            print(f"⚠️ Metadata fetch failed: {e}")
        
        # Try to get subtitles
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-auto-sub',
            '--write-sub',
            '--sub-lang', 'en,en-US,en-GB',
            '--sub-format', 'json3',
            '-o', f'{temp_dir}/%(id)s',
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Find subtitle files
        sub_files = glob.glob(f'{temp_dir}/*.json3')
        
        if not sub_files:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("⚠️ No captions available via yt-dlp")
            return None, metadata, None
        
        # Parse first subtitle file
        with open(sub_files[0], 'r', encoding='utf-8') as f:
            subs_data = json.load(f)
        
        full_text_parts = []
        for event in subs_data.get('events', []):
            if 'segs' in event:
                text = ''.join(seg.get('utf8', '') for seg in event['segs'])
                if text.strip():
                    full_text_parts.append(text.strip())
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if full_text_parts:
            full_text = ' '.join(full_text_parts)
            print(f"✅ yt-dlp captions SUCCESS: {len(full_text)} chars")
            return full_text, metadata, 'en'
        
        return None, metadata, None
        
    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timed out")
        return None, None, None
    except Exception as e:
        print(f"❌ yt-dlp error: {e}")
        return None, None, None


# =============================================================================
# METHOD 3: Whisper Transcription (FALLBACK - compute intensive)
# =============================================================================

def extract_with_whisper(video_url: str, model_size: str = "base") -> tuple[Optional[str], Optional[dict], Optional[str]]:
    """
    Extract transcript using OpenAI Whisper (compute-intensive fallback).
    
    Args:
        video_url: YouTube URL
        model_size: "tiny", "base", "small", or "medium"
    
    Returns:
        (transcript_text, metadata_dict, language)
    """
    try:
        import whisper
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp(prefix='whisper_')
        
        print(f"🎤 Downloading audio for Whisper ({model_size})...")
        
        # Download audio
        cmd = [
            'yt-dlp',
            '-x',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '-o', f'{temp_dir}/audio.%(ext)s',
            '--print-json',
            '--no-warnings',
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Parse metadata
        metadata = None
        for line in result.stdout.strip().split('\n'):
            if line.startswith('{'):
                try:
                    metadata = json.loads(line)
                    break
                except:
                    continue
        
        # Find audio file
        audio_files = glob.glob(f'{temp_dir}/audio.*')
        if not audio_files:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("❌ Audio download failed")
            return None, metadata, None
        
        audio_file = audio_files[0]
        print(f"✅ Audio downloaded, transcribing with Whisper {model_size}...")
        
        # Transcribe
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_file, language=None)
        
        transcript = result['text']
        language = result.get('language', 'unknown')
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print(f"✅ Whisper complete: {len(transcript)} chars, lang={language}")
        return transcript, metadata, language
        
    except ImportError:
        print("❌ Whisper not installed")
        return None, None, None
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return None, None, None


# =============================================================================
# METHOD 4: Apify (PREMIUM - if all else fails)
# =============================================================================

def extract_with_apify(video_url: str, actor_id: str = "topaz_sharingan/youtube-transcript-scraper") -> tuple[Optional[str], Optional[dict], Optional[str]]:
    """
    Extract transcript using Apify actor (paid service).
    
    Args:
        video_url: YouTube URL
        actor_id: Apify actor ID
    
    Returns:
        (transcript_text, metadata_dict, language)
    """
    try:
        import requests
        
        apify_token = os.environ.get('APIFY_API_TOKEN')
        if not apify_token:
            print("⚠️ APIFY_API_TOKEN not set")
            return None, None, None
        
        print(f"🌐 Calling Apify actor: {actor_id}...")
        
        # Run actor
        run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
        headers = {"Authorization": f"Bearer {apify_token}"}
        payload = {"input": {"videoUrl": video_url}}
        
        response = requests.post(run_url, json=payload, headers=headers, timeout=120)
        
        if response.status_code != 201:
            print(f"❌ Apify run failed: {response.status_code}")
            return None, None, None
        
        run_data = response.json()
        run_id = run_data['data']['id']
        
        # Wait for completion (poll)
        import time
        for _ in range(60):  # Max 5 min
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            status_resp = requests.get(status_url, headers=headers)
            status_data = status_resp.json()
            
            if status_data['data']['status'] == 'SUCCEEDED':
                break
            elif status_data['data']['status'] in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                print(f"❌ Apify run {status_data['data']['status']}")
                return None, None, None
            
            time.sleep(5)
        
        # Get results
        results_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
        results_resp = requests.get(results_url, headers=headers)
        results = results_resp.json()
        
        if results:
            item = results[0]
            transcript = item.get('transcript', item.get('text', ''))
            metadata = {
                'title': item.get('title', 'Unknown'),
                'channel': item.get('channel', 'Unknown'),
                'duration': item.get('duration', 0)
            }
            language = item.get('language', 'en')
            
            print(f"✅ Apify SUCCESS: {len(transcript)} chars")
            return transcript, metadata, language
        
        return None, None, None
        
    except Exception as e:
        print(f"❌ Apify error: {e}")
        return None, None, None


# =============================================================================
# MAIN EXTRACTION FUNCTION
# =============================================================================

def extract_transcript(
    video_url: str,
    use_whisper_fallback: bool = True,
    whisper_model: str = "base",
    use_apify: bool = False,
    log_to_supabase: bool = True,
    category: str = "learning"
) -> TranscriptResult:
    """
    Extract transcript from any YouTube video using Smart Router strategy.
    
    Strategy:
    1. youtube-transcript-api (FREE, instant, Python)
    2. yt-dlp captions (FREE, fast)
    3. Whisper (FREE, compute-intensive)
    4. Apify (paid, premium)
    
    Args:
        video_url: Any YouTube URL format
        use_whisper_fallback: Try Whisper if FREE methods fail
        whisper_model: "tiny", "base", "small", "medium"
        use_apify: Use Apify as last resort (requires APIFY_API_TOKEN)
        log_to_supabase: Log result to Supabase insights
        category: Category for Supabase (learning, michael_swim, business, personal)
    
    Returns:
        TranscriptResult with transcript and metadata
    """
    print(f"\n{'='*60}")
    print(f"📺 YOUTUBE TRANSCRIPT AGENT V2.0")
    print(f"{'='*60}")
    print(f"🔗 URL: {video_url}")
    
    # Parse video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        return TranscriptResult(
            video_id="",
            video_url=video_url,
            video_type="unknown",
            title="Unknown",
            channel="Unknown",
            duration_seconds=0,
            transcript="",
            transcript_source="none",
            language="unknown",
            word_count=0,
            char_count=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            category=category,
            error=f"Invalid YouTube URL: {video_url}"
        )
    
    video_type = get_video_type(video_url)
    print(f"📺 Video ID: {video_id}")
    print(f"📱 Type: {video_type.upper()}")
    
    transcript = None
    segments = None
    metadata = None
    language = None
    source = TranscriptSource.NONE
    
    # ==========================================================================
    # STRATEGY 1: youtube-transcript-api (PRIMARY FREE)
    # ==========================================================================
    print(f"\n🎯 STRATEGY 1: youtube-transcript-api (FREE)")
    transcript, segments, language = extract_with_transcript_api(video_id)
    
    if transcript and len(transcript) > 20:
        source = TranscriptSource.YOUTUBE_TRANSCRIPT_API
        # Get metadata separately
        try:
            meta_cmd = ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', video_url]
            result = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                metadata = json.loads(result.stdout.strip())
        except:
            pass
    
    # ==========================================================================
    # STRATEGY 2: yt-dlp captions (SECONDARY FREE)
    # ==========================================================================
    if not transcript or len(transcript) < 20:
        print(f"\n🎯 STRATEGY 2: yt-dlp captions (FREE)")
        transcript, metadata, language = extract_with_ytdlp(video_url)
        
        if transcript and len(transcript) > 20:
            source = TranscriptSource.YOUTUBE_CAPTIONS
    
    # ==========================================================================
    # STRATEGY 3: Whisper (FALLBACK - compute intensive)
    # ==========================================================================
    if (not transcript or len(transcript) < 20) and use_whisper_fallback:
        print(f"\n🎯 STRATEGY 3: Whisper transcription ({whisper_model})")
        transcript, metadata, language = extract_with_whisper(video_url, whisper_model)
        
        if transcript and len(transcript) > 20:
            source = TranscriptSource.WHISPER_BASE if whisper_model == "base" else TranscriptSource.WHISPER_SMALL
    
    # ==========================================================================
    # STRATEGY 4: Apify (PREMIUM - if all else fails)
    # ==========================================================================
    if (not transcript or len(transcript) < 20) and use_apify:
        print(f"\n🎯 STRATEGY 4: Apify (PREMIUM)")
        transcript, metadata, language = extract_with_apify(video_url)
        
        if transcript and len(transcript) > 20:
            source = TranscriptSource.APIFY
    
    # ==========================================================================
    # BUILD RESULT
    # ==========================================================================
    if not transcript:
        transcript = ""
    
    result = TranscriptResult(
        video_id=video_id,
        video_url=video_url,
        video_type=video_type,
        title=metadata.get('title', 'Unknown') if metadata else 'Unknown',
        channel=metadata.get('channel', metadata.get('uploader', 'Unknown')) if metadata else 'Unknown',
        duration_seconds=int(metadata.get('duration', 0)) if metadata else 0,
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
    print(f"📊 RESULT SUMMARY")
    print(f"{'='*60}")
    print(f"   📺 Title: {result.title[:60]}...")
    print(f"   👤 Channel: {result.channel}")
    print(f"   ⏱️ Duration: {result.duration_seconds // 60}m {result.duration_seconds % 60}s")
    print(f"   📝 Source: {result.transcript_source}")
    print(f"   🌍 Language: {result.language}")
    print(f"   📊 Words: {result.word_count}")
    print(f"   📦 Category: {result.category}")
    
    if transcript:
        print(f"\n📝 TRANSCRIPT PREVIEW:")
        print(f"   {transcript[:500]}...")
    
    # ==========================================================================
    # LOG TO SUPABASE
    # ==========================================================================
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
            print("⚠️ No Supabase key available")
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
                "transcript_preview": result.transcript[:3000]
            }, ensure_ascii=False),
            "source": "youtube_transcript_agent_v2",
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
        
        print(f"\n📤 Logged to Supabase: {response.status_code}")
        return response.status_code in [200, 201, 204]
        
    except Exception as e:
        print(f"⚠️ Supabase logging failed: {e}")
        return False


# =============================================================================
# LANGGRAPH WORKFLOW (OPTIONAL)
# =============================================================================

def build_youtube_transcript_graph():
    """Build LangGraph workflow for YouTube transcript extraction"""
    
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph required. Install: pip install langgraph")
    
    def parse_url_node(state: AgentState) -> AgentState:
        video_id = extract_video_id(state['video_url'])
        if not video_id:
            state['error'] = f"Invalid URL: {state['video_url']}"
            state['stage'] = 'error'
            return state
        state['video_id'] = video_id
        state['video_type'] = get_video_type(state['video_url'])
        state['stage'] = 'try_transcript_api'
        return state
    
    def try_transcript_api_node(state: AgentState) -> AgentState:
        transcript, segments, lang = extract_with_transcript_api(state['video_id'])
        if transcript and len(transcript) > 20:
            state['transcript'] = transcript
            state['segments'] = segments
            state['language'] = lang
            state['transcript_source'] = TranscriptSource.YOUTUBE_TRANSCRIPT_API.value
            state['stage'] = 'complete'
        else:
            state['stage'] = 'try_ytdlp'
        return state
    
    def try_ytdlp_node(state: AgentState) -> AgentState:
        transcript, metadata, lang = extract_with_ytdlp(state['video_url'])
        if transcript and len(transcript) > 20:
            state['transcript'] = transcript
            state['metadata'] = metadata
            state['language'] = lang
            state['transcript_source'] = TranscriptSource.YOUTUBE_CAPTIONS.value
            state['stage'] = 'complete'
        else:
            state['stage'] = 'try_whisper'
        return state
    
    def try_whisper_node(state: AgentState) -> AgentState:
        transcript, metadata, lang = extract_with_whisper(state['video_url'])
        if transcript and len(transcript) > 20:
            state['transcript'] = transcript
            state['metadata'] = metadata or state.get('metadata')
            state['language'] = lang
            state['transcript_source'] = TranscriptSource.WHISPER_BASE.value
            state['stage'] = 'complete'
        else:
            state['error'] = "All extraction methods failed"
            state['stage'] = 'error'
        return state
    
    def router(state: AgentState) -> str:
        stage = state.get('stage', '')
        if stage == 'complete' or stage == 'error':
            return END
        return state['stage']
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("parse_url", parse_url_node)
    workflow.add_node("try_transcript_api", try_transcript_api_node)
    workflow.add_node("try_ytdlp", try_ytdlp_node)
    workflow.add_node("try_whisper", try_whisper_node)
    
    workflow.set_entry_point("parse_url")
    
    workflow.add_edge("parse_url", "try_transcript_api")
    workflow.add_conditional_edges("try_transcript_api", router, {
        "try_ytdlp": "try_ytdlp",
        END: END
    })
    workflow.add_conditional_edges("try_ytdlp", router, {
        "try_whisper": "try_whisper",
        END: END
    })
    workflow.add_edge("try_whisper", END)
    
    return workflow.compile()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcript_agent_v2.py <youtube_url> [options]")
        print("\nOptions:")
        print("  --no-whisper     Skip Whisper fallback")
        print("  --no-supabase    Skip Supabase logging")
        print("  --whisper=MODEL  Whisper model: tiny, base, small, medium")
        print("  --category=CAT   Category: learning, michael_swim, business, personal")
        print("\nExamples:")
        print("  python youtube_transcript_agent_v2.py 'https://youtube.com/shorts/C2Dl6P7diHw'")
        print("  python youtube_transcript_agent_v2.py 'https://youtu.be/dQw4w9WgXcQ' --no-whisper")
        print("  python youtube_transcript_agent_v2.py 'https://youtube.com/watch?v=jNQXAC9IVRw' --category=business")
        sys.exit(1)
    
    url = sys.argv[1]
    use_whisper = '--no-whisper' not in sys.argv
    log_supabase = '--no-supabase' not in sys.argv
    
    # Parse whisper model
    whisper_model = "base"
    for arg in sys.argv:
        if arg.startswith('--whisper='):
            whisper_model = arg.split('=')[1]
    
    # Parse category
    category = "learning"
    for arg in sys.argv:
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
    output_path = 'transcript_result.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Result saved to: {output_path}")
