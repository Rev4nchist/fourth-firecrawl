---
name: content-gap-analysis
description: |
  Identify content angles competitors are covering that Fourth's Marketing Brain KB is not. Produces a three-way comparison (competitor content topics vs. Fourth KB coverage vs. proposed new angles) that feeds the content roadmap. Use this skill when the user says "what content are competitors publishing that we're not", "find content gaps vs R365", "topic coverage analysis", "where's our blog thin compared to 7shifts", "content gap report for Deputy", "what are competitors writing about that we should", or "compare our KB to competitor resources". Do NOT trigger for simple competitor page scraping (use competitor-intel), one-off KB searches (use the fourth-marketing-brain MCP directly), or general market research (use market-scan).
allowed-tools:
  - Bash(firecrawl *)
  - Bash(npx firecrawl *)
  - Bash(mkdir *)
  - Bash(date *)
  - Read
  - Write
triggers:
  - what content are competitors publishing that we are not
  - find content gaps vs [competitor]
  - topic coverage analysis
  - content gap report for [competitor]
  - where is our blog thin compared to [competitor]
  - compare our KB to competitor resources
  - content roadmap opportunities
  - find topics competitors cover better
version: 1.0.0
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

1. Firecrawl CLI authenticated: `firecrawl --status`.
2. Competitor registry for blog/resource URLs:
   - `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md`
3. Fourth Marketing Brain MCP access — ideally the `fourth-marketing-brain` MCP is registered with `search_documents` available. If not registered in the current session, the skill will prompt the user to run KB searches manually.
4. Credit budget awareness — see `${CLAUDE_PLUGIN_ROOT}/skills/firecrawl-cli/rules/credit-budget.md`.

## Workflow

1. **Scope** -> identify the competitor(s) and topic domain (scheduling, labor forecasting, tip pooling, HR, etc.).
2. **Enumerate competitor content** -> `firecrawl map` on their blog / resources root, then `firecrawl scrape` titles + summaries for top N.
3. **Query Fourth KB** -> use `mcp__fourth-marketing-brain__search_documents` (if available) with the same topic terms.
4. **Compute the delta** -> topics the competitor covers that Fourth does not.
5. **Propose angles** -> for each gap, write a Fourth-voice angle that differentiates instead of imitating.
6. **Stage output** -> `.firecrawl/content-gaps/<competitor>-gaps-<YYYYMMDD>.md`.
7. **Next step:** suggest `kb-ingest-review` if any scraped competitor content should land in the KB under `competitive/` as reference material.

## Examples

### Step 1: Map competitor blog/resources

```bash
mkdir -p .firecrawl/content-gaps
firecrawl map "https://restaurant365.com/blog" --limit 200 --json \
  -o ".firecrawl/content-gaps/r365-blog-urls.json"

firecrawl map "https://restaurant365.com/resources" --limit 100 --json \
  -o ".firecrawl/content-gaps/r365-resources-urls.json"
```

### Step 2: Batch-scrape titles and metadata

```bash
# Scrape a curated set of top post URLs — pull from the map output
firecrawl scrape \
  "https://restaurant365.com/blog/labor-forecasting" \
  "https://restaurant365.com/blog/food-cost-control" \
  "https://restaurant365.com/blog/restaurant-scheduling" \
  --only-main-content
```

### Step 3: Cluster titles with firecrawl agent

```bash
firecrawl agent "cluster these blog post URLs by topic and return a topic taxonomy with counts" \
  --urls "https://restaurant365.com/blog" \
  --wait --max-credits 1000 \
  -o ".firecrawl/content-gaps/r365-topic-taxonomy-$(date +%Y%m%d).json"
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

## Options Used

| Flag | Source skill | Notes |
|------|--------------|-------|
| `--limit <n>` | `../firecrawl-map` | Cap URLs returned (stay under budget) |
| `--search <q>` | `../firecrawl-map` | Pre-filter by topic keyword |
| `--json` | `../firecrawl-map`, `../firecrawl-search` | Needed for jq extraction of URLs |
| `--only-main-content` | `../firecrawl-scrape` | Cleaner titles + intros |
| `--urls <urls>` | `../firecrawl-agent` | Seed agent with blog roots |
| `--max-credits <n>` | `../firecrawl-agent` | Required — gap analysis can runaway |
| `--wait` | `../firecrawl-agent` | Block for inline results |
| `-o, --output <path>` | all | Stage under `.firecrawl/content-gaps/` |

## Output Naming

```
.firecrawl/content-gaps/<competitor-slug>-gaps-<YYYYMMDD>.md
.firecrawl/content-gaps/<competitor-slug>-blog-urls.json
.firecrawl/content-gaps/<competitor-slug>-topic-taxonomy-<YYYYMMDD>.json
```

## Cost

Gap analysis is the most expensive skill in this plugin because it combines `map` (cheap), bulk `scrape` (moderate), and `agent` (expensive). Typical run: 800-2000 credits per competitor. Always cap `--max-credits` on agent calls. See `${CLAUDE_PLUGIN_ROOT}/skills/firecrawl-cli/rules/credit-budget.md` for budget guidance.

## Three-Way Comparison Notes

The value of this skill is the three-way compare:
1. **Competitor coverage** (what they publish)
2. **Fourth KB coverage** (what we already have)
3. **Gap + differentiated angle** (what we should write — not a copy of theirs)

Never propose angles that are mirror-images of competitor posts. Fourth's voice is operator-first and evidence-based — see `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md`.

## See Also

- `../firecrawl-map` — enumerate competitor content URLs
- `../firecrawl-scrape` — grab titles and summaries
- `../firecrawl-agent` — cluster by topic with AI
- `../competitor-intel` — run before this for structured competitor data
- `../market-scan` — complementary industry context
- `../kb-ingest-review` — push competitor reference material to KB
- `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md` — blog / resources URLs
- `../firecrawl-cli/rules/credit-budget.md` — cost guardrails
