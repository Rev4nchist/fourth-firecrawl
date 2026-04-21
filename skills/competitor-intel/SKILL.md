---
name: competitor-intel
description: |
  Scrape and structure competitor intelligence (pricing, features, case studies, customer logos) from Fourth's curated competitor registry. Uses pre-built JSON extraction schemas to produce comparable, structured output across vendors. Use this skill when the user says "research R365 pricing", "get competitor intel on 7shifts", "pull Deputy features", "compare HCM competitors", "what's Paycom charging", "scrape competitor pricing pages", or names any competitor in Fourth's registry (Restaurant365, 7shifts, Deputy, HotSchedules, When I Work, Paycom, UKG, Toast, Paylocity). Output is staged in `.firecrawl/competitor-intel/` for review before ingestion to the Marketing Brain KB. Do NOT trigger for general web search, customer research (use ebr-research for that), or one-off URL scraping (use firecrawl-scrape).
allowed-tools:
  - Bash(firecrawl *)
  - Bash(npx firecrawl *)
  - Bash(mkdir *)
  - Bash(date *)
  - Read
  - Write
triggers:
  - research [competitor] pricing
  - get competitor intel on [vendor]
  - scrape [competitor] features
  - compare HCM competitors
  - competitive analysis on R365
  - what is 7shifts charging
  - pull Deputy case studies
  - Paycom vs Fourth pricing
  - refresh competitor pricing data
version: 1.0.0
---

# Competitor Intel

Targeted, schema-driven competitor research. Produces structured, comparable intel that drops cleanly into Fourth's Marketing Brain KB under the `competitive/` folder.

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

1. Firecrawl CLI authenticated: `firecrawl --status` (see `../firecrawl-cli/rules/install.md` if not).
2. Read the competitor registry to resolve name -> URLs:
   - `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md`
3. Pick the extraction schema that matches your intent:
   - `${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/` (pricing-page.json, feature-list.json, case-study.json, etc.)
4. Confirm the request will respect the credit budget — see `${CLAUDE_PLUGIN_ROOT}/skills/firecrawl-cli/rules/credit-budget.md`.

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
2. **Pick schema** -> match intent to a schema file under `references/extraction-schemas/`.
3. **Stage output directory** -> `mkdir -p .firecrawl/competitor-intel`.
4. **Run `firecrawl agent` with schema** (or `firecrawl scrape` for simple pages) with `--max-credits` budget.
5. **Review the staged file** -> `head`, `jq`, or Read the output.
6. **Next step:** suggest running the `kb-ingest-review` skill to push approved content into the Marketing Brain KB with source metadata `competitor-crawl`.

## Examples

### Pricing extraction with schema

```bash
mkdir -p .firecrawl/competitor-intel
firecrawl agent "extract pricing tiers for Restaurant365" \
  --urls "https://restaurant365.com/pricing" \
  --schema-file "${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/pricing-page.json" \
  --wait --max-credits 500 \
  -o ".firecrawl/competitor-intel/r365-pricing-$(date +%Y%m%d).json"
```

### Feature list across multiple pages

```bash
firecrawl agent "extract the full feature list with categories" \
  --urls "https://7shifts.com/features" \
  --schema-file "${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/feature-list.json" \
  --wait --max-credits 750 \
  -o ".firecrawl/competitor-intel/7shifts-features-$(date +%Y%m%d).json"
```

### Case studies (map + scrape)

```bash
# Find the case study index pages first
firecrawl map "https://deputy.com/case-studies" --limit 50 --json \
  -o ".firecrawl/competitor-intel/deputy-case-study-urls.json"

# Then batch-scrape concurrently
firecrawl scrape \
  "https://deputy.com/case-studies/restaurant-brand-a" \
  "https://deputy.com/case-studies/restaurant-brand-b" \
  --only-main-content
```

### Simple pricing page (no AI, cheaper)

```bash
firecrawl scrape "https://wheniwork.com/pricing" \
  --only-main-content --wait-for 2000 \
  -o ".firecrawl/competitor-intel/wiw-pricing-$(date +%Y%m%d).md"
```

## Options Used

| Flag | Source skill | Notes |
|------|--------------|-------|
| `--urls <urls>` | `../firecrawl-agent` | Starting URLs for agent run |
| `--schema-file <path>` | `../firecrawl-agent` | Path to JSON schema |
| `--max-credits <n>` | `../firecrawl-agent` | Cap per-run credit spend |
| `--wait` | `../firecrawl-agent`, `../firecrawl-crawl` | Block until complete |
| `--only-main-content` | `../firecrawl-scrape` | Strip chrome / nav |
| `--wait-for <ms>` | `../firecrawl-scrape` | Wait for JS-rendered content |
| `-o, --output <path>` | all | Always stage under `.firecrawl/competitor-intel/` |

## Output Naming Convention

```
.firecrawl/competitor-intel/<competitor-slug>-<topic>-<YYYYMMDD>.<ext>
```

Examples:
- `.firecrawl/competitor-intel/r365-pricing-20260420.json`
- `.firecrawl/competitor-intel/7shifts-features-20260420.json`
- `.firecrawl/competitor-intel/deputy-casestudy-chainname-20260420.md`

## Cost

Competitor intel runs can burn credits fast on multi-page extractions. Always pass `--max-credits`. Budget guidance and per-command cost table: `${CLAUDE_PLUGIN_ROOT}/skills/firecrawl-cli/rules/credit-budget.md`. If that rule file is missing, default caps: 500 credits per simple page, 1000 per agent run across <= 5 pages.

## Handoff to KB

After review, tell the user:

> "Competitor intel staged at `.firecrawl/competitor-intel/<file>`. Run the `kb-ingest-review` skill to push approved content to the Marketing Brain KB under `competitive/`."

Never call the Marketing Brain MCP directly from this skill. Ingestion is a separate, user-confirmed step.

## See Also

- `../firecrawl-agent` — AI extraction engine used with schemas
- `../firecrawl-scrape` — simpler single-page extraction (cheaper)
- `../firecrawl-map` — discover case study index URLs
- `../firecrawl-cli/rules/credit-budget.md` — cost guardrails
- `../kb-ingest-review` — review-and-ingest stage after this skill
- `${CLAUDE_PLUGIN_ROOT}/references/competitor-registry.md` — canonical competitor list + URLs
- `${CLAUDE_PLUGIN_ROOT}/references/extraction-schemas/` — reusable JSON schemas
