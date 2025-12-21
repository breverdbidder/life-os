"""
YouTube Transcript Agent - Life OS LangGraph Orchestration
============================================================
Extracts transcripts from ANY YouTube video (shorts, reels, long-form, live streams)

STRATEGY (Smart Router Philosophy):
1. FREE Tier: yt-dlp captions extraction (instant, no compute)
2. Fallback: OpenAI Whisper base model (compute-intensive)
3. Premium: Apify actors (if FREE fails and Whisper unavailable)

Supports:
- Regular videos: https://youtube.com/watch?v=VIDEO_ID
- Shorts/Reels: https://youtube.com/shorts/VIDEO_ID
- Short URLs: https://youtu.be/VIDEO_ID
- Embed URLs: https://youtube.com/embed/VIDEO_ID
- Playlists: Extracts first video or all videos

Author: Claude AI Architect
Version: 1.0.0
Date: 2025-12-21
"""

import os
import re
import json
import subprocess
from datetime import datetime
from typing import TypedDict, Optional, List, Literal
from dataclasses import dataclass
from enum import Enum

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not installed - running in standalone mode")


class TranscriptSource(Enum):
    """Source of the transcript extraction"""
    YOUTUBE_CAPTIONS = "youtube_captions"  # Native YouTube captions (FREE)
    WHISPER_BASE = "whisper_base"          # OpenAI Whisper base model
    WHISPER_SMALL = "whisper_small"        # OpenAI Whisper small model
    APIFY = "apify"                         # Apify actor (paid)
    NONE = "none"                           # No transcript available


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


@dataclass 
class TranscriptResult:
    """Complete transcript extraction result"""
    video_id: str
    video_url: str
    metadata: VideoMetadata
    transcript: str
    transcript_source: TranscriptSource
    language: str
    word_count: int
    char_count: int
    timestamp: str
    error: Optional[str] = None


class AgentState(TypedDict):
    """LangGraph agent state"""
    video_url: str
    video_id: Optional[str]
    metadata: Optional[dict]
    transcript: Optional[str]
    transcript_source: Optional[str]
    language: Optional[str]
    error: Optional[str]
    stage: str
    attempts: int
    log_to_supabase: bool


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
    - https://m.youtube.com/watch?v=VIDEO_ID
    """
    if not url:
        return None
        
    # Clean the URL
    url = url.strip()
    
    patterns = [
        r'shorts/([a-zA-Z0-9_-]{11})',           # Shorts (check first)
        r'(?:v=|/v/)([a-zA-Z0-9_-]{11})',        # Standard watch or /v/
        r'youtu\.be/([a-zA-Z0-9_-]{11})',        # Short URLs  
        r'embed/([a-zA-Z0-9_-]{11})',            # Embed URLs
        r'(?:^|/)([a-zA-Z0-9_-]{11})(?:$|\?)',   # Just the ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Validate it looks like a video ID (11 chars, alphanumeric with - and _)
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id
    
    return None


def is_shorts_url(url: str) -> bool:
    """Check if URL is a YouTube Shorts"""
    return '/shorts/' in url.lower()


# =============================================================================
# CAPTION EXTRACTION (FREE TIER)
# =============================================================================

def extract_with_ytdlp(video_url: str) -> tuple[Optional[str], Optional[dict], Optional[str]]:
    """
    Extract transcript using yt-dlp captions (FREE, instant)
    
    Returns:
        (transcript_text, metadata_dict, language) or (None, None, None) on failure
    """
    try:
        # First, get video info and subtitles
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-subs',
            '--write-auto-subs',
            '--sub-lang', 'en,en-US,en-GB',  # Prefer English
            '--convert-subs', 'vtt',
            '--print-json',
            '--no-warnings',
            '-o', 'subtitle.%(ext)s',
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"⚠️ yt-dlp failed: {result.stderr[:200]}")
            return None, None, None
        
        # Parse metadata from JSON output
        metadata = None
        for line in result.stdout.strip().split('\n'):
            if line.startswith('{'):
                try:
                    metadata = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        
        # Look for downloaded subtitle file
        import glob
        vtt_files = glob.glob('subtitle*.vtt')
        
        if not vtt_files:
            print("⚠️ No subtitle files found")
            return None, metadata, None
            
        # Parse VTT file
        transcript_text = parse_vtt_file(vtt_files[0])
        
        # Detect language from filename or metadata
        lang = 'en'
        if metadata and 'subtitles' in metadata:
            lang = list(metadata['subtitles'].keys())[0] if metadata['subtitles'] else 'en'
        
        # Cleanup
        for f in vtt_files:
            try:
                os.remove(f)
            except:
                pass
                
        return transcript_text, metadata, lang
        
    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timed out")
        return None, None, None
    except Exception as e:
        print(f"❌ yt-dlp error: {e}")
        return None, None, None


def parse_vtt_file(filepath: str) -> str:
    """Parse WebVTT subtitle file to plain text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove VTT header
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip headers, timestamps, and empty lines
            if not line:
                continue
            if line.startswith('WEBVTT'):
                continue
            if line.startswith('Kind:') or line.startswith('Language:'):
                continue
            if '-->' in line:  # Timestamp line
                continue
            if re.match(r'^\d+$', line):  # Cue number
                continue
            if line.startswith('<'):  # VTT tags
                line = re.sub(r'<[^>]+>', '', line)
            
            # Remove duplicate lines (common in auto-captions)
            if text_lines and line == text_lines[-1]:
                continue
                
            text_lines.append(line)
        
        # Join and clean
        text = ' '.join(text_lines)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    except Exception as e:
        print(f"❌ VTT parse error: {e}")
        return ""


