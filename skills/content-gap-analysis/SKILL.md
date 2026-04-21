---
name: content-gap-analysis
description: |
  Identify content angles competitors are covering that Fourth's Marketing Brain KB is not. Produces a three-way comparison (competitor content topics vs. Fourth KB coverage vs. proposed new angles) that feeds the content roadmap. Use when users request content-gap analysis — phrases like "what content are competitors publishing that we're not", "find content gaps vs R365", "topic coverage analysis", "where's our blog thin compared to 7shifts", "content gap report for Deputy", "what are competitors writing about that we should", "compare our KB to competitor resources", "content roadmap opportunities", or "find topics competitors cover better". Do NOT trigger for simple competitor page scraping (use competitor-intel), one-off KB searches (use the fourth-marketing-brain MCP directly), or general market research (use market-scan).
allowed-tools:
  - mcp__firecrawl__firecrawl_map
  - mcp__firecrawl__firecrawl_scrape
  - mcp__firecrawl__firecrawl_extract
  - mcp__firecrawl__firecrawl_agent
  - mcp__firecrawl__firecrawl_agent_status
  - Bash(mkdir *)
  - Bash(date *)
  - Read
  - Write
---

# Content Gap Analysis

Three-way comparison that surfaces content angles Fourth should publish. Competitor content is scraped, Fourth's KB is queried, and the delta is written up as a gap report with proposed angles.

## Purpose

- Enumerate what competitors are publishing on their blogs, resource hubs, and learning centers.
- Cross-reference with Fourth's Marketing Brain KB to identify coverage gaps.
- Propose Fourth-voice angles for topics where we have no comparable content.

## When to Use

| Trigger | Example |
|---------|---------|
| Head-to-head gap ask | "Find content gaps vs R365" |
| Roadmap planning | "What should we publish next quarter?" |
| Competitive content audit | "Topic coverage analysis across HCM competitors" |
| Fourth KB gap detection | "Where's our KB thin on scheduling content?" |

**Do NOT use this skill for:**
- Simple competitor page scraping — use `competitor-intel`
- One-off KB searches — use the `fourth-marketing-brain` MCP's `search_documents` directly
- General trade press research — use `market-scan`

## Prerequisites

1. Firecrawl MCP must be connected — if `mcp__firecrawl__firecrawl_map` (or any firecrawl tool) is not in the available toolset, run `/fourth-firecrawl:setup` to wire it up. Do not fall back to WebFetch or WebSearch.
2. Competitor registry for blog/resource URLs:
   - `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md`
3. Fourth Marketing Brain MCP access — ideally the `fourth-marketing-brain` MCP is registered with `search_documents` available. If not registered in the current session, the skill will prompt the user to run KB searches manually.
4. Credit budget awareness — see Cost section below.

## Workflow

1. **Scope** -> identify the competitor(s) and topic domain (scheduling, labor forecasting, tip pooling, HR, etc.).
2. **Enumerate competitor content** -> `mcp__firecrawl__firecrawl_map` on their blog / resources root, then `mcp__firecrawl__firecrawl_scrape` titles + summaries for top N.
3. **Query Fourth KB** -> use `mcp__fourth-marketing-brain__search_documents` (if available) with the same topic terms.
4. **Compute the delta** -> topics the competitor covers that Fourth does not.
5. **Propose angles** -> for each gap, write a Fourth-voice angle that differentiates instead of imitating.
6. **Stage output** -> `.firecrawl/content-gaps/<competitor>-gaps-<YYYYMMDD>.md`.
7. **Next step:** suggest `kb-ingest-review` if any scraped competitor content should land in the KB under `competitive/` as reference material.

## Examples

First, stage the output directory:

```bash
mkdir -p .firecrawl/content-gaps
```

### Step 1: Map competitor blog/resources

```json
{
  "name": "mcp__firecrawl__firecrawl_map",
  "arguments": {
    "url": "https://restaurant365.com/blog",
    "limit": 200
  }
}
```

```json
{
  "name": "mcp__firecrawl__firecrawl_map",
  "arguments": {
    "url": "https://restaurant365.com/resources",
    "limit": 100
  }
}
```

Write each response to `.firecrawl/content-gaps/r365-blog-urls.json` and `...resources-urls.json`.

### Step 2: Scrape titles and metadata (repeat for each URL)

