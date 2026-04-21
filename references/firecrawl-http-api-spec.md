# Firecrawl HTTP API Reference (v2)

Generated: 2026-04-20
Purpose: Implementation-ready reference for rewriting the Fourth Firecrawl plugin to call the HTTP API directly, skipping firecrawl-cli in headless sandbox environments.

Base URL: `https://api.firecrawl.dev/v2`

## 1. TL;DR

1. **Can we drop the CLI?** Yes. Every CLI verb we use (scrape, search, map, crawl, agent, --status) maps 1:1 to a public HTTP endpoint on `api.firecrawl.dev/v2`. The CLI is a thin wrapper around `@mendable/firecrawl-js`, which itself is a thin wrapper around these HTTP endpoints. Confirmed by reading `src/commands/credit-usage.ts` and `src/commands/status.ts` in the firecrawl/cli repo -- they literally call `fetch(apiUrl + "/v2/team/credit-usage")` with an `Authorization: Bearer` header.
2. **Does device-code OAuth (RFC 8628) exist?** **No.** Firecrawl does not offer RFC 8628 device-code flow. The CLI `firecrawl login` uses a custom **PKCE + polling** scheme that requires the user default browser to open on the same machine (auth.ts lines 40-65 launch open/xdg-open/start). There is no user-facing short code to enter on a second device. For headless sandbox use, the only supported path is API-key auth via the `FIRECRAWL_API_KEY` env var or manual key entry. An `/admin/integration/validate-api-key` endpoint exists but is restricted to referred-user integration partners.
3. **Is there a credit-balance HTTP endpoint?** **Yes** -- `GET /v2/team/credit-usage` returns `{ success, data: { remainingCredits, planCredits, billingPeriodStart, billingPeriodEnd } }`. A companion `GET /v2/team/queue-status` returns concurrency info. **Caveat:** neither endpoint returns the team/account **name or email**. The team name is surfaced only by the webapp login polling endpoint (`firecrawl.dev/api/auth/cli/status`) and is never persisted by the CLI. The "burning credits for: <user>" accountability line must be satisfied with something else -- a fingerprint of the API key (e.g., last 4 chars of `fc-...`) or a plugin-level config value, not an API identity call.

Show-stopper assessment: **None**. The rewrite is straightforward (see section 5 for cost-of-rewrite).

---

## 2. Endpoint-by-endpoint reference

All endpoints use bearer auth: `Authorization: Bearer fc-<key>`. Content type is `application/json` for all POST bodies. `success: true` in response bodies indicates a happy-path result. Error shapes vary by status code; see below per endpoint.

### 2.1 POST /v2/scrape

Replaces: `firecrawl scrape <url> --format markdown,links --only-main-content --wait-for <ms> -o <file>`

- **Method / URL:** `POST https://api.firecrawl.dev/v2/scrape`
- **Sync/async:** Synchronous. Returns the scraped content in the response body.
- **Rate limit (req/min):** Free 10, Hobby 100, Standard 500, Growth 5000, Scale 7500.
- **Credit cost:** 1 credit / page base. +4 for JSON extraction, +4 for Enhanced Mode, +1 for ZDR, +1/PDF page. Stacking charges are cumulative.

**Request body (flat, ScrapeOptions merged with url):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `url` | string (URI) | yes | Target URL |
| `formats` | array of strings OR array of {type: "<fmt>"} objects | no (default: ["markdown"]) | Supported: markdown, summary, html, rawHtml, links, images, screenshot, json, changeTracking |
| `onlyMainContent` | boolean | no | Strips nav/header/footer |
| `waitFor` | integer (ms) | no | JS render delay before scrape |
| `includeTags` | string[] | no | HTML tags/selectors to keep |
| `excludeTags` | string[] | no | HTML tags/selectors to drop |
| `maxAge` | integer (ms) | no | Serve cached version if fresher than this |
| `minAge` | integer (ms) | no | Return cache only; no fresh fetch |
| `headers` | object | no | Custom request headers/cookies |
| `mobile` | boolean | no | Emulate mobile UA |
| `skipTlsVerification` | boolean | no | Skip TLS validation |
| `timeout` | integer (ms) | no | Min 1000. Counts queue time. |
| `parsers` | array | no | Controls PDF + file handling |
| `actions` | array | no | Pre-scrape browser actions (click, scroll, type) |
| `location` | object | no | {country, languages} geo override |
| `removeBase64Images` | boolean | no | Strips data: URIs from markdown |
| `blockAds` | boolean | no | Ad + cookie popup blocker |
| `proxy` | string | no | basic / stealth / auto |
| `storeInCache` | boolean | no | Cache in Firecrawl index |
| `profile` | object | no | Persistent browser storage |
| `zeroDataRetention` | boolean | no | ZDR mode (+1 credit/page) |

