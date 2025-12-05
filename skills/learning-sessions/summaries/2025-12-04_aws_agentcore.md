# Learning Session: AWS AgentCore

## Video Information
- **Title:** סוכני AI מאפס למאה - עם AWS AgentCore! (AI Agents from Zero to Hundred - with AWS AgentCore!)
- **Channel:** בינה מלאכותית עם יובל אבידני YUV AI (@yuv-ai)
- **URL:** https://youtube.com/watch?v=Ea1EpD-4sUU
- **Date Watched:** December 4, 2025

---

## Key Takeaways from AWS AgentCore (AWS re:Invent 2025)

### What is AgentCore?
Amazon Bedrock AgentCore is the most advanced platform for building and deploying AI agents securely at scale. It bridges the gap between proof-of-concept and production for AI agents.

### Core Services

| Service | Purpose |
|---------|---------|
| **AgentCore Runtime** | Secure, dynamic workloads up to 8 hours (longest in industry), framework agnostic |
| **AgentCore Identity** | Secure access to AWS + third-party tools (GitHub, Salesforce, Slack) |
| **AgentCore Gateway** | Transforms APIs/Lambda into agent-ready tools, supports MCP protocol |
| **AgentCore Browser** | Managed web browser instances for web automation |
| **AgentCore Code Interpreter** | Isolated environment for agent-generated code execution |
| **AgentCore Memory** | Episodic memory - agents learn from experience over time |
| **AgentCore Policy** | Natural-language boundaries on agent actions |
| **AgentCore Evaluations** | 13 pre-built evaluators for agent quality monitoring |

### Key Differentiators
1. **Framework Agnostic:** Works with CrewAI, LangGraph, LlamaIndex, Strands, custom frameworks
2. **Protocol Support:** MCP (Model Context Protocol), A2A (Agent2Agent)
3. **Enterprise-Grade Security:** Uses automated reasoning (math-based verification)
4. **Scalable:** From prototype to millions of users
5. **Long-Running Tasks:** Up to 8 hours per session

### Success Stories
- **PGA TOUR:** 1,000% content writing speed increase, 95% cost reduction
- **MongoDB:** Deployed agent-based application in 8 weeks (was months)
- **Swisscom:** Launched B2C agent solution in 4 weeks
- **Lyft:** 87% reduction in resolution time, 70% increase in agent usage

---

## Application to BrevardBidderAI

### Direct Relevance
BrevardBidderAI is positioned as an "Agentic AI ecosystem" - AgentCore provides the enterprise infrastructure pattern to emulate.

### Architecture Mapping

| BrevardBidderAI Current | AWS AgentCore Equivalent |
|-------------------------|--------------------------|
| 12-Stage Pipeline | AgentCore Runtime (long-running tasks) |
| Smart Router (multi-tier LLM) | Native support for any model |
| BECA Scraper | AgentCore Browser + Code Interpreter |
| Supabase Integration | AgentCore Memory |
| Layer 8 IP Protection | AgentCore Policy + Identity |
| XGBoost ML Models | AgentCore Evaluations |

### Potential Improvements to Consider
1. **MCP Protocol:** Standardize BrevardBidderAI tools as MCP-compatible
2. **Policy Layer:** Implement natural-language constraints on bid recommendations
3. **Episodic Memory:** Track deal outcomes to improve ML predictions
4. **Gateway Pattern:** Expose APIs (BCPAO, AcclaimWeb) as agent-ready tools
5. **Evaluation Suite:** Build pre-built evaluators for:
   - Lien priority accuracy
   - Max bid calculation correctness
   - Title search completeness

### V14 Roadmap Considerations
- [ ] Evaluate AWS Bedrock for Smart Router PRODUCTION tier
- [ ] Implement MCP-compatible tool definitions
- [ ] Add AgentCore-style Policy layer for bid limits
- [ ] Build evaluation framework for agent recommendations

---

## Notable Quotes (from AWS sources)

> "AI agents will dramatically accelerate innovation and improve productivity across every industry." - Swami Sivasubramanian, AWS VP Agentic AI

> "Being able to take advantage of the reasoning capabilities of these models, which is coupled with being able to do real-world things through tools, feels like a sustainable pattern." - AWS

---

## Tags
#AWS #AgentCore #AgenticAI #Architecture #BrevardBidderAI #Infrastructure #MCP #Enterprise

---

## Follow-Up Actions
- [ ] Watch full video for implementation details
- [ ] Research MCP protocol integration patterns
- [ ] Compare AgentCore pricing vs current stack
- [ ] Evaluate for BidDeedAI multi-county scaling
