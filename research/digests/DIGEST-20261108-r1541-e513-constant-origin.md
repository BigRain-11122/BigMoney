# DIGEST 2026-11-08 r1541 bm-b — E513: a module constant that supplies a population is often not a module constant at all

**Card** E513 · **Face** `results/state_tilt/CONSTANTORIGIN-2026-11-08.json` (+ `constantorigin_latest.json`)
**Script** `scripts/e513_constant_origin.py` (run / check / verify / selftest) · **Upstream** `results/state_tilt/CALLERSUPPLIED-2026-11-07.json` (E508)

## Question

E508 (r1538) classified every call site of E505's 35 argument-only surfaces and put 123 arguments in a
"module constant" bucket (`module_constant_literal` 53, `module_constant_built` 57,
`imported_constant` 13). It answered "can an adapter read this population at the call site" with
`how_many_sites_pass_a_module_constant = 79`. A module constant is not a published population:
`CORPUS_DIRS = tuple(e346.CORPUS_DIRS)` is a literal in one module and an alias in the other, and
`corpus` inside `def build()` is neither.

So: follow each of those names one hop and publish what it ultimately holds, plus whether an
adapter that imports **only** the surface module can reach it.

## Reading

84 distinct bindings over 123 sites:

| scope of the name | bindings | what it means |
|---|---|---|
| module scope of the calling module | 19 literal + 23 needing a second module + 14 unresolved | the label fits |
| a local of the enclosing function | **58 bindings / 80 sites** | the label does not fit at all |
| no binding anywhere | 14 | needs a reader, not a label |

* **19** populations are written out as names in their own module (frozen, readable by importing it).
* **23** need a second module (attribute on an import, or a call into another in-repo module) — the
  constant crosses an import edge, so `recoverable from the call site` hides `import the other module too`.
* **0** are a tree walk or a file read at import time (E505's own headline said 0 walks / 0 cwd).
* **10 of 84** bindings are readable by an adapter that imports only the surface module;
  **101 of 123 sites** lose reachability.

The headline is the local-variable arm, not the literal arm: 65 % of the sites E508 counted as
"a caller passes a module constant" pass a value that exists only inside the calling function
(`corpus` in `e347` is `corpus = e341.pinned_corpus(PIN_SHA)`, a call result; `groups` in `e278`
is a `build()` local; `NAMES` in a selftest is a literal but a *fixture* literal).

## Two self-inflicted bugs this window

1. **`row["module"]` is not where the call site lives.** E508's `module` field names the module the
   *surface* belongs to, while `source` is the file the call sits in — for `e347_published_number_gate_census`
   the module field was `e341_sibling_closer_what_changed`. First build resolved all 123 sites in the
   wrong module and reported 56/65 as "no module-scope binding". Fix: resolve in the module derived
   from `source`, and fall back to the surface module as a **separate, published** scope value
   (`scope_of_the_module_E508_named_the_surface_after`) instead of silently mixing them.
2. **A count on a name that promises something else.** The first grouping key was
   `(site_module, surface_module, name, source)`, so the same binding reached by two surfaces was
   published twice as "distinct constants" (73 vs a true 84/…). Renamed to
   `distinct_bindings_followed` and re-keyed on `(module, name, scope, enclosing function)` —
   two functions of one module binding the same name legitimately stay two rows.

## Reusable lessons

* When a label says "constant", check the **scope** before following the value: a `Name` node at a
  call site is a module attribute, a local, or a parameter, and only one of the three is published.
* Publishing "which module E508 named" alongside "which module actually binds the name" turns a
  silent wrong-population measurement into two named scopes; the difference is the finding.
* A reachability answer needs both the import edge and the binding kind: a tree walk is importable
  but not frozen, and a function local is neither.

## Bounds

Module scope + enclosing-function scope only (a class-body binding is not modelled); aliases stay
inside a module and stop on cycles; crossing into another repo module happens once and then stops
(that hop is E514); the upstream face's own kind labels are taken as given.