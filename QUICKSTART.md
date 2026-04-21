# Fourth Firecrawl — Quickstart

## What this plugin does

The fourth-firecrawl plugin connects Claude to the Firecrawl web-scraping platform via a hosted MCP connector and layers four task-oriented research skills on top of it: competitor intelligence, hospitality market scanning, content gap analysis, and staged KB ingestion. It gives Fourth team members a repeatable, credit-aware workflow for pulling competitor pricing, tracking industry news, and landing structured research directly into the Fourth Marketing Brain knowledge base. All Firecrawl operations happen through MCP tool calls — no CLI installation required.

## Prerequisites

- **A Firecrawl account** — free tier, 500 credits/month. You will create one during setup if you do not have one. Get a key at https://firecrawl.dev/app/api-keys.
- **Claude Code** running with the fourth-firecrawl plugin installed (Cowork org plugin or Claude Code CLI plugin).
- **No Node.js install required** — the plugin uses the hosted Firecrawl MCP at `https://mcp.firecrawl.dev/v2/mcp`. There is nothing to install locally.

## First-time setup

Run this slash command in Claude Code:

```
/fourth-firecrawl:setup
```

Setup checks whether the Firecrawl MCP tools are already in your available toolset. If they are, you are done. If not, it walks you through connecting your personal API key via the Cowork connector UI (Cowork users) or setting the `FIRECRAWL_API_KEY` environment variable (Claude Code CLI users).

**Fourth does not issue Firecrawl keys. Each user registers their own free account — upgrade through the Fourth AI Enablement Team if you exhaust the free tier.**

Full setup instructions, including both Cowork and Claude Code CLI paths, are at `commands/setup.md`.

## Your 5-minute first run

After setup completes, try these three prompts directly in Claude Code. Each one auto-triggers the appropriate Fourth skill — you do not need to name the skill explicitly.

### 1. Competitor research

**Prompt:** "Research R365 pricing"

**What happens:**
- The `competitor-intel` skill activates
- Claude calls `mcp__firecrawl__firecrawl_extract` with the bundled `pricing-page.json` schema against the R365 pricing page
- Output is staged at `.firecrawl/competitor-intel/r365-pricing-YYYYMMDD.json`
- Claude summarizes findings and offers to ingest to the Marketing Brain KB

**Expected output:** A structured JSON file with tier names, price indicators, and feature inclusions as R365 presents them on their public pricing pages.

### 2. Market scan

**Prompt:** "Scan hospitality news for tipping trends this week"

**What happens:**
- The `market-scan` skill activates
- Claude calls `mcp__firecrawl__firecrawl_search` with `tbs: "qdr:w"` and `sources: [{ "type": "news" }]` across NRN, FSR Magazine, Restaurant Dive, and QSR Magazine
- Results are staged at `.firecrawl/market-scan/`
- Claude produces a Fourth-voice summary with source attribution

**Expected output:** A briefing document covering 3-8 articles with headlines, source names, and relevance notes for Fourth customer segments (QSR, full-service, hotels).

### 3. KB ingestion

**Prompt:** "Ingest this scrape to the KB" (after running either of the above)

**What happens:**
- The `kb-ingest-review` skill activates
- Claude presents the staged `.firecrawl/` content for your review
- You confirm which files to ingest and under what KB folder (`competitive/`, `market-signals/`, etc.)
- Claude calls the Fourth Marketing Brain MCP to create or update KB entries with source metadata

**Expected output:** Confirmed KB entries with source URL, scrape date, and Fourth-assigned category tags.

## Routing cheat sheet

| Need to... | Skill | Example prompt |
|------------|-------|----------------|
| Research a specific competitor's pricing or features | `competitor-intel` | "Pull Deputy pricing and feature list" |
| Track hospitality industry news or trends | `market-scan` | "What's new in hotel workforce tech this week?" |
| Find content gaps vs. competitors | `content-gap-analysis` | "What topics are 7shifts covering that Fourth isn't?" |
| Land staged research into the Marketing Brain KB | `kb-ingest-review` | "Ingest the staged competitor files to the marketing brain" |
| Scrape a single URL ad-hoc | `firecrawl-scrape` | "Scrape https://competitor.com/pricing as markdown" |
| Discover all URLs on a site | `firecrawl-map` | "Map the Toast website and filter for pricing pages" |
| Crawl a site section in bulk | `firecrawl-crawl` | "Crawl all blog posts on restaurant365.com/blog" |
| Extract structured data from known URLs | `firecrawl-agent` (extract mode) | "Extract pricing tiers from these 3 URLs with this schema" |
| Autonomous deep research across unknown sources | `firecrawl-agent` (agent mode) | "Research what competitors say about tipping compliance" |

