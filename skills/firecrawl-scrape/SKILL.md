---
name: firecrawl-scrape
description: |
  Extract clean markdown from any URL, including JavaScript-rendered SPAs, via the hosted Firecrawl MCP. Use when users provide a URL and want its content — phrases like "scrape", "grab", "fetch", "pull", "get the page", "extract from this URL", or "read this webpage". Handles JS-rendered pages, schema-driven JSON extraction, and returns LLM-optimized markdown. Prefer this over WebFetch for any webpage content extraction. Do NOT trigger for web search (use firecrawl-search), URL discovery on a single site (use firecrawl-map), or bulk multi-page extraction (use firecrawl-crawl).
allowed-tools:
  - mcp__firecrawl__firecrawl_scrape
  - Read
  - Write
  - Bash(mkdir *)
---

# firecrawl-scrape

Single-URL scrape via the hosted Firecrawl MCP. Returns clean, LLM-optimized markdown. The fastest, most reliable scraper for one page at a time.

## Preflight

If `mcp__firecrawl__firecrawl_scrape` is NOT in the available toolset, STOP. Instruct the user to run `/fourth-firecrawl:setup` to wire up the Firecrawl MCP. Do NOT fall back to WebFetch, WebSearch, or any substitute — the plugin's per-user credit accountability depends on MCP.

## When to Use

- You have a specific URL and want its content as markdown
- The page is static or JS-rendered (SPA)
- You need schema-driven JSON from a single known page
- Step 2 in the workflow escalation pattern: search → **scrape** → map → crawl → interact

## Quick Start

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://www.r365hub.com/pricing",
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string (required) | Target URL |
| `formats` | array | `markdown`, `html`, `rawHtml`, `links`, `screenshot`, `summary`, `changeTracking`, `json`, `branding` |
| `onlyMainContent` | boolean | Strip nav/footer/sidebar |
| `includeTags` / `excludeTags` | string[] | HTML tag filters |
| `waitFor` | number | ms to wait for JS rendering (5000-10000 for SPAs) |
| `timeout` | number | Request timeout in ms |
| `mobile` | boolean | Use mobile viewport |
| `skipTlsVerification` | boolean | Ignore TLS errors |
| `removeBase64Images` | boolean | Strip inline base64 images |
| `proxy` | enum | `basic` or `stealth` |
| `location` | object | `{ country, languages }` geo-spoofing |
| `maxAge` | number | Cache TTL — up to ~5x faster on cached hits |
| `storeInCache` | boolean | Persist result to cache |
| `blockAds` | boolean | Block ad domains during render |
| `jsonOptions` | object | `{ prompt, schema, systemPrompt }` when `formats` includes `json` |
| `actions` | array | Interactive actions BEFORE extraction (see firecrawl-interact) |

## Examples

### Plain markdown of main content

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://www.r365hub.com/pricing",
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

### JS-rendered SPA (wait for content)

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://app.example.com/dashboard",
    "formats": ["markdown"],
    "waitFor": 5000,
    "onlyMainContent": true
  }
}
```

### Schema-driven JSON extraction

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://competitor.com/pricing",
    "formats": [
      {
        "type": "json",
        "prompt": "Extract all pricing tiers",
        "schema": {
          "type": "object",
          "properties": {
            "tiers": { "type": "array" }
          }
        }
      }
    ]
  }
}
```

### Markdown + links in one call

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://example.com/blog",
    "formats": ["markdown", "links"],
    "onlyMainContent": true
  }
}
```

## Tips

- **Prefer `firecrawl_scrape` over `firecrawl_extract` for one known URL.** Extract is async and costs more — reserve it for multi-URL batches.
- **Use `maxAge` for repeat scrapes.** Cached hits are dramatically cheaper and faster.
- **Use `waitFor: 5000-10000` for SPAs.** Static HTML needs no wait.
- **Returned `scrapeId` enables `firecrawl_interact`.** If you might need to click or fill forms afterwards, save the scrapeId from the response metadata.
- **Credit budget:** single scrape is cheap (~1 credit); schema-driven JSON is moderate (~5 credits). See `../../references/credit-budget.md` if present.

## See Also

- `../firecrawl-search/SKILL.md` — find pages when you don't have a URL
- `../firecrawl-map/SKILL.md` — discover URLs within a site
- `../firecrawl-crawl/SKILL.md` — bulk-extract many pages
- `../firecrawl-agent/SKILL.md` — schema-driven extract across multiple URLs or autonomous research
- `../firecrawl-interact/SKILL.md` — click, fill, scroll after scraping
