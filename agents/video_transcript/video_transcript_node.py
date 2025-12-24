"""
Video Transcript Agent V8 - Unified YouTube + Facebook with Translation
5-Tier: Platform API → yt-dlp → Whisper → Apify → Translation
"""

import os
import json
import asyncio
from typing import Dict, Optional, Tuple
from langdetect import detect
import anthropic
import yt_dlp
import httpx

class VideoTranscriptAgent:
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        
    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        if any(domain in url.lower() for domain in ['youtube.com', 'youtu.be']):
            return 'youtube'
        elif any(domain in url.lower() for domain in ['facebook.com', 'fb.watch', 'fb.com']):
            return 'facebook'
        else:
            raise ValueError(f"Unsupported platform: {url}")
    
    async def tier1_youtube_api(self, video_id: str) -> Optional[Dict]:
        """Tier 1: YouTube Data API v3"""
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                # Get captions list
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/captions",
                    params={"part": "snippet", "videoId": video_id, "key": api_key}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("items"):
                    return None
                
                # Try to get English caption first, fallback to first available
                caption_id = None
                language = None
                for item in data["items"]:
                    lang = item["snippet"]["language"]
                    if lang == "en":
                        caption_id = item["id"]
                        language = "en"
                        break
                
                if not caption_id and data["items"]:
                    caption_id = data["items"][0]["id"]
                    language = data["items"][0]["snippet"]["language"]
                
                if not caption_id:
                    return None
                
                # Download caption
                caption_response = await client.get(
                    f"https://www.googleapis.com/youtube/v3/captions/{caption_id}",
                    params={"key": api_key, "tfmt": "srt"}
                )
                
                return {
                    "text": caption_response.text,
                    "language": language,
                    "source": "youtube_api"
                }
        except Exception as e:
            print(f"Tier 1 YouTube API failed: {e}")
            return None
    
    async def tier2_ytdlp(self, url: str, platform: str) -> Optional[Dict]:
        """Tier 2: yt-dlp (works for both YouTube and Facebook)"""
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'he', 'ar'],  # English, Hebrew, Arabic
                'skip_download': True,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try subtitles
                if info.get('subtitles') or info.get('automatic_captions'):
                    subs = info.get('subtitles', {}) or info.get('automatic_captions', {})
                    
                    # Prefer English, then Hebrew, then first available
                    for lang in ['en', 'he', list(subs.keys())[0] if subs else None]:
                        if lang and lang in subs:
                            subtitle_url = subs[lang][0]['url']
                            async with httpx.AsyncClient() as client:
                                sub_response = await client.get(subtitle_url)
                                return {
                                    "text": sub_response.text,
                                    "language": lang,
                                    "source": f"ytdlp_{platform}"
                                }
                
                return None
        except Exception as e:
            print(f"Tier 2 yt-dlp failed: {e}")
            return None
    
    async def tier3_whisper(self, url: str, platform: str) -> Optional[Dict]:
        """Tier 3: Download audio + Whisper transcription"""
        try:
            # Download audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '/tmp/%(id)s.%(ext)s',
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(info)
            
            # Transcribe with Whisper via Anthropic (if we add this capability)
            # For now, return None - we'd need Whisper API setup
            # Could use OpenAI Whisper API or local Whisper model
            
            return None
        except Exception as e:
            print(f"Tier 3 Whisper failed: {e}")
            return None
    
    async def tier4_apify(self, url: str, platform: str) -> Optional[Dict]:
        """Tier 4: Apify platform-specific scrapers"""
        apify_token = os.environ.get("APIFY_API_TOKEN")
        if not apify_token:
            return None
        
        try:
            # Different actors for different platforms
            actor_id = {
                'youtube': 'streamers/youtube-scraper',
                'facebook': 'apify/facebook-posts-scraper'
            }.get(platform)
            
            if not actor_id:
                return None
            
            async with httpx.AsyncClient(timeout=300) as client:
                # Run actor
                run_response = await client.post(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs",
                    params={"token": apify_token},
                    json={"startUrls": [{"url": url}]}
                )
                run_response.raise_for_status()
                run_id = run_response.json()["data"]["id"]
                
                # Wait for completion (simplified - should poll)
                await asyncio.sleep(30)
                
                # Get results
                result_response = await client.get(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}/dataset/items",
                    params={"token": apify_token}
                )
                result_response.raise_for_status()
                items = result_response.json()
                
                if items and len(items) > 0:
                    # Extract text from first item
                    item = items[0]
                    text = item.get('text') or item.get('description') or item.get('caption', '')
                    
                    if text:
                        return {
                            "text": text,
                            "language": "unknown",  # Will detect later
                            "source": f"apify_{platform}"
                        }
            
            return None
        except Exception as e:
            print(f"Tier 4 Apify failed: {e}")
            return None
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            # Clean text for detection
            clean_text = text[:1000]  # Use first 1000 chars
            lang = detect(clean_text)
            return lang
        except:
            return "unknown"
    
    async def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate text to English using Claude API"""
        if source_lang == "en":
            return text  # Already English
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{
                    "role": "user",
                    "content": f"""Translate this {source_lang} text to English. Preserve formatting.

