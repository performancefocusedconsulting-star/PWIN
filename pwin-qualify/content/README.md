# Qualify Content System

This directory holds the **single source of truth** for everything that drives the Qualify product's scoring and AI behaviour: questions, rubrics, persona, opportunity-type calibration, and the rebid modifier layer.

Both Qualify HTML apps — the consulting standalone ([pwin-qualify/docs/PWIN_Architect_v1.html](../docs/PWIN_Architect_v1.html)) and the website MVP ([bidequity-co/qualify-app.html](../../bidequity-co/qualify-app.html)) — load their content from this directory at build time. They share one scoring brain. UX, branding, and feature flags can drift freely between them; the intelligence cannot.

## Files

- **`qualify-content-v0.1.json`** — the canonical content. Versioned semver. This is the file you edit when tuning rubrics, signals, persona triggers, or calibration.
- **`build-content.js`** — Node script that injects the JSON into both HTML apps between sentinel markers. Idempotent. Has a `--check` mode that fails if the apps are out of sync.
- **`eval-harness.js`** — Node script that runs each fixture through the live API and diffs against expected verdicts. Use before publishing a new content version.
- **`eval-fixtures/`** — JSON fixtures with expected verdicts. The harness reads these. See `eval-fixtures/README.md` for the schema.

## What you can tune

The four areas designed for iteration:

| Area | Where it lives in the JSON | When to edit |
|---|---|---|
| **Rubric bands** | `questionPacks.standard.questions[].rubric` and `modifiers.incumbent.addsQuestions[].rubric` | When the threshold for Strongly Agree / Agree / Disagree should sharpen or soften |
| **Inflation signals (per-question)** | `questionPacks.standard.questions[].inflationSignals` | When you spot a phrase the AI should auto-flag for that question |
| **Persona workflow triggers** | `persona.workflowTriggers.{autoChallenge, autoQuery, calibrationRules, inflationTriggers}` and `modifiers.incumbent.addsPersonaTriggers.*` | When you want a rule that applies across questions (TCV-based, stage-based, etc.) |
| **Opportunity-type calibration** | `opportunityTypeCalibration.{BPO, IT Outsourcing, ...}` | When sector/type-specific guidance for Alex needs sharpening |

## What NOT to tune (for now)

- **Question and category weights** (`qw`, `categories[].weight`, `weightProfiles`) — the user has confirmed these are stable. Changing them re-balances the entire scoring model and breaks fixture comparisons. If you need to change weights, plan a major version bump and re-baseline the eval fixtures.

## The publishing workflow

```
edit JSON → bump version → fill changelog → run eval harness → review diff → run build → commit → push
```

### Step 1 — Edit the JSON

Open `qualify-content-vX.Y.json` (the latest version). Make your changes inside the four tunable areas above. Save.

### Step 2 — Bump the version and add a changelog entry

Bump the `version` field at the top of the file:

- **Patch (0.1.0 → 0.1.1)** — wording polish, no behavioural change expected
- **Minor (0.1.0 → 0.2.0)** — new signal/trigger/calibration rule, expected to change verdicts on some fixtures
- **Major (0.1.0 → 1.0.0)** — schema change, weight rebalance, or new question pack/modifier

Add a changelog entry:

```json
"changelog": [
  {
    "version": "0.2.0",
    "date": "2026-04-15",
    "author": "your name",
    "notes": "Sharpened R4 rubric — Strongly Agree now requires named contact within 60 days (was 90 days). Added inflation trigger RI-5 for 'we go way back' phrases."
  },
  { /* prior entries below */ }
]
```

If you've made a substantive change, **rename the file** to match the new version (`qualify-content-v0.2.0.json`) so the previous version stays on disk for rollback. The build script always uses the latest semver-sorted file.

### Step 3 — Run the eval harness

```bash
ANTHROPIC_API_KEY=sk-... node pwin-qualify/content/eval-harness.js
```

The harness runs every fixture through the live API and reports each as PASS or FAIL. If a fixture you didn't intend to change starts failing, your change had a wider effect than expected — investigate before publishing.

If you intentionally changed a fixture's expected outcome (because the new rule corrected what was previously a wrong verdict), update the fixture file and re-run.

If a totally new behaviour is introduced, **add a new fixture** that exercises it. The eval suite should grow with every meaningful tune.

### Step 4 — Review the diff manually

