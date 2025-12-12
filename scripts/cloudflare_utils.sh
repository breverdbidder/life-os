#!/bin/bash
# Cloudflare Utils for Everest Capital
# Account: 83ab3f2fbbabd1a9b01a018fb4efe219
# Token: Set via CF_TOKEN env var

CF_TOKEN="${CF_TOKEN:-_mWiZdUKMcqWFZN1TYq8w0g4i1Pv7WaweEdlpkSZ}"
CF_ACCOUNT="83ab3f2fbbabd1a9b01a018fb4efe219"
CF_API="https://api.cloudflare.com/client/v4"

# List all Pages projects
cf_projects() {
  curl -s "$CF_API/accounts/$CF_ACCOUNT/pages/projects" \
    -H "Authorization: Bearer $CF_TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('result', []):
    latest = p.get('latest_deployment', {})
    status = latest.get('latest_stage', {}).get('status', 'unknown')
    print(f\"{p['name']}: {p['subdomain']} [{status}]\")
"
}

# Get deployment status for a project
cf_status() {
  PROJECT="${1:-brevard-bidder-landing}"
  curl -s "$CF_API/accounts/$CF_ACCOUNT/pages/projects/$PROJECT/deployments?per_page=5" \
    -H "Authorization: Bearer $CF_TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for d in data.get('result', [])[:5]:
    trigger = d.get('deployment_trigger', {}).get('metadata', {})
    stage = d.get('latest_stage', {})
    print(f\"{d['short_id']} | {stage.get('status')} | {trigger.get('commit_message', 'N/A')[:50]}\")
"
}

# Purge cache for a project
cf_purge() {
  PROJECT="${1:-brevard-bidder-landing}"
  # Get zone ID first (if custom domain attached)
  echo "Cache purge requires zone ID for custom domains. For Pages, redeploy instead."
}

# Trigger redeploy (latest commit)
cf_redeploy() {
  PROJECT="${1:-brevard-bidder-landing}"
  curl -s -X POST "$CF_API/accounts/$CF_ACCOUNT/pages/projects/$PROJECT/deployments" \
    -H "Authorization: Bearer $CF_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"branch": "main"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    r = data['result']
    print(f\"✅ Deployment triggered: {r['short_id']} - {r['url']}\")
else:
    print(f\"❌ Failed: {data.get('errors')}\")
"
}

# Get environment variables
cf_env() {
  PROJECT="${1:-brevard-bidder-landing}"
  curl -s "$CF_API/accounts/$CF_ACCOUNT/pages/projects/$PROJECT" \
    -H "Authorization: Bearer $CF_TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
prod = data.get('result', {}).get('deployment_configs', {}).get('production', {}).get('env_vars', {})
print('Production env vars:')
for k, v in prod.items():
    vtype = v.get('type', 'unknown')
    val = '[SECRET]' if vtype == 'secret_text' else v.get('value', '')
    print(f'  {k}: {val} ({vtype})')
"
}

case "$1" in
  projects) cf_projects ;;
  status) cf_status "$2" ;;
  redeploy) cf_redeploy "$2" ;;
  env) cf_env "$2" ;;
  *) echo "Usage: $0 {projects|status|redeploy|env} [project_name]" ;;
esac
