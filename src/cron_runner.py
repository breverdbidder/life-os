"""
Life OS Cron Runner
Runs every 30 minutes to update metrics and check for interventions
Includes XGBoost Daily Focus Score calculation
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta

# Add scripts directory to path for FocusPredictor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from focus_monitor import FocusMonitor
from daily_report import DailyReportGenerator

try:
    from life_os_engine import FocusPredictor
except ImportError:
    FocusPredictor = None

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
        self.monitor = FocusMonitor()
        self.report_generator = DailyReportGenerator()
    
    def run_30min_cycle(self):
        """Main 30-minute cycle"""
        now = datetime.now()
        print(f"\n{'='*60}")
        print(f"🔄 LIFE OS CRON - {now.strftime('%Y-%m-%d %H:%M:%S')} EST")
        print(f"{'='*60}\n")
        
        # 1. Run focus monitoring
        print("🧠 Running FOCUS Monitor...")
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
        """Update cumulative daily metrics with XGBoost Focus Score"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's task stats
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?initiated_at=gte.{today}T00:00:00",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        
        if r.status_code != 200:
            print(f"   ❌ Failed to fetch tasks: {r.status_code}")
            return
        
        tasks = r.json()
        
        completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        abandoned = len([t for t in tasks if t.get('status') == 'ABANDONED'])
        total = len(tasks)
        
        completion_rate = (completed / total) if total > 0 else 0
        abandonment_rate = (abandoned / total) if total > 0 else 0
        
        # Calculate average complexity of completed tasks
        completed_tasks = [t for t in tasks if t.get('status') == 'COMPLETED']
        avg_complexity = sum(t.get('complexity', 5) for t in completed_tasks) / len(completed_tasks) if completed_tasks else 5
        
        # Calculate average focus quality
        avg_focus_quality = sum(t.get('focus_quality', 5) for t in tasks) / len(tasks) if tasks else 5
        
        # Get context switches count
        r = requests.get(
            f"{self.supabase_url}/rest/v1/activities?activity_type=eq.CONTEXT_SWITCH&start_time=gte.{today}T00:00:00&select=id",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        context_switches = len(r.json()) if r.status_code == 200 else 0
        
        # Get intervention count
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_interventions?triggered_at=gte.{today}T00:00:00&select=id",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        intervention_count = len(r.json()) if r.status_code == 200 else 0
        
        # Calculate time efficiency (actual / estimated)
        time_efficiency = 1.0
        if completed_tasks:
            total_estimated = sum(t.get('estimated_minutes', 30) for t in completed_tasks)
            total_actual = sum(t.get('actual_minutes', t.get('estimated_minutes', 30)) for t in completed_tasks)
            time_efficiency = total_actual / total_estimated if total_estimated > 0 else 1.0
        
        # Calculate productivity streak
        streak = self._calculate_productivity_streak(today)
        
        # Calculate XGBoost Daily Focus Score
        focus_score = 50  # Default
        focus_grade = "C"
        focus_breakdown = {}
        
        if FocusPredictor:
            score_result = FocusPredictor.calculate_daily_focus_score(
                tasks_completed=completed,
                tasks_abandoned=abandoned,
                tasks_total=total,
                avg_focus_quality=avg_focus_quality,
                avg_complexity_completed=avg_complexity,
                context_switches=context_switches,
                time_efficiency=time_efficiency,
                consecutive_productive_days=streak,
                interventions_triggered=intervention_count
            )
            focus_score = score_result.get('score', 50)
            focus_grade = score_result.get('grade', 'C')
            focus_breakdown = score_result.get('feature_breakdown', {})
            
            print(f"   🧠 XGBoost Focus Score: {focus_score} ({focus_grade})")
        else:
            print(f"   ⚠️ FocusPredictor not available, using default score")
        
        # Upsert daily metrics with Focus Score
        metrics = {
            'user_id': 1,
            'date': today,
            'tasks_completed': completed,
            'tasks_abandoned': abandoned,
            'completion_rate': round(completion_rate, 3),
            'abandonment_rate': round(abandonment_rate, 3),
            'intervention_count': intervention_count,
            'context_switches': context_switches,
            'average_focus_quality': round(avg_focus_quality, 2),
            'average_complexity': round(avg_complexity, 2),
            'time_efficiency': round(time_efficiency, 3),
            'productivity_streak': streak,
            'focus_score': focus_score,
            'focus_grade': focus_grade,
            'focus_breakdown': json.dumps(focus_breakdown),
            'updated_at': datetime.now().isoformat()
        }
        
        r = requests.post(
            f"{self.supabase_url}/rest/v1/daily_metrics",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json=metrics,
            verify=False,
            timeout=30
        )
        
        if r.status_code in [200, 201]:
            print(f"   ✅ Tasks: {completed}/{total} completed, Focus Score: {focus_score} ({focus_grade})")
        else:
            print(f"   ❌ Failed to save metrics: {r.status_code}")
    
    def _calculate_productivity_streak(self, today: str) -> int:
        """Calculate consecutive days with focus_score >= 70"""
        streak = 0
        check_date = datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)
        
        for _ in range(30):  # Check up to 30 days back
            date_str = check_date.strftime("%Y-%m-%d")
            r = requests.get(
                f"{self.supabase_url}/rest/v1/daily_metrics?date=eq.{date_str}&select=focus_score",
                headers=self.headers,
                verify=False,
                timeout=10
            )
            
            if r.status_code != 200:
                break
                
            data = r.json()
            if not data or data[0].get('focus_score', 0) < 70:
                break
            
            streak += 1
            check_date -= timedelta(days=1)
        
        return streak
    
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
