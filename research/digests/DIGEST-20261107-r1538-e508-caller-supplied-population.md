# DIGEST-20261107-r1538-e508-caller-supplied-population

**Round:** r1538 bm-b (dept=research+engineering) · **Study:** E508 · **Face:** `results/state_tilt/callersupplied_latest.json`

## Question carried in

E505 (r1534) classed 35 of 180 studies as `the_only_surface_that_names_a_population_requires_caller_arguments`
and left them unpriced, because no adapter can call a function that needs arguments. That is a
fact about the signature. The signature never said where the value comes from: a surface every
caller feeds with a module constant is priceable by reading that constant; a surface that only
receives its caller's own parameter is not priced one hop later either; a surface nobody calls has
no population until something runs it. E505 put all three in one cell.

## What was measured

Static, read-only. For each of the 35 surfaces, every call site in the tree is located by import
form only (same-module direct name, `from <module> import <name>`, `import <module> as X` then
`X.name(...)`; `getattr`, star imports and dynamic dispatch are out of reach and counted as
neither present nor absent). Each call site's arguments are aligned to the callee's parameters and
each supplied expression gets a value-form kind: literal names, literal string, composite literal,
module constant (literal vs built), imported constant, tree walk, file read, derived from other
values, another call, caller's parameter, process cwd, path composition, `__file__` root, not
supplied, unclassified. Each surface then gets two arms — **all sites** and **sites outside
selftests** — with the headline taken from the second, and a reach axis (external / own module /
selftest only / never called).

## Readings

35 surfaces, 119 call sites, 3,763 source files parsed, 23 unparseable.

| axis | reading |
| --- | --- |
| sites by import form | 103 same-module, 16 module attribute, 0 direct `from` name |
| population argument, all sites | constant 79 (literal 34 / built 42 / imported 3), literal 23, parameter 14, derived 1, file read 1, another call 1, tree walk 0, cwd 0 |
| **surfaces whose reading flips when selftest sites are dropped** | **10** |
| headline resolution | constant 23, literal 2, parameter 7, derived 1, file read 1, another call 1 |
| recoverable | **26** (33 if selftest fixtures are counted) |
| never called | **0** |
| called from another module | 5 (30 only from their own module; 22 recoverable ones never leave it) |
| multi-parameter surfaces | 14, of which **6** have the most concrete argument on a parameter other than the first |

## Why it matters

"Signature is not readable" is not the same as "the population is undetermined". Twenty-six of the
thirty-five arms were already fed a value at a call site, twenty-three of them a module constant
the adapter can read; the unpriced bucket was partly an artefact of never having looked at the call
sites. The other half of the finding is the correction: 10 surfaces change their reading once the
`_selftest()` fixtures are dropped (literal rises 2 -> 6, recoverable 26 -> 33 counting fixtures),
so a face that counts them publishes test data as data. And arity is not a population pointer:
E505 recorded only how many arguments the surface needs, so on 6 of 14 multi-parameter surfaces the
most concrete value sits on a parameter other than the first, which the headline assumption and the
per-parameter table both have to say out loud.

## Bounds

Population is E505's published rows, never re-derived. A walk is attributed one hop (a callee's own
body checked for `os.walk`/`glob`/`listdir`); two hops read as a plain call. Only the tree is read,
so a call from git history, a notebook or a scheduled task's command line is out of reach and the
reach axis says so rather than folding it into "never called". Constants are not type-checked: a
module constant reaching the population parameter may hold something other than names, and every
constant ships the expression that supplied it. A `literal_string` may be a key rather than a
corpus (`scan_key(payload, "session_open")`), which the per-parameter table exposes.

## Delivery and wiring

`scripts/e508_caller_supplied_population.py` (run rc0 / check problems=[] / verify rebuild
identical / selftest 18/18) · `results/state_tilt/CALLERSUPPLIED-2026-11-07.json` +
`callersupplied_latest.json` (byte-identical twins) · S6 leg `caller_supplied` rc0 0.06s
(`results/_r1538bmb_s6_chain.json`) · smoke leg `# E508` executed verbatim standalone 1/1 green
(`_r1538_leg508.py`) · methodology card E508. Not run and not claimed: the full smoke suite, the
rest of the S6 chain, the collectors, any GPU or cloud work.