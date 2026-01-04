"""
Life OS RSS Exporter
Generates RSS 2.0 feed from Supabase task_states table
Filters: ABANDONED + BLOCKED only (for ADHD interventions)
Updates: Every 30min via GitHub Actions
Cost: $0
"""

import os
import json
import requests
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import List, Dict

class LifeOSRSSExporter:
    """Export Life OS tasks as RSS 2.0 for Make.com automation"""
    
    def __init__(self):
        self.supabase_url = os.getenv(
            "SUPABASE_URL", 
            "https://mocerqjnksmhcjzxrewo.supabase.co"
        )
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_key:
            raise ValueError("SUPABASE_KEY environment variable required")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        self.base_url = "https://life-os-aiy.pages.dev"
    
    def fetch_intervention_tasks(self, hours_back: int = 24) -> List[Dict]:
        """
        Fetch ABANDONED and BLOCKED tasks from last N hours
        
        Args:
            hours_back: How far back to look (default 24 hours)
        
        Returns:
            List of task dictionaries
        """
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        # Query Supabase for ABANDONED or BLOCKED tasks
        params = {
            "status": f"in.(ABANDONED,BLOCKED)",
            "updated_at": f"gte.{cutoff_time}",
            "order": "updated_at.desc",
            "limit": "50"
        }
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/task_states",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                tasks = response.json()
                print(f"✅ Fetched {len(tasks)} intervention tasks")
                return tasks
            else:
                print(f"❌ Failed to fetch tasks: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching tasks: {e}")
            return []
    
    def generate_rss_xml(self, tasks: List[Dict]) -> str:
        """
        Generate RSS 2.0 XML from task list
        
        Args:
            tasks: List of task dictionaries
        
        Returns:
            Pretty-printed XML string
        """
        # Create RSS root
        rss = Element('rss', version='2.0', attrib={
            'xmlns:atom': 'http://www.w3.org/2005/Atom'
        })
        
        channel = SubElement(rss, 'channel')
        
        # Channel metadata
        SubElement(channel, 'title').text = 'Ariel Shapira Life OS - Task Interventions'
        SubElement(channel, 'link').text = self.base_url
        SubElement(channel, 'description').text = (
            'ADHD intervention feed: ABANDONED and BLOCKED tasks requiring attention'
        )
        SubElement(channel, 'language').text = 'en-us'
        SubElement(channel, 'lastBuildDate').text = datetime.now().strftime(
            '%a, %d %b %Y %H:%M:%S +0000'
        )
        
        # Self-referencing atom:link (required for RSS 2.0 validation)
        SubElement(channel, '{http://www.w3.org/2005/Atom}link', attrib={
            'href': f'{self.base_url}/rss.xml',
            'rel': 'self',
            'type': 'application/rss+xml'
        })
        
        # Add items
        for task in tasks:
            self._add_task_item(channel, task)
        
        # Pretty print XML
        rough_string = tostring(rss, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    def _add_task_item(self, channel: Element, task: Dict):
        """Add single task as RSS item"""
        
        item = SubElement(channel, 'item')
        
        # Title with emoji indicator
        status = task.get('status', 'UNKNOWN')
        emoji = '⚠️' if status == 'ABANDONED' else '🚫'
        title = f"{emoji} {status}: {task.get('description', 'No description')[:60]}"
        SubElement(item, 'title').text = title
        
        # Description with full task details
        duration = self._calculate_duration(task)
        description = f"""
Task: {task.get('description', 'No description')}
Status: {status}
Domain: {task.get('domain', 'UNKNOWN')}
Complexity: {task.get('complexity', 'N/A')}/10
Clarity: {task.get('clarity', 'N/A')}/10
Estimated Time: {task.get('estimated_minutes', 'N/A')} minutes
Started: {task.get('initiated_at', 'Unknown')}
Last Updated: {task.get('updated_at', 'Unknown')}
Duration Since Start: {duration}

This task requires intervention - it has been {status.lower()} and needs attention.
        """.strip()
        
        SubElement(item, 'description').text = description
        
        # GUID (unique identifier)
        guid = SubElement(item, 'guid', isPermaLink='false')
        guid.text = f"lifeos_{task.get('task_id', 'unknown')}"
        
        # Publication date (use updated_at)
        pub_date = self._format_rfc822_date(task.get('updated_at'))
        SubElement(item, 'pubDate').text = pub_date
        
        # Category (domain)
        SubElement(item, 'category').text = task.get('domain', 'UNKNOWN')
        
        # Link (to Life OS dashboard with task filter)
        task_id = task.get('task_id', '')
        SubElement(item, 'link').text = f"{self.base_url}?task={task_id}"
    
    def _calculate_duration(self, task: Dict) -> str:
        """Calculate human-readable duration since task initiated"""
        try:
            initiated = datetime.fromisoformat(task.get('initiated_at', ''))
            now = datetime.now()
            delta = now - initiated
            
            if delta.days > 0:
                return f"{delta.days} day(s)"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour(s)"
            else:
                minutes = delta.seconds // 60
                return f"{minutes} minute(s)"
        except:
            return "Unknown"
    
    def _format_rfc822_date(self, iso_date: str) -> str:
        """Convert ISO date to RFC 822 format for RSS"""
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except:
            return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    def generate_daily_summary(self, tasks_all: List[Dict]) -> Dict:
        """
        Generate daily summary statistics
        
        Args:
            tasks_all: All tasks from today
        
        Returns:
            Dictionary with summary stats
        """
        today = datetime.now().date()
        today_tasks = [
            t for t in tasks_all 
            if datetime.fromisoformat(t.get('initiated_at', '')).date() == today
        ]
        
        completed = [t for t in today_tasks if t.get('status') == 'COMPLETED']
        abandoned = [t for t in today_tasks if t.get('status') == 'ABANDONED']
        blocked = [t for t in today_tasks if t.get('status') == 'BLOCKED']
        
        total_actionable = len(completed) + len(abandoned) + len(blocked)
        completion_rate = (
            (len(completed) / total_actionable * 100) if total_actionable > 0 else 0
        )
        
        return {
            'date': today.isoformat(),
            'completed': len(completed),
            'abandoned': len(abandoned),
            'blocked': len(blocked),
            'completion_rate': f"{completion_rate:.1f}%",
            'domains': {
                'BUSINESS': sum(1 for t in completed if t.get('domain') == 'BUSINESS'),
                'MICHAEL': sum(1 for t in completed if t.get('domain') == 'MICHAEL'),
                'FAMILY': sum(1 for t in completed if t.get('domain') == 'FAMILY'),
                'ARIEL': sum(1 for t in completed if t.get('domain') == 'ARIEL')
            }
        }
    
    def export_to_file(self, output_path: str = 'public/rss.xml', hours_back: int = 24):
        """
        Main export function: Fetch tasks and generate RSS file
        
        Args:
            output_path: Where to write RSS XML
            hours_back: How far back to look for tasks
        """
        print(f"\n{'='*60}")
        print("Life OS RSS Exporter")
        print(f"{'='*60}\n")
        
        # Fetch intervention tasks
        tasks = self.fetch_intervention_tasks(hours_back)
        
        if not tasks:
            print("⚠️  No intervention tasks found - generating empty feed")
        
        # Generate RSS XML
        rss_xml = self.generate_rss_xml(tasks)
        
        # Write to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rss_xml)
        
        print(f"✅ RSS feed generated: {output_path}")
        print(f"📊 Items: {len(tasks)}")
        print(f"🔗 URL: {self.base_url}/rss.xml")
        
        # Also generate JSON summary for debugging
        summary_path = output_path.replace('.xml', '_summary.json')
        with open(summary_path, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'task_count': len(tasks),
                'tasks': tasks
            }, f, indent=2)
        
        print(f"📝 Debug summary: {summary_path}\n")

if __name__ == "__main__":
    # Run exporter
    exporter = LifeOSRSSExporter()
    exporter.export_to_file(
        output_path='public/rss.xml',
        hours_back=24  # Last 24 hours of ABANDONED/BLOCKED tasks
    )
