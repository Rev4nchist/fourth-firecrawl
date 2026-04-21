---
description: First-time setup for the fourth-firecrawl plugin. Checks that the Firecrawl MCP connector is active, walks through API key registration, and verifies the connection with a test scrape.
---

# Fourth Firecrawl Setup

Welcome to the fourth-firecrawl plugin. This setup command confirms your personal Firecrawl API key is wired into the MCP connector and verifies that Claude can reach the Firecrawl tools before you run your first research task.

Fourth does not issue or proxy Firecrawl API keys. Each user registers their own free account.

## Step 1: Check whether the Firecrawl MCP is already connected

Look at the tools currently available to Claude. If you can see tools whose names begin with `mcp__firecrawl__` (for example, `mcp__firecrawl__firecrawl_scrape`), the connector is active and your key is working. Skip directly to Step 5.

If those tools are absent, continue to Step 2.

## Step 2: Get a free Firecrawl API key

Register at: https://firecrawl.dev/app/api-keys

The free tier provides 500 credits per month — enough for weekly competitor scans, ad-hoc market searches, and occasional agent runs. Fourth does not issue Firecrawl keys. Register your own account; contact the Fourth AI Enablement Team about upgrade options if you regularly exhaust the free tier. Do not request a shared key from anyone on the team.

## Step 3: Configure the MCP connector

Choose the path that matches how you run Claude:

### Cowork path

1. Open your Cowork workspace and go to **Settings → Connectors**.
2. Find **Firecrawl** in the connector list. It is auto-discovered from the plugin's `.mcp.json` file when the plugin is installed.
3. Paste your Firecrawl API key (the `fc-...` string from Step 2) into the key field.
4. Click **Save**.

Cowork injects the key as the `FIRECRAWL_API_KEY` environment variable at MCP-connect time. The key is never written into the plugin repository.

### Claude Code CLI path

Add your key to your shell environment before starting Claude Code:

```bash
export FIRECRAWL_API_KEY=fc-YOUR-KEY-HERE
```

Add that line to your shell profile (`~/.zshrc`, `~/.bashrc`, or equivalent) for persistence across sessions, then restart Claude Code so the plugin picks up the environment variable.

## Step 4: Verify the connection

Ask Claude to run a small test scrape using the Firecrawl MCP:

> "Call `mcp__firecrawl__firecrawl_scrape` on `https://firecrawl.dev` with `formats: ["markdown"]` and `onlyMainContent: true`. Return the first 200 characters of the result."

If Claude returns a markdown snippet of the Firecrawl homepage, setup is complete.

If Claude reports that the tool is not available, go back to Step 3 and confirm the connector saved correctly. In Cowork, check Settings → Connectors and verify the Firecrawl entry shows a green connected status. In Claude Code CLI, confirm the environment variable is set in the same shell session where you launched Claude Code.

## Step 5: Available skills

You now have access to four Fourth-specific research skills. Say any of these naturally in Claude Code to trigger the relevant skill:

| Skill | Example trigger |
|-------|----------------|
| `competitor-intel` | "Research R365 pricing" or "Get competitor intel on 7shifts" |
| `market-scan` | "Scan hospitality news for tipping trends this week" |
| `content-gap-analysis` | "What topics are competitors covering that Fourth isn't?" |
| `kb-ingest-review` | "Ingest this scrape to the Marketing Brain KB" |

See `QUICKSTART.md` for the 5-minute first-run walkthrough and a full routing cheat sheet.

---

Need more credits? Contact the Fourth AI Enablement Team about upgrade paths. Never request shared keys — each user authenticates individually.
