# Credit Budget

Cost guardrails for Firecrawl CLI operations. Each user's quota is their own — there is no shared credit pool across the Fourth team.

## How to check your quota

```bash
firecrawl --status
```

Output includes a line like:

```
Credits: 487 remaining
```

Read this before any expensive operation. If credits are at zero, new requests will be refused by the API until the monthly cycle resets.

For a detailed usage breakdown:

```bash
firecrawl credit-usage
```

## Default caps

Apply these limits in skill commands unless the user explicitly requests a different scope. The `--max-credits` flag caps credit spend per operation; `--limit` caps the number of pages or results.

| Operation | Default flags | Approximate credit cost |
|-----------|---------------|------------------------|
| `firecrawl scrape` (single page) | No cap needed | 1 credit |
| `firecrawl search` | `--limit 10` | 10-20 credits |
| `firecrawl map` | `--limit 50` | 5-10 credits |
| `firecrawl crawl` | `--limit 20 --max-credits 1000` | 20-100 credits |
| `firecrawl agent` | `--max-credits 500` | 50-500 credits |

For `firecrawl agent` runs involving many pages or complex extraction, costs can exceed 500 credits. Always pass `--max-credits` explicitly and confirm with the user if the run would be expensive relative to their remaining balance.

## Escalation thresholds

Before running an operation, estimate the credit cost from the table above. Compare against the user's remaining balance from `firecrawl --status`.

| Estimated cost vs. remaining credits | Action |
|--------------------------------------|--------|
| Less than 25% of remaining | Proceed without asking |
| 25% to 50% of remaining | Ask user to confirm before proceeding |
| More than 50% of remaining | Refuse and suggest a smaller alternative |

When refusing or asking for confirmation, tell the user:
- The estimated cost of the requested operation
- Their current remaining balance
- A smaller alternative that stays within the 25% threshold

Example message when threshold is exceeded:

> This agent run is estimated at ~800 credits. You have 1,200 remaining (free tier). That would use 67% of your monthly allowance. A targeted scrape of just the pricing page would cost ~5 credits. Proceed with the full agent run, or switch to the targeted scrape?

## Free tier guidance

500 credits per month is the Firecrawl free tier. Typical usage patterns for a Fourth team member:

- Weekly competitor pricing check (1-2 pages per competitor, 5 competitors): ~50 credits/week → ~200 credits/month
- Weekly hospitality news scan (10-result search, 4 sources): ~80 credits/week → ~320 credits/month
- Occasional agent run for deep extraction: 200-500 credits per run

Running both weekly scans plus one agent run per month will typically exhaust the free tier. If a user consistently needs more than 500 credits per month, they should contact the Fourth AI Enablement Team about paid-tier upgrade options.

**Fourth does not subsidize individual paid Firecrawl accounts by default.** Upgrade decisions are handled case-by-case between the user and the Fourth AI Enablement Team.

## Per-user, not shared

Each user's Firecrawl account is individual. Credits are tied to the API key or OAuth session that authenticated the CLI. There is no cross-user pooling.

Usage analytics and credit history are visible in the user's own Firecrawl dashboard at firecrawl.dev/app — no one at Fourth can see another user's usage unless that user grants explicit access through Firecrawl's own account-sharing features.

## Agent self-check pseudocode

Before any `firecrawl agent` call, the skill should run this check:

```
status = run "firecrawl --status"
remaining = parse "Credits: N remaining" from status output

estimated_cost = --max-credits value for this run (or 500 if not set)

if estimated_cost > (0.50 * remaining):
    refuse — suggest smaller alternative, surface remaining balance
elif estimated_cost > (0.25 * remaining):
    ask user for confirmation before proceeding
else:
    proceed
```

If `firecrawl --status` fails or the credits line cannot be parsed, surface the error and stop. Do not proceed with an expensive operation when quota cannot be verified.
