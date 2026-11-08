# DIGEST 2026-11-08 r1564 bm-b -- E532: is the sentinel nothing replaces in its own body replaced one hop out?

Face: `results/state_tilt/ONEHOPOUT-2026-11-08.json` (+ `onehopout_latest.json`)
Runner: `scripts/e532_one_hop_out.py` (run / check / verify / selftest 15/15)
Upstream: `results/state_tilt/defaultparam_latest.json` (E531) + `thirdhop_latest.json` (E530),
both sha-pinned in the face.

## Question

E531 published, per omission site, what the signature default names and what the *own body* does
with it. Exactly one arm came back as `the_body_passes_the_sentinel_on_unchanged`, and E530 had
published the same shape one hop earlier. Both faces stop at that sentence, which is true and
unusable: "nothing replaces this sentinel" is a claim about one function, not about the value.
The card asks the next question -- is it replaced one hop out, by the callee it is handed to?

## Method

Population = every arm E531 publishes with `rescue_class == the_body_passes_the_sentinel_on_unchanged`,
plus every E530 chain whose terminals include
`nothing_is_passed_so_the_signature_default_applies`, keyed by `(module, function, parameter)`.

Per arm: find every `Call` inside the owning body (nested defs excluded) that hands the parameter
onward; map the argument onto the callee's own parameter (keyword, or position against the
callee's positional list); resolve the callee through the E520 ownership classifier (same module /
by-name import / attribute of an imported module -- a bare name no import binds, or a receiver
that is not a name, is published as `no_signature`, never merged onto a same-named function); then
read what THAT body does with it. Classes: replaced by module constant / call result / read / literal
/ computed, guarded by a constant or another value, `still_forwarded` (the callee hands it on
again), `never_read`, `no_signature`, `no_forwarding_site`.

`still_forwarded` is deliberately outside the "replaced" set: it is the answer "the chain is longer
than the card".

## Readings

| quantity | value |
|---|---|
| arms in population | 2 (1 from E531, 1 from E530) |
| forwarding sites examined | 3 |
| sources read | 2,760 |
| arms replaced one hop out | **2 / 2** |
| arms still forwarded | 0 |
| arms whose callee never reads it | 0 |
| arms whose callee is not in this tree | 0 |
| distinct callee signatures | 3 |

Per arm:

* `e328_quoted_number_staleness::verify(root)` -- its own body passes `root=None` straight into
  `build(root=root, ...)` at line 358; `build` opens with `root = root or ROOT`, so the sentinel is
  replaced one hop out by a module constant whose chain is
  `e328_quoted_number_staleness:ROOT -> e326.ROOT -> e312.ROOT`.
* `e489_write_wire::build(root)` -- hands `root` to two callees at lines 448 and 501:
  `classify(root)` forwards it **again** (so that site stays open past this hop), while
  `_write(root)` replaces it with the module's own `ROOT`. One arm, two different fates.

Verdict (re-derived by the gate from the summary):
`at_least_one_sentinel_that_nothing_replaces_in_its_own_body_is_replaced_one_hop_out`.

## What this changes

E531's sentence was true for both arms and misleading for both: the value never stays a `None`
sentinel -- it lands on the repository root one call deeper. The honest unit of the claim is the
*arm-plus-its-forwarding-sites*, not the function: one arm can be replaced at one site and still
open at another, and E531's single word per site could not carry that.

Second, the E530 chain that "ends at a signature default" is not an end: `build` omits nothing,
it forwards. The chain E530 called terminal is terminal only because nothing looked at the
callee.

## Reusable lessons

* **"Nothing replaces it" is a statement about a function, not about a value.** Any face that
  publishes a rescue class must either follow one hop or name the hop count it stopped at; a
  rescue class with no hop count reads as a claim about the value.
* **One arm, several fates.** An arm with N forwarding sites can be replaced at one and still
  forwarded at another. Publish per site and let the arm class be derived (this face's gate
  refuses an arm declared `no_forwarding` beside its own site list).
* **A callee that forwards again is not a replacement.** Folding `still_forwarded` into "replaced"
  would have reported a rescue that does not exist -- the arithmetically tempting move, because
  it makes the answer uniform (2/2 replaced) instead of honest (2 arms, 3 sites, 2 replaced at
  one site and still open at the other).
* **Mapping the argument is not optional.** The parameter the value lands in (`root` -> `root`
  here) is a coincidence of naming; the classifier reads the callee's positional list, so a site
  that passes into a differently-named parameter is not silently credited.

## Cost and disclosure

`check` 0.05s, `verify` re-derives the whole population from the live tree, static only -- nothing
executed, no source rewritten. `sources_read` is a snapshot of a tree other lanes write to: it is
published but not gated, while every class, every count and the verdict are re-derived.

Not run this window: the full smoke suite was started before this study existed and was still in
flight at close (0 FAIL lines read), so no suite total is claimed for the new leg; the rest of the
S6 chain, the collector family and the market/paper chain were not run.