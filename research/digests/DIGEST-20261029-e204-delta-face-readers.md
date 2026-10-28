# Digest — E204: who actually reads a delta face's number (r1232 bm-b)

Face: `results/e79/SIGNEXPOSURE-2026-10-27.json`
Code: `scripts/e97_routing.py` mode `signexposure` (selftest 70 -> 77)
Upstream: E193 (delta build stance) + E201 (sign declaration), both r1227-r1230 bm-b
Dept: research + engineering. Cost: reader-facing only, zero bp, no published number moves.

## The question E201 left open

E201 measured 14 of 14 decomposition-family faces never state their sign convention in
prose, and printed the sentence each one would have to add. That is a defect only if a
reader can be misled. Publishing "write this line" for a face nobody reads by name is
documentation debt; publishing it for a face a second script pulls the number out of is a
live trap. Nothing had measured which case each face was in.

## What was measured

For every face in the E193/E201 census:

1. the delta leaf names its cells carry (from the E193 stance rows),
2. every in-repo script that names one of those leaves as a **quoted literal** (substring
   matching is refused: a reader of `engine_ann_diff_bp_raw` is not a reader of
   `engine_ann_diff_bp`),
3. the face's own producer, identified by directory token + filename stem inside a script
   that also carries a `results/` path,
4. the reader class — `read_outside_the_producer` / `producer_only` / `no_reader_in_repo` /
   `producer_unlocated`,
5. `trap = needs_line AND read_outside_the_producer`.

## Reading

- faces 14, silent 14 (E201 reproduced exactly), traps **0**, producers unlocated 0.
- reader class: `producer_only` = 14 of 14.
- verdict `every_silent_face_has_no_reader_outside_its_producer`.

So the whole E201 census is documentation debt, not exposure: every one of these numbers is
written by `scripts/e39_panel_census.py` (or, for `WIDESIDEGROSS`, that script plus its
one-window generator `Tools/_r1226bmb_face.py`) and named by nothing else. A reader of these
faces is a human reading prose, and the prose is exactly what does not teach the direction.

## The pitfall this study hit on its first fire (the real methodological content)

The first run reported **5 traps** — `HIST`, `LADDERSIDECASH`, `TILT3LEGFAMILY`, `TILT3REACH`,
`WIDESIDEGROSS` — with every external reader being `scripts/e97_routing.py`, i.e. **the auditor
itself**. The module carries leaf names in its own classification table
(`LEVEL_OVERRIDES = {"engine_ann_diff_bp": "anchored"}`) and in its own selftest fixtures, so a
name-scan of the source tree finds the auditor as a "consumer" on every face whose leaf it has
ever had to classify.

A naming table is not a consumer. The auditor is now excluded from its own reader set
(`SIGNEXPOSE_SELF`), the exclusion is published in the face's `spec.self_excluded`, and leg L74
pins it. Without that leg, the headline of this study would have been a 5-face trap list that
exists only because the measuring tool spells the field names.

Sibling form of the same class already on file: r1292's unit-token-in-the-middle-of-a-name,
and r1232's own quoted-literal rule (which is the same pitfall caught one level down).

## Consequence for E201

The suggested lines stay worth writing — but as a documentation task with no mechanism behind
it, not as a defect that can cost a reader a sign today. The cheap mechanical fix, if a later
window wants one, is a leg that fails when a NEW delta leaf appears in a face while that face's
text block stays silent — i.e. gate the growth, not the backlog.