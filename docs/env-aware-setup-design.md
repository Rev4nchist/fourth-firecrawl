# Environment-Aware Setup & Execution - Design

Plugin: `fourth-firecrawl`
Version target: v1.1 (HTTP-first, Cowork-compatible)
Author: architect-agent
Created: 2026-04-20
Status: DESIGN (implementation happens in the kraken phase)

---

## 1. Problem statement

Today the plugin assumes a local Claude Code CLI shell: it tells users to `npm install -g firecrawl-cli`, authenticate with `firecrawl login --browser`, and routes every skill through the CLI. Phase 1 research (see `references/firecrawl-http-api-spec.md`) established that none of these preconditions are satisfiable in **Cowork** - the hosted, non-root, headless environment for Claude Code on the Web - because (a) `npm install -g` fails with EACCES against `/usr/lib/node_modules`, (b) Firecrawl's PKCE + browser login requires a desktop browser on the same machine, and (c) Firecrawl does not offer RFC 8628 device-code OAuth. Every Firecrawl verb we use has a 1:1 HTTP endpoint at `https://api.firecrawl.dev/v2/*`, so the rewrite is feasible. This doc specifies how the plugin detects its environment, how `/fourth-firecrawl:setup` branches, whether skills carry dual code paths or collapse to HTTP-only, and how we preserve per-user credit accountability when Firecrawl's API exposes no account-identity endpoint.

---

## 2. Environment detection

### 2.1 What we actually know about the runtime environments

Two environments matter for v1.1. A third ("unknown") is the safe fallback.

| Environment | What is set / true | Source of confidence |
|---|---|---|
| **Local Claude Code CLI** | `CLAUDECODE=1`, `CLAUDE_CODE_ENTRYPOINT=cli`, `CLAUDE_CODE_EXECPATH` points at local binary; user has normal shell; `npm -g` usually works; a desktop browser is usually reachable (`$DISPLAY` set on Linux, `open`/`start` exist on macOS/Windows). | Verified by inspecting our own live shell. These vars are set by the CLI itself when it launches the Bash tool. |
| **Cowork (Claude Code on the Web)** | Headless, non-root Linux sandbox. Bubblewrap-isolated on Linux per Claude Code's documented sandbox model. No desktop browser. `npm install -g` fails EACCES. | Inferred from (a) Claude Code sandbox docs at `docs.claude.com/en/docs/claude-code/sandboxing` referencing bubblewrap / Seatbelt isolation and (b) the problem statement's empirical findings. **Unverified**: no public doc confirms a stable, Cowork-specific env var name like `CLAUDE_COWORK=1`. Confirmed env vars that may appear: `CLAUDE_CODE_SANDBOXED` (surfaced by Claude Code docs site search), possibly `CLAUDE_CODE_BUBBLEWRAP` on Linux. |
| **Unknown** | CI jobs, Docker containers, dev containers, SSH sessions without any `CLAUDE_*` vars set. | Any shell we can't positively identify. |

Because we **cannot** assume a single Cowork env marker exists (and Anthropic may rename it), the detector must be layered: positive signals first, each with a confidence score, then a final "default to local-cli" fallback that prioritizes safety over auto-magic.

### 2.2 Signals

Ordered by strength. A positive hit at priority 1 wins; otherwise combine priorities 2-4.

| # | Signal | What it suggests | Notes |
|---|---|---|---|
| 1 | `CLAUDE_COWORK=1` or `CLAUDE_CODE_COWORK=1` env var set | Cowork (high confidence) | **Speculative** - no doc confirms this name. We check anyway so the plugin "just works" if Anthropic adds it. Cheap and forward-compatible. |
| 2 | `CLAUDE_CODE_SANDBOXED` truthy **or** `/run/.containerenv` exists **or** `/.dockerenv` exists **or** `cat /proc/1/cgroup` contains `bubblewrap`/`bwrap` | Sandboxed Linux environment (likely Cowork) | All four are real markers used by bubblewrap/podman/docker. `/proc/1/cgroup` inspection is the conventional way to detect sandboxing. |
| 3 | Non-root + `/usr/lib/node_modules` not writable + `$HOME` under `/home/<nonroot>` | Constrained shell | Dry-run check: `touch /usr/lib/node_modules/.fc-probe && rm $_` inside a subshell with `2>/dev/null`. Non-destructive on success (we remove it); silent failure on Cowork. |
| 4 | No desktop browser: none of `$DISPLAY`, `$WAYLAND_DISPLAY`, `$BROWSER` set **and** none of `open`, `xdg-open`, `start`, `cygstart` on PATH | Headless | Exactly the precondition that breaks `firecrawl login --browser`. |
| 5 | `CLAUDECODE=1` **and** `CLAUDE_CODE_ENTRYPOINT=cli` **and** `CLAUDE_CODE_EXECPATH` exists | Local Claude Code CLI on user's own machine | Verified on our Windows workstation. These vars come from the CLI. |
| 6 | `firecrawl` already on PATH (`command -v firecrawl`) | Local, pre-CLI-installed user | Only useful once; doesn't distinguish Cowork-with-manual-install (unlikely but possible on a persisted workspace). |


