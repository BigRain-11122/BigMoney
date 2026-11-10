# DIGEST 2026-11-10 r1670 bm-b -- E649 guarded module-level writes

**Question.** E643 published two independent numbers: 2,641 two-depth write sites with no enclosing
function, and 3,237 module-body sites inside a module-level compound statement. Both can be true
while "module-level write" still does not say whether the write runs at import. Which of the 2,641
write sites execute behind a module-level guard?

**Method.** Re-parse the E391 corpus (E638's two-depth grouping, E640's owner split), keep the sites
with no owner function that carry a store/delete, and for each publish the guard region holding its
(position) inside the module-level block tree -- bare body, `if __name__ == '__main__'`, other
conditional, loop, `with`, `try` body, `try`-else, `except` handler, `finally` -- plus the full
nesting chain, the region depth, E643's bucket, the literal keys its write members address, and
whether any of them names one of E633's counted row keys (derived live from the E638/E640 join).

**Reading.**

* 13,110 files; **2,641** residual write sites -- identical to E643's published 2,641 (delta 0).
* guards: bare 1,629 / loop 548 / conditional 380 / except handler 67 / try 17.
* **1,629 run unconditionally at import; 1,012 (38.3%) sit behind a guard.**
* **0** carry `if __name__ == '__main__'` on the chain -- the guard everyone expects is absent.
* region depth 0:1,629 / 1:612 / 2:284 / 3:91 / 4:16 / 5:5 / 6:2 / 7:1 / 8:1 (deepest 8,
  `results/_r979bma_resolve.py`).
* exactly **1** site names a counted key: `results/_r920bmb_n2u3_flip.py:71` writes its own
  `verdict` row (a generic word E648 priced at 3,473 files), inside one conditional.
* 0 write sites are outside the module body (E643's bucket split and this guard split agree).

**Verdict.** `module_level` is two execution faces, not one: 61.7% is an import-time write face and
38.3% is code that may run zero, one or many times.

**Limits carried in the face.** Execution timing is read off the guard kind alone (a loop may run
zero times, a `with` may raise, a conditional may be false); only literal keys can name a counted
key, so the key column is a lower bound; region depth exceeds AST block depth exactly on `try`'s
else/finally, which carry no node of their own; files over 1MB are skipped and counted apart.

**Evidence.** `scripts/e649_guarded_write.py` (selftest 24/24, check/verify `problems=[]`) ·
`results/state_tilt/GUARDEDWRITE.json` + `guardedwrite_latest.json` ·
`scripts/run_e649_smoke_leg.py` (1/1 PASS, `--doctor` red with byte-identical restore) ·
`smoke_test.py` leg E649 · S6 leg `guarded_write` (rc=0, 0.07s).
