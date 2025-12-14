---
paths:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"
---
# Security Rules

## Data Protection

### Never Log or Commit
- API keys or tokens
- Health information (PHI)
- Michael's personal data (grades, times)
- Financial information
- Location data

### Input Sanitization
- Validate all user inputs
- Escape special characters in logs
- Use parameterized queries for Supabase

## ADHD Safety
- Never expose task abandonment stats publicly
- Keep intervention patterns private
- Protect learning session content

## Environment Variables
Always use environment variables for:
- `SUPABASE_KEY`
- `GITHUB_TOKEN`
- `GOOGLE_API_KEY`
