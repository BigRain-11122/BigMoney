# DIGEST — E259: the draw multiplier is a distribution, not a three-seed range (r1286 bm-b)

Face: `results/state_tilt/BANDWINDIST-2026-10-29.json` (+ `bandwindist_latest.json`)
Runner: `scripts/e259_band_multiplier_distribution.py` (run / selftest 30/30 / verify)
Chain: `Tools/s6_chain_bmb.py` leg `band_multiplier_distribution`, smoke leg
"product: the draw multiplier is a distribution, not a three-seed range"
Card: `knowledge/METHODOLOGY_ASSETS.md` E259
Evidence cutoff 2026-10-29 · 4 windows × 2 legs × 2 published base counts = 16 intervals × 40 streams

## What was asked

E258 measured each published window's own draw multiplier and published it as `min..max` over
**three** shuffle streams. Three draws from a Monte-Carlo stream are not a distribution: nothing in
them says where the interval's ends sit, and every "outside at every seed" statement in the star
family rested on that range. E259 replaces the range with the sample: 40 independent streams inside
each published window (same dates, same published star, same members, prefix-nested), and publishes
`[p05, p95]` of the per-seed multipliers.

## Reading

| statement | number |
|---|---|
| intervals measured | 16 of 16 arms (4 windows: all_five, early_three, era_2023_2024, era_2025_now) |
| interval width | 0.519 .. 1.196, median 0.827 |
| interval ÷ E258's three-seed range | 1.09 .. **11.77**, median **2.25**; **16 of 16 wider** |
| published rows re-judged | 16 (10 outside at the median, 2 inside, 4 unjudgeable) |
| rows whose verdict changes inside their own interval | **3** |
| rows outside at *every* end of the interval | 7 |
| per-seed multipliers reading exactly 1.0 | **52 of 640**, spread over 14 of 16 arms |

The worst understatement is exactly where the double cross-check lived: `era_2025_now self:60`
carries a three-seed range 0.088 wide and a real interval 1.040 wide (**11.77×**). `all_five
cross:200` carries a three-seed range of 0.428 against an interval `[1.000, 1.525]`.

Three rows are interval-dependent — outside at the tight end and at the median, inside at the wide
end: `early_three` cross (`b = -0.4942`, band `[-0.2741, 0.3084]`), `era_2023_2024` star lag-1
residual (`b = -0.8332`, band `[-0.3897, 0.3463]`) and `early_three` star lag-1 residual
(`b = -0.4942`). None of them flips at *every* stream, so the honest verdict is
`interval_is_wider_than_the_three_seed_range`, not "the verdicts were wrong": what changes is how
much of the published "outside" survives a reader who stands at the wide end.

## The degenerate reading (published, not cleaned up)

A prefix-nested band has a floor: if the draw that sets the band's lower endpoint already arrived
inside the base prefix, later draws cannot move that endpoint again and the multiplier is **exactly
1.0** — 52 of 640 streams do this. Those seeds are what drag `p05` to 1.000 in 14 of the 16 arms,
and dropping them as "degenerate" would make the interval look narrower and prettier than the
streams it came from. The face counts them (`n_endpoint_already_attained`) and the smoke leg
requires an interval whose lower end is exactly one to **name** such a seed.

## Pit (the reusable one)

**A lookup keyed more coarsely than the arm it claims to read silently returns another arm's
numbers.** E258's window record is keyed by base count alone and is built with `multiplier_at`'s
default leg, so it carries the SELF arm; the first run of this face looked up `cross:60`, got the
self stream, and reported `e258_reproduced = 8/16` — a pure lookup error dressed as a
non-reproduction. The pin now applies only to the arm E258 published (`8/8` bit-for-bit) and the
other eight say `n_e258_published = no` instead of a false mismatch. Second, smaller: `verify` and
`run` are a pair — the cross-arm guard has a selftest leg that fabricates a "published" table of
9.9s and requires it to be named, not absorbed.

## What did not happen

No coefficient re-priced, no member billed, no band adopted, no panel trade beyond rebuilding the
shuffles (five-member ETF basket only). GPU parked (C-20261014-01); cloud untouched.