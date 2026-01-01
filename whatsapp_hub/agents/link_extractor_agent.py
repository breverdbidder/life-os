"""
WhatsApp Link Extractor Agent
Extracts URLs from messages and fetches metadata (title, description, preview)

Repository: life-os/whatsapp_hub
Created: 2025-01-01
Agent: Link Extractor Agent (Stage 2)
"""

import re
import os
from urllib.parse import urlparse
from typing import Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from supabase import create_client, Client
import httpx
from bs4 import BeautifulSoup

# ============================================================
# STATE DEFINITION
# ============================================================
class LinkExtractorState(TypedDict):
    """State for link extraction workflow"""
    group_id: str
    messages: List[Dict]
    extracted_links: List[Dict]
    total_links: int
    error: Optional[str]

# ============================================================
# SUPABASE CLIENT
# ============================================================
def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

# ============================================================
# URL EXTRACTION PATTERNS
# ============================================================
URL_PATTERN = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

# ============================================================
# LINK EXTRACTOR NODES
# ============================================================

def fetch_messages_from_db(state: LinkExtractorState) -> LinkExtractorState:
    """Fetch messages from Supabase for a given group"""
    print(f"📥 Fetching messages for group: {state['group_id']}")
    
    try:
        supabase = get_supabase_client()
        
        # Fetch all messages for this group
        result = supabase.table('whatsapp_messages')\
            .select('id, message_text, sender_name, message_timestamp')\
            .eq('group_id', state['group_id'])\
            .execute()
        
        state['messages'] = result.data
        print(f"✅ Fetched {len(result.data)} messages")
        return state
        
    except Exception as e:
        state['error'] = f"Failed to fetch messages: {str(e)}"
        print(f"❌ {state['error']}")
        return state

def extract_urls(state: LinkExtractorState) -> LinkExtractorState:
    """Extract all URLs from messages"""
    print(f"🔗 Extracting URLs from {len(state['messages'])} messages")
    
    links = []
    url_map = {}  # Track duplicate URLs
    
    for message in state['messages']:
        text = message.get('message_text', '')
        if not text:
            continue
        
        # Find all URLs in message
        urls = re.findall(URL_PATTERN, text)
        
        for url in urls:
            # Parse URL
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Track duplicate URLs
            if url in url_map:
                url_map[url]['share_count'] += 1
                continue
            
            # Create link record
            link = {
                'message_id': message['id'],
                'url': url,
                'url_domain': domain,
                'shared_by': message['sender_name'],
                'shared_at': message['message_timestamp'],
                'share_count': 1,
            }
            
            links.append(link)
            url_map[url] = link
    
    state['extracted_links'] = links
    state['total_links'] = len(links)
    
    print(f"✅ Extracted {len(links)} unique URLs")
    return state

def fetch_link_metadata(state: LinkExtractorState) -> LinkExtractorState:
    """Fetch metadata for each URL (title, description, preview image)"""
    print(f"📊 Fetching metadata for {len(state['extracted_links'])} URLs")
    
    async def fetch_metadata_async(link: Dict) -> Dict:
        """Async function to fetch metadata for a single URL"""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(link['url'])
                
                if response.status_code != 200:
                    return link
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = None
                if soup.find('meta', property='og:title'):
                    title = soup.find('meta', property='og:title').get('content')
                elif soup.find('title'):
                    title = soup.find('title').string
                
                # Extract description
                description = None
                if soup.find('meta', property='og:description'):
                    description = soup.find('meta', property='og:description').get('content')
                elif soup.find('meta', attrs={'name': 'description'}):
                    description = soup.find('meta', attrs={'name': 'description'}).get('content')
                
                # Extract preview image
                preview_image = None
                if soup.find('meta', property='og:image'):
                    preview_image = soup.find('meta', property='og:image').get('content')
                
                link['url_title'] = title[:500] if title else None  # Limit length
                link['url_description'] = description[:1000] if description else None
                link['url_preview_image'] = preview_image
                
                return link
                
        except Exception as e:
            print(f"  ⚠️ Failed to fetch metadata for {link['url']}: {str(e)}")
            return link
    
    # Process links with metadata fetching
    # Use asyncio for concurrent fetching
    import asyncio
    
    async def process_all_links():
        tasks = [fetch_metadata_async(link) for link in state['extracted_links']]
        return await asyncio.gather(*tasks)
    
    try:
        enriched_links = asyncio.run(process_all_links())
        state['extracted_links'] = enriched_links
        
        # Count how many got metadata
        with_metadata = sum(1 for link in enriched_links if link.get('url_title'))
        print(f"✅ Fetched metadata for {with_metadata}/{len(enriched_links)} URLs")
        
    except Exception as e:
        print(f"⚠️ Metadata fetching failed: {str(e)}")
        # Continue with links that have partial/no metadata
    
    return state

def save_links_to_supabase(state: LinkExtractorState) -> LinkExtractorState:
    """Save extracted links to Supabase"""
    print(f"💾 Saving {len(state['extracted_links'])} links to Supabase")
    
    try:
        supabase = get_supabase_client()
        
        # Prepare link records
        link_records = [
            {
                'message_id': link['message_id'],
                'group_id': state['group_id'],
                'url': link['url'],
                'url_domain': link['url_domain'],
                'url_title': link.get('url_title'),
                'url_description': link.get('url_description'),
                'url_preview_image': link.get('url_preview_image'),
                'shared_by': link['shared_by'],
                'shared_at': link['shared_at'],
                'share_count': link['share_count'],
            }
            for link in state['extracted_links']
        ]
        
        # Batch insert (500 at a time)
        batch_size = 500
        total_inserted = 0
        
        for i in range(0, len(link_records), batch_size):
            batch = link_records[i:i+batch_size]
            supabase.table('whatsapp_links').insert(batch).execute()
            total_inserted += len(batch)
            print(f"  ↳ Inserted {total_inserted}/{len(link_records)} links")
        
        print(f"✅ All links saved to Supabase")
        return state
        
    except Exception as e:
        state['error'] = f"Failed to save links: {str(e)}"
        print(f"❌ {state['error']}")
        return state

# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

def create_link_extractor_graph() -> StateGraph:
    """Create LangGraph workflow for link extraction"""
    
    workflow = StateGraph(LinkExtractorState)
    
    # Add nodes
    workflow.add_node("fetch_messages", fetch_messages_from_db)
    workflow.add_node("extract", extract_urls)
    workflow.add_node("fetch_metadata", fetch_link_metadata)
    workflow.add_node("save", save_links_to_supabase)
    
    # Define flow
    workflow.set_entry_point("fetch_messages")
    workflow.add_edge("fetch_messages", "extract")
    workflow.add_edge("extract", "fetch_metadata")
    workflow.add_edge("fetch_metadata", "save")
    workflow.add_edge("save", END)
    
    return workflow.compile()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    """Run link extractor agent standalone"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python link_extractor_agent.py <group_id>")
        sys.exit(1)
    
    initial_state = {
        'group_id': sys.argv[1],
        'messages': [],
        'extracted_links': [],
        'total_links': 0,
        'error': None,
    }
    
    graph = create_link_extractor_graph()
    result = graph.invoke(initial_state)
    
    if result.get('error'):
        print(f"\n❌ FAILED: {result['error']}")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: Extracted {result['total_links']} links")
