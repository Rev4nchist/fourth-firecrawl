# Credit Budget

Per-operation credit guidance, escalation thresholds, and cost-minimization rules for the fourth-firecrawl plugin.

## How to check your quota

The Firecrawl MCP does not expose a credit-balance tool. There is no `mcp__firecrawl__firecrawl_credit_status` call you can make from within Claude.

**Check your balance at:** https://firecrawl.dev/app

Your remaining credits appear in the dashboard after login. Check before starting any multi-step operation (crawl, agent run, or large search) if you are uncertain how much quota remains.

Credits reset monthly on the anniversary of your account creation date, not on a calendar month boundary.

## Default operation budgets

Apply these defaults in every skill that calls Firecrawl MCP tools. Do not exceed them without explicit user confirmation.

| Tool | Default parameter cap | Approximate credit cost |
|------|----------------------|------------------------|
| `mcp__firecrawl__firecrawl_scrape` | No per-call cap — single page, cheap | ~1 credit per page |
| `mcp__firecrawl__firecrawl_search` | `limit: 10` — do not exceed without confirmation | ~10 credits (no per-result scrape); ~10-50 credits if `scrapeOptions` is included |
| `mcp__firecrawl__firecrawl_map` | `limit: 50` default | ~5 credits |
| `mcp__firecrawl__firecrawl_crawl` | `limit: 100`, `maxConcurrency: 2` | ~100-200 credits depending on page count |
| `mcp__firecrawl__firecrawl_check_crawl_status` | Read-only poll — no credit cost | 0 credits |
| `mcp__firecrawl__firecrawl_extract` | No per-call cap — prefer over agent for known URLs | ~5-15 credits for 1-3 URLs |
| `mcp__firecrawl__firecrawl_agent` | `maxSteps: 10`, `maxCredits: 500` | 50-500 credits — treat as expensive |
| `mcp__firecrawl__firecrawl_agent_status` | Read-only poll — no credit cost | 0 credits |
| `mcp__firecrawl__firecrawl_interact` | Single session action | ~5-20 credits depending on session duration |
| `mcp__firecrawl__firecrawl_interact_stop` | Frees session resources | 0 credits |

Note: `firecrawl_search` with `scrapeOptions` scrapes every result page — cost multiplies by the number of results. Omit `scrapeOptions` unless the task explicitly needs full page content from each result.

## Escalation thresholds

Before starting any operation, estimate the likely credit cost. Apply these rules:

| Estimated cost | Action |
|---------------|--------|
| Less than 25 credits | Proceed without asking |
| 25-125 credits (up to 25% of free-tier monthly quota) | Mention the estimate to the user; proceed unless they object |
| 125-250 credits (25-50% of monthly quota) | Ask the user to confirm before proceeding. Suggest a cheaper alternative if one exists. |
| More than 250 credits (more than 50% of monthly quota) | Refuse to proceed automatically. Explain the cost, describe smaller alternatives, and wait for explicit user approval. |

The 500-credit free-tier figure is the baseline for threshold math. Users on paid tiers have higher quotas — if the user confirms they are on a paid plan, adjust thresholds proportionally.

## Free tier guidance

The 500-credit free monthly quota supports typical team usage patterns:

- One weekly `market-scan` run (10-30 credits per run, ~50 credits/month)
- Two to three `competitor-intel` runs per month (15-50 credits per run, ~100 credits/month)
- Occasional ad-hoc scrapes and searches (~50 credits/month)
- One or two `firecrawl_agent` runs per month at moderate scope (~100-200 credits)

That leaves a buffer for unexpected tasks. If a user reports regularly exhausting the free tier, they should contact the Fourth AI Enablement Team about a paid tier upgrade. Fourth does not subsidize individual paid accounts by default — upgrades are handled case-by-case.

## Per-user, not shared

Each user's Firecrawl credits are tied to their own API key and their own Firecrawl account. There is no cross-user credit pooling. Usage is visible only in each user's own Firecrawl dashboard.

Never request or accept another team member's API key. Never ask the Fourth AI Enablement Team for a shared key. Each user authenticates individually.

## Choosing the right tool: cost decision tree

Work through this order before selecting a Firecrawl MCP tool:

1. **Do you know the exact URLs and the output schema you need?**
   Yes → use `mcp__firecrawl__firecrawl_extract`. This is the cheapest structured-data path.

2. **Do you have a URL but just need the page content as markdown or text?**
   Yes → use `mcp__firecrawl__firecrawl_scrape`. Single-page, minimal cost.

3. **Do you need to find URLs first before scraping?**
   Yes → use `mcp__firecrawl__firecrawl_map` to discover the URL set, then `firecrawl_scrape` or `firecrawl_extract` on the results.

4. **Do you need many pages from one site?**
   Yes → use `mcp__firecrawl__firecrawl_crawl` with a `limit` appropriate to the task. Set `maxConcurrency: 2` to pace requests.

5. **Do you not know where the data is and need autonomous multi-step research?**
   Last resort → use `mcp__firecrawl__firecrawl_agent` with `maxSteps: 10` and `maxCredits: 500`. Inform the user of the expected cost range before starting.

The rule: reach for `firecrawl_agent` only when no other tool can answer the question. Agent runs are multi-step and autonomous — cost is unpredictable and can be high.
