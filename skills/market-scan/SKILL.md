---
name: market-scan
description: |
  Sweep Fourth's curated hospitality trade press for industry news, trends, and signals. Feeds both EBR builds (Phase 1.5 benchmarking context) and marketing research. Use this skill when the user says "scan hospitality news for Q1 2026 trends", "what's happening in restaurant labor news", "industry signals on tipping legislation", "what's the trade press saying about AI in restaurants", "market scan for hotel tech", "grab the latest NRN headlines", "what are restaurant operators worrying about this month", or any request for a time-bounded hospitality-industry news sweep. Queries curated sources (NRN, FSR, Skift, Hotel News Now, Nation's Restaurant News, Restaurant Business, AHLA, National Restaurant Association) and summarizes in Fourth voice. Do NOT trigger for general web search (use firecrawl-search), competitor-specific research (use competitor-intel), or customer-specific research (use ebr-research).
allowed-tools:
  - Bash(firecrawl *)
  - Bash(npx firecrawl *)
  - Bash(mkdir *)
  - Bash(date *)
  - Read
  - Write
triggers:
  - scan hospitality news
  - what is happening in restaurant labor news
  - industry signals on [topic]
  - market scan for [segment]
  - trade press sweep on [topic]
  - hospitality trends this quarter
  - restaurant technology news roundup
  - latest hotel tech industry news
  - scan NRN for [topic]
version: 1.0.0
---

# Market Scan

Time-bounded sweep of curated hospitality trade press. Produces a dated markdown brief with source attribution that feeds EBR narratives and marketing positioning.

## Purpose

- Surface industry news, trends, and signals the CSM or marketing team can cite.
- Use curated, high-signal sources — not raw search results.
- Produce a scannable brief in Fourth voice with every claim sourced.

## When to Use

| Trigger | Example |
|---------|---------|
| Time-bounded news sweep | "What hit the hospitality trade press last week?" |
| Topic sweep | "Find industry signals on tipping legislation" |
| Segment context for EBR | "Pressures affecting QSR operators this quarter" |
| Marketing content prep | "What's trending in restaurant tech coverage?" |

**Do NOT use this skill for:**
- Specific vendor intelligence — use `competitor-intel`
- Customer account research — use `ebr-research`
- General web search — use `../firecrawl-search`

## Prerequisites

1. Firecrawl CLI authenticated: `firecrawl --status` (see `../firecrawl-cli/rules/install.md` if not).
2. Source catalog:
   - `${CLAUDE_PLUGIN_ROOT}/references/hospitality-sources.md` — canonical list of NRN, FSR, Skift, Hotel News Now, Restaurant Business, NRA, AHLA, Restaurant Dive, etc.
3. Voice guide (optional but preferred for write-up):
   - `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md`
4. Credit budget awareness — see `${CLAUDE_PLUGIN_ROOT}/skills/firecrawl-cli/rules/credit-budget.md`.

## Workflow

1. **Clarify scope** -> topic + segment + time window (past week? past month? past quarter?).
2. **Pick sources** -> read `references/hospitality-sources.md`, select 3-6 relevant domains.
3. **Stage output directory** -> `mkdir -p .firecrawl/market-scan`.
4. **Run search or map+scrape** -> prefer `firecrawl search` with `--sources news` and `--tbs` time filters.
5. **Write the brief** -> dated markdown file with source attribution table + Fourth-voice summary.
6. **Next step:** suggest `kb-ingest-review` if the sweep has reusable insights for the KB under `messaging/` or `competitive/` folders.

## Examples

### News sweep, past week, general topic

```bash
mkdir -p .firecrawl/market-scan
firecrawl search "restaurant labor legislation 2026" \
  --sources news --tbs qdr:w --limit 15 --scrape \
  -o ".firecrawl/market-scan/labor-legislation-$(date +%Y%m%d).json" \
  --json
```

### Constrained to a specific trade press domain

```bash
firecrawl search "site:nrn.com tipping" \
  --sources news --tbs qdr:m --limit 20 --scrape \
  -o ".firecrawl/market-scan/nrn-tipping-$(date +%Y%m%d).json" \
  --json
```

