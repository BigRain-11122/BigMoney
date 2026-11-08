# E555 (r1581 bm-b): are the 67 unfolded second arguments constants a wider evaluator can name?

## Question

E554 published the repository's whole `print("wrote", <path>)` population and left 67 rows
unresolved with one reason: *the second argument is a name this scan cannot fold*. That reason is a
statement about the fold, not about the code. If the name is a module constant, a conditional-block
binding, or an import, a static evaluator could have named the face.

## Method

The population is machine-read from E554's face (`unresolved_because ==
the_second_argument_is_a_name_this_scan_cannot_fold`), re-parsed at each row's own `writer:line`.
The render call is recovered including the one-argument `%`-format shape whose faces sit in the
format tuple. Every free name in the argument is priced against a fixed binding order (parameter,
import, module assignment by whether its *value* folds, loop/with target, container store, enclosing
function local, never bound). Two capabilities are then added and each folded row publishes which
one closed it: `Path(__file__).resolve().parents[k]` evaluated against the writer's own relative
path, and an order-blind module-constant search (imports included). The control arm runs E554's own
resolver over the same rows and must fold none of them.

## Reading

- 67 rows: **6 fold**, all six through `parents[k]`, and **all six faces exist on disk**
  (capital_placement json+md, etf_book_buffer_adoption md, etf_book_premium_phases json+md,
  etf_book_voltarget_phase json+md).
- **61 are run-time by construction**: 38 enclosing-function locals, 10 module constants whose value
  is a clock or `sys.argv`, 6 caller parameters, 4 tuple targets of a helper call, 3 loop targets.
- control arm: **0** folds. Verdict:
  `some_of_the_unfolded_names_are_constants_a_wider_evaluator_can_name`.

## Three things this cost

1. The first draft called 49 rows "a name this module never binds" — most were `for path in ...:`
   targets. The fold read `ast.Assign` inside the enclosing function and not loop/with targets. After
   widening the binding census, `never_binds` went to 0 (38 locals + 3 loop + 4 unpacking).
2. The first draft labelled the six folded rows "a module constant defined below the message" — but
   E554's `_module_constants` is already order-blind (a fixture proves it folds the same shape). What
   actually closed them is the `parents[1]` subscript, so the class name was changed and the
   capability published separately as `closed_by`, with a leg pinning the "already order-blind" fact.
3. The first draft dropped 24 rows as "the render call is no longer at that line" — they are
   one-argument `%`-format messages whose faces sit in the format tuple. After handling that arm the
   class is empty.

## Bound

Module-level bindings and flat imports to depth 4. No attribute chains (`E.PATHS.results_dir`,
`config.PATHS` stay unfoldable; an import whose module is not in the tree is published separately),
no function returns, no environment lookups. "Foldable" means the whole expression folds from
literals only.

## Evidence

`scripts/e555_unfolded_second_arg.py` (build / check problems=[] / verify identical / selftest 19/19),
`results/state_tilt/UNFOLDEDNAME-2026-11-08.json` + `unfoldedname_latest.json`, smoke leg `# E555`
(`scripts/run_e555_smoke_leg.py` 1/1 green, `--doctor` 1/1 red), S6 leg `unfolded_second_arg`.
