# Digest E287 -- a field that names rows while publishing group labels

Round: r1309 (bm-b) | study: E284_disagreement_field_scope | evidence_cutoff 2026-10-29
Face: `results/state_tilt/BANDDISAGREESCOPE-2026-10-29.json` (+ `banddisagreescope_latest.json`)
Runner: `scripts/e284_disagreement_field_scope.py` (run / verify / selftest 23/23)
Card: `knowledge/METHODOLOGY_ASSETS.md` E287

## Question

E281 re-derived E279's census cell by cell and found one summary field whose NAME says rows while
its VALUE is a list of group labels. `rows_where_tails_disagree_on_reachability` publishes
`["cross", "star_lag1_residual"]` where the disagreement is one CELL inside each leg, and each leg
carries four cells. Does the rest of the published family carry the same slip -- a name promising
one unit and a value measuring another?

## What was measured

1. **The known slip, repaired at cell scope.** The disagreeing cells are re-derived from E279's own
   per-tail reachability booleans (never from the summary): `cross|era_2025_now|9` and
   `star_lag1_residual|era_2023_2024|13`. Those land exactly on the keys the same face already
   publishes as `swap_deflation_rows` (`matches_published_swap_rows = true`) -- so the repair and the
   face's own earlier publication agree, which is the only reason to believe either.
   The old field is kept readable as a **group-scope upper bound**, and the bound direction is
   measured rather than assumed: `max_cells_in_one_group = 1` here, so group scope does bound cell
   scope from above. A group holding two disagreeing cells makes it a LOWER bound, and the same
   code publishes that (`selftest` L8) instead of quoting an inequality nobody checked.

2. **Family-wide sweep for the same shape.** 30 dated BAND faces walked field by field; every field
   whose value is a list of group labels is classified by what its own name promises. Exactly **one**
   field is flagged -- the E279 field -- and the rest are either correctly named as groups
   (`group_scope_named_correctly`) or un-named (`group_labels_unnamed_scope`, reported not judged).

3. **What was not assessed is published.** 1338 integer fields (`n_rows`, `n_records`, `n_moved`,
   ...) carry per-face census semantics that cannot be re-derived without re-running that face.
   They are aggregated by key name (n_total / n_distinct_keys / occurrences per key, and the
   occurrences are asserted to sum to n_total) and disclosed as **not assessed**. An unassessed field
   is not a clean field (E207).

## Why it matters

A summary field is the whole of what most readers see. When it names a group for a one-cell finding,
the face over-claims coverage by the number of cells in the group (4x here) with no visible error --
the wrong reading and the right reading print the same characters. The repair is cheap precisely
because the census already carried the cells; only the projection was wrong.

## Pit (recorded)

The first run keyed cell keys on `leg|base|index` and printed `cross|60|9` and `cross|60|13` for two
**different** groups, because every row in E279's census carries `leg = "cross"` while its group label
lives in `row`. Two groups collapsed into one leg key, and the face's `groups_match` check would have
reported a mismatch that looked like an upstream problem. Fixed by keying on the spelling the family
already publishes (`row|cell|index`) and carrying `leg|base|index` alongside for E282-keyed readers;
selftest L21 pins the collapse (two rows sharing leg, different row labels must give two keys).

Second pit, same family as r1308: PowerShell has no heredoc -- the patch was attempted with a `<<'PY'`
shell heredoc and PowerShell parsed it as redirection. Edits go through the edit tool.

## Reuse

- Scope vocabulary (group / leg / arm / family vs row) is the mechanical test; it needs no model.
- `classify_field` + `sweep_face` + `count_key_summary` are reusable for any family whose faces
  publish label lists.
- The bound-direction measurement (max cells in one group) is the part worth copying: "keep the old
  field as an upper bound" is a claim that must be checked, not a courtesy.