### Map + scrape for a known trade site's coverage

```bash
# 1. Find recent coverage pages
firecrawl map "https://www.nrn.com" --search "AI in restaurants" --limit 30 \
  --json -o ".firecrawl/market-scan/nrn-ai-urls.json"

# 2. Batch-scrape top results
firecrawl scrape \
  "https://www.nrn.com/technology/article-one" \
  "https://www.nrn.com/technology/article-two" \
  --only-main-content
```

### Parallel sweep across 3 sources

```bash
firecrawl search "ghost kitchens" --sources news --tbs qdr:m --limit 10 \
  -o ".firecrawl/market-scan/ghost-kitchens-news.json" --json &
firecrawl search "hotel labor shortage" --sources news --tbs qdr:m --limit 10 \
  -o ".firecrawl/market-scan/hotel-labor-news.json" --json &
firecrawl search "restaurant tipping" --sources news --tbs qdr:w --limit 10 \
  -o ".firecrawl/market-scan/tipping-news.json" --json &
wait
```

Respect the concurrency limit shown in `firecrawl --status`.

## Time-Window Flags

`--tbs` controls the recency window for `firecrawl search`:

| Flag | Window |
|------|--------|
| `--tbs qdr:h` | Past hour |
| `--tbs qdr:d` | Past day |
| `--tbs qdr:w` | Past week |
| `--tbs qdr:m` | Past month |
| `--tbs qdr:y` | Past year |

Default is unbounded — always pass `--tbs` for market scans so you don't surface stale content.

## Source Filtering

`--sources <web,images,news>` narrows search to news vertical. For hospitality trade press, combine with `site:` operators in the query string when you need to pin one domain (see examples).

## Options Used

| Flag | Source skill | Notes |
|------|--------------|-------|
| `--sources news` | `../firecrawl-search` | News vertical |
| `--tbs <qdr:d\|w\|m>` | `../firecrawl-search` | Time window |
| `--scrape` | `../firecrawl-search` | Grab full page content in-line |
| `--limit <n>` | `../firecrawl-search` | Cap results — mind the budget |
| `--search <q>` | `../firecrawl-map` | Filter URLs when mapping a specific site |
| `--only-main-content` | `../firecrawl-scrape` | Strip nav / chrome |
| `-o, --output <path>` | all | Stage under `.firecrawl/market-scan/` |

## Output Format

Produce a markdown brief at `.firecrawl/market-scan/<topic>-<YYYYMMDD>.md` with this structure:

```markdown
# Market Scan: <topic>
**Window:** <past week | past month | custom>
**Sources:** NRN, FSR, Skift, Hotel News Now, ...
**Date:** <YYYY-MM-DD>

## Executive Summary
<3-5 sentences in Fourth voice — direct, operator-focused, no fluff>

## Key Signals
| Signal | Source | Confidence |
|--------|--------|-----------|
| <headline> | <outlet + URL> | VERIFIED / REPORTED |

## Implications for Fourth
- <Positioning angle>
- <EBR talking point>

## Gaps
<What was thin / what the user should fill>
```

Voice: use `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md` — concise, operator-first, no hype. Every claim must cite a source URL.

## Cost

News sweeps with `--scrape` on 15 results can approach ~150-300 credits. See `${CLAUDE_PLUGIN_ROOT}/skills/firecrawl-cli/rules/credit-budget.md`. Default guardrails: limit `--limit 10-20` for daily scans, cap `--limit 30` for monthly deep dives, always use `--tbs` to scope.

## See Also

- `../firecrawl-search` — underlying search engine with `--tbs` and `--sources`
- `../firecrawl-map` — alternative when targeting a single known domain
- `../firecrawl-scrape` — fetch individual articles after finding them
- `../firecrawl-cli/rules/credit-budget.md` — cost guardrails
- `../kb-ingest-review` — push approved signals to Marketing Brain KB
- `${CLAUDE_PLUGIN_ROOT}/references/hospitality-sources.md` — curated source list
- `${CLAUDE_PLUGIN_ROOT}/references/fourth-voice-guide.md` — voice/tone reference
