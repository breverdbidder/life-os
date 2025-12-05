# 📚 Consolidated Learnings

A living document of key insights from learning sessions, automatically updated when important content is stored.

---

## December 2025

### AWS AgentCore (Dec 4, 2025)
**Source:** [YUV AI - YouTube](https://youtube.com/watch?v=Ea1EpD-4sUU)

**TL;DR:** AWS Bedrock AgentCore is enterprise infrastructure for AI agents. Framework-agnostic, 8-hour runtime, MCP protocol support.

**Key Services:**
- Runtime, Identity, Gateway, Browser, Code Interpreter, Memory, Policy, Evaluations

**Application to BrevardBidderAI:**
- AgentCore pattern validates our "Agentic AI ecosystem" positioning
- Consider MCP protocol for tool standardization
- Policy layer concept for bid recommendation constraints

**Success Metrics:**
- PGA TOUR: 1,000% speed increase, 95% cost reduction
- Swisscom: B2C agent in 4 weeks

---

### Kernel.ai Entity Graph Architecture (Dec 4, 2025)
**Source:** Research session

**TL;DR:** B2B RevOps platform using entity graphs for CRM data cleaning and enrichment.

**Application to BrevardBidderAI:**
- Entity deduplication patterns for property data
- Relationship mapping concept for lien priority stacks
- Continuous data processing vs batch approach

---

## How This File Works

When Claude analyzes a learning session and you say "Log this" or it's marked as important:
1. Full analysis saved to `summaries/YYYY-MM-DD_topic.md`
2. Key points added to this LEARNINGS.md
3. Metadata saved to Supabase `insights` table

Browse summaries for full details. This file = quick reference.
