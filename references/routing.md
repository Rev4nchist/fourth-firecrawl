# Routing Guide

Decision table for which skill to use and when. Read the preflight section before every run.

## Preflight — MCP availability gate

Before executing any research task, verify that the Firecrawl MCP tools are present in Claude's available toolset. Look for tools with names beginning with `mcp__firecrawl__` (such as `mcp__firecrawl__firecrawl_scrape` or `mcp__firecrawl__firecrawl_search`).

**If those tools are absent from the toolset: STOP.**

Instruct the user to run `/fourth-firecrawl:setup` or add the Firecrawl connector in Cowork (Settings → Connectors → Firecrawl) before proceeding. Do NOT fall back to WebFetch, WebSearch, built-in search, or any other web-access tool as a substitute. Firecrawl is the designated tool for these workflows — silent fallback produces inconsistent output, bypasses the credit guardrails, and writes nothing to `.firecrawl/` for KB ingestion.

This rule applies even if the user asks Claude to "just grab the page quickly." The per-user credit accountability model and the staging pipeline both depend on MCP. Surface the setup requirement and wait.

If the user explicitly asks to use a different tool after being informed about the missing connector, that is the user's decision to make — execute it, but do not initiate the substitution silently.

## Routing table

| User intent | Primary skill | When to use | Related MCP tools |
|-------------|---------------|-------------|-------------------|
| Research a specific competitor's pricing, features, or case studies | `competitor-intel` | Named competitor in Fourth's registry (R365, 7shifts, Deputy, UKG, Toast, Paycom, Homebase, Paylocity, ADP, Push Operations, When I Work) | `mcp__firecrawl__firecrawl_extract`, `mcp__firecrawl__firecrawl_scrape`, `mcp__firecrawl__firecrawl_map` |
| Scrape a competitor page not in the registry | `firecrawl-scrape` | One-off URL, not a named registry entry; no extraction schema needed | `mcp__firecrawl__firecrawl_scrape` |
| Find all URLs on a competitor or source site | `firecrawl-map` | Need to discover subpages before scraping in bulk | `mcp__firecrawl__firecrawl_map` |
| Crawl an entire competitor docs or blog section | `firecrawl-crawl` | Need many pages from one site (for example, all /blog/ posts) | `mcp__firecrawl__firecrawl_crawl`, `mcp__firecrawl__firecrawl_check_crawl_status` |
| Track hospitality industry news or trends | `market-scan` | Recurring or ad-hoc news sweep across trade press catalog | `mcp__firecrawl__firecrawl_search` |
| Find what content competitors publish that Fourth does not | `content-gap-analysis` | Strategic content planning, gap identification before a campaign or EBR | `mcp__firecrawl__firecrawl_extract`, `mcp__firecrawl__firecrawl_search` |
| Land staged research into the Marketing Brain KB | `kb-ingest-review` | After any skill run that produced `.firecrawl/` output the user wants to keep | — |
| Extract structured data from known URLs with a defined schema | `firecrawl-agent` (extract mode) | URLs are known, output shape is defined — prefer over agent for cost efficiency | `mcp__firecrawl__firecrawl_extract` |
| Autonomous deep research across unknown sources | `firecrawl-agent` (agent mode) | Source URLs are unknown; requires multi-step AI navigation — expensive, use as last resort | `mcp__firecrawl__firecrawl_agent`, `mcp__firecrawl__firecrawl_agent_status` |
| Interact with a page requiring clicks, form fills, or pagination | `firecrawl-interact` | Content locked behind a button, modal, or multi-step flow | `mcp__firecrawl__firecrawl_scrape` (with actions) + `mcp__firecrawl__firecrawl_interact`, `mcp__firecrawl__firecrawl_interact_stop` |
| General web search on a topic with no specific URL | `firecrawl-search` | No URL yet; need to discover sources first | `mcp__firecrawl__firecrawl_search` |

## EBR vs. marketing-brain context

**When running research as part of an EBR build:**

Run `competitor-intel` and/or `market-scan` to produce `.firecrawl/` staging output. Surface key findings to the EBR author. Use `kb-ingest-review` only if the findings are worth persisting in the Marketing Brain KB beyond the EBR — not every EBR-session scrape needs to be ingested.

Typical EBR flow:
1. `competitor-intel` — pull current pricing for 1-2 named competitors relevant to the account's segment
2. `market-scan` — pull 2-3 recent industry headlines relevant to the account's pain points
3. Surface summaries directly in the EBR session (`.firecrawl/` staging is sufficient for EBR use)
4. Optionally: `kb-ingest-review` if findings update existing KB competitive docs

**When running research in a standalone marketing-brain session:**

Research is intended to persist. After any `competitor-intel` or `market-scan` run, follow up with `kb-ingest-review` to land approved content in the KB. Use source metadata tags (`competitor-crawl`, `market-signal`, `press-release`) so KB entries are filterable by type.

## When NOT to use this plugin

- **Single-URL reads of known, static internal pages** — use the built-in WebFetch tool for quick one-off lookups where no staging or credit tracking is needed and the content is a simple page read
- **Fetching internal URLs** — anything behind Fourth's VPN, internal wiki, or authenticated internal tools; the Firecrawl MCP cannot authenticate with Fourth's internal systems
- **Fourth's own properties** — use direct file access or internal MCP tools, not a web scraper
- **Social media profiles or paywalled publications** — Firecrawl does not bypass authentication walls; for paywalled trade press (for example, Skift Research reports) scrape only the free-access portion and note the limitation in the KB entry

## Fallback rule

When the Firecrawl MCP tools are not available in the toolset: surface the problem to the user and stop.

Do not route around it by substituting another tool. The four Fourth skills produce `.firecrawl/` output that the `kb-ingest-review` skill expects. A WebFetch workaround breaks the staging pipeline and produces no structured output for KB ingestion.

See `references/credit-budget.md` for guidance on estimating operation costs before starting a task that may be expensive.
