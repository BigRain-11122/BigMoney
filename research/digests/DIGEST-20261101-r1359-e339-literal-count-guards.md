# DIGEST 2026-11-01 r1359 (bm-b) — E339: the silent branch of a literal-count guard is real, but it is where repairs happen and its "was it paid for" test is uninformative

**Card:** E339 → **Face:** `results/state_tilt/GUARDLOOSEN-2026-11-01.json` → **Script:** `scripts/e339_literal_count_guards.py`

## The question

E337 repaired one hard-coded inertness guard by publishing a transition instead of a literal "nothing moved".
Its digest named the general failure: **a guard that hard-codes a count either goes red on the next legitimate
landing, or gets quietly loosened so it stops going red.** The first branch is loud. The second leaves no trace,
so the card asked for a census of every literal-count guard in `smoke_test.py` and the S6 leg table, a
classification of every edit to them out of git history, and — for each loosening — whether the same commit also
republished a face whose count moved.

## What was measured

| axis | reading |
|---|---|
| guards at head | **86** (85 in `smoke_test.py`, 1 in `Tools/s6_chain_bmb.py`) |
| population of possible relaxations | **41 commits** that delete ≥1 line in those files (150 deleted lines in the whole history — the file grows by appending) |
| relaxed since landing | **2** — both `deleted`-kind, **0** literal raises, **0** operator changes, **0** tightenings |
| how they disappeared | **2 of 2 by replacement** (the predicate was rewritten under a new name), **0 outright removals** |
| exact-count guards at head (`==`/`!=`, literal > 1) | **7** |
| of those, counting a *corpus* (landing-fragile) | **0** |

The two loosened guards are the same gate, loosened twice:

```
c169c702  same_day = [...opens.get(sym) == date...]        len(same_day) == 0
      →   viol     = [...hold_days == 0 and not is_t0()]   len(viol) == 0
8e06e8a7  viol (hold_days == 0)
      →   same_day = [...hold_days <= 0...]                len(same_day) == 0
```

Both are the T+1 invariant. Both loosened it (the accepted set widened). Both were labelled false-positive
repairs of an over-strict check, and both explanations are in the commit message. Read as the card framed them,
the silent branch is **not a hack in this tree — it is where repairs go**, and the reason it is silent is that a
loosened guard produces no output at all: the gate that would have objected is the gate that was changed.

## Why the "was it paid for" reading had to be priced against a base rate

The card's test — did the same commit also publish a face whose count changed — **cannot distinguish anything in
this repository**: of the 41 commits that deleted a line in a guarded file, **39 (95.1%) touched `results/` and
39 moved a number in a `results/*.json`**. A round here republishes a dozen status faces whether or not it touched
a guard. So the reading was published with its own base rate rather than as evidence, and the interesting number
is its complement:

**`c169c702` is the only one of the 41 that touched neither a face nor a number.** A pure guard change, with no
published consequence anywhere. That is the shape of a loosening nobody would ever see, and it happened exactly
once — and it was a repair, not a fudge.

## The premise the census corrected

E337's fear was that a hard-coded count "breaks on the next landing". In these two files it does not, because
**none of the seven exact-count guards counts a corpus**: they count study-internal structures
(`len(combos) == 432`, `len(_arms62) != 16`, `len(h1) == 8`, `len(_clamp101) != 3`, `len(_gw42) != 2`,
`len(_trim.get('interval') or []) != 2`, `len(_r330['branches']) != 2`). A new `.py` landing cannot move any of
them; only editing the study that owns the fixture can. The landing-fragile population is therefore **0**, and
publishing "7 guards would break on the next landing" would have been the wrong headline from correct arithmetic.

## Defects caught in this round

1. **Substring matching on guard expressions.** The first pass keyed guards by `expr` with plain `in` matching,
   so `_n` matched `_name338` and every leg in the file became a candidate edit of every other (274 events, most
   of them noise). Token boundaries (`(?<![\w])expr(?![\w])`) cut it to 9 real events.
2. **`.get()` counted as a count.** Treating every `Call(attr='get')` as count-shaped pulled in tolerance
   comparisons (`...get('max_abs_diff_t_max_end') != 0.0`). Now a `.get()` counts only when its key carries a
   count word, and floats are excluded — a tolerance is not a count.
3. **A rename is not a removal.** `len(viol)` → `len(same_day)` appeared as one deletion; without the
   replacement pairing (same commit, same file, same op + literal) it would have read as "the gate was deleted".
   The `relaxed_by` field is what separates them, and the smoke leg refuses a replacement whose partner does not
   carry the deleted literal.
4. **98 s build from 82 `git show` spawns.** One `git cat-file --batch` for all versions: 6.8 s.

## Verification

- `selftest 28/28`; `run` → dated face + `guardloosen_latest.json`; `verify` → **0 problems** (re-derives the
  whole face in ~7 s).
- Smoke leg extracted verbatim (`scripts/run_e339_smoke_leg.py`): PASS; a doctored face
  (`relaxed: 99`, `share_numbers_moved: 0.5`) was caught with two named problems and the published bytes were
  restored identically (sha256 `6702fd2f2372`).
- Chain leg `literal_count_guards` wired into `Tools/s6_chain_bmb.py`.

## Seeded next

`E342-WHICH-REPAIRS-LEAVE-NO-OUTPUT` — every loosened guard in this tree was a false-positive repair, and the
repair's only record is a commit message a human must read. Ask the general question: of the guards that were
rewritten in place to stop firing, how many left behind a machine-readable statement of what they now accept,
and what would a face look like that a repair had to publish?