### 2.3 Detection function (pseudocode)

```
def detect_environment() -> "cowork" | "local-cli" | "unknown":
    # Priority 1: explicit Cowork env var (future-proof)
    if env_truthy("CLAUDE_COWORK") or env_truthy("CLAUDE_CODE_COWORK"):
        return "cowork"

    # Priority 2: sandbox markers (real and observable today)
    sandbox_markers = [
        env_truthy("CLAUDE_CODE_SANDBOXED"),
        file_exists("/run/.containerenv"),
        file_exists("/.dockerenv"),
        proc_cgroup_contains_any(["bubblewrap", "bwrap", "docker", "containerd"]),
    ]
    if any(sandbox_markers):
        # Sandbox confirmed. Distinguish Cowork from a user's local dev container.
        # Heuristic: Cowork ALSO has no browser AND cannot npm install -g.
        if (not has_desktop_browser()) and (not can_npm_global_install_dryrun()):
            return "cowork"
        # Sandboxed but with browser/npm means a user-local container, fall through.

    # Priority 3: combined "headless + constrained" without explicit sandbox marker
    if (not has_desktop_browser()) and (not can_npm_global_install_dryrun()):
        return "cowork"     # duck-typed Cowork

    # Priority 4: positive local CLI signal
    if env_truthy("CLAUDECODE") and env_truthy("CLAUDE_CODE_ENTRYPOINT", expected="cli"):
        return "local-cli"

    # Priority 5: fall through - we couldn't positively identify anything
    return "unknown"

def env_truthy(name, expected=None):
    v = os.environ.get(name, "")
    if expected is not None: return v == expected
    return v not in ("", "0", "false", "no")

def has_desktop_browser():
    if any_env(["DISPLAY", "WAYLAND_DISPLAY", "BROWSER"]): return True
    return any_on_path(["open", "xdg-open", "start", "cygstart"])

def can_npm_global_install_dryrun():
    # Best test: try to write a probe file to the npm global prefix.
    # Never actually run `npm install -g`.
    prefix = run("npm config get prefix", timeout=3).stdout.strip()
    if not prefix: return False
    probe = f"{prefix}/lib/node_modules/.fc-write-probe"
    try:
        open(probe, "w").close(); os.remove(probe); return True
    except OSError:
        return False

def proc_cgroup_contains_any(needles):
    try:
        with open("/proc/1/cgroup") as f: body = f.read()
        return any(n in body for n in needles)
    except OSError:
        return False   # not Linux or unreadable
```

**Implementation note:** the detector runs **once per session**, at the start of `/fourth-firecrawl:setup` and at the start of any skill that needs Firecrawl. Cache the result in `.firecrawl/.env-detected` (or a module-level variable inside a helper script) so we don't re-probe on every bash example.

### 2.4 Failure modes

| Wrong result | What the user sees | How bad |
|---|---|---|
| Detected as `cowork` when actually local-CLI | Setup prompts for an API key instead of offering browser OAuth. User can still paste a key - nothing breaks. | **Low severity.** Small UX regression; user has agency to override. |
| Detected as `local-cli` when actually Cowork | Setup tries `npm install -g`, gets EACCES, tries `firecrawl login --browser`, hangs waiting for a browser that never opens. User sees confusing errors. | **High severity.** This is the worst failure. Must make sure the detector is biased toward `cowork` when any Cowork-ish signal fires. |
| Detected as `unknown` | Setup asks the user: "Are you in Cowork or a local shell?" and branches on their answer. | **Acceptable.** Explicit is fine; CI users self-identify. |

The detector is intentionally biased: priority 2 and 3 short-circuit to `cowork` on any sandbox/headless/constrained signal. False-positive Cowork is cheap (the user types a key); false-negative Cowork is expensive (broken setup).

### 2.5 Recommendation

Ship the layered detector above. Document the uncertainty about `CLAUDE_COWORK` in the commit message and add a note in `CHANGES-FROM-UPSTREAM.md` so that if Anthropic later publishes an official Cowork marker, upgrading is a one-line change. Also expose an override: `FOURTH_FIRECRAWL_ENV=cowork|local-cli` that forces a specific branch, for CI and for debugging.

---

## 3. Setup flow - Cowork path

### 3.1 Step-by-step

