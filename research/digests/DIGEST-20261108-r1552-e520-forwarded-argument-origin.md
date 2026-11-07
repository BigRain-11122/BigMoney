# DIGEST 20261108 r1552 bm-b — E520: one hop past the caller's boundary

**Question.** E519 followed every call-site argument that was a local of the calling function back
to the statement that binds it and stopped at the caller's own edge: 7 of 61 bindings turned out to
be *a parameter of the caller itself* and 5 names were bound neither as a parameter nor by an
assignment inside the caller. Both are the same non-answer one level up, in opposite directions —
so this round follows each one hop further:

* a parameter of the owning function is supplied by **that function's call sites** — enumerate them
  and publish what each one hands over;
* a name the caller does not bind is bound by **another scope** — an enclosing function (closure
  cell), a comprehension/loop/`with`/`except` target, a destructuring assignment, a walrus, a
  function-local import, a module global, or nowhere at all.

**Population.** The `LOCALARGORIGIN-2026-11-08.json` rows whose origin is
`a_parameter_of_the_calling_function_itself` (7) or
`no_binding_in_the_calling_function_or_its_parameters` (5). 3,800 modules parsed, 23 unparseable.
Call sites are matched by the callee's bare name and then filtered by ownership: same module,
from-import of that name, or an attribute on a name imported from that module. 20 real call sites.

**Readings (2026-11-08).** Verdict
`most_forwarded_parameters_are_again_a_parameter_or_a_local_at_the_next_call_site_so_the_hop_did_not_reach_a_source`.

* **5 of 5 "unbound" names are destructuring targets**, not unbound names: `charge, rows, store,
  pin = _arms()` (`e372_store_the_absent_members.build`), `sources, errors = corpus()`
  (`e462_identity_dialect.build`), `for name, payload in faces` (`e298_replay_control_census.build`
  and twice in `cmd_selftest`). E519's assignment scan records only `ast.Name` targets, so a tuple
  target is invisible to it — **the "unbound" arm was an artifact of the scan, and the true unbound
  count in this tree is 0**.
* Of the 20 call sites of the 7 owning functions: **1** hands a written value (an attribute on an
  imported name, `e365.ROOT`), **12** hand again a local (8) or a parameter (4), **6** leave the
  parameter at its default and **1** row has no call site at all. **0** call sites omit a parameter
  that has no default.
* Binding by binding: **0 of 7** parameters are written at every call site, 3 are forwarded again at
  every call site, 3 are mixed and 1 is never supplied. 3 of the 7 parameters have no default.
* The named cases: `e279_substitution_soundness.censused(rows)` (2 sites, both forward),
  `e374_store_load_bearing_members.attribute(store)` (4 sites, all forward),
  `e489_write_wire.classify(root)` (2 sites, both forward), `e365_face_population_pin.build(root)`
  (7 sites: 2 forward, 3 defaults, 1 local `tmp`, 1 `e365.ROOT`), `e441_facehome_family.build(index)`
  (2 defaults + 1 forwarded parameter), `e402_fragment_producers.build(sources)` (only call site is
  the default), `e406_blob_vs_tree_readers.call_sites(git_names)` — **no call site anywhere in the
  tree**; its own docstring calls it "deprecated shim kept for the selftest's older fixtures".

**Method lessons.**
1. *A zero-hit needs a census of why it is zero.* All 5 "bound nowhere" rows were tuple
   unpackings. Publishing 4 dead bindings would have been a false defect report; the fix is a
   named arm (`an_element_of_a_tuple_or_list_destructuring_assignment`), not a looser threshold.
2. *"Nothing is passed" and "nothing can be passed" are different.* Six call sites that leave a
   parameter alone are harmless only if the signature has a default — the arm is split
   (`nothing_is_passed_so_the_signature_default_applies` vs
   `nothing_is_passed_and_the_parameter_has_no_default_so_the_call_would_raise`) and the count of
   the second arm is 0, which is a measurement, not an assumption.
3. *A bare-name callee match is not a call site.* Matching `build(...)` cheaply pulls in every
   other module's `build`; the ownership column (same module / from-import / attribute on an
   imported module / same-named only) is published per site so a reader can see the filter working
   instead of trusting it.
4. *A dead function is a legitimate finding.* `e406.call_sites` has a parameter and no caller —
   the only row with the `no_call_site_of_this_function_exists_in_this_tree` arm, and it is
   recorded as such rather than as "supplied by default".
5. *The upstream face is a dependency, so the row counts are asserted.* 7 + 5 = 12 is checked
   against E519's own summary; if E519 is rebuilt with different counts this face's `check` fails
   instead of silently measuring a different population.

**Evidence.** `scripts/e520_forwarded_argument.py` (`build` rc0, `check` problems=0, `verify`
problems=0 — a fresh build is byte-identical, `selftest` 0 problems over 7 fixture rows and eight
doctored faces), `results/state_tilt/FORWARDEDARG-2026-11-08.json` + `forwardedarg_latest.json`,
S6 leg `forwarded_argument` (rc0 0.06s), smoke leg `# E520` (`scripts/run_e520_smoke_leg.py`
1/1 green, `--doctor` 1/1 red, face restored to sha `eb97c93ec38b`), card E520 in
`knowledge/METHODOLOGY_ASSETS.md`.

**Not run.** The full smoke suite (~20–30 min), the remaining S6 chain legs (update_*, market_*,
paper), `monitor.build_status`, `daily_scorecard`, the collector family and the market/paper chain.
No GPU, no cloud, nothing deleted, no queue head claimed.