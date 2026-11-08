# DIGEST 20261108 r1588 bm-b — E562: does any existing field separate a deliberate one-leg run from a chain killed mid-run?

**Question.** E561 ended on a sentence it could not price: of 320 chain receipts, 159 are shorter
than the leg table of their own round, and "a stopped run and an `--only` run look identical"
inside the file. This study asks the narrower question that decides whether that gap is tolerable:
is there **any field already on disk** that separates the two — and if not, where does the
separating fact live?

## Population

159 short receipts from E561's published face (bm-b 151 / bm-c 8; 135 of them exactly one row).
Read as a **vintage** (E369): `population_source.sha16` names the E561 face, and the short class is
re-derived locally from `rows < table_at_its_round` rather than trusted as a label.

## Method — static, on the runner blob of each receipt's own round

For each short receipt: `join_commit:Tools/s6_chain_bm<X>.py` → one `git cat-file --batch` for the
whole population (159 specs, 159 reachable) → AST over each distinct blob, measuring four things:

| measurement | what it decides |
|---|---|
| writer position | does the runner close the receipt after the leg loop, or per leg? |
| selection arm | does the runner honour an `--only` argument at all? |
| skip arm | can the loop drop a leg by itself (`continue` before the row append)? |
| per-leg catch | does a leg that raises still get its own row? |

## Readings

| fact | receipts |
|---|---|
| joined to the runner blob of their own round | 159 / 159 |
| writer closes the receipt **after** the leg loop | **159** |
| writer closes it inside the loop (a kill could leave it) | **0** |
| runner honours `--only` | 159 |
| loop can drop a leg by `continue` | 0 |
| a raising leg still gets its own row | 159 |

So **0 of the 159 short receipts can be a killed chain**: a process killed inside the loop leaves no
file at all, because the write happens after the loop. All 159 are deliberate subsets. The other
half of the answer is a gap, not a resolution: **0 receipts record which legs were asked for** (a
key sweep over every receipt on disk finds no `only` / `request` / `selected` / `argv` / `subset`
field), and the only prose witness — the round reports — names `--only` on 7 lines covering 17
rounds, of which just 5 of the 135 single-leg rounds are mentioned.

## Why it matters beyond the receipt

1. **Ask where the file is written, not only what it says.** The same exception structure either
   leaves a half file (write inside the loop) or no file (write after it). The deciding fact lives
   in code, and "the field is absent" is not "the answer is absent".
2. **Historical evidence must come from the blob of that round.** Today's source proves how it
   writes today; only the join commit proves how it wrote then (E369 family).
3. **A saved artefact has to record who asked.** A future reader holding one short receipt has no
   way to tell; the round report covers 5 of 135, which is the size of that hole measured.

## Bound

Static only: no runner is executed and no receipt is rewritten. An unreadable blob would be
published as "cannot be said", never skipped silently. If a runner changes its write position the
per-row class stops holding, and the gate re-derives it from source instead of trusting the face.

## Pointers

`scripts/e562_single_leg_provenance.py` (build/check/verify, selftest 14/14) ·
`results/state_tilt/SINGLELEGPROVENANCE-2026-11-08.json` + `singlelegprovenance_latest.json` ·
S6 leg `single_leg_provenance` (1.3 s rc=0) · smoke leg `# E562` +
`scripts/run_e562_smoke_leg.py --doctor` · card `knowledge/METHODOLOGY_ASSETS.md` E562