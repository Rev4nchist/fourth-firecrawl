# Firecrawl MCP Specification for Cowork Plugin Rewrite

Generated: 2026-04-21
Purpose: Implementation-ready reference for rewriting fourth-firecrawl from a CLI-driven plugin to an MCP-first plugin suitable for Claude Cowork users.
Source of truth: firecrawl/firecrawl-mcp-server v3.13.0, src/index.ts, README, official docs at docs.firecrawl.dev/mcp-server, anthropics/knowledge-work-plugins, Claude Code MCP docs.

---

## 1. TL;DR

1. **Does Firecrawl MCP cover all our needs?** **Yes, with one caveat.** The server exposes 14 verified tools that cover scrape, search, map, crawl, extract (schema-driven structured), agent (autonomous research), and interact (clicks/forms). The caveat: there is **no credit-balance or status tool in the MCP** (that lived only in the CLI firecrawl --status). If we need credit accountability, we must call the HTTP GET /v2/team/credit-usage endpoint directly, or drop credit display entirely in Cowork. Also: the upstream README lists firecrawl_batch_scrape and firecrawl_check_batch_status but those are **NOT present in the current v3.13.0 source** -- README is ahead of the implementation. Do not rely on batch tools.
2. **Is there a hosted transport for Cowork?** **Yes.** Firecrawl operates a hosted MCP at https://mcp.firecrawl.dev/v2/mcp (streamable HTTP, Bearer auth) with a second shape https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp (key in path, no header). This is the **only viable transport for Cowork** because Cowork sandboxes cannot spawn stdio child processes (npx local MCPs are blocked) and remote MCPs are connected from Anthropic cloud, not from the user network interface.
3. **How do per-user keys work?** The hosted MCP reads the user Firecrawl API key from: (a) Authorization: Bearer header, (b) X-Firecrawl-API-Key header, (c) X-API-Key header, or (d) the URL path segment for the per-key URL shape. Confirmed in src/index.ts extractApiKey(headers) function. In a Cowork plugin, keys must NOT live in .mcp.json -- the only safe pattern is the path-based URL configured per-workspace via Cowork connector settings, OR ${FIRECRAWL_API_KEY} env-var interpolation if Cowork supports it (TBD -- see Open Questions).
4. **ebr-presentation-suite precedent?** ebr-presentation-suite/.mcp.json ships exactly one remote MCP (fourth-playwright) as type: sse pointing at a Railway-hosted URL with no auth headers (it is an open service). Pattern is minimal and works today for Cowork users. Firecrawl needs per-user auth, so our .mcp.json will be more complex -- but we reuse the remote URL in .mcp.json, no CLI shape.
5. **Recommended plugin structure post-pivot:** Keep all 4 Fourth task skills (competitor-intel, market-scan, content-gap-analysis, kb-ingest-review), rewrite 5-6 upstream primitive skills as MCP tool wrappers, delete firecrawl-cli and firecrawl-download skills (CLI-only, no MCP equivalent for download). Ship .mcp.json with hosted Firecrawl URL. Estimated rewrite: ~600 lines across 6 skill files + 1 .mcp.json + README updates. Roughly 4-6 hours of focused work.

---

## 2. MCP tool reference (v3.13.0, verified from src/index.ts)

All 14 tools are registered via server.addTool() in src/index.ts. Parameters below are zod schemas extracted verbatim from the source. Tool names are exact.

### firecrawl_scrape

Single-URL scrape with format control. The most powerful, fastest, most reliable scraper tool per the server description.

