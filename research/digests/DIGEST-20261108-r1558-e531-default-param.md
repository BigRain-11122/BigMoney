# DIGEST 2026-11-08 r1558 bm-b — E531: what the signature default actually names

**Question.** E530 published that some chains end at a *signature default* rather than at a caller
(`e489_write_wire.build(root)` is omitted at 8 sites). A default is a value the signature itself
writes, so the chain does reach something — but whether that something is a population was unread.

**Method.** Every omission site the two upstream faces publish (`argument_kind` = the signature
default) — 9 from E530's chains and E526's hop sites, deduplicated by (caller module, line, callee,
parameter) — is resolved to its callee signature through E520's ownership classifier: same module,
imported by name, or attribute on an imported module resolve; a bare name no import binds, or a
receiver that is not a name, is published as a *name collision* and never merged back. Each resolved
signature is then read twice: what its default expression names (a `None`/empty sentinel, a literal,
a module constant with the module-level chain it folds through, a name from another module, a call
result, a read/scan of the tree, a computed expression), and what the *defining body* does with a
sentinel (rebind from a module constant / rebind from a call / guard every use with a fallback /
pass it on unchanged / never read it). Finally the omitting caller is asked whether it held a value
of that name in scope.

**Readings (9 omission sites, 5 resolved, 5 sentinel defaults).**

- 5 sites resolve to a signature on disk; the other 4 are `PaperSession().run(...)` /
  `LiveSession().run(...)` attribute calls on a `run` that is not the function in question — published
  as collisions (`the_receiver_of_the_attribute_call_is_not_a_name`), 0 merged into the population.
- **All 5 resolved defaults are the sentinel `None`; 0 defaults are themselves a value.**
- 4 sentinels are replaced inside the defining body: 2 from the module constant `ROOT`
  (`e489_write_wire.verify` / `.run`, where `ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
  folds to a call result — the repository root) and 2 from the call `e435.face_index(root)`
  (`e445_facehome_target.build(index)`).
- 1 sentinel is passed on unchanged: `e328_quoted_number_staleness.verify(root=None)` forwards `root`
  to `build()`, whose own body begins `root = root or ROOT` — the replacement is one hop out, and the
  method limit publishes it as the sentinel it is in *this* body rather than guessing.
- 0 omitting callers held a value of that name in scope: none has a `root` parameter, local or
  module name (the module constant is `ROOT`, a different name).
- Verdict (re-derived by the gate): `some_default_is_a_sentinel_that_nothing_in_the_body_replaces`.

**Reusable lessons.**

1. "The default supplies it" has to be read in three steps — what the signature writes, what the body
   does with it, and what the omitting caller held. All three empty is the only case where "the
   population is whatever the signature happens to hold" is the honest sentence; here all three are
   occupied and the chain lands on the repository root.
2. A function name is not a signature: `run` matched four sites under `PaperSession`/`LiveSession`
   attribute receivers, and merging them would have invented four "defaults" that no signature
   supplies.
3. Unresolved rows need their own label and no default class. A first draft marked them "the default
   is already a value", which counted 4 collisions as 4 real values — the label a row carries is read
   as a measurement, so the vocabulary has to be disjoint.

**Verification.** `scripts/e531_default_param.py` run rc0 / check problems=0 / verify problems=0 /
selftest 19/19 (four rescue arms + five doctored copies refused: hand-written verdict, sentinel
reported as already supplied, unresolved row carrying a default class, value default carrying a
rescue, rescue without its source). Face `results/state_tilt/DEFAULTPARAM-2026-11-08.json` +
`defaultparam_latest.json`. S6 leg `default_param` rc0 0.06s; smoke leg `# E531` 1/1 extracted from
`smoke_test.py` by its own anchors (`scripts/run_e531_smoke_leg.py`). Not run this window: the full smoke
suite (~20–30 min) and the rest of the S6 chain.

**Next card seeded.** E532: the 1 sentinel published as passed on unchanged is forwarded to a callee
that *does* rebind it — follow every such hand-over one hop and publish what it lands on, so
"nothing in the body replaces it" stops standing in for "the population really is the sentinel".