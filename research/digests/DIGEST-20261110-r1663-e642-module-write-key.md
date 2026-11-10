# E642 — the module-level residual E640 dropped is empty for these reads

**Round** r1663 bm-b · 2026-11-10 · lane cpu-only · department 研究
**Face** `results/state_tilt/MODULEWRITEKEY.json` + `modulewritekey_latest.json`
**Script** `scripts/e642_module_write_key.py` (selftest 17/17, check/verify `problems=[]`, rebuild byte-identical)
**Source** E640 (r1660 bm-b) `results/state_tilt/WRITEREADCOLLIDE.json`

## The question

E640 answered "can a write sit in the same function as a counted read" for the 2,873 write sites
that have an enclosing function, and published the rest as a number: **2,641 of the 5,514** two-depth
write sites sit at module level, where no function exists. A module-level dict literal
(`LEVELS = {...}`) writes every key the module later reads, so that residual is where a counted read
could still be standing next to a write of its own key — and E640 could not even ask.

## What was measured

Take the modules that hold E633's 13 counted read lines (via E638's join, so the read population is
the published one), re-parse each, keep only the two-depth sites whose innermost enclosing function
is `None` under E640's own owner rule, and publish each site's member keys beside the keys that
module's counted read lines read.

| | |
|---|---|
| corpus module-level two-depth sites | 17,720 |
| corpus module-level two-depth **writes** | **2,641** — re-derives E640's published residual exactly |
| modules holding a counted read line | 6 (all measured) |
| counted read lines / distinct row keys | 13 / 6 (`bar`, `days`, `rows`, `slip_exec`, `verdict`, `x1`) |
| module-level two-depth sites in those 6 modules | **0** |
| module-level writes in those 6 modules | **0** |
| write sites naming a row key | **0** |

So E640's exclusion is empty **for these reads**: none of the 6 modules that hold the 13 counted
read lines has any module-level two-depth site at all — not a write, not even a read. The zero names
what it counted (E444 family): the corpus does carry the form (2,641 writes), it is these modules
that do not.

## The weaker arm, published apart

A key name is not scoped to its module, so the face also asks the corpus-wide question: any
module-level write, in any module, whose member key equals any counted row key. **7 hits** in 2,641
write sites — and they are exactly what E207/E208 warn about:

- `verdict` ×4 in `results/_r478bmc_trio_watch.py`, `_r479bmc_trio_watch.py`, `_r675bmb_trio_watch.py`, `_r920bmb_n2u3_flip.py`
- `rows` ×3 in `_r872bma_ledger_heal.py`, `scripts/run_e563_smoke_leg.py`

Unrelated round scripts and a smoke-leg runner writing generic words. Zero of them sits in a module
that holds a counted read, which is why the per-module hit count and the cross-module
"in the modules that hold the reads" count are both 0 and are published separately from the 7.

## Lessons

1. **A residual published as a number is a question, not an answer.** E640 said "2,641 sites have no
   owner function" and that sentence can only be read two ways — "so the walk is finished" or "so a
   whole population is untested". It is the second, and the test is one module-scope filter away; a
   reconciliation figure (2,641 re-derived under an independently written filter) is what makes the
   test credible.
2. **A zero must be priced against the population that does carry the form.** "0 module-level writes"
   alone reads as "this form does not happen"; beside "17,720 sites / 2,641 writes elsewhere" it reads
   as "it happens, just not here", and the two are different findings.
3. **Key-name overlap is the weakest possible collision test, so publish it in its own block.** The
   7 cross-module hits are generic words in unrelated scripts; mixing them into the per-module count
   would have turned "no collision" into "7 collisions".

## Where next

`E646` (seeded, cpu-only): whether any of the 7 cross-module name hits shares a container or binding
lineage with the counted read it appears to collide with — i.e. price the name≠semantics caveat on
this arm instead of asserting it.