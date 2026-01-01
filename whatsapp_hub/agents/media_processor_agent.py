"""
WhatsApp Media Processor Agent
Processes attachments (images, videos, audio, documents) from WhatsApp exports

Repository: life-os/whatsapp_hub
Created: 2025-01-01
Agent: Media Processor Agent (Stage 3)
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from supabase import create_client, Client
from PIL import Image
import subprocess

# ============================================================
# STATE DEFINITION
# ============================================================
class MediaProcessorState(TypedDict):
    """State for media processing workflow"""
    group_id: str
    media_folder_path: str
    messages_with_media: List[Dict]
    processed_attachments: List[Dict]
    total_attachments: int
    total_size_bytes: int
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
# MEDIA TYPE DETECTION
# ============================================================
MEDIA_TYPE_MAP = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic', 'bmp'],
    'video': ['mp4', 'mov', 'avi', 'mkv', 'webm', '3gp'],
    'audio': ['mp3', 'wav', 'ogg', 'm4a', 'aac', 'opus'],
    'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'],
}

def detect_file_type(filename: str) -> str:
    """Detect file type from extension"""
    ext = Path(filename).suffix[1:].lower()  # Remove the dot
    
    for file_type, extensions in MEDIA_TYPE_MAP.items():
        if ext in extensions:
            return file_type
    
    return 'other'

# ============================================================
# MEDIA PROCESSOR NODES
# ============================================================

def fetch_media_messages(state: MediaProcessorState) -> MediaProcessorState:
    """Fetch messages that have media attachments"""
    print(f"📥 Fetching media messages for group: {state['group_id']}")
    
    try:
        supabase = get_supabase_client()
        
        # Fetch messages with media
        result = supabase.table('whatsapp_messages')\
            .select('id, media_filename, sender_name, message_timestamp')\
            .eq('group_id', state['group_id'])\
            .eq('has_media', True)\
            .is_not('media_filename', 'null')\
            .execute()
        
        state['messages_with_media'] = result.data
        print(f"✅ Found {len(result.data)} messages with media")
        return state
        
    except Exception as e:
        state['error'] = f"Failed to fetch media messages: {str(e)}"
        print(f"❌ {state['error']}")
        return state

def process_attachments(state: MediaProcessorState) -> MediaProcessorState:
    """Process each attachment: upload to storage, create thumbnails, extract metadata"""
    print(f"🖼️ Processing {len(state['messages_with_media'])} attachments")
    
    supabase = get_supabase_client()
    media_folder = Path(state['media_folder_path'])
    
    if not media_folder.exists():
        state['error'] = f"Media folder not found: {media_folder}"
        print(f"❌ {state['error']}")
        return state
    
    attachments = []
    total_size = 0
    
    for message in state['messages_with_media']:
        filename = message['media_filename']
        file_path = media_folder / filename
        
        if not file_path.exists():
            print(f"  ⚠️ File not found: {filename}")
            continue
        
        try:
            # Get file info
            file_size = file_path.stat().st_size
            total_size += file_size
            
            file_type = detect_file_type(filename)
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Upload to Supabase storage
            storage_path = f"{state['group_id']}/{filename}"
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to storage bucket
            upload_result = supabase.storage.from_('whatsapp-attachments')\
                .upload(storage_path, file_data, {
                    'content-type': mime_type or 'application/octet-stream'
                })
            
            # Get public URL (or signed URL if bucket is private)
            storage_url = supabase.storage.from_('whatsapp-attachments')\
                .get_public_url(storage_path)
            
            # Create attachment record
            attachment = {
                'message_id': message['id'],
                'group_id': state['group_id'],
                'original_filename': filename,
                'file_type': file_type,
                'file_extension': Path(filename).suffix[1:],
                'file_size_bytes': file_size,
                'mime_type': mime_type,
                'storage_path': storage_path,
                'storage_url': storage_url,
                'uploaded_by': message['sender_name'],
                'uploaded_at': message['message_timestamp'],
            }
            
            # Process based on file type
            if file_type == 'image':
                attachment = process_image(file_path, attachment, supabase, state['group_id'])
            elif file_type == 'video':
                attachment = process_video(file_path, attachment, supabase, state['group_id'])
            elif file_type == 'audio':
                attachment = process_audio(file_path, attachment)
            
            attachments.append(attachment)
            print(f"  ✅ Processed: {filename} ({file_size} bytes)")
            
        except Exception as e:
            print(f"  ❌ Failed to process {filename}: {str(e)}")
            continue
    
    state['processed_attachments'] = attachments
    state['total_attachments'] = len(attachments)
    state['total_size_bytes'] = total_size
    
    print(f"✅ Processed {len(attachments)} attachments ({total_size / 1024 / 1024:.2f} MB)")
    return state

def save_attachments_to_db(state: MediaProcessorState) -> MediaProcessorState:
    """Save attachment metadata to Supabase"""
    print(f"💾 Saving {len(state['processed_attachments'])} attachment records")
    
    try:
        supabase = get_supabase_client()
        
        # Batch insert
        batch_size = 500
        total_inserted = 0
        
        for i in range(0, len(state['processed_attachments']), batch_size):
            batch = state['processed_attachments'][i:i+batch_size]
            supabase.table('whatsapp_attachments').insert(batch).execute()
            total_inserted += len(batch)
            print(f"  ↳ Inserted {total_inserted}/{len(state['processed_attachments'])} records")
        
        print(f"✅ All attachment metadata saved")
        return state
        
    except Exception as e:
        state['error'] = f"Failed to save attachments: {str(e)}"
        print(f"❌ {state['error']}")
        return state

# ============================================================
# MEDIA-SPECIFIC PROCESSING
# ============================================================

def process_image(file_path: Path, attachment: Dict, supabase: Client, group_id: str) -> Dict:
    """Process image: create thumbnail, extract dimensions"""
    try:
        with Image.open(file_path) as img:
            # Get dimensions
            attachment['width'] = img.width
            attachment['height'] = img.height
            
            # Create thumbnail (max 300x300)
            img.thumbnail((300, 300))
            
            # Save thumbnail to temp file
            thumb_path = file_path.parent / f"thumb_{file_path.name}"
            img.save(thumb_path, format=img.format or 'JPEG')
            
            # Upload thumbnail
            thumb_storage_path = f"{group_id}/thumbnails/thumb_{file_path.name}"
            
            with open(thumb_path, 'rb') as f:
                thumb_data = f.read()
            
            supabase.storage.from_('whatsapp-attachments')\
                .upload(thumb_storage_path, thumb_data)
            
            attachment['thumbnail_path'] = thumb_storage_path
            
            # Clean up temp file
            thumb_path.unlink()
            
    except Exception as e:
        print(f"    ⚠️ Image processing failed: {str(e)}")
    
    return attachment

def process_video(file_path: Path, attachment: Dict, supabase: Client, group_id: str) -> Dict:
    """Process video: extract duration, dimensions, create thumbnail"""
    try:
        # Use ffprobe to get video metadata
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            metadata = json.loads(result.stdout)
            
            # Extract duration
            if 'format' in metadata and 'duration' in metadata['format']:
                attachment['duration_seconds'] = int(float(metadata['format']['duration']))
            
            # Extract dimensions from video stream
            for stream in metadata.get('streams', []):
                if stream.get('codec_type') == 'video':
                    attachment['width'] = stream.get('width')
                    attachment['height'] = stream.get('height')
                    break
            
            # Create thumbnail at 1 second mark
            thumb_path = file_path.parent / f"thumb_{file_path.stem}.jpg"
            
            thumb_cmd = [
                'ffmpeg',
                '-i', str(file_path),
                '-ss', '00:00:01',
                '-vframes', '1',
                '-vf', 'scale=300:-1',
                str(thumb_path)
            ]
            
            subprocess.run(thumb_cmd, capture_output=True)
            
            if thumb_path.exists():
                # Upload thumbnail
                thumb_storage_path = f"{group_id}/thumbnails/thumb_{file_path.stem}.jpg"
                
                with open(thumb_path, 'rb') as f:
                    thumb_data = f.read()
                
                supabase.storage.from_('whatsapp-attachments')\
                    .upload(thumb_storage_path, thumb_data)
                
                attachment['thumbnail_path'] = thumb_storage_path
                
                # Clean up
                thumb_path.unlink()
        
    except Exception as e:
        print(f"    ⚠️ Video processing failed: {str(e)}")
    
    return attachment

def process_audio(file_path: Path, attachment: Dict) -> Dict:
    """Process audio: extract duration"""
    try:
        # Use ffprobe for audio duration
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            str(file_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            metadata = json.loads(result.stdout)
            
            if 'format' in metadata and 'duration' in metadata['format']:
                attachment['duration_seconds'] = int(float(metadata['format']['duration']))
        
    except Exception as e:
        print(f"    ⚠️ Audio processing failed: {str(e)}")
    
    return attachment

# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

def create_media_processor_graph() -> StateGraph:
    """Create LangGraph workflow for media processing"""
    
    workflow = StateGraph(MediaProcessorState)
    
    # Add nodes
    workflow.add_node("fetch_media", fetch_media_messages)
    workflow.add_node("process", process_attachments)
    workflow.add_node("save", save_attachments_to_db)
    
    # Define flow
    workflow.set_entry_point("fetch_media")
    workflow.add_edge("fetch_media", "process")
    workflow.add_edge("process", "save")
    workflow.add_edge("save", END)
    
    return workflow.compile()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    """Run media processor agent standalone"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python media_processor_agent.py <group_id> <media_folder_path>")
        sys.exit(1)
    
    initial_state = {
        'group_id': sys.argv[1],
        'media_folder_path': sys.argv[2],
        'messages_with_media': [],
        'processed_attachments': [],
        'total_attachments': 0,
        'total_size_bytes': 0,
        'error': None,
    }
    
    graph = create_media_processor_graph()
    result = graph.invoke(initial_state)
    
    if result.get('error'):
        print(f"\n❌ FAILED: {result['error']}")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: Processed {result['total_attachments']} attachments")
        print(f"   Total size: {result['total_size_bytes'] / 1024 / 1024:.2f} MB")