1. **Detect environment** -> `cowork`. Set internal flag.
2. **Skip CLI install attempt entirely.** Do not shell out to `npm install -g` - guaranteed failure and wasted time.
3. **Check for an existing key** in this priority order:
   a. `FIRECRAWL_API_KEY` env var set this session?
   b. `.firecrawl/.env` exists and contains `FIRECRAWL_API_KEY=fc-...`?
   c. Neither -> prompt the user.
4. **If prompting:** Display the getting-a-key guidance (see 3.2 chat text below), then ask the user to paste their key. Accept pasted text that starts with `fc-`; reject anything else with "That does not look like a Firecrawl key (`fc-` prefix expected). Paste again?".
5. **Verify the key** with one request:
   ```
   GET https://api.firecrawl.dev/v2/team/credit-usage
   Authorization: Bearer fc-<key>
   ```
   Parse `body.success === true && body.data.remainingCredits` to confirm. On any 4xx, surface the error (401/403 -> "Invalid key"; 404 -> "API unreachable - check network"; other -> show status + body).
6. **Persist for the session**: export `FIRECRAWL_API_KEY` in the running shell (via `. .firecrawl/.env` or inline `export`). Document that it lives only for the current Cowork session.
7. **Offer optional dotfile persistence** (see 3.3): one-liner the user can re-run if they want the key to survive Cowork session restarts within the same sandbox, with clear security caveats.
8. **Display identity + balance card:**
   ```
   Authenticated.
     Key fingerprint: fc-...abc1
     Credits:        487 remaining (Free tier, resets monthly)
     Env:            Cowork (headless)
   ```
9. **Print three example invocations**, one per Fourth skill:
   - `Research R365 pricing` (competitor-intel)
   - `Scan hospitality news for tipping trends this week` (market-scan)
   - `What topics are 7shifts covering that Fourth isn't?` (content-gap-analysis)

### 3.2 Example chat / prompt text (Cowork)

```
Welcome to fourth-firecrawl. I detect this is a Cowork session - headless and
sandboxed, so no CLI install or browser login. All Firecrawl access will go
over HTTPS directly.

Step 1 - get a free API key:
  1. On your laptop, open https://firecrawl.dev/app/api-keys
  2. Sign in (or register - free, 500 credits/month)
  3. Create a new key named something like "fourth-cowork-2026"
  4. Copy the key (it looks like fc-abc123...)

Step 2 - paste it here. I will only store it for this session unless you
explicitly opt in to dotfile persistence. The key will never be printed in
full; I will verify it once and then keep it out of logs.

Paste your key:
```

After paste:

```
Verifying...
  GET https://api.firecrawl.dev/v2/team/credit-usage -> 200 OK

Authenticated.
  Key fingerprint: fc-...abc1
  Credits:        487 remaining
  Env:            Cowork (session-scoped)

The key is in memory for this turn. Next turn in this session, the
FIRECRAWL_API_KEY env var may or may not persist - Cowork's env-var
behavior across turns is not documented (see Open Questions). If the
plugin asks you to paste again later, that is expected.

Optional: persist across turns by writing to `.firecrawl/.env` (gitignored).
Say "persist the key" and I will create the file. Tradeoff: any sandbox
tool that reads `.firecrawl/` sees the key.

Try one of these to start:
  1. "Research R365 pricing"
  2. "Scan hospitality news for tipping trends this week"
  3. "What topics are 7shifts covering that Fourth isn't?"
```

### 3.3 Cowork-specific open questions surfaced in this flow

- **Env persistence across turns.** Unclear whether `export FIRECRAWL_API_KEY=...` inside one Bash tool call survives to the next tool call in the same Cowork session. Our best guess is **no** (each Bash tool call is often a fresh shell), but behavior may differ between turns and between sessions. If it does not persist, the dotfile path in `.firecrawl/.env` is the practical workaround. **Flagged in Open Questions sec 8.**
- **Dotfile security.** Writing the key to `.firecrawl/.env` is convenient but means any tool call that `cat`s that directory could leak the key into the transcript. Mitigation: gitignore (already done for `.firecrawl/`), never `cat` the file in diagnostic output, and document the risk explicitly so the user chooses.
- **Paste visibility in the transcript.** The API key appears in the chat transcript when pasted. That is unavoidable for v1.1 - Cowork does not offer a secret-input widget for plugins today. Mitigation: recommend the user rotate the key after the session if the transcript is shared.

---

## 4. Setup flow - Local CLI path

### 4.1 Step-by-step

