# r1306 — the commodity sleeve: 30% of the gross return, and it is mostly gold

**Question.** `results/etf_equity_alpha.json` says the commodity class produced 30.1% of the
book's gross return while the book held only ~6% of its weight in it on average. Nothing in
the repo priced the same engine on a commodity-only universe, so the reading was ambiguous:
either the ranking picks metals well, or the book is a dressed-up holder of gold.

**Method.** Three arms, one basis (N5/R20/10bp, decide at close t → fill at open t+1 →
hold to the next open), all reusing `etf_composite_pf.build_score` and
`etf_equity_alpha.run_with_attribution` — no re-implementation:

| arm | what it is |
|---|---|
| `all_classes` | the published cell, re-priced as the CONTROL |
| `commodity_only` | the same engine re-ranked inside the 41 commodity ETFs |
| `commodity_ew` | equal weight of every eligible commodity name |
| `deepest_name_passive` | buy and hold 518880, the deepest-turnover commodity ETF |

**Control.** `all_classes` re-prices at 9.12%/yr against the published 9.13% (−0.01pp, on a
panel three bars longer), so the arm the deltas are taken against is the arm that was
published (r1297).

**Read.**

- **Commodity-only book 16.31%/yr, Sharpe 1.02, maxDD −27.0%, turnover 0.45** versus
  **11.45%/yr (0.71, −33.2%) for holding the sleeve equally** → selection adds **+4.86pp/yr**
  (+2.09pp IS, +9.16pp OOS).
- **Passive 518880 returned 13.91%/yr** (0.86, −31.2%). So the sleeve beat holding the metal
  by **+2.40pp**, and equal-weighting the 41 names would have *lost* to it by −2.46pp.
- **Concentration is real, not a single name.** 15 distinct names over 82 decisions, the
  most-held name (518800) takes 17.1% of the slots, and the five names held at least half
  the time are 159934 / 159937 / 159980 / 518800 / 518880 — gold proxies plus one industrial
  metals ETF. So it rotates among metal vehicles rather than sitting in one.
- **But the raw return is metal beta.** 13.91 of the 16.31 points are "hold gold"; the
  ranking is worth +2.4pp over that, and its excess over equal weight is concentrated in
  2024+ (+9.16pp OOS vs +2.09pp IS) — the same 2020+/2024+ shape as the whole book
  (`DIGEST-20261027-r1305-pre2020-out-of-period.md`).

**Verdict.** The commodity sleeve *is* a selection sleeve against its own equal weight, but
the honest description of its 30.1% contribution is "gold-beta exposure with a modest
ranking overlay", not "a commodity ranking that pays". Reading the 30% as evidence that the
six factors work on metals would be wrong by 13.9 of 16.3 points.

**Carried limits.** 41-name cross-section; a 5-name book holds 12% of the sleeve, so single
names move it. The ETF pool has no delisted funds (survival-filtered). No preregistration,
no verdict booking, no ledger entry.

**Where it lands.** `scripts/etf_book_production.py` now reads
`results/etf_book_commodity_split.json` and prints the verdict as the card's second caveat
(right after the pre-2020 line), with two selftest legs (artifact present → the numbers must
read out of both arms; artifact absent → production still runs) and r1262's discipline
applied: the names recovered by the picks replay are only trusted because that replay
reproduces the engine nav exactly (max gap 0.0).

**Method card.** E140 in `knowledge/METHODOLOGY_ASSETS.md` — "a contribution share is not a
skill share: price the sleeve restricted and against its own passive alternative".

Artifact: `results/etf_book_commodity_split.json` (schema `etf_book_commodity_split/v1`).
Script: `scripts/etf_book_commodity_split.py` (selftest 10/10).