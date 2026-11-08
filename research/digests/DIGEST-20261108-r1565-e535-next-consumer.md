# DIGEST 2026-11-08 r1565 (bm-b) -- E535: the «handed onward» class is five shapes, not one

**Card**: E535-WHICH-SENTINEL-A-READER-HANDS-ONWARD-IS-CONSUMED-BY-A-CALLER-THAT-WRITES-A-PAYLOAD
**Face**: `results/state_tilt/NEXTCONSUMER-2026-11-08.json` + `nextconsumer_latest.json`
**Tool**: `scripts/e535_next_consumer.py` (run / check / verify / selftest)
**Upstream**: `results/state_tilt/captopayload_latest.json` (E534, sha-pinned in the face)

## What was asked

E534 followed every depth-cap arm of E529 into its reader and published what the reader does with
the value. Six sites it published as "the value leaves the reader" (five forwarded, one carried
into a field of a container no reader writes) were left open by its own limit: the next consumer
was not followed. So "does the cap reach a payload as the claim that the thing is not there" was
structurally unanswered for exactly those six.

## What was measured

Six sites, 2,758 sources (1 syntax failure), static only, nothing executed.

| outcome | sites | where |
| --- | --- | --- |
| reaches a consumer that writes a payload / sentence / count | 0 | -- |
| assembles a field and writes nothing either | 0 | -- |
| the hop is a builtin test at the site (`isinstance`) | 3 | e503 `module_consts`:148, `chain_legs`:165, `script_refs`:223 |
| the hop is a library call (`sorted`) | 1 | e504 `analyse`:452 |
| the read is already inside a non-null guard in the reader | 1 | e379 `_why`:178 read at 181, guard at 179 |
| genuinely forwarded again | 1 | e398 `_resolve_module_chain`:410 -> 3 consumers all forward again |

The gate recomputes the verdict from the summary:
`the_handed_on_class_is_not_one_shape_part_of_it_never_reaches_a_second_reader_and_part_is_still_moving`.

## Why this is not the same number as E534's

E534's "forwarded" was a statement about a call site made by a one-hop flow walk. One hop further,
four of those five sites turn out never to leave the reader at all: `isinstance(value, str)` is a
test performed on the value where it already is, and `sorted(...)` hands it to a body that is not
in this corpus by design. One more is separated by a guard in the reader's own body, which E534's
classifier does not weigh: the `return` that carries the value sits inside `if resolved is not None:`.
Only `_resolve_module_chain`'s return is still moving three hops out.

## Instrument notes

* **guard before hop kind.** A read inside a branch that already compared the value against
  non-null cannot be a null carrier; classifying it as a forward is treating a guard as air.
* **a builtin name is not an unresolvable callee.** `isinstance`/`sorted` have no body in the
  corpus by construction. Folding them into "callee not defined" publishes two different things
  under one name; tests happen in place and transforms enter a library, each needs its own class.
* **destructuring hides a binding** (E519 family). `why, target = _why(...)` is invisible to a scan
  that records only `ast.Name` targets, so the second consumer reads as "stops inside". This face
  adds the arm; the fixture proves it follows the destructured piece to its writer. No row of the
  real population needed it (the guard row resolved first), so the arm is fixture-proved only and
  published as such.

## Wiring

* S6 leg `next_consumer` (rc0, 0.06s), registered after `cap_to_payload`.
* Smoke leg `# E535` (1/1) + `scripts/run_e535_smoke_leg.py --doctor` (1/1 doctored verdict refused).

## Not run this window

The full smoke suite, the rest of the S6 chain (collectors, market/paper lanes) were not launched;
no suite total is claimed.