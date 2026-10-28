# DIGEST 2026-10-28 r1223 bm-b — E190: how fragile is the fragile verdict?

Pool head burned: `E190-DROP-FRAGILITY-SWEEP` (seeded r1220 after E189, ready since
2026-10-28T15:45). Leg `tilt3ladderdropcurve` in `scripts/e39_panel_census.py`; face
`results/e43_tilt_4member/LADDERDROPCURVE-20261027.json`; evidence cutoff 2026-10-27.

## The question

E189 removed exactly one month per pair — the month E186 had named as the carrier — and all
four era-level reversals collapsed. That says the verdict is fragile; it does not say how
fragile, because one removal is not a curve. Publish the curve: remove k = 1..8 months under
four different rules and report the k at which the two readings (additive sum vs compounded
link) stop disagreeing in sign.

The four rules are deliberately not one ordering in disguise:

- **gap** — rank by |`gap_bp`|: the months that move the level most.
- **delta_sum** — rank by |`delta_sum`|: the months that move the additive path most.
- **first** / **last** — the era's own chronological edges: is the verdict an edge-of-window
  effect?

## Result: every flagged reversal dies at k = 1, and the reading is rule-sensitive

| era | pair | gap | delta_sum | first | last | class (gap rule) |
|---|---|---|---|---|---|---|
| 2024_now | sh510050 | **1** | **1** | **1** | **1** | two_month_artefact |
| full | sh510050 | **1** | **1** | 4 | 4 | two_month_artefact |
| pre2017 | sh510300 | **1** | **1** | 8 | **1** | two_month_artefact |
| pre2017 | sh510500 | **1** | **1** | **never** | **1** | two_month_artefact |

1. **One month is the whole verdict on all four pairs.** Under both magnitude rules the
   disagreement is gone at k=1: remove the single largest-gap month and the additive and
   compounded readings stand on the same side of zero. No pair survives the sweep.
2. **But "which month is worst" is not a fact.** Removing the era's *edges* needs 4 months on
   `full`, 8 on `pre2017`/sh510300, and on `pre2017`/sh510500 never clears within k≤8 — an
   `era_property` under the `first` rule and a `two_month_artefact` under the other three.
   Three of the four pairs are class-sensitive, so a headline that names a class without
   naming the rule is not reproducible.
3. **The class boundary is not a knife edge.** The `first`-rule cases land at k=4 and k=8:
   the window's *edges* carry real repair motion even though the biggest months carry the
   reversal. Both statements are true of the same era, which is why the answer has to be a
   curve and not a label.

Join check: the two era readings rebuilt from E186's published month rows land within
8.8e-05 bp of the published effects, so this is the same arithmetic, not a second one.

## What this licenses

The era-level reversal in the E183-E186 family **may not be quoted as an era verdict**. It is
a single-month event under both magnitude rules. It may be quoted as: "within this era, the
additive and compounded readings of the ladder drop disagree, and one month owns the
disagreement" — with the month named, because E186 already names it and this leg confirms
that naming the month is what makes the claim true.

## Limits

- k is capped at min(8, months-2): a short era cannot be trimmed to one observation and read
  as agreement. `pre2017`/sh510500's `first`-rule `null` is "not cleared within the cap", not
  "an era property forever".
- Removing months changes the sample the verdict is computed on. This measures fragility; it
  does not license dropping any month from a published number.
- No pair in this family manufactures a reversal by trimming (`k_reversal_created` empty on
  all 16 rule-pair cells), so the curve has one direction only.
- Descriptive census: no gate, no prereg, no trial count.

## Next

`E192-WIDE-CARRIER-PERSISTENCE` and `E193-DELTA-BUILD-STANCE` remain ready. The natural
follow-up here is the *justification* of the trim rule — `E195-DROP-TRIM-RULE-JUSTIFY` was
seeded: pick the rule from an independent criterion (which months an outside observer could
have flagged in advance) instead of from which rule clears the disagreement.