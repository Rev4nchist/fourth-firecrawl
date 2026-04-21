---
name: firecrawl-agent
description: |
  AI-powered structured extraction from websites, via the hosted Firecrawl MCP. Use when users want structured data as JSON, need to extract pricing tiers, product listings, directory entries, case-study data, or any structured records across one or more pages — phrases like "extract structured data", "get all the products", "pull pricing info", "extract as JSON", "deep research", "find me across the web", or any time the user provides a JSON schema for website data. Routes between two tools: firecrawl_extract (when you have URLs and a schema — fast) and firecrawl_agent (when you don't know where the data lives — slow, autonomous). Do NOT trigger for single-page markdown scrape (use firecrawl-scrape), web search (use firecrawl-search), or bulk same-site content (use firecrawl-crawl).
allowed-tools:
  - mcp__firecrawl__firecrawl_extract
  - mcp__firecrawl__firecrawl_agent
  - mcp__firecrawl__firecrawl_agent_status
  - Read
  - Write
  - Bash(mkdir *)
---

# firecrawl-agent

Two MCP tools cover structured extraction: `firecrawl_extract` (you know the URLs, you have a schema) and `firecrawl_agent` (autonomous research, open-ended).

> **Tool namespace:** your Cowork runtime may prefix Firecrawl tools with its connector UUID or name (e.g., `mcp__68cba2b7-…__firecrawl_extract` or `mcp__firecrawl-official__firecrawl_extract`). Examples below use the short names `firecrawl_extract`, `firecrawl_agent`, and `firecrawl_agent_status`; Claude will match by intent — call whichever full names are registered in your session.

## Preflight

If `firecrawl_extract` or `firecrawl_agent` is NOT in the available toolset, STOP. Instruct the user to run `/fourth-firecrawl:setup` to wire up the Firecrawl MCP. Do NOT fall back to WebFetch, WebSearch, or any substitute — the plugin's per-user credit accountability depends on MCP.

## Which Tool to Use

| Situation | Tool |
|-----------|------|
| You have specific URL(s) + schema, want JSON records back | `firecrawl_extract` |
| You have a research question, no specific URLs, need the agent to go find | `firecrawl_agent` + `firecrawl_agent_status` (async poll) |
| Multi-page same-site bulk extraction | Use `firecrawl-crawl` instead |

**Rule of thumb:** `firecrawl_extract` is faster and cheaper when you can name the URLs. Only use `firecrawl_agent` when you genuinely don't know where the data is.

## firecrawl_extract — Schema-Driven Extraction

Sync. Point it at URLs + schema, get structured records.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `urls` | string[] (required) | One or more URLs |
| `prompt` | string | Natural-language extraction instruction |
| `schema` | JSON schema object | Output shape |
| `allowExternalLinks` | boolean | Follow off-domain links during extraction |
| `enableWebSearch` | boolean | Allow web search for additional context |
| `includeSubdomains` | boolean | Include subdomain pages |

### Quick Start

```json
{
  "name": "firecrawl_extract",
  "arguments": {
    "urls": ["https://www.r365hub.com/pricing"],
    "prompt": "Extract all pricing tiers including name, monthly price, user limits, features",
    "schema": {
      "type": "object",
      "properties": {
        "tiers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "monthly_price": { "type": "number" },
              "user_limit": { "type": "integer" },
              "features": { "type": "array", "items": { "type": "string" } }
            }
          }
        }
      }
    }
  }
}
```

### Multi-URL extract (one schema, many pages)

```json
{
  "name": "firecrawl_extract",
  "arguments": {
    "urls": [
      "https://competitor-a.com/pricing",
      "https://competitor-b.com/pricing",
      "https://competitor-c.com/pricing"
    ],
    "prompt": "Extract pricing tiers from each page",
    "schema": {
      "type": "object",
      "properties": {
        "tiers": { "type": "array" }
      }
    }
  }
}
```

## firecrawl_agent — Autonomous Research (Async)

The agent navigates the web on its own. Slow (minutes), expensive, but handles open-ended research when URLs are unknown.

### Two-Step Async Flow

1. Start a job with `firecrawl_agent` — returns a job id.
2. Poll `firecrawl_agent_status` with `{ id }` every 10-30s until `status === "completed"`.

### Parameters (firecrawl_agent)

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string (required, max 10000 chars) | Natural-language research task |
| `urls` | string[] | Starting URLs to focus the agent |
| `schema` | JSON schema | Structured output shape |

### Parameters (firecrawl_agent_status)

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string (required) | Job id from `firecrawl_agent` response |

### Quick Start

```json
{
  "name": "firecrawl_agent",
  "arguments": {
    "prompt": "Find all US-based hospitality workforce management vendors with published pricing pages, and extract their pricing tiers",
    "schema": {
      "type": "object",
      "properties": {
        "vendors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "url": { "type": "string" },
              "tiers": { "type": "array" }
            }
          }
        }
      }
    }
  }
}
```

Then poll:

```json
{
  "name": "firecrawl_agent_status",
  "arguments": { "id": "agent-abc123" }
}
```

### Agent with starting URLs (faster)

```json
{
  "name": "firecrawl_agent",
  "arguments": {
    "prompt": "Extract all case studies with customer name, industry, and headline result",
    "urls": [
      "https://deputy.com/case-studies",
      "https://7shifts.com/case-studies"
    ]
  }
}
```

## Tips

- **Prefer `firecrawl_extract` when you can name URLs.** It's dramatically cheaper than `firecrawl_agent`.
- **Always provide a `schema`** for `firecrawl_extract` — otherwise you get freeform JSON that's hard to post-process.
- **Agent runs take minutes.** Kick off the job, poll every 10-30s, don't block on it.
- **`enableWebSearch: true`** on extract lets it pull supporting context from the broader web. Helpful for enrichment, more expensive.
- **Credit budget:** extract is ~5-20 credits per URL depending on schema complexity; agent runs are 100-1000+ credits. Check balance at `firecrawl.dev/app` before launching an agent.

## See Also

- `../firecrawl-scrape/SKILL.md` — single-page markdown or schema JSON (cheaper for one URL)
- `../firecrawl-crawl/SKILL.md` — bulk same-site extraction
- `../firecrawl-search/SKILL.md` — discover sources first when your research is news-led
- `../competitor-intel/SKILL.md` — Fourth-specific schema-driven competitor research
- `../content-gap-analysis/SKILL.md` — Fourth-specific three-way gap analysis using this tool
