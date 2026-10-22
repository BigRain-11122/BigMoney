# DIGEST 2026-10-23 — E92 gap-tolerant split screen (who owns the 2021_2023 churn numbers)

- **Face**: `results/e44_midmonth/SCREENGAP-20261022.json` (evidence_cutoff 2026-10-22)
- **Runner**: `python scripts/e39_panel_census.py gapsplit` (census selftest 237/237, `--gaps 1,2,5`)
- **Screen**: `scripts/panel_screen.py` mode `neutralise_gap` (`gap_limit` in sessions, integer-ratio only) — selftest 23/23
- **Status**: descriptive census only. Zero prereg, zero judgement, zero ledger booking, trial_count 0.

## The question

E91 named a defect it could not repair: the 12:1 split on `sh510150` (2021-05-31, printed
10.414 → 0.87) sits **one missing panel bar** (2021-05-28) away from its own previous close,
so `panel_screen` files it as *gapped*. Both screen arms skip gapped prints by design, so the
print survived at exactly +9424.4bp, and it owned the 2021_2023 mid-month churn transition
(2021-05-17 → 2021-06-15) that E83 showed is the sole owner of the published +318.8bp era gap.

E92 answers it by measurement rather than argument: widen the screen to accept integer-ratio
prints up to N sessions behind a gap, sweep N = 1/2/5, and re-derive the churn cells on the
same burn.

## Census: how many prints live in the blind spot

| gap limit | gapped prints (panel) | eligible (integer ratio) | names | by era |
|---|---|---|---|---|
| 1 session  | 33 | 10 | 10 | 2021_2023: 9, pre2017: 1 |
| 2 sessions | 33 | 10 | 10 | 2021_2023: 9, pre2017: 1 |
| 5 sessions | 33 | 11 | 10 | 2021_2023: 9, pre2017: 2 |

Naming the 2021_2023 set: `sh510150` 12:1 (05-31), `sh510580` 10:1, `sh510030` 8:1,
`sh510210` 5:1, `sh512600` 5:1, `sh510630` 4:1, `sh512070` 3:1, `sh512710` 2:1, `sh513500` 2:1.
The pre2017 pair is `sz159901` (5:1 at 2010-11-22 behind a 3-session gap, 5:1 at 2014-09-01).

**Nine of the eleven gapped integer prints sit in 2021_2023.** The blind spot is not spread
evenly through history — it is concentrated exactly where the chain has been quoting its most
confident numbers.

Screen effect at `gap_limit=1`: 75 events neutralised (the 65 adjacent integer prints E76
already repaired, plus these 10), 74 names touched, 23 gapped prints still left alone because
their ratio is not an integer.

## Answer: the level was levered, the gap was not

Churn sleeve, equal-weight mean over swapped names, bp per swap:

| era | book | unscreened | gap-screened (limit 1) | change |
|---|---|---|---|---|
| 2021_2023 | month-end | +1866.5 | +768.2 | −1098.3 (−59%) |
| 2021_2023 | mid-15 | +2185.4 | +1068.2 | −1117.2 (−51%) |
| 2021_2023 | **gap (mid − me)** | **+318.9** | **+300.0** | **−18.9 (94% survives)** |
| 2024_now | month-end | +87.3 | +92.4 | +5.1 |
| 2024_now | mid-15 | −123.7 | −364.7 | −241.0 |
| 2024_now | **gap (mid − me)** | **−211.0** | **−457.1** | **−246.1 (widens)** |

Two readings, both load-bearing:

1. **The published 2021_2023 churn *levels* were roughly half a corporate-action artifact.**
   Repairing nine gapped splits removes ~1098bp from the month-end cell and ~1117bp from the
   mid-month cell. Any future quote of "churn alpha ≈ 1900-2200bp per swap in 2021_2023" has
   to say unscreened, or halve it.
2. **The published 2021_2023 *gap* is not.** +318.9 → +300.0 is a 5.9% loss: the repair hits
   both books nearly symmetrically, and the mid-minus-me gap is a difference, so the artefact
   cancels. E83's "one transition owns 18.9% of the gap" was a statement about a *magnitude*,
   and the magnitude does move (−9185bp on that one transition), but the gap it sits in does not
   depend on it.

The newest era goes the other way: the gap **widens** from −211.0 to −457.1 under the screen.
The mid-month deficit in 2024-now is therefore not a repair artifact either — repairing prints
makes it larger, and the screened number reproduces E82's `neutralise` cell (−364.7) exactly, so
the two arms agree and no double count is introduced.

## Transitions actually moved

9 of 69 month-end transitions and 10 of 69 mid-month transitions move by more than 0.5bp.
Largest mid-month moves: 2021-05-17 → 2021-06-15 −9185.4bp (the E83/E91 transition, now
repaired), 2021-07-15 → 2021-08-16 −5480.7, 2021-06-15 → 2021-07-15 −4389.8, and
2024-01-15 → 2024-02-19 −6614.2 (E82's amplifier, also a split). Month-end largest:
2021-06-30 → 2021-07-30 −9096.8, 2021-04-30 → 2021-05-31 −4826.0.

## Honest limits

- The integer-ratio test is evidence, not proof: a real resumption that lands on an integer
  ratio would be repaired by this branch.
- A wider gap limit buys more repairs and more false positives together; the sweep is published
  so a reader can see what each session costs (2 → 5 adds only one pre2017 event).
- The churn sleeve is an equal-weight mean over swapped names, not a portfolio return.
- Screen reports count repairs, not book impact: a repaired print still enters the rank cache at
  its adjusted level, so the era *spread* face (ladder vs wide) is untouched here — that is the
  next unit, not a claim of this one.