1. **Detect environment** -> `local-cli`.
2. **Check CLI availability.** `command -v firecrawl`. If missing -> offer:
   ```
   firecrawl-cli is not installed. Install globally?
     npm install -g firecrawl-cli@1.14.8
   Proceed? [y/N]
   ```
   On failure (EACCES or similar), fall back to user-prefix install:
   ```
   Global install failed. Try user-prefix install:
     npm install --prefix ~/.local firecrawl-cli@1.14.8
     export PATH="$HOME/.local/bin:$PATH"
   ```
   If both fail, gracefully downgrade to the Cowork/HTTP path (paste-a-key) with a note: "Falling back to HTTP mode because CLI install failed."
3. **Run `firecrawl --status`.** Parse output for:
   - "Authenticated" line + "Credits: N remaining"
   - OR "Not authenticated" / error -> go to step 4.
4. **Offer auth flow:**
   - **Option A (default):** `firecrawl login --browser` - launches OAuth in the user's browser.
   - **Option B (fallback):** if `--browser` fails (no browser available despite local detection; rare edge case), prompt for key paste same as Cowork path, then `firecrawl login --api-key fc-...`.
   - **Option C (power user):** user already has `FIRECRAWL_API_KEY` in their shell profile - `firecrawl --status` will pick it up automatically.
5. **Verify with a tiny HTTP call, not a scrape.** Why: a tiny scrape burns 1 credit. `GET /v2/team/credit-usage` is free and equally definitive. Replaces the current `firecrawl scrape https://firecrawl.dev` smoke test at the end of setup. (This is a change from the v1.0 setup - worth preserving the test scrape as an optional extra step if the user wants to prove end-to-end output writing to `.firecrawl/`.)
6. **Display the same identity + balance card** as Cowork (keep the UX unified):
   ```
   Authenticated.
     Key fingerprint: fc-...abc1     (or: "via browser OAuth")
     Credits:        487 remaining
     Env:            Local (CLI available)
   ```
7. **Print the same three example invocations.**

### 4.2 What is different vs. Cowork path

- CLI install is attempted (not skipped).
- Browser OAuth is offered as the primary auth method.
- `firecrawl --status` is still usable as a diagnostic tool later, and the credit-budget rule can keep using it.
- The smoke-test scrape at the end is optional, not mandatory (saves 1 credit on first run).

---

## 5. Skill execution model

### 5.1 The options revisited

- **Option A - HTTP-first everywhere.** All 4 Fourth skills and all 8 upstream firecrawl-* skills get rewritten to call `https://api.firecrawl.dev/v2/*` directly (via `curl` or a tiny node wrapper). CLI stays available to users who happen to have it installed, but no skill depends on it. One code path.
- **Option B - Branch per skill.** Each skill detects env and runs CLI OR HTTP. Two code paths x 12 skills = 24 execution paths. Preserves CLI UX for local users.
- **Option C - Mixed.** Fourth skills (the 4 we added) go HTTP-first. Upstream firecrawl-* skills (the 8 we preserved unchanged) stay CLI-only. Local users get both; Cowork users only get the 4 Fourth skills.

### 5.2 Trade-off analysis

| Criterion | Option A (HTTP-first) | Option B (branch) | Option C (mixed) |
|---|---|---|---|
| Works in Cowork | Yes, all 12 skills | Yes, all 12 skills | Only 4 of 12 |
| Lines of skill code | ~1.0x current | ~1.6x current | ~1.2x current |
| Merge burden when upstream updates firecrawl-* | High (we diverge on every skill) | Medium (we add branches) | Low (upstream-as-is) |
| Local CLI UX (`firecrawl scrape ...` in transcript) | Lost from skill examples, but CLI still works standalone | Preserved | Preserved for upstream skills |
| Surface area for bugs | Small (one code path) | Large (two code paths x 12 skills) | Medium |
| Onboarding complexity | Low | High | Medium |
| Credit-budget enforcement | Must reimplement `--max-credits` for /crawl client-side (HTTP spec 4.2 confirms no server-side budget on crawl) | CLI handles it on local path; reimplement only on HTTP branch | Local path uses CLI; HTTP path reimplements |

### 5.3 Recommendation: **Option A (HTTP-first everywhere)**

Rationale, in priority order:

1. **Cowork coverage is the whole point of v1.1.** Option C ships a product that literally does not work for 8 of 12 skills in Cowork. That is untenable - users who "research R365 pricing" today can, but users who say "scrape this arbitrary URL" (routing them to `firecrawl-scrape`) can't. The routing table in `references/routing.md` actively directs users to upstream skills.
2. **Single code path means fewer bugs.** Option B doubles the skill execution surface area for a UX win (keeping `firecrawl scrape` in example boxes) that accrues to power users who can install the CLI independently anyway.
3. **Merge burden is manageable.** The upstream skills we preserved unchanged are markdown files with bash snippets. Rewriting the bash snippets to `curl` / node one-liners is mechanical (see 5.4) and the skills' prose, workflow decisions, and references all stay. We already diverged from upstream via the `CHANGES-FROM-UPSTREAM.md` boundary, so a second divergence is not structurally new.
4. **The CLI is not going away for users who want it.** Users can still `npm install -g firecrawl-cli` on their own local shell and run `firecrawl scrape ...` outside Claude Code. What changes: the plugin's skills no longer require it.
5. **The HTTP spec is complete.** Phase 1 confirmed every verb has a 1:1 endpoint, including agent and crawl (with a small client-side helper for `--max-credits`). No capability is lost.