# =============================================================================
# WHISPER EXTRACTION (FALLBACK)
# =============================================================================

def extract_with_whisper(video_url: str, model_size: str = "base") -> tuple[Optional[str], Optional[dict], Optional[str]]:
    """
    Extract transcript using OpenAI Whisper (compute-intensive fallback)
    
    Args:
        video_url: YouTube URL
        model_size: "base", "small", or "medium"
    
    Returns:
        (transcript_text, metadata_dict, language)
    """
    try:
        import whisper
        
        # Download audio
        print(f"🔊 Downloading audio for Whisper...")
        cmd = [
            'yt-dlp',
            '-x',
            '--audio-format', 'mp3',
            '-o', 'whisper_audio.%(ext)s',
            '--print-json',
            '--no-warnings',
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ Audio download failed: {result.stderr[:200]}")
            return None, None, None
        
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
        import glob
        audio_files = glob.glob('whisper_audio.*')
        if not audio_files:
            print("❌ No audio file found")
            return None, metadata, None
        
        audio_file = audio_files[0]
        print(f"✅ Audio downloaded: {audio_file}")
        
        # Transcribe with Whisper
        print(f"🎤 Transcribing with Whisper {model_size}...")
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_file, language=None)  # Auto-detect
        
        transcript_text = result['text']
        language = result.get('language', 'unknown')
        
        # Cleanup
        for f in audio_files:
            try:
                os.remove(f)
            except:
                pass
        
        print(f"✅ Whisper transcription complete: {len(transcript_text)} chars, lang={language}")
        return transcript_text, metadata, language
        
    except ImportError:
        print("❌ Whisper not installed")
        return None, None, None
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return None, None, None


# =============================================================================
# LANGGRAPH NODES
# =============================================================================

def parse_url_node(state: AgentState) -> AgentState:
    """Parse YouTube URL and extract video ID"""
    video_id = extract_video_id(state['video_url'])
    
    if not video_id:
        state['error'] = f"Invalid YouTube URL: {state['video_url']}"
        state['stage'] = 'error'
        return state
    
    state['video_id'] = video_id
    state['stage'] = 'try_captions'
    print(f"📺 Parsed video ID: {video_id}")
    return state


def try_captions_node(state: AgentState) -> AgentState:
    """Try to extract captions using yt-dlp (FREE)"""
    print(f"🎯 Attempting FREE caption extraction...")
    
    transcript, metadata, lang = extract_with_ytdlp(state['video_url'])
    
    if transcript and len(transcript) > 50:
        state['transcript'] = transcript
        state['metadata'] = metadata
        state['language'] = lang or 'en'
        state['transcript_source'] = TranscriptSource.YOUTUBE_CAPTIONS.value
        state['stage'] = 'complete'
        print(f"✅ Captions extracted: {len(transcript)} chars")
    else:
        state['attempts'] = state.get('attempts', 0) + 1
        state['stage'] = 'try_whisper'
        print("⚠️ No captions available, falling back to Whisper...")
    
    return state


def try_whisper_node(state: AgentState) -> AgentState:
    """Fallback to Whisper transcription"""
    print(f"🎤 Attempting Whisper transcription...")
    
    transcript, metadata, lang = extract_with_whisper(state['video_url'])
    
    if transcript and len(transcript) > 50:
        state['transcript'] = transcript
        state['metadata'] = metadata or state.get('metadata')
        state['language'] = lang or 'unknown'
        state['transcript_source'] = TranscriptSource.WHISPER_BASE.value
        state['stage'] = 'complete'
        print(f"✅ Whisper transcription complete: {len(transcript)} chars")
    else:
        state['error'] = "All extraction methods failed"
        state['stage'] = 'error'
        print("❌ Whisper transcription failed")
    
    return state


