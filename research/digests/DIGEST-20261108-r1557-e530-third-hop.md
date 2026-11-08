# DIGEST 2026-11-08 r1557 bm-b — E530: the third hop

**Question.** E526 published that the chain is still moving in 2 parcels (`e489_write_wire.classify(root)`
forwards `root` at every call site; `e328_quoted_number_staleness.build(root)` is handed a local at 3
of 4 sites). "Still moving" names a position, not an origin.

**Method.** The 5 second-hop hand-overs that are again a parameter or a local are followed one hop at a
time with the same machinery (E526's `hop_of_parcel` + E520's classifier and parameter tracer, imported
not cloned), capped at 6 hops. Each chain is published with every hop, the terminal kinds, `hops_to_origin`,
and one of six shapes: ends at a value this tree writes or reads / some arms reach a value and some end
at a signature default / ends at a signature default / dead-ends on a parameter no call site supplies /
loops back into a function it already visited / still moving at the cap.

**Readings (5 chains, 2,743 sources).**

- 3 chains end at a value — all of them "the result of another call", 1 hop past the second.
- 1 chain is mixed: one arm reaches a call result at 2 hops, the other 7 sites omit the parameter and
  take the signature default.
- 1 chain ends at the signature default only (1 hop, no `hops_to_origin`).
- 0 dead ends, 0 loops, 0 chains at the hop cap. Verdict (re-derived by the gate):
  `some_chain_ends_at_a_signature_default_rather_than_at_a_caller`.
- Named: `e328.build(root)` ×3 are locals bound by `_fixture()` / `mkdtemp()` calls; `e489_write_wire.build(root)`
  omits `root` at 8 sites (default) and at one site forwards 2 cross-module locals (`dates` in
  `etf_book_capacity_carry`).

**Reusable lessons.**

1. "One parcel is still moving" and "one value is still moving" are not the same count — 2 parcels expand
   to 5 chains, and using the parcel count as the denominator reads 5 values as 2.
2. A mixed chain must be its own shape: publishing only "reaches a value" hides the 7 sites nobody supplies.
3. A branching chain's depths are not `1..n` (the real sequence is [1,2,2]) — the gate must assert
   "starts at 1 and never jumps up by more than one", which a first-draft `range()` equality failed.
4. A fixture value is a written value but not a production supply; the face records it as a call result
   and leaves that distinction to its readers.

**Wiring.** S6 leg `third_hop` (0.06s) + smoke leg `# E530` (executed verbatim through
`scripts/_r1557_leg530.py`). Face: `results/state_tilt/THIRDHOP-2026-11-08.json` + `thirdhop_latest.json`.
Not run: the full smoke suite, the rest of the S6 chain, the collectors and the market/paper chain.