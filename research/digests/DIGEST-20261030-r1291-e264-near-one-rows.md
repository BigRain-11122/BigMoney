# E264 — a near-one multiplier is a bucket, not a row-side hazard

**Face** `results/state_tilt/BANDNEAR1-2026-10-29.json` (+ `bandnear1_latest.json`)
**Runner** `scripts/e264_near_one_seeds_reading.py` (run / verify 0 problems / selftest 26/26)
**Cutoff** 2026-10-29 · reads E259's published face only, no draw, no panel, no re-pricing
**Verdict** `closest_row_survives_without_them`

## Why this needed asking

E259 published, per (window, leg, base count), 40 independent multipliers `m_k = edge_k(top) /
edge_k(base)` and read the interval as `[p05, p95]`. E261 then showed the floor at exactly one
belongs to the endpoint-already-attained bucket rather than to the stream. Both results are about
the *band*. Neither answered the row-side question: a published row's verdict at multiplier `m` is

    outside  <=>  |b| > max(|lo|, |hi|) * m  <=>  m < m*   where  m* = |b| / max(|lo|, |hi|)

so `m*` alone decides where a row flips — no draws involved. Two things follow that E259/E261
could not see from the arm side:

1. which published row sits **closest** to its band, and
2. whether the `p05 == 1` floor those near-one seeds create is **load-bearing** for it.

## What was measured

**12 of 16 rows are readable**; the 4 unread ones are `pre2020_four` and `era_2020_2022` (self and
cross), which carry no coefficient or no band on the E259 face — disclosed, not absorbed.

**4 rows end exactly on the floor** (`p05 == 1.0`). Dropping every near-one seed lifts `p05` to
1.110–1.201 (median shift 0.090, max 0.201) — and **no row's tight-end verdict moves**. The reason
is arithmetic: those four rows carry `m*` between 2.14 and 3.08, so the floor would have to roughly
double before it could reach any of them. The floor is a property of the attained bucket, and the
rows that touch it sit far outside their bands.

**The closest row is at the wide end, not the floor.** `era_2025_now` cross:60 has
`m* = 1.9583` against its own `p95 = 1.9678` — a gap of **0.0095**, i.e. 0.48 % of the multiplier.
It clears its own wide end and nothing more. Then `era_2023_2024` self:60 (`m* = 2.0991`, gap
0.0757) and `era_2023_2024` star_lag1_residual cross:60 (`m* = 2.1384`, gap 0.1223). Median gap
across the twelve is 0.413, max 1.551 — the distribution is lopsided: a handful of rows sit within
a tenth of a multiplier of their edge and the rest are nowhere near.

**Cross-check against E262 (disclosure, not a screen).** The two rows a borrowed wide end actually
moved — `era_2025_now` cross (index 9) and `era_2023_2024` star_lag1_residual (index 13) — are
both inside the top-3 closest. The third-closest (`era_2023_2024` self, gap 0.0757) did not move,
because no published donor at that leg/base reaches `m* = 2.10`. So the row-side ranking recovers
the transfer damage, but "closest" is a superset rather than an equivalence; whether the screen is
exact at `m*` is E265's study.

## What this settles and what it does not

Settled: the E261 floor finding has **no row-side consequence** on this face. Removing the
near-one seeds changes the interval's tight end by up to 0.20 and changes zero verdicts, because no
read row has `m*` anywhere near one. A reader who worried that the floor was propping up rejections
can stop worrying about that mechanism here.

Not settled: the wide end. Every row that sits close sits close to `p95`, which is exactly the end
E262 showed is donor-dependent. This face publishes the ranking; it does not test a threshold rule
(E265) and it does not re-derive any row's science verdict.

## Pits recorded

1. The first fixture asserted "inside at the floor, outside without it" and the code returned
   `outside → inside`. The code was right: `outside <=> m < m*`, so dropping the floor *raises* m
   past `m*` and **loses** the rejection. The assertion encoded the opposite direction of the same
   flip (r1281 shape: the assertion was wrong, not the code).
2. `e262.row_records` reads `band_draws` off the row; the fixture carried `base`. The leg failed on
   a missing key rather than on a wrong number, which is the cheap failure.
3. A near-one flag tested on existence ("this arm has near-one seeds") would have flagged rows
   whose floor is nowhere near their threshold. It is the **conjunction** of "the tight end was the
   floor" and "dropping it moves the verdict" — named `near_one_dependent`, pinned by legs
   (E207/E208 family).
4. PowerShell does not take heredocs (`python - <<'PY'`) — the wiring patch died in the parser and
   the edit tool did the job (r1288/r1290 pit, third sighting).
5. The smoke leg cannot be run by the suite in-window (~35 min), so it is executed by extracting
   its own source text out of `smoke_test.py` and exec'ing it
   (`results/_r1291bmb_e264_smokeleg_harness.py` → PASS). A re-implementation would prove the copy.