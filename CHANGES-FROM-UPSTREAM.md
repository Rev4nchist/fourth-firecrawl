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

---

## v1.1.0 — MCP pivot (2026-04-21)

### Why

Cowork sandbox blocks `npm install -g` and arbitrary HTTPS from bash. The v1.0 CLI-based auth model was dead in Cowork. Pivoted to the hosted Firecrawl MCP at https://mcp.firecrawl.dev/v2/mcp with per-user Bearer auth.

### Deleted

- `skills/firecrawl-cli/` (entire directory — CLI umbrella skill plus `rules/install.md`, `rules/security.md`, `rules/credit-budget.md`)
- `skills/firecrawl-download/` (CLI-only; no MCP equivalent)

### Renamed

- `skills/firecrawl-instruct/` → `skills/firecrawl-interact/` (matches MCP tool naming: `firecrawl_interact`)

### Added

- `.mcp.json` at plugin root (Firecrawl MCP connector declaration — `type: http`, hosted URL, `${FIRECRAWL_API_KEY}` env interpolation)
- `PROJECT-DESCRIPTION.md` and `PROJECT-INSTRUCTIONS.md` (Cowork and Claude.ai project config)
- `references/credit-budget.md` (relocated from `skills/firecrawl-cli/rules/credit-budget.md`, rewritten for MCP context)
- `references/firecrawl-mcp-spec.md` (implementation reference: tool parameters, auth patterns, Cowork integration notes)
- `docs/env-aware-setup-design.md` (design doc for the env-var-aware setup flow)

### Rewritten

- All 6 upstream primitive skills (`firecrawl-scrape`, `firecrawl-search`, `firecrawl-map`, `firecrawl-crawl`, `firecrawl-agent`, `firecrawl-interact`) now use MCP tool calls (`mcp__firecrawl__firecrawl_*`) instead of CLI bash commands
- 4 Fourth-custom skills (`competitor-intel`, `market-scan`, `content-gap-analysis`, `kb-ingest-review`) now reference MCP tool names in examples
- `commands/setup.md`: CLI install flow → MCP connector flow (check for `mcp__firecrawl__*` tools, configure Cowork connector or shell env var, test scrape via MCP)
- `README.md`: CLI paths removed; MCP setup + per-user key guidance added; plugin structure tree updated
- `QUICKSTART.md`: CLI paths replaced with MCP paths; `firecrawl --status` removed; credit balance guidance updated to dashboard-only
- `references/routing.md`: fail-stop rule re-keyed on MCP tool availability (not `firecrawl --status`); routing table updated with MCP tool names

### Re-sync strategy (updated)

Upstream firecrawl-claude-plugin is still CLI-based. We are now deeply diverged — sync from upstream is unlikely to be useful. Track [firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) for new MCP tool additions or parameter changes instead.
