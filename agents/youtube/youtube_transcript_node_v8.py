"""
YouTube Transcript Agent V8 - LangGraph Implementation
Combines Manus AI clean patterns + BidDeed 4-tier resilience

Author: Claude AI Architect, BidDeed.AI
Date: Dec 31, 2025
Repo: breverdbidder/life-os

ARCHITECTURE:
- 4-tier fallback: YT-API → yt-dlp+Whisper → Apify → Manual
- Clean conditional edges (Manus AI pattern)
- TypedDict state for better typing
- Explicit error node vs inline try-catch
- Cost optimization: FREE tier first
"""

import os
import re
import subprocess
import json
from typing import TypedDict, Literal, Optional
from pathlib import Path

# LangGraph imports
from langgraph.graph import StateGraph, END

# Tier 1: YouTube API (FREE)
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TIER1_AVAILABLE = True
except ImportError:
    TIER1_AVAILABLE = False

# Tier 2: OpenAI Whisper (PAID fallback)
try:
    from openai import OpenAI
    TIER2_AVAILABLE = True
except ImportError:
    TIER2_AVAILABLE = False

# ============================================================================
# STATE DEFINITION (Manus AI Pattern)
# ============================================================================

class YouTubeAgentState(TypedDict):
    """
    State definition for YouTube transcript workflow.
    Passed between all nodes in the graph.
    """
    # Input
    youtube_url: str
    video_id: str
    
    # Processing artifacts
    audio_path: Optional[str]
    transcript_text: Optional[str]
    transcript_path: Optional[str]
    
    # Metadata
    title: Optional[str]
    channel: Optional[str]
    duration: Optional[int]
    
    # Workflow control
    current_tier: int  # 1-4 tracking which tier we're on
    current_task: str  # Human-readable status
    error: Optional[str]  # Error message if any step fails
    
    # Output
    success: bool
    output_file: Optional[str]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


def clean_transcript(text: str) -> str:
    """Clean up transcript text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove music/sound annotations
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text.strip()


# ============================================================================
# GRAPH NODES (One function per processing step)
# ============================================================================

def start_node(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    Entry point: Parse URL and initialize state
    """
    print("=" * 80)
    print("YOUTUBE TRANSCRIPT AGENT V8")
    print("=" * 80)
    
    try:
        video_id = extract_video_id(state["youtube_url"])
        print(f"✓ Video ID: {video_id}")
        
        return {
            **state,
            "video_id": video_id,
            "current_tier": 1,
            "current_task": "Starting transcript extraction...",
            "success": False,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "error": f"Invalid YouTube URL: {str(e)}",
            "current_task": "Failed to parse URL"
        }


