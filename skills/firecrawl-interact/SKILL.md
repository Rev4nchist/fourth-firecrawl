---
name: firecrawl-interact
description: |
  Control and interact with a live browser session on any scraped page — click buttons, fill forms, navigate flows, scroll, and extract data using natural language prompts or code. Via the hosted Firecrawl MCP. Use when the user needs to interact with a webpage beyond simple scraping: logging into a site, submitting forms, clicking through pagination, handling infinite scroll, navigating multi-step checkout or wizard flows, or when a regular scrape failed because content is behind JavaScript interaction. Triggers on "browser", "interact", "click", "fill out the form", "log in to", "sign in", "submit", "paginated", "next page", "infinite scroll", "interact with the page", "navigate to", "open a session", or "scrape failed". Do NOT trigger for web searches (use firecrawl-search instead), simple scrapes (use firecrawl-scrape), or bulk extraction (use firecrawl-crawl).
allowed-tools:
  - mcp__firecrawl__firecrawl_scrape
  - mcp__firecrawl__firecrawl_interact
  - mcp__firecrawl__firecrawl_interact_stop
  - Read
  - Write
  - Bash(mkdir *)
---

# firecrawl-interact

Two paths for interactive pages: inline `actions` on `firecrawl_scrape` (simple pre-extract steps), or `firecrawl_interact` against a scrapeId (live browser session after scraping).

## Preflight

If `mcp__firecrawl__firecrawl_scrape` and `mcp__firecrawl__firecrawl_interact` are NOT in the available toolset, STOP. Instruct the user to run `/fourth-firecrawl:setup` to wire up the Firecrawl MCP. Do NOT fall back to WebFetch, WebSearch, or any substitute — the plugin's per-user credit accountability depends on MCP.

## When to Use

- Content requires interaction: clicks, form fills, pagination, login
- `firecrawl_scrape` alone didn't capture what you need
- You need a multi-step flow (login, then navigate, then extract)
- Last resort in the workflow escalation pattern: search → scrape → map → crawl → **interact**
- **Never use interact for web searches** — use `firecrawl_search` instead

## Two Approaches

### Approach A — Inline `actions` on `firecrawl_scrape`

Best when interaction is simple and happens BEFORE extraction (e.g., click a "Load more" button, wait for a modal, fill one field). One call, one result.

### Approach B — `firecrawl_interact` against a scrapeId

Best when you need a live browser session that stays open across multiple operations (e.g., login flow, pagination, iterative form testing). Requires a `scrapeId` from a prior `firecrawl_scrape` response, plus a stop call when done.

## Approach A — `firecrawl_scrape` with `actions`

### Quick Start — click then extract

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://example.com/dynamic",
    "formats": ["markdown"],
    "actions": [
      { "type": "wait", "milliseconds": 2000 },
      { "type": "click", "selector": "#load-more" },
      { "type": "wait", "milliseconds": 1500 }
    ]
  }
}
```

### Fill a search box before extracting

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://example.com/search",
    "formats": ["markdown"],
    "actions": [
      { "type": "write", "selector": "#query", "text": "pricing" },
      { "type": "press", "key": "Enter" },
      { "type": "wait", "milliseconds": 3000 }
    ]
  }
}
```

Supported action types include: `click`, `wait`, `write`, `press`, `screenshot`, `scroll`, `scrape`, `executeJavascript`, `pdf`, `generatePDF`. <!-- verify: exact parameter shape per action type is not fully documented in the spec; the names above match firecrawl_scrape's actions array -->

## Approach B — `firecrawl_interact` + scrapeId

### Step 1 — scrape to open the session

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://app.example.com/login",
    "formats": ["markdown"]
  }
}
```

Response metadata includes a `scrapeId` (e.g., `"scrape-abc123"`).

### Step 2 — interact via prompt (natural language)

```json
{
  "name": "mcp__firecrawl__firecrawl_interact",
  "arguments": {
    "scrapeId": "scrape-abc123",
    "prompt": "Fill the email field with user@example.com and click the login button"
  }
}
```

### Step 2 alt — interact via code

```json
{
  "name": "mcp__firecrawl__firecrawl_interact",
  "arguments": {
    "scrapeId": "scrape-abc123",
    "code": "agent-browser click @e5",
    "language": "bash",
    "timeout": 30
  }
}
```

### Step 3 — stop the session

```json
{
  "name": "mcp__firecrawl__firecrawl_interact_stop",
  "arguments": {
    "scrapeId": "scrape-abc123"
  }
}
```

## Parameters (firecrawl_interact)

| Parameter | Type | Description |
|-----------|------|-------------|
| `scrapeId` | string (required) | From prior `firecrawl_scrape` response metadata |
| `prompt` | string | Natural-language action (use this OR `code`) |
| `code` | string | Code to execute (use this OR `prompt`) |
| `language` | enum | `bash`, `python`, or `node` (default `node`) |
| `timeout` | number (1-300) | Seconds (default 30) |

## Parameters (firecrawl_interact_stop)

| Parameter | Type | Description |
|-----------|------|-------------|
| `scrapeId` | string (required) | Session to terminate |

## Tips

- **Prefer Approach A (`actions`) when possible.** One call is simpler and cheaper than a full live session.
- **Always call `firecrawl_interact_stop` when done** with Approach B — free browser resources.
- **Prompt is usually easier than code.** The agent interprets natural-language instructions reliably for standard interactions.
- **Use `code` for precision** when you need specific selectors or deterministic behavior.
- **Live sessions cost credits per second.** Long-running interact sessions get expensive — stop them.

## See Also

- `../firecrawl-scrape/SKILL.md` — try scrape first, escalate here only when needed
- `../firecrawl-search/SKILL.md` — for web searches (never use interact for searching)
- `../firecrawl-agent/SKILL.md` — autonomous research / schema-driven extract (less manual control)
