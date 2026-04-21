---
name: firecrawl-search
description: |
  Web search with optional full-page content extraction, via the hosted Firecrawl MCP. Use when users want to search the web, find articles, research a topic, look something up, find recent news, or discover sources — phrases like "search for", "find me", "look up", "what are people saying about", or "find articles about". Returns real search results with optional full-page markdown — not just snippets. Supports Google-style operators (site:, intitle:, -, quoted terms), time filters (past hour/day/week/month/year), and multi-source search (web/news/images). Provides capabilities beyond Claude's built-in WebSearch. Do NOT trigger for scraping a specific known URL (use firecrawl-scrape) or enumerating pages on a single site (use firecrawl-map).
allowed-tools:
  - mcp__firecrawl__firecrawl_search
  - Read
  - Write
  - Bash(mkdir *)
---

# firecrawl-search

Web search via the hosted Firecrawl MCP. Returns search results with optional inline scrape of each result's full page.

> **Tool namespace:** your Cowork runtime may prefix Firecrawl tools with its connector UUID or name (e.g., `mcp__68cba2b7-…__firecrawl_search` or `mcp__firecrawl-official__firecrawl_search`). Examples below use the short name `firecrawl_search`; Claude will match by intent — call whichever full name is registered in your session.

## Preflight

If `firecrawl_search` is NOT in the available toolset, STOP. Instruct the user to run `/fourth-firecrawl:setup` to wire up the Firecrawl MCP. Do NOT fall back to WebFetch, WebSearch, or any substitute — the plugin's per-user credit accountability depends on MCP.

## When to Use

- You don't have a specific URL yet
- You need to find pages, answer questions, or discover sources
- You want time-bounded news (past hour/day/week)
- First step in the workflow escalation pattern: **search** → scrape → map → crawl → interact

## Quick Start

```json
{
  "name": "firecrawl_search",
  "arguments": {
    "query": "restaurant365 pricing changes",
    "limit": 10,
    "tbs": "qdr:w",
    "sources": [{ "type": "news" }]
  }
}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string (required, min 1 char) | Search query (supports `site:`, `intitle:`, `-`, quoted terms) |
| `limit` | number | Results count; default is low (~5) to avoid timeouts |
| `tbs` | string | Google time-based filter (`qdr:h\|d\|w\|m\|y`) |
| `filter` | string | Additional search filter |
| `location` | string | Geo context for search |
| `sources` | array | Multi-source: `[{ type: "web" \| "news" \| "images" }]` |
| `scrapeOptions` | object | Full scrape params — scrape each result inline |
| `enterprise` | array | `default`, `anon`, or `zdr` (zero data retention) |

## Time Filter Reference

| `tbs` value | Window |
|-------------|--------|
| `qdr:h` | Past hour |
| `qdr:d` | Past day |
| `qdr:w` | Past week |
| `qdr:m` | Past month |
| `qdr:y` | Past year |

## Examples

### News from the past week

```json
{
  "name": "firecrawl_search",
  "arguments": {
    "query": "restaurant labor legislation 2026",
    "limit": 15,
    "tbs": "qdr:w",
    "sources": [{ "type": "news" }]
  }
}
```

### Search + inline scrape (no follow-up scrape needed)

```json
{
  "name": "firecrawl_search",
  "arguments": {
    "query": "tipping compliance restaurants",
    "limit": 10,
    "tbs": "qdr:m",
    "sources": [{ "type": "news" }],
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }
}
```

### Site-scoped search with Google operator

```json
{
  "name": "firecrawl_search",
  "arguments": {
    "query": "site:nrn.com ghost kitchens",
    "limit": 20,
    "tbs": "qdr:m"
  }
}
```

## Tips

- **`scrapeOptions` fetches full content inline** — don't re-scrape URLs from search results. Saves credits.
- **Always pass `tbs`** when recency matters. Unbounded searches surface stale pages.
- **Use `site:`** to constrain to a specific trade press domain (e.g., `site:nrn.com`).
- **Use `limit` generously but mind the budget.** 10 results with inline `scrapeOptions` burns ~50 credits; 30 burns ~150.
- **`sources: [{ type: "news" }]`** is the news vertical (better for time-bounded sweeps). Default is `web`.

## See Also

- `../firecrawl-scrape/SKILL.md` — scrape a specific URL once you have it
- `../firecrawl-map/SKILL.md` — enumerate URLs within a known site
- `../firecrawl-crawl/SKILL.md` — bulk-extract from a site section
- `../market-scan/SKILL.md` — Fourth-specific trade press sweep using this tool
