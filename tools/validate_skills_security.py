#!/usr/bin/env python3
"""
Skills Security Validator
Pre-flight check to enforce read-only skills directories
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple


LOCKED_PATHS = [
    ".claude/skills",
    "/mnt/skills/public",
    "/mnt/skills/examples",
    "/mnt/skills/user"
]

FORBIDDEN_OPERATIONS = ["write", "delete", "create", "modify", "rename", "chmod"]


def is_path_locked(filepath: str) -> bool:
    """Check if a filepath is within a locked directory"""
    filepath = str(Path(filepath).resolve())
    
    for locked in LOCKED_PATHS:
        locked_abs = str(Path(locked).resolve())
        if filepath.startswith(locked_abs):
            return True
    
    return False


def validate_operation(operation: str, filepath: str) -> Tuple[bool, str]:
    """
    Validate if an operation on a filepath is allowed
    
    Returns:
        (is_valid, error_message)
    """
    if operation.lower() in ["read", "execute", "list"]:
        return True, ""
    
    if operation.lower() in FORBIDDEN_OPERATIONS:
        if is_path_locked(filepath):
            return False, (
                f"SECURITY VIOLATION: Cannot {operation} in locked skills directory\n"
                f"Path: {filepath}\n"
                f"Skills directories are READ-ONLY for agents.\n"
                f"To create new skills, use /tmp/new_skills/ or outputs/new_skills/"
            )
    
    return True, ""


def check_file_modifications(modified_files: List[str]) -> Tuple[bool, List[str]]:
    """
    Check a list of files for security violations
    
    Returns:
        (all_valid, list_of_errors)
    """
    errors = []
    
    for filepath in modified_files:
        if is_path_locked(filepath):
            errors.append(
                f"BLOCKED: Attempt to modify locked skill file: {filepath}"
            )
    
    return len(errors) == 0, errors


def log_violation(operation: str, filepath: str, agent_id: str = "unknown"):
    """Log security violation to insights table"""
    try:
        import requests
        import json
        from datetime import datetime, timezone
        
        SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_SERVICE_KEY', ''))
        
        if not SUPABASE_KEY:
            print("WARNING: Cannot log violation - no SUPABASE_KEY", file=sys.stderr)
            return
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        data = {
            'category': 'security',
            'subcategory': 'skills_violation',
            'insight': json.dumps({
                'operation': operation,
                'filepath': filepath,
                'agent_id': agent_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'severity': 'high'
            }),
            'metadata': {
                'type': 'security_violation',
                'auto_blocked': True
            }
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/insights",
            headers=headers,
            json=data,
            timeout=5
        )
        
        if response.status_code not in [200, 201]:
            print(f"WARNING: Failed to log violation: {response.status_code}", file=sys.stderr)
    
    except Exception as e:
        print(f"WARNING: Error logging violation: {e}", file=sys.stderr)


def print_security_banner():
    """Print security status banner"""
    print("=" * 70)
    print("SKILLS SECURITY: ACTIVE")
    print("=" * 70)
    print("Locked Directories (Read-Only):")
    for path in LOCKED_PATHS:
        if Path(path).exists():
            print(f"  ✓ {path}")
        else:
            print(f"  - {path} (not present)")
    print("\nStaging Area for New Skills:")
    print("  • /tmp/new_skills/")
    print("  • /mnt/user-data/outputs/new_skills/")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate skills directory security")
    parser.add_argument("--check-path", help="Check if path is locked")
    parser.add_argument("--validate", nargs=2, metavar=("OPERATION", "PATH"),
                      help="Validate operation on path")
    parser.add_argument("--banner", action="store_true", help="Print security banner")
    
    args = parser.parse_args()
    
    if args.banner:
        print_security_banner()
    
    elif args.check_path:
        locked = is_path_locked(args.check_path)
        print(f"Path: {args.check_path}")
        print(f"Locked: {locked}")
        sys.exit(0 if locked else 1)
    
    elif args.validate:
        operation, filepath = args.validate
        valid, error = validate_operation(operation, filepath)
        
        if valid:
            print(f"✓ ALLOWED: {operation} on {filepath}")
            sys.exit(0)
        else:
            print(error, file=sys.stderr)
            log_violation(operation, filepath)
            sys.exit(1)
    
    else:
        print_security_banner()
