# E378 — "load-bearing" is a property of the yardstick, not of the store (bm-b r1397, 2026-11-03)

**Question.** E374 published that three of the 128 members in
`research/corpus_store/PINSTORE-daf9a897.json` are necessary and sufficient for E353's unwritten-guard
*pairs* (129 -> 131). E371 had published that the two `store_needed` members bind and write no field of
the E350 arm. Both sentences were then quoted as "the store is (not) load-bearing". The queue card asks
for the same four-arm ablation on E350's own headline numbers — `fields`, `fields_with_no_writer`,
`guard_fields_with_no_writer` — and for a per-arm answer if the two instruments disagree.

**Measurement** (`scripts/e378_store_load_bearing_e350_arm.py`, pin `daf9a897`, 2,251 pin members,
128 store members, four arms):

| arm | fields | fields_with_no_writer | guard_fields_with_no_writer |
|---|---|---|---|
| A pin only | 2,264 | 1,687 | 129 |
| B pin + store | 2,306 | 1,712 | **131** |
| D store minus the 20 | 2,264 | 1,687 | 129 |
| C the 20 only | 2,306 | 1,712 | **131** |

* The store moves E350's numbers too — by +42 fields, +25 unwritten fields, and **+2** on the guard
  face, the same +2 E353 reports. So the store is not "footprint-empty on E350"; only the two
  `store_needed` members are, which is what E371 actually said.
* The exact set is **20 of 128**: dropping all 20 returns the pin exactly, keeping only them returns
  the full store exactly. 108 members are ballast on both instruments.
* The subset that flips a *status* (guards a field the pin does not guard, or writes a field the pin
  counts as written by nobody) is **3 members**, and it is exactly E353's three
  (`Tools/_r1234bmb_pool.py`, `Tools/_r1334bmb_closeout.py`, `Tools/_r1334bmb_delivery.py`).
  The other 17 add only *new field keys* — they raise `fields` and `fields_with_no_writer` without
  closing or opening a single guard pair.
* So: E353's pairs are bought by 3 members, E350's field count by 20, the intersection is exactly the
  3. "Load-bearing" is per-arm; the store's measurable value to the firm is still those two guard
  pairs on its own heartbeat/status faces.

**Pitfall found in this window's own first draft.** The first pass attributed the set from
`e350.build()`'s published `rows`, which are capped at `MAX_ROWS` (260). On a truncated table the
status-flip rule returned **10** members, and the ablation refused to return to the pin
(2,295 / 1,706 / 128 vs 2,264 / 1,687 / 129) — the failure was the diagnostic, not noise. Re-running
from the **full** table gave 3, and adding the third movement rule gave 20 with exact return at both
ends. A publication cap silently became the population.

Verdict: `the_two_instruments_disagree_about_necessity_so_load_bearing_needs_a_per_arm_table`.
Face: `results/state_tilt/E350ARM-2026-11-03.json` (`e350arm_latest.json`). Selftest 11/11,
`verify` 0 problems.