**Parameters** (scrapeParamsSchema, Zod):
- url (string, required): Target URL
- formats (array of enums or objects): markdown, html, rawHtml, links, screenshot, summary, changeTracking, json (with prompt+schema), branding
- onlyMainContent (boolean, optional): Strip nav/footer/sidebar
- includeTags / excludeTags (string[], optional): HTML tag filters
- waitFor (number, optional): ms to wait for JS rendering (use 5000-10000 for SPA)
- timeout (number, optional)
- mobile (boolean, optional): Mobile viewport
- skipTlsVerification (boolean, optional)
- removeBase64Images (boolean, optional)
- proxy (enum, optional): basic, stealth
- location ({ country, languages }, optional): Geo-spoofing
- maxAge (number, optional): Cache TTL -- 500 percent faster scrapes using cached data
- storeInCache (boolean, optional)
- blockAds (boolean, optional)
- jsonOptions ({ prompt, schema, systemPrompt }, optional): Used when formats includes json
- actions (array, optional): Interactive actions BEFORE extraction (click, wait, write, press, screenshot, scroll, scrape, executeJavascript, pdf, generatePDF). NB: SAFE_MODE disables these.

**Returns:** Text block (JSON or markdown depending on format). Includes a scrapeId in metadata usable for firecrawl_interact.

**Example (markdown, main content):**

    {
      "name": "firecrawl_scrape",
      "arguments": {
        "url": "https://www.r365hub.com/pricing",
        "formats": ["markdown"],
        "onlyMainContent": true
      }
    }

**Example (JSON schema extraction):**

    {
      "name": "firecrawl_scrape",
      "arguments": {
        "url": "https://competitor.com/pricing",
        "formats": [{
          "type": "json",
          "prompt": "Extract all pricing tiers",
          "schema": { "type": "object", "properties": { "tiers": { "type": "array" } } }
        }]
      }
    }


### firecrawl_map

Discover URLs on a site, optionally filtered by search query.

**Parameters:**
- url (string, required, URL)
- search (string, optional): Filter URLs by matching query
- sitemap (enum: include | skip | only, optional)
- includeSubdomains (boolean, optional)
- limit (number, optional)
- ignoreQueryParameters (boolean, optional)

**Returns:** Array of URLs found on the site.

**Example:**

    {
      "name": "firecrawl_map",
      "arguments": {
        "url": "https://docs.r365hub.com",
        "search": "pricing"
      }
    }

### firecrawl_search

Web search with optional scrape of results. Supports Google-style operators (site:, intitle:, -, quoted terms).

**Parameters:**
- query (string, required, min length 1)
- limit (number, optional): Results count; default low (~5) to avoid timeouts
- tbs (string, optional): Google time-based search filter (e.g., qdr:w for past week)
- filter (string, optional)
- location (string, optional): Geo context
- sources (array of { type: web | images | news }, optional): Multi-source search
- scrapeOptions (full scrape params, optional): Scrape each result
- enterprise (array of default | anon | zdr, optional): ZDR = zero data retention

**Returns:** Array of search results with optional scraped content.

**Example (news in past week):**

    {
      "name": "firecrawl_search",
      "arguments": {
        "query": "restaurant365 pricing changes",
        "limit": 10,
        "tbs": "qdr:w",
        "sources": [{ "type": "news" }]
      }
    }

### firecrawl_crawl

Async bulk-extract multiple pages from a site. Returns a job ID; poll with firecrawl_check_crawl_status.

**Parameters:**
- url (string, required)
- prompt (string, optional): Natural-language crawl scope hint
- excludePaths / includePaths (string[], optional): URL path filters
- maxDiscoveryDepth (number, optional)
- sitemap (enum, optional)
- limit (number, optional): Max pages to crawl
- allowExternalLinks / allowSubdomains / crawlEntireDomain (boolean, optional)
- delay (number, optional): ms between requests
- maxConcurrency (number, optional)
- webhook / webhookHeaders (optional, disabled in SAFE_MODE)
- deduplicateSimilarURLs (boolean, optional)
- ignoreQueryParameters (boolean, optional)
- scrapeOptions (full scrape params, optional): Per-page scrape config

**Returns:** { id, url } job metadata. Poll status with firecrawl_check_crawl_status.

### firecrawl_check_crawl_status

Check status of a crawl job.

**Parameters:** { id: string }

