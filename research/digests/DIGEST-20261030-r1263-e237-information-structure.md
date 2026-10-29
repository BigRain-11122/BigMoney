# E237 — the own-turnover channel is not an information-arrival artefact (r1263 bm-b)

Card: `E237-INFORMATION-VS-TURNOVER-SHARED-RETURN`.
Face: `results/state_tilt/INFOSTRUCT-2026-10-29.json` (+ `infostruct_latest.json`).
Runner: `scripts/e237_information_structure.py` (selftest 18/18).
S6 leg: `information_structure`, immediately after `share_difference`.

## What E236 left open

E236 published three stationary designs whose b_own intervals did not overlap: the difference
design read **0.431 [0.341, 0.520]** and the cross-sectional ones 0.017 / 0.023. It named the
mechanism in prose — *the difference design prices a session against that session's own
turnover CHANGE, which co-moves with the same information arrival that sets |r|* — and stopped
there. This face measures that mechanism instead of asserting it.

## Readings (pooled, 15,641 member-sessions, 5 sleeves)

| reading | value |
|---|---|
| uncontrolled b_own (E236 design A, re-used verbatim) | **0.431** |
| controlled for the market's own log\|r\| | **0.394** |
| first stage: d(share) on d(log\|r_book\|) | −0.0024, **t −1.23** |
| d(share) on d(relative component) | 0.0313, t 11.0 |
| components (turnover on return): common c | 0.1085 [0.1001, 0.1169] |
| components (turnover on return): relative c | 0.0730 [0.0658, 0.0802] |
| common-relative size ratio | 1.49 |
| pooled verdict | **own_channel_survives** |
| per member | 4 of 5 survive; sh510300 = `residual_only_channel` |

The coefficient loses only 0.037 of 0.431 when the market's own return is known, and the first
stage says the share **never carried market information** (t −1.23, R² 0.0001). Both stages
agree: the artefact hypothesis is rejected. The share does echo the member's own information
arrival, but weakly (0.031), so the surviving 0.394 is not a relabelled information channel
either — it is something else, and that "something else" is now the open question rather than
the artefact.

The bill gate still refuses: the two decomposition components both clear the bar (7.4σ and
9.7σ against a 2.77 t bar over 9 pooled tests) but their intervals are disjoint (ratio 1.49),
so under the card's rule no per-member charge is written. The family's linear charge stands.

## The trap this face had to walk past

Fitting the share coefficient with the **relative component** as the control looks like the
card's design and is mathematically dead: dy = d(common) + d(relative) identically, so
controlling the relative part leaves only the common part and *every* other regressor's
coefficient measures its covariance with d(common). The first draft did exactly that and would
have "found" an artefact in every panel, including a synthetic one whose truth was a genuine
relative channel. The control has to be an *outside* regressor (the market's own |r|), not a
component of the dependent variable.

Sibling trap, same family: writing the artefact test in the turnover direction (dlo on
d(share), d(book)) is degenerate because dshare + d(book) = dlo exactly — the regression
returns a 1.0/1.0 split regardless of the data. The share designs must keep E236's direction
(dy on turnover changes) and the components designs the card's direction (turnover on return
components); no coefficient is compared across the two directions, and the face says so.

## Identity, published rather than celebrated

The components design (dlo on d(common), d(relative)) and the direct design (dlo on d(log|r|),
d(log|r_book|)) span the same regressor space, so **c_rel IS the dy coefficient** — exact to
1e-9 on a single member and 1.7e-4 on the pooled fit (the per-member betas differ). Two designs
agreeing by algebra must never be counted as two readings; the face publishes
`c_rel_minus_dy` as a number and a selftest leg pins the identity.

## Reusable

1. **"Artefact" is a claim about where a coefficient lives, so it needs a control that is not
   a component of the dependent variable.** Controlling an exact decomposition of y makes the
   test vacuous and silently turns every panel into an artefact.
2. **Refuting an artefact claim takes two measurements, not one**: the coefficient under the
   control, and the first stage that says whether the regressor ever carried the confounder.
   Here both are clean (0.431 → 0.394; t −1.23), which is what makes the rejection readable.
3. **Direction is part of a regression's identity.** dshare + d(book) = d(own) makes one
   direction degenerate; dy = d(common) + d(relative) makes one control degenerate. Writing
   the direction down next to the design is cheaper than discovering it after the burn.