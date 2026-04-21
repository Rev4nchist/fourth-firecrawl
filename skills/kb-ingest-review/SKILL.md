---
name: kb-ingest-review
description: |
  Review-and-ingest stage for Firecrawl staging files. Takes content from `.firecrawl/` subdirectories (competitor-intel, market-scan, content-gaps, etc.) and pushes user-approved files to the Fourth Marketing Brain KB with proper metadata. NEVER auto-ingests — always requires per-document user confirmation. Use this skill when the user says "ingest competitor intel to KB", "review firecrawl staging", "push this research to marketing brain", "ingest the R365 pricing data", "review and ingest today's market scan", "publish firecrawl output to KB", "what's in the firecrawl staging area", or "move staged content to the knowledge base". Do NOT trigger for creating new research (use competitor-intel, market-scan, content-gap-analysis, or ebr-research first), direct KB queries (use fourth-marketing-brain MCP directly), or anything outside the `.firecrawl/` staging tree.
allowed-tools:
  - Bash(mkdir *)
  - Bash(mv *)
  - Bash(ls *)
  - Bash(date *)
  - Read
  - Write
---

# KB Ingest Review

Manual review-and-ingest gate between Firecrawl staging output and the Fourth Marketing Brain KB. Ensures every KB document has proper folder, title, source, and confidence metadata — and that a human approved each ingest.

## Purpose

- Keep staged research auditable by default (in `.firecrawl/`).
- Require explicit user confirmation before any write to the Marketing Brain KB.
- Attach consistent metadata (source, confidence, folder) per Fourth KB conventions.
- Preserve an audit trail of what was ingested and when.

## When to Use

| Trigger | Example |
|---------|---------|
| User has staged research to ingest | "Push today's R365 pricing to the KB" |
| Staging review | "What's in `.firecrawl/` waiting to go to KB?" |
| Post-skill handoff | After `competitor-intel`, `market-scan`, or `content-gap-analysis` completes |

**Do NOT use this skill for:**
- Creating new research — run the source skill first (`competitor-intel`, `market-scan`, `content-gap-analysis`, or upstream scrape/search/map).
- Direct KB queries / document reads — use the `fourth-marketing-brain` MCP directly.
- Bulk auto-ingest — this skill enforces per-document confirmation.

## Prerequisites

1. Staged files exist under `.firecrawl/` (typically in subdirectories from other skills).
2. `fourth-marketing-brain` MCP is registered with `create_document` and `append_to_document` tools available. If not registered in the current session, see the **Graceful Fallback** section below.
3. Understanding of the KB folder taxonomy — see the Target Folders table.

## Target Folders (Fourth Marketing Brain KB)

| Folder | Use for |
|--------|---------|
| `competitive/` | Competitor pricing, features, case studies, positioning |
| `messaging/` | Fourth voice / positioning statements, voice exemplars |
| `solutions/` | Product solution narratives, feature deep-dives |
| `rfp-responses/` | Canonical RFP answer language |
| `compliance/` | Labor law, tipping, wage, scheduling compliance reference |
| `integrations/` | Partner / integration reference content |

## Source Metadata Values

Use these exact values for the `source` field:

| Value | Use when |
|-------|----------|
| `competitor-crawl` | Scraped directly from competitor property |
| `web-research` | Trade press, industry reports, market scans |
| `sales-call` | Notes or quotes from customer-facing calls |
| `rfp-ingestion` | Material extracted from an RFP document |
| `manual` | Direct author input, not scraped |

## Confidence Levels

| Level | Meaning |
|-------|---------|
| `HIGH` | Sourced from the vendor's own property (pricing page, case study) or verified primary source |
| `PARTIAL` | Reported in trade press but not confirmed by the subject |
| `LOW` | Inferred, secondhand, or needs verification before customer use |

## Workflow

1. **Enumerate staged files** -> `ls -la .firecrawl/**/*` and list candidates.
2. **Per-file review loop** — for each file:
   a. Show the user a preview (first N lines of the file).
   b. Ask the four metadata questions (see below).
   c. Read user confirmation before any MCP call.
   d. Call `create_document` or `append_to_document` via the `fourth-marketing-brain` MCP.
   e. On success, move the staging file into `.firecrawl/ingested/<YYYY-MM-DD>/` as audit trail.
3. **Summary** -> report count ingested vs skipped, plus the audit trail location.

## The Four Metadata Questions

For each file, prompt the user exactly once with:

