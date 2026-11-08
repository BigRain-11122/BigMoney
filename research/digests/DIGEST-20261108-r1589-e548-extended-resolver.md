# DIGEST — E548: how much of E527's whole undecidable population closes with the two resolver additions

- Round: r1589 bm-b, 2026-11-08
- Card: E548 (pool, cpu-only)
- Face: `results/state_tilt/EXTENDEDRESOLVER-2026-11-08.json` (+ `extendedresolver_latest.json`)
- Carrier: `scripts/e548_extended_resolver.py` (build / check / verify / selftest 13/13)
- S6 leg: `extended_resolver` (rc=0, 0.05s)
- Smoke leg: `# E548` in `smoke_test.py` + `scripts/run_e548_smoke_leg.py` (with `--doctor`)
- Parent: `UNDECIDABLEARM-2026-11-08.json` (E527, 52 sites / 53 arms)

## The question

E545 priced two resolver additions (the caller module's own top-level functions in `_fn_map`;
one hop of binding for the free names *inside* a call's argument) on the four arms E533 carried,
and closed one. Nothing had priced them over the population, so "the resolver cannot settle it"
was still a sentence about a handful of rows.

## Method

Every arm in E527's published face is re-read under four passes, each a different switch position
on E536's interpreter:

| pass | caller module's own functions | one-hop free-name binding |
|---|---|---|
| `verbatim` | no | no |
| `functions` | yes | no |
| `bindings` | no | yes |
| `extended` | yes | yes |

Nothing is executed and no source is rewritten.

## Readings

- **53 arms / 52 sites.** **43 of them name no parameter of the callee at all** — no argument
  resolver can ever move them. The movable population is **10 arms**, and that number is the
  denominator any "closed fraction" has to name.
- Of the 10: **1 closes verbatim**, **1 closes only when both additions are present**,
  **0 close under either addition alone**, **5 stop at a binding that reads module state**,
  **2 at a name the caller never binds**, **1 is a caller parameter whose call site does fold**.
  Verdict: *some arms that name a parameter close, the rest stop at a named layer*.
- **The two additions never act independently on this population.** The functions switch moves 0
  arms on its own; the binding switch moves 0; the one arm they close needs both. A study that
  reported "additions help" from E545's four-row sample would have been reading a coincidence.
- **Parent reconciliation is the load-bearing finding.** E527 declared **6 arms settled** by "the
  literal the caller binds one hop out". Re-run under this resolver, **0 of those 6 reproduce**:
  **5 rest on a module-level constant** (this interpreter refuses to read module state, which is
  a purity decision, not an oversight) and **1 on a name with no binding before the site**. The
  parent's "6 settled" and this face's "2 closed" are two different rules applied to one
  population — publishing either number alone misleads.

## Reusable lessons

1. **A "closed fraction" must name its denominator's structure.** 43 of 53 arms were never
   candidates. Quoting "2 of 53 closed" reads as a weak resolver; the truth is "2 of the 10 that
   could ever close", and the other 43 were already decided before the resolver arrived.
2. **Two additions measured together can look like two additions working.** Both switches alone
   move nothing; the arm closes only in combination. Per-addition columns are what makes that
   visible — a single "extended" column would have hidden it.
3. **Re-running a parent's verdicts needs the parent's rule, not its arithmetic.** The 6-vs-2 gap
   is not a contradiction in the totals: it is the same population measured under a stricter
   purity rule, and it is only readable because each arm carries
   `parent_settlement_reproduced` beside its own outcome.