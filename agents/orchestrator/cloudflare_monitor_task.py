"""
Cloudflare Monitor Task for LangGraph Orchestrator
Integrates with Everest Capital Agentic AI pipeline
"""

import os
import json
import subprocess
from datetime import datetime
from typing import TypedDict, Annotated

class CloudflareState(TypedDict):
    projects: list
    last_check: str
    alerts: list
    deployment_history: dict

def check_cloudflare_status() -> CloudflareState:
    """Check status of all Cloudflare Pages projects"""
    
    CF_TOKEN = os.getenv("CF_TOKEN", "_mWiZdUKMcqWFZN1TYq8w0g4i1Pv7WaweEdlpkSZ")
    CF_ACCOUNT = "83ab3f2fbbabd1a9b01a018fb4efe219"
    
    import requests
    
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Get all projects
    resp = requests.get(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/pages/projects",
        headers=headers
    )
    
    data = resp.json()
    
    state = CloudflareState(
        projects=[],
        last_check=datetime.utcnow().isoformat(),
        alerts=[],
        deployment_history={}
    )
    
    for project in data.get("result", []):
        name = project["name"]
        latest = project.get("latest_deployment", {})
        status = latest.get("latest_stage", {}).get("status", "unknown")
        
        state["projects"].append({
            "name": name,
            "url": project["subdomain"],
            "status": status,
            "last_deploy": latest.get("created_on"),
            "commit": latest.get("deployment_trigger", {}).get("metadata", {}).get("commit_message", "N/A")
        })
        
        # Alert on failures
        if status == "failure":
            state["alerts"].append({
                "project": name,
                "type": "deployment_failure",
                "message": f"Deployment failed for {name}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    return state

def trigger_redeploy(project_name: str) -> dict:
    """Trigger a new deployment for a project"""
    
    CF_TOKEN = os.getenv("CF_TOKEN", "_mWiZdUKMcqWFZN1TYq8w0g4i1Pv7WaweEdlpkSZ")
    CF_ACCOUNT = "83ab3f2fbbabd1a9b01a018fb4efe219"
    
    import requests
    
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/pages/projects/{project_name}/deployments",
        headers=headers,
        json={"branch": "main"}
    )
    
    data = resp.json()
    
    if data.get("success"):
        return {
            "success": True,
            "deployment_id": data["result"]["short_id"],
            "url": data["result"]["url"]
        }
    else:
        return {
            "success": False,
            "errors": data.get("errors", [])
        }

# LangGraph node definition
def cloudflare_monitor_node(state: dict) -> dict:
    """LangGraph node for Cloudflare monitoring"""
    
    cf_state = check_cloudflare_status()
    
    # Auto-remediation: retry failed deployments
    for alert in cf_state["alerts"]:
        if alert["type"] == "deployment_failure":
            result = trigger_redeploy(alert["project"])
            alert["remediation"] = result
    
    state["cloudflare"] = cf_state
    return state

if __name__ == "__main__":
    # Test run
    state = check_cloudflare_status()
    print(json.dumps(state, indent=2))
