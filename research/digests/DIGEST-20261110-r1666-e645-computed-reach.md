# r1666 bm-b — E645 prices E644's own published residual, and the answer is container identity

**Card:** E645 — whether a depth-1 store whose subscript is computed can reach a counted row key.
**Face:** `results/state_tilt/COMPUTEDREACH.json` (+ `computedreach_latest.json`)
**Tool:** `scripts/e645_computed_subscript_reach.py` (selftest 13/13, `run` / `check` / `verify` / `--help` all rc0)
**Legs:** `scripts/run_e645_smoke_leg.py` 1/1 green, `--doctor` goes red and restores the face byte-identically (sha d42b4ce1dec0 in and out); `Tools/s6_chain_bmb.py` leg `computed_reach`

## What was open

E644 closed the two-depth census's blind spot with a literal-only reading and said so itself: 22 of
the 32 depth-1 Store/Del sites in the counted functions subscript with an expression rather than a
string constant, so "no site names a counted row key" is a statement about **spellings**, not about
values. A computed subscript could equal `days` / `slip_exec` / `verdict` at run time and no reader
of E644's face could see it.

## Two gates, published side by side

| gate | question | states |
|---|---|---|
| key | can the subscript evaluate to the counted key? | `resolved` (finite string set) / `not_a_string_key` (tuple key, non-string constant, slice) / `unresolved` |
| container | does the store write into the object a counted read line reads? | `same_name` / `alias` / `another_object` |

A site reaches the counted mapping only when **both** gates open. The container gate is the stronger
one: a matching key written into a different dict cannot change the value the counted line reads,
whatever the subscript evaluates to.

## Readings

| | |
|---|---|
| computed-subscript depth-1 stores | 22, in 3 of the 6 counted functions |
| domain states | 9 resolved / 3 not_a_string_key / 10 unresolved |
| domains that hit a counted read key | **0** (all 9 resolved sets are `CORE_DD10 … SAT40_DD20` cell names) |
| stores writing into the read container | **0** (0 via alias) |
| sites reaching a counted row key | **0** |
| excluded by container identity **alone** | 10 (the unresolved domains whose container is another object) |

The 9 resolved domains are the loop targets over `JUDGED_CELLS`, so they enumerate cleanly and none
of them can spell a row key. The 10 unresolved ones are parameters, call results, attribute or slice
expressions — and every one of them writes into a container bound inside its own function
(`cell_recs`, `judged_series`, `g1`, `dsr`, `g2`, `row`, `same_batch`, `stable`, `descriptive`,
`gate_axis`, `leg_counts`, `sat_picks`, `per_face`, `cells_out`, `mask_k`, `rb`, `r_nav`, `ser`,
`h_day`, `cost_day`, `numbers`, `verdicts`), never into `P` / `faces`, the objects the counted lines
read. That is why 10 sites are excluded **structurally** rather than by value.

## The reusable lesson

**When one gate cannot be decided, look for a second gate that makes the first one irrelevant — then
publish both, and name which one carried the verdict.** E644's residual looked like it needed a
runtime tracer. It needed a container-identity check: the counted read lines read `P['days']` and
`faces['verdict']`, and all 22 computed stores write into fresh local dicts, so the value a computed
subscript could spell never reaches the counted mapping. Quoting only the key gate would have said
"10 sites undecidable"; quoting only the container gate would have hidden that 9 domains actually
resolve and exclude the key by value. Neither reading alone is the answer.

Two supporting rules:

1. **`not_a_string_key` is a third state, not a miss.** A tuple subscript (`cell_recs[(cell, face)]`),
   a non-string constant and a slice can never equal a string row key regardless of value — folding
   them into `unresolved` would inflate the undecidable count with shapes that are decided.
2. **A resolved value set must be the set the expression can take, not the set it was tested with.**
   `_resolve_name` follows loop targets over literal collections, local assignments over literals and
   module-scope literals at most three hops; a parameter, call result, attribute or f-string stays
   `unresolved` rather than being published as an empty set.
