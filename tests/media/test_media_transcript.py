"""
Media Transcript Agent V8 - Test Examples
Run these to verify all platforms and translation capabilities
"""

import asyncio
from media_transcript_node import MediaTranscriptAgent

async def test_youtube_hebrew():
    """Test YouTube video with Hebrew content"""
    print("\n" + "="*80)
    print("TEST 1: YouTube Hebrew Video")
    print("="*80)
    
    agent = MediaTranscriptAgent()
    
    # Example: Replace with actual Hebrew YouTube video
    url = "https://www.youtube.com/watch?v=YOUR_HEBREW_VIDEO_ID"
    
    result = await agent.extract_transcript(url)
    
    print(f"Platform: {result['platform']}")
    print(f"Method: {result.get('method', 'N/A')}")
    print(f"Language: {result.get('language', 'N/A')}")
    
    if result.get('transcript'):
        print(f"\nOriginal (Hebrew): {result['transcript'][:200]}...")
    
    if result.get('translation'):
        print(f"\nTranslation (English): {result['translation'][:200]}...")
        print(f"Translation method: {result['translation_method']}")
    
    if result.get('error'):
        print(f"ERROR: {result['error']}")
    
    return result

async def test_youtube_english():
    """Test YouTube video with English content (no translation needed)"""
    print("\n" + "="*80)
    print("TEST 2: YouTube English Video")
    print("="*80)
    
    agent = MediaTranscriptAgent()
    
    # Example: TED Talk or other English content
    url = "https://www.youtube.com/watch?v=YOUR_ENGLISH_VIDEO_ID"
    
    result = await agent.extract_transcript(url)
    
    print(f"Platform: {result['platform']}")
    print(f"Method: {result.get('method', 'N/A')}")
    print(f"Language: {result.get('language', 'N/A')}")
    
    if result.get('transcript'):
        print(f"\nTranscript: {result['transcript'][:200]}...")
    
    if result.get('translation'):
        print("⚠️ Translation shouldn't occur for English content")
    else:
        print("✅ No translation (already English)")
    
    return result

async def test_facebook():
    """Test Facebook video"""
    print("\n" + "="*80)
    print("TEST 3: Facebook Video")
    print("="*80)
    
    agent = MediaTranscriptAgent()
    
    # Example from Ariel's Facebook share
    url = "https://www.facebook.com/share/r/1EVegyZC3N/"
    
    result = await agent.extract_transcript(url)
    
    print(f"Platform: {result['platform']}")
    print(f"Method: {result.get('method', 'N/A')}")
    print(f"Language: {result.get('language', 'N/A')}")
    
    if result.get('transcript'):
        print(f"\nOriginal: {result['transcript'][:200]}...")
    
    if result.get('translation'):
        print(f"\nTranslation: {result['translation'][:200]}...")
    
    if result.get('error'):
        print(f"ERROR: {result['error']}")
        print("\nNote: Facebook videos may require public access")
    
    return result

async def test_instagram():
    """Test Instagram reel"""
    print("\n" + "="*80)
    print("TEST 4: Instagram Reel")
    print("="*80)
    
    agent = MediaTranscriptAgent()
    
    # Example Instagram reel
    url = "https://www.instagram.com/reel/YOUR_REEL_ID/"
    
    result = await agent.extract_transcript(url)
    
    print(f"Platform: {result['platform']}")
    print(f"Method: {result.get('method', 'N/A')}")
    
    if result.get('transcript'):
        print(f"\nTranscript: {result['transcript'][:200]}...")
    
    if result.get('error'):
        print(f"ERROR: {result['error']}")
        print("\nNote: Instagram reels may not have subtitles")
    
    return result

async def test_all_tiers():
    """Test fallback through all tiers"""
    print("\n" + "="*80)
    print("TEST 5: Tier Fallback Testing")
    print("="*80)
    
    test_urls = [
        ("YouTube with captions", "https://www.youtube.com/watch?v=VIDEO_WITH_CAPTIONS"),
        ("Facebook public", "https://www.facebook.com/watch?v=PUBLIC_VIDEO"),
        ("YouTube without captions", "https://www.youtube.com/watch?v=NO_CAPTIONS"),
    ]
    
    agent = MediaTranscriptAgent()
    
    for name, url in test_urls:
        print(f"\nTesting: {name}")
        result = await agent.extract_transcript(url)
        print(f"  Method: {result.get('method', 'FAILED')}")
        print(f"  Success: {result.get('transcript') is not None}")

async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "🚀"*40)
    print("MEDIA TRANSCRIPT AGENT V8 - COMPLETE TEST SUITE")
    print("🚀"*40)
    
    results = {
        'youtube_hebrew': await test_youtube_hebrew(),
        'youtube_english': await test_youtube_english(),
        'facebook': await test_facebook(),
        'instagram': await test_instagram(),
    }
    
    await test_all_tiers()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get('transcript') else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    # Run individual test
    # asyncio.run(test_facebook())
    
    # Or run all tests
    asyncio.run(run_all_tests())
