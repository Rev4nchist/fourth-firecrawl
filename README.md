# fourth-firecrawl

Fork of [firecrawl/firecrawl-claude-plugin](https://github.com/firecrawl/firecrawl-claude-plugin) — customized for the Fourth AI Enablement Team.

Adds task-oriented research skills for competitor intelligence, hospitality market scanning, content gap analysis, and staged KB ingestion into Fourth Marketing Brain. Bundles curated source catalogs and pre-built extraction schemas on top of the upstream Firecrawl CLI integration.

The base plugin turns any website into clean, LLM-ready markdown or structured data directly from Claude Code. The Fourth layer makes that capability actionable for specific research workflows the team runs repeatedly — competitor pricing sweeps before EBRs, weekly hospitality news briefings, and landing approved research into the Marketing Brain KB without manual copy-paste.

## Fourth-specific features

- **Task-oriented skills** — competitor-intel, market-scan, content-gap-analysis, and kb-ingest-review replace ad-hoc prompting with consistent, repeatable workflows
- **Curated source catalogs** — competitor registry (R365, 7shifts, Deputy, UKG, Toast, and more) and hospitality trade press catalog (NRN, FSR, Skift, Hotel Management, QSR, HR Dive) with verified URLs
- **Pre-built extraction schemas** — JSON schemas for pricing pages, feature comparisons, case studies, and press releases ensure comparable structured output across vendors
- **Staged KB ingestion** — all research lands in `.firecrawl/` for human review before the `kb-ingest-review` skill pushes approved content to the Marketing Brain KB via MCP
- **Credit guardrails** — per-operation caps and escalation thresholds applied automatically; per-user quota, not a shared pool

## Getting started

**Team members:** run `/fourth-firecrawl:setup` in Claude Code, then read `QUICKSTART.md`.

**Prerequisites:** Node.js 18+, Claude Code, plugin installed via Cowork organization plugins. No Firecrawl account needed before setup — the setup command walks you through it.

## Plugin structure

```
firecrawl-plugin/
├── .claude-plugin/
│   ├── plugin.json               Plugin manifest (name, skills array, license)
│   └── marketplace.json          Cowork marketplace metadata
│
├── commands/
│   └── setup.md                  /fourth-firecrawl:setup slash command
│
├── references/                   Plugin-wide reference docs
│   ├── competitor-registry.md    Competitor URLs + schema assignments
│   ├── hospitality-sources.md    Trade press URL catalog
│   ├── fourth-voice-guide.md     Tone rules for summarizing scraped content
│   ├── routing.md                Decision table: which skill for which task
│   └── extraction-schemas/       JSON extraction schemas
│       ├── pricing-page.json
│       ├── feature-comparison.json
│       ├── case-study.json
│       └── press-release.json
│
├── skills/
│   ├── firecrawl-cli/            Base CLI skill (upstream, preserved)
│   │   ├── SKILL.md
│   │   └── rules/
│   │       ├── install.md        Installation + auth instructions
│   │       ├── security.md       Output handling guidelines
│   │       └── credit-budget.md  Cost guardrails (Fourth addition)
│   │
│   ├── firecrawl-scrape/         Upstream skill
│   ├── firecrawl-search/         Upstream skill
│   ├── firecrawl-map/            Upstream skill
│   ├── firecrawl-crawl/          Upstream skill
│   ├── firecrawl-agent/          Upstream skill
│   ├── firecrawl-instruct/       Upstream skill
│   ├── firecrawl-download/       Upstream skill
│   │
│   ├── competitor-intel/         Fourth skill — schema-driven competitor scraping
│   ├── market-scan/              Fourth skill — hospitality trade press sweeps
│   ├── content-gap-analysis/     Fourth skill — identify coverage gaps vs. competitors
│   └── kb-ingest-review/         Fourth skill — review + ingest to Marketing Brain KB
│
├── QUICKSTART.md                 Team onboarding guide
├── CHANGES-FROM-UPSTREAM.md     Tracked diff from upstream repository
├── NOTICE                        Attribution and licensing
└── LICENSE                       AGPL-3.0 full text
```

## Attribution

This plugin is a fork of [firecrawl/firecrawl-claude-plugin](https://github.com/firecrawl/firecrawl-claude-plugin), copyright Firecrawl, licensed under AGPL-3.0. Fourth's additions are documented in `CHANGES-FROM-UPSTREAM.md`. See `NOTICE` for the full attribution statement.

## License

Licensed under AGPL-3.0, consistent with the upstream plugin. See `LICENSE` for the full text.
