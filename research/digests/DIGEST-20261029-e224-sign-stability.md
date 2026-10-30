# E224 — the six sign directions rank 6 of 64 on one window, and the ordering does not survive a split of it (r1337 bm-c)

**Card:** E224 in `knowledge/METHODOLOGY_ASSETS.md`.
**Artifacts:** `results/etf_sign_stability.json` (re-emitted every chain run by the new
`etf_sign_stability` leg) + a smoke leg that recomputes the verdict from the per-period table.
**Code:** `scripts/etf_sign_stability.py` — selftest 21/21. One panel load, all 64 sign sets,
sub-period numbers sliced off the same trading path (~100s, offline, deterministic).

## The sentence E223 left open

E223 ran all 2^6 sign sets and priced the choice: production rank 6/64, median arm −1.63%/yr,
best-of-64 +8.56%, spread 20.8pp/yr. Every one of those numbers is **one window**
(2020-01-01 → 2026-10-28). A rank only means something if the ranking is a property of the
panel rather than of the period, so this face splits the window and re-ranks both halves:

- IS = 2020-01-01 … 2023-12-31 (1,043 bars)
- OOS = 2024-01-01 … 2026-10-28 (457 bars)

Frozen before the run: `REBAL=20, N_HOLD=12, COST=10bp/side, TOP_DECILE=0.10,
SPEARMAN_TRANSFER=0.50, MIN_BARS_PER_PERIOD=200`. Determinism check built in: the full-window
rank recomputed here is **6/64, identical to E223's stored rank**.

## What the split says

| | value |
|---|---|
| Spearman(IS arm ranks, OOS arm ranks) | **0.308** (null sd 0.126, z 2.44) |
| frozen transfer line | 0.50 |
| top-decile (7 of 64) arms shared by both halves | **1** (chance 0.77, p(≥1) = 0.574) |
| production rank, IS / OOS / full | **8 / 10 / 6** |
| production CAGR, IS / OOS | 2.12% / 12.81% |
| median arm CAGR, IS / OOS | −4.27% / 2.92% |
| in-sample-best arm, out of sample | **−2.34%/yr, rank 45/64** |
| "pick the best half and trade the second" vs the median arm | **−5.26 pp/yr** |

Verdict, recomputed by the gate from the per-period table: **`sign_ordering_does_not_transfer`**.

Three readings that matter, in order:

1. **The rank is not learnable.** A chooser that picks the best of 64 sign sets on 2020-2023
   and trades 2024-2026 lands at −2.34%/yr — 45th of 64, i.e. worse than the median arm by
   5.26pp. The single best arm of 64 becomes a below-median arm in the next period.
2. **The ordering is not noise either.** ρ = 0.31 sits 2.4 null-sd above zero, so there is some
   real persistence — but far too little to act on: at the level that decides a position
   (top decile) the two halves agree on 1 of 7 arms, and the chance overlap is 0.77 (p = 0.57).
   "Some weak ordering exists" and "you can rank arms" are different claims; the second is false.
3. **The level moved far more than the ordering.** The median arm went from −4.27%/yr in
   2020-2023 to +2.92%/yr in 2024-2026 (+7.2pp) with the *same* factors, same width, same
   costs. What E223's single-window median (−1.63%) actually describes is the average of two
   very different periods. So the honest quote for "what picking directions blindly is worth"
   is a range, not a point.

## Where the production advantage actually lives (main effects, per half)

Balanced factorial design, so each factor's direction is readable without extra engine runs:

| factor | effect IS (pp/yr) | effect OOS (pp/yr) | production sign is the paying one? |
|---|---|---|---|
| vol_60 | −3.76 | **−6.67** | yes, and it strengthens |
| intraday_range | −1.38 | **−7.45** | yes, and it strengthens |
| adx_14 | +2.41 | +1.99 | yes, both halves |
| mom_12_1 | +0.87 | **−4.99** | **no out of sample** (sign flips) |
| drawdown_60 | −0.54 | **+3.35** | no in IS, yes in OOS (sign flips) |
| price_position | +2.15 | −0.41 | flips to a small negative |

The two low-volatility directions are the only ones that keep their sign **and** their money in
both halves; momentum and drawdown swap places. That is why the production set sits 8th/10th in
each half (just above the line, never inside the top decile) and yet still beats the median arm
by 6.39pp in IS and 9.89pp in OOS: two of six signs are period-stable and they carry the edge.

## Consequence for money

- No headline on this line may say "rank 6 of 64" without saying "on one 6.85-year window, with
  a rank-transfer ρ of 0.31 and one shared top-decile arm". The chain leg now re-derives both
  numbers with the panel, so the quote cannot go stale silently.
- The remaining defensible sign rule is the narrow one: **vol_60 negative, intraday_range
  negative, adx_14 positive** — the three directions that pay in both halves. Momentum and
  drawdown directions cannot be claimed to be more than period artefacts, which is exactly what
  E222 predicted from the other end (trailing-IC reconstruction loses 17pp).
- Sign selection still dominates the signal (spread 20.8pp/yr vs a ~4pp published advantage
  over the equal-weight control). The correct response is not another grid on signs — it is to
  stop publishing an arm-level rank as if it were a rule.

## Caveats on this face

- Sub-period numbers are read off the **same trading path** as the full-window arm: the book
  trades across the 2024-01-01 boundary, with no fresh flat start and no re-entry cost. They
  describe "what this path did during those bars", which is what a rank-transfer test needs —
  not "what launching the book on 2024-01-01 earns".
- Reference engine only (no impact cost, no gap risk), flat sizing: not the card's headline.
- A dropped factor is a different question (E223 already priced the IC floor).
- ETF pool is today's listed set (survivorship), unchanged caveat on this line.
- The test asks about **order**, not level: a panel where all arms fall together can still show
  a stable ordering, and this one does not show one anyway.