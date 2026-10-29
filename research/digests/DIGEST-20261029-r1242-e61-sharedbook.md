# r1242 / E61 — the mid-month calendar gap, split into a timing part and a selection part

**Face:** `results/e44_midmonth/SHAREDBOOK-20261028.json` (study `e61_shared_candidate_pool`)
**Runner:** `python scripts/e39_panel_census.py sharedbook` (new CLI mode, new S6 leg `sharedbook`)
**Method card:** E215 · **Chain:** S6 leg `sharedbook` (after `offbookera`)
**Engine seam:** `e27.simulate(..., universe_at=callable)` (default `None` = static universe, every published curve unchanged; selftest 9 → 11 legs)

## Why

E57 (r1134) named the mid-month entrants and found that 50.4% of them are names the month-end book
*still holds* (+0.96% forward vs +0.89% for month-end entrants). That is a **name-level** reading of a
**portfolio** question. The pool card has carried the portfolio version since 2026-10-21
(`E61-SHARED-SUBSET-BOOK`, status `waiting`) and the blocker was stated as "needs an engine seam —
per-session holdings". The engine does return holdings, but `simulate` only accepted one static
universe, so the per-session restriction could not be expressed. It can now.

## What this leg does

Three arms, one load, one calendar, one rank function, all at x0 (cost was closed on this family):

- `me` — month-end calendar, full eligible universe, top-N by trailing liquidity
- `mid` — mid-month (day 15) calendar, full eligible universe
- `mid_shared` — mid-month calendar whose **candidate pool at each session is the month-end book's
  holdings at that session**

The split is then an identity, not two measurements:

```
total     = mid − me            (the gap being explained)
timing    = mid_shared − me     (same names on offer, different decision sessions)
selection = mid − mid_shared    (what the wider candidate set adds)
residual  = total − (timing + selection)          ← must read 0.0
```

The pool is deliberately **one-sided**. "Names both calendars hold at the same session" would put the
mid arm's own book inside its own candidate set — circular, since the pool would already contain
whatever the arm decides to buy.

## Reading

| window | me | mid | mid_shared | total | timing | selection | residual |
|---|---|---|---|---|---|---|---|
| full (2020-01→2026-10) | −1.56%/yr | −1.38%/yr | −0.72%/yr | +18.0 bp | **+84.0 bp** | **−66.0 bp** | 0.0 |
| 2021_2023 | −11.14% | −11.30% | −10.88% | −16.0 bp | +26.0 bp | −42.0 bp | 0.0 |
| 2024_now | +9.48% | +10.22% | +11.39% | +74.0 bp | **+191.0 bp** | **−117.0 bp** | 0.0 |
| 2017_2020 | 0.00% | 0.00% | 0.00% | degenerate cash slice — not counted | | | |

Width control (`widths`): pick_n = 10 for every arm, pool median 10, `pool_binds=true`
(early sessions have a pool of 0–9, i.e. before the month-end book is invested) — so the restriction
really bit and the arms are the same width where a comparison is made.

Three things are load-bearing:

1. **Timing is a gain in both counted eras, selection is a loss in both.** In the newest era the
   mid-month calendar earns **+191 bp/yr more on the same names**, and then gives back **117 bp/yr**
   by choosing from a wider candidate set. The published net gap (+74 bp) is the small difference of
   two much larger, opposite-signed parts — which is why E57's name-level reading ("they are early,
   not wrong") and the portfolio reading ("the wider pool costs money") are both true and neither is
   the headline.
2. **The full-window sign of the net gap is not the newest-era sign in size.** Full window +18.0 bp
   against +74.0 bp in 2024_now: the pre-2021 panel (2012→2020 is outside this 2020-start window) and
   the burn-in block dilute it. Any single-number quote of "the mid-month calendar costs/earns X bp"
   has to name the era.
3. **The zero era is a burn-in block, not robustness.** 2017_2020 prints 0/0/0 for all three arms
   because at a 2020-01-01 start the first invested decision is 2021-01-29 (E212). It is tagged
   `degenerate_cash_slice` and excluded from the dominance count instead of being read as "the parts
   balance in every era".

## Rules

(a) **A gap that arrives already decomposed must carry its identity residual.** Three numbers that are
    algebraically tied are a check on how the arms were run; if the residual is not printed, a reader
    cannot tell a decomposition from three independent (and possibly incompatible) measurements. The
    leg fails its own smoke leg when `identity_ok` is false.

(b) **"The candidate set" is a per-session object, and the engine only had a static one.** Adding
    `universe_at` as a default-`None` seam (the same shape as the `contrib` seam) keeps every published
    curve bit-identical while making the question askable. The idx-keyed rank cache is bypassed in
    that mode: two decisions can now share an index with different pools, and a cache would answer the
    second with the first's pool.

(c) **A two-way split needs its widths pinned first.** At pick_n=9999 both books hold the whole
    universe, the candidate set difference vanishes and the "selection part" would read 0 by
    construction — a fake confirmation. The leg pins pick_n=10 and publishes the pool-size distribution
    so the reader can see whether the restriction bound at all.

How to apply: when a calendar (or any structural) cost is being attributed, restrict the treatment arm
to the control arm's own pool at each session, publish the identity residual beside the two parts, and
never quote the net gap without the era it was measured in.