#!/usr/bin/env python3
"""
Capacity Enforcement System
Monitors Claude's token usage and flags violations of the 80% rule
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

# Supabase credentials
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Capacity rules
CONTEXT_WINDOW = 1_000_000  # 1M tokens
VIOLATION_THRESHOLD = 0.80  # 80% - can't claim limitations before this

class CapacityEnforcement:
    def __init__(self):
        self.capacity = CONTEXT_WINDOW
        self.threshold = VIOLATION_THRESHOLD
        
    def check_compliance(self, tokens_used: int, claimed_limitation: bool) -> Dict[str, Any]:
        """
        Check if Claude violated the 80% rule
        
        Args:
            tokens_used: Number of tokens used in conversation
            claimed_limitation: Whether Claude claimed space/token limitations
            
        Returns:
            Dict with compliance status and violation details
        """
        usage_percent = tokens_used / self.capacity
        violation = claimed_limitation and usage_percent < self.threshold
        
        return {
            "tokens_used": tokens_used,
            "capacity": self.capacity,
            "usage_percent": round(usage_percent * 100, 2),
            "threshold_percent": self.threshold * 100,
            "claimed_limitation": claimed_limitation,
            "is_violation": violation,
            "violation_severity": self._get_severity(usage_percent) if violation else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_severity(self, usage_percent: float) -> str:
        """Determine severity of violation based on how far from threshold"""
        if usage_percent < 0.20:  # Less than 20% usage
            return "SEVERE"
        elif usage_percent < 0.40:  # 20-40% usage
            return "HIGH"
        elif usage_percent < 0.60:  # 40-60% usage
            return "MEDIUM"
        else:  # 60-80% usage
            return "LOW"
    
    def log_to_supabase(self, compliance_data: Dict[str, Any]) -> bool:
        """
        Log compliance check to Supabase
        
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            import httpx
            
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            
            # Insert into capacity_compliance table
            response = httpx.post(
                f"{SUPABASE_URL}/rest/v1/capacity_compliance",
                headers=headers,
                json=compliance_data
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Error logging to Supabase: {e}")
            return False
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """
        Get summary of violations from Supabase
        
        Returns:
            Dict with violation statistics
        """
        try:
            import httpx
            
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            
            # Query violations
            response = httpx.get(
                f"{SUPABASE_URL}/rest/v1/capacity_compliance?is_violation=eq.true&select=*",
                headers=headers
            )
            
            if response.status_code == 200:
                violations = response.json()
                return {
                    "total_violations": len(violations),
                    "violations": violations
                }
            
            return {"total_violations": 0, "violations": []}
            
        except Exception as e:
            print(f"Error fetching violations: {e}")
            return {"total_violations": 0, "violations": [], "error": str(e)}

if __name__ == "__main__":
    enforcer = CapacityEnforcement()
    
    # Example usage
    result = enforcer.check_compliance(
        tokens_used=125_000,
        claimed_limitation=True
    )
    
    print(json.dumps(result, indent=2))
    
    if result["is_violation"]:
        print(f"\n⚠️ VIOLATION DETECTED: {result['violation_severity']}")
        print(f"   Used {result['usage_percent']}% but claimed limitations")
        print(f"   Threshold: {result['threshold_percent']}%")
