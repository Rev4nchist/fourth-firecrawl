---
name: firecrawl-map
description: |
  Discover and list all URLs on a website, with optional search filtering, via the hosted Firecrawl MCP. Use when users want to find a specific page on a large site, list all URLs, see the site structure, or find where something is on a domain — phrases like "map the site", "find the URL for", "what pages are on", or "list all pages". Essential when the user knows which site but not which exact page. Do NOT trigger for general web search (use firecrawl-search), scraping a known URL (use firecrawl-scrape), or bulk content extraction (use firecrawl-crawl).
allowed-tools:
  - mcp__firecrawl__firecrawl_map
  - Read
  - Write
  - Bash(mkdir *)
---

# firecrawl-map

Discover URLs on a single site via the hosted Firecrawl MCP. Optionally filter URLs by a search query to find a specific page fast.

> **Tool namespace:** your Cowork runtime may prefix Firecrawl tools with its connector UUID or name (e.g., `mcp__68cba2b7-…__firecrawl_map` or `mcp__firecrawl-official__firecrawl_map`). Examples below use the short name `firecrawl_map`; Claude will match by intent — call whichever full name is registered in your session.

## Preflight

If `firecrawl_map` is NOT in the available toolset, STOP. Instruct the user to run `/fourth-firecrawl:setup` to wire up the Firecrawl MCP. Do NOT fall back to WebFetch, WebSearch, or any substitute — the plugin's per-user credit accountability depends on MCP.

## When to Use

- You need to find a specific subpage on a large site
- You want a list of all URLs on a site before scraping or crawling
- Step 3 in the workflow escalation pattern: search → scrape → **map** → crawl → interact

## Quick Start

```json
{
  "name": "firecrawl_map",
  "arguments": {
    "url": "https://docs.r365hub.com",
    "search": "pricing"
  }
}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string (required, URL) | Root URL of the site to map |
| `search` | string | Filter URLs by matching query |
| `sitemap` | enum | `include`, `skip`, or `only` — sitemap handling strategy |
| `includeSubdomains` | boolean | Include subdomain URLs |
| `limit` | number | Max URLs to return |
| `ignoreQueryParameters` | boolean | Dedupe URLs by stripping `?foo=bar` |

## Examples

### Find a specific page on a large docs site

```json
{
  "name": "firecrawl_map",
  "arguments": {
    "url": "https://docs.example.com",
    "search": "authentication",
    "limit": 50
  }
}
```

### List all URLs on a marketing site

```json
{
  "name": "firecrawl_map",
  "arguments": {
    "url": "https://www.7shifts.com",
    "limit": 500,
    "ignoreQueryParameters": true
  }
}
```

### Enumerate a competitor's blog

```json
{
  "name": "firecrawl_map",
  "arguments": {
    "url": "https://restaurant365.com/blog",
    "limit": 200
  }
}
```

## Tips

- **Map + scrape is a common pattern**: use `firecrawl_map` with `search` to find the right URL, then `firecrawl_scrape` it.
- **Use `sitemap: "only"`** to strictly respect a site's declared sitemap — fastest but may miss pages.
- **Use `sitemap: "skip"`** to map via link-following only — slower but finds un-sitemapped pages.
- **`includeSubdomains: true`** captures `blog.example.com`, `docs.example.com`, etc. Default is same-host only.
- **Credit budget:** map is cheap (~1 credit per call regardless of result count). Scraping the discovered URLs is where cost accumulates.

## See Also

- `../firecrawl-scrape/SKILL.md` — scrape the URLs you discover
- `../firecrawl-crawl/SKILL.md` — bulk extract instead of map + scrape
- `../firecrawl-search/SKILL.md` — find sites you don't know about yet
- `../content-gap-analysis/SKILL.md` — Fourth-specific skill that maps competitor blogs