**Returns:** Status, progress counts, and (when complete) the extracted content. NB: crawl responses can be very large -- the tool warns about token overflow.


### firecrawl_extract

Schema-driven structured extraction across one or more URLs. This is the MCP equivalent of the old firecrawl-agent CLI when used with --schema.

**Parameters:**
- urls (string[], required): Array of URLs
- prompt (string, optional): Natural-language extraction instruction
- schema (JSON schema object, optional): Output shape
- allowExternalLinks (boolean, optional)
- enableWebSearch (boolean, optional): Allow web search for additional context during extraction
- includeSubdomains (boolean, optional)

**Returns:** Structured object matching the schema.

**Example (pricing extraction, matches references/extraction-schemas/pricing-page.json):**

    {
      "name": "firecrawl_extract",
      "arguments": {
        "urls": ["https://www.r365hub.com/pricing"],
        "prompt": "Extract all pricing tiers including name, monthly price, user limits, features",
        "schema": {
          "type": "object",
          "properties": {
            "tiers": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "monthly_price": { "type": "number" },
                  "user_limit": { "type": "integer" },
                  "features": { "type": "array", "items": { "type": "string" } }
                }
              }
            }
          }
        }
      }
    }

### firecrawl_agent

Async autonomous research agent. Returns a job ID; poll with firecrawl_agent_status. This is what firecrawl-agent CLI ran synchronously with --wait.

**Parameters:**
- prompt (string, required, max 10,000 chars): Natural-language research task
- urls (string[], optional): Starting URLs to focus the agent on
- schema (JSON schema, optional): Structured output shape

**Returns:** Job ID. Poll firecrawl_agent_status until status is completed.

**Note:** Complex agent queries take minutes. Use the async pattern -- start the job, do other work, poll every 10-30s.

### firecrawl_agent_status

Poll an agent job for results.

**Parameters:** { id: string }

**Returns:** Object with status (processing | completed | failed) and, when complete, the extracted data.

### firecrawl_interact

Interact with a previously scraped page in a live browser session. Requires a scrapeId from a prior firecrawl_scrape call. This is the MCP equivalent of the old firecrawl-instruct CLI.

**Parameters:**
- scrapeId (string, required): From prior scrape response metadata
- prompt (string, optional): Natural-language action (use this OR code)
- code (string, optional): Code to execute (use this OR prompt)
- language (enum: bash | python | node, optional, default node)
- timeout (number 1-300, optional, default 30): Seconds

**Returns:** Execution result: stdout, stderr, exit code, and live view URLs for the browser session.

### firecrawl_interact_stop

Stop an interact session to free resources.

**Parameters:** { scrapeId: string }

**Returns:** Ack confirmation.

### firecrawl_browser_create (DEPRECATED)

Create a cloud browser session. **Deprecated in favor of firecrawl_scrape + firecrawl_interact.**

**Parameters:**
- ttl (30-3600, optional): Total session lifetime in seconds
- activityTtl (10-3600, optional): Idle timeout
- streamWebView (boolean, optional)
- profile ({ name, saveChanges }, optional): Named profile for persistent state

**Returns:** { sessionId, cdpUrl, liveViewUrl }.

### firecrawl_browser_execute (DEPRECATED)

Execute bash/python/node code in a browser session.

**Parameters:** { sessionId, code, language } + agent-browser CLI commands.

### firecrawl_browser_list (DEPRECATED)

List browser sessions, filtered by status.

### firecrawl_browser_delete (DEPRECATED)

Destroy a browser session.

---

### Capability coverage matrix

