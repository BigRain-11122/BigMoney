# QA — book_pair_cushion_regime (r2183, bm-c)

Round: 2183 · machine `bm-c` · generated 2026-11-27 · bars to 2026-11-26

## Why this round ran on new files only

`python Tools\repo_write_contention.py --lookback-min 45` returned **rc=3 CONTENTION**
(another interactive host, pid 132592, alive since 18:56:09; 6 shared faces written by
that host before this round started; 0 written inside the overlap). Under r1927/r1907
the round is therefore restricted to **new files**: no edits to `Tools/s6_chain_bmc.py`,
no edits to `smoke_test.py`, no S6 chain re-run. The two owed wires from r2181 are still
owed, and this file says so again rather than pretending they happened.

## What the face asks

r2179 found the 30/70 book cushions ETF drawdowns by 0.43pp a month on average; r2181 put
a band on that average. Both averaged over the whole overlap. Neither asked whether the
cushion survives when the convertible market is **expensive**, which matters because the
cb sleeve is the dual-low convertible book — a convertible is mostly a premium over parity,
so a rich market has less premium left to expand.

## Method (and the two places look-ahead could have crept in)

- parents imported, never rebuilt: cb = `cb_dual_low` n_hold=20/rebal=20/10bp,
  etf = `etf_nobond_vt` vol_target=8% n_hold=5 entry_lag=1; weight read from
  `results/book_pair_blend.json` `best.w_cb` = 0.30.
- regime = tertiles of the CB market's **median** conversion premium, read at the
  **previous month end**, edges from an **expanding** window (≥250 premium days).
  A selftest leg plants a future premium spike of 500 and asserts past labels do not move.
- the rule pays 10bp per side on the traded 30% share, and an unlabelled month (not enough
  premium history yet) stays **invested** — an unknown state is not evidence of a rich market.

## Numbers (from `results/book_pair_cushion_regime.json`)

| regime | months | falling months | cushion | upside given up |
|---|---|---|---|---|
| cheap | 6 | 3 | +0.26 pp | +1.19 pp |
| mid | 29 | 6 | +0.93 pp | −0.24 pp |
| rich | 46 | 22 | +0.25 pp | −0.70 pp |

- rich-minus-rest cushion difference **−0.46pp**, 95% band **−1.36 .. +0.65**, P(≤0)=0.81
  → **`CUSHION_DIFFERENCE_NOT_SEPARABLE`**: the cushion is the same in expensive months as
  in the rest; it is not a fair-weather property.
- the sample is one-sided: the CB market was rich in 46 of 81 labelled months, and the
  cheap side holds only **3** falling months. The cheap-vs-rich split is printed for the
  record and is **not** evidence.
- rule (cash in the cb sleeve while rich) vs always-on vs same-exposure control:
  9.97% / 9.29% / 8.15% CAGR, Sharpe **1.383 / 1.215 / 1.266**, maxdd **−4.37% / −8.96% / −5.16%**,
  11 switches, 0.33pp of cost.
- rule edge over its own exposure **+0.144 pp/month**, band **+0.018 .. +0.275**,
  P(≤0)=0.013 → `THE_RULE_BEATS_ITS_OWN_EXPOSURE`.
- **but** the whole edge is +11.64pp across 81 months and the 5 best months carry
  **64.7%** of it → it is a drawdown story, not a return story. Printed next to maxdd,
  not instead of it.

## Six self-catches this round (all found by running, not by reading)

1. `_verify` compared a stored verdict string to `verdict_of(...)`'s **tuple** — every face
   would have verified "drift". Fixed by taking `[0]`; the selftest caught it because the
   "consistent face must verify" leg failed on a face I believed was consistent.
2. Two selftest expectations were written wrong (a planted cushion of 1.50pp that the
   arithmetic makes 0.45pp; a monotonicity check that compared a list containing `None`
   against a filtered one). Both fixed in the tests, not by loosening the code.
3. `render_research` crashed on a literal `%` inside a `%`-formatted string
   ("vol_target=8%") — the face JSON and MD were already written, so a silent half-written
   face was avoided only because research md is written last.
4. **`evidence_cutoff` was the month-end label (2026-11-30), not the last bar (2026-11-26).**
   Found by reading my own rendered page. This is the r1788/r1880 family: a date printed
   from the wrong object. Now the cutoff is the last bar, and the final month is marked
   month-to-date.
5. A hard-coded "73 of 81 months rich" made it into the unverified text before I checked
   the table — the real count is 46 of 81. Now formatted from the counts.
6. The verdict mapping claimed `CUSHION_HOLDS_IN_BOTH_REGIMES` while the band straddled
   zero — an over-claim. Reordered so a band spanning zero yields
   `CUSHION_DIFFERENCE_NOT_SEPARABLE`, and a new leg pins that. Also added a gate on the
   size of each side (≥8 falling months) so a 3-month side can never be read as a regime.

## Verification actually run

- `selftest` → **22/22 PASS** (added: thin-side gate, matched-exposure control, rule-verdict
  mapping, edge band determinism, edge concentration).
- `run` → face written, reconciliation against the parent's own `cb.in_window`
  (bars 1671 / cagr / sharpe within 1e-6) = **True**.
- `check` → `{"ok": true, "verdict": "CUSHION_DIFFERENCE_NOT_SEPARABLE", "kind": "CHECK OK"}`.
  Drift branch says **STALE** by contract (r1934/r1850) so a future chain leg can pay to rebuild.

## Not done (and why)

- **chain leg + smoke leg**: both live in shared files; this round is contention-restricted.
- **CEO page section**: same reason (`scripts/ceo_live_usage.py` is a shared face).
- **full smoke suite**: ~1,142s does not fit a 10-minute round; the two commands this face
  covers were run directly instead. This is **not** a "suite is green" claim.
- **sleeve-level premium** (the 20 held bonds' own premium rather than the market median):
  named as owed, because a market-rich month need not be a sleeve-rich month.