**Trade-off accepted:** upstream firecrawl/firecrawl-claude-plugin will drift further from our fork. We accept that - we already forked intentionally. If upstream adds a feature we want, we port the idea, not the code verbatim.

### 5.4 How to invoke HTTP from inside a skill's bash snippet

Constraints:
- Cowork's sandbox is non-root but has standard Linux tooling.
- We cannot rely on `jq` being installed in every Cowork image (unverified). We can rely on `node` (Claude Code needs it).
- `python` may or may not be present on the Cowork sandbox (unverified; Claude Code historically ships Node only).

Candidates:

| Tool | Pros | Cons |
|---|---|---|
| `curl` + `jq` | Terse, idiomatic | `jq` not guaranteed on Cowork |
| `curl` + `node -e` for parsing | Terse, guaranteed runtime | Multi-step, two processes |
| `node` with `fetch` (node >=18) | Single process, guaranteed runtime, promise-native | Bash examples look less "shell-y" |
| `python3 -c "import urllib.request..."` | Portable if Python is present | Python presence unverified on Cowork |

**Recommendation:** a shared `scripts/firecrawl-http.mjs` wrapper that exposes the 6 verbs (scrape/search/map/crawl/agent/credits) as CLI commands. One node file, one code path, zero dependencies beyond what Claude Code already has. Skills call it like:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/firecrawl-http.mjs" scrape \
  --url "https://restaurant365.com/pricing" \
  --formats markdown,links \
  --only-main-content \
  -o .firecrawl/competitor-intel/r365-pricing-$(date +%Y%m%d).md
