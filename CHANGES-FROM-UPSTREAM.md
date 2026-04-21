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

---

## v1.2.0 — Reliability fixes from Donna's v1.1.0 Cowork test report (2026-04-21)

### Why

Donna's end-to-end test of v1.1.0 in Cowork (2026-04-21) surfaced four reliability issues that either broke live execution, wasted credits, or produced hallucinated output. This release fixes all four. Priority on reliability and accuracy, not credit efficiency. Source findings: P1, P2, P5, P6 from the test report.

### Deleted

- `.mcp.json` at plugin root — **P1 fix**. The plugin-bundled connector declaration was racing with the Cowork-registered Firecrawl connector, surfacing two Firecrawl connectors in the same session (one persistent `mcp__<uuid>__*`, one plugin-bundled `mcp__plugin_fourth-firecrawl_firecrawl__*` that cycled on and off). v1.2 now expects the Firecrawl connector to be registered at the Cowork workspace level only — no bundled MCP declaration.

### Modified

#### Skills — namespace portability (P2 fix)

All 9 firecrawl-using skills (`competitor-intel`, `market-scan`, `content-gap-analysis`, `firecrawl-scrape`, `firecrawl-search`, `firecrawl-map`, `firecrawl-crawl`, `firecrawl-agent`, `firecrawl-interact`):

- **Body/examples**: replaced hard-coded `mcp__firecrawl__firecrawl_scrape` (and all 9 other tool variants) with the bare tool names (`firecrawl_scrape`, `firecrawl_search`, `firecrawl_map`, `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_extract`, `firecrawl_agent`, `firecrawl_agent_status`, `firecrawl_interact`, `firecrawl_interact_stop`). The v1.1 hard-coded prefix failed literal execution in Cowork, where the live tool namespace is UUID-prefixed (e.g. `mcp__68cba2b7-…__firecrawl_scrape`) or connector-named.
- **Frontmatter `allowed-tools`**: kept the `mcp__firecrawl__*` pattern — Claude's tool allowlist system uses glob matching so this is still safe as a declarative allow pattern.
- **New note near the top of each skill**: explicit callout that the runtime namespace may be prefixed, and Claude will match the registered tool by intent.

`kb-ingest-review` is unchanged — it does not call Firecrawl tools.

#### `references/competitor-registry.md` — `public_pricing` flag (P6 fix)

Added a `public_pricing: true|false` field to each of the 11 competitor entries:

- `false` (pricing is gated / quote-only): **Restaurant365, Toast, Push Operations, Paycom, UKG, Paylocity, ADP** (7 competitors)
- `true` (real dollar amounts on the pricing page): **7shifts, Deputy, When I Work, Homebase** (4 competitors)

Added an explanation section at the top of the registry describing the flag's intent — skills should skip automated pricing extraction on `public_pricing: false` vendors and reference captured Fourth sales data in the Marketing Brain KB instead. Root cause: v1.1 ran `firecrawl_extract` on R365's gated pricing page, returning empty arrays and burning ~25 credits per run.

#### `skills/competitor-intel/SKILL.md` — preflight + hallucination filter (P5 + P6 fix)

Two new workflow steps:

- **Step 2 (new)**: Before a pricing extract, check the competitor's `public_pricing` flag in the registry. If `false`, SKIP the pricing page extract and tell the user to refer to captured Fourth proposals in the Marketing Brain KB instead. Saves credits on guaranteed-empty extractions.
- **Step 6 (new)**: After extracting a case study (or similar dated artifact), validate the `publication_date` field. If it equals the scrape date (today's date), the model hallucinated it — drop the field from the output and log the miss so we know which source pages lack reliable dates.

### Updated docs

- `.claude-plugin/plugin.json` — version → `1.2.0`; description updated to note the Cowork-registered connector expectation and that the plugin no longer ships its own MCP declaration.
- `.claude-plugin/marketplace.json` — version → `1.2.0` (new field); description aligned with the plugin manifest.
- `NOTICE` — added a v1.2.0 note recording the removal of the bundled MCP declaration.

### Re-sync strategy (unchanged)

Still deeply diverged from upstream firecrawl-claude-plugin. Track [firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) for tool changes.
