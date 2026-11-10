# DIGEST-20261110-r1665-e648-key-genericity

- study: **E648** — how generic are the six counted row keys, corpus-wide?
- round: **r1665 bm-b** (2026-11-10) · machine `bm-b` · lane `cpu-only`
- face: `results/state_tilt/KEYGENERICITY.json` + `keygenericity_latest.json`
- tool: `scripts/e648_keygenericity.py` (selftest 14/14, `check`/`verify` `problems=[]`, rebuild byte-identical `d4678dfc27b9`)
- legs: `smoke_test.py` leg E648 (`scripts/run_e648_smoke_leg.py` 1/1 PASS, `--doctor` 1/1 red with the face restored byte-identically) + `Tools/s6_chain_bmb.py` leg `key_genericity` (rc=0)

## Why the question exists

E642's headline is "zero module-level two-depth writes in the six modules that hold the counted reads",
followed by a weak arm: "seven module-level writes elsewhere name one of the six counted row keys".
E646 then spent a whole round proving all seven are name collisions. Both readings rest on **literal
key-name equality** over six keys that are ordinary English words (`verdict`, `rows`, `days`, `bar`,
`x1`, `slip_exec`). E207/E208 say a name is not a measurement; the missing piece was the **base rate**:
if `rows` is spelled in 400 files, one collision means nothing; if `slip_exec` is spelled nowhere, one
collision is the whole population.

## Readings (re-derived from the tree, no lineage test)

| quantity | value |
|---|---|
| python files seen / parsed | 13,086 / 12,778 (holes: 304 do not parse, 4 over the 1MB cap) |
| files spelling ≥1 counted key | 3,854 |
| counted read lines / keys / modules | 13 / 6 / 6 |
| literal string occurrences of the six keys | 16,956 |
| subscript sites | 8,389 (read 5,802 · write 2,587 · delete 0) |
| dict-literal key sites | 2,734 |
| computed subscripts (invisible to the literal arm) | 149,479 |
| distinct receiver roots | 49 |

Per key: **5 of 6 are generic words** (≥20 files outside the counted faces), **0 narrow**, **1 private**.
The widest is `verdict` — 3,473 files / 3,657 read sites; the narrowest is `slip_exec` — **0 files
outside the counted faces**, 5 read sites, i.e. a private address.

Verdict: `the six counted row keys price differently... so a key-name hit has to be priced per key
rather than over the set`.

## Three reusable laws

1. **A key-name test is only as strong as its inverse base rate.** Publishing the hit count without
   "how many unrelated files spell this word" makes a collision look like evidence. Publish the
   outside-file count beside every hit, and classify with **floors frozen before the run** (20 files =
   generic, 1..19 = narrow, 0 = private).
2. **"Seen" and "scanned" are two numbers, not one.** 311 of 13,086 files were holes (304 unparseable
   ad-hoc scripts + 4 over the 1MB read cap). Naming a single counter `python_files_scanned` and
   filling it with the attempted count makes `scanned + holes != seen` undetectable; publishing both
   and asserting the identity is what turns the hole list into a measurement instead of a footnote.
3. **A per-key census cannot be re-added from per-key rows alone.** The file denominators belong to the
   scan, not to any key, so the face gate must (a) re-add every per-key column from the rows and
   (b) separately assert `scanned + holes == seen`; demanding that the denominators re-add from rows is
   a checker bug that looks like a face bug.

## Limits carried on the face

- a literal string is not an access: docstring prose raises the base rate without any code reading a key;
- the subscript arm only matches literal slices — computed keys (`k='verdict'; D[k]`) are counted
  separately (149,479 of them) rather than folded into the zero;
- `files over 1MB are skipped` (E391's cap), so a very large module that spells a key is in any consumer
  that reads the file directly but absent from this denominator — `smoke_test.py` (28k lines) is exactly
  such a file;
- the receiver root is the leftmost `Name`, so two different objects under one name share a row;
- the class is a base rate, not a lineage test.

## Not run this round

Full smoke suite (r1499: no leg filter, ≈30 min), the rest of the S6 chain (only this leg), GPU work
(parked, C-20261014-01 §3), any cloud call, any deletion.
