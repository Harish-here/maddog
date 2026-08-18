| # | Finding | Source | Tag |
|---|---------|--------|-----|
| 1 | Markdown uses 34–38% fewer tokens than JSON for same data | [JSON vs Markdown vs XML in LLM Prompts: What Works Best](https://jsonkit.in/blog/json-vs-markdown-llm-prompts) | benchmark |
| 2 | Markdown typically uses 40–60% fewer tokens for document content; 1,000-doc KB = 500K token savings per retrieval pass | [JSON vs Markdown vs XML in LLM Prompts](https://jsonkit.in/blog/json-vs-markdown-llm-prompts) | benchmark |
| 3 | XML requires 80% more tokens than Markdown (nearly 2× inference cost) | [Which Nested Data Format Do LLMs Understand Best?](https://www.improvingagents.com/blog/best-nested-data-format/) | benchmark |
| 4 | LLMLingua achieves up to 20× prompt compression with minimal performance loss (tested on GSM8K, BBH, ShareGPT, ArXiv; EMNLP 2023) | [LLMLingua: Compressing Prompts for Accelerated Inference](https://arxiv.org/abs/2310.05736) | paper |
| 5 | Context accuracy U-shaped: 30%+ lower accuracy when relevant info in middle vs start/end of context | [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) | paper |
| 6 | Stanford 2023: With 20 documents (~4K tokens), LLM accuracy drops from 70–75% to 55–60% | [Lost in the Middle](https://arxiv.org/abs/2307.03172) | benchmark |
| 7 | Chroma tested 18 frontier models; every single one degrades as input length increases | [Context Rot: How Increasing Input Tokens Impacts LLM Performance](https://www.trychroma.com/research/context-rot) | benchmark |
| 8 | RAG reduces token usage by 60–80% compared to reading full documents | [Token-Budget-Aware LLM Reasoning](https://redis.io/blog/token-budget-aware-llm-reasoning/) | vendor-guidance |
| 9 | Concise prompt engineering (minimal yet essential info) reduces token costs by 30–50% | [Token-Budget-Aware LLM Reasoning](https://redis.io/blog/token-budget-aware-llm-reasoning/) | vendor-guidance |
| 10 | Context budget model: system prompts ~350 tokens; conversation ~1,500 tokens; output generation ~512 tokens | [Tool-Schema Compression Enables Agentic RAG](https://arxiv.org/pdf/2605.26165) | framework |
| 11 | Three-tier adaptive compression: Early Warning (40% capacity), Critical (60% capacity), Emergency (95% capacity) triggers | [Automatic Context Compression in LLM Agents](https://medium.com/the-ai-forum/automatic-context-compression-in-llm-agents-why-agents-need-to-forget-and-how-to-help-them-do-it-well) | framework |
| 12 | Preserve last 10% of context window verbatim; summarizing active working memory breaks agent continuity | [Automatic Context Compression in LLM Agents](https://medium.com/the-ai-forum/automatic-context-compression-in-llm-agents-why-agents-need-to-forget-and-how-to-help-them-do-it-well) | framework |
| 13 | .claudeignore discipline achieves 85.5% context reduction | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | vendor-guidance |
| 14 | Skill metadata (name + description) only pre-loaded at startup; SKILL.md loaded only when skill becomes relevant | [Agent Skills best practices](https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices) | vendor-guidance |
| 15 | Keep SKILL.md under 500 lines; file references one level deep | [Agent Skills best practices](https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices) | vendor-guidance |
| 16 | Skill description must state both what Skill does AND when to use it (write in third person) | [Agent Skills best practices](https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices) | vendor-guidance |
| 17 | Structured sections (<instructions>, <tools>, ## Output format) improve readability and modularity | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | vendor-guidance |
| 18 | llms.txt uses Markdown (not XML/JSON) as standard for LLM-friendly site documentation | [The /llms.txt file, v2](https://llmstxt.org/) | convention |
| 19 | ## Optional section in llms.txt marks links LLMs may skip when token budget tight; all other sections mandatory | [The /llms.txt file, v2](https://llmstxt.org/) | convention |
| 20 | Preserve architectural decisions, unresolved bugs, implementation details in conversation summaries; discard redundant tool outputs | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | vendor-guidance |
| 21 | One real code snippet beats three paragraphs describing convention | [How to write a great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) | convention |
| 22 | Place executable commands early in AGENTS.md; agent references them repeatedly throughout task | [How to write a great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) | convention |
| 23 | Multi-agent system (Claude Opus + Sonnet 4) outperformed single-agent Opus 4 by 90.2% on research tasks | [Building Production Multi-Agent Research Systems](https://www.zenml.io/llmops-database/building-production-multi-agent-research-systems-with-claude) | research |
| 24 | Multi-agent architecture consumes approximately 15× more tokens than standard chat interactions | [Building Production Multi-Agent Research Systems](https://www.zenml.io/llmops-database/building-production-multi-agent-research-systems-with-claude) | research |
| 25 | Filesystem pattern for subagent outputs minimizes "game of telephone" effect in information transfer | [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | vendor-guidance |
| 26 | Structured handoff schema for compressed summaries: files modified, tools called, decisions made, in-progress state, constraints, preferences | [MemRefine: LLM-Guided Compression for Long-Term Agent Memory](https://arxiv.org/pdf/2606.13177) | paper |
| 27 | Structured note fields: content, contextual description, keywords, tags, embeddings, links (enables dual canonical + in-context approach) | [MemRefine: LLM-Guided Compression for Long-Term Agent Memory](https://arxiv.org/pdf/2606.13177) | paper |
| 28 | Keep CLAUDE.md short enough to skim between meetings (loaded into every conversation; every word costs tokens) | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | vendor-guidance |
| 29 | Use @file system instead of pasting; file pulled exactly when needed, not stranded in context | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | vendor-guidance |
| 30 | /btw command: answer never enters conversation history (check details without growing context) | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | vendor-guidance |
| 31 | Fit right information (not most) into model's limited attention window to maximize useful signal, minimize noise | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | vendor-guidance |
| 32 | Context engineering: strategy for curating + maintaining optimal token set during inference (natural progression of prompt engineering) | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | vendor-guidance |
| 33 | Context functions as finite resource with diminishing marginal returns; performance gradient (not absolute cutoff) with length | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | vendor-guidance |
| 34 | LLMLingua-2 extends compression via data distillation; LongLLMLingua for long-context scenarios (extends 2023 work) | [LLMLingua: Compressing Prompts for Accelerated Inference](https://arxiv.org/abs/2310.05736) | paper |
| 35 | Transformer architecture: n² pairwise token relationships; as context length increases, model's ability to capture relationships stretches thin | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | vendor-guidance |
| 36 | NEEDLE in HAYSTACK (NIAH) benchmark widely used for evaluating long-context capabilities | [Context Rot Research](https://www.trychroma.com/research/context-rot) | benchmark |
| 37 | LOCA-bench: benchmark for Long-Context Agents with automated, scalable control of environment state | [LOCA-bench: Benchmarking Language Agents Under Controllable and Extreme Context Growth](https://arxiv.org/pdf/2602.07962) | benchmark |
| 38 | Tool-schema compression minimizes tool description overhead; budget-constrained agentic RAG requires schema reduction | [Tool-Schema Compression Enables Agentic RAG Under Constrained Context Budgets](https://arxiv.org/pdf/2605.26165) | paper |

---

## NOTES

**Searches Executed:** All 12 queries returned results with usable citations.

**Unverified Claim:**
Search 5 summary stated "Auto-generated AGENTS.md reduces task success in 5/8 settings, adds 2.45-3.92 steps per task" but the GitHub blog source itself does not provide empirical comparison metrics—it only advocates for manual creation with human review. Claim removed from table.

**Access & Paywalls:**
All primary sources accessible; no paywalled content blocked findings.

**Contradictions Between Sources:**
None detected. Minor variations exist (e.g., exact token percentages vary by dataset/model), documented in source links.

**Coverage Gaps:**
- Search 7 (Anthropic agent skills SKILL.md): returned vendor guidance but no published research paper on skill authoring ROI.
- Search 1 (Context engineering): yields vendor guidance; no peer-reviewed benchmark comparing Anthropic's approach to alternatives quantitatively.
- No direct comparison of llms.txt adoption metrics or token savings achieved by sites using the standard (introduced Sept 2024; adoption data sparse).

**Key Dates:**
- llms.txt standard: September 2024 (Jeremy Howard, Answer.AI)
- Lost-in-the-Middle original: July 2023 (https://arxiv.org/abs/2307.03172)
- LLMLingua: EMNLP 2023 (https://arxiv.org/abs/2310.05736)
- AGENTS.md GitHub blog: 2026 (lessons from 2,500+ repositories, no earlier pub date in source)
- Context Rot Chroma research: 2024–2025 (active benchmark cycle)
