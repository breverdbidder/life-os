"""
Life OS Daily Report Generator
Generates comprehensive end-of-day reports with focus insights
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List

class DailyReportGenerator:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def get_day_tasks(self, date: str = None) -> List[dict]:
        """Get all tasks for a specific day"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?initiated_at=gte.{date}T00:00:00&initiated_at=lt.{date}T23:59:59&order=initiated_at.asc",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def get_day_interventions(self, date: str = None) -> List[dict]:
        """Get all interventions for a specific day"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_interventions?triggered_at=gte.{date}T00:00:00&triggered_at=lt.{date}T23:59:59&order=triggered_at.asc",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def get_day_activities(self, date: str = None) -> List[dict]:
        """Get all activities for a specific day"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        r = requests.get(
            f"{self.supabase_url}/rest/v1/activities?start_time=gte.{date}T00:00:00&start_time=lt.{date}T23:59:59&order=start_time.asc",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def calculate_metrics(self, tasks: List[dict], interventions: List[dict], 
                         activities: List[dict]) -> dict:
        """Calculate daily metrics from raw data"""
        
        # Task metrics
        total_tasks = len(tasks)
        completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        abandoned = len([t for t in tasks if t.get('status') == 'ABANDONED'])
        in_progress = len([t for t in tasks if t.get('status') in ['INITIATED', 'SOLUTION_PROVIDED', 'IN_PROGRESS']])
        
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        abandonment_rate = (abandoned / total_tasks * 100) if total_tasks > 0 else 0
        
        # Domain breakdown
        domains = {}
        for t in tasks:
            domain = t.get('domain', 'UNKNOWN')
            if domain not in domains:
                domains[domain] = {'total': 0, 'completed': 0, 'abandoned': 0}
            domains[domain]['total'] += 1
            if t.get('status') == 'COMPLETED':
                domains[domain]['completed'] += 1
            elif t.get('status') == 'ABANDONED':
                domains[domain]['abandoned'] += 1
        
        # Time metrics
        total_estimated = sum(t.get('estimated_minutes', 0) for t in tasks)
        
        # Actual time for completed tasks
        total_actual = 0
        for t in tasks:
            if t.get('status') == 'COMPLETED' and t.get('initiated_at') and t.get('completed_at'):
                try:
                    start = datetime.fromisoformat(t['initiated_at'].replace('Z', ''))
                    end = datetime.fromisoformat(t['completed_at'].replace('Z', ''))
                    total_actual += (end - start).total_seconds() / 60
                except:
                    pass
        
        # Intervention metrics
        total_interventions = len(interventions)
        intervention_by_level = {1: 0, 2: 0, 3: 0}
        successful_interventions = 0
        
        for i in interventions:
            level = i.get('intervention_level', 1)
            intervention_by_level[level] = intervention_by_level.get(level, 0) + 1
            if i.get('successful'):
                successful_interventions += 1
        
        # Activity metrics
        context_switches = sum(a.get('context_switches', 0) for a in activities)
        avg_focus = sum(a.get('focus_quality', 7) for a in activities) / len(activities) if activities else 7
        avg_energy = sum(a.get('energy_level', 7) for a in activities) / len(activities) if activities else 7
        
        # Calculate productivity score (0-100)
        productivity_score = min(100, (
            completion_rate * 0.4 +
            (100 - abandonment_rate) * 0.2 +
            avg_focus * 10 * 0.2 +
            avg_energy * 10 * 0.1 +
            (100 - min(context_switches, 20) * 5) * 0.1
        ))
        
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'total_tasks': total_tasks,
            'completed': completed,
            'abandoned': abandoned,
            'in_progress': in_progress,
            'completion_rate': round(completion_rate, 1),
            'abandonment_rate': round(abandonment_rate, 1),
            'productivity_score': round(productivity_score, 1),
            'domains': domains,
            'total_estimated_minutes': total_estimated,
            'total_actual_minutes': round(total_actual, 1),
            'total_interventions': total_interventions,
            'interventions_by_level': intervention_by_level,
            'successful_interventions': successful_interventions,
            'context_switches': context_switches,
            'avg_focus_quality': round(avg_focus, 1),
            'avg_energy_level': round(avg_energy, 1)
        }
    
    def generate_timeline(self, tasks: List[dict], interventions: List[dict]) -> List[dict]:
        """Generate chronological timeline of the day"""
        timeline = []
        
        for t in tasks:
            if t.get('initiated_at'):
                timeline.append({
                    'time': t['initiated_at'],
                    'type': 'TASK_START',
                    'description': t.get('description', 'Unknown task'),
                    'domain': t.get('domain'),
                    'status': t.get('status')
                })
            
            if t.get('completed_at'):
                timeline.append({
                    'time': t['completed_at'],
                    'type': 'TASK_COMPLETE',
                    'description': t.get('description', 'Unknown task'),
                    'domain': t.get('domain')
                })
            
            if t.get('abandoned_at'):
                timeline.append({
                    'time': t['abandoned_at'],
                    'type': 'TASK_ABANDONED',
                    'description': t.get('description', 'Unknown task'),
                    'domain': t.get('domain')
                })
        
        for i in interventions:
            if i.get('triggered_at'):
                timeline.append({
                    'time': i['triggered_at'],
                    'type': f"INTERVENTION_L{i.get('intervention_level', 1)}",
                    'description': i.get('task_description', 'Unknown'),
                    'message': i.get('message', ''),
                    'risk_level': i.get('risk_level')
                })
        
        # Sort by time
        timeline.sort(key=lambda x: x.get('time', ''))
        
        return timeline
    
    def generate_insights(self, metrics: dict, timeline: List[dict]) -> List[str]:
        """Generate focus-specific insights from the day's data"""
        insights = []
        
        # Completion rate insight
        if metrics['completion_rate'] >= 80:
            insights.append(f"🌟 Excellent completion rate ({metrics['completion_rate']}%)! Your focus strategies are working.")
        elif metrics['completion_rate'] >= 50:
            insights.append(f"📊 Moderate completion rate ({metrics['completion_rate']}%). Consider breaking tasks smaller tomorrow.")
        else:
            insights.append(f"⚠️ Low completion rate ({metrics['completion_rate']}%). Let's identify blockers and adjust complexity.")
        
        # Abandonment pattern
        if metrics['abandonment_rate'] > 30:
            insights.append(f"🔴 High abandonment rate ({metrics['abandonment_rate']}%). Pattern: Check if tasks are too complex or unclear.")
        
        # Intervention effectiveness
        if metrics['total_interventions'] > 0:
            if metrics['successful_interventions'] / metrics['total_interventions'] > 0.5:
                insights.append(f"✅ Interventions working! {metrics['successful_interventions']}/{metrics['total_interventions']} led to task completion.")
            else:
                insights.append(f"💡 Interventions need adjustment. Only {metrics['successful_interventions']}/{metrics['total_interventions']} were effective.")
        
        # Domain performance
        for domain, stats in metrics.get('domains', {}).items():
            if stats['total'] > 0:
                domain_rate = stats['completed'] / stats['total'] * 100
                if domain_rate < 50:
                    insights.append(f"📌 {domain} domain needs attention: only {domain_rate:.0f}% completion rate.")
        
        # Time estimation
        if metrics['total_estimated_minutes'] > 0 and metrics['total_actual_minutes'] > 0:
            ratio = metrics['total_actual_minutes'] / metrics['total_estimated_minutes']
            if ratio > 1.5:
                insights.append(f"⏰ Tasks taking {ratio:.1f}x longer than estimated. Adjust future estimates upward.")
            elif ratio < 0.7:
                insights.append(f"⚡ Completing tasks faster than estimated ({ratio:.1f}x). You may be underestimating yourself!")
        
        # Focus quality
        if metrics['avg_focus_quality'] < 5:
            insights.append("🧠 Low focus quality today. Consider: sleep, breaks, environment changes.")
        
        # Context switches
        if metrics['context_switches'] > 10:
            insights.append(f"🔄 High context switches ({metrics['context_switches']}). Try time-blocking tomorrow.")
        
        return insights
    
    def generate_report(self, date: str = None) -> dict:
        """Generate complete daily report"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"📊 Generating report for {date}...")
        
        tasks = self.get_day_tasks(date)
        interventions = self.get_day_interventions(date)
        activities = self.get_day_activities(date)
        
        print(f"   Tasks: {len(tasks)}, Interventions: {len(interventions)}, Activities: {len(activities)}")
        
        metrics = self.calculate_metrics(tasks, interventions, activities)
        timeline = self.generate_timeline(tasks, interventions)
        insights = self.generate_insights(metrics, timeline)
        
        report = {
            'report_date': date,
            'generated_at': datetime.now().isoformat(),
            'metrics': metrics,
            'timeline': timeline,
            'insights': insights,
            'task_details': tasks,
            'intervention_details': interventions
        }
        
        # Save to daily_metrics
        self._save_daily_metrics(metrics)
        
        return report
    
    def _save_daily_metrics(self, metrics: dict) -> bool:
        """Save metrics to daily_metrics table"""
        data = {
            'user_id': 1,
            'date': metrics['date'],
            'tasks_completed': metrics['completed'],
            'tasks_abandoned': metrics['abandoned'],
            'completion_rate': metrics['completion_rate'] / 100,
            'abandonment_rate': metrics['abandonment_rate'] / 100,
            'productivity_score': metrics['productivity_score'],
            'average_focus_quality': metrics['avg_focus_quality'],
            'energy_average': metrics['avg_energy_level'],
            'context_switches': metrics['context_switches'],
            'intervention_count': metrics['total_interventions'],
            'domains': json.dumps(metrics['domains']),
            'created_at': datetime.now().isoformat()
        }
        
        # Upsert
        r = requests.post(
            f"{self.supabase_url}/rest/v1/daily_metrics",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json=data,
            verify=False,
            timeout=30
        )
        
        return r.status_code in [200, 201]
    
    def format_report_text(self, report: dict) -> str:
        """Format report as readable text"""
        m = report['metrics']
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║            LIFE OS DAILY REPORT - {report['report_date']}              ║
╚══════════════════════════════════════════════════════════════╝

📊 SUMMARY
───────────────────────────────────────────────────────────────
  Productivity Score: {m['productivity_score']}/100
  Tasks: {m['completed']}/{m['total_tasks']} completed ({m['completion_rate']}%)
  Abandoned: {m['abandoned']} ({m['abandonment_rate']}%)
  Still Active: {m['in_progress']}

⏱️ TIME
───────────────────────────────────────────────────────────────
  Estimated: {m['total_estimated_minutes']} minutes
  Actual: {m['total_actual_minutes']} minutes
  
🧠 FOCUS METRICS
───────────────────────────────────────────────────────────────
  Focus Quality: {m['avg_focus_quality']}/10
  Energy Level: {m['avg_energy_level']}/10
  Context Switches: {m['context_switches']}
  Interventions: {m['total_interventions']} (L1:{m['interventions_by_level'][1]}, L2:{m['interventions_by_level'][2]}, L3:{m['interventions_by_level'][3]})

📁 BY DOMAIN
───────────────────────────────────────────────────────────────"""
        
        for domain, stats in m.get('domains', {}).items():
            rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            text += f"\n  {domain}: {stats['completed']}/{stats['total']} ({rate:.0f}%)"
        
        text += """

💡 INSIGHTS
───────────────────────────────────────────────────────────────"""
        
        for insight in report.get('insights', []):
            text += f"\n  {insight}"
        
        text += """

📅 TIMELINE
───────────────────────────────────────────────────────────────"""
        
        for event in report.get('timeline', [])[:15]:  # Last 15 events
            try:
                time = datetime.fromisoformat(event['time'].replace('Z', '')).strftime('%H:%M')
            except:
                time = "??:??"
            text += f"\n  {time} | {event['type']}: {event['description'][:40]}"
        
        text += "\n\n═══════════════════════════════════════════════════════════════\n"
        text += f"Generated: {report['generated_at']}\n"
        text += "Life OS v2.0 - FOCUS-Optimized Task Management\n"
        
        return text

if __name__ == "__main__":
    generator = DailyReportGenerator()
    report = generator.generate_report()
    print(generator.format_report_text(report))
