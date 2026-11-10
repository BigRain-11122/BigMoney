# DIGEST-20261110-r1667-e643-non-function-site

- study: **E643** — what syntactic context holds the two-depth sites that belong to no function?
- round: **r1667 bm-b** (2026-11-10) · machine `bm-b` · lane `cpu-only`
- face: `results/state_tilt/NONFUNCSITE.json` + `nonfuncsite_latest.json`
- tool: `scripts/e643_nonfunc_site.py` (selftest 20/20, `check`/`verify` `problems=[]`)
- legs: `smoke_test.py` leg E643 (`scripts/run_e643_smoke_leg.py` 1/1 PASS, `--doctor` 1/1 red with the face restored byte-identically, sha `a7ecf39cf92f` in = out) + `Tools/s6_chain_bmb.py` leg `non_function_site` (rc=0 0.09s)

## Why the question exists

E640 published two numbers side by side: 27,675 of the 45,395 two-depth sites have an enclosing
function, 17,720 do not — and it labelled the remainder **module level**. That label is a name, not
a measurement. A site outside every function can sit in a module body, a class body, a class header,
a lambda, a comprehension, or a decorator expression, and those have different scopes at runtime.
E642 then priced "2,641 module-level writes" on top of that label, so whether the label covers one
population or several decides how much E642's headline is worth.

## What was measured

Every `.py` in the corpus E391 walks (13,099 files; 304 unparseable, 4 over the 1 MB cap) was
re-parsed, E638's two-depth site grouping and E640's innermost-owner split were **imported**, and
each site whose owner is absent was classified by the innermost container that holds its
(line, column) — with the full chain published, so `class_body>lambda` is not `class_body`.

| context | sites | write sites | literal keys | computed keys |
|---|---|---|---|---|
| module_body | 17,337 | 2,641 | 16,151 | 1,186 |
| comprehension | 342 | 0 | 290 | 52 |
| lambda | 41 | 0 | 14 | 27 |
| class_body / class_header / decorator / function_body | **0 (measured)** | 0 | — | — |

- residual total **17,720**, which is E640's published residual to the site — `delta_vs_source_face = 0`
  (the corpus grew by 61 sites since r1660 and every one of them landed inside a function).
- all **2,641** residual write sites sit in module body, which is exactly E642's "2,641 module-level
  write sites" — E642's name turns out to be a measurement, not just a label.
- 3,237 module-body sites sit inside a module-level compound statement (`if`/`for`/`while`/`with`/
  `try`), i.e. the module body is itself a block tree rather than a flat list.
- the four zero contexts are published as **measured zeros** (`contexts_measured_with_no_sites`),
  and an independent probe over the same corpus (`_probe_e643_class.py`, line-range containment, no
  use of this study's classifier) agrees: 0 residual sites inside any `ClassDef` span, 0 inside any
  decorator.

## Verdict

`the_sites_without_an_enclosing_function_split_across_several_syntactic_contexts_while_every_site_
that_writes_sits_in_one_of_them,_so_the_read_side_of_the_residual_is_many_contexts_and_its_write_
side_is_one`

## Lessons

1. **A residual's label is a claim about its population.** E640's "module level" was coined to
   describe 17,720 sites it never looked inside. Measuring the split shows it is 97.8% module body
   and 2.2% comprehension/lambda — so the label survived, but only as a result rather than as an
   assumption, and the two write-side conclusions built on it (E642, E646) are now priced against a
   measured population.
2. **A decorator is outside its own `def`'s span.** `FunctionDef.lineno` starts at `def`, so an
   owner-split built on spans classifies decorated module-level sites as module body. The decorator
   pass has to be separate, and the two zero decorator sites are the answer *after* that pass —
   without it the bucket would have been silently folded into module body.
3. **Zeros must be published as measured, not omitted.** A histogram that only lists non-empty
   buckets is unreadable: the reader cannot tell "no class-body site" from "class body not tested".
   `contexts_measured_with_no_sites` plus an independent probe is the difference.