```json
{
  "name": "mcp__firecrawl__firecrawl_scrape",
  "arguments": {
    "url": "https://restaurant365.com/blog/labor-forecasting",
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

### Step 3: Cluster titles with firecrawl_extract (cheaper than agent)

When you have the URL list from Step 1, use `firecrawl_extract` with a taxonomy schema across all URLs:

```json
{
  "name": "mcp__firecrawl__firecrawl_extract",
  "arguments": {
    "urls": [
      "https://restaurant365.com/blog/labor-forecasting",
      "https://restaurant365.com/blog/food-cost-control",
      "https://restaurant365.com/blog/restaurant-scheduling"
    ],
    "prompt": "Return topic, category, and 3-sentence summary for each post",
    "schema": {
      "type": "object",
      "properties": {
        "posts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "url": { "type": "string" },
              "topic": { "type": "string" },
              "category": { "type": "string" },
              "summary": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

Alternative: open-ended cluster with the autonomous agent (slower, more expensive — poll `firecrawl_agent_status`):

```json
{
  "name": "mcp__firecrawl__firecrawl_agent",
  "arguments": {
    "prompt": "Cluster the blog posts at this site by topic and return a topic taxonomy with post counts per topic",
    "urls": ["https://restaurant365.com/blog"]
  }
}
```

### Step 4: Query the Fourth KB (if MCP is registered)

Call `mcp__fourth-marketing-brain__search_documents` with topic terms derived from the taxonomy. Example terms to try:
- "labor forecasting"
- "food cost control"
- "restaurant scheduling automation"
- "tip pooling compliance"

If the MCP is not registered in this session, prompt the user:

> "The `fourth-marketing-brain` MCP is not available in this session. Run these searches manually in the Marketing Brain UI and paste the coverage summary back to me:
> - labor forecasting
> - food cost control
> - restaurant scheduling automation
> ..."

### Step 5: Produce the gap report

Output `.firecrawl/content-gaps/<competitor>-gaps-<YYYYMMDD>.md`:

```markdown
# Content Gap Analysis: Fourth vs <Competitor>
**Date:** <YYYY-MM-DD>
**Competitor:** <name>
**KB scope checked:** <topics queried>

## Topic Coverage Matrix
| Topic | <Competitor> posts | Fourth KB docs | Gap? |
|-------|-------------------|----------------|------|
| Labor forecasting | 12 | 3 | Partial |
| Tip pooling compliance | 8 | 0 | YES |
| Food cost control | 15 | 7 | No |

## Gaps Identified
### <Topic 1 — GAP>
- **<Competitor> coverage:** <summary, URL>
- **Why it matters:** <operator pain point>
- **Proposed Fourth angle:** <differentiated take, not imitation>

### <Topic 2 — PARTIAL>
- **<Competitor> coverage:** <summary, URL>
- **Fourth existing:** <KB doc title + folder>
- **Proposed refresh angle:** <what to add>

## Recommended Publishing Priorities
1. <Highest-leverage gap>
2. <Second priority>
3. <Third priority>

## Sources
<List of competitor URLs scraped>
```

## MCP Tools Used

| Tool | Source skill | Notes |
|------|--------------|-------|
| `mcp__firecrawl__firecrawl_map` | `../firecrawl-map` | Enumerate competitor content URLs |
| `mcp__firecrawl__firecrawl_scrape` | `../firecrawl-scrape` | Grab titles and summaries |
| `mcp__firecrawl__firecrawl_extract` | `../firecrawl-agent` | Schema-driven clustering (preferred) |
| `mcp__firecrawl__firecrawl_agent` + `_status` | `../firecrawl-agent` | Autonomous clustering (fallback) |

Stage all output under `.firecrawl/content-gaps/` via the Write tool.

## Output Naming

```
.firecrawl/content-gaps/<competitor-slug>-gaps-<YYYYMMDD>.md
.firecrawl/content-gaps/<competitor-slug>-blog-urls.json
.firecrawl/content-gaps/<competitor-slug>-topic-taxonomy-<YYYYMMDD>.json
```

## Cost

Gap analysis is the most expensive skill in this plugin because it combines `firecrawl_map` (cheap, ~1 credit), bulk `firecrawl_scrape` (moderate, ~1-5 credits per page), and `firecrawl_extract` or `firecrawl_agent` (expensive, 5-1000+ credits). Typical run: 800-2000 credits per competitor. Prefer `firecrawl_extract` with a named URL list over `firecrawl_agent` for open-ended clustering — dramatically cheaper. Check balance at `firecrawl.dev/app` before starting.

## Three-Way Comparison Notes

The value of this skill is the three-way compare:
1. **Competitor coverage** (what they publish)
2. **Fourth KB coverage** (what we already have)
3. **Gap + differentiated angle** (what we should write — not a copy of theirs)

Never propose angles that are mirror-images of competitor posts. Fourth's voice is operator-first and evidence-based — see `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md`.

## See Also

- `../firecrawl-map/SKILL.md` — enumerate competitor content URLs
- `../firecrawl-scrape/SKILL.md` — grab titles and summaries
- `../firecrawl-agent/SKILL.md` — `firecrawl_extract` (schema) and `firecrawl_agent` (autonomous)
- `../competitor-intel/SKILL.md` — run before this for structured competitor data
- `../market-scan/SKILL.md` — complementary industry context
- `../kb-ingest-review/SKILL.md` — push competitor reference material to KB
- `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md` — blog / resources URLs
