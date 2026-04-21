---
name: market-scan
description: |
  Sweep Fourth's curated hospitality trade press for industry news, trends, and signals. Feeds both EBR builds (Phase 1.5 benchmarking context) and marketing research. Use when users request a time-bounded hospitality-industry news sweep — phrases like "scan hospitality news for Q1 2026 trends", "what's happening in restaurant labor news", "industry signals on tipping legislation", "what's the trade press saying about AI in restaurants", "market scan for hotel tech", "grab the latest NRN headlines", "what are restaurant operators worrying about this month", "trade press sweep on [topic]", "hospitality trends this quarter", or "scan NRN for [topic]". Queries curated sources (NRN, FSR, Skift, Hotel News Now, Nation's Restaurant News, Restaurant Business, AHLA, National Restaurant Association) and summarizes in Fourth voice. Do NOT trigger for general web search (use firecrawl-search), competitor-specific research (use competitor-intel), or customer-specific research (use ebr-research).
allowed-tools:
  - mcp__firecrawl__firecrawl_search
  - mcp__firecrawl__firecrawl_scrape
  - mcp__firecrawl__firecrawl_map
  - Bash(mkdir *)
  - Bash(date *)
  - Read
  - Write
---

# Market Scan

Time-bounded sweep of curated hospitality trade press. Produces a dated markdown brief with source attribution that feeds EBR narratives and marketing positioning.

## Purpose

- Surface industry news, trends, and signals the CSM or marketing team can cite.
- Use curated, high-signal sources — not raw search results.
- Produce a scannable brief in Fourth voice with every claim sourced.

## When to Use

| Trigger | Example |
|---------|---------|
| Time-bounded news sweep | "What hit the hospitality trade press last week?" |
| Topic sweep | "Find industry signals on tipping legislation" |
| Segment context for EBR | "Pressures affecting QSR operators this quarter" |
| Marketing content prep | "What's trending in restaurant tech coverage?" |

**Do NOT use this skill for:**
- Specific vendor intelligence — use `competitor-intel`
- Customer account research — use `ebr-research`
- General web search — use `../firecrawl-search`

## Prerequisites

1. Firecrawl MCP must be connected — if `mcp__firecrawl__firecrawl_search` (or any firecrawl tool) is not in the available toolset, run `/fourth-firecrawl:setup` to wire it up. Do not fall back to WebFetch or WebSearch.
2. Source catalog:
   - `${CLAUDE_PLUGIN_ROOT}/references/hospitality-sources.md` — canonical list of NRN, FSR, Skift, Hotel News Now, Restaurant Business, NRA, AHLA, Restaurant Dive, etc.
3. Voice guide (optional but preferred for write-up):
   - `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md`
4. Credit budget awareness — see Cost section below.

## Workflow

1. **Clarify scope** -> topic + segment + time window (past week? past month? past quarter?).
2. **Pick sources** -> read `${CLAUDE_PLUGIN_ROOT}/references/hospitality-sources.md`, select 3-6 relevant domains.
3. **Stage output directory** -> `mkdir -p .firecrawl/market-scan`.
4. **Run search or map+scrape** -> prefer `mcp__firecrawl__firecrawl_search` with `sources: [{ "type": "news" }]` and `tbs` time filters.
5. **Write the brief** -> dated markdown file with source attribution table + Fourth-voice summary via the Write tool.
6. **Next step:** suggest `kb-ingest-review` if the sweep has reusable insights for the KB under `messaging/` or `competitive/` folders.

## Examples

First, stage the output directory:

```bash
mkdir -p .firecrawl/market-scan
```

### News sweep, past week, general topic (search + inline scrape)

```json
{
  "name": "mcp__firecrawl__firecrawl_search",
  "arguments": {
    "query": "restaurant labor legislation 2026",
    "sources": [{ "type": "news" }],
    "tbs": "qdr:w",
    "limit": 15,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }
}
```