| Capability we need | MCP tool | Status |
|---|---|---|
| Single-URL scrape to markdown | firecrawl_scrape (formats: [markdown]) | Full coverage |
| Search with time filter (past week) | firecrawl_search (tbs: qdr:w) | Full coverage |
| Search with source type (news) | firecrawl_search (sources with type news) | Full coverage |
| URL map | firecrawl_map | Full coverage |
| Bulk crawl | firecrawl_crawl + firecrawl_check_crawl_status | Full coverage |
| Schema-driven structured extraction | firecrawl_extract | Full coverage |
| Deep research / autonomous agent | firecrawl_agent + firecrawl_agent_status | Full coverage |
| Interactive browser actions (click, fill) | firecrawl_scrape (with actions) OR firecrawl_interact | Full coverage |
| Credit balance / status | **NONE** | **Gap** -- GET /v2/team/credit-usage HTTP endpoint exists but blocked by Cowork HTTPS sandbox |
| Bulk batch of known URLs | firecrawl_batch_scrape in README but NOT IMPLEMENTED in v3.13.0 src | **Gap** -- call firecrawl_scrape N times, or pass multiple URLs to firecrawl_extract |
| Site download to local files | None (CLI-only feature) | **Gap** -- drop this skill entirely for Cowork |

---

## 3. Auth + per-user keys

### 3.1 Hosted transport (Cowork + Claude Code remote)

**Endpoint:** https://mcp.firecrawl.dev/v2/mcp (streamable HTTP)
**Key-in-path alternative:** https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp (and SSE sibling https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/sse)

**Auth extraction order (from src/index.ts extractApiKey function):**
1. X-Firecrawl-API-Key header (highest precedence)
2. X-API-Key header
3. Authorization: Bearer <key> header
4. URL path segment (if using per-key URL shape)

Source excerpt:

    function extractApiKey(headers) {
      const headerAuth = headers[authorization];
      const headerApiKey = (headers[x-firecrawl-api-key] || headers[x-api-key]);
      if (headerApiKey) return Array.isArray(headerApiKey) ? headerApiKey[0] : headerApiKey;
      if (typeof headerAuth === string && headerAuth.toLowerCase().startsWith(bearer ))
        return headerAuth.slice(7).trim();
      return undefined;
    }

**Recommended .mcp.json shape for Claude Code (header auth):**

    {
      "mcpServers": {
        "firecrawl": {
          "type": "http",
          "url": "https://mcp.firecrawl.dev/v2/mcp",
          "headers": {
            "Authorization": "Bearer ${FIRECRAWL_API_KEY}"
          }
        }
      }
    }

Claude Code .mcp.json supports ${VAR} and ${VAR:-default} expansion. Per docs: https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/mcp-integration/references/authentication.md

**Alternative per-key URL shape (simpler, but key visible in config):**

    {
      "mcpServers": {
        "firecrawl": {
          "type": "http",
          "url": "https://mcp.firecrawl.dev/${FIRECRAWL_API_KEY}/v2/mcp"
        }
      }
    }

### 3.2 Local stdio (NOT usable in Cowork sandbox)

For Claude Desktop or Claude Code where stdio works:

    {
      "mcpServers": {
        "firecrawl": {
          "command": "npx",
          "args": ["-y", "firecrawl-mcp"],
          "env": {
            "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
          }
        }
      }
    }

On Windows npx needs the cmd /c wrapper:

    {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "..." }
    }

**This stdio path will NOT work in Cowork.** Cowork sandboxed VM blocks child-process spawning for local MCPs. Our plugin must use the hosted URL.

### 3.3 Docker (for self-hosted; irrelevant to Cowork)

Docker image mcp/firecrawl exists on Docker Hub but requires host-level installation -- not applicable to Cowork.

### 3.4 Multi-tenant / per-user keys

Multiple Firecrawl MCP instances can run per machine with different keys (each spawns its own process with its own env). For hosted transport, each connection headers/URL carry the key -- no server-side state shared. Firecrawl dashboard tracks usage per API key, so each user credit drain is billed to their own key.

---

## 4. Cowork integration approach

### 4.1 What actually happens in Cowork

