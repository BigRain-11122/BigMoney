# E412 -- the guard decision over E406's blob-read faces (r1431 bm-b, 2026-11-04)

Face: `results/state_tilt/BLOBGUARD-2026-11-05.json` (+ `blobguard_latest.json`)
Study: `scripts/e412_blob_guard_decision.py` (run / verify / selftest 19/19)
Card: `E412-WHICH-LEG-SHOULD-FAIL-WHEN-A-BLOB-READERS-FACE-MOVED`

## Question

E406 published 307 git-object read sites over 126 modules, 25 faces present both at HEAD and on
disk, 5 differing at census time, and 1 module ever comparing the two arms. It never asked which leg
should have gone red. This card answers that as a decision per face: (a) a leg that re-derives the
face and compares it (E387 shape), (b) a leg that refuses a HEAD blob read whose face is newer than
HEAD, or (c) nothing.

## Answer

**25 of 25 on (c). Zero on (a), zero on (b).** The reason is the attribution, not the absence of
consumers.

| reason (frozen) | faces |
|---|---|
| `no_call_carries_the_face` | 18 |
| `only_its_own_writer_reads_it` | 6 |
| `read_only_by_round_scoped_tools` | 1 |
| `every_reader_pins_a_commit` | 0 |
| owed a guard (a + b) | 0 |

Verdict: `every_measured_face_was_attributed_by_a_module_literal_and_no_call_hands_it_to_a_git_reader_so_the_gap_describes_no_consumer`.

## Why

- E406's `reader_rows` are **module-level**: the module's whole face list is repeated on every row.
  `scripts/e340_who_authorizes_whose_allowance.py:430` carries `guardloosen_latest.json` while the
  call there is `head_sha(root)`, which reads no face. Treating those rows as sites yields 41
  consumers; resolving each site by AST taint (does an argument of a git-object call carry the face?)
  yields 0.
- All 25 measured faces carry `basis = module_face_literal`, E406's weakest basis (the one that took
  the face count from 2 to 58). The strong-basis names are the 32 that resolve to no file. A census
  of faces present on disk is therefore a census of the weak basis by construction.
- 3 faces differ from HEAD right now -- `greenwindow_latest.json` (11 keys),
  `guardloosen_latest.json` (4 keys), `repairrecord_latest.json` (4 keys) -- and all three are
  producer-owned: the producer rewrote its own face after the last commit, and the only reader is the
  producer itself. Drift no consumer can see is a freshness question for that face's leg, not a
  blob-vs-file guard.

## Instrument lessons (each one measured after being wrong)

1. **Module row != call site.** First run read E406's rows as sites and produced 41 consumers; the
   real count is 0. Site = a call whose argument carries the face.
2. **A mention is not a write.** `writers_for` v1 (basename present + any write call in the module)
   made all 25 faces "read only by their own writer". Taint from the face name into a write call is
   the test; v2 also needs E408's blind spots closed: a module-local helper
   (`_write(os.path.join(outdir, "facepoppin_latest.json"), doc)` in `e365`) and a `Path` receiver
   (`p2.write_text(...)` in `lane_host_ownership.py`) are writes that E408's `write_evidence` does
   not see.
3. **Leg names come from `_nameNNN`, not from line numbers.** Both the name assignment and the
   `check(...)` call sit outside the `try` node's span, so an AST-only reader names every leg
   `check@<line>`; the name is read backwards from the block and the check forwards past `except`.
4. **Round-scoped readers are not consumers.** `Tools/_r423bmc_marker_repair.py` reads
   `origin/main` on purpose and runs once by name; a later write cannot blind it.
5. **A self-read is not a consumer.** 6 faces are read only by the module that writes them.

## What this means for the repair

Adding (a)/(b) guards to the 25 faces would guard nothing: no call in the measured set hands those
faces to a git reader. The repair is to fix the attribution -- resolve the 32 strong-basis names
(`literal_in_body` / `literal_at_call_site`) that resolve to no file and ask the same site question
there. That is card E413, seeded this round.

## Wiring

- `scripts/e412_blob_guard_decision.py` run / verify problems=[] / selftest 19/19
- smoke leg `# E412:` in `smoke_test.py` (before `# E406:`), proved verbatim by
  `scripts/run_e412_smoke_leg.py` -> 1/1
- S6 leg `blob_guard_decision` in `Tools/s6_chain_bmb.py` -> rc 0, 0.05 s
- pool: E412 done, E413 seeded (ready floor 3: E403, E411, E413)
- no reader and no leg was edited; git was only read