Even with the harness passing, eyeball at least one full Alex review against each affected fixture. The harness checks structured fields (verdict, inflationDetected, suggestedScore) but not narrative quality.

### Step 5 — Run the build script

```bash
node pwin-qualify/content/build-content.js
```

This injects the new JSON into both HTML apps between the `// <QUALIFY_CONTENT_BEGIN>` … `// <QUALIFY_CONTENT_END>` sentinels. The script is idempotent — running it twice in a row reports "unchanged" the second time.

To verify both apps are synchronised with the latest content without modifying them:

```bash
node pwin-qualify/content/build-content.js --check
```

This exits with code 1 if either app is out of sync.

### Step 6 — Commit and push

```bash
git add pwin-qualify/content/qualify-content-vX.Y.json \
        pwin-qualify/docs/PWIN_Architect_v1.html \
        bidequity-co/qualify-app.html

git commit -m "Tune: <one-line summary of what you changed and why>"

git push
```

Both HTML files MUST be committed alongside the JSON. They are derived but not auto-built — the next CI run, deploy, or fork won't have access to the JSON unless the embedded sentinel block is committed.

## Architecture notes

### Why both apps inline the JSON instead of fetching it

The two Qualify apps must work as standalone HTML files with no server dependency. A runtime fetch would require either bundling the JSON with the app (which is what inlining does anyway) or hosting it on a CORS-enabled endpoint. Inlining at build time gives the same result with one less moving part.

### Why the rebid module is a "modifier" not a separate question pack

The rebid spec activates 12 additional questions, additional persona rules, and an additional output schema **on top of** the standard 24 — it is additive, not a replacement. Modelling it as a `modifier` (with `addsCategory`, `addsQuestions`, `addsPersonaTriggers`, `addsOutput`) keeps the standard pack intact and lets the modifier be conditionally activated based on context. The same modifier mechanism will accommodate future layers (challenger position, framework call-off, etc.) without further structural change.

### Why brand colors are NOT in the content file

The two apps have different visual identities (Midnight Executive vs BidEquity brand). Putting colors in the content file would force a single colour palette on both. Instead, each app declares its own `CAT_BRAND` constant in the hydration block, and the content file owns names, weights, and order. This is the *only* place per-app drift is allowed in the scoring layer.

### Sentinel format

The build script looks for and replaces this exact pattern in each HTML file:

```js
// <QUALIFY_CONTENT_BEGIN v0.1.0>
// AUTO-GENERATED ...
// Source: ...
const QUALIFY_CONTENT = { ... };
// <QUALIFY_CONTENT_END>
```

The hydration block (which references `QUALIFY_CONTENT`) is anchored by `// QUALIFY CONTENT HYDRATION` directly below the sentinel. The build script's anchor regex looks for that header — if you ever rename or move it, update [build-content.js](build-content.js) too.

## Smoke test

There's no committed smoke test, but a useful one (run from repo root) verifies both apps' hydration blocks evaluate cleanly under Node:

```bash
python3 -c "
import re, subprocess, tempfile, pathlib
for path in ['pwin-qualify/docs/PWIN_Architect_v1.html', 'bidequity-co/qualify-app.html']:
    src = pathlib.Path(path).read_text()
    scripts = re.findall(r'(?is)<script[^>]*>(.*?)</script>', src)
    body = '\n'.join(scripts)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(body)
        tmp = f.name
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    print(f'{path}: {\"OK\" if r.returncode == 0 else \"SYNTAX ERROR\"}')"
```

## Troubleshooting

**Build script complains "Cannot find injection anchor"** — the `// QUALIFY CONTENT HYDRATION` header has been deleted or renamed in one of the HTML files. Restore it from git or re-run the patcher.

**App throws "QUALIFY_CONTENT not loaded" at runtime** — the build script never ran, or the sentinel block was deleted. Run `node pwin-qualify/content/build-content.js` to inject.

**Eval harness reports unexpected failures after a tune** — your change had a wider effect than intended. Either:
1. Revert and try a more targeted change, or
2. Update the affected fixtures' expected outcomes (only if the new behaviour is correct), or
3. Investigate why the trigger fires too broadly (often a substring match where you wanted exact match).

**Both apps are out of sync (`--check` fails)** — someone edited one of the HTML files by hand inside the sentinel block. Re-run `build-content.js` to resync from the JSON.
