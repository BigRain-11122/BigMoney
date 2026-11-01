# CASE PREREG — E25 ETF book causal rebuild: is the one-bar price recoverable?

Status: **FROZEN 2026-11-02T01:4x+08:00 (bm-a r1224), before the first run.**
Queue row: `state/queue/explore.md` E25. Supersedes nothing; consumes E25 on completion.

## 1. Question

The card printed 9.60%/yr and r1207/r1220 measured the same rule one bar later at 8.46%/yr
(`etf_book_lookahead_audit`, monotone lag ladder -2:+15.98 / 0:+9.60 / +1:+8.46 / +20:+5.09
pp/yr). One bar of information is worth **1.14 pp/yr**.

E25 asks the question a reader of the card actually has: *is that 1.14 pp lost to timing
information (irrecoverable), or can a rule built only on information that existed at the
fill price earn part of it back?*

Two candidate mechanisms, and they must be separated, not conflated:

1. **Signal quality** — the causal ranking is simply worse because it is older.
2. **Turnover** — a one-bar-lagged ranking churns more (the book is chased after it has
   already moved). Some of the 1.14 pp would then be cost, not information.

## 2. Mechanism claim (α)

A temporally smoothed causal score — the average of the last `k` scores, each computed from
a close ≤ d-1 and filled at open d — is a *legitimate* rebuild: it changes how noisy the
ranking is, never when the information existed. If smoothing recovers return, the recovered
part is turnover-sensitive signal, not future information.

## 3. Arms (all on the card's own ladder: n_hold=5, rebal=20, cost 10bp/side, 8% vol target
that only de-levers, open-to-open, same repaired panel, same class filter)

| arm | score | causal? |
|---|---|---|
| `as_coded` | `score` | no — control, must reproduce 9.60% |
| `declared` | `score.shift(1)` | yes — the number the card now carries |
| `smooth_k2` | mean(shift 1..2) | yes |
| `smooth_k3` | mean(shift 1..3) | yes |
| `smooth_k4` | mean(shift 1..4) | yes |
| `smooth_k6` | mean(shift 1..6) | yes |

Four decision phases (the `phase_starts` rule already frozen in
`etf_book_vol_window_phase`, imported, not re-implemented) — one phase cannot distinguish a
rule from one lucky decision sequence.

## 4. Frozen criteria

- `RECOVERY_MIN_PP = 0.57` — **half** the published one-bar price of 1.14 pp/yr. Recovering
  less than half is not a reason to change what the card prints.
- `SHARPE_MIN` = the `declared` arm's own Sharpe (no fixed number: it is read from this run's
  `declared` row, so the criterion cannot drift with the panel).
- `DD_TOL_PP = 2.0` — a smoothed arm may not be more than 2 pp/yr deeper in drawdown than
  `declared`.
- `PHASE_SHARE_MIN = 3/4` — the winning arm must beat `declared` on CAGR in at least three of
  the four phases.

Verdict rule (evaluated from the published rows only, so `--check` can re-derive it):

- `RECOVERABLE` — some smoothed arm meets all four tests. Recommendation: that arm's number
  is what the card should carry (adoption itself is a separate, frozen change, not this face).
- `IRRECOVERABLE` — no arm meets them. Recommendation: the card keeps 8.46% and no further
  smoothing work is worth burning.
- `MIXED_ACROSS_PHASES` — the tests pass on the full span but not phase-wide (or vice versa):
  a rule that wins on one decision sequence is not a rule.
- `INCOMPLETE` — a required arm failed to price.

## 5. Cost decomposition (mandatory, not optional)

For the best smoothed arm and for `declared`, re-run with `cost = 0`. Publish
`recovered_gross_pp` (signal) and `recovered_cost_pp` (turnover) so the recovery is attributed
rather than asserted. A recovery that is entirely cost saving must be printed as such.

## 6. Mechanism audits (must pass or the face is void)

- `A1` control: `as_coded` reproduces the published card CAGR within 0.05 pp.
- `A2` the `declared` arm reproduces the published 8.46% within 0.05 pp.
- `A3` **rank-layer causality**: `build_score` on the panel truncated at bar d returns the
  same score row at d as on the full panel (the score is a per-date cross-section, so no
  later row may leak into it). Asserted on a sample of decision bars across the span.
- `A4` **feature-layer causality (source pin)**: `engine/factors.py` contains no whole-sample
  statistic — every `.mean()`/`.std()`/`.rank()` call site must be inside a `rolling`/
  `expanding` context or carry `axis=1`. The auditor is itself selftested against a planted
  violation, so it cannot pass by never firing.
- `A5` plumbing: no smoothed arm may read a lag < 1 (constructive — asserted on the lag list).

## 7. Boundaries

- No config, card, or engine is rewritten by this face. Adoption is a separate frozen step.
- Mark basis stays open-to-open throughout; the close-marked ledger arm (9.12%) is a
  different question and is not mixed in here (r1207 boundary, kept).
- Panel is the current repaired ETF panel; survivorship of the instrument list is unchanged
  and remains disclosed on every card.

## 8. Outputs

`results/etf_book_causal_rebuild.json`, `research/ETF_BOOK_CAUSAL_REBUILD.md`, methodology card
`E341`, one smoke leg that re-derives the verdict from the published rows.