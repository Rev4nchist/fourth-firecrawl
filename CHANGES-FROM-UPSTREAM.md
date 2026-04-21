# Changes from Upstream

Fork of https://github.com/firecrawl/firecrawl-claude-plugin at commit-depth=1, cloned 2026-04-20.

This document tracks Fourth's divergence from the upstream plugin so future re-sync decisions are easy.

## Added

### New skills (Fourth task-oriented layer)

| Skill | Purpose |
|-------|---------|
| `skills/competitor-intel/` | Scrape + structure competitor pricing, features, case studies from curated registry |
| `skills/market-scan/` | Sweep hospitality trade press for industry news, trends, signals |
| `skills/content-gap-analysis/` | Identify content angles competitors cover that Fourth doesn't |
| `skills/kb-ingest-review/` | Review `.firecrawl/` staging output, prompt user, ingest to Fourth Marketing Brain KB via MCP |

### New references (bundled content)

| File | Purpose |
|------|---------|
| `references/competitor-registry.md` | R365, HCM point solutions — URLs, known pages (pricing, features, case studies) |
| `references/hospitality-sources.md` | NRN, FSR Magazine, Hotel Management, Skift, etc. — trade press URL catalog |
| `references/fourth-voice-guide.md` | Tone/positioning rules for summarizing scraped content in Fourth voice |
| `references/routing.md` | Decision table: which skill for which task (EBR vs marketing-brain vs general) |
| `references/extraction-schemas/pricing-page.json` | JSON schema for pricing extraction |
| `references/extraction-schemas/case-study.json` | JSON schema for case study extraction |
| `references/extraction-schemas/feature-comparison.json` | JSON schema for feature comparison extraction |
| `references/extraction-schemas/press-release.json` | JSON schema for press release extraction |

### New rules

| File | Purpose |
|------|---------|
| `skills/firecrawl-cli/rules/credit-budget.md` | Cost guardrails — `--max-credits` defaults, approval thresholds |

### New docs

| File | Purpose |
|------|---------|
| `QUICKSTART.md` | Team onboarding guide |
| `NOTICE` | Attribution to upstream under AGPL-3.0 |
| `CHANGES-FROM-UPSTREAM.md` | This file |

## Modified

| File | Change |
|------|--------|
| `.claude-plugin/plugin.json` | Renamed to `fourth-firecrawl`, Fourth author, expanded keywords, expanded skills array to include 4 new skills |
| `.claude-plugin/marketplace.json` | Owner → Fourth AI Enablement Team, plugin name, description, expanded skills array |
| `README.md` | Replaced with Fourth-focused overview; upstream install instructions preserved |

## Preserved (unchanged from upstream)

- `commands/skill-gen.md`
- `skills/firecrawl-cli/SKILL.md` (plus `rules/install.md`, `rules/security.md`)
- `skills/firecrawl-scrape/SKILL.md`
- `skills/firecrawl-search/SKILL.md`
- `skills/firecrawl-map/SKILL.md`
- `skills/firecrawl-crawl/SKILL.md`
- `skills/firecrawl-agent/SKILL.md`
- `skills/firecrawl-instruct/SKILL.md`
- `skills/firecrawl-download/SKILL.md`
- `.gitignore`

## Re-sync strategy

If upstream ships meaningful changes (new CLI subcommands, bug fixes to `firecrawl-cli` skill, security updates):

1. `git remote add upstream https://github.com/firecrawl/firecrawl-claude-plugin.git`
2. `git fetch upstream`
3. Diff upstream `main` against `skills/firecrawl-*/SKILL.md` files (the preserved set)
4. Cherry-pick relevant changes; our custom skills and references stay untouched
5. Update this file with new divergence notes