**Response 200 (ScrapeResponse):**

```json
{
  "success": true,
  "data": {
    "markdown": "...",
    "summary": "...",
    "html": "...",
    "rawHtml": "...",
    "screenshot": "https://...",
    "audio": "https://...signed",
    "links": ["..."],
    "actions": { "screenshots": [], "scrapes": [] },
    "metadata": {
      "title": "...", "description": "...", "language": "...",
      "statusCode": 200, "sourceURL": "...", "url": "..."
    },
    "json": {}
  }
}
```

**Error codes:** 402 payment required (out of credits), 429 rate limit, 500 server error. Error shape: `{ error: "message" }` or for 500: `{ success: false, code, error }`.

### 2.2 POST /v2/search

Replaces: `firecrawl search <query> --sources news --tbs qdr:d --scrape --limit N --json`

- **Method / URL:** `POST https://api.firecrawl.dev/v2/search`
- **Sync/async:** Synchronous. Returns results in body. (Also emits a job `id`, but there is no corresponding `GET /search/{id}` poll endpoint in the v2 spec -- `id` is for telemetry/logging.)
- **Rate limit (req/min):** Free 5, Hobby 50, Standard 250, Growth 2500, Scale 7500.
- **Credit cost:** 2 credits / 10 results (rounded up per 10). If `scrapeOptions` supplied, each scraped result also incurs scrape costs.

**Request body:**

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `query` | string | **yes** | -- | Search query |
| `limit` | integer | no | 10 | Per-source cap |
| `sources` | array | no | ["web"] | Subset of ["web", "news", "images"] |
| `categories` | array | no | [] | Filter to categories (GitHub, research, PDFs, etc.) |
| `tbs` | string | no | -- | Time filter: qdr:h, qdr:d, qdr:w, qdr:m, qdr:y |
| `location` | string | no | -- | e.g. "San Francisco,California,United States" |
| `country` | string | no | US | ISO code |
| `timeout` | integer | no | 60000 | ms |
| `ignoreInvalidURLs` | boolean | no | false | Skip URLs unusable by Firecrawl |
| `enterprise` | string[] | no | [] | ["zdr"] for 10 cr/10 results Zero Data Retention |
| `scrapeOptions` | object | no | {} | Full ScrapeOptions schema -- triggers auto-scrape of each result |

**Response 200:**

```json
{
  "success": true,
  "data": {
    "web":    [ { "url": "...", "title": "...", "description": "...", "markdown": "...", "metadata": {} } ],
    "news":   [],
    "images": []
  },
  "warning": "...",
  "id": "search_job_id",
  "creditsUsed": 2
}
```

The arrays returned map 1:1 to whichever `sources` were requested. Errors: 408 timeout `{ success: false, error }`, 500 as above.

### 2.3 POST /v2/map

Replaces: `firecrawl map <url> --search <q> --limit N --json`

- **Method / URL:** `POST https://api.firecrawl.dev/v2/map`
- **Sync/async:** Synchronous.
- **Rate limit:** same as /scrape.
- **Credit cost:** 1 credit / call (flat).

**Request body:**

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `url` | string (URI) | **yes** | -- | Root URL |
| `search` | string | no | -- | Filter terms |
| `sitemap` | string | no | -- | "include" / "only" / "skip" |
| `includeSubdomains` | boolean | no | false | |
| `ignoreQueryParameters` | boolean | no | false | |
| `ignoreCache` | boolean | no | false | |
| `limit` | integer | no | (up to 5000) | Max URLs |
| `timeout` | integer (ms) | no | -- | |
| `location` | object | no | -- | |

**Response 200 (MapResponse):**

```json
{
  "success": true,
  "links": [
    { "url": "https://...", "title": "...", "description": "..." }
  ]
}
```

Errors: 402, 429, 500.

### 2.4 POST /v2/crawl (and GET /v2/crawl/{id} for status)