```

This keeps skill-level bash snippets short and swap-in-compatible with the current `firecrawl scrape ...` lines - the kraken rewrite becomes largely a find/replace on command names plus flag normalization. **Implementation-side note:** the shared wrapper is also where we reimplement the `--max-credits` guard for `/crawl` (per HTTP spec 5).

### 5.5 Fallback rule update

Today's routing.md has a hard fail-stop: "if `firecrawl --status` fails, STOP and tell user to run setup." Rewrite this to be env-aware:

> **Preflight:** hit `GET /v2/team/credit-usage`. If it fails with 401/403, the key is invalid or missing - tell the user to re-run `/fourth-firecrawl:setup`. If it fails with a network error, surface the error and stop. Do not fall back to WebFetch/WebSearch.

Same spirit, different probe. Works in both environments.

---

## 6. Credit accountability design

### 6.1 The identity gap

Firecrawl's API exposes `remainingCredits`, `planCredits`, `billingPeriodStart`, `billingPeriodEnd` - but not team name or user email (spec 2.6). The only endpoint that returns identity is `/admin/integration/validate-api-key`, gated to referred-integration partners. We can't use it.

### 6.2 What we display instead

Three ingredients combine into the accountability string:

1. **Key fingerprint** - last 4 chars of the key. `fc-abc123def456` -> `fc-...f456`. Unambiguous enough that a user can tell which of their keys is loaded; low enough entropy that it's not a credential.
2. **Optional user-chosen label** - during setup, prompt (optionally): "Give this key a friendly name (e.g., 'david-laptop', 'cowork-2026-q2'). This is stored locally, never sent to Firecrawl." Stored in `.firecrawl/key-label` (plain text, the key is not in this file).
3. **Credit balance** - from the credit-usage endpoint. Cached for 60 seconds so we don't hammer the endpoint on every skill call.

### 6.3 Display format

```
Key fingerprint:  fc-...f456   (label: david-laptop)
Credits:          487 remaining (Free tier)
Last checked:     2026-04-20 14:32 UTC (12s ago)
```

If no label is set:

```
Key fingerprint:  fc-...f456
Credits:          487 remaining
Last checked:     2026-04-20 14:32 UTC
```

Show this card:
- After successful setup verification.
- At the start of any skill run (one-line version: `Running competitor-intel as fc-...f456 · 487 credits`).
- On demand: a new slash command `/fourth-firecrawl:whoami` that prints the card.

### 6.4 Why this is enough accountability

The "burning credits for: <user>" line today is social, not cryptographic - nobody's authenticating anything, they're answering the question "did *I* just spend 500 credits or did someone else's key leak into my session?". The fingerprint + label covers that case. If the user sees `fc-...xyz9` and they know their key ends in `f456`, something is wrong and they can rotate.

---

## 7. Key safety policy

Rules the plugin (every skill, every helper, every log message) must obey:

- **Never log the full key.** Not in error messages, not in verbose-mode output, not in `.firecrawl/` files. Only the last-4 fingerprint is ever printed.
- **Never include the key in `curl -v` output reaching the transcript.** The `Authorization: Bearer fc-...` header is sensitive. If the helper needs to show a debug URL, it redacts the bearer: `Authorization: Bearer fc-***...f456`.
- **Never echo the key back on paste.** When the user pastes during setup, confirm with the fingerprint only: "Got it - fc-...f456. Verifying..." Not "Got it - fc-abc123def456f456."
- **Error messages omit the key.** Parse HTTP errors and surface the status code + server error text, never the request headers.
- **`.firecrawl/.env` is gitignored by default.** The plugin adds `.firecrawl/` to `.gitignore` if the project is a git repo and doesn't already ignore it. Document the gitignore behavior in the setup output.
- **`.firecrawl/.env` is file-mode 0600 when created** (Linux/macOS). On Windows, we best-effort `icacls` to restrict to the current user; if that fails, warn the user.
- **Rotate-on-suspect advisory.** If the user mentions in chat that they shared their transcript, Claude should remind them: "Your API key was typed in this session. If this transcript will be shared outside Fourth, rotate the key at firecrawl.dev/app/api-keys before sharing."
- **No cross-session key leak detection.** Detecting whether the same fingerprint is used by two different users would require a server we don't have. Out of scope for v1.1.
- **Helper wrapper script reads `FIRECRAWL_API_KEY` from env only.** Never from arguments. This prevents keys from showing up in `ps`, shell history, or the Bash tool's command transcript.
- **No telemetry.** The plugin sends nothing to Fourth; it sends only what the user's request requires to Firecrawl.

---

## 8. Open questions

Prioritized. The #1 item needs a decision before kraken starts.

1. **[BLOCKING for Cowork UX polish]** Does `export FIRECRAWL_API_KEY=...` in one Bash tool call persist to the next tool call in the same Cowork session? Empirical test needed (spin up a Cowork session, export a var, read it in the next turn). **Recommended decision path:** assume NOT persistent and default to re-pasting per-session. Offer dotfile persistence as an explicit opt-in. If persistence does exist, document as a bonus feature later.
2. **Where does `.firecrawl/.env` live across Cowork sessions?** If the Cowork sandbox is reset between sessions, the dotfile persistence is moot - the file won't survive. If the sandbox is persistent per user, the dotfile path works. Needs empirical test. Mitigation until confirmed: always re-verify the key on each session start; if verification fails, prompt for paste.
3. **Is there a real `CLAUDE_COWORK` env var?** Today I did not find one documented. Mitigation: layered detector covers it either way. If Anthropic publishes one later, update priority 1 of the detector.
4. **Cowork network egress to `api.firecrawl.dev`.** Whether Cowork's sandbox permits outbound HTTPS to arbitrary domains is unverified. If it does not, the entire v1.1 plan fails - this is a prerequisite worth testing before any implementation. **Test:** `curl -I https://api.firecrawl.dev/v2/team/credit-usage` from a Cowork session. If 200 or 401, egress works.
5. **`python` availability in Cowork.** If `node` is guaranteed but `python3` is not, the wrapper must be pure node. **Recommendation:** commit to node-only in the wrapper, per 5.4.
6. **`jq` availability in Cowork.** Some of today's skills use `jq -r '.data.web[].url' .firecrawl/search.json`. If `jq` is missing, rewrite these to `node -e` one-liners. Low risk; node is available.
7. **Does the CLI respect `FIRECRAWL_API_KEY` if we set it post-install?** Relevant to the local-cli path if we let users paste a key rather than browser-OAuth. The CLI docs say yes, but worth confirming empirically.
8. **Rate-limit behavior in shared sandbox IPs.** Multiple Cowork users may share an egress IP. Firecrawl's rate limits are per-team/bearer, not per-IP (spec 4.5), but undocumented anti-abuse throttles may apply. Mitigation: nothing the plugin can do except handle 429 gracefully with exponential backoff. Already covered in spec 5.
9. **ToS compliance.** Spec 5 notes that Firecrawl's marketing explicitly targets AI agents, but no formal ToS clause was cited. Human legal review recommended before wide rollout to non-pilot Fourth team members.
10. **Paste visibility in transcript.** The user's key goes into the chat transcript when they paste. Accepted as an unavoidable v1.1 limitation; documented in 3.3.

---

## 9. Implementation hooks (for kraken)

Exact files the rewrite touches, with what changes:

### 9.1 New files to create

