# DIGEST 2026-11-08 r1574 bm-b -- E545: re-pointing an old set of open arms at a newer resolver

**Card**: E545-WHICH-OF-E533-S-REMAINING-OPEN-ARMS-THE-E536-RESOLVER-CAN-SETTLE-ONCE-THE-INTERPRETER-IS-IN-HAND
**Face**: `results/state_tilt/RESOLVERRETRY-2026-11-08.json` (+ `resolverretry_latest.json`)
**Parent**: `results/state_tilt/CALLPUREARM-2026-11-08.json` (E533)
**Script**: `scripts/e545_resolver_retry.py` -- build / check (problems=[]) / verify (problems=[]) / selftest 12/12

## The question

E533 published four arms of E527's population and closed one. The other three carried the reason
"the callee is not a pure chain of literals", a sentence that is true of any expression the fold
never read. E536 then shipped a literal interpreter that runs a repo-source body with the site's
arguments bound to it -- and nobody pointed it at those three arms. So the published face could not
distinguish *not decidable* from *not measured*.

## What the three passes returned

| arm | verbatim (E536 unchanged) | extended (own-module fn map + one hop of free names) | outcome |
|---|---|---|---|
| `scripts/e285_interrange_gap_ceiling.py:505` `interval(off['rows'], 'tight')` | `name_not_bound_in_the_inlined_scope:off` | folds to `{'lo': 1.0, 'hi': 1.1, 'spread': 0.1, 'n_rows_with_interval': 2}` | closed by the extension |
| `scripts/regime5_validation.py:173` `stats_idxs` | `the_name_is_the_caller_s_own_parameter` | still the caller's parameter | open on a parameter |
| `scripts/regime5_validation.py:319` `win_stats` | `name_not_bound_in_the_inlined_scope:rb` | still open: binds at 312 to a comprehension over `rb` | open on a face read |

Three of three failed verbatim; the extension moved exactly one. That is the honest split: the
refusal was **not** about decidability for the e285 arm -- it was about the interpreter not having
the caller module's own functions in its `_fn_map` and not binding free names *inside a call's
arguments*. E536 bound a bare base name; `interval(off['rows'], 'tight')` needs the name `off`
inside an argument of a call whose callee is same-module.

## The parameter arm, one hop out

`perm_nulls(raw, win_pos, stats_idxs, ...)` has four call sites:

* `:329` (production) passes `win_stats`, a comprehension over `rb` -- `rb` itself is built from
  `labels`/`r_next`, which are read off the anchor face. **Not decidable statically.**
* `:598`, `:635`, `:637` (self-test) pass `stats_idx = list(range(59))` -> `[0, 1, ..., 58]`.
  **Measurable**, and measured.

So the parameter arm is not one answer: the production site is a read no static resolver follows,
and the three self-test sites are literals that were sitting there unread. Publishing only
"caller's parameter" would have hidden three of four sites.

## The store E544 already priced, now visible from this side too

For the e285 arm the extension publishes `intervening_item_stores = [{binding: off, store_line: 504,
target: off['rows'][1]['tight']}]`. The folded value is the **unmutated** container (lo=1.0); the
site at :505 sees lo=0.9. So the closed arm is closed *about the value the fold publishes*, not about
the value the assertion consumes -- which is E544's finding and is now stated beside the value rather
than inferred elsewhere.

## Two bugs the build published before the gate could

1. **A call target reported as a free name.** `interval` appeared in the binding table as "no binding
   of this name before the site", in the same row that folded to a value. Class and value
   contradicted each other; the gate re-derives counts, not consistency. Rule now: a name in
   `Call.func` that resolves through `_fn_map` is the interpreter's job, not a binding lookup.
2. **A builtin call in a binding read as a repo callee.** `stats_idx = list(range(59))` was refused
   as "the binding calls a name no single module defines: list", which would have published all four
   call sites as undecidable. One bug deciding three of four readings is exactly the kind of thing a
   "not decidable" verdict can hide.

## Gate and witness

`face_problems` re-derives every count from the rows, refuses a class outside its vocabulary, refuses
an open arm that carries a value or a closed arm that carries none, refuses a parameter arm with no
call sites, and requires the e285 witness to be **in the population and closed by the extension** --
a scan that never reached the witness cannot claim the pattern is priced. Smoke leg `# E545` adds
four doctored copies (flipped outcome, hand-written verdict, summary outliving its rows, emptied
call-site list), each of which must be refused; `--doctor` proves the leg can go red.

## Limits, published with the face

`one_hop_out` reads call sites in the same module only, so a parameter filled by another module's
caller stays "not measured". Item stores are not replayed here. The interpreter is a whitelist and
stops with a name rather than guessing.