Then Write the returned JSON to `.firecrawl/market-scan/labor-legislation-<YYYYMMDD>.json`.

### Constrained to a specific trade press domain

```json
{
  "name": "mcp__firecrawl__firecrawl_search",
  "arguments": {
    "query": "site:nrn.com tipping",
    "sources": [{ "type": "news" }],
    "tbs": "qdr:m",
    "limit": 20,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }
}
```

### Map + scrape for a known trade site's coverage

Step 1 — find recent coverage pages:

```json
{
  "name": "mcp__firecrawl__firecrawl_map",
  "arguments": {
    "url": "https://www.nrn.com",
    "search": "AI in restaurants",
    "limit": 30
  }
}
```

Step 2 — scrape a chosen article (repeat for each URL):

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://www.nrn.com/technology/article-one",
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

### Sweep across multiple topics

Run `mcp__firecrawl__firecrawl_search` once per topic in sequence (the MCP handles concurrency server-side). Example topics:

- `ghost kitchens` / `qdr:m`
- `hotel labor shortage` / `qdr:m`
- `restaurant tipping` / `qdr:w`

Each call returns JSON; Write each result to `.firecrawl/market-scan/<topic>-<YYYYMMDD>.json`.

## Time-Window Values

The `tbs` parameter on `firecrawl_search` controls the recency window:

| `tbs` value | Window |
|-------------|--------|
| `qdr:h` | Past hour |
| `qdr:d` | Past day |
| `qdr:w` | Past week |
| `qdr:m` | Past month |
| `qdr:y` | Past year |

Default is unbounded — always pass `tbs` for market scans so you don't surface stale content.

## Source Filtering

The `sources` parameter (array of `{ type: "web" | "news" | "images" }`) narrows search to a vertical. For hospitality trade press, combine `[{ "type": "news" }]` with `site:` operators in the query string when you need to pin one domain (see examples).

## MCP Tools Used

| Tool | Source skill | Notes |
|------|--------------|-------|
| `mcp__firecrawl__firecrawl_search` | `../firecrawl-search` | News + time-filtered search; inline scrape via `scrapeOptions` |
| `mcp__firecrawl__firecrawl_map` | `../firecrawl-map` | Pin to a single trade-press domain |
| `mcp__firecrawl__firecrawl_scrape` | `../firecrawl-scrape` | Fetch an individual article |

Stage all output under `.firecrawl/market-scan/` via the Write tool.

## Output Format

Produce a markdown brief at `.firecrawl/market-scan/<topic>-<YYYYMMDD>.md` with this structure:

```markdown
# Market Scan: <topic>
**Window:** <past week | past month | custom>
**Sources:** NRN, FSR, Skift, Hotel News Now, ...
**Date:** <YYYY-MM-DD>

## Executive Summary
<3-5 sentences in Fourth voice — direct, operator-focused, no fluff>

## Key Signals
| Signal | Source | Confidence |
|--------|--------|-----------|
| <headline> | <outlet + URL> | VERIFIED / REPORTED |

## Implications for Fourth
- <Positioning angle>
- <EBR talking point>

## Gaps
<What was thin / what the user should fill>
```

Voice: use `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md` — concise, operator-first, no hype. Every claim must cite a source URL.

## Cost

News sweeps with inline `scrapeOptions` on 15 results can approach ~150-300 credits. Default guardrails: `limit: 10-20` for daily scans, cap `limit: 30` for monthly deep dives, always pass `tbs` to scope. Check balance at `firecrawl.dev/app`.

## See Also

- `../firecrawl-search/SKILL.md` — underlying search tool with `tbs` and `sources`
- `../firecrawl-map/SKILL.md` — alternative when targeting a single known domain
- `../firecrawl-scrape/SKILL.md` — fetch individual articles after finding them
- `../kb-ingest-review/SKILL.md` — push approved signals to Marketing Brain KB
- `${CLAUDE_PLUGIN_ROOT}/references/hospitality-sources.md` — curated source list
- `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md` — voice/tone reference
