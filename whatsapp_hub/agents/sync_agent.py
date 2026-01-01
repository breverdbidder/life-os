"""
WhatsApp Sync Agent
Syncs all extracted data to Supabase: messages, links, attachments, groups
"""

import os
from typing import Dict, List
from datetime import datetime
from supabase import create_client, Client

class SupabaseSync:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.url = supabase_url or os.getenv('SUPABASE_URL')
        self.key = supabase_key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required")
        
        self.client: Client = create_client(self.url, self.key)
        self.group_id = None
    
    def sync_all(self, state: Dict) -> Dict:
        """Sync all parsed data to Supabase"""
        
        print("🔄 Syncing to Supabase...")
        
        # 1. Create group record
        self.group_id = self._sync_group(state['parsed_data'])
        
        # 2. Insert messages
        message_ids = self._sync_messages(state['parsed_data']['messages'])
        
        # 3. Insert links
        if 'extracted_links' in state:
            self._sync_links(state['extracted_links'], message_ids)
        
        # 4. Insert attachments
        if 'processed_attachments' in state:
            self._sync_attachments(state['processed_attachments'])
        
        # 5. Log processing completion
        self._log_completion(state)
        
        print(f"✅ Sync complete. Group ID: {self.group_id}")
        
        return {
            'group_id': self.group_id,
            'synced_messages': len(message_ids),
            'synced_links': len(state.get('extracted_links', [])),
            'synced_attachments': len(state.get('processed_attachments', []))
        }
    
    def _sync_group(self, parsed_data: Dict) -> str:
        """Create group record"""
        
        date_range = parsed_data.get('date_range', (None, None))
        
        group_data = {
            'group_name': parsed_data['group_name'],
            'export_date': datetime.now().isoformat(),
            'participant_count': len(parsed_data.get('participants', [])),
            'message_count': parsed_data['stats'].get('total_messages', 0),
            'date_range_start': date_range[0].isoformat() if date_range[0] else None,
            'date_range_end': date_range[1].isoformat() if date_range[1] else None
        }
        
        result = self.client.table('whatsapp_groups').insert(group_data).execute()
        return result.data[0]['id']
    
    def _sync_messages(self, messages: List) -> Dict[str, str]:
        """Insert messages and return filename->id mapping"""
        
        print(f"  📝 Inserting {len(messages)} messages...")
        
        message_records = []
        message_id_map = {}
        
        for msg in messages:
            record = {
                'group_id': self.group_id,
                'message_timestamp': msg.timestamp.isoformat(),
                'sender_name': msg.sender_name,
                'message_text': msg.message_text,
                'is_system_message': msg.is_system_message,
                'has_attachments': msg.has_attachments,
                'message_type': msg.message_type
            }
            message_records.append(record)
        
        # Batch insert
        result = self.client.table('whatsapp_messages').insert(message_records).execute()
        
        # Build mapping
        for i, msg in enumerate(messages):
            if msg.attachment_filename:
                message_id_map[msg.attachment_filename] = result.data[i]['id']
        
        return message_id_map
    
    def _sync_links(self, links: List[Dict], message_ids: Dict):
        """Insert extracted links"""
        
        if not links:
            return
        
        print(f"  🔗 Inserting {len(links)} links...")
        
        link_records = []
        for link in links:
            record = {
                'group_id': self.group_id,
                'url': link['url'],
                'domain': link['domain'],
                'title': link.get('title'),
                'description': link.get('description'),
                'shared_by': link['shared_by'],
                'shared_at': link['shared_at'],
                'link_type': link.get('link_type', 'other'),
                'is_dead_link': link.get('is_dead_link', False)
            }
            link_records.append(record)
        
        self.client.table('whatsapp_links').insert(link_records).execute()
    
    def _sync_attachments(self, attachments: List[Dict]):
        """Insert processed attachments"""
        
        if not attachments:
            return
        
        print(f"  📎 Inserting {len(attachments)} attachments...")
        
        att_records = []
        for att in attachments:
            record = {
                'group_id': self.group_id,
                'original_filename': att['original_filename'],
                'file_type': att['file_type'],
                'file_extension': att['file_extension'],
                'file_size_bytes': att['file_size_bytes'],
                'mime_type': att['mime_type'],
                'storage_path': att['storage_path'],
                'thumbnail_path': att.get('thumbnail_path'),
                'width': att.get('width'),
                'height': att.get('height'),
                'shared_by': att['shared_by'],
                'shared_at': att['shared_at'],
                'checksum': att.get('checksum'),
                'is_duplicate': att.get('is_duplicate', False)
            }
            att_records.append(record)
        
        self.client.table('whatsapp_attachments').insert(att_records).execute()
    
    def _log_completion(self, state: Dict):
        """Log processing completion"""
        
        log_data = {
            'group_id': self.group_id,
            'agent_name': 'sync',
            'stage': 'completed',
            'messages_processed': len(state['parsed_data']['messages']),
            'links_extracted': len(state.get('extracted_links', [])),
            'attachments_processed': len(state.get('processed_attachments', [])),
            'execution_time_seconds': state.get('total_execution_time', 0)
        }
        
        self.client.table('whatsapp_processing_logs').insert(log_data).execute()

def sync_agent_node(state: Dict) -> Dict:
    """LangGraph sync node"""
    
    syncer = SupabaseSync()
    sync_result = syncer.sync_all(state)
    
    return {
        **state,
        'sync_result': sync_result,
        'next_agent': None,  # End of pipeline
        'sync_complete': True
    }
