# E393 — the 1 MB read cap was hiding the faces that do store the key

Round r1410 (bm-b), 2026-11-03. Face: `results/state_tilt/READCAP-2026-11-03.json`.
Script: `scripts/e393_read_cap_price.py` (run / verify problems=[] / selftest 15/15).

## What E392 left as a bound

E392 published `share_of_name_matched_reads_that_resolve_and_store = 0.051` and said, in the
summary itself, that 3,292 of its resolved reads opened a face it could not read — **3,271 of them
refused on size** at `MAX_FACE_BYTES = 1 MB`. The aggregate faces (judge files, wave results,
transfer envelopes) are exactly the ones above that cap, so the published 5.1% could not have been
a ceiling.

## What the price is

E392's own `scan` is called with one function swapped: a face above the cap is read in 8 MB chunks
and asked the same question — *does this face store this key* — by matching `"<key>":` on raw
bytes, intersected with the population so 500 MB of corpus cannot inflate memory.

| | with the cap (published) | without the cap |
|---|---|---|
| name-matched reads | 112,910 | 112,910 (drift 0) |
| reads that open a face storing the key | 5,763 | 9,004 |
| share | **0.051** | **0.0797** |
| refused reads | 3,292 | 21 (JSONDecodeError, untouched) |

The 3,271 hidden reads split **3,241 store the key / 30 do not** — the cap was hiding faces that
hold the key at a 99.1% rate, well above the 5.1% it was capping the census at. 195 faces, 270 MB,
7.1 s of scanning. Because the name-matched total is byte-identical, the delta is the cap and not
tree drift — which is the one thing this design could otherwise not prove.

## Three things worth keeping

1. **A cap is a sample, and it is a biased one.** The refused population was 99.1% positive against
   an aggregate of 5.1%: size correlates with what E392 measures (a big judge file stores many
   keys). Any census that refuses on size and still publishes a ratio is publishing a lower bound
   shaped like an upper bound.
2. **The cheap repair is a presence test, not a parser.** `json.load` needs memory linear in the
   file; the question E392 actually asks needs 8 MB of buffer and a regex. 283 MB in 7.1 s means
   the cap should never have been the reason to leave a read unpublished — the refusal reason was
   an implementation limit wearing the costume of a method limit.
3. **Escapes make the byte matcher honest in the direction that matters.** `[^"\\]` between the
   quotes means a key name carried inside a string value cannot match (valid JSON must escape it),
   so the false-positive surface is unescaped `"name":` at any depth — the same "any depth" upper
   bound E392 already discloses, in the same direction.

Two mechanics: swapping a module-level function that the callee looks up at call time (`e392.scan`
resolves `face_key_index` in its own globals) is enough to re-derive the whole census with one
walk — but keep the original in a name first, or the wrapper calls itself and you get a
`RecursionError` from `ntpath.join` three seconds in. And when a study is spliced into
`smoke_test.py`, run the leg through the extracted-verbatim runner (`scripts/run_e393_smoke_leg.py`)
so the published leg is the one that passed.

Wiring: S6 leg `read_cap_price` in `Tools/s6_chain_bmb.py` (168 legs, 0 ghosts; this round ran the
leg's exact `verify` command directly rather than the whole chain); smoke leg E393 (1/1 via
`scripts/run_e393_smoke_leg.py`); pool card E393 closed with `result_ref`, E394 seeded (floor 3/3).