| Path | Purpose |
|---|---|
| `scripts/firecrawl-http.mjs` | Node wrapper exposing scrape/search/map/crawl/agent/credits as subcommands. Reads `FIRECRAWL_API_KEY` from env. Implements `--max-credits` client-side for crawl. One file, ~300-400 LOC. |
| `scripts/env-detect.mjs` | The detection function from 2.3. Emits `cowork`, `local-cli`, or `unknown` to stdout. Used by `/fourth-firecrawl:setup` and by the preflight check. ~80 LOC. |
| `scripts/setup-verify.mjs` | Verifies a pasted key via `GET /v2/team/credit-usage`. Returns fingerprint + credits or an error object. ~40 LOC. |
| `.firecrawl/.env.example` | Template showing `FIRECRAWL_API_KEY=fc-REPLACE-ME`. Gitignored. |
| `docs/env-aware-setup-design.md` | This doc. (Already created.) |

### 9.2 Files to modify

| Path | Changes |
|---|---|
| `commands/setup.md` | Full rewrite. Remove "Step 1: firecrawl --status" universality. Add "Step 0: detect environment" then branch into Cowork path (section 3) or Local CLI path (section 4). Keep the existing "Step 5: Available skills" block verbatim. Preserve the "do not request shared keys" advisory. |
| `QUICKSTART.md` | Rewrite the "First-time setup" and "Troubleshooting" sections to reflect env-aware branching. Keep the 5-minute first-run walkthrough unchanged (the example prompts do not mention CLI). Update the Credit Budget Basics section to show both `GET /v2/team/credit-usage` (HTTP way) and `firecrawl --status` (local CLI way). |
| `skills/firecrawl-cli/rules/install.md` | Mark CLI install as **optional, local-only enhancement**. Keep the instructions but reframe: "If you want the `firecrawl` command in your own shell, install it yourself - the plugin skills do not require it." Remove the "Quick Setup (Recommended)" npx line. |
| `skills/firecrawl-cli/rules/credit-budget.md` | Replace `firecrawl --status` references with "call `GET /v2/team/credit-usage`" (via the wrapper). Update the agent self-check pseudocode to read from the wrapper output, not CLI stdout parsing. Keep the threshold table (<25% / 25-50% / >50%) unchanged - that is business logic, not transport. |
| `references/routing.md` | Rewrite the "Preflight - authentication gate" section to use `GET /v2/team/credit-usage` instead of `firecrawl --status`. Keep the fallback rule ("do not silently substitute WebFetch") as-is. |
| `skills/competitor-intel/SKILL.md` | Replace each `firecrawl agent ...` and `firecrawl scrape ...` bash example with the node wrapper equivalent. Update the "Prerequisites" section: step 1 becomes "plugin setup is complete (see `/fourth-firecrawl:setup`)" instead of "firecrawl --status". Keep workflow, schemas, naming conventions untouched. |
| `skills/market-scan/SKILL.md` | Same shape of rewrite as competitor-intel. Replace `firecrawl search` examples with wrapper calls; keep trade-press catalog references. |
| `skills/content-gap-analysis/SKILL.md` | Same shape. Replace any CLI bash with wrapper calls. |
| `skills/kb-ingest-review/SKILL.md` | **Minimal change.** This skill does not call Firecrawl - it moves files between `.firecrawl/` and the KB MCP. Only update any lingering "check `firecrawl --status`" lines, if any. |
| `skills/firecrawl-scrape/SKILL.md` (upstream preserved) | Rewrite bash examples to use the wrapper. Preserve the prose. Note divergence in CHANGES-FROM-UPSTREAM.md. |
| `skills/firecrawl-search/SKILL.md` | Same. |
| `skills/firecrawl-map/SKILL.md` | Same. |
| `skills/firecrawl-crawl/SKILL.md` | Same. Additional: document that `--max-credits` is client-side-enforced by the wrapper (not a server-side API field). |
| `skills/firecrawl-agent/SKILL.md` | Same. Additional: the `--schema-file` behavior (read local JSON then pass as `schema` in request body) is implemented in the wrapper, matching what the CLI does today. |
| `skills/firecrawl-download/SKILL.md` | Same. |
| `skills/firecrawl-instruct/SKILL.md` | Probably no-op - this skill is meta, about how to use the other skills. Check for any lingering CLI references. |
| `skills/firecrawl-cli/SKILL.md` | Rewrite to be the "optional local-CLI extra" skill. Currently it is the umbrella skill that the other firecrawl-* skills hang off of. After the rewrite, it becomes a pointer to the wrapper plus "if you want the real CLI, install it yourself." |
| `CHANGES-FROM-UPSTREAM.md` | Add a new section "v1.1 - HTTP-first rewrite" listing the divergence from upstream: wrapper script added, CLI made optional, all bash examples rewritten. |
| `.gitignore` | Add `.firecrawl/` (may already exist) and `.firecrawl/.env`. Add explicitly even if `.firecrawl/` is already there - defense in depth. |

