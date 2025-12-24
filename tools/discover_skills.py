#!/usr/bin/env python3
"""
Skill Discovery Tool for AI Agents
Scans .claude/skills/ directory and returns available skills with metadata
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional


def parse_skill_md(skill_path: Path) -> Dict[str, str]:
    """Parse SKILL.md file to extract name and description"""
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        return {
            "name": skill_path.name,
            "description": "No SKILL.md found",
            "path": str(skill_path)
        }
    
    try:
        content = skill_md.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        name = skill_path.name
        description = ""
        
        # Parse markdown headers
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            if line.startswith('# '):
                name = line.replace('# ', '').strip()
            elif line.startswith('## Description') or line.startswith('**Description'):
                # Get next non-empty line
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        description = lines[j].strip()
                        break
            elif i == 0 and not line.startswith('#'):
                # First line might be description
                description = line.strip()
        
        # If no description found, use first paragraph
        if not description:
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    description = line.strip()[:200]  # Max 200 chars
                    break
        
        return {
            "name": name,
            "description": description or "No description available",
            "path": str(skill_path)
        }
    
    except Exception as e:
        return {
            "name": skill_path.name,
            "description": f"Error parsing: {e}",
            "path": str(skill_path)
        }


def discover_skills(
    skills_dir: str = ".claude/skills",
    filter_name: Optional[str] = None,
    format: str = "json"
) -> str:
    """
    Discover available skills in the skills directory
    
    Args:
        skills_dir: Path to skills directory (default: .claude/skills)
        filter_name: Optional filter to search for specific skill names
        format: Output format - 'json', 'list', or 'detailed'
    
    Returns:
        Formatted string with skill information
    """
    skills_path = Path(skills_dir)
    
    if not skills_path.exists():
        return json.dumps({
            "error": f"Skills directory not found: {skills_dir}",
            "available_skills": []
        })
    
    # Scan for skills
    skills = []
    for item in skills_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            skill_info = parse_skill_md(item)
            
            # Apply filter if specified
            if filter_name and filter_name.lower() not in skill_info['name'].lower():
                continue
            
            # Check for additional files
            skill_info['has_scripts'] = any(
                f.suffix in ['.py', '.js', '.sh'] 
                for f in item.glob('*')
            )
            skill_info['files'] = [f.name for f in item.glob('*') if f.is_file()]
            
            skills.append(skill_info)
    
    # Sort by name
    skills.sort(key=lambda x: x['name'])
    
    # Format output
    if format == "json":
        return json.dumps({
            "skills_directory": str(skills_path),
            "total_skills": len(skills),
            "skills": skills
        }, indent=2)
    
    elif format == "list":
        output = f"Available Skills ({len(skills)}):\n"
        output += "=" * 60 + "\n"
        for skill in skills:
            output += f"\n• {skill['name']}\n"
            output += f"  {skill['description'][:80]}...\n" if len(skill['description']) > 80 else f"  {skill['description']}\n"
        return output
    
    elif format == "detailed":
        output = f"Skills Directory: {skills_path}\n"
        output += f"Total Skills: {len(skills)}\n"
        output += "=" * 60 + "\n\n"
        
        for skill in skills:
            output += f"Name: {skill['name']}\n"
            output += f"Path: {skill['path']}\n"
            output += f"Description: {skill['description']}\n"
            output += f"Has Scripts: {'Yes' if skill['has_scripts'] else 'No'}\n"
            output += f"Files: {', '.join(skill['files'])}\n"
            output += "-" * 60 + "\n\n"
        
        return output
    
    else:
        return json.dumps({"error": f"Invalid format: {format}"})


def get_skill_content(skill_name: str, skills_dir: str = ".claude/skills") -> str:
    """
    Get the full content of a specific skill's SKILL.md file
    
    Args:
        skill_name: Name of the skill to retrieve
        skills_dir: Path to skills directory
    
    Returns:
        Content of SKILL.md or error message
    """
    skills_path = Path(skills_dir)
    
    # Find matching skill (case-insensitive)
    for item in skills_path.iterdir():
        if item.is_dir() and item.name.lower() == skill_name.lower():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                return f"=== {item.name} ===\n\n" + skill_md.read_text(encoding='utf-8')
            else:
                return f"Error: SKILL.md not found in {item.name}"
    
    return f"Error: Skill '{skill_name}' not found"


if __name__ == "__main__":
    import sys
    
    # CLI interface
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            print(discover_skills(format="list"))
        
        elif command == "json":
            print(discover_skills(format="json"))
        
        elif command == "detailed":
            print(discover_skills(format="detailed"))
        
        elif command == "get" and len(sys.argv) > 2:
            skill_name = sys.argv[2]
            print(get_skill_content(skill_name))
        
        else:
            print("Usage:")
            print("  python discover_skills.py list       # List all skills")
            print("  python discover_skills.py json       # JSON output")
            print("  python discover_skills.py detailed   # Detailed view")
            print("  python discover_skills.py get <name> # Get specific skill")
    else:
        # Default: list format
        print(discover_skills(format="list"))