def tier1_youtube_api(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    TIER 1: YouTube Transcript API (FREE, instant)
    Best case: Native transcript available
    """
    print("\n[TIER 1] Trying YouTube Transcript API (FREE)...")
    
    if not TIER1_AVAILABLE:
        return {
            **state,
            "current_tier": 2,
            "error": "youtube_transcript_api not installed"
        }
    
    try:
        video_id = state["video_id"]
        
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try English first, then any available
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = list(transcript_list)[0]  # First available
        
        # Fetch transcript data
        transcript_data = transcript.fetch()
        
        # Combine all segments
        full_text = ' '.join([entry['text'] for entry in transcript_data])
        full_text = clean_transcript(full_text)
        
        # Save to file
        output_path = f"/tmp/youtube_{video_id}_transcript.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"✅ SUCCESS - Tier 1 (FREE)")
        print(f"   Length: {len(full_text)} chars")
        print(f"   Segments: {len(transcript_data)}")
        
        return {
            **state,
            "transcript_text": full_text,
            "transcript_path": output_path,
            "output_file": output_path,
            "current_task": "Transcript extracted via YouTube API",
            "success": True,
            "error": None
        }
        
    except Exception as e:
        print(f"✗ Tier 1 failed: {str(e)}")
        return {
            **state,
            "current_tier": 2,
            "error": f"Tier 1 failed: {str(e)}"
        }


def tier2_ytdlp_download(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    TIER 2: yt-dlp audio download (FREE)
    Downloads audio for Whisper transcription
    """
    print("\n[TIER 2] Trying yt-dlp + Whisper...")
    
    try:
        video_id = state["video_id"]
        url = state["youtube_url"]
        output_path = f"/tmp/youtube_{video_id}.mp3"
        
        # Download audio using yt-dlp
        cmd = [
            "yt-dlp",
            "-f", "bestaudio[ext=m4a]/bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_path.replace(".mp3", ".%(ext)s"),
            url
        ]
        
        print(f"   Downloading audio...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"yt-dlp failed: {result.stderr}")
        
        if not os.path.exists(output_path):
            raise Exception(f"Audio file not created: {output_path}")
        
        print(f"✓ Audio downloaded: {output_path}")
        
        return {
            **state,
            "audio_path": output_path,
            "current_task": "Audio downloaded, ready for transcription",
            "error": None
        }
        
    except Exception as e:
        print(f"✗ Tier 2 download failed: {str(e)}")
        return {
            **state,
            "current_tier": 3,
            "error": f"Tier 2 download failed: {str(e)}"
        }


def tier2_whisper_transcribe(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    TIER 2B: OpenAI Whisper transcription (PAID)
    Transcribes the downloaded audio
    """
    print("\n[TIER 2B] Transcribing with Whisper...")
    
    if not TIER2_AVAILABLE:
        return {
            **state,
            "current_tier": 3,
            "error": "OpenAI library not available"
        }
    
    if not state.get("audio_path"):
        return {
            **state,
            "current_tier": 3,
            "error": "No audio file to transcribe"
        }
    
    try:
        audio_path = state["audio_path"]
        video_id = state["video_id"]
        
        # Transcribe with Whisper
        client = OpenAI()
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        full_text = clean_transcript(transcription)
        
        # Save transcript
        output_path = f"/tmp/youtube_{video_id}_transcript.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Clean up audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        print(f"✅ SUCCESS - Tier 2 (Whisper PAID)")
        print(f"   Length: {len(full_text)} chars")
        
        return {
            **state,
            "transcript_text": full_text,
            "transcript_path": output_path,
            "output_file": output_path,
            "current_task": "Transcript extracted via Whisper",
            "success": True,
            "error": None
        }
        
    except Exception as e:
        print(f"✗ Tier 2 Whisper failed: {str(e)}")
        return {
            **state,
            "current_tier": 3,
            "error": f"Tier 2 Whisper failed: {str(e)}"
        }


def tier3_apify(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    TIER 3: Apify actor (PAID, slower)
    Last automated resort before manual intervention
    """
    print("\n[TIER 3] Trying Apify actor...")
    
    # This would require Apify API integration
    # Placeholder for now - implement when Apify credentials available
    
    print("✗ Tier 3 not implemented yet")
    return {
        **state,
        "current_tier": 4,
        "error": "Tier 3 (Apify) not implemented"
    }


def handle_error(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    Error handling node - reports failure and suggests manual intervention
    """
    print("\n" + "=" * 80)
    print("❌ WORKFLOW FAILED")
    print("=" * 80)
    print(f"Final error: {state.get('error', 'Unknown error')}")
    print(f"Failed at tier: {state.get('current_tier', 'Unknown')}")
    print(f"\nSuggestions:")
    print("1. Check if video has transcripts enabled")
    print("2. Verify video is public and accessible")
    print("3. Try manual download with yt-dlp")
    print("=" * 80)
    
    return {
        **state,
        "current_task": "Failed - manual intervention needed",
        "success": False
    }


def finish_success(state: YouTubeAgentState) -> YouTubeAgentState:
    """
    Success node - reports successful completion
    """
    print("\n" + "=" * 80)
    print("✅ TRANSCRIPT EXTRACTION SUCCESSFUL")
    print("=" * 80)
    print(f"Method: Tier {state['current_tier']}")
    print(f"Output: {state['output_file']}")
    print(f"Length: {len(state['transcript_text'])} characters")
    print("=" * 80)
    
    return state


# ============================================================================
# CONDITIONAL EDGE FUNCTION (Manus AI Pattern)
# ============================================================================

def should_continue(state: YouTubeAgentState) -> Literal["continue", "retry_next_tier", "error", "success"]:
    """
    Determines next node based on current state.
    
    This is the Manus AI pattern - cleaner than nested try-catch.
    """
    # If we have success, we're done
    if state.get("success"):
        return "success"
    
    # If we have an error, check if we can retry
    if state.get("error"):
        current_tier = state.get("current_tier", 1)
        
        # Can we try next tier?
        if current_tier < 4:
            return "retry_next_tier"
        else:
            # Exhausted all tiers
            return "error"
    
    # No error, no success - continue normal flow
    return "continue"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_youtube_transcript_graph() -> StateGraph:
    """
    Builds the LangGraph workflow with conditional edges.
    
    Graph flow:
    start → tier1 → (success? → finish | fail? → tier2_download)
    tier2_download → tier2_whisper → (success? → finish | fail? → tier3)
    tier3 → (success? → finish | fail? → error)
    """
    
    workflow = StateGraph(YouTubeAgentState)
    
    # Add all nodes
    workflow.add_node("start", start_node)
    workflow.add_node("tier1_api", tier1_youtube_api)
    workflow.add_node("tier2_download", tier2_ytdlp_download)
    workflow.add_node("tier2_whisper", tier2_whisper_transcribe)
    workflow.add_node("tier3_apify", tier3_apify)
    workflow.add_node("handle_error", handle_error)
    workflow.add_node("finish_success", finish_success)
    
    # Set entry point
    workflow.set_entry_point("start")
    
    # Start always goes to tier 1
    workflow.add_conditional_edges(
        "start",
        lambda s: "error" if s.get("error") else "continue",
        {
            "continue": "tier1_api",
            "error": "handle_error"
        }
    )
    
    # Tier 1: Success → finish, Failure → tier 2
    workflow.add_conditional_edges(
        "tier1_api",
        should_continue,
        {
            "success": "finish_success",
            "retry_next_tier": "tier2_download",
            "error": "handle_error"
        }
    )
    
    # Tier 2 download: Success → Whisper, Failure → tier 3
    workflow.add_conditional_edges(
        "tier2_download",
        should_continue,
        {
            "continue": "tier2_whisper",
            "retry_next_tier": "tier3_apify",
            "error": "handle_error"
        }
    )
    
    # Tier 2 Whisper: Success → finish, Failure → tier 3
    workflow.add_conditional_edges(
        "tier2_whisper",
        should_continue,
        {
            "success": "finish_success",
            "retry_next_tier": "tier3_apify",
            "error": "handle_error"
        }
    )
    
    # Tier 3: Success → finish, Failure → error
    workflow.add_conditional_edges(
        "tier3_apify",
        should_continue,
        {
            "success": "finish_success",
            "error": "handle_error"
        }
    )
    
    # Terminal nodes
    workflow.add_edge("handle_error", END)
    workflow.add_edge("finish_success", END)
    
    return workflow.compile()


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage
    app = create_youtube_transcript_graph()
    
    # Test video
    test_url = "https://youtu.be/vkQkQmvDz1M"
    
    initial_state: YouTubeAgentState = {
        "youtube_url": test_url,
        "video_id": "",
        "audio_path": None,
        "transcript_text": None,
        "transcript_path": None,
        "title": None,
        "channel": None,
        "duration": None,
        "current_tier": 1,
        "current_task": "Initializing...",
        "error": None,
        "success": False,
        "output_file": None
    }
    
    # Run the graph
    for output in app.stream(initial_state):
        for node_name, node_state in output.items():
            print(f"\n>>> Node completed: {node_name}")
    
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
