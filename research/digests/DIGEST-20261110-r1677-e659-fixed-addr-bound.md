# DIGEST 2026-11-10 r1677 bm-b -- E659: how many times a fixed-address loop write writes

**Card** E659 (pool head, watermark red: pool-batch-runnable-idle-low-cpu / ready 4 / py 1.7%).
**Face** `results/state_tilt/FIXEDADDRBOUND.json` (+ `fixedaddrbound_latest.json`), 149 rows.
**Script** `scripts/e659_fixed_addr_bound.py` (selftest 22/22; build/check/verify problems=[]).
**Wiring** smoke leg E659 (+ `scripts/run_e659_smoke_leg.py`, `--doctor` red and byte-restored,
sha `351323f93562`), S6 leg `fixed_address_bound` (wired, not run this round).

## What was asked

E653 split the 845 loop-guarded residual module-level write sites by address shape: 696 compute the
address from the loop target, 149 repeat one address every pass. That split answers *what the body
writes*; it says nothing about *how many times it writes it*. A fixed-address site inside
`for x in range(3): P['k'] = x` performs three writes of one key -- two are dead stores. A
fixed-address site inside `for x in rows: P['k'] = x` does the same, but the source never states the
count. E659 prices both.

## What was measured

| reading | value |
|---|---|
| fixed-address loop write sites (E653's last-write-wins) | 149 |
| bound the source states (exact) | 63 (42.3%) |
| bound not readable (unknown) | 84 |
| site inside a `while` (no bound by construction) | 2 |
| dead stores removed by collapsing the exact ones | 163 |
| exact bound median / max | 3 / 13 |
| bounds that came through a module-level constant chain | 46 |

Exact-bound histogram: `2 -> 24`, `3 -> 30`, `4 -> 1`, `6 -> 1`, `9 -> 1`, `10 -> 3`, `13 -> 3`.

Cross-class by iterable form (the reading E653 could not make):

| iterable form | exact | unknown | while |
|---|---|---|---|
| literal_container | 24 | 0 | 0 |
| module_constant | 39 | 7 | 0 |
| bare_name | 0 | 58 | 0 |
| call | 0 | 14 | 0 |
| enumerate_call | 0 | 2 | 0 |
| attribute_or_subscript | 0 | 2 | 0 |
| other | 0 | 1 | 0 |
| condition_compare | 0 | 0 | 2 |

Unknown reasons: `bare_name_bound_not_statically_known` 60,
`call_bound_not_statically_known` 15, `member_read_bound_not_statically_known` 4,
`comprehension_bound_depends_on_its_generator` 4, `form_not_recognised_as_a_static_bound` 1,
`a_while_loop_has_no_static_iteration_bound` 2.

## The reading that matters

**`module_constant` is not one thing.** E653 labelled 46 sites `module_constant`; E659 resolves the
binding chain and finds 39 of them bottom out in a literal container or a `range` over resolvable
integers (exact), and 7 bottom out in a call or a comprehension (unknown). A label that says "the
loop iterates a module-level name" reads as "the bound is in the source" to anyone who does not open
the binding; for 7 of 46 it is not. This is the same family as E653's own `loop` label -- a bucket
that names *where the expression is written*, not *what it evaluates to*.

**42.3% of the repeated writes are dead stores the source already prices.** 163 writes are removed
by collapsing 63 loops that write one address N times. The remaining 84 are real repeated writes
whose count no reader can quote -- and 58 of those are bare names, which is the shape a function
parameter or a set built at runtime produces.

## Lessons (for the card)

1. **A bound is a syntactic promise, not a loop count.** `break`, a `return`, or a raising guard
   shortens the run and this ruler does not look for them; the face says so in `limits` rather than
   pretending the number is a runtime measurement.
2. **Resolve the label before you report it.** `module_constant` splits 39/7 the moment the binding
   chain is followed; publishing the label as if it were a reading is how a bucket becomes a claim.
3. **Reconcile against the predecessor's face row by row, not by count.** `only_in_source_face` is a
   hard red (the population shrank); `only_in_this_build` is disclosed growth. Both directions are
   published so a later reader can tell a tree that grew from a ruler that changed.
4. **Cheap verify beats expensive re-measure when the face names its own evidence.** Every row names
   a module and a position, so `verify` re-parses only those files and re-derives the bound (149 rows,
   problems=[]), instead of re-walking 13k files to prove the same reading.

## Evidence

- `scripts/e659_fixed_addr_bound.py` (selftest 22/22; build rc=0 188s; check/verify problems=[])
- `results/state_tilt/FIXEDADDRBOUND.json` + `fixedaddrbound_latest.json` (149 rows)
- `scripts/run_e659_smoke_leg.py` (1/1 PASS; `--doctor` red_legs=1 and sha `351323f93562` restored)
- `smoke_test.py` leg E659; `Tools/s6_chain_bmb.py` leg `fixed_address_bound`
