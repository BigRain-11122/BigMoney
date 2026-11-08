# E526 — the second hop of the 12 arguments E520 said are forwarded again (r1556 bm-b)

**Question.** E520 followed E519's non-answers one hop and published that 12 of the 20 values
handed to a forwarded parameter are *again* a parameter or a local one level up. It published that
as one number, `arguments_forwarded_again`. A single number cannot say where the chain ends.

**Measurement.** Each of those 12 forwarding call sites becomes a parcel. For a forwarded
**parameter**, the parcel is followed through every call site of the function that owns that
parameter (E520's tracer, imported rather than cloned); for a forwarded **local**, the parcel is
followed to the statement inside the caller that binds the name and to what that statement binds it
from. Each parcel gets an arrival class that keeps two answers apart:
`resolved_at_the_second_hop` (the value is written, computed, called or read right there) versus
`forwarded_again_at_the_second_hop`.

**Reading.** 12 parcels (4 parameters / 8 locals) over 2,741 sources, 23 second-hop hand-overs:

| second-hop kind | sites |
|---|---|
| a literal written at the site | 9 |
| the result of another call | 6 |
| a parameter / a local, i.e. forwarded again | 2 / 3 |
| nothing passed, the signature default applies | 3 |

Arrivals: 9 resolved, 1 forwarded again, 1 mixed, 1 default-only, 0 with no supplying site.
Verdict (re-derived by the gate): `the_chain_continues_past_the_second_hop`.

The chain stays open in exactly three places:

* `scripts/e489_write_wire.py:448` — `classify(root)`; both of its call sites hand `root` on as a
  parameter again, so this is a third hop, not a supply.
* `scripts/e328_quoted_number_staleness.py:358` — `build(root)`; 3 of 4 call sites pass a local
  named `root`, the fourth omits it (default).
* `scripts/e445_facehome_target.py:144` — `build(index)`; **both** call sites omit the parameter, so
  the value comes from the signature default, never from a caller.

**Reusable lessons.**

1. *"Forwarded again" is not "never arrived".* Folding a second parameter hop and an unbound name
   into one `forwarded` count reads 12 values as 12 dangling ends; three quarters of them are
   settled one hop later, and only 5 of 23 hand-overs keep moving.
2. *A default is a supplier too.* When every call site omits a parameter, the value comes from the
   signature, not from any caller — counting it as a written value would read "nobody passes this"
   as "somebody does".
3. *A local must be followed to its binding statement, not to the function boundary.* Stopping at
   the boundary yields "it is a local" and never "here is what it was bound from"; the binding
   statement (assignment / loop target / `with` target / walrus) can be classified with the same
   vocabulary as a call-site argument.

**Verification.** `scripts/e526_second_hop.py` — build rc0 / check problems=0 / verify problems=0 /
selftest 11/11 (4 fixture shapes: parameter-and-mixed, local-bound-from-a-call, loop target,
function with no call site; 3 doctored faces refused: hidden forwarding site, arrival relabelled
resolved, population that does not add up to E520's count). Face
`results/state_tilt/SECONDHOP-2026-11-08.json` + `secondhop_latest.json` (same bytes). S6 leg
`second_hop` rc0 0.06s. Smoke leg `# E526` with `scripts/run_e526_smoke_leg.py` 1/1 green,
`--doctor` 1/1 red, face restored byte-identically (sha `00567c31567d`). Card E526 in
`knowledge/METHODOLOGY_ASSETS.md`.

**Bound, published not claimed.** The scan never follows a third hop: a value that is again a
parameter or local is published as such and the chain ends in this face — that residue is E530. A
function reached through a container, a callback or an instance attribute is outside the scan and is
published as `no_supplying_site_in_this_tree`, never as a written value.