### 9.3 New slash commands to add

| Slash command | Purpose |
|---|---|
| `/fourth-firecrawl:whoami` | Print the identity + balance card (6.3). Calls `GET /v2/team/credit-usage`, displays fingerprint + label + credits. |
| `/fourth-firecrawl:persist-key` | (Optional.) Write the currently-loaded key to `.firecrawl/.env` with mode 0600. Shows the security caveats again before writing. |

### 9.4 Testing & verification plan (hand-off to arbiter)

Three tests the kraken phase must pass before marking v1.1 done:

1. **Cowork end-to-end.** Spin up a Cowork session. Run `/fourth-firecrawl:setup` then paste a valid key then run "Research R365 pricing" then verify `.firecrawl/competitor-intel/r365-pricing-YYYYMMDD.json` is written. Credits deducted matches the HTTP response. Key never appears in the transcript in full.
2. **Local CLI end-to-end.** Same machine we developed on. Run `/fourth-firecrawl:setup` then browser OAuth then run the same prompt then verify same output. Confirm detector returns `local-cli`. Confirm a stray `firecrawl --status` call still works as a diagnostic.
3. **Negative cases.** (a) Invalid key then setup surfaces clear error, does not crash. (b) Network blocked (simulate) then surface clear error. (c) Credits exhausted (mock 402) then credit-budget rule refuses gracefully. (d) Detector forced to `unknown` then setup asks the user.

---

## 10. Errata from HTTP API spec review

While writing this design I cross-read `references/firecrawl-http-api-spec.md`. Errata found:

- **Section 2.6 identity gap** - spec says the team name is surfaced only by the webapp login endpoint. Verified against the doc; no change needed. Just flagging that this is the precise blocker that forces the key-fingerprint approach in section 6.
- **Section 4.3 credit costs** - table shows `/agent` as "dynamic" with "5 free runs/day then usage-based." Worth double-checking in the billing docs before the kraken phase, because the credit-budget rule needs to handle the "5 free runs" case specifically (it is not a linear per-run cost for the first 5). No correction needed to the spec; just noting the implementation nuance.
- **Section 5 "No maxCredits on /crawl"** - confirmed; wrapper must poll and DELETE. Design 5.4 reflects this.
- No other errata.

---

## 11. Summary for the engineer

One paragraph for the kraken-phase implementer:

> Build a node wrapper at `scripts/firecrawl-http.mjs` that exposes scrape/search/map/crawl/agent/credits subcommands backed by the Firecrawl v2 HTTP API, reading `FIRECRAWL_API_KEY` from env. Build an env detector at `scripts/env-detect.mjs` using the layered signal set in section 2.3, biased toward returning `cowork` when in doubt. Rewrite `commands/setup.md` to branch on the detector: Cowork path = paste-a-key + verify via `/v2/team/credit-usage` + show fingerprint; Local-CLI path = same UX but offer `firecrawl login --browser` as primary. Rewrite every bash example in every skill to call the wrapper. Make the CLI officially optional. Enforce the key-safety rules in section 7 everywhere. Ship Option A (HTTP-first) - Options B and C were considered and rejected for the reasons in section 5.3. Before starting, test that `curl -I https://api.firecrawl.dev/v2/team/credit-usage` works from a Cowork session - that is the single blocking prerequisite.

---

## 12. Sources consulted

- `references/firecrawl-http-api-spec.md` - Firecrawl v2 HTTP API reference produced by Phase 1 oracle.
- `commands/setup.md` - current v1.0 setup flow (what we are replacing).
- `skills/firecrawl-cli/rules/install.md` - current install guidance (what we are deprecating).
- `skills/firecrawl-cli/rules/credit-budget.md` - current credit-budget rule (will be updated).
- `references/routing.md` - current preflight rule (will be updated).
- `QUICKSTART.md` - current first-run doc (will be updated).
- Claude Code docs: `docs.claude.com/en/docs/claude-code/sandboxing` - confirmed bubblewrap on Linux, Seatbelt on macOS, WSL2 on Windows. No public doc surfaced a stable `CLAUDE_COWORK` env var; `CLAUDE_CODE_SANDBOXED` and `CLAUDE_CODE_BUBBLEWRAP` appeared in web-search result snippets but were not verified in any authoritative doc page that renders server-side (the docs site is a client-rendered SPA).
- Direct env inspection of a live local Claude Code shell - confirmed `CLAUDECODE=1` and `CLAUDE_CODE_ENTRYPOINT=cli` are reliably set.
