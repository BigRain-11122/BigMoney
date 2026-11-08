# DIGEST 2026-11-08 r1559 bm-b — E527: does following the argument one hop settle an undecidable arm?

**Question.** E521 published 52 production call sites whose verdict is exactly "the read would raise
and the arm's reachability is not decidable from the call site". The card behind this round asks which
of those 52 becomes decidable when the guard's parameter is followed one hop into the caller. The
premise of that question — that the deciding value sits one scope out — is what this round measures.

**Method.** Population = E521's published rows whose verdict is exactly that sentence (52, re-derived
from the face at build time, never copied from the card). For each site the callee's empty-arm census
is recomputed by importing E521's own arm machinery rather than re-implementing it, and per site the
recomputed reach list is asserted equal to the reach list E521 published (52/52 reproduce, 0 mismatch).
Each arm then gets the parameter its guard names, using the same first-parameter-naming-`if` walk the
reach class came from — so a published parameter is by construction the parameter the class named.
Arms split in two:

* *followable* — the guard names a parameter of the callee and the site passes no literal;
* *structural* — the guard sits behind a test that names no parameter of the callee at all.

Followable arms then get their argument resolved exactly one hop: the argument expression is read from
the call site, and if it is a bare name, the nearest binding *before* the call inside the calling
function is classified. Only three shapes are decisive: a literal the caller binds, a module-level
constant that folds to a literal, and nothing else. Deliberately non-decisive: a binding inside an
`if`/`for`/`while`/`try` the call does not sit in, a name bound more than once before the call, and
every non-name argument. A name the calling function never binds is looked up once in the module scope
(a module-level literal settles the arm; any other module binding is published as module-scope-only,
not as an unbound name).

**Readings (52 sites / 53 undecidable arms / 2,753 sources).**

- **43 of the 53 arms (81%) cannot be settled by any argument**: their guard sits behind a test that
  names no parameter of the callee, so the arm reads state the callee owns. 42 of the 52 sites are in
  this class. "Not decidable from the call site" is, for this majority, a scope problem rather than a
  missing hop.
- 10 arms are followable and **6 of them are settled by a literal one hop out** (all six exclude the
  arm, none guarantee it): 5 are module-level fixtures (`GE20_BLOCK_FIXTURE` and friends in
  `national_team_face.py`, non-empty strings feeding `parse_ge20`) and 1 is a caller-local literal
  (`divlowvol_live_picks.py:352` binds `firing` to a non-empty list of tuples before
  `current_block(firing, idx)`, so its `if not x: return None` arm is unreachable).
- The other 4 followable arms stay open: 1 argument is the caller's own parameter
  (`regime5_validation.py:173`, `stats_idxs`), 1 is bound to a non-literal expression
  (`win_stats`), and 2 are not bare names at all (`interval(off['rows'], 'tight')`,
  `list(range(6))` — a call, not a value).
- Site-level: 5 fully decidable / 1 partly / 42 structural / 4 still open after the hop.
- Verdict (re-derived by the gate from the summary):
  `following_the_argument_settles_at_least_one_arm_but_not_all_of_them`.

**Reusable lessons.**

1. "Undecidable from the call site" is usually not "one hop short": 92% of these sites (42/52) have an
   arm that never reads the call. Answering such a population with a follow-the-argument study reads a
   scope problem as a missing layer — the honest answer needs the structural class as its own bucket,
   not folded into "still open".
2. The module scope is one of the caller's scopes. A first draft labelled the five `GE20_*_FIXTURE`
   arguments "no scope of the caller binds" when they are module-level literals — i.e. decisive. A
   key named `no_scope_binds_the_name` that actually means "my scanner does not read the module body"
   is the name-as-measurement failure again (E207 / E462 lineage); the fix is a module-scope leg, not
   a looser threshold.
3. A static nearest binding is not the runtime value: a binding inside a branch the call does not sit
   in, a name bound more than once, and any binding after the call are all published as non-decisive
   rather than resolved to the first one seen.
4. "The test names no parameter" has to be its own class. Merged into "undecided", a reader concludes
   those 43 arms are merely unexamined, when in fact there is nothing there to examine.

**Verification.** `scripts/e527_undecidable_arm.py` build rc0 / check problems=0 / verify re-derives
problems=0 / selftest green (11 fixture arms covering literal / module constant / module-only / call
result / caller parameter / loop target / branch binding / rebound name / non-name argument /
structural arm, plus 6 doctored faces refused: hand-written verdict, structural arm published as open,
settled arm with no literal text, site outcome its own arms do not derive, settled arm bound by a call
result, summary counts that do not re-derive). Face `results/state_tilt/UNDECIDABLEARM-2026-11-08.json`
+ `undecidablearm_latest.json`. S6 leg `undecidable_arm` rc0 0.05s; smoke leg `# E527` 1/1 extracted
from `smoke_test.py` by its own anchors (`scripts/run_e527_smoke_leg.py`). Not run this window: the full
smoke suite (~20–30 min) and the rest of the S6 chain.

**Next card seeded.** E533: the four followable arms that stay open all point at the same gap — the
argument is a *call*, not a value (`interval(...)`, `list(range(6))`, `win_stats` bound from a call).
Ask which of those callees is itself a pure function of literals at the site, so the hop can be closed
by folding one call rather than by following a name.