# DIGEST 2026-11-02 r1377 -- E355: the runner's imports are not the suite's imports

## What was observed

`_smoke_r1376.log` (written 06:56, after r1376 closed) ends `267/279 PASS, 12 FAIL`. Ten of the
twelve are the published census-corpus reds from r1364 (faces that no longer re-derive against a
corpus that grows every round). The other two are new and are the interesting ones:

```
[FAIL] product: the field-level branch census re-derives ... | NameError("name 're' is not defined")
[FAIL] product: the unwritten-guard presence face re-derives ... | NameError("name 're' is not defined")
```

Both legs had been delivered with the sentence "smoke leg executed standalone PASS". They were.
`scripts/run_e350_smoke_leg.py` and `scripts/run_e353_smoke_leg.py` each begin with `import re`
and lift the leg's statement block out of `smoke_test.py` by AST, so the leg ran inside a
namespace that had `re`. `smoke_test.py` never imported it, so the suite could not run the leg at
all -- and the runner reported the opposite. Earlier in the same log the same two labels appear
as PASS, which is exactly what a masking runner produces: the evidence looked green.

## What was done

1. `smoke_test.py`: module-level `import re`.
2. `scripts/prove_smoke_leg_isolation.py`: rebuilds the suite's own module head (module-level
   imports, helpers, constants; `main()` body excluded, because a leg-local name is not
   inherited) and executes an extracted leg against that namespace plus `check`/`RESULTS` stubs.
   Anything a runner injects but the suite lacks fails as NameError. selftest 6/6:
   - a suite without `import re` rejects a leg that uses `re` (the r1377 defect, reproduced);
   - the same leg passes once the head imports it;
   - a name the runner injects (`requests`) is caught;
   - a leg using a name from `main()`'s body is caught (the head is not the whole module);
   - an anchor with no `check()` call is refused by extraction rather than read as a pass;
   - all eight runner-backed legs (E341/E342/E346/E349/E350/E351/E352/E353) execute against the
     suite head.
3. `smoke_test.py` leg E355: runs the prover over `LEG_ANCHORS` and refuses a shrunken list.
   E355 is deliberately not in `LEG_ANCHORS` -- it would prove itself recursively.

## Readings

- 8 runner-backed legs: 8/8 execute against the suite's module head after the fix.
- 2 of 2 new reds traced to the same missing name, not to two independent defects.
- 10 remaining reds unchanged: this round did not attempt them (they are the r1364 corpus class,
  where the face is stale relative to a corpus that gains sources every round).

## Bound

The full ~280-leg suite was launched detached (`_smoke_r1377.log`) and had not finished inside the
round wall; the 10 corpus reds are neither fixed nor re-graded here. What is proven is narrower and
sufficient for the claim: every runner-backed leg now runs in the suite's namespace, and a future
leg cannot be delivered on runner-only evidence without this leg going red.