### 2.4 POST /v2/crawl (and GET /v2/crawl/{id} for status)

Replaces: `firecrawl crawl <url> --wait --limit N --include-paths <pattern> --max-credits N`

- **Method / URL:** `POST https://api.firecrawl.dev/v2/crawl`
- **Sync/async:** **Async.** Returns a job `id` + status `url`. Poll `GET /v2/crawl/{id}` until `status === "completed"` or `"failed"`.
- **Rate limit (crawl POST req/min):** Free 1, Hobby 15, Standard 50, Growth 250, Scale 750.
- **Rate limit (status polling req/min):** Free 1500, Hobby+ 1500 (uniform).
- **Credit cost:** 1 credit / page crawled. Same per-page modifiers as /scrape. Credits are billed **as pages complete**, not up front.

**Request body (partial -- full schema has ~22 fields):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `url` | string (URI) | **yes** | Start URL |
| `prompt` | string | no | Natural-language prompt to derive crawl params |
| `limit` | integer | no | Default 10,000. Max pages. |
| `includePaths` | array (regex) | no | Pathname-only regex filter (whole regex via regexOnFullURL) |
| `excludePaths` | array (regex) | no | |
| `maxDiscoveryDepth` | integer | no | |
| `sitemap` | string | no | include / only / skip |
| `crawlEntireDomain` | boolean | no | |
| `allowExternalLinks` | boolean | no | |
| `allowSubdomains` | boolean | no | |
| `ignoreQueryParameters` | boolean | no | |
| `ignoreRobotsTxt` | boolean | no | |
| `regexOnFullURL` | boolean | no | |
| `robotsUserAgent` | string | no | |
| `delay` | integer (ms) | no | Per-request delay |
| `scrapeOptions` | object | no | Applied to every page |
| `webhook` | object | no | {url, headers?} for push delivery |

Note: there is **no maxCredits** field on /crawl. The CLI --max-credits is enforced client-side by watching status.creditsUsed during poll and calling DELETE /v2/crawl/{id} when the budget is hit. You must replicate this logic yourself.

**Response 200 from POST:**

```json
{ "success": true, "id": "<jobId>", "url": "https://api.firecrawl.dev/v2/crawl/<jobId>" }
```

**Response 200 from GET /v2/crawl/{id} (CrawlStatusResponseObj):**

```json
{
  "status": "scraping",
  "total": 123,
  "completed": 12,
  "creditsUsed": 12,
  "expiresAt": "2026-05-01T00:00:00Z",
  "next": null,
  "data": [
    {
      "markdown": "...", "html": "...", "rawHtml": "...", "links": ["..."],
      "screenshot": "...",
      "metadata": { "title": "", "description": "", "statusCode": 200, "sourceURL": "", "url": "" }
    }
  ]
}
```

`next` pages the result set in 10 MB chunks when a crawl is large. `DELETE /v2/crawl/{id}` cancels an active crawl. Errors per status code as above.

### 2.5 POST /v2/agent (and GET /v2/agent/{jobId} for polling)

Replaces: `firecrawl agent <prompt> --urls <url> --schema-file <path> --max-credits N --wait`

- **Method / URL:** `POST https://api.firecrawl.dev/v2/agent`
- **Sync/async:** **Async.** Returns { success, id }. Poll GET /v2/agent/{jobId} until status == completed or failed.
- **Rate limit (POST agent req/min):** Free 10, Hobby 100, Standard 500, Growth 1000, Scale 1000.
- **Rate limit (status polling req/min):** Free 500, Hobby+ 25000.
- **Credit cost:** Dynamic. 5 runs/day free, then usage-based pricing. maxCredits defaults to 2500; values >2500 are always billed as paid.

**Request body:**

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `prompt` | string (<=10000 chars) | **yes** | -- | |
| `urls` | string[] (URIs) | no | -- | Constrain to these URLs |
| `schema` | object (JSON schema) | no | -- | Output shape. CLI --schema-file <path> is client-side file read; the resulting object goes here. |
| `maxCredits` | number | no | 2500 | Budget cap. Enforced server-side. |
| `strictConstrainToURLs` | boolean | no | -- | If true, agent is not allowed to follow links outside urls |
| `model` | string enum | no | spark-1-mini | spark-1-mini (cheap) or spark-1-pro (accurate) |

**Response 200 from POST:** `{ "success": true, "id": "<jobId>" }`

