# CASE PREREG — E27: is the fill itself the last lever? (slicing the rebalance over k opens)

Frozen BEFORE the first run. Source row: `state/queue/explore.md` E27 (seeded by r1226 bm-a).

## Question

E25 showed the 1.14 pp/yr gap between the card's as-coded arm (buy at bar d open) and its
declared arm (decide on bar d close -> fill at bar d+1 open) is information, not turnover:
smoothing recovers +0.07 pp of 1.14 (signal +0.06 / cost +0.01). E26 priced the only
information channel between the decision close and the fill open — the overnight gap — and got
+0.81 pp/yr on the full span while winning only 2/4 decision phases, negative as a ranking
signal. So both the information and the price are exhausted; what is left is the *mechanics of
the fill*: instead of putting the whole delta through one open print, put it through `k`
consecutive opens in equal slices.

Note what this arm can and cannot claim. It does **not** reduce turnover: the equal slices sum
to the same absolute delta, so the total commission is identical to the single-open fill by
construction (asserted, not assumed). What it changes is the **price path** — the book spends
part of the transition in cash and each slice is paid at a different open (averaging the fill
against the gap dispersion measured in E26 at ~40-70 bp per entry bar).

## Implementation freeze

Same engine, same book, same sizing, same costs — only the execution schedule differs:

- `n_hold`, `rebal`, `cost_per_side` and `vol_target` are `etf_book_forward.CONFIG` values,
  read, never restated.
- The target book at decision `d` is the same `nlargest(n_hold)` selection and the same
  8% vol-target sizing (de-lever only, `vol_cap=1.0`) as `etf_robust_pf.open_to_open_equity`.
- `k` in {1, 2, 3, 5}: equal slices of the *original* delta, one per open from `d` to `d+k-1`.
- Identity leg: `k=1` must reproduce `etf_robust_pf.open_to_open_equity` **bit for bit**
  (max |diff| <= 1e-12 on the equity series) — otherwise the wrapper is a new engine and the
  comparison means nothing.
- Participation leg: after the last slice the held book equals the target exactly, and the
  total turnover charged over the `k` slices equals the single-open turnover for the same
  decisions (tolerance 1e-9). A sliced arm that also shrinks the book would be a different
  experiment (the E197 lesson: cut the flip, not the position).
- Four decision phases from `etf_book_vol_window_phase.phase_starts`, same as E26.

## Criterion (frozen, no tuning after the fact)

An arm `k` is admissible iff, versus the `k=1` control:

1. full-span CAGR gain **>= 0.57 pp/yr** (half the one-bar price — less than that is not a
   reason to change how the desk trades), and
2. it wins **>= 3 of 4** decision phases (a single decision sequence is not a rule), and
3. max drawdown is **no deeper than the control minus 2.0 pp**.

Verdict states: `ADOPT_SLICED` (at least one admissible k) / `MIXED_ACROSS_PHASES` (the return
line is cleared but the phase test or the drawdown test fails) / `NO_SLICING_EDGE` (gain below
0.57 pp regardless of consistency) / `INCOMPLETE` (control arm did not price).

Controls that must both hold before any verdict is read: the `k=1` arm reproduces the card's
published declared CAGR within 0.05 pp, and the identity leg is exact.

## Honest limits (declared now)

- Slicing over k opens delays part of the position by up to k-1 sessions; the book therefore
  carries cash during the transition. That is the mechanism, not a bug, and it is the same
  for every k.
- No market-impact model: the only cost is the published 10 bp per side on traded weight.
  Slicing can only look better or worse through the price path, never through impact.
- ETF universe is the surviving-instrument panel (survivorship, unchanged from prior faces).
- This is a research face. It never rewrites `etf_book_production` config; an ADOPT verdict
  means the next frozen change window may move the desk, not this run.