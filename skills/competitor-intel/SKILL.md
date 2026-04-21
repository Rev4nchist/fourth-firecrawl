---
name: competitor-intel
description: |
  Scrape and structure competitor intelligence (pricing, features, case studies, customer logos) from Fourth's curated competitor registry. Uses pre-built JSON extraction schemas to produce comparable, structured output across vendors. Use when users request competitor research — phrases like "research R365 pricing", "get competitor intel on 7shifts", "pull Deputy features", "compare HCM competitors", "what's Paycom charging", "scrape competitor pricing pages", "competitive analysis on R365", or any named competitor in Fourth's registry (Restaurant365, 7shifts, Deputy, HotSchedules, When I Work, Paycom, UKG, Toast, Paylocity). Output is staged in `.firecrawl/competitor-intel/` for review before ingestion to the Marketing Brain KB. Do NOT trigger for general web search, customer research (use ebr-research for that), or one-off URL scraping (use firecrawl-scrape).
allowed-tools:
  - mcp__firecrawl__firecrawl_scrape
  - mcp__firecrawl__firecrawl_map
  - mcp__firecrawl__firecrawl_extract
  - mcp__firecrawl__firecrawl_agent
  - mcp__firecrawl__firecrawl_agent_status
  - Bash(mkdir *)
  - Bash(date *)
  - Read
  - Write
---

# Competitor Intel

Targeted, schema-driven competitor research. Produces structured, comparable intel that drops cleanly into Fourth's Marketing Brain KB under the `competitive/` folder.

> **Tool namespace:** your Cowork runtime may prefix Firecrawl tools with its connector UUID or name (e.g., `mcp__68cba2b7-…__firecrawl_extract` or `mcp__firecrawl-official__firecrawl_extract`). Examples below use the short names `firecrawl_scrape`, `firecrawl_map`, `firecrawl_extract`, `firecrawl_agent`, and `firecrawl_agent_status`; Claude will match by intent — call whichever full names are registered in your session.

## Purpose

- Scrape competitor pricing, features, case studies, and positioning from their own web properties.
- Use consistent JSON schemas so output across vendors is comparable.
- Stage output for human review before ingesting to the KB (never auto-ingest).

## When to Use

| Trigger | Example |
|---------|---------|
| Competitor named in Fourth registry | "Research R365 pricing" |
| Topic + competitor | "Get 7shifts feature list" |
| Comparative ask | "Compare HCM competitors on onboarding" |
| Refresh existing intel | "Update Deputy pricing — is their old data stale?" |

**Do NOT use this skill for:**
- Customer research on live hospitality accounts — use `ebr-research`
- General web search — use `../firecrawl-search`
- One-off arbitrary URL scraping — use `../firecrawl-scrape`

## Prerequisites

1. Firecrawl MCP must be connected — if `firecrawl_extract` (or any firecrawl tool) is not in the available toolset, run `/fourth-firecrawl:setup` to wire it up. Do not fall back to WebFetch or WebSearch.
2. Read the competitor registry to resolve name -> URLs:
   - `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md`
3. Pick the extraction schema that matches your intent:
   - `${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/` (pricing-page.json, feature-list.json, case-study.json, etc.)
4. Confirm the request will respect the credit budget — see `${CLAUDE_PLUGIN_ROOT}/references/credit-budget.md` if present, or default caps in the Cost section below.

## Known Competitors

| Name | Common alias | Primary domain |
|------|--------------|----------------|
| Restaurant365 | R365 | restaurant365.com |
| 7shifts | 7shifts | 7shifts.com |
| Deputy | Deputy | deputy.com |
| HotSchedules | HotSchedules (Fourth legacy) | fourth.com/hotschedules |
| When I Work | WIW | wheniwork.com |
| Paycom | Paycom | paycom.com |
| UKG | UKG (Kronos) | ukg.com |
| Toast | Toast scheduling | pos.toasttab.com |
| Paylocity | Paylocity | paylocity.com |

The full URL catalog (pricing pages, resources, case study indices) lives in `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md`.

## Workflow

1. **Resolve competitor** -> read registry, pick URLs relevant to the topic (pricing / features / case studies).
2. **Check `public_pricing` flag (PRICING REQUESTS ONLY)** -> before any pricing extract, read the competitor's entry in `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md`. If `public_pricing: false`, **SKIP the pricing page extract entirely** — don't burn credits on a gated page. Tell the user:
   > "`<competitor>` pricing is quote-only (gated). Refer to captured Fourth proposals and sales data in the Marketing Brain KB (`competitive/<vendor>-pricing-*`) instead of scraping. I can scan the KB or move on to features/case studies if you'd like."
   Only proceed to a pricing extract when `public_pricing: true`.
