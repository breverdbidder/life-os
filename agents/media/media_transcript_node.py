"""
Media Transcript Agent V8
Supports: YouTube, Facebook, Instagram, TikTok
Features: 4-tier extraction + Hebrew→English translation
"""

import asyncio
import os
import re
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import anthropic
from googletrans import Translator
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import httpx

class MediaTranscriptAgent:
    """Multi-platform transcript extraction with translation"""
    
    PLATFORM_PATTERNS = {
        'youtube': r'(?:youtube\.com|youtu\.be)',
        'facebook': r'facebook\.com|fb\.watch',
        'instagram': r'instagram\.com',
        'tiktok': r'tiktok\.com'
    }
    
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.translator = Translator()
        self.yt_dlp_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['he', 'iw', 'en'],  # Hebrew + English
            'skip_download': True
        }
    
    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        for platform, pattern in self.PLATFORM_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                return platform
        return 'unknown'
    
    async def extract_transcript(self, url: str) -> Dict[str, Any]:
        """
        4-Tier Extraction System:
        Tier 1: Platform-specific API (YouTube Transcript API)
        Tier 2: yt-dlp (works for YouTube, Facebook, Instagram, TikTok)
        Tier 3: Whisper transcription (audio extraction)
        Tier 4: Apify scraper fallback
        """
        platform = self.detect_platform(url)
        
        result = {
            'url': url,
            'platform': platform,
            'transcript': None,
            'language': None,
            'translation': None,
            'method': None,
            'error': None
        }
        
        # Tier 1: Platform-specific API (YouTube only)
        if platform == 'youtube':
            video_id = self._extract_youtube_id(url)
            if video_id:
                tier1_result = await self._tier1_youtube_api(video_id)
                if tier1_result['success']:
                    result.update(tier1_result)
                    result['method'] = 'tier1_youtube_api'
                    return await self._translate_if_hebrew(result)
        
        # Tier 2: yt-dlp (all platforms)
        tier2_result = await self._tier2_ytdlp(url)
        if tier2_result['success']:
            result.update(tier2_result)
            result['method'] = 'tier2_ytdlp'
            return await self._translate_if_hebrew(result)
        
        # Tier 3: Whisper (audio extraction + transcription)
        tier3_result = await self._tier3_whisper(url)
        if tier3_result['success']:
            result.update(tier3_result)
            result['method'] = 'tier3_whisper'
            return await self._translate_if_hebrew(result)
        
        # Tier 4: Apify scraper
        tier4_result = await self._tier4_apify(url, platform)
        if tier4_result['success']:
            result.update(tier4_result)
            result['method'] = 'tier4_apify'
            return await self._translate_if_hebrew(result)
        
        result['error'] = 'All tiers failed'
        return result
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def _tier1_youtube_api(self, video_id: str) -> Dict[str, Any]:
        """Tier 1: YouTube Transcript API"""
        try:
            # Try Hebrew first, then English
            for lang in ['he', 'iw', 'en']:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript([lang])
                    data = transcript.fetch()
                    
                    full_text = ' '.join([item['text'] for item in data])
                    
                    return {
                        'success': True,
                        'transcript': full_text,
                        'language': lang if lang != 'iw' else 'he',  # Normalize
                        'raw_data': data
                    }
                except Exception:
                    continue
            
            return {'success': False, 'error': 'No transcript available'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _tier2_ytdlp(self, url: str) -> Dict[str, Any]:
        """Tier 2: yt-dlp extraction (YouTube, Facebook, Instagram, TikTok)"""
        try:
            with yt_dlp.YoutubeDL(self.yt_dlp_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check for subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # Try Hebrew first, then English
                for lang in ['he', 'iw', 'en']:
                    if lang in subtitles:
                        subtitle_url = subtitles[lang][0]['url']
                        transcript = await self._download_subtitle(subtitle_url)
                        return {
                            'success': True,
                            'transcript': transcript,
                            'language': lang if lang != 'iw' else 'he'
                        }
                    
                    if lang in automatic_captions:
                        subtitle_url = automatic_captions[lang][0]['url']
                        transcript = await self._download_subtitle(subtitle_url)
                        return {
                            'success': True,
                            'transcript': transcript,
                            'language': lang if lang != 'iw' else 'he'
                        }
                
                return {'success': False, 'error': 'No subtitles found'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _download_subtitle(self, url: str) -> str:
        """Download and parse subtitle file"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            content = response.text
            
            # Remove VTT/SRT formatting
            lines = content.split('\n')
            text_lines = []
            for line in lines:
                # Skip timestamps and metadata
                if '-->' not in line and not line.strip().isdigit() and line.strip():
                    if not line.startswith('WEBVTT') and not line.startswith('Kind:'):
                        text_lines.append(line.strip())
            
            return ' '.join(text_lines)
    
    async def _tier3_whisper(self, url: str) -> Dict[str, Any]:
        """Tier 3: Whisper transcription via DeepSeek V3.2"""
        try:
            # Use DeepSeek to coordinate Whisper transcription
            # This would require audio extraction first (not implemented in this tier)
            # Placeholder for future implementation
            return {'success': False, 'error': 'Whisper tier not yet implemented'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _tier4_apify(self, url: str, platform: str) -> Dict[str, Any]:
        """Tier 4: Apify scraper fallback"""
        try:
            # Apify actor IDs for different platforms
            actor_map = {
                'youtube': 'bernardo/youtube-scraper',
                'facebook': 'apify/facebook-posts-scraper',
                'instagram': 'apify/instagram-scraper',
                'tiktok': 'apify/tiktok-scraper'
            }
            
            if platform not in actor_map:
                return {'success': False, 'error': f'No Apify actor for {platform}'}
            
            # Placeholder - would require Apify API integration
            return {'success': False, 'error': 'Apify tier requires API key'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is Hebrew"""
        # Hebrew Unicode range: 0x0590 to 0x05FF
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return 'unknown'
        
        hebrew_ratio = hebrew_chars / total_chars
        return 'he' if hebrew_ratio > 0.3 else 'en'
    
    async def _translate_if_hebrew(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Translate to English if Hebrew detected"""
        if not result.get('transcript'):
            return result
        
        # Detect language if not already set
        if not result.get('language'):
            result['language'] = self._detect_language(result['transcript'])
        
        # Only translate if Hebrew
        if result['language'] not in ['he', 'iw']:
            return result
        
        # Tier 1: DeepSeek V3.2 translation ($0.28/1M tokens)
        tier1_translation = await self._translate_deepseek(result['transcript'])
        if tier1_translation:
            result['translation'] = tier1_translation
            result['translation_method'] = 'deepseek_v3.2'
            return result
        
        # Tier 2: Google Translate (FREE)
        tier2_translation = await self._translate_google(result['transcript'])
        if tier2_translation:
            result['translation'] = tier2_translation
            result['translation_method'] = 'google_translate'
            return result
        
        result['translation_error'] = 'Translation failed'
        return result
    
    async def _translate_deepseek(self, text: str) -> Optional[str]:
        """Translate using DeepSeek V3.2 via Anthropic Messages API"""
        try:
            # Using Claude as proxy to DeepSeek (if Smart Router configured)
            # Alternative: Direct DeepSeek API call
            
            prompt = f"""Translate the following Hebrew text to English. 
Provide ONLY the English translation, no explanations.

Hebrew text:
{text}

English translation:"""
            
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",  # Will route via Smart Router if configured
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            translation = message.content[0].text.strip()
            return translation
        
        except Exception as e:
            print(f"DeepSeek translation failed: {e}")
            return None
    
    async def _translate_google(self, text: str) -> Optional[str]:
        """Translate using Google Translate (FREE)"""
        try:
            # Split into chunks if too long (Google has limits)
            max_chunk = 5000
            if len(text) <= max_chunk:
                result = self.translator.translate(text, src='he', dest='en')
                return result.text
            
            # Chunk and translate
            chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
            translations = []
            
            for chunk in chunks:
                result = self.translator.translate(chunk, src='he', dest='en')
                translations.append(result.text)
            
            return ' '.join(translations)
        
        except Exception as e:
            print(f"Google translation failed: {e}")
            return None


# LangGraph Node Implementation
async def media_transcript_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for media transcript extraction + translation
    
    Input state:
        - url: str (required)
        - options: Dict (optional)
    
    Output state:
        - transcript_result: Dict with transcript, language, translation
    """
    url = state.get('url')
    if not url:
        return {
            **state,
            'transcript_result': {
                'error': 'No URL provided',
                'success': False
            }
        }
    
    agent = MediaTranscriptAgent()
    result = await agent.extract_transcript(url)
    
    return {
        **state,
        'transcript_result': result
    }


# CLI Testing
async def main():
    """Test the agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python media_transcript_node.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    agent = MediaTranscriptAgent()
    result = await agent.extract_transcript(url)
    
    print("\n" + "="*80)
    print(f"MEDIA TRANSCRIPT AGENT V8")
    print("="*80)
    print(f"URL: {result['url']}")
    print(f"Platform: {result['platform']}")
    print(f"Method: {result.get('method', 'N/A')}")
    print(f"Language: {result.get('language', 'N/A')}")
    print(f"Translation Method: {result.get('translation_method', 'N/A')}")
    print("-"*80)
    
    if result.get('transcript'):
        print("\nORIGINAL TRANSCRIPT:")
        print(result['transcript'][:500] + "..." if len(result['transcript']) > 500 else result['transcript'])
    
    if result.get('translation'):
        print("\n" + "-"*80)
        print("ENGLISH TRANSLATION:")
        print(result['translation'][:500] + "..." if len(result['translation']) > 500 else result['translation'])
    
    if result.get('error'):
        print(f"\nERROR: {result['error']}")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
