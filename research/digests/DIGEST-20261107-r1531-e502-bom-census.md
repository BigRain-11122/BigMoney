# DIGEST 2026-11-07 r1531 bm-b — E502: what the nine BOM sources cost the published censuses

**Card**: E502-DOES-THE-BOM-SOURCE-LIST-CHANGE-ANY-PUBLISHED-CENSUS
**Study**: E502_bom_census
**Face**: `results/state_tilt/BOMCENSUS-2026-11-07.json` (+ `bomcensus_latest.json`)
**Script**: `scripts/e502_bom_census.py` (run rc0 / check problems=[] / verify identical / selftest 24/24)
**Verdict** (recomputed by the gate from the rows, never written by hand):
`at_least_one_published_payload_moves_when_the_bom_sources_parse`

## Question

E495 disclosed nine sources in the shared canonical scan that begin with a UTF-8 BOM, and
showed that one of them (`scripts/e429_two_hop_writer.py`) makes `ast.parse` raise. E495
stripped the BOM for its own face and left the rest unpriced: every other E-series study
that reuses the same read still reads those nine files as text that names nothing. How much
of the published census body was built on a corpus that silently held nine fewer files?

## Method (four arms, static, no network)

| arm | what it measures | population |
|---|---|---|
| A | which sources begin with a BOM | canonical scan 364 sources / 9 BOM; full tree 215 BOM of which **206 outside the canonical scan** |
| B | does the reader strip the BOM before parsing | 201 modules with `build()`: **83 parse raw**, **11 strip**, 107 never parse source text |
| C | is a BOM source inside that study's own corpus | 9 in corpus / 9 not / **183 unmeasured** (no zero-argument `corpus()`) |
| D | does the payload change when the BOM is stripped | 7 exposed studies, each built twice in a subprocess, structural diff |

Every write a replay performs is backed up before it happens and restored afterwards, with a
per-file assertion; a failed restoration is a gate problem.

## Readings (2026-11-07, replay budget 900 s)

* **3 of 7 replayed payloads move — 56 field positions in total**:
  * `e442_deadpath` — 40 positions, `rows` 17797 → 17978
  * `e429_two_hop_writer` — 15 positions, `rows[4].caller_hits` 37 → 38
  * `e432_fixture_write` — 1 position
* **4 unchanged**: e419_unstampable, e423_dirfield_join, e448_dropped_path, e467_docstringcard
* **5 at risk** — parse raw, a BOM source is inside their corpus, and the payload never names
  the source it could not parse: e419, e423, e432, e442, e448
* `replays_that_wrote_a_file` = 1 (e467 wrote `DOCSTRINGCARD-2026-11-07.json` and
  `docstringcard_latest.json`), `restores_that_failed` = 0

## The finding that matters most: the budget was deciding the reading

The same code at a **240 s** budget priced `e429_two_hop_writer` as `timeout after 240s`
(i.e. unmeasured) and published **2 changed studies / 41 positions**. The measured cost of
that study's two arms is **231.9 s / 237.0 s — 99 % of the old budget**. At **900 s** the
same study publishes 15 changed positions and the reading is **3 / 56**.

So the instrument's clock, not the corpus, chose between two defensible-looking answers, and
both runs "passed". The fix is not a bigger number on its own: the budget is now published in
the face beside the superseded reading and the measured arm times.

## Reusable rules

1. **Ask "can this study even read that file?" before "what happens when it does".** 183 of 201
   studies expose no zero-argument corpus; publishing them as `safe` would have turned a bound
   into a claim. They are published as `unmeasured`.
2. **A stripping reader is not automatically stable.** `e429_two_hop_writer` strips the BOM and
   still moves: stripping lets one previously unparsable source appear, so `caller_hits` goes
   37 → 38. "Already handled the input" and "the answer does not depend on the input" differ.
3. **Disclosure means naming the dropped source**, not just handling it. The silent/disclosed
   split is decided by whether a readable field in the payload names the source it could not
   parse.
4. **A timeout is a measurement, not a defect.** It gets its own class, and any timeout that
   fires must be re-priced at a budget several times the slowest observed arm — otherwise a
   loaded box silently rewrites a published count.

## Boundaries

Arm B classifies a reader by source text, not by running it. The diff is structural (dotted
paths), so a re-ordered list of equal elements reads as a change, and it is capped at 40 rows.
Arm C can only test a zero-argument `corpus()`; a study whose corpus needs arguments is
`unmeasured`, never `safe`. Both populations are published because a per-study corpus walks
206 files the canonical scan never sees.

## Wiring

* S6 leg `bom_census` in `Tools/s6_chain_bmb.py` (rc0 0.07 s)
* smoke leg `E502 ...` in `smoke_test.py` + `scripts/run_e502_smoke_leg.py` (doctored arm red)
* pool card E502 → done; supply floor refilled
* methodology card E502 in `knowledge/METHODOLOGY_ASSETS.md`