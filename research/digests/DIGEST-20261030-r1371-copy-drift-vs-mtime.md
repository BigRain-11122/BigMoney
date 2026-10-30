# r1371 / E280 — a staleness gate that measured the filesystem

**Trigger.** S6 chain leg `etf_book_phase_atlas_arms` exited 1 at 22:05:09 on the full 103-leg run:
`face is inconsistent: 1 field(s) disagree with a re-derivation and no source moved:
.arms.cost0.audit.workers`.

**What the field is.** `workers` is run metadata, not a reading: `build()` copies each arm face's
`audit` block verbatim, so the published face records the worker count of whichever run wrote each
source. Sources on disk: `etf_book_phase_atlas_cost0.json` says 8 (written 14:05:46); the published
arms face says 4. No number computed by the gate disagrees.

**Why the gate called it an edit.** The r1346 split is decided by mtime: a face whose source is
newer is *stale* (refresh), otherwise *inconsistent* (stay red). The published arms face was
restored by the 20:46 checkout, so it carried a 20:46 mtime over 14:05-era content, and the source
looked older. mtime answers "which file was touched last", which every git operation rewrites; it
cannot answer "whose content is newer".

**Fix.** Classify drift by provenance instead of by clock. Leaves `baseline.audit*` and
`arms.<name>.audit.*` are copied from a source face; if one of them differs, the source moved -- so
the face is `stale` (rc=2) and the chain pays the declared refresh. If every copied leaf still
matches while a derived leaf differs, no source moved and the face is `inconsistent` (rc=1) as
before. Copy agreement is positive evidence; the old path only had the absence of a newer mtime.

**Selftest.** 100 -> 102 legs. `L11b` writes a face with one copied audit leaf moved and forces its
mtime 3,600 s into the future so the old rule cannot see it, and demands rc=2. `L11c` adds a
hand-edited verdict on top and demands rc=1 (copy drift may not launder an edit). The first
version of L11b failed honestly: `_diff` emits paths with a leading dot, so the classifier put every
leaf in the derived bucket -- a leg that had only asserted the answer on the real face would have
passed while the classifier was wrong.

**Outcome.** `run` refreshed the face: `git diff --stat` = 1 insertion, 1 deletion (the worker
count). Every published verdict and every cell reading is byte-identical, and the leg is green
(`arms face matches its own sources on cutoff 2026-10-29: buffer_k05=REJECT | cost05=NOT-SEPARABLE |
cost20=REJECT | cost40=REJECT | buffer_k10=NOT-SEPARABLE | buffer_k20=NOT-SEPARABLE |
buffer_k02=NOT-SEPARABLE | buffer_k40=REJECT | buffer_k05_cost20=REJECT | cost0=NOT-SEPARABLE`).

**Open.** Other gates in this repo may still decide staleness by mtime (the r1346 family); this
round fixed the one the chain flagged rather than auditing all of them, and named it here so the
sweep can be claimed deliberately instead of by accident.
