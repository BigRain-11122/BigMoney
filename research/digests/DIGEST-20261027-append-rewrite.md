# A one-row append that rewrites the whole frozen panel (found in r1190)

**Trigger**: `python scripts/update_daily.py` reported `new rows: 3` — and `git diff
--numstat data/daily` answered **1651/1650, 1651/1650, 1650/1649** on the three core-ETF
panels. Three new bars, ~5,000 changed lines.

**Root cause** (scripts/update_daily.py `update_one`): the function's own docstring said
"never rewrites rows", but the implementation was

```python
merged = pd.concat([old[COLUMNS], new[COLUMNS]], ignore_index=True)
merged.to_csv(tmp, index=False)
```

`read_csv` → `to_csv` is a **float round-trip**, not a copy: the panel prints `4.1200`
and pandas writes `4.12`, so every row's text changes while every row's value does not.
The append was row-accurate and byte-destructive at the same time.

**Why it matters more than aesthetics**: `data/daily` is a frozen panel that several
freeze checks, blob comparisons and watermark faces read. A whole-file rewrite makes
every one of them report a panel-wide event for a one-bar arrival, and it makes
`git blame`/`git diff` useless on the only artefact that records what the book actually
priced. It also inflates the repo's churn and hides real history rewrites inside
formatting noise — the overlap-mismatch guard exists precisely to *not* rewrite history,
and the writer was doing it on every good day.

**Fix** (same file):
- `_panel_decimals(path)` reads the decimal places off the panel's own last data line.
- `_fmt_price(v, dp)` formats in that style **only when it round-trips exactly** — a
  panel printed at 1dp must not truncate a `4.35` source bar into `4.3` (the first
  version of this fix did exactly that and the selftest caught it).
- `update_one` now appends text: existing bytes are read and re-emitted verbatim, new
  rows are formatted and appended. `volume`/`amount` stay integers.
- selftest leg **C2** pins the property: after an append the file must still *start with
  the exact original text*, and the appended rows must carry the panel's style. Without
  that leg, block B ("append-only + idempotent") passes on the pandas version too — it
  checks rows, not bytes.

**Repair of the live damage**: the three panels were restored from HEAD and the three new
bars re-appended through the fixed writer. `git diff --numstat data/daily` now reads
`1 0` per file. A second `update_daily` run reports `new rows: 0` and leaves the files
untouched, so the fix is idempotent on a fresh panel.

**Generalisation**: "append-only" is a claim about **bytes**, not about rows. Any writer
whose test asserts `len(df)` and `df.iloc[-1]` after a read-back will pass while
rewriting every line. Assert `new_text.startswith(old_text)`.

Evidence: scripts/update_daily.py (selftest leg C2), data/daily/{510300,510050,159915}.csv
diff = 1 added line each, results/update_status.json.