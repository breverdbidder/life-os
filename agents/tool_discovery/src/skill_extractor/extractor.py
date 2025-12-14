"""
Skill Extractor
Converts successful Claude.ai exploration sessions into frozen GitHub Actions workflows
Part of BidDeed.AI Agentic Architecture

Pattern: Exploration (expensive) → Skill Extraction → Production (cheap)
"""

import os
import json
import re
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import yaml
import httpx

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "breverdbidder/life-os"


@dataclass
class ExtractedSkill:
    """A skill extracted from a successful chat session"""
    name: str
    description: str
    trigger_patterns: list[str]  # What user inputs trigger this skill
    tool_sequence: list[dict]    # Ordered list of tools used
    input_schema: dict           # Expected inputs
    output_schema: dict          # Expected outputs
    success_criteria: str        # How to know it worked
    source_chat_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = field(default_factory=dict)


async def analyze_chat_for_skills(chat_messages: list[dict]) -> list[dict]:
    """
    Analyze a chat conversation to extract potential skills
    
    Looks for:
    1. Repeated tool call patterns
    2. Successful task completions
    3. Multi-step workflows that succeeded
    """
    
    skills = []
    tool_sequences = []
    current_sequence = []
    
    for msg in chat_messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        # Detect tool calls in assistant messages
        if role == "assistant":
            # Look for function_calls patterns
            tool_matches = re.findall(r'<invoke name="([^"]+)"', content)
            if tool_matches:
                current_sequence.extend(tool_matches)
        
        # Task completion signals
        completion_signals = [
            "✅", "Done", "Completed", "Successfully", 
            "deployed", "created", "saved to"
        ]
        
        if any(signal in content for signal in completion_signals):
            if current_sequence:
                tool_sequences.append({
                    "tools": current_sequence.copy(),
                    "completion_msg": content[:200]
                })
                current_sequence = []
    
    # Identify repeated patterns (potential skills)
    pattern_counts = {}
    for seq in tool_sequences:
        pattern_key = "→".join(seq["tools"][:5])  # First 5 tools as pattern
        pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
    
    # Extract skills from repeated patterns
    for pattern, count in pattern_counts.items():
        if count >= 2:  # Pattern repeated at least twice = skill candidate
            tools = pattern.split("→")
            skills.append({
                "pattern": pattern,
                "tools": tools,
                "occurrences": count,
                "skill_candidate": True
            })
    
    return skills


def generate_workflow_yaml(skill: ExtractedSkill) -> str:
    """
    Generate a GitHub Actions workflow YAML from an extracted skill
    This is the "frozen skill" that runs in production
    """
    
    # Map tool names to workflow steps
    steps = []
    
    # Checkout step
    steps.append({
        "name": "Checkout",
        "uses": "actions/checkout@v4"
    })
    
    # Setup Python
    steps.append({
        "name": "Setup Python",
        "uses": "actions/setup-python@v5",
        "with": {"python-version": "3.11"}
    })
    
    # Install dependencies
    steps.append({
        "name": "Install dependencies",
        "run": "pip install httpx pydantic"
    })
    
    # Main skill execution
    skill_code = generate_skill_code(skill)
    steps.append({
        "name": f"Execute: {skill.name}",
        "env": {
            "SUPABASE_URL": "${{ secrets.SUPABASE_URL }}",
            "SUPABASE_KEY": "${{ secrets.SUPABASE_KEY }}"
        },
        "run": f"python -c '{skill_code}'"
    })
    
    workflow = {
        "name": f"Skill: {skill.name}",
        "on": {
            "workflow_dispatch": {
                "inputs": {
                    k: {"description": v.get("description", k), "required": v.get("required", False)}
                    for k, v in skill.input_schema.items()
                }
            },
            "schedule": [{"cron": "0 6 * * *"}] if "daily" in skill.name.lower() else []
        },
        "jobs": {
            "execute": {
                "runs-on": "ubuntu-latest",
                "steps": steps
            }
        }
    }
    
    # Clean up empty schedule
    if not workflow["on"]["schedule"]:
        del workflow["on"]["schedule"]
    
    return yaml.dump(workflow, default_flow_style=False, sort_keys=False)