**Response 200 from GET /v2/agent/{jobId}:**

```json
{
  "success": true,
  "status": "processing",
  "data": {},
  "model": "spark-1-mini",
  "error": null,
  "expiresAt": "2026-...",
  "creditsUsed": 42
}
```

`DELETE /v2/agent/{jobId}` cancels. Errors: 402 budget exhausted, 429 rate limit.

**Verified feature identity with CLI:** firecrawl agent is NOT CLI-only. The CLI agent.ts calls app.getAgentStatus(jobId) from @mendable/firecrawl-js which hits the same HTTP endpoints. HTTP and CLI are feature-equivalent.

### 2.6 GET /v2/team/credit-usage (replaces firecrawl --status, credit line)

- **Method / URL:** `GET https://api.firecrawl.dev/v2/team/credit-usage`
- **Sync/async:** Synchronous.
- **Rate limit:** Not documented per-endpoint. Shares team-wide limits.
- **Credit cost:** 0 (free to poll).

**Response 200:**

```json
{
  "success": true,
  "data": {
    "remainingCredits": 1000,
    "planCredits": 500000,
    "billingPeriodStart": "2026-01-01T00:00:00Z",
    "billingPeriodEnd": "2026-01-31T23:59:59Z"
  }
}
```

billingPeriodStart / billingPeriodEnd are null on the Free plan. Errors: 404, 500 with { success: false, error }.

Companion endpoints:
- `GET /v2/team/credit-usage/historical?byApiKey=<bool>` -- monthly history, optionally per-key
- `GET /v2/team/queue-status` -- returns { jobsInQueue, activeJobsInQueue, waitingJobsInQueue, maxConcurrency, mostRecentSuccess }
- `GET /v2/team/token-usage` -- tokens remaining (Extract only)
- `GET /v2/team/activity?endpoint=<>&limit=<>&cursor=<>` -- recent job log (endpoint, target URL/query, created_at, id)

**Identity gap:** None of these return the authenticated team name or user email. If the plugin needs to print burning credits for: <user>, it must take that value from plugin config or derive a stable fingerprint (e.g., fc-...xxxx last-4 of the key). The only API that returns team name + email is /admin/integration/validate-api-key, which is gated to referred-user integration partners and is not general-purpose.

---

## 3. Authentication options

### 3.1 API key (supported, recommended for sandbox)

- **Format:** `fc-` prefix followed by a UUID-style hex string. Validated client-side by the CLI at auth.ts line 522 (apiKey.startsWith(fc-)).
- **Header:** `Authorization: Bearer fc-<uuid>`
- **Env var:** `FIRECRAWL_API_KEY` (read by CLI, SDK, and is the conventional way to pass keys to CI).
- **Multiple keys:** Supported. The dashboard at firecrawl.dev/app/api-keys allows creating, naming, and revoking keys. Keys are team-scoped (all keys share the team credit pool). Constraint: you must always have >=1 active key; to revoke the last remaining key you create a new one first.
- **Self-hosted / custom API URL:** `FIRECRAWL_API_URL` env var or --api-url flag. When API URL is anything other than https://api.firecrawl.dev, the CLI skips auth entirely, allowing localhost:3002 local instances to run without a key.

### 3.2 Browser OAuth / PKCE (CLI only, NOT headless-compatible)

The firecrawl login command uses a **custom PKCE + polling** scheme, **not** RFC 8628 device code:
1. CLI generates session_id + code_verifier + code_challenge (SHA-256).
2. CLI shells out to open / xdg-open / start to launch the user default browser at https://firecrawl.dev/cli-auth?code_challenge=...#session_id=...
3. User logs in via the webapp UI on the same machine.
4. CLI polls POST https://firecrawl.dev/api/auth/cli/status (the webapp, not the API) every 2s for up to 5 minutes, sending session_id + code_verifier.
5. On success, response returns { status: complete, apiKey, apiUrl, teamName }. The CLI stores { apiKey, apiUrl } in ~/.config/firecrawl-cli/credentials.json (Linux) or ~/Library/Application Support/firecrawl-cli/ (macOS) or %AppData%/Roaming/firecrawl-cli/ (Windows).