For the full decision table including edge cases, see `references/routing.md`.

## Credit budget basics

Each Firecrawl account on the free tier gets 500 credits per month. Credits are per user — there is no shared pool across the team.

**Check your remaining balance** at https://firecrawl.dev/app (dashboard, top right). The Firecrawl MCP does not expose a credit-check tool — the dashboard is the only way to see your balance.

**Typical operation costs:**

| Operation | Approximate cost |
|-----------|-----------------|
| `firecrawl_scrape` — single page | ~1 credit |
| `firecrawl_search` — 10 results, no per-result scrape | ~10 credits |
| `firecrawl_map` — 50 URLs | ~5 credits |
| `firecrawl_crawl` — 20 pages | ~20-40 credits |
| `firecrawl_extract` — 1-3 URLs with schema | ~5-15 credits |
| `firecrawl_agent` run — autonomous, varies by scope | 50-500 credits |

The skills apply automatic caps: crawls default to `limit: 100`, agent runs cap at `maxCredits: 500`. For any operation estimated to burn more than 125 credits (25% of the free monthly quota), the skill will ask for confirmation before proceeding.

Full per-tool guidance is at `references/credit-budget.md`.

## Troubleshooting

**"MCP not connected" or Firecrawl tools not available**

The `mcp__firecrawl__*` tools are missing from Claude's toolset. Re-run `/fourth-firecrawl:setup` and follow the Step 3 instructions to connect the Firecrawl MCP connector.

- Cowork: verify the Firecrawl entry appears in Settings → Connectors with a connected status.
- Claude Code CLI: confirm `echo $FIRECRAWL_API_KEY` returns your key in the shell where Claude Code is running.

**"Invalid API key" or 401 responses from the MCP**

Your key may have been regenerated or entered with a typo. Go to https://firecrawl.dev/app/api-keys, create a new key, and update it in Cowork connector settings or your shell environment. Re-run `/fourth-firecrawl:setup` Step 4 to verify.

**Credits exhausted mid-task**

The Firecrawl API returns a 402 or quota-exceeded error. Check your balance at https://firecrawl.dev/app. If credits are at zero, the MCP will refuse new requests until the monthly cycle resets or you upgrade. Contact the Fourth AI Enablement Team if this is blocking active work.

**Skill not triggering automatically**

The skills use natural-language triggers. If auto-detection misses your intent, name the skill explicitly: "Use the competitor-intel skill to research HotSchedules pricing."

**Output files not appearing in `.firecrawl/`**

Make sure Claude Code is open in the correct project directory. Verify with `ls .firecrawl/` after a run. The `.firecrawl/` directory is created by the first skill run if it does not exist.

## Output location

All staged research lands in `.firecrawl/` subdirectories:

```
.firecrawl/
  competitor-intel/    <- competitor-intel skill output
  market-scan/         <- market-scan skill output
  content-gap/         <- content-gap-analysis skill output
```

These files are gitignored by default. They are staging only — content moves to the Fourth Marketing Brain KB via the `kb-ingest-review` skill after your review and confirmation.

KB ingestion lands content under the folder structure you confirm during the ingest step (for example, `competitive/r365/` or `market-signals/tipping/`).

## Getting help

For plugin issues, questions about credit upgrades, or onboarding support, reach out to the Fourth AI Enablement Team at [#ai-enablement] in your team's Slack workspace.

For Firecrawl MCP or API issues (rate limits, persistent auth failures), check the [Firecrawl docs](https://docs.firecrawl.dev) or the [firecrawl-mcp-server GitHub repo](https://github.com/firecrawl/firecrawl-mcp-server/issues).