def generate_skill_code(skill: ExtractedSkill) -> str:
    """Generate Python code for the frozen skill"""
    
    tool_imports = set()
    tool_calls = []
    
    for i, tool in enumerate(skill.tool_sequence):
        tool_name = tool.get("name", f"tool_{i}")
        tool_imports.add(tool_name)
        tool_calls.append(f"    # Step {i+1}: {tool_name}")
        tool_calls.append(f"    result_{i} = await {tool_name}(**params)")
    
    code = f'''
import asyncio
import httpx
import os

async def {skill.name.replace("-", "_").replace(" ", "_")}():
    """
    {skill.description}
    
    Frozen skill extracted from exploration phase.
    Tools: {" → ".join(t.get("name", "?") for t in skill.tool_sequence)}
    """
    
    params = {{}}  # Populated from workflow inputs
    
{chr(10).join(tool_calls)}
    
    print("✅ Skill completed: {skill.name}")

asyncio.run({skill.name.replace("-", "_").replace(" ", "_")}())
'''
    return code.replace("'", "\\'").replace("\n", "\\n")


async def save_skill_to_db(skill: ExtractedSkill) -> dict:
    """Save extracted skill to Supabase for tracking"""
    
    payload = {
        "skill_name": skill.name,
        "description": skill.description,
        "trigger_patterns": skill.trigger_patterns,
        "tool_sequence": skill.tool_sequence,
        "input_schema": skill.input_schema,
        "output_schema": skill.output_schema,
        "success_criteria": skill.success_criteria,
        "source_chat_id": skill.source_chat_id,
        "metadata": skill.metadata
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/extracted_skills",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=payload
        )
        
        return {"success": response.status_code in [200, 201], "data": response.json() if response.status_code in [200, 201] else None}


async def deploy_skill_to_github(skill: ExtractedSkill) -> dict:
    """
    Deploy frozen skill as GitHub Actions workflow
    
    This is the key step: exploration → production
    """
    
    workflow_yaml = generate_workflow_yaml(skill)
    workflow_path = f".github/workflows/skill-{skill.name.lower().replace(' ', '-')}.yml"
    
    # Check if file exists
    async with httpx.AsyncClient() as client:
        # Get current file SHA if exists
        check_response = await client.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{workflow_path}",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        sha = None
        if check_response.status_code == 200:
            sha = check_response.json().get("sha")
        
        # Create or update file
        import base64
        content_b64 = base64.b64encode(workflow_yaml.encode()).decode()
        
        payload = {
            "message": f"Deploy frozen skill: {skill.name}",
            "content": content_b64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha
        
        response = await client.put(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{workflow_path}",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            json=payload
        )
        
        return {
            "success": response.status_code in [200, 201],
            "path": workflow_path,
            "action": "updated" if sha else "created"
        }


async def extract_and_deploy_skill(
    skill_name: str,
    description: str,
    tool_sequence: list[dict],
    input_schema: dict,
    trigger_patterns: list[str] = None,
    source_chat_id: str = None
) -> dict:
    """
    Full pipeline: Extract skill from successful pattern → Deploy as frozen workflow
    """
    
    skill = ExtractedSkill(
        name=skill_name,
        description=description,
        trigger_patterns=trigger_patterns or [],
        tool_sequence=tool_sequence,
        input_schema=input_schema,
        output_schema={},
        success_criteria=f"Workflow completes without errors",
        source_chat_id=source_chat_id
    )
    
    # Save to database
    db_result = await save_skill_to_db(skill)
    
    # Deploy to GitHub
    deploy_result = await deploy_skill_to_github(skill)
    
    return {
        "skill": skill_name,
        "database": db_result,
        "github": deploy_result,
        "workflow_url": f"https://github.com/{GITHUB_REPO}/actions/workflows/skill-{skill_name.lower().replace(' ', '-')}.yml"
    }


# SQL for extracted_skills table
EXTRACTED_SKILLS_TABLE = """
CREATE TABLE IF NOT EXISTS extracted_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name TEXT NOT NULL UNIQUE,
    description TEXT,
    trigger_patterns JSONB DEFAULT '[]',
    tool_sequence JSONB DEFAULT '[]',
    input_schema JSONB DEFAULT '{}',
    output_schema JSONB DEFAULT '{}',
    success_criteria TEXT,
    source_chat_id TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS extracted_skills_name_idx ON extracted_skills(skill_name);
"""