Confirmed from Anthropic remote-MCP docs (https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) and Cowork sandbox writeup (https://dev.to/aaron_walker_dc0d1194638f/escaping-the-sandbox-jailbreaking-claude-cowork-dbd):

- **Remote MCPs connect from Anthropic cloud infrastructure**, not from the user machine. The https://mcp.firecrawl.dev/v2/mcp endpoint must be reachable from Anthropic IP ranges (it is -- Firecrawl is a public hosted service).
- **Local stdio MCPs cannot be used** because the Cowork VM has no access to the user local processes.
- **Outbound HTTPS from the sandbox is proxy-restricted** -- this is why user-code curl calls to api.firecrawl.dev fail. But MCP traffic goes through Anthropic side, not the user side.

### 4.2 User install flow (plugin distribution)

From anthropics/knowledge-work-plugins README and Cowork plugin support docs (https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork):

**Admin (org owner):**
1. Organization settings > Plugins
2. Click Add plugin, select GitHub as source
3. Enter owner/repo format (e.g., fourth-ai/fourth-firecrawl)
4. Plugin appears in org plugin library

**End user:**
1. Browse claude.com/plugins or the org plugin library in Cowork
2. Click Install on fourth-firecrawl
3. Cowork reads .claude-plugin/plugin.json and .mcp.json from the repo
4. Cowork surfaces any required auth (Firecrawl API key) through its connector UI
5. User pastes their Firecrawl API key into Cowork settings; Cowork injects it as the ${FIRECRAWL_API_KEY} env var for the plugin MCP config

**Claude Code (CLI) users:**

    # One-time: add marketplace
    claude plugin marketplace add fourth-ai/fourth-firecrawl

    # Install
    claude plugin install fourth-firecrawl@fourth-firecrawl

User must set FIRECRAWL_API_KEY in shell env or claude-code settings before install.

### 4.3 Key handoff patterns

Three patterns, in order of safety:

**Pattern A (RECOMMENDED): Cowork connector with env interpolation**
Ship .mcp.json with ${FIRECRAWL_API_KEY} placeholder. Cowork connector setup UI collects the key from the user and injects it at MCP-connect time. Key never touches disk in plugin form.

    {
      "mcpServers": {
        "firecrawl": {
          "type": "http",
          "url": "https://mcp.firecrawl.dev/v2/mcp",
          "headers": { "Authorization": "Bearer ${FIRECRAWL_API_KEY}" }
        }
      }
    }

**Pattern B: Per-key URL, env-interpolated**
Same safety as A but uses URL path. Slightly higher risk because URL logs may capture the key.

    {
      "mcpServers": {
        "firecrawl": {
          "type": "http",
          "url": "https://mcp.firecrawl.dev/${FIRECRAWL_API_KEY}/v2/mcp"
        }
      }
    }

**Pattern C (ANTI-PATTERN -- do not use): Hardcoded key in repo**
Never commit a hardcoded Bearer fc-abc123 to the plugin .mcp.json. This leaks the key to anyone who installs the plugin AND means all users share one bill.

### 4.4 Onboarding copy for README

Suggested language for the rewritten README:

> ## Setup
>
> This plugin requires a Firecrawl API key. Get one at https://www.firecrawl.dev/app/api-keys.
>
> **Cowork users:** After installing the plugin, Cowork will prompt you for your Firecrawl API key in the connector setup. Paste the key and finish setup -- the plugin will use your personal key for all scrape/search/extract calls and bill against your personal Firecrawl credits.
>
> **Claude Code users:** Set FIRECRAWL_API_KEY=fc-... in your shell environment before running claude plugin install fourth-firecrawl.

---

## 5. CLI -> MCP mapping (skill-by-skill)

| Old CLI verb | Old skill path | New MCP tool | New skill action |
|---|---|---|---|
| firecrawl scrape | skills/firecrawl-scrape/SKILL.md | firecrawl_scrape | REWRITE -- swap CLI commands for MCP tool calls, keep workflow tips |
| firecrawl search | skills/firecrawl-search/SKILL.md | firecrawl_search | REWRITE -- same Google-style operators still work |
| firecrawl map | skills/firecrawl-map/SKILL.md | firecrawl_map | REWRITE -- 1:1 parameter mapping |
| firecrawl crawl | skills/firecrawl-crawl/SKILL.md | firecrawl_crawl + firecrawl_check_crawl_status | REWRITE -- add async polling guidance |
| firecrawl agent | skills/firecrawl-agent/SKILL.md | firecrawl_extract (schema-driven) AND/OR firecrawl_agent + firecrawl_agent_status | REWRITE -- split guidance between I-have-URLs-and-schema (extract) and I-dont-know-where-the-data-is (agent) |
| firecrawl instruct | skills/firecrawl-instruct/SKILL.md | firecrawl_scrape (actions) + firecrawl_interact + firecrawl_interact_stop | REWRITE -- simplify to modern scrape+interact flow |
| firecrawl download | skills/firecrawl-download/SKILL.md | **NO MCP EQUIVALENT** | DELETE -- feature is CLI-only convenience. Users can replicate via firecrawl_map + firecrawl_scrape loop |
| firecrawl --status + firecrawl credit-usage | skills/firecrawl-cli/SKILL.md (umbrella skill) | **NO MCP EQUIVALENT** (credit-usage lives at HTTP GET /v2/team/credit-usage, blocked in Cowork sandbox) | DELETE -- primary skill no longer needed. Move any install/security guidance to plugin README + MCP troubleshooting reference |
| firecrawl init, firecrawl login, firecrawl config | (install rules) | **N/A -- Cowork handles key injection** | DELETE rules/install.md. MERGE any key-safety content into README under Setup. |
| credit budget enforcement | skills/firecrawl-cli/rules/credit-budget.md | No MCP tool; can still be advisory | REWRITE as rules/credit-budget.md with MCP-context guidance (e.g., prefer firecrawl_scrape over firecrawl_agent for single pages, cap crawl limit at 100) |

**Fourth task skills (untouched):**
- skills/competitor-intel/SKILL.md -- KEEP, update internal CLI examples to MCP tool calls
- skills/market-scan/SKILL.md -- KEEP, update internal references
- skills/content-gap-analysis/SKILL.md -- KEEP, update internal references
- skills/kb-ingest-review/SKILL.md -- KEEP, no Firecrawl-specific CLI references likely

**Files to delete outright:**
- skills/firecrawl-cli/SKILL.md
- skills/firecrawl-cli/rules/install.md
- skills/firecrawl-cli/rules/security.md (content about output/file handling may merge into a plugin-wide rules file)
- skills/firecrawl-download/SKILL.md

**Files to rewrite (5-6):**
- skills/firecrawl-scrape/SKILL.md
- skills/firecrawl-search/SKILL.md
- skills/firecrawl-map/SKILL.md
- skills/firecrawl-crawl/SKILL.md
- skills/firecrawl-agent/SKILL.md
- skills/firecrawl-instruct/SKILL.md (optionally rename to firecrawl-interact to match MCP naming)

**New file:**
- .mcp.json (root of plugin)

**Files to update:**
- .claude-plugin/plugin.json -- remove ./skills/firecrawl-cli from skills array; optionally add a mcpServers entry referencing the .mcp.json
- .claude-plugin/marketplace.json -- same
- README.md -- replace CLI install instructions with MCP/API-key setup
- QUICKSTART.md -- update user-facing commands

**Rewrite size estimate:**
- 6 skill rewrites at ~80 lines each = ~480 lines
- 1 new .mcp.json = ~15 lines
- README + QUICKSTART updates = ~100 lines changed
- Plugin manifests = ~10 lines changed
- **Total: ~600 lines**, roughly 4-6 hours of focused work

---

## 6. ebr-presentation-suite precedent

Full .mcp.json contents (3 fields only):

    {
      "mcpServers": {
        "fourth-playwright": {
          "type": "sse",
          "url": "https://fourth-playwright-mcp-production.up.railway.app/mcp"
        }
      }
    }

### Analysis

- **Transport type:** type is sse (Server-Sent Events). Note: SSE is marked deprecated in the MCP spec in favor of http (streamable HTTP), but it still works for existing Cowork users per bug report 7290 (https://github.com/anthropics/claude-code/issues/7290) -- the Claude Code team supports both.
- **Remote URL:** https://fourth-playwright-mcp-production.up.railway.app/mcp -- Railway-hosted, publicly reachable from Anthropic IP ranges. Good.
- **Auth headers:** None. The Playwright MCP accepts anonymous connections (no secrets involved on that service side).
- **Key location:** N/A (no key). Nothing sensitive in the file.
- **Known to work in Cowork:** Trusted precedent per the commit history (7f3df8a fix: use sse transport type for fourth-playwright MCP connector). The commit explicitly fixed the transport type to sse, confirming it was shipped and validated.

### Differences for Firecrawl

Firecrawl requires per-user auth. We diverge from the ebr pattern in three ways:

1. **Transport:** Use type http (streamable HTTP, the modern standard) instead of type sse. Cowork and Claude Code both support HTTP transport. The Firecrawl hosted MCP supports both, but HTTP is the recommended default.
2. **Auth header:** Add headers with Authorization Bearer followed by the FIRECRAWL_API_KEY variable. The ebr plugin has none.
3. **URL:** Point to https://mcp.firecrawl.dev/v2/mcp (official hosted endpoint), not a custom Railway URL.

**Key takeaway from precedent:** A plugin CAN ship a .mcp.json referencing a remote-hosted MCP and have Cowork users install it cleanly. The pattern is proven. Our job is to extend it to a pay-per-use authenticated service.

---

## 7. Open questions + risks

### Q1 (CRITICAL): Does Cowork connector UI support VAR expansion in plugin .mcp.json files?

**Why it matters:** Without env-var interpolation, users would need to either (a) hardcode their key in a local override (friction) or (b) use the per-key URL shape with the key pasted into Cowork connector config field. Option (b) works but mixes config paths.

**Evidence we have:** Claude Code .mcp.json definitely supports VAR-style expansion per Anthropic plugin-dev docs (https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/mcp-integration/references/authentication.md). Cowork is adjacent but not identical -- its connector UX may require a different pattern.

**Recommended resolution:**
- Ship .mcp.json with Bearer pattern first (matches Claude Code docs exactly).
- Test install on a real Cowork account as part of the rewrite.
- If Cowork does not support VAR expansion, switch to the per-key URL shape and document the friction.

### Q2 (HIGH): Is there any Firecrawl-sanctioned Cowork connector listing?

**Why it matters:** Some MCP vendors (Notion, HubSpot, Slack, Canva -- all in the anthropic/knowledge-work-plugins list) have OAuth-based connectors where Cowork/Anthropic handles token management. If Firecrawl has one, we would skip the API-key UX entirely.

**Evidence we have:** The anthropic knowledge-work-plugins repo marketing/.mcp.json lists 12+ connectors including ahrefs, similarweb, klaviyo, canva, supermetrics -- none of them are Firecrawl. Firecrawl does not appear in any of the 11 official plugins.

**Recommended resolution:**
- Short-term: ship our own .mcp.json with Bearer auth.
- Medium-term: reach out to Firecrawl (sales@firecrawl.dev or the MCP Registry maintainers) to ask if they plan an Anthropic OAuth connector; if yes, plan a future migration.

### Q3 (MEDIUM): Credit-balance visibility in Cowork

**Why it matters:** The old firecrawl-cli skill displayed firecrawl --status output with remaining credits. The MCP has no equivalent tool. Users may run multi-crawl operations with no idea they are burning credits.

**Recommended resolution:**
- Document in the rewritten firecrawl-crawl and firecrawl-agent skills: This operation is costly -- check your balance at firecrawl.dev/app.
- Keep credit-budget guidance in rules/credit-budget.md with safer defaults (e.g., limit: 20 for crawl, prefer scrape over agent for single-page).
- **Advanced option:** file a feature request upstream for a firecrawl_credit_status MCP tool. Low effort, high value.

### Q4 (MEDIUM): Firecrawl MCP version drift

**Why it matters:** README mentions firecrawl_batch_scrape and firecrawl_check_batch_status, which are NOT in v3.13.0 source. If Firecrawl ships these tools in a future version, our skill files may need updates. Also: SSE transport is deprecated, so we need to monitor for removal.

**Recommended resolution:**
- Pin to documented tool set in our skills (14 tools, no batch).
- Periodically check firecrawl-mcp-server releases for new tools.
- Do NOT rely on README claims that are not verified in source.

### Q5 (LOW): Windows/npx stdio fallback for non-Cowork users

**Why it matters:** Power users on native Windows who want stdio (faster first-request, local debugging) hit the well-documented cmd /c wrapper problem. Not a blocker for Cowork (which ignores stdio entirely) but may affect Claude Code users.

**Recommended resolution:**
- Default all users to the hosted URL (works on Cowork and Claude Code on all OSes).
- Document the stdio fallback with cmd /c wrapper for Windows power users who want it.

---

## 8. Sources

1. [firecrawl/firecrawl-mcp-server GitHub](https://github.com/firecrawl/firecrawl-mcp-server) -- official repo, v3.13.0
2. [firecrawl-mcp-server README](https://raw.githubusercontent.com/firecrawl/firecrawl-mcp-server/main/README.md) -- tool list, install, config
3. [src/index.ts](https://raw.githubusercontent.com/firecrawl/firecrawl-mcp-server/main/src/index.ts) -- authoritative tool registrations (14 tools verified)
4. [package.json](https://raw.githubusercontent.com/firecrawl/firecrawl-mcp-server/main/package.json) -- confirms name firecrawl-mcp, version 3.13.0, deps on @mendable/firecrawl-js and firecrawl-fastmcp
5. [Firecrawl MCP official docs](https://docs.firecrawl.dev/mcp-server) -- hosted URL, Claude Code install
6. [Firecrawl blog: Claude Managed Agents with Firecrawl](https://www.firecrawl.dev/blog/claude-managed-agents) -- Claude Code MCP setup example
7. [Claude Code MCP docs](https://code.claude.com/docs/en/mcp) -- transport types, headers, env-var expansion
8. [Claude Code plugin-dev auth reference](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/mcp-integration/references/authentication.md) -- .mcp.json Bearer pattern
9. [Cowork local-MCP sandbox writeup](https://dev.to/murat-a-a/how-we-got-local-mcp-servers-working-in-claude-cowork-the-missing-guide-nbc) -- confirms stdio blocked in sandbox
10. [Anthropic remote MCP docs](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) -- Anthropic cloud connects, not the user
11. [Cowork plugin support article](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork) -- plugin install UX
12. [anthropics/knowledge-work-plugins README](https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/README.md) -- plugin directory structure, marketplace install
13. [anthropics/knowledge-work-plugins marketing/.mcp.json](https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/marketing/.mcp.json) -- example .mcp.json with 13 connectors
14. [anthropics/knowledge-work-plugins sales/.mcp.json](https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/.mcp.json) -- example .mcp.json with 14 connectors
15. [Cowork sandbox architecture](https://www.anthropic.com/engineering/claude-code-sandboxing) -- official network isolation description
16. [bug: HTTP/SSE MCP Transport Ignores Authentication Headers](https://github.com/anthropics/claude-code/issues/7290) -- confirms SSE still works
17. ebr-presentation-suite/.mcp.json (local) -- local precedent at C:/Users/david.hayes/Projects/ebr-presentation-suite/.mcp.json
18. references/firecrawl-http-api-spec.md (local) -- prior HTTP-API research (superseded by this spec for Cowork use)
