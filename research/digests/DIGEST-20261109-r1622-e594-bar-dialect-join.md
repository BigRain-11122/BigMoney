# DIGEST — E594: the bar is spelled four ways and no spelling is universal (r1622 bm-b, 2026-11-09)

**Question.** E586 (r1621) closed the consumer-side question — zero silent readers, zero
money-carrying surfaces that omit the bar — and left one residue: the bar is written `pricing_bar`,
`ticket_bar`/`evidence_cutoff`, `as_of`, and in prose. A reader that asks for a spelling the face it
reads does not carry gets `None`, which renders exactly like a bar with no value.

**Readings** (`results/state_tilt/BARDIALECTJOIN.json`)

- 21 in-repo readers address a ticket; **13 name a published face this census can resolve**, 8 name
  only fragments (published as `unresolved`, which is not evidence of a broken join).
- They spell the bar in **4 dialects**: pricing(11), decision(10), evidence_cutoff(16), as_of(11).
- Across **27 candidate faces no spelling is carried by all of them** → a consumer cannot join on one
  name; it needs a per-face hand map.
- **88 graded (reader, spelling, face) pairs, 48 miss.** Because a wide-naming module crosses every
  spelling with every face it names, that pair count is published as the broad arm, never deciding.
- **3 readers miss on every pair they can make** — the class where the join silently returns nothing:
  `scripts/e403_family_arg.py`, `scripts/e446_frozen_writer.py`, `scripts/etf_book_bridge.py`. All
  three ask `latest.json` for `evidence_cutoff`; the pointer face carries `as_of` and **no**
  `evidence_cutoff`, `pricing_bar` or `book_decided_at` (keys: `as_of`, `k_now`, `beta_target`,
  `file`). That pointer face is the one the CEO page follows.
- 10 readers can obtain the bar from at least one face they name.

**Verdict.** `some_reader_asks_for_a_spelling_the_face_it_reads_does_not_carry`.

**Lessons**

- A reader population crossed with the faces each reader names is a Cartesian product; grading every
  cross product as a join turns `smoke_test.py` (which names nearly every published face) into nine
  silent readers. Two arms are required: per-pair (breadth, published) and per-reader-all-pairs-fail
  (deciding).
- A missing spelling and an empty value are the same observation at the call site, so "did the reader
  get a bar" cannot be answered by the reader alone — it needs the face's own key set.
- The pointer face's dialect is the dialect the human page inherits: fixing the ticket's spelling did
  not fix the pointer.
- Self-inclusion: this study's own literals are the spelling table, so it must be excluded from its own
  reader population (E180/E207/E319 family, caught in the first build).

**Limits.** Static matching cannot prove a join runs (a literal may build a path or be logged); each
pair carries the literal family that produced it. A reader with no resolved target is `unresolved`,
not broken. Text faces are graded by name occurrence, so prose that never names the field reads as
not carrying it.

**Evidence.** `scripts/e594_bar_dialect_join.py` (selftest 27/27, `check`/`verify` problems=[]),
`scripts/run_e594_smoke_leg.py` (PASS, 1/1 red under `--doctor`), `smoke_test.py` leg E594,
S6 leg `bar_dialect_join` (rc0, 2.00s).