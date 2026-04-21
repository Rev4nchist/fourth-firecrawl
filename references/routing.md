# Routing Guide

Decision table for which skill to use and when. Read the preflight section before every run.

## Preflight — authentication gate

Before executing any research task, check Firecrawl authentication:

```bash
firecrawl --status
```

**If this command returns an error, "Not authenticated", or "No API key found": STOP.**

Tell the user to run `/fourth-firecrawl:setup` and do not proceed with the research task. Do NOT fall back to WebFetch, WebSearch, built-in search, or any other web-access tool as a substitute. Firecrawl is the designated tool for these workflows — silent fallback produces inconsistent output, bypasses the credit guardrails, and writes nothing to `.firecrawl/` for KB ingestion.

The same stop-and-surface rule applies if authentication succeeds but credits are at zero. Check `firecrawl --status` output for "Credits: 0 remaining" and surface the situation to the user before any billable operation.

## Routing table

| User intent | Primary skill | When to use | Related upstream skills |
|-------------|---------------|-------------|------------------------|
| Research a specific competitor's pricing, features, or case studies | `competitor-intel` | Named competitor in Fourth's registry (R365, 7shifts, Deputy, UKG, Toast, Paycom, Homebase, Paylocity, ADP, Push Operations, When I Work) | `firecrawl-agent`, `firecrawl-scrape`, `firecrawl-map` |
| Scrape a competitor page not in the registry | `firecrawl-scrape` | One-off URL, not a named registry entry; no extraction schema needed | — |
| Find all URLs on a competitor or source site | `firecrawl-map` | Need to discover subpages before scraping in bulk | — |
| Crawl an entire competitor docs or blog section | `firecrawl-crawl` | Need many pages from one site (e.g., all /blog/ posts) | `firecrawl-map` |
| Track hospitality industry news or trends | `market-scan` | Recurring or ad-hoc news sweep across trade press catalog | `firecrawl-search` |
| Find what content competitors publish that Fourth does not | `content-gap-analysis` | Strategic content planning, gap identification before a campaign or EBR | `competitor-intel`, `market-scan` |
| Land staged research into the Marketing Brain KB | `kb-ingest-review` | After any skill run that produced `.firecrawl/` output the user wants to keep | — |
| Extract structured data from a complex or JavaScript-heavy site | `firecrawl-agent` | Needs AI-guided navigation or a JSON schema; `firecrawl-scrape` alone is insufficient | — |
| Interact with a page requiring clicks, form fills, or pagination | `firecrawl-scrape` + `firecrawl-interact` | Content locked behind a button, modal, or multi-step flow | — |
| Download an entire site as local files | `firecrawl-download` | Archive a site snapshot; not for ongoing research workflows | — |
| General web search on a topic with no specific URL | `firecrawl-search` | No URL yet; need to discover sources first | `firecrawl-scrape` for follow-up |

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

- **Single-URL reads of known, static pages** — use the built-in WebFetch tool for quick one-off lookups where no staging or credit tracking is needed and the content is a simple page read
- **Fetching internal URLs** — anything behind Fourth's VPN, internal wiki, or authenticated internal tools; Firecrawl cannot authenticate with Fourth's internal systems
- **Fourth's own properties** — use direct file access or internal MCP tools, not a web scraper
- **Social media profiles or paywalled publications** — Firecrawl does not bypass authentication walls; for social content use appropriate tools; for paywalled trade press (e.g., Skift Research reports, SHRM member content) note the limitation in the KB entry and scrape only the free-access portion

## Fallback rule

When Firecrawl authentication fails or credits are exhausted: surface the problem to the user and stop.

Do not route around it by substituting another tool. The Four Fourth skills produce `.firecrawl/` output that the `kb-ingest-review` skill expects. A WebFetch workaround breaks the staging pipeline and produces no structured output for KB ingestion.

If the user explicitly asks to use a different tool after being told about the auth/quota issue, that is a user decision — execute it, but do not initiate the substitution silently.
