"""
WhatsApp Parser Agent
Extracts messages, timestamps, senders, and metadata from WhatsApp chat export .txt files
Uses Gemini 2.5 Flash (FREE tier) via Smart Router for cost optimization
"""

import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
from dataclasses import dataclass, asdict

@dataclass
class ParsedMessage:
    """Structured message data"""
    timestamp: str  # ISO format
    sender: str
    message_text: str
    is_system_message: bool = False
    reply_to: Optional[str] = None
    has_media: bool = False
    media_filename: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class WhatsAppParserAgent:
    """
    Agent responsible for parsing WhatsApp chat export files
    
    Handles:
    - Multiple date/time formats
    - Multi-line messages
    - System messages (user joined, group created, etc.)
    - Media attachments
    - Emoji/unicode preservation
    - Reply chains (if present)
    """
    
    # Regex patterns for different WhatsApp export formats
    PATTERNS = {
        # Format: [1/1/26, 10:30:45 AM] Sender: Message
        'us_format': r'\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2}\s(?:AM|PM))\]\s([^:]+):\s(.*?)(?=\n\[|$)',
        
        # Format: [1/1/2026, 10:30] Sender: Message (24-hour)
        '24hour_format': r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\]\s([^:]+):\s(.*?)(?=\n\[|$)',
        
        # Format: 1/1/26, 10:30 AM - Sender: Message
        'dash_format': r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s(?:AM|PM))\s-\s([^:]+):\s(.*?)(?=\n\d|$)',
        
        # System messages (no sender)
        'system_message': r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM)?)\]\s(.*?)(?=\n\[|$)',
    }
    
    # Patterns for media attachments
    MEDIA_PATTERNS = {
        'attached': r'<attached:\s([^>]+)>',
        'omitted': r'\(file attached\)',
        'image': r'IMG[-_]\d{8}[-_]WA\d{4}\.(jpg|jpeg|png)',
        'video': r'VID[-_]\d{8}[-_]WA\d{4}\.(mp4|mov)',
        'audio': r'AUD[-_]\d{8}[-_]WA\d{4}\.(opus|m4a|mp3)',
        'document': r'DOC[-_]\d{8}[-_]WA\d{4}\.(pdf|docx|xlsx)',
    }
    
    # System message keywords
    SYSTEM_KEYWORDS = [
        'created group',
        'changed the subject',
        'changed this group\'s icon',
        'added',
        'left',
        'removed',
        'changed their phone number',
        'Messages and calls are end-to-end encrypted',
        'You\'re now an admin',
        'security code changed',
    ]
    
    def __init__(self):
        self.messages: List[ParsedMessage] = []
        self.parse_errors: List[Dict] = []
        self.detected_format: Optional[str] = None
        
    def parse_file(self, file_content: str, group_name: str = "Unknown") -> Dict:
        """
        Main parsing function
        
        Args:
            file_content: Raw text content from WhatsApp export
            group_name: Name of the group chat
            
        Returns:
            Dictionary with parsed messages and metadata
        """
        print(f"🔍 Parsing WhatsApp export for group: {group_name}")
        
        # Clean content
        file_content = self._clean_content(file_content)
        
        # Detect format
        self.detected_format = self._detect_format(file_content)
        print(f"📅 Detected format: {self.detected_format}")
        
        if not self.detected_format:
            return {
                'success': False,
                'error': 'Could not detect WhatsApp export format',
                'messages': []
            }
        
        # Parse messages
        self.messages = self._extract_messages(file_content)
        
        # Post-processing
        self._detect_media()
        self._detect_system_messages()
        self._link_replies()
        
        # Generate stats
        stats = self._generate_stats()
        
        print(f"✅ Parsed {len(self.messages)} messages")
        print(f"   - System messages: {stats['system_message_count']}")
        print(f"   - With media: {stats['media_count']}")
        print(f"   - Unique senders: {stats['unique_senders']}")
        
        return {
            'success': True,
            'group_name': group_name,
            'detected_format': self.detected_format,
            'messages': [msg.to_dict() for msg in self.messages],
            'stats': stats,
            'parse_errors': self.parse_errors
        }
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize file content"""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
        
        return content
    
    def _detect_format(self, content: str) -> Optional[str]:
        """Detect WhatsApp export format by testing patterns"""
        sample = content[:5000]  # Test first 5000 chars
        
        for format_name, pattern in self.PATTERNS.items():
            if format_name == 'system_message':
                continue
            matches = re.findall(pattern, sample, re.DOTALL)
            if len(matches) >= 3:  # Need at least 3 matches to confirm
                return format_name
        
        return None
    
    def _extract_messages(self, content: str) -> List[ParsedMessage]:
        """Extract messages using detected format"""
        messages = []
        pattern = self.PATTERNS[self.detected_format]
        
        # Split into lines for multi-line handling
        lines = content.split('\n')
        current_message = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match as new message
            match = re.match(pattern, line, re.DOTALL)
            
            if match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                # Extract components
                date_str, time_str, sender, text = match.groups()
                
                # Parse timestamp
                timestamp = self._parse_timestamp(date_str, time_str)
                
                # Create new message
                current_message = ParsedMessage(
                    timestamp=timestamp,
                    sender=sender.strip(),
                    message_text=text.strip(),
                )
            elif current_message:
                # Multi-line message continuation
                current_message.message_text += '\n' + line
        
        # Add last message
        if current_message:
            messages.append(current_message)
        
        return messages
    
    def _parse_timestamp(self, date_str: str, time_str: str) -> str:
        """Convert WhatsApp timestamp to ISO format"""
        try:
            # Combine date and time
            datetime_str = f"{date_str} {time_str}"
            
            # Try different formats
            formats = [
                '%m/%d/%y %I:%M:%S %p',  # 1/1/26 10:30:45 AM
                '%m/%d/%Y %I:%M:%S %p',  # 1/1/2026 10:30:45 AM
                '%m/%d/%y %H:%M',        # 1/1/26 22:30
                '%m/%d/%Y %H:%M',        # 1/1/2026 22:30
                '%m/%d/%y %I:%M %p',     # 1/1/26 10:30 AM
                '%m/%d/%Y %I:%M %p',     # 1/1/2026 10:30 AM
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(datetime_str, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            # If no format worked, log error
            self.parse_errors.append({
                'type': 'timestamp_parse_error',
                'value': datetime_str
            })
            return datetime.now().isoformat()
            
        except Exception as e:
            self.parse_errors.append({
                'type': 'timestamp_parse_error',
                'error': str(e),
                'value': f"{date_str} {time_str}"
            })
            return datetime.now().isoformat()
    
    def _detect_media(self):
        """Detect media attachments in messages"""
        for msg in self.messages:
            # Check for media patterns
            for pattern_name, pattern in self.MEDIA_PATTERNS.items():
                match = re.search(pattern, msg.message_text, re.IGNORECASE)
                if match:
                    msg.has_media = True
                    if pattern_name == 'attached':
                        msg.media_filename = match.group(1)
                    elif pattern_name in ['image', 'video', 'audio', 'document']:
                        msg.media_filename = match.group(0)
                    break
    
    def _detect_system_messages(self):
        """Identify system/administrative messages"""
        for msg in self.messages:
            # Check if sender is a system keyword
            if any(keyword in msg.message_text.lower() for keyword in self.SYSTEM_KEYWORDS):
                msg.is_system_message = True
            
            # WhatsApp system messages often have no colon in sender
            if ':' not in msg.message_text and len(msg.sender.split()) > 3:
                msg.is_system_message = True
    
    def _link_replies(self):
        """
        Attempt to detect reply chains
        WhatsApp doesn't always export reply metadata, so this is best-effort
        """
        # This is a placeholder - WhatsApp export format doesn't include reply metadata
        # Could be enhanced by analyzing message proximity and content patterns
        pass
    
    def _generate_stats(self) -> Dict:
        """Generate parsing statistics"""
        total = len(self.messages)
        system_msgs = sum(1 for msg in self.messages if msg.is_system_message)
        media_msgs = sum(1 for msg in self.messages if msg.has_media)
        unique_senders = len(set(msg.sender for msg in self.messages if not msg.is_system_message))
        
        # Date range
        timestamps = [datetime.fromisoformat(msg.timestamp) for msg in self.messages]
        date_range_start = min(timestamps).isoformat() if timestamps else None
        date_range_end = max(timestamps).isoformat() if timestamps else None
        
        return {
            'total_messages': total,
            'system_message_count': system_msgs,
            'media_count': media_msgs,
            'unique_senders': unique_senders,
            'date_range_start': date_range_start,
            'date_range_end': date_range_end,
            'parse_errors': len(self.parse_errors)
        }


def parse_whatsapp_export(file_path: str, group_name: str = "Unknown") -> Dict:
    """
    Convenience function to parse WhatsApp export file
    
    Args:
        file_path: Path to .txt file from WhatsApp export
        group_name: Name of the group
        
    Returns:
        Parsing results with messages and stats
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = WhatsAppParserAgent()
    return parser.parse_file(content, group_name)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Example usage
    sample_content = """[1/1/26, 10:30:45 AM] John Doe: Hey everyone!
[1/1/26, 10:31:12 AM] Jane Smith: Hi John! How are you?
[1/1/26, 10:31:45 AM] John Doe: I'm good, thanks!
Check out this link: https://example.com
[1/1/26, 10:32:00 AM] John Doe: <attached: IMG-20260101-WA0001.jpg>
[1/1/26, 10:33:00 AM] System: Jane Smith added Bob Johnson
[1/1/26, 10:35:00 AM] Bob Johnson: Thanks for adding me!"""
    
    parser = WhatsAppParserAgent()
    result = parser.parse_file(sample_content, "Test Group")
    
    print(json.dumps(result, indent=2))