3. **Pick schema** -> match intent to a schema file under `${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/`.
4. **Stage output directory** -> `mkdir -p .firecrawl/competitor-intel`.
5. **Run `firecrawl_extract` with schema** (or `firecrawl_scrape` for simple single pages).
6. **Validate the extract (CASE STUDIES ONLY)** -> after extracting a case study, check the `publication_date` field:
   - If `publication_date` equals today's date (the scrape date), the model hallucinated it — the source page has no reliable date. **Drop the field** from the written output (set to `null` or omit entirely).
   - Log the miss in a comment in the output file so we know which source pages have no reliable date (e.g., `// publication_date missing on source — model returned today's date, dropped`).
   - Apply the same rule to other date fields where today's-date would be a hallucination signal (e.g., `announcement_date` on press releases).
7. **Write the result** to `.firecrawl/competitor-intel/<slug>-<topic>-<YYYYMMDD>.json` using the Write tool.
8. **Review the staged file** -> Read the output.
9. **Next step:** suggest running the `kb-ingest-review` skill to push approved content into the Marketing Brain KB with source metadata `competitor-crawl`.

## Examples

First, always stage the output directory:

```bash
mkdir -p .firecrawl/competitor-intel
```

Read the schema file with the Read tool, then inline it into the MCP call.

### Pricing extraction with schema (preferred — use firecrawl_extract)

```json
{
  "name": "firecrawl_extract",
  "arguments": {
    "urls": ["https://restaurant365.com/pricing"],
    "prompt": "Extract pricing tiers for Restaurant365 including name, monthly price, user limits, features",
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

Then Write the result to `.firecrawl/competitor-intel/r365-pricing-<YYYYMMDD>.json`.

### Feature list across multiple pages

```json
{
  "name": "firecrawl_extract",
  "arguments": {
    "urls": [
      "https://7shifts.com/features",
      "https://7shifts.com/features/scheduling",
      "https://7shifts.com/features/labor-compliance"
    ],
    "prompt": "Extract the full feature list with categories, descriptions, and target personas",
    "schema": {
      "type": "object",
      "properties": {
        "features": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "category": { "type": "string" },
              "name": { "type": "string" },
              "description": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

### Case studies (map + scrape)

Step 1 — discover case study URLs:

```json
{
  "name": "firecrawl_map",
  "arguments": {
    "url": "https://deputy.com/case-studies",
    "limit": 50
  }
}
```

Step 2 — scrape a selected case study (repeat for each URL):

```json
{
  "name": "firecrawl_scrape",
  "arguments": {
    "url": "https://deputy.com/case-studies/restaurant-brand-a",
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

### Simple pricing page (no schema, cheaper)

```json
{
  "name": "firecrawl_scrape",
  "arguments": {
    "url": "https://wheniwork.com/pricing",
    "formats": ["markdown"],
    "onlyMainContent": true,
    "waitFor": 2000
  }
}
```

### Deep autonomous research (when URLs are unknown)

When you don't know which pages hold the data, use the async agent. Poll `firecrawl_agent_status` until complete.

```json
{
  "name": "firecrawl_agent",
  "arguments": {
    "prompt": "Find Restaurant365's published pricing tiers across their site and pull feature lists for each tier",
    "urls": ["https://restaurant365.com"]
  }
}
```

## MCP Tools Used

| Tool | Source skill | Notes |
|------|--------------|-------|
| `firecrawl_extract` | `../firecrawl-agent` | Schema-driven extraction, fast |
| `firecrawl_agent` + `_status` | `../firecrawl-agent` | Autonomous research, async |
| `firecrawl_scrape` | `../firecrawl-scrape` | Single-page markdown or JSON |
| `firecrawl_map` | `../firecrawl-map` | URL discovery before scrape |

Always stage output under `.firecrawl/competitor-intel/` via the Write tool.

## Output Naming Convention

```
.firecrawl/competitor-intel/<competitor-slug>-<topic>-<YYYYMMDD>.<ext>
```

Examples:
- `.firecrawl/competitor-intel/r365-pricing-20260420.json`
- `.firecrawl/competitor-intel/7shifts-features-20260420.json`
- `.firecrawl/competitor-intel/deputy-casestudy-chainname-20260420.md`

## Cost

Competitor intel runs can burn credits fast on multi-page extractions. Default caps:
- Single scrape: ~1-5 credits
- `firecrawl_extract` with schema: ~5-20 credits per URL
- `firecrawl_agent` run: 100-1000+ credits (autonomous, open-ended)

Check balance at `firecrawl.dev/app` before launching a `firecrawl_agent` job. Prefer `firecrawl_extract` with named URLs whenever possible — it is dramatically cheaper.

## Handoff to KB

After review, tell the user:

> "Competitor intel staged at `.firecrawl/competitor-intel/<file>`. Run the `kb-ingest-review` skill to push approved content to the Marketing Brain KB under `competitive/`."

Never call the Marketing Brain MCP directly from this skill. Ingestion is a separate, user-confirmed step.

## See Also

- `../firecrawl-agent/SKILL.md` — `firecrawl_extract` (schema) and `firecrawl_agent` (autonomous)
- `../firecrawl-scrape/SKILL.md` — single-page scrape (cheaper)
- `../firecrawl-map/SKILL.md` — discover case study index URLs
- `../kb-ingest-review/SKILL.md` — review-and-ingest stage after this skill
- `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md` — canonical competitor list + URLs
- `${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/` — reusable JSON schemas
