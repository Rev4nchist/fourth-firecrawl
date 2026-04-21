# Fourth Firecrawl — Quickstart

## What this plugin does

The fourth-firecrawl plugin connects Claude Code to the Firecrawl web-scraping platform and layers four task-oriented research skills on top of it: competitor intelligence, hospitality market scanning, content gap analysis, and staged KB ingestion. It gives Fourth team members a repeatable, credit-aware workflow for pulling competitor pricing, tracking industry news, and landing structured research directly into the Fourth Marketing Brain knowledge base.

Underneath the Fourth-specific skills, the full Firecrawl CLI is available for ad-hoc scraping, crawling, mapping, and AI-powered structured extraction.

## Prerequisites

- **Node.js and npm** installed (Node 18+). Verify: `node --version`
- **Claude Code** running with the fourth-firecrawl plugin installed via Cowork organization plugins
- **A Firecrawl account** — you will create one in the setup step below (free, no payment required)

You do not need a Firecrawl account before installing the plugin. Setup handles that.

## First-time setup

Run this slash command in Claude Code:

```
/fourth-firecrawl:setup
```

It will check your auth status, walk you through registering an API key if needed, authenticate the CLI, and verify the install with a test scrape.

**Fourth does not issue Firecrawl keys. Each user registers their own free account — upgrade through Fourth AI Enablement Team if you exhaust the free tier.**

If you see "command not found" when the setup tries to run `firecrawl`, install the CLI manually first:

```bash
npm install -g firecrawl-cli
```

Then re-run `/fourth-firecrawl:setup`.

## Your 5-minute first run

After setup completes, try these three prompts directly in Claude Code. Each one auto-triggers the appropriate Fourth skill — you do not need to name the skill explicitly.

### 1. Competitor research

**Prompt:** "Research R365 pricing"

**What happens:**
- The `competitor-intel` skill activates
- Claude maps restaurant365.com, extracts pricing page content using the bundled `pricing-page.json` schema
- Output is staged at `.firecrawl/competitor-intel/r365-pricing-YYYYMMDD.json`
- Claude summarizes findings and offers to ingest to the Marketing Brain KB

**Expected output:** A structured JSON file with tier names, price indicators, and feature inclusions as R365 presents them on their public pricing pages.

### 2. Market scan

**Prompt:** "Scan hospitality news for tipping trends this week"

**What happens:**
- The `market-scan` skill activates
- Claude searches across NRN, FSR Magazine, Restaurant Dive, and QSR Magazine for tipping-related coverage from the past 7 days
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

| Need to... | Use skill | Example prompt |
|------------|-----------|----------------|
| Research a specific competitor | `competitor-intel` | "Pull Deputy pricing and feature list" |
| Track hospitality industry news | `market-scan` | "What's new in hotel workforce tech this week?" |
| Find content gaps vs. competitors | `content-gap-analysis` | "What topics are 7shifts covering that Fourth isn't?" |
| Land research into the KB | `kb-ingest-review` | "Ingest the staged competitor files to the marketing brain" |

For edge cases — single-URL fetches, deep site crawls, form-submission scraping — the base Firecrawl skills (`firecrawl-scrape`, `firecrawl-crawl`, `firecrawl-map`, `firecrawl-agent`, `firecrawl-search`) are also available. Ask Claude to "scrape this URL" or "crawl this site" directly.

See `references/routing.md` for the full decision table including fail-stop rules.

## Credit budget basics

Each Firecrawl account on the free tier gets 500 credits per month. Credits are per user — there is no shared pool across the team.

**Check your remaining credits:**

```bash
firecrawl --status
```

Look for "Credits: N remaining" in the output.

**Typical operation costs:**

| Operation | Approximate credit cost |
|-----------|------------------------|
| Single page scrape | 1 credit |
| `firecrawl search` (10 results) | 10-20 credits |
| `firecrawl map` (50 URLs) | 5-10 credits |
| `firecrawl crawl` (20 pages) | 20-40 credits |
| `firecrawl agent` run | 50-500 credits depending on scope |

The credit-budget rule file (`skills/firecrawl-cli/rules/credit-budget.md`) specifies the default caps the skills apply automatically. For agent runs that would exceed 25% of your remaining credits, the skill will ask for confirmation before proceeding.

If you regularly hit the 500-credit ceiling, contact the Fourth AI Enablement Team. Paid-tier upgrades are handled case-by-case — Fourth does not subsidize individual accounts by default.

## Troubleshooting

**"firecrawl: command not found"**

The CLI is not installed or not on your PATH.

```bash
npm install -g firecrawl-cli
```

If npm global installs are not on PATH, add the npm bin directory:

```bash
# macOS / Linux — add to ~/.zshrc or ~/.bashrc
export PATH="$(npm bin -g):$PATH"
```

**"Not authenticated" or "Invalid API key"**

Re-run setup:

```
/fourth-firecrawl:setup
```

Or re-authenticate directly:

```bash
firecrawl login --browser
```

**"Rate limited" or credits exhausted mid-task**

Check your balance:

```bash
firecrawl --status
```

If credits are at zero, the CLI will refuse new requests until the monthly cycle resets or you upgrade. Contact the Fourth AI Enablement Team if this is blocking active work.

**Skill not triggering automatically**

The skills use natural-language triggers. If auto-detection misses your intent, name the skill explicitly: "Use the competitor-intel skill to research HotSchedules pricing."

**Output files not appearing**

The skills write to `.firecrawl/` in your current working directory. Make sure Claude Code is open in the correct project directory. Verify with `ls .firecrawl/` after a run.

## Where does output go?

All staged research lands in `.firecrawl/` subdirectories:

```
.firecrawl/
  competitor-intel/    <- competitor-intel skill output
  market-scan/         <- market-scan skill output
  content-gap/         <- content-gap-analysis skill output
  install-check.md     <- written during setup verification
```

These files are gitignored by default (the plugin ships a `.gitignore` entry for `.firecrawl/`). They are staging only — content moves to the Fourth Marketing Brain KB via the `kb-ingest-review` skill after your review.

KB ingestion lands content under the folder structure you confirm during the ingest step (e.g., `competitive/r365/`, `market-signals/tipping/`).

## Getting help

For plugin issues, questions about credit upgrades, or onboarding support, reach out to the Fourth AI Enablement Team at [#ai-enablement] in your team's Slack workspace.

For Firecrawl CLI bugs or API issues (rate limits, auth failures that persist after re-login), check the [Firecrawl docs](https://docs.firecrawl.dev) or their [GitHub issues](https://github.com/mendableai/firecrawl/issues).
