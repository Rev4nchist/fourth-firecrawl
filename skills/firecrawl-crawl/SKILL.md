---
name: firecrawl-crawl
description: |
  Bulk-extract content from an entire website or site section, via the hosted Firecrawl MCP. Use when users want to crawl a site, extract all pages from a docs section, or bulk-scrape multiple pages following links — phrases like "crawl", "get all the pages", "extract everything under /docs", "bulk extract", or any request for content from many pages on the same site. Handles depth limits, path filtering, and concurrent extraction. Async: returns a job id that must be polled with firecrawl_check_crawl_status. Do NOT trigger for single-page scrape (use firecrawl-scrape), URL discovery only (use firecrawl-map), or schema-driven extract across known URLs (use firecrawl-agent).
allowed-tools:
  - mcp__firecrawl__firecrawl_crawl
  - mcp__firecrawl__firecrawl_check_crawl_status
  - Read
  - Write
  - Bash(mkdir *)
---

# firecrawl-crawl

Async bulk extraction via the hosted Firecrawl MCP. Starts a crawl job, returns a job id, and you poll for status + results.

> **Tool namespace:** your Cowork runtime may prefix Firecrawl tools with its connector UUID or name (e.g., `mcp__68cba2b7-…__firecrawl_crawl` or `mcp__firecrawl-official__firecrawl_crawl`). Examples below use the short names `firecrawl_crawl` and `firecrawl_check_crawl_status`; Claude will match by intent — call whichever full names are registered in your session.

## Preflight

If `firecrawl_crawl` or `firecrawl_check_crawl_status` is NOT in the available toolset, STOP. Instruct the user to run `/fourth-firecrawl:setup` to wire up the Firecrawl MCP. Do NOT fall back to WebFetch, WebSearch, or any substitute — the plugin's per-user credit accountability depends on MCP.

## When to Use

- You need content from many pages on a single site (e.g., all `/docs/`)
- You want to extract an entire site section
- Step 4 in the workflow escalation pattern: search → scrape → map → **crawl** → interact

## Two-Step Async Flow

Crawls run asynchronously. You must:

1. Call `firecrawl_crawl` — returns `{ id, url }`.
2. Poll `firecrawl_check_crawl_status` with `{ id }` every 10-30s until `status` is `completed`.
3. When complete, the status response contains the extracted pages.

## Quick Start

### Step 1 — start the crawl

```json
{
  "name": "firecrawl_crawl",
  "arguments": {
    "url": "https://docs.example.com",
    "includePaths": ["/docs"],
    "limit": 50,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }
}
```

Response contains an `id`, e.g. `"crawl-abc123"`.

### Step 2 — poll status

```json
{
  "name": "firecrawl_check_crawl_status",
  "arguments": {
    "id": "crawl-abc123"
  }
}
```

Repeat until `status === "completed"`. Response will contain the crawled pages.

## Parameters (firecrawl_crawl)

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string (required) | Root URL to crawl |
| `prompt` | string | Natural-language scope hint for the crawler |
| `includePaths` / `excludePaths` | string[] | URL path filters |
| `maxDiscoveryDepth` | number | Max link depth to follow |
| `sitemap` | enum | `include`, `skip`, or `only` |
| `limit` | number | Max pages (cap this — 50-100 is a safe default) |
| `allowExternalLinks` | boolean | Follow links off-domain |
| `allowSubdomains` | boolean | Follow subdomains |
| `crawlEntireDomain` | boolean | Ignore path restrictions |
| `delay` | number | ms between requests (respect target) |
| `maxConcurrency` | number | Parallel workers |
| `deduplicateSimilarURLs` | boolean | Skip near-duplicate URLs |
| `ignoreQueryParameters` | boolean | Dedupe by stripping `?foo=bar` |
| `scrapeOptions` | object | Per-page scrape config (formats, onlyMainContent, etc.) |

## Parameters (firecrawl_check_crawl_status)

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string (required) | Job id from `firecrawl_crawl` response |

## Examples

### Crawl a docs section

```json
{
  "name": "firecrawl_crawl",
  "arguments": {
    "url": "https://docs.r365hub.com",
    "includePaths": ["/docs"],
    "limit": 50,
    "maxDiscoveryDepth": 3,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }
}
```

### Crawl with exclusions

```json
{
  "name": "firecrawl_crawl",
  "arguments": {
    "url": "https://www.example.com",
    "excludePaths": ["/admin", "/careers", "/legal"],
    "limit": 100,
    "scrapeOptions": {
      "formats": ["markdown"],
      "onlyMainContent": true
    }
  }
}
```

### Crawl with subdomains

```json
{
  "name": "firecrawl_crawl",
  "arguments": {
    "url": "https://example.com",
    "allowSubdomains": true,
    "limit": 150,
    "delay": 500
  }
}
```

## Tips

- **Always set `limit`.** Uncapped crawls can burn hundreds of credits on a large site.
- **Prefer `includePaths`** over `maxDiscoveryDepth` — it's more predictable.
- **Poll at 10-30s intervals.** Large crawls take minutes.
- **Crawl responses can be huge.** The tool warns about token overflow — expect to process in batches or filter by URL after completion.
- **Credit budget:** crawl is ~1 credit per page scraped. A 100-page crawl is ~100 credits. Check balance at `firecrawl.dev/app`.

## See Also

- `../firecrawl-scrape/SKILL.md` — single-page scrape
- `../firecrawl-map/SKILL.md` — discover URLs before deciding to crawl
- `../firecrawl-agent/SKILL.md` — schema-driven extract across multiple known URLs
- `../competitor-intel/SKILL.md` — Fourth-specific crawl patterns for competitor sites