**Critical limitation for our sandbox:** there is no short user_code that the user can type into a web form on their phone (the hallmark of RFC 8628). The CLI requires a browser on the same machine, which does not work in headless Linux sandboxes. A GitHub issue mentioning this pattern exists for Claude Code itself (anthropics/claude-code#22992), but there is no Firecrawl analog.

### 3.3 Service-account / deploy-key patterns

None documented. Firecrawl model is: one team, N API keys, all keys have equal privilege. There is no notion of scoped/read-only keys or service accounts. The closest equivalent is simply generating a new named key per deployment target (e.g., ci-sandbox-2026-04) and rotating via the dashboard when needed.

### 3.4 Integration-partner validation

POST /admin/integration/validate-api-key returns { teamName, email } for keys belonging to users referred through a registered integration partner. Requires partner credentials and referrer-slug verification. Not available for general use.

### Recommendation for plugin

Sandbox path: **FIRECRAWL_API_KEY env var** is the only viable auth. The user supplies it once during plugin setup; the plugin never needs a browser. For accountability strings, use fc-...<last4> fingerprint since no /me endpoint exists.

---

## 4. Rate limits / credit cost reference

### 4.1 API rate limits (requests / minute, current plans)

| Plan | /scrape | /map | /crawl | /search | /agent | /crawl/status | /agent/status |
|---|---|---|---|---|---|---|---|
| Free | 10 | 10 | 1 | 5 | 10 | 1500 | 500 |
| Hobby | 100 | 100 | 15 | 50 | 100 | 1500 | 25000 |
| Standard | 500 | 500 | 50 | 250 | 500 | 1500 | 25000 |
| Growth | 5000 | 5000 | 250 | 2500 | 1000 | 1500 | 25000 |
| Scale | 7500 | 7500 | 750 | 7500 | 1000 | 25000 | 25000 |

Notes:
- Limits are **per team** (all API keys on a team share counters).
- /extract shares limits with /agent. /batch/scrape shares with /crawl.
- FIRE-1 agent calls have a separate hard cap: 10/min for /scrape + /extract in agent mode, regardless of plan.
- Exceeding limits returns 429 with { error }.

### 4.2 Concurrent browser limits

| Plan | Concurrent browsers | Max queued jobs |
|---|---|---|
| Free | 2 | 50,000 |
| Hobby | 5 | 50,000 |
| Standard | 50 | 100,000 |
| Growth | 100 | 200,000 |
| Scale/Enterprise | 150+ | 300,000+ |

Jobs over the concurrency limit queue up to Max queued jobs; queue time counts against the request timeout. Exceeding the queue cap returns 429.

### 4.3 Credit costs per endpoint

| Endpoint | Base cost |
|---|---|
| /scrape | 1 credit / page |
| /crawl | 1 credit / page |
| /map | 1 credit / call |
| /search | 2 credits / 10 results (rounded up per 10; ["zdr"] enterprise = 10 credits / 10) |
| /browser | 2 credits / browser minute |
| /agent | Dynamic (5 free runs/day, then usage-based) |

**Scrape modifier stacks** (apply to /scrape, /crawl, /search scrapeOptions):

| Modifier | Extra cost |
|---|---|
| PDF parsing | +1 credit / PDF page |
| JSON format (LLM extraction) | +4 credits / page |
| Enhanced Mode | +4 credits / page |
| Zero Data Retention (ZDR) | +1 credit / page |

Example: JSON + Enhanced = 1 + 4 + 4 = **9 credits / page**.

**Credits are charged even on HTTP 403/404** from the target site -- rendering cost is paid regardless. Check metadata.statusCode in responses before retrying. Crawl/batch credits bill asynchronously as pages complete, so dashboard totals may lag the submit by minutes.

### 4.4 Monthly credit allotments

| Plan | Monthly credits |
|---|---|
| Free | 500 (one-time, does not renew) |
| Hobby | 3,000 |
| Standard | 100,000 |
| Growth | 500,000 |
| Scale / Enterprise | 1,000,000+ (custom) |

- Plan credits **do not roll over**; auto-recharge pack credits do (and expire 1 year after purchase).
- Out of credits + no auto-recharge -> HTTP 402 Payment Required.

### 4.5 IP-based limits

Not documented. Rate limits are bearer-token/team scoped, not IP-scoped. Running from a shared sandbox IP is fine as long as the bearer token team has available quota. (Unverified -- Firecrawl may apply undocumented anti-abuse IP throttles for very high request rates.)

---

## 5. Constraints discovered

### ToS / automation

- Firecrawl is marketed explicitly for AI agents, bots, and CI/CD use. The onboarding skill (firecrawl.dev/agent-onboarding/SKILL.md) is designed for autonomous agents. Headless sandbox use is an intended use case.
- No ToS clause was surfaced in the docs repo restricting programmatic / headless use. A formal ToS review was not performed (the ToS page was not in the docs mdx). Flagging as **unverified** -- recommend human legal check of the ToS before shipping.

### Feature gating (CLI vs HTTP)

- All scrape/search/map/crawl/agent/credit-usage features work identically over HTTP. The CLI is a thin wrapper around @mendable/firecrawl-js, verified by reading src/utils/client.ts in firecrawl/cli.
- CLI-only conveniences that must be reimplemented:
  - --max-credits for /crawl -- not a real API field; CLI watches creditsUsed during poll and issues DELETE /v2/crawl/{id} when budget is hit. Reimplement client-side.
  - --wait for crawl/agent -- CLI polls on your behalf. HTTP callers must loop.
  - --schema-file <path> for agent -- CLI reads file and includes as schema in body. Trivial to replicate.
  - -o <file> / --pretty -- pure output formatting. Trivial.
  - Team name display -- CLI gets this from the webapp login endpoint only. Not available via API. See section 3.
- Auth flow:
  - HTTP has only API-key auth. No browser flow. This is what we want for the sandbox.

### Sandbox-specific concerns

- **Credential storage:** the CLI credentials.json location is platform-specific. If our plugin stores the key for reuse, handle XDG_CONFIG_HOME (Linux), LocalAppData (Windows), ~/Library/Application Support (macOS) -- or just require the env var every run.
- **Node.js requirement:** firecrawl-cli requires npm install -g, which fails in a non-root sandbox. Dropping the CLI entirely removes this friction. Plain fetch or curl + jq suffices for HTTP calls.
- **Retry / backoff:** SDK handles this automatically. In HTTP-only mode, respect 429 and use exponential backoff. Firecrawl does not return Retry-After consistently -- test empirically.

---

## 6. Open questions / unverified claims

1. **Is the success: true guarantee consistent across 200 responses?** Observed in scrape, search, map, credit-usage. For some endpoints the spec shows success alone; some also have code/error siblings. **Recommend:** always check response.ok (HTTP 2xx) AND body.success === true defensively.
2. **Error shape consistency.** The spec shows different error shapes for different codes: { error } for 402/429/404 on some paths, { success: false, error } on others, { success: false, code, error } for 500. **Recommend:** centralize error parsing in one helper.
3. **ToS language.** Not verified in docs repo -- only inferred from marketing. Human legal review recommended before commercial deployment.
4. **IP-based rate limits or anti-abuse.** Not documented. Behavior from a shared sandbox IP at very high rates is unknown.
5. **/v2/search id field.** The response contains an id but no GET /v2/search/{id} endpoint is in the OpenAPI spec. Inferred to be telemetry-only. Not usable for polling.
6. **maxCredits on /crawl.** Absent from the v2 OpenAPI request schema. CLI implements this client-side. Confirmed there is no server-side budget gate for crawl; agent maxCredits *is* server-enforced.
7. **Team identity endpoint.** No /me or /account endpoint exists. The CLI login flow reveals teamName once at login but does not persist it. For the burning-credits-for line, fall back to key-fingerprint or require plugin config.
8. **api.firecrawl.dev hostname change.** Some v1 docs show api.firecrawl.com. The v2 OpenAPI and current CLI both use api.firecrawl.dev. Verified via auth.ts line 15 and credit-usage.ts line 55.
9. **GET /v2/scrape with URL param.** Some older blog posts mention GET /v2/scrape?url=... -- documentation drift. Only POST /v2/scrape is in the OpenAPI spec. Use POST.

---

## 7. Cost of rewrite (brief)

Straightforward. Estimated effort:

- **HTTP client (shared):** ~50 LOC. Bearer header, JSON body, response parsing, unified error handling.
- **Each CLI verb -> HTTP:** 15-40 LOC each. Scrape, map are trivial (one POST). Crawl + agent need a poll loop (~30 LOC each). Status is one GET.
- **max-credits guard for crawl:** ~20 LOC. Watch creditsUsed during poll, DELETE on breach.
- **Credit accountability string:** 1 LOC (fc- prefix plus the last-4 chars of the key).

Gotchas to budget for:
- Plan diff for scrapeOptions shape -- CLI accepts comma-separated --format markdown,links, HTTP wants formats: [markdown, links] (or the richer object form). Normalize in one place.
- Crawl polling cadence -- CLI defaults to 5s. Status endpoint has generous rate limits (1500/min on Free), so 2-3s is safe.
- Format objects for advanced formats (screenshot fullPage, JSON schema) vs plain strings. The Formats schema is oneOf [string, object] per format type.
- The next pagination URL on /v2/crawl/{id} for crawls >10 MB. You must follow it to get the full data set.

No nasty edges. The HTTP rewrite is less code than the CLI glue we have today and removes the entire npm install -g / global binary dependency chain from the sandbox.

---

## 8. Sources consulted

- Firecrawl v2 OpenAPI spec -- [firecrawl-docs/api-reference/v2-openapi.json](https://raw.githubusercontent.com/firecrawl/firecrawl-docs/main/api-reference/v2-openapi.json) (primary source for shapes)
- Firecrawl v1 OpenAPI spec -- [firecrawl/apps/api/openapi.json](https://raw.githubusercontent.com/firecrawl/firecrawl/main/apps/api/openapi.json) (cross-check)
- Firecrawl CLI auth source -- [firecrawl/cli src/utils/auth.ts](https://raw.githubusercontent.com/firecrawl/cli/main/src/utils/auth.ts) (PKCE flow confirmed, NOT RFC 8628)
- Firecrawl CLI credit source -- [firecrawl/cli src/commands/credit-usage.ts](https://raw.githubusercontent.com/firecrawl/cli/main/src/commands/credit-usage.ts) (HTTP mapping confirmed)
- Firecrawl CLI status source -- [firecrawl/cli src/commands/status.ts](https://raw.githubusercontent.com/firecrawl/cli/main/src/commands/status.ts) (credit + queue compound)
- Firecrawl CLI client wrapper -- [firecrawl/cli src/utils/client.ts](https://raw.githubusercontent.com/firecrawl/cli/main/src/utils/client.ts) (SDK passthrough confirmed)
- Firecrawl CLI credentials -- [firecrawl/cli src/utils/credentials.ts](https://raw.githubusercontent.com/firecrawl/cli/main/src/utils/credentials.ts) (no teamName persisted)
- Firecrawl CLI README -- [firecrawl/cli README.md](https://github.com/firecrawl/cli/blob/main/README.md)
- Firecrawl billing doc -- [firecrawl-docs/billing.mdx](https://raw.githubusercontent.com/firecrawl/firecrawl-docs/main/billing.mdx) (credit costs, stacking modifiers, 402 behavior)
- Firecrawl rate limits doc -- [firecrawl-docs/rate-limits.mdx](https://raw.githubusercontent.com/firecrawl/firecrawl-docs/main/rate-limits.mdx) (per-plan req/min, concurrency)
- Firecrawl dashboard doc -- [firecrawl-docs/dashboard.mdx](https://raw.githubusercontent.com/firecrawl/firecrawl-docs/main/dashboard.mdx) (API key management, team roles)
- Scrape endpoint guide -- [Firecrawl Blog: Mastering /scrape](https://www.firecrawl.dev/blog/mastering-firecrawl-scrape-endpoint)
- Crawl endpoint guide -- [Firecrawl Blog: Mastering /crawl](https://www.firecrawl.dev/blog/mastering-the-crawl-endpoint-in-firecrawl)
- Search endpoint guide -- [Firecrawl Blog: Mastering /search](https://www.firecrawl.dev/blog/mastering-firecrawl-search-endpoint)
- Integration validate-api-key -- [DeepWiki: Admin Interface](https://deepwiki.com/firecrawl/firecrawl/8.2-deployment-and-self-hosting) (partner-only, not general-use)
- Credit usage endpoint -- [Firecrawl Docs: Credit Usage](https://docs.firecrawl.dev/api-reference/endpoint/credit-usage)
- Queue status endpoint -- [Firecrawl Docs: Queue Status](https://docs.firecrawl.dev/api-reference/endpoint/queue-status)
- Device-code feature request (unrelated, for Claude Code) -- [claude-code#22992](https://github.com/anthropics/claude-code/issues/22992) (confirms this pattern does not exist in Firecrawl either)
