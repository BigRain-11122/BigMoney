# E385 -- does splitting a merged key move any published number? (r1415 bm-b, 2026-11-03)

**Question (from the pool, entered r1402).** E383 found eight keys that each name two or more files
on disk and seven of them quoted from a published face's key list. E386 priced the merge inside one
family. The open question a republish turns on: would splitting those keys move a published NUMBER?

**Method.** Four headlines are functions of the key set. Each is re-derived from the same population
under two keyings: the published one (a key is one unit), and a split one (every identified file
behind a key is its own unit). A key whose files cannot all be identified is priced as a floor, never
as a count. No upstream face is rewritten; E350/E353/E377/E381 are read as published.

| headline | published | split | verdict |
|---|---|---|---|
| E350 `faces_named` | 862 names | 1,002 documents (+140, floor) | meaning changes, number does not |
| E353 `pairs` | 131 | 210 (by_class 5/103/23 -> 80/108/22) | **moves** |
| E377 `faces_no_census_keys` | 36 | 36 | unit is a path, cannot move |
| E381 `joined_only_faces` | 12 | 12 | unit is a path, cannot move |

**Readings.**

- 19 of 862 names merge two or more files; the largest is `latest.json` with 28. All 19 merges
  survive dropping every file outside the census walk, so the merge lives in the data, not in the
  index's choice of directories.
- All 7 guard pairs on an ambiguous key are published as `guard_unreachable`; naming each member
  moves 7 of 7. 2 are settled by exactly one in-census member (the other member of `meta.json` sits
  in `Money02`, outside the walk) and 5 stay ambiguous inside the walk (`manifest.json` 19 members,
  `probe.json` 14). So of the seven, 2 are the instrument's ambiguity and 5 are the data's.
- 4 of the 48 faces in the two list arms share their basename with other files, and neither list
  moves: a path names one file however many neighbours share its name.

**Verdict (gate-derived, not written):**
`splitting_moves_the_guard_headline_and_only_the_pairs_whose_ambiguity_comes_from_outside_the_census_walk_are_settled_by_naming_a_member_while_the_rest_stay_undecidable_inside_it`

**Not measured.** Whether a consumer of a merged key reads the right member (that is E383's consumer
table); a document count for a name the tree cannot resolve (published as a floor).

**Wiring.** `scripts/e385_merged_key_split.py` (run / verify problems=[] / selftest 19/19); smoke leg
E385 (exec'd verbatim, 1/1); S6 leg `merged_key_split` (rc 0, 0.33 s); face
`results/state_tilt/SPLITPRICE-2026-11-03.json` + `splitprice_latest.json`; methodology card E385.

**Two rules worth keeping.**

1. A split that multiplies rows is only a republish when the headline's unit is a document. Here the
   name count moved by 0 and the pair count by 79, and calling both a republish would have been wrong
   in one direction or the other.
2. Before repairing an ambiguity by naming a member, ask which members the census can even see: an
   index that includes trees the corpus never parses manufactures an ambiguity that the corpus does
   not have.