# E320 -- is the decoy avoidable? (r1340, bm-b)

Face: `results/state_tilt/DECOYRESOLVE-2026-10-31.json` (+ `decoyresolve_latest.json`)
Runner: `scripts/e320_decoy_resolution.py` (run / verify / selftest 14 legs)
Upstream: `results/state_tilt/PRINTCOV-2026-10-31.json` pinned at commit `6266c617b`

## The question

E317 published 225 gate leaves whose own block offers at least two positive numbers a reader
could substitute for the quantity the gate is rated in, and quoted the substitution span as the
cost of getting it wrong. E318 then removed the leaves that are counts of gates. This study takes
the **219** leaves that survive and asks the only question that decides whether E317's span is a
risk or a worst case: **is the quantity itself in the block?**

## Readings

| class | rows |
|---|---|
| resolved_by_name (the gate's own key points at exactly one candidate) | 16 |
| resolved_by_copy (the gate's magnitude printed twice) | 7 |
| ambiguous (two or more identifications) | 62 |
| unresolved (no identification at all) | 134 |

- **23 of 219 (10.5%) are avoidable** by a reader who reads the whole block; **134 are not**:
  the block publishes numbers in the same unit and nothing that names or fingerprints the gated
  quantity, so E317's span is the truth for those and a worst case for the rest.
- After the identified candidate is removed the **median span falls 1.979 -> 1.347 decades**
  (165 rows carry a residual span; 54 rows have no residual ambiguity at all). The maximum,
  19.59 decades, is untouched: it is an unresolved row (`results/shortline/p1e_equiv.json`, a
  bare `tol`).
- The quantity's **name comes from the gate's own key on 108 rows**; on 96 the key says nothing
  but `tolerance`, and on 15 the key names only a unit (`*_tolerance_bp`), so those rows can only
  be resolved by the fingerprint channel. 44 of the 57 faces in the population carry at least one
  unresolved leaf.

## Why the naive rule answered "ambiguous 159"

Two mechanical errors, both caught before publish:

1. **The block label is in every candidate path.** Matching the gate's stem against the *full*
   path makes every sibling match by construction (the first cut reported 159 ambiguous rows and
   a block named `recovery_known_answer` matched all five of its own numbers). Matching must be on
   the path with the block prefix removed.
2. **A unit word is not a quantity name.** `residual_tolerance_bp` stems to `bp`, which names
   every number in the block. Unit words are dropped from the stem and the row is published as
   `gate_key_unit_only`.

And the fallback that was tried and withdrawn: when the key names nothing, the block's own name
is *not* a statement about the quantity. It was used for one draw (95 rows) and turned a real
population into manufactured ambiguity; the published rule now leaves those rows unresolved and
says so.

## The control, and why the input has to be pinned

The study reproduces **every one of the 219 published spans** from the block it re-reads --
but only after pinning the input to the commit that carries `PRINTCOV`. Read from the live
worktree, three rows fail to reproduce, because those faces were rewritten after E317 scanned
them (`GATETOL-2026-10-31.json` carries 1774 added / 143 deleted lines in the worktree, and
`PRECISIONCENSUS-2026-10-29.json` had its `by_kind.exact_equality` moved 22 -> 26 by a later
round). A census over a mutable directory measures the directory; the face publishes
`base_commit` and `read_sources` so the population it counted is recoverable (E319/r1339 family,
third contact).

## Law (card E320)

An ambiguity span is a bound on a *careless* reader, not on a careful one. Before quoting the
span as risk, ask per leaf whether the quantity is published, and price the residual after the
identified candidate is removed; where it is not published, the span is the reading and the
block is simply undecidable from itself.