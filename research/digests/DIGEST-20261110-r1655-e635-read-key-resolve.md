# E635 — the computed-key reads are decided inside their own function, and none of them is the counted key

**Round** r1655 · bm-b · 2026-11-10 · card E635 (`cpu-only`) ·
face `results/state_tilt/READKEYRESOLVE.json` · script `scripts/e635_read_key_resolve.py` (selftest 18/18)

## What E634 left open

E634 walked the whole body of the function that holds each counted read line and found **0** unnamed
entry reads of the key — but it also published a residue: **30 computed-key reads** at the receiver's
own level (8 before / 1 at / 21 after the dead line). Those read *some* key. A computed key is the one
shape E633's classifier cannot name, so the zero above is only as strong as the claim that none of
those 30 expressions can be the counted key.

## What this round measured

For every computed-key read E634 could not name, propagate constants **inside its own function**:
a literal at the read, a module-level string constant (chase depth ≤ 6), an assignment in the scope,
a `for` target, a comprehension target, or a parameter of the scope. Chains stop at the function
boundary — a key handed in by a caller is not guessed.

| reading | count |
|---|---|
| distinct computed-key read sites | 12 |
| occurrences across E634's counted lines | 30 |
| occurrences after the dead line | 21 |
| **proven to be the counted key** | **0** (0 before / 0 at / 0 after) |
| could be the counted key | 1 (a rebound loop variable, unioned not proven) |
| proven to be another key | 5 (module-level string constants) |
| unresolved | 6 (all bound by a `for` target over a parameter's iteration set) |
| binding sits only after the read it would explain | 0 |
| read names a parameter or nothing at all | 0 |

Verdict:
`no_after_side_computed_read_resolves_to_the_counted_key`

## Why the zero is a measurement

The same rule as E444/E207: publish what the instrument looked at. Here every one of the 12 sites is
named with module, function, line, column and side of the dead line, and each carries the binding kind
that decided it — `for_target` 7, `module_level_string_constant` 5. The five that resolve are
*published as another key*, which is the part that makes the six zeros credible: the walker can and
does name keys, it just never names the counted one.

The 21 after-side occurrences land on only 6 sites, all in `scripts/ew6_portfolio.py::write_outputs`
(one before-side site is `could_be`, five after-side are `unresolved`). The single `could_be` is a loop
variable rebound in the scope — proven would require running, which this study does not do.

## What stands and what does not

- E634's "no unnamed entry read after the dead line" **stands**: none of the 30 computed-key
  occurrences can be shown to be the counted key.
- E633's line-scoped census and E632's node count **both hold**.
- Not claimed: that the 6 unresolved sites are *not* the key. They are unresolved — a caller-supplied
  iteration set is outside intra-procedural reach, and "unresolved" is never counted as the key.
- Handoff to E636: the 6 unresolved sites all take a `for` target over a **parameter's** iteration
  set; following one hop into the callers is the only remaining way to close them.

## Limits published on the face

1. Constant propagation is intra-procedural (caller-supplied keys stay unresolved).
2. A name bound more than once is unioned → `could_be`, never `proven`.
3. Module-level constant chains stop at depth 6.
4. No runner, no fixture write: this study reads source and E634's published rows only.