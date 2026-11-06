# DIGEST 2026-11-06 r1478 bm-b — E456: the cross-module half of E450 is entirely builtins and local factories

**Face.** `results/state_tilt/importclass_latest.json` (+ `IMPORTCLASS-2026-11-04.json`)
**Study.** E456_which_call_bound_receiver_names_a_class_imported_from_another_module
**Card.** E456 (seeded by r1475 after E450 closed the local half)
**Verdict.** `no_row_callee_resolves_to_a_class_defined_in_this_repository`

## What was asked

E450 graded the caller side of E444's 24,831 attribute call rows and left 6,875 whose receiver is a
name assigned a call to something that is **not** a class the caller defines. Those are the rows
where the receiver's class, if it has one, came from elsewhere — exactly the attribution the name
index would have got wrong. E456 resolves each such callee through the caller's own imports to a
module in this repository, indexes that module's classes and methods, and asks whether the row names
a method the imported class carries.

## Reading

| arm | rows |
|---|---|
| cross-module receivers in scope (E450 arm 6,875 + 23 growth) | 6,898 |
| callee resolves to a class in an in-repo module | **0** |
| rows naming a method that class carries | **0** |
| residue (callee not resolvable to an in-repo class) | 6,898 |

Residue, by kind:

| kind | rows |
|---|---|
| the callee is a builtin name (`open`, `dict`, `list`, `datetime`…) | 3,495 |
| the callee is defined in the caller itself (a local factory) | 2,238 |
| the imported module has no file in this repository (stdlib / third-party) | 928 |
| the callee name is not imported, bound or local to the caller | 113 |
| the imported name exists in that module but is a function, not a class | 59 |
| the call target is not a plain name or a module-qualified name | 54 |
| the call reads an attribute of an imported name, not a module | 10 |
| the module defines no name of that kind | 1 |

1,000 rows did go through an import (853 module-level, 137 module-level aliased, 6 function-level,
2 function-level aliased) and not one of them named a class.

## The zero carries its own census

A headline zero is only a reading if the instrument is shown to fire (E444's rule). The face
publishes a resolver control over the whole corpus: of **69,562** assignments whose value is a call
to a plain or module-qualified name, **36** do resolve to a class this repository defines
(`engine/exit_rules.py: ExitConfig/ExitState`, `knowledge/rules.py: FeeSchedule`, both harvested by
`engine/backtester.py` and `monitor/build_status.py`). So the resolver is not blind — those 36
programs simply never attribute-call those receivers inside E450's wrapper population.

Reading the other way: half the cross-module arm (3,495, 50.7%) is `open()`. The next largest block
(2,238) is a local factory. The remaining 1,000 imports name functions, stdlib modules, or objects —
never a class. "A receiver bound to a call" in this corpus is overwhelmingly not an object at all;
it is a file handle.

## Pits (measured, not assumed)

1. **A single residue bucket destroys the finding.** The first build folded builtins, local
   factories and untraceable imports into "the callee name is not imported by the caller" (5,846
   rows) — one story. Splitting by mechanism turned the headline from "nothing resolves" into "half
   of it is `open()`", which is the load-bearing statement.
2. **A dotted-only import resolver finds nothing in this corpus.** Scripts import their siblings by
   bare name (`import e444_attr_method as e444`); a resolver that only joins `a.b.c` to `a/b/c.py`
   resolves zero in a tree that does exactly that everywhere. Both spellings are tried, and a module
   string that matches two corpus files is published as ambiguous instead of resolved by preference.
3. **A method name is not a module-level name.** Reading the whole AST for "functions the module
   defines" graded `from mod import helper` as "imported a function" even when `helper` was only a
   method of a class in `mod`. Restricted to top level; the one remaining
   "module-defines-no-name" row is real.
4. **The import form belongs to the import that was involved, not to the one that succeeded.** The
   first tally refused the face because residue rows from import-side failures carried a form. The
   rule is now "present exactly when an import was involved", which keeps the 928 outside-tree rows
   attributable to the import form that produced them.
5. **The population is E450's, not a second derivation.** `e450.graded_rows()` was extracted from
   `build()` and E456 filters it; a second derivation would have been a second measurement of who is
   in scope. E450's own `check`/`selftest` were re-run after the refactor and still pass
   (`check problems=0`, `selftest 46/46`).

## Wiring

* `scripts/e456_import_class.py` — `run` / `check` (0 problems) / `verify` / `selftest` (42/42)
* `smoke_test.py` leg `# E456 (r1478 bm-b)` — 1/1 green; doctored (a residue row promoted to a name
  hit) 1/1 red, face restored byte-identical (sha `a4998527…`)
* `Tools/s6_chain_bmb.py` leg `import_class` → `check` (the chain leg must not re-walk the corpus;
  full `verify` is the closeout gate)
* `knowledge/METHODOLOGY_ASSETS.md` card E456
* `results/runnable_pool.json`: E456 done with `result_ref`, one card seeded back to the floor

## Not run / not claimed

GPU untouched (parked, C-20261014-01); no cloud call; nothing deleted; the full 352-leg smoke suite
was **not** re-run this window (it was launched by r1477 at 08:31 and came back 344/352 with 8 FAIL,
all of them the pre-existing corpus-growth "summary does not re-derive" class — see the round row);
no S6 lane collector was re-run.