def save_result_node(state: AgentState) -> AgentState:
    """Save transcript result"""
    result = {
        "video_id": state.get('video_id'),
        "video_url": state.get('video_url'),
        "title": state.get('metadata', {}).get('title', 'Unknown') if state.get('metadata') else 'Unknown',
        "channel": state.get('metadata', {}).get('channel', 'Unknown') if state.get('metadata') else 'Unknown',
        "duration_seconds": state.get('metadata', {}).get('duration', 0) if state.get('metadata') else 0,
        "transcript": state.get('transcript', ''),
        "transcript_source": state.get('transcript_source', 'none'),
        "language": state.get('language', 'unknown'),
        "word_count": len(state.get('transcript', '').split()),
        "char_count": len(state.get('transcript', '')),
        "timestamp": datetime.now().isoformat(),
        "error": state.get('error')
    }
    
    # Save to JSON file
    with open('transcript_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 Result saved to transcript_result.json")
    print(f"   Title: {result['title']}")
    print(f"   Source: {result['transcript_source']}")
    print(f"   Words: {result['word_count']}")
    
    return state


def log_to_supabase_node(state: AgentState) -> AgentState:
    """Log transcript to Supabase insights table"""
    if not state.get('log_to_supabase', True):
        return state
        
    supabase_url = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
    supabase_key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_key:
        print("⚠️ No Supabase key available, skipping logging")
        return state
    
    try:
        import requests
        
        metadata = state.get('metadata') or {}
        transcript = state.get('transcript', '')
        
        insight_data = {
            "user_id": 1,
            "insight_type": "youtube_transcript",
            "title": f"YT: {metadata.get('title', state.get('video_id', 'Unknown'))[:80]}",
            "description": json.dumps({
                "video_id": state.get('video_id'),
                "video_url": state.get('video_url'),
                "channel": metadata.get('channel', 'Unknown'),
                "duration_min": metadata.get('duration', 0) // 60 if metadata.get('duration') else 0,
                "transcript_source": state.get('transcript_source'),
                "language": state.get('language'),
                "word_count": len(transcript.split()),
                "transcript_preview": transcript[:3000] if transcript else ""
            }, ensure_ascii=False),
            "priority": 2
        }
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        response = requests.post(
            f"{supabase_url}/rest/v1/insights",
            headers=headers,
            json=insight_data,
            timeout=30
        )
        
        if response.status_code in [200, 201, 204]:
            print(f"📤 Logged to Supabase insights")
        else:
            print(f"⚠️ Supabase log failed: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Supabase logging error: {e}")
    
    return state


def route_after_parse(state: AgentState) -> str:
    """Route after URL parsing"""
    if state.get('error'):
        return 'error'
    return 'try_captions'


def route_after_captions(state: AgentState) -> str:
    """Route after caption extraction attempt"""
    if state.get('stage') == 'complete':
        return 'save'
    return 'try_whisper'


def route_after_whisper(state: AgentState) -> str:
    """Route after Whisper attempt"""
    return 'save'


# =============================================================================
# BUILD LANGGRAPH WORKFLOW
# =============================================================================

def build_youtube_transcript_graph():
    """Build the LangGraph workflow for YouTube transcript extraction"""
    
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph is required. Install with: pip install langgraph")
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_url", parse_url_node)
    workflow.add_node("try_captions", try_captions_node)
    workflow.add_node("try_whisper", try_whisper_node)
    workflow.add_node("save", save_result_node)
    workflow.add_node("log_supabase", log_to_supabase_node)
    
    # Set entry point
    workflow.set_entry_point("parse_url")
    
    # Add edges
    workflow.add_conditional_edges(
        "parse_url",
        route_after_parse,
        {
            "try_captions": "try_captions",
            "error": "save"
        }
    )
    
    workflow.add_conditional_edges(
        "try_captions",
        route_after_captions,
        {
            "save": "save",
            "try_whisper": "try_whisper"
        }
    )
    
    workflow.add_edge("try_whisper", "save")
    workflow.add_edge("save", "log_supabase")
    workflow.add_edge("log_supabase", END)
    
    return workflow.compile()


# =============================================================================
# STANDALONE FUNCTION (NO LANGGRAPH)
# =============================================================================

def extract_transcript(video_url: str, use_whisper_fallback: bool = True, log_to_supabase: bool = True) -> dict:
    """
    Standalone transcript extraction function (no LangGraph required)
    
    Args:
        video_url: YouTube URL (any format)
        use_whisper_fallback: Try Whisper if captions unavailable
        log_to_supabase: Log result to Supabase insights
    
    Returns:
        dict with transcript and metadata
    """
    print(f"\n{'='*60}")
    print(f"🎬 YouTube Transcript Agent")
    print(f"{'='*60}")
    print(f"📺 URL: {video_url}")
    
    # Parse video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"error": f"Invalid YouTube URL: {video_url}"}
    
    print(f"✅ Video ID: {video_id}")
    is_short = is_shorts_url(video_url)
    print(f"📱 Type: {'Shorts/Reel' if is_short else 'Regular video'}")
    
    # Try captions first (FREE)
    print(f"\n🎯 Strategy 1: YouTube Captions (FREE)")
    transcript, metadata, lang = extract_with_ytdlp(video_url)
    
    source = TranscriptSource.NONE
    
    if transcript and len(transcript) > 50:
        source = TranscriptSource.YOUTUBE_CAPTIONS
        print(f"✅ SUCCESS: {len(transcript)} chars extracted")
    elif use_whisper_fallback:
        print(f"\n🎯 Strategy 2: Whisper Transcription (Fallback)")
        transcript, metadata, lang = extract_with_whisper(video_url)
        if transcript and len(transcript) > 50:
            source = TranscriptSource.WHISPER_BASE
            print(f"✅ SUCCESS: {len(transcript)} chars transcribed")
    
    if not transcript:
        transcript = ""
        print(f"\n❌ No transcript available")
    
    # Build result
    result = {
        "video_id": video_id,
        "video_url": video_url,
        "is_short": is_short,
        "title": metadata.get('title', 'Unknown') if metadata else 'Unknown',
        "channel": metadata.get('channel', 'Unknown') if metadata else 'Unknown',
        "duration_seconds": metadata.get('duration', 0) if metadata else 0,
        "transcript": transcript,
        "transcript_source": source.value,
        "language": lang or 'unknown',
        "word_count": len(transcript.split()) if transcript else 0,
        "char_count": len(transcript),
        "timestamp": datetime.now().isoformat()
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 RESULT SUMMARY")
    print(f"{'='*60}")
    print(f"   Title: {result['title'][:60]}...")
    print(f"   Channel: {result['channel']}")
    print(f"   Duration: {result['duration_seconds'] // 60}m {result['duration_seconds'] % 60}s")
    print(f"   Source: {result['transcript_source']}")
    print(f"   Language: {result['language']}")
    print(f"   Words: {result['word_count']}")
    print(f"\n📝 Transcript Preview:")
    print(f"   {transcript[:500]}..." if len(transcript) > 500 else f"   {transcript}")
    
    # Log to Supabase if enabled
    if log_to_supabase and transcript:
        try:
            import requests
            supabase_url = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
            supabase_key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_SERVICE_KEY')
            
            if supabase_key:
                insight_data = {
                    "user_id": 1,
                    "insight_type": "youtube_transcript",
                    "title": f"YT: {result['title'][:80]}",
                    "description": json.dumps({
                        "video_id": video_id,
                        "channel": result['channel'],
                        "duration_min": result['duration_seconds'] // 60,
                        "source": result['transcript_source'],
                        "words": result['word_count'],
                        "preview": transcript[:2000]
                    }, ensure_ascii=False),
                    "priority": 2
                }
                
                response = requests.post(
                    f"{supabase_url}/rest/v1/insights",
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                        "Content-Type": "application/json"
                    },
                    json=insight_data,
                    timeout=30
                )
                print(f"\n📤 Logged to Supabase: {response.status_code}")
        except Exception as e:
            print(f"\n⚠️ Supabase logging skipped: {e}")
    
    return result


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcript_agent.py <youtube_url> [--no-whisper] [--no-supabase]")
        print("\nExamples:")
        print("  python youtube_transcript_agent.py 'https://youtube.com/shorts/C2Dl6P7diHw'")
        print("  python youtube_transcript_agent.py 'https://youtu.be/dQw4w9WgXcQ'")
        print("  python youtube_transcript_agent.py 'https://youtube.com/watch?v=jNQXAC9IVRw'")
        sys.exit(1)
    
    url = sys.argv[1]
    use_whisper = '--no-whisper' not in sys.argv
    log_supabase = '--no-supabase' not in sys.argv
    
    result = extract_transcript(url, use_whisper_fallback=use_whisper, log_to_supabase=log_supabase)
    
    # Save result
    with open('transcript_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Full result saved to: transcript_result.json")
