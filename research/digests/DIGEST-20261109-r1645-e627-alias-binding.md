# DIGEST-20261109-r1645 — E627: the alias hole E625/E626 published is empty

**Card** POOL E627 `E627-WHETHER-THE-OBJECT-A-DEAD-FACE-KEY-LINE-READS-IS-ALSO-BOUND-TO-ANOTHER-NAME`
**Round** r1645 bm-b · 2026-11-09 · lane cpu-only · static, no runner, no fixture write
**Face** `results/state_tilt/ALIASBINDING.json` (+ `aliasbinding_latest.json`)
**Tool** `scripts/e627_alias_binding.py` (selftest 26/26, run/check/verify `problems=[]`)
**Wiring** `scripts/run_e627_smoke_leg.py` (1/1 PASS, `--doctor` 1/1 red, face restored byte-identically)
+ `smoke_test.py` leg E627 + `Tools/s6_chain_bmb.py` leg `alias_binding`

## The question

E625 (r1643) priced the value test and E626 (r1644) followed the one handover into its callee. Both
publish the same limit in their own faces: **no alias analysis**, so a write through a second local
name bound to the same dict is invisible to both. That is the last stated hole in the key → object →
value → handover stack, and this card prices it.

## The reading

* population: 34 live dead face-key lines / 4 same-object duplicate rows, 1,099 modules, 14 self-excluded
* **125 second-name bindings in the intervals**, classified by what the right-hand side actually is:

| class | count |
|---|---|
| a second name bound to **the same object** (`alias = recv`, `alias = previous alias`) | **0** |
| a second name bound to **a value of the receiver** (`v = recv.get(k)` / `recv[k]`) | 3 |
| a second name bound to **the receiver's items** (`for k, v in recv.items()`) | 0 |
| a second name bound to **a copy of the receiver** (`recv.copy()` — a different dict) | 0 |
| a second name bound to **something else** | 122 |

* 0 duplicate rows carry a same-object alias; 0 are written at the key through one (named / unnamed /
  handed to a call all empty)
* corrected split **4 survive / 0 stored / 0 undecided** — item-for-item the same as E626's 4/0/0
* all 19 same-object sibling reads land in `the_alias_scan_has_nothing_to_say`
* E626 cross-check: the 34 lines re-parse row-for-row and class-for-class (0 differences)

**Verdict** `no_second_name_is_bound_to_the_receiver_in_any_of_the_4_duplicate_intervals`

## What it means

The hole is empty, and that is worth having: it upgrades E625's "the value really was not rewritten"
to "not rewritten even through an indirect name", so 4/0/0 no longer rests on the luck of nobody
using an alias. It also prices the denominator: 122 of 125 bindings are just another expression bound
to a name — folding them into "might hide a write" would inflate the population 40× and move nothing.

## Rules worth reusing

1. Same-object-ness is decided by **the shape of the right-hand side**, not by how the names look.
2. Only SAME_OBJECT is a dangerous class; the other four need **their own names and counts**, or a
   reader cannot tell "there were none" from "they were merged away".
3. An alias window has a **lower bound**: after `alias = other` a write through that alias says
   nothing about the receiver — that leg is pinned as its own selftest.
4. The instrument must not claim what it can close: `duplicate_rows_the_alias_scan_can_close` has to
   equal the number of duplicate rows whose scan class is stores-over, both counts re-derived from
   the rows and asserted against each other.

## Bounds (published, not claimed)

No alias bound **before** the function body (a module-level name), no rebinding through a container or
a comprehension, no attribute/class resolution, no interprocedural descent. If the receiver itself
arrives through a container element or a module-level dict, E627's interval is not where the object
began — that is seeded as **E628** (`results/state_tilt/RECEIVERORIGIN.json`).

## Instrument note found in this window

The script arrived untracked and complete from a dead window, but its leg "a row with no alias
anywhere has nothing for the scan to say" pointed at a fixture function with only one read — a row
that is not in the population at all, so the leg could not pass. The fix was to give the fixture a
real population row with two reads and no alias (`plain_two_reads`) and to make the leg assert its
whole class (`binds_of` empty, scan nothing-to-say, duplicate survives), not to relax the assertion.