# E111 -- a face's identity is (code version, cutoff); unstamped is UNKNOWN

Ticket (pool E111-FACE-FACTOR-STAMP): every e44 face carries an implicit version -- the code that
burned it. E110 proved a control can compare two different experiments and call the difference a
defect, and the cutoff guard only catches one of the two axes. Stamp a `repair_factor` marker into
every face written by `e39_panel_census` so a join can refuse a cross-version comparison instead of
reporting a mismatch. Back-stamping is impossible: publish the stamp going forward and make the
control treat an unstamped face as unknown, not as agreeing.

## What was actually wrong

`burncontrol` (E88) joins three faces read off disk and demands exact equality of `mean_bp`. E110
added the cutoff axis (`mismatch_across_cutoffs` + `stale_twins`). The second axis -- which repair
code produced the face -- was never written down anywhere, so a pre-E108 face (2026-10-22, folded
share ratio as factor) and a post-E108 one could be joined and the gap reported as a burn defect.

The sharpest symptom is the one that survived E110: two *unstamped* faces that agree are published
as `identical_on_this_face`. That is an agreement claim the instrument cannot support.

## What was built

| piece | where |
|---|---|
| `repair_factor_id()` -- 12-char sha256 over `split_events`/`neutralise`/`implied_ratio` source, CRLF-normalised | `scripts/panel_screen.py` |
| `_stamp_repair_factor()` -- stamps `repair_factor` + `repair_factor_src` in the ONE writer every face goes through | `scripts/e39_panel_census.py` (`write_json`) |
| `_repair_factor_guard()` -- `uniform` / `version_unknown` / `mixed_repair_factors` | `scripts/e39_panel_census.py`, wired into `run_burncontrol` |
| census of what is on disk + end-to-end writer proof | `scripts/e111_face_factor_stamp.py` → `results/e44_midmonth/FACESTAMP-20261027.json` |

Live id at this commit: `a78d23e15b45`.

## What it reads today

- faces scanned: **70**, stamped with the live factor: **0**, stamped with another factor: **0**,
  unstamped: **70**.
- `burncontrol` status flips from a join that could claim identity (`identical_on_this_face` when the
  means agree) to **`version_unknown`**, with `unstamped = [churnse, churnrobust, churnrobust_s2013]`.
- The published face itself comes back off disk carrying `repair_factor=a78d23e15b45`
  (`writer_proof.stamped_on_disk = true`, `matches_current = true`) -- the stamp path is proven, not
  asserted.

So the honest state after this round: **no cross-face comparison on this panel is currently
licensed**, because none of the faces in the directory records the code that made it. That is a
true statement about the instrument, and it is strictly better than the previous state, which could
not distinguish it from agreement.

## What clears it

Re-burn the twins on the current panel (`run_robustchurn`, `run_churnse` and the 2013-start twin).
Every face written from this commit on carries the stamp, a join of two such faces at one cutoff is
`uniform`, and the control can then speak about the burn instead of about its own inputs.

Deliberately not done here: touching any published number, or inferring a stamp for an old face.
The id is computed from source text including comments -- a wording change is a reason to re-burn,
not a reason to keep joining.

## Verification

```
python scripts/panel_screen.py                     -> 39/39 PASS (4 new legs: id length/stability/CRLF/sensitivity)
python scripts/e39_panel_census.py selftest        -> 324/324 PASS (4 new legs: uniform/unknown/mixed/missing face)
python scripts/e111_face_factor_stamp.py selftest  -> 13/13
python scripts/e111_face_factor_stamp.py run       -> published, writer_proof stamped_on_disk=true
python -m smoke_test                               -> 84/84 PASS
```