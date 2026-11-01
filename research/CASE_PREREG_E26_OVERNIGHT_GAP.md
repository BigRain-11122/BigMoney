# CASE PREREG E26 — the overnight gap: the only information channel left between decide and fill

**Frozen before the first run.** Queue row: `state/queue/explore.md` E26. Seeded by E25
(`results/etf_book_causal_rebuild.json`, verdict `IRRECOVERABLE`).

## 1. The question

The card declares `decide at close of bar d -> fill at open of bar d+1`. E25 showed the
1.14 pp/yr that this costs cannot be won back by rebuilding the same score causally: the best
smoothed arm recovered +0.07 pp of 1.14 (signal +0.06, cost +0.01), i.e. the price is
information, not commission and not a badly lagged rank.

If the price is information, then the only lever left is a *different* information channel.
Exactly one channel exists between the decision close and the fill open:

    gap[t] = open[t] / close[t-1] - 1        (per name, per entry bar)

It is completely observed at the fill instant, so it is admissible (no look-ahead): a desk can
look at the open print and decide whether to still take the trade.

Two economically distinct uses, both frozen here:

- **rank on it** — replace the price score with the gap itself, both signs
  (`gap_rank_up` buys the names that gapped up, `gap_rank_down` buys the ones that gapped down);
- **exclude the names whose gap already ran** — keep the declared ranking, but drop names whose
  gap is extreme before selecting, so the book does not pay up for a move that already happened.

## 2. Arms (frozen set, no additions after the run)

| arm | score fed to the ladder | causal basis |
|---|---|---|
| `declared` | `score.shift(1)` | control — the number the card carries |
| `gap_rank_up` | `+gap[t]` | gap observed at open t |
| `gap_rank_down` | `-gap[t]` | gap observed at open t |
| `excl_absgap_q80` | `declared`, minus names whose `abs(gap)` is in the top 20 % of that bar | fill-time |
| `excl_absgap_q90` | `declared`, minus names whose `abs(gap)` is in the top 10 % of that bar | fill-time |
| `excl_upgap_q80` | `declared`, minus names whose `gap` is in the top 20 % (one-sided) | fill-time |

`excl_upgap_q80` is the arm with the actual economic story (you do not want to buy what already
jumped at the open); `excl_absgap_q80` is its two-sided control, and `gap_rank_*` tests whether
the gap carries information at all.

Ladder is the card's own (`F.CONFIG`): n_hold 12, rebal 20 bars, 10 bp/side, 8 % vol target
that only de-levers, open→open, same repaired panel and class filter. Four decision phases
(`etf_book_vol_window_phase.phase_starts`) so a single decision sequence cannot pass as a rule.

## 3. Criterion (frozen — adopted from the queue row, not invented here)

An arm is **admissible** iff all three hold:

1. `CAGR(arm) - CAGR(declared) >= 0.57 pp/yr` on the full span (half the 1.14 pp one-bar price);
2. `phase_share >= 0.75` — it beats `declared` on CAGR in at least 3 of the 4 decision phases;
3. `maxDD(arm) >= maxDD(declared) - 2.0 pp` (no deeper drawdown by more than 2 pp).

Verdict vocabulary:

- `ADOPT_GAP` — at least one arm admissible; the payload names the arm to carry.
- `MIXED_ACROSS_PHASES` — the return line is cleared but the phase share is not, or the reverse.
  Nothing is recommended; a rule that wins on one decision sequence is not a rule.
- `NO_GAP_EDGE` — no arm clears the return line. The gap stays information and the row closes
  as a further negative.
- `INCOMPLETE` — the declared arm did not price (never silently a pass).

Control: `declared` must reproduce the published card within 0.05 pp (`execution_basis.
declared_cagr` in `results/etf_book_production/latest.json`). A miss is reported, not absorbed.

## 4. Audits (mechanical, so the sentence cannot pass by never firing)

- **A6 fill-time causality** — the gap row at bar t must be reproducible from `open[t]` and
  `close[t-1]` alone. The auditor is selftested against a planted leak (same-bar
  `open[t]/close[t]-1`), which must make it fire.
- **A7 declared lag** — the control arm uses `shift(1)`; lag 0 is the look-ahead arm and is not
  an admissible baseline.
- **A8 exclusion is a mask, not a rescale** — an exclusion arm changes the *selection set* only:
  names below the threshold keep their declared score bit-for-bit.

## 5. What this face does not do

- It adopts nothing. It prices candidates; changing what the card prints is a separate frozen
  step across every face that quotes the headline.
- It does not mix in the close-marked ledger arm (9.12 %) — that answers a different question.
- Instrument-list survivorship is unchanged and still disclosed on the card.
- If the verdict is negative it is published as a negative: the row closes, and a further
  attempt needs a new information channel, not another parameter sweep of this one.