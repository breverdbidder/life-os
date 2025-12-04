"""
Life OS Cron Runner
Runs every 30 minutes to update metrics and check for interventions
"""
import os
import json
import requests
from datetime import datetime
from adhd_monitor import ADHDMonitor
from daily_report import DailyReportGenerator

class LifeOSCronRunner:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.monitor = ADHDMonitor()
        self.report_generator = DailyReportGenerator()
    
    def run_30min_cycle(self):
        """Main 30-minute cycle"""
        now = datetime.now()
        print(f"\n{'='*60}")
        print(f"🔄 LIFE OS CRON - {now.strftime('%Y-%m-%d %H:%M:%S')} EST")
        print(f"{'='*60}\n")
        
        # 1. Run ADHD monitoring
        print("🧠 Running ADHD Monitor...")
        interventions = self.monitor.run_monitoring_cycle()
        print(f"   Generated {len(interventions)} interventions")
        
        # 2. Update daily metrics
        print("\n📊 Updating daily metrics...")
        self._update_daily_metrics()
        
        # 3. Check for stale tasks (no update in 2+ hours)
        print("\n⏰ Checking for stale tasks...")
        stale_count = self._check_stale_tasks()
        print(f"   Found {stale_count} stale tasks")
        
        # 4. Log this cron run
        self._log_cron_run(len(interventions), stale_count)
        
        # 5. If end of day (after 9 PM), generate daily report
        if now.hour >= 21:
            print("\n📝 Generating end-of-day report...")
            report = self.report_generator.generate_report()
            print(self.report_generator.format_report_text(report))
        
        print(f"\n✅ Cron cycle complete at {datetime.now().strftime('%H:%M:%S')}")
        
        return {
            'timestamp': now.isoformat(),
            'interventions': len(interventions),
            'stale_tasks': stale_count
        }
    
    def _update_daily_metrics(self):
        """Update cumulative daily metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's task stats
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?initiated_at=gte.{today}T00:00:00",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        
        if r.status_code != 200:
            return
        
        tasks = r.json()
        
        completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        abandoned = len([t for t in tasks if t.get('status') == 'ABANDONED'])
        total = len(tasks)
        
        completion_rate = (completed / total) if total > 0 else 0
        abandonment_rate = (abandoned / total) if total > 0 else 0
        
        # Get intervention count
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_interventions?triggered_at=gte.{today}T00:00:00&select=id",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        intervention_count = len(r.json()) if r.status_code == 200 else 0
        
        # Upsert daily metrics
        metrics = {
            'user_id': 1,
            'date': today,
            'tasks_completed': completed,
            'tasks_abandoned': abandoned,
            'completion_rate': completion_rate,
            'abandonment_rate': abandonment_rate,
            'intervention_count': intervention_count,
            'created_at': datetime.now().isoformat()
        }
        
        r = requests.post(
            f"{self.supabase_url}/rest/v1/daily_metrics",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json=metrics,
            verify=False,
            timeout=30
        )
        
        print(f"   Tasks: {completed}/{total} completed, {intervention_count} interventions")
    
    def _check_stale_tasks(self) -> int:
        """Mark tasks as potentially abandoned if no update in 2+ hours"""
        two_hours_ago = (datetime.now() - __import__('datetime').timedelta(hours=2)).isoformat()
        
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?status=in.(INITIATED,SOLUTION_PROVIDED,IN_PROGRESS)&updated_at=lt.{two_hours_ago}",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        
        if r.status_code != 200:
            return 0
        
        stale_tasks = r.json()
        
        # Trigger Level 3 intervention for stale tasks
        for task in stale_tasks:
            intervention = {
                'user_id': 1,
                'task_id': task.get('task_id'),
                'task_description': task.get('description', 'Unknown')[:50],
                'intervention_type': 'STALE_TASK',
                'intervention_level': 3,
                'message': f"⚠️ STALE TASK: '{task.get('description', 'Task')[:40]}' has had no updates for 2+ hours. Status: {task.get('status')}. Take action or mark as abandoned.",
                'abandonment_probability': 0.85,
                'risk_level': 'HIGH',
                'triggered_at': datetime.now().isoformat(),
                'timestamp': datetime.now().isoformat()
            }
            
            requests.post(
                f"{self.supabase_url}/rest/v1/task_interventions",
                headers=self.headers,
                json=intervention,
                verify=False,
                timeout=30
            )
        
        return len(stale_tasks)
    
    def _log_cron_run(self, interventions: int, stale_tasks: int):
        """Log this cron run to activities"""
        log = {
            'user_id': 1,
            'activity_type': 'CRON_RUN',
            'platform': 'life_os',
            'domain': 'SYSTEM',
            'start_time': datetime.now().isoformat(),
            'notes': json.dumps({
                'type': '30min_cycle',
                'interventions_generated': interventions,
                'stale_tasks_found': stale_tasks,
                'timestamp': datetime.now().isoformat()
            }),
            'timezone': 'America/New_York'
        }
        
        requests.post(
            f"{self.supabase_url}/rest/v1/activities",
            headers=self.headers,
            json=log,
            verify=False,
            timeout=30
        )

if __name__ == "__main__":
    runner = LifeOSCronRunner()
    result = runner.run_30min_cycle()
    print(f"\nResult: {result}")