1. **Folder** — which KB folder does this belong in? (`competitive` / `messaging` / `solutions` / `rfp-responses` / `compliance` / `integrations`)
2. **Source** — which source value? (`competitor-crawl` / `web-research` / `sales-call` / `rfp-ingestion` / `manual`)
3. **Confidence** — `HIGH` / `PARTIAL` / `LOW`
4. **Title** — what should the KB doc be called? Suggest one based on filename + content, but let the user override.

Also ask: **Create or append?** If a doc with that title already exists in the target folder, ask whether to `create_document` (new doc) or `append_to_document` (extend existing).

## Examples

### List what's waiting to ingest

```bash
ls -la .firecrawl/competitor-intel/ \
       .firecrawl/market-scan/ \
       .firecrawl/content-gaps/ 2>/dev/null
```

### Preview a staged file before ingest

```bash
# Show the first 80 lines of the staged file for the user to review
head -80 .firecrawl/competitor-intel/r365-pricing-20260420.json
```

### Typical ingest flow (MCP available)

After user confirms metadata, the skill calls the MCP tool. Pseudocode — the actual call is an MCP tool invocation, not a bash command:

```
mcp__fourth-marketing-brain__create_document(
  folder="competitive",
  title="Restaurant365 Pricing Tiers (April 2026)",
  content=<file contents>,
  source="competitor-crawl",
  confidence="HIGH"
)
```

Or when extending an existing doc:

```
mcp__fourth-marketing-brain__append_to_document(
  folder="competitive",
  title="Restaurant365 Pricing Tiers (April 2026)",
  content=<new content block>
)
```

### Move ingested file to audit trail

```bash
mkdir -p ".firecrawl/ingested/$(date +%Y-%m-%d)"
mv ".firecrawl/competitor-intel/r365-pricing-20260420.json" \
   ".firecrawl/ingested/$(date +%Y-%m-%d)/"
```

## Graceful Fallback (MCP not registered)

If `mcp__fourth-marketing-brain__create_document` or `append_to_document` are not available in the current session:

1. Do NOT attempt to call them (the call will fail).
2. Produce an ingest plan file instead: `.firecrawl/ingest-plan-<YYYYMMDD>.md`
3. The plan should contain, per file:
   - Source staging path
   - Proposed folder, title, source, confidence
   - The file contents (or a reference) ready for manual ingest
4. Tell the user:

> "The `fourth-marketing-brain` MCP is not registered in this session. I've written an ingest plan to `.firecrawl/ingest-plan-<date>.md`. You can either:
> - Register the MCP and re-run this skill, or
> - Ingest manually via the Marketing Brain UI using the metadata in the plan."

Do not move files to `.firecrawl/ingested/` on fallback — they have not actually been ingested.

## Safety Rules

- **Never auto-ingest.** Every document requires an explicit user "yes" before the MCP call.
- **Never skip metadata.** All four fields (folder, title, source, confidence) must be set.
- **Never guess confidence.** Ask the user — or default to `PARTIAL` if unsure and flag it.
- **Never delete staging files.** Move them to `.firecrawl/ingested/<date>/` after successful ingest; never `rm`.
- **Never ingest without a preview.** User must see what's about to land in the KB.
- **Stop on MCP error.** If `create_document` or `append_to_document` returns an error, stop the loop, report the error, do not move the file.

## Audit Trail Layout

```
.firecrawl/ingested/
  2026-04-20/
    r365-pricing-20260420.json
    7shifts-features-20260420.json
  2026-04-21/
    labor-legislation-20260421.json
```

This directory is the source of truth for "what did we push to the KB and when".

## Cost

This skill does not call Firecrawl — no credits consumed. The cost is entirely MCP calls to `fourth-marketing-brain`, which should be metered on the KB side, not the Firecrawl side. Upstream skills (`competitor-intel`, `market-scan`, `content-gap-analysis`) feed this one and consume Firecrawl credits; see each for its own cost notes.

## See Also

- `../competitor-intel` — produces staging in `.firecrawl/competitor-intel/`
- `../market-scan` — produces staging in `.firecrawl/market-scan/`
- `../content-gap-analysis` — produces staging in `.firecrawl/content-gaps/`
- `../firecrawl-scrape/SKILL.md`, `../firecrawl-search/SKILL.md`, `../firecrawl-map/SKILL.md`, `../firecrawl-crawl/SKILL.md`, `../firecrawl-agent/SKILL.md` — upstream Firecrawl primitives whose output can also feed this review stage
