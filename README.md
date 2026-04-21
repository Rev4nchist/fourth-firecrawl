# Fourth Firecrawl

Fork of [firecrawl/firecrawl-claude-plugin](https://github.com/firecrawl/firecrawl-claude-plugin) — customized for the Fourth AI Enablement Team. Licensed under AGPL-3.0.

## What it is

The fourth-firecrawl plugin connects Claude to the Firecrawl web-scraping platform via the hosted Firecrawl MCP at `https://mcp.firecrawl.dev/v2/mcp`. It layers four task-oriented research skills on top of that connection to give Fourth team members repeatable, credit-aware workflows for competitive intelligence, market monitoring, and staged KB ingestion.

- **Competitor intelligence** — schema-driven pricing, feature, and case-study extraction from a curated registry of named competitors (R365, 7shifts, Deputy, UKG, Toast, and more)
- **Hospitality market scanning** — weekly sweeps across trade press (NRN, FSR Magazine, Skift, Hotel Management, QSR, Restaurant Dive) for trends and signals
- **Content gap analysis** — identify topics competitors publish that Fourth does not, feeding content strategy and EBR preparation
- **Staged KB ingestion** — all research lands in `.firecrawl/` for human review before the `kb-ingest-review` skill pushes approved content to the Fourth Marketing Brain knowledge base via MCP

## How it works

1. **Scrape or search** — Claude calls one or more Firecrawl MCP tools (`mcp__firecrawl__firecrawl_scrape`, `mcp__firecrawl__firecrawl_search`, `mcp__firecrawl__firecrawl_extract`, etc.) using your personal API key. Requests are billed against your individual Firecrawl credit quota, not a shared pool.
2. **Stage in `.firecrawl/`** — results are written to subdirectories under `.firecrawl/` in your working directory. These files are gitignored and exist for review only.
3. **Review and ingest** — after confirming the staged output, `kb-ingest-review` calls the Fourth Marketing Brain MCP to create or update KB entries with source metadata.

## Install

### Cowork

1. An org admin adds `fourth-ai/fourth-firecrawl` via **Organization Settings → Plugins → Add plugin**.
2. Browse to the plugin in the org plugin library and click **Install**.
3. Run `/fourth-firecrawl:setup` to connect your personal Firecrawl API key via the Cowork connector UI.

### Claude Code CLI

```bash
# Add marketplace and install
claude plugin marketplace add fourth-ai/fourth-firecrawl
claude plugin install fourth-firecrawl@fourth-firecrawl
```

Then run `/fourth-firecrawl:setup` to configure your API key.

Both paths require a personal Firecrawl API key. See `QUICKSTART.md` and `commands/setup.md` for the full key-setup walkthrough.

## Plugin structure

```
fourth-firecrawl/
├── .claude-plugin/
│   ├── plugin.json               Plugin manifest
│   └── marketplace.json          Cowork marketplace metadata
│
├── .mcp.json                     Firecrawl MCP connector declaration
│
├── commands/
│   └── setup.md                  /fourth-firecrawl:setup slash command
│
├── references/
│   ├── competitor-registry.md    Competitor URLs + schema assignments
│   ├── hospitality-sources.md    Trade press URL catalog
│   ├── fourth-voice-guide.md     Tone rules for summarizing scraped content
│   ├── routing.md                Decision table: which skill for which task
│   ├── credit-budget.md          Per-operation credit caps and escalation thresholds
│   ├── firecrawl-mcp-spec.md     MCP tool reference (implementation notes)
│   └── extraction-schemas/
│       ├── pricing-page.json
│       ├── feature-comparison.json
│       ├── case-study.json
│       └── press-release.json
│
├── skills/
│   ├── firecrawl-scrape/         Single-URL scrape via MCP
│   ├── firecrawl-search/         Web search via MCP
│   ├── firecrawl-map/            URL discovery via MCP
│   ├── firecrawl-crawl/          Async bulk crawl via MCP
│   ├── firecrawl-agent/          Autonomous research agent via MCP
│   ├── firecrawl-interact/       Browser interaction via MCP (scrape + interact)
│   ├── competitor-intel/         Fourth skill — schema-driven competitor scraping
│   ├── market-scan/              Fourth skill — hospitality trade press sweeps
│   ├── content-gap-analysis/     Fourth skill — identify coverage gaps vs. competitors
│   └── kb-ingest-review/         Fourth skill — review + ingest to Marketing Brain KB
│
├── QUICKSTART.md                 Team onboarding guide
├── CHANGES-FROM-UPSTREAM.md      Tracked diff from upstream repository
├── NOTICE                        Attribution and licensing
└── LICENSE                       AGPL-3.0 full text
```

## Attribution

See `NOTICE` for the full attribution statement. `CHANGES-FROM-UPSTREAM.md` documents all divergence from the upstream [firecrawl/firecrawl-claude-plugin](https://github.com/firecrawl/firecrawl-claude-plugin) repository.

## License

Licensed under AGPL-3.0, consistent with the upstream plugin. See `LICENSE` for the full text.

---

See `QUICKSTART.md` to get running in 5 minutes.
