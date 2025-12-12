"""
Life OS Library
===============
Universal Bridge and utilities for Life OS integration.

Usage:
    from lib.life_os_bridge import LifeOSBridge
    
    bridge = LifeOSBridge()
    bridge.log_swim_time("100 Free", 52.45)
    bridge.create_task("Review auction list", domain="BUSINESS")
    bridge.deploy_to_claude_code("Fix BECA scraper", "P0")
"""

from .life_os_bridge import LifeOSBridge, SupabaseClient, Domain, Priority

__all__ = ["LifeOSBridge", "SupabaseClient", "Domain", "Priority"]

