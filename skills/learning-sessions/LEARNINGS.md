# 📚 Consolidated Learnings

A living document of key insights from learning sessions. Focus on actionable knowledge for BrevardBidderAI, Life OS, and Everest Capital.

---

## December 2025

### AWS AgentCore → BrevardBidderAI V14 Roadmap (Dec 4, 2025)
**Source:** [YUV AI - YouTube](https://youtube.com/watch?v=Ea1EpD-4sUU)  
**Relevance:** ⭐⭐⭐⭐⭐ CRITICAL

**TL;DR:** AWS AgentCore validates BrevardBidderAI's "Agentic AI ecosystem" positioning. Enterprise infrastructure pattern matches our architecture.

**The 8 AgentCore Services:**
| Service | BrevardBidderAI Equivalent |
|---------|---------------------------|
| Runtime (8hr tasks) | 12-Stage Pipeline |
| Gateway (MCP protocol) | Smart Router |
| Browser | BECA Scraper |
| Memory | Supabase + historical_auctions |
| Policy | Max Bid Formula Rules |
| Evaluations | XGBoost ML Accuracy |

**V14 Action Items:**
- [ ] Implement MCP-compatible tool definitions for scrapers
- [ ] Add Policy layer ("Never bid above 75% ARV minus repairs")
- [ ] Build Evaluation framework (lien accuracy, max bid correctness)
- [ ] Episodic memory - track deal outcomes to improve ML

**Enterprise Proof Points:**
- PGA TOUR: 1,000% speed increase, 95% cost reduction
- MongoDB: 8 weeks deployment vs months
- Swisscom: B2C agent in 4 weeks

**Valuation Impact:** AWS investing heavily in this category validates our $300-400K internal value assessment.

---

### Kernel.ai Entity Graph Architecture (Dec 4, 2025)
**Source:** Research session

**TL;DR:** B2B RevOps platform using entity graphs for CRM data cleaning.

**Application to BrevardBidderAI:**
- Entity deduplication for property records
- Relationship mapping for lien priority stacks
- Continuous processing vs batch approach

---

## How This File Works

1. **Share YouTube URL** → Claude analyzes
2. **Say "Log this"** → Saved to summaries/ + this file + Supabase
3. **Quick reference here** → Full details in summaries/

---

## Index

| Date | Topic | File |
|------|-------|------|
| Dec 4, 2025 | AWS AgentCore | `summaries/2025-12-04_aws_agentcore.md` |
