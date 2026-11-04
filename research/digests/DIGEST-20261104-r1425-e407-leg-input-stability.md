# DIGEST 2026-11-04 r1425 bm-b -- E407: the card's own instance does not have the mechanism it names

**Card.** `E407-DOES-A-SMELL-TEST-LEG-READ-A-FACE-AN-EARLIER-LEG-REPUBLISHES`, seeded by the r1422
postscript when the E305 leg re-red twice in one window. The premise was explicit: "That build reads
sibling faces ... which OTHER legs of the same suite republish earlier in the run."

**What was measured.** Not the premise -- the object. `e305.build()` reads exactly the `faces_named`
of the at-risk rows in the census it consumes: 14 rows, 13 distinct faces, all 13 present on disk.
A literal scan of `scripts/`, `Tools/`, `monitor/`, `live/`, `firm/` finds a writer in the tree for
**13 of 13** -- so the input set is mutable, but between rounds. Inside a run the question is
decidable: of the 236 statically attributable leg groups in `main()`, **0** import one of those 13
writers and call a write verb on it, and **0** run one as a non-selftest subprocess. Order pairs: 0.

**Verdict** (recomputed by the gate, not written):
`no_leg_in_the_suite_executes_a_writer_of_any_input_face_so_the_leg_is_order_stable_and_the_pinned_columns_are_the_audit`.

**Why the leg re-red anyway.** The E387 republish leg compares each covered face *on disk* against
the fresh column the audit stored when it last ran. That column is pinned to 2026-11-03. Nothing in
the suite moves the face; the round does. Re-running `e387_republish_audit.py run` this window moved
0 faces and the leg went green in the same minute -- the same conclusion the r1424 postscript had to
learn the hard way after predicting a commit would clear it.

**The same window's other red, and why it was already fixed.** The suite read 303/305 at 07:58 with
two FAILs: the E387 leg (cleared by the audit re-run above) and E398's own leg, whose verify said
"family-named pointer count moved: 180 vs 178". That is a corpus move, not a defect: rounds after
E398 published two more studies with `*_latest.json` pointers. The face was re-derived from the live
build (verify `problems=[]`, 187 readers / 162 named-at-site / 17 by signature / 7 self-written / 1
unsupplied) and the leg passes standalone. **Loosening either assertion was available and is not
what happened.**

**Bound.** 236 attributable leg groups vs the suite's own leg count -- legs executed from helper
functions and loops are outside a static region model, so both counts are published and the gap is
not folded into either. The within-run claim rests on the static leg-to-writer analysis; the face
carries the 13 input hashes so a pre/post hash probe over one full suite run can confirm it without
rebuilding anything. That probe is not run this window and is stated as not run.

**Artifacts.** `scripts/e407_leg_input_stability.py` (selftest 11/11, verify `problems=[]`);
`results/state_tilt/LEGINPUT-2026-11-04.json` + `leginput_latest.json`; smoke leg E407 (1/1 via
`scripts/run_e407_smoke_leg.py`); S6 leg `leg_input_stability` (rc 0, 3.3 s); card E407 in
`knowledge/METHODOLOGY_ASSETS.md`. The card's deliverable name said `LEGINPUT-2026-11-05.json`; a
future-dated face is future data, so it is dated today and the deviation is recorded on the face.