TEXT:
{text}

Provide ONLY the English translation, no explanations."""
                }]
            )
            
            translation = response.content[0].text
            return translation
        except Exception as e:
            print(f"Translation failed: {e}")
            return text  # Return original if translation fails
    
    async def extract_video_id(self, url: str, platform: str) -> str:
        """Extract video ID from URL"""
        if platform == 'youtube':
            # Handle youtube.com/watch?v=, youtu.be/, youtube.com/embed/
            if 'watch?v=' in url:
                return url.split('watch?v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                return url.split('youtu.be/')[1].split('?')[0]
            elif 'embed/' in url:
                return url.split('embed/')[1].split('?')[0]
        
        # For Facebook, return full URL as "ID"
        return url
    
    async def process_video(self, url: str) -> Dict:
        """Main processing function - tries all tiers with translation"""
        platform = self.detect_platform(url)
        video_id = await self.extract_video_id(url, platform)
        
        print(f"Processing {platform} video: {video_id}")
        
        # Try each tier in sequence
        result = None
        
        if platform == 'youtube':
            result = await self.tier1_youtube_api(video_id)
            if result:
                print(f"✓ Tier 1 YouTube API succeeded")
        
        if not result:
            result = await self.tier2_ytdlp(url, platform)
            if result:
                print(f"✓ Tier 2 yt-dlp succeeded")
        
        if not result:
            result = await self.tier3_whisper(url, platform)
            if result:
                print(f"✓ Tier 3 Whisper succeeded")
        
        if not result:
            result = await self.tier4_apify(url, platform)
            if result:
                print(f"✓ Tier 4 Apify succeeded")
        
        if not result:
            return {
                "success": False,
                "error": "All tiers failed",
                "platform": platform,
                "url": url
            }
        
        # Detect language if not already known
        if result["language"] == "unknown":
            result["language"] = self.detect_language(result["text"])
        
        print(f"Detected language: {result['language']}")
        
        # Translate if not English
        english_text = result["text"]
        if result["language"] != "en":
            print(f"Translating from {result['language']} to English...")
            english_text = await self.translate_to_english(
                result["text"],
                result["language"]
            )
        
        return {
            "success": True,
            "platform": platform,
            "url": url,
            "source": result["source"],
            "original_language": result["language"],
            "original_text": result["text"] if result["language"] != "en" else None,
            "english_text": english_text,
            "requires_translation": result["language"] != "en"
        }


async def main():
    """Test function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_transcript_node.py <video_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    agent = VideoTranscriptAgent()
    result = await agent.process_video(url)
    
    print("\n" + "="*80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
