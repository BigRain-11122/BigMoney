# DIGEST — E595: aliasing the pointer face is a no-op, because nobody asks it for that key (r1624 bm-b, 2026-11-09)

**Question.** E594 (r1622) found the bar spelled four ways with no universal spelling, and named
three readers as asking `results/etf_book_order/latest.json` for `evidence_cutoff` — a face that
carries only `as_of`. The obvious repair is one line in the writer: publish the bar under every
name. E594 published that repair as unmeasured, and named its blast radius: an alias can also make a
reader that previously fell through to a default start reading a real value. This study prices the
repair.

**Readings** (`results/state_tilt/BARALIAS.json`)

- **27 faces on disk are named `latest.json`**, and E594 resolves targets by basename. Of the 20
  graded pairs aimed at the pointer face, only **11 name it**; 8 readers were graded silent and
  **3 of them are basename collisions** — `etf_book_bridge.py` reads
  `results/etf_book_production/latest.json`, and in `e403_family_arg.py` / `e446_frozen_writer.py`
  the string appears in their own face names, fixtures and prose.
- **A three-step funnel, and only the last step can move an answer.** Names this face: 3 modules
  (`etf_book_ceo_page.py`, `etf_book_registry.py`, `smoke_test.py`). Names it *and* shows an open
  witness: the same 3. Opens it *and* actually asks it for the key the alias would add: **0**.
  `etf_book_ceo_page` asks only `ticket_file`/`file`/`path`/`ticket`; `etf_book_registry` fetches no
  key at all (it registers the path); `smoke_test` asks `as_of`, which the face already carries.
- **12 flips, 3 of them on a reader that opens the face, 0 on a reader that wants the key.** So the
  bar arm (6 names) moves 12 payload-key grades and no answer. Verdict:
  `aliasing_this_face_moves_no_reader_that_addresses_it`.
- **The hazard arm flips 3 pairs** (`etf_book_ceo_page`, `etf_book_order`, `smoke_test`): aliasing
  `book_decided_at`/`decision_bar` to the pricing bar supplies a *decision* instant that never
  existed. A decision bar and a pricing bar are two instants (E586 measured the ticket printing
  both), so that arm fabricates an answer; it is published beside the repair arm and never counted
  into it.
- **Zero default-fallback sites**: among the three modules that actually open the face, `.get(name,
  default)` on any of the 12 alias names returns **0** hits — the "alias overrides a default"
  exposure is empty here, not merely unseen.

**Verdict.** `aliasing_this_face_moves_no_reader_that_addresses_it_because_the_silent_ones_name_a_different_face`.

**Lessons.**

- Same basename is two populations (E366 one layer down). Resolving a target by basename merges 27
  faces into one, so "this reader wants a key that face lacks" may be a reader of a *different*
  face. The discriminator is the directory in the reader's own literal, and folding an
  `os.path.join` must tolerate a leading constant name (`ROOT`) or the directory is thrown away and
  the collision is recreated.
- Naming is not opening is not fetching (E470, one hop further). Publish all three — addressing,
  open witness, key set — because "the reader that needs fixing" lives only in the third layer.
  `etf_book_ceo_page` passes the first two and is empty in the third: it opens the face and never
  asks for that field.
- Price a repair by the people who want the key, not by the keys it adds. Twelve flips against zero
  real readers says the missing field has **no demand in this chain** — the finding a payload-key
  grade alone cannot produce (it produces 12).
- The hazard arm must be published beside the repair arm. Both arms "supply the name"; they differ
  only in the semantics of the name. Merged, or reported as a flip count, a fabricated decision bar
  reads as a repair.
- The default-fallback exposure needs its own field. An empty `default_fallbacks` is the difference
  between "nothing moved" (a conclusion) and "nothing could move because nobody has a default"
  (a boundary).

**Limits.** Addressing is decided from each reader's own string literals; a runtime-composed path is
visible only through the parts it spells. The open witness is a deliberately weak line-local test
(the literal within ±6 lines of `open`/`json.load`/`read_text`), so a module without a witness is
published as *unwitnessed*, not as *not reading*. The key set resolves a payload binding up to four
hops (`x = json.load(open(...))`, `x = _load(POINTER)`, module constants); an unresolvable binding is
published as `payload_binding_resolved=false` rather than counted as asking for nothing. The alias
arms exist only in memory — the pointer face on disk was not written by this study.

**Evidence.** `scripts/e595_pointer_alias_blast.py` (selftest 36/36, check/verify problems=[]),
`scripts/run_e595_smoke_leg.py` (PASS, 1/1 red under `--doctor`), `results/state_tilt/BARALIAS.json`
(+ `-latest`), S6 leg `pointer_alias_blast` (rc0 5.12s), smoke leg `E595` (45 added lines, 0 deleted).