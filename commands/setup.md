---
description: First-time setup for the fourth-firecrawl plugin. Checks auth status, walks through API key registration, authenticates the Firecrawl CLI, and verifies the install with a test scrape.
---

# Fourth Firecrawl Setup

Welcome to the fourth-firecrawl plugin. This setup command gets your personal Firecrawl account connected and verifies everything works before you run your first research task.

Fourth does not issue or proxy Firecrawl API keys. Each user registers their own free account.

## Step 1: Check current status

```bash
firecrawl --status
```

Read the output:

- If it shows "Authenticated" and a credit balance, you are set. Skip to Step 5 to see available skills.
- If it shows "Not authenticated", "No API key found", or returns an error, continue to Step 2.

If the `firecrawl` command is not found at all, install it first:

```bash
npm install -g firecrawl-cli
```

Then re-run `firecrawl --status` before proceeding.

## Step 2: Get a free API key

Register at: https://firecrawl.dev/app/api-keys

The free tier provides 500 credits per month. That is enough for weekly competitor scans, ad-hoc market searches, and occasional agent runs. If you regularly exhaust the free tier, contact the Fourth AI Enablement Team about upgrade options — do not request a shared key from anyone on the team.

## Step 3: Authenticate

Choose one method:

**Option A — Browser OAuth (recommended)**

```bash
firecrawl login --browser
```

This opens firecrawl.dev in your browser. Sign in or create an account. Credentials are stored securely by the CLI and persist across sessions.

**Option B — API key directly**

```bash
firecrawl login --api-key "fc-YOUR-KEY-HERE"
```

Replace `fc-YOUR-KEY-HERE` with the key you copied from firecrawl.dev/app/api-keys.

**Option C — Environment variable**

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, or equivalent) for persistence:

```bash
export FIRECRAWL_API_KEY=fc-YOUR-KEY-HERE
```

Then reload your shell or run `source ~/.zshrc`.

## Step 4: Verify the install

Run one small scrape to confirm authentication, CLI functionality, and file output all work:

```bash
mkdir -p .firecrawl
firecrawl scrape "https://firecrawl.dev" -o .firecrawl/install-check.md
```

Expected result: a markdown file appears at `.firecrawl/install-check.md` with the Firecrawl homepage content. If this fails, re-run `firecrawl --status` to confirm auth is active.

## Step 5: Available skills

You now have access to four Fourth-specific research skills. Say any of these naturally in Claude Code to trigger the relevant skill:

| Skill | Example trigger |
|-------|----------------|
| `competitor-intel` | "Research R365 pricing" or "Get competitor intel on 7shifts" |
| `market-scan` | "Scan hospitality news for tipping trends this week" |
| `content-gap-analysis` | "What topics are competitors covering that Fourth isn't?" |
| `kb-ingest-review` | "Ingest this scrape to the Marketing Brain KB" |

See `QUICKSTART.md` for the 5-minute first-run walkthrough and a routing cheat sheet.

---

Need more credits? Contact the Fourth AI Enablement Team for upgrade paths. Do NOT request shared keys — each user authenticates individually.
