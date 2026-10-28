# E192 — churn-independence is not carrier persistence (round r1225, bm-b)

**Question.** E187 showed the wide book's surviving monthly repair motion is
independent of its own membership turnover (|r| <= 0.16 in every era) and that
the high-churn half carries *less* motion. The reading attached to that was
E184's: *the same names moving*, not different names being held. But
independence of WHO WAS HELD says nothing about stability of WHO DID THE
REPAIRING — a book can hold the same names and still be repaired by a different
name every month. E192 measures the carriers directly.

**Face.** `results/e43_tilt_4member/WIDECARRIERPERSIST-20261028.json`
(leg `scripts/e39_panel_census.py tilt3widecarrierpersist`, selftest 678 -> 686).

## Reading

| era | class | mean adjacent Jaccard | carry share | persistent carriers | their share of era gross |
|---|---|---|---|---|---|
| pre2017 | `no_repair_in_era` | – | – | 0 | – |
| 2017_2020 | `no_repair_in_era` | – | – | 0 | – |
| 2021_2023 | `carriers_persist` | 0.8217 | 95.6% | 352 names | 85.5% |
| 2024_now | `carriers_persist` | 0.9731 | 97.3% | 849 names | 89.2% |
| full | `carriers_persist` | 0.9207 | 96.7% | 691 names | 79.8% |

`carry share` = the part of this month's absolute repair motion carried by
names that also repaired the previous month. `persistent carriers` = names
repairing in at least half of the era's *repairing* months (a book-relative
majority, not an absolute count).

**Verdict: E184's "same names moving" is supported at name level.** In all
three eras where the wide book repairs at all, 94–97% of each month's motion
comes from names that were already repairing the month before, and the names
that persist carry 80–89% of the era's gross motion. Nothing recycles.

**The reversal months are not new names either — they are the *same* names
going the other way.** In 2024_now the four months that fight the era total are
carried 100.0% by names that repaired in the previous month (other months
97.2%); full era 94.6% vs 97.5%. `against_driven_by_new_names` is false in every
era. So the thin +49.6bp net E182 published is not churn noise: it is a stable
set of carriers oscillating in sign month to month, and E184's
"between-month sign disagreement" has an owner — the same names.

Top persistent carriers are the same block in every era (2024_now: sh510020 /
sh510030 / sh510050 / sh510060 / sh510150, each repairing 23 of 23 repairing
months).

## Controls and honest boundaries

- **Same-cutoff control**: E187's own formula (`_month_cancel_verdict` on the
  same sink) is recomputed inside this leg. Max residual 0.000399bp against a
  0.0005bp double-rounding bound, so the construct is reproduced exactly.
- **The 0.242bp head-to-head gap against the published E187 face is a CUTOFF
  difference, not a wedge**: that face was built at 2026-10-27 with 34 months in
  2024_now; this panel has 33. Published as `e187_join.cutoff_match=false`
  rather than quoted as a reproduction (E180's lesson: a gap needs a name).
- **A month with nothing repaired is not a recycling month.** Its pairs are
  skipped and counted (`pairs_unmeasured` 26/15/134), not scored 0.0 — scoring
  them would manufacture the "recycle" verdict out of sparsity. This is why
  pre2017 and 2017_2020 land in `no_repair_in_era` rather than in a class.
- Jaccard ignores magnitude, so `persistent_carrier_share_pct` (magnitude-
  weighted) is published beside it; a persistent minnow and a persistent giant
  count the same in the Jaccard column.
- Descriptive census: n is month pairs, not trials. No gate, no prereg.