# DIGEST -- E370: the whole summary classified by how it answers a grown corpus (r1394 bm-b)

**Face** `results/state_tilt/KEYSENS-2026-11-03.json` (+ `keysens_latest.json`)
**Study** `scripts/e370_key_sensitivity.py` (run / verify 0 problems / selftest 13/13)
**Pin** `535be1fe` (2368 members at 1244ee23; disk 2360 / git 6 / store_needed 2)
**Verdict** `published_keys_split_into_6_ratio_4_count_11_filtered_and_the_rule_is_that_a_share_absorbs_a_2.77_pct_corpus_growth_while_a_predicate_count_does_not_25_keys_are_unmoved_because_their_studys_population_never_changed_in_any_arm`

## What was asked

E368 compared four keys (corpus_sources, fields_with_no_writer, guard_fields,
guard_fields_with_no_writer) and found one stable, one moving 20%. E370's card asked for the whole
summary, per key, classified as ratio / count / filtered, with the drift each key tolerated.

## Arms

| arm | population source | E350 sources | drift vs published |
|---|---|---|---|
| published | `fieldbranch_latest.json` / `guardpresence_latest.json` | 2343 | 0 |
| live | fresh walk of the tree | 2408 | +2.774% |
| pinned_list | pin members, today's bytes | 2367 | +1.024% |
| pinned_bytes | pin members, pin-commit bytes where the disk drifted | 2367 | +1.024% |

E353's population (guard pairs) is 131 in every arm and the live arm agrees with E353's own face
(`cross_check.agrees = true`), so all 25 of its leaves are published as **unmoved** rather than
**ratio** -- a study whose population never changed was never asked the question.

## Readings (49 numeric leaves: 6 ratio / 4 count / 11 filtered / 1 flag / 1 other / 25 unmoved)

* **Invariant (ratio, tolerated 2.77%)** -- the guard family: `guard_fields` 230,
  `guard_fields_with_no_writer` 131, `guard_sites` 909, `max_blast_radius` 14,
  `reads_by_branch.assert_guard` 849, `reads_by_branch.exit_guard` 60.
* **Count (moves with the population)** -- `corpus_sources` 2343 -> 2408, `sources_parsed`
  2329 -> 2392, `dump_sinks` 876 -> 889, `unresolved_load_bindings` 3237 -> 3321.
* **Filtered (moves, not proportionally)** -- `fields` 2289 -> 2318 live / 1947 pinned,
  `field_reads` 5398 -> 5491 / 4914, `fields_with_no_writer` 1698 -> 1717 / 1356,
  `choice_sites` 1130 -> 1166 / 769, `choice_fields` 728 -> 745 / 440, `faces_named`
  846 -> 856 / 773, `json_bindings` 1632 -> 1663 / 1556, `reads_by_branch.unbranched`
  3359 -> 3416 / 3236, `reads_by_branch.choice`, `skipped_numeric_keys`,
  `fields_with_unresolved_face`.

## The membership arithmetic (published so the unexplained move is not attributed to population)

`population_overlap` = common 2368, only_live 41, only_pin 0. The pin is a subset of the live walk,
and a shared member contributes the same disk bytes in both arms, so only the 41 live-only members
(all created after the pin: `Tools/_r1390_*`, `Tools/_r1393_*`, drama runner assets) can move a count
by membership. The 15% drop in `fields` between live and pinned is therefore **not** a membership
effect; it is a content/vintage effect and this study publishes it without attributing it.

## Pit

The first burn printed every key as `ratio` with `tolerated=None` because `table()` read
`arms[arm][study]["summary"]` while the arms block already *is* the summary -- every population ratio
came out `None`, so "no arm moved the population" was true for all 49 keys and the rule silently
answered "nothing is claimed" everywhere. A second defect came with the repair: E353's genuinely
immovable population still had to be named, and calling it `ratio` would have manufactured a stability
claim -- hence `unmoved` as a first-class class, pinned by a selftest leg.

## How to apply

Quote a **ratio** through the drift it publishes; correct a **count** by the population change; re-run
a **filtered** number; never read **unmoved** as stable. And classify by the response, not by the key's
name: the word "fields" covers both an invariant guard count and a 15%-moving field count.