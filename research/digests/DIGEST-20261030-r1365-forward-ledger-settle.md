# DIGEST 2026-10-30 — the forward ledger froze on a bar whose panel was still filling

Window: bm-c, round 1365 (yield window — a live headless round owns the tree; this
window did read-only diagnosis + one new read-only tool, and touched no shared face).
Tool: `scripts/etf_book_forward_settle_audit.py` (selftest 9/9).
Face: `results/etf_book_forward_settle_audit.json`.
Subject: `results/etf_book_forward/LEDGER.json` frozen since 2026-10-29 on
`2026-10-29:5.064e-06`.

## The question nobody asked

Rounds 1362 and 1364 both saw the freeze and both declined to spend `--rebase` on it,
with the same reasoning: *a 5e-6 difference is not worth buying with a ledger rebase*.
That is a statement about the price of the escape, not about the cause of the freeze.
The cause matters because the ledger is the only live product face: while
`status=frozen` it accrues nothing, and when today's bar lands it will refuse it too.

## What the numbers say

The drift is not a data revision. Measured:

- **No published price was rewritten.** `git diff` over `data/daily/` contains zero
  removed `2026-10-2x` rows; every held symbol shows exactly one added line, the new
  `2026-10-30` bar.
- **The panel is still filling after the close.** Symbols with a bar per day:
  10-27 → 1,720, 10-28 → 1,721, 10-29 → 1,723, and 10-30 → 1,710 of a 1,725-symbol
  universe (15 symbols have not printed today yet). Coverage rises toward the newest
  date, which means every date was, at some point, less covered than it is now.
- **The ledger priced 10-29 at 15:52 on 10-29**, 43 minutes after the close, i.e. on
  the panel as it stood then — not the panel that exists now.
- **Only the newest bar moved.** `checked_bars=5`, and the failed set is exactly
  `['2026-10-29']`: the four older bars re-derive inside the engine's own `DRIFT_TOL`
  of 1e-9. Settled bars are bit-stable; the bar whose inputs were still arriving is the
  one that failed.

Mechanism: a late-arriving bar replaces a stale `ffill` with a genuine print. That moves
the symbol's cross-sectional features, can change the book's ranked selection, and
therefore moves a mark that is already published. No revision is required for this to
happen — and none occurred.

## Why the gate cannot be satisfied as written

`DRIFT_TOL = 1e-9` is checked against **every** published bar, including the newest one,
whose panel is by construction still growing. An honestly priced last bar will therefore
fail on a later day, freeze the ledger, and offer exactly one exit: `--rebase`, which
rewrites the history the gate exists to protect. The gate is doing the opposite of its
purpose on this input class.

Recommended rule, published in the face:

> A drift gate may only police **settled** bars. The newest published bar is provisional
> until its panel date stops gaining symbols; while provisional, a re-derivation
> mismatch is reported, not frozen on — and never bought with a history rewrite.

Verdict string the audit emits and re-derives in `check`: `drift_only_on_unsettled_bar`.

## What the audit adds beyond this one case

It answers the next freeze in one command instead of a debate: read the ledger's own
drift block, classify each published bar as settled or provisional against the panel's
current coverage, and name which of the three states it is —

- `no_drift` — ledger clean;
- `drift_only_on_unsettled_bar` — the freeze is a false positive for revision (rerun the
  bar's pricing later, do not rebase);
- `drift_on_settled_bar` — the case the gate exists for; inspect for a real revision
  before touching history.

It also prints the pending-symbol count per day, so the at-risk size of the next bar is
visible before it drifts (today: 15 symbols).

L11/L12-class honesty: point-in-time coverage at pricing time is not recorded anywhere,
so "the panel was still filling" is *inferred* from the panel's current shape plus the
pricing run's timestamp, not observed directly; and it cannot attribute the 5.064e-06 to
a named symbol because it does not re-run the engine. Both limits are in the face's
`caveats`, not in a footnote here.

## Handover

Not done by this window, and why: the tree is owned by a running headless round, so the
engine edit (gate on settled bars only), a chain leg and a smoke leg are **not** written
here. Named for the next free window:

1. `etf_book_forward.py`: apply the settled-bar rule inside the drift gate, and stop
   offering `--rebase` as the answer to a provisional-bar mismatch.
2. chain leg running `settle_audit run` after the forward leg, so a freeze is classified
   the round it happens rather than two rounds later by hand.
3. smoke leg asserting the three verdict states from the frozen fixture (the selftest
   already contains them: provisional-only / settled / clean).
4. The frozen ledger stays frozen until then: unfreezing it without the rule just
   re-arms the same false positive on the 10-30 bar, which has 15 symbols still in flight.