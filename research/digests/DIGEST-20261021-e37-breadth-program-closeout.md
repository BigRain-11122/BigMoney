# DIGEST 2026-10-21 — E37 breadth program closeout (bm-b r1110)

Three open questions from the E36 burn (r1109) were answered in one round, four runs, zero new engines.
Everything here is descriptive census: zero prereg, zero judgment, zero ledger booking, trial_count 0.

## Q1 — is the wide-book edge monotone in breadth N?

**No.** The r1109 reading (0 / +9.4 / +23.5 bp per month at N=5/10/all) was assembled from three
separate runs on two different windows. Swept inside one run on one window
(2021-01-04 → 2026-10-20, sh511 excluded, 1,265-code universe, 1,402 bars, 57 monthly rebalances):

| book | ann % | vol % | Sharpe | vs ladder (bp/yr) | t |
|---|---|---|---|---|---|
| ladder5 (frozen five) | 0.42 | 19.25 | 0.118 | — | — |
| top5 | -5.74 | 22.55 | -0.15 | **-533.4** | -1.15 |
| top10 | 1.21 | 21.40 | 0.163 | +80.0 | 0.30 |
| top25 | 0.17 | 18.89 | 0.103 | -25.0 | -0.00 |
| top50 | 0.74 | 18.00 | 0.131 | +32.3 | 0.19 |
| top100 | -1.19 | 17.10 | 0.015 | -155.1 | -0.43 |
| top250 | -0.05 | 17.20 | 0.083 | -46.4 | -0.10 |
| top9999 (all eligible) | 2.07 | 17.00 | 0.206 | **+170.8** | 0.67 |

Non-monotone, sign-flipping, and every interior point is inside noise. Neither the top-5 concentration
nor the top-10/top-50 middle range reproduces the "more names = more edge" story. The only point that
beats the ladder is *all eligible names*, and even that is t=0.67.

**Verdict: the breadth axis is not a gradient. It is a "do not concentrate" effect.**

## Q2 — does the sh511 (money/bond block) contribution hold on the clean window?

2020-01-02 → 2026-10-20, N=all, 69 rebalances:

- excluding sh511: **+156.0 bp/yr** (t 0.69), cost 8.1 bp/yr
- including sh511: **+189.2 bp/yr** (t 0.79), cost 8.0 bp/yr

So on the post-2020 slice the bond/money block supplies ~33 bp/yr, against ~66 bp/yr on the 2018+
window measured at r1109. The block still helps, but its share of the gap roughly halves on the
cleaner slice. Honest caveat: the included run's own comparator is the same ladder5 arm, so the
33 bp *is* a same-run difference; only the comparison to the r1109 2018+ number spans windows.

## Q3 — does the post-2020 magnitude survive cost x3?

Same window, sh511 excluded, cost multiplied by three (39.12 bp/side):

- x1: +156.0 bp/yr (t 0.69), turnover cost 8.1 bp/yr
- x3: +149.4 bp/yr (t 0.67), turnover cost 24.2 bp/yr

A 6.6 bp/yr drop. **Cost is not the binding constraint** on the clean window — consistent with the
E34 finding on the ladder. If the edge is not real, it is not fees that kill it.

## The load-bearing number this round: +215.5 → +156.0

r1109 read the post-2020 wide book at +215.5 bp/yr (t 0.89). Re-running the same spec one day later,
on a panel that grew to 1,265 eligible codes with bars extended to 2026-10-20, gives +156.0 bp/yr
(t 0.69). **A 60 bp/yr swing with no change to the specification** — same engine, same window, same
exclusions.

That is the honest headline of the whole program: the *sign* of the wide-book edge is stable across
windows and cost assumptions, but the *magnitude* is inside the revision noise of the panel itself.
Anyone quoting a wide-book number to two significant figures is quoting a panel snapshot, not the
strategy. Note also the structural cause is now visible in the data: the panel had no refresh leg
until E29, and 1,671 of 1,725 panel files are still frozen at the 2026-09-22 bulk import (E30
coverage report), so the in-repo panel is a moving target by construction.

## The decisive probe: truncate the panel, not the spec

The 60 bp swing above could be a specification error or a data effect. To separate them, the *same
spec* (2020-01-02 start, sh511 excluded, N=all) was run a third time with the panel truncated at
**2026-09-22** — the date 1,671 of the 1,725 panel files are frozen at:

| panel state | wide book ann % | vs ladder (bp/yr) | t | eligible on the comparison date |
|---|---|---|---|---|
| cut at 2026-09-22 | 2.30 | **+82.7** | 0.41 | 1,190 (2026-09-22) |
| through 2026-10-20 | 1.06 | **+156.0** | 0.69 | 985 (2026-10-20 run, same date) |

Two things fall out, and the second is worse than the first:

1. **The last ~4 weeks of bars carry ~73 bp/yr of a 156 bp/yr edge.** Nearly half the magnitude comes
   from a 3% extension of the sample.
2. **Eligibility itself drifts between runs**: 1,190 codes eligible at 2026-09-22 in the truncated
   run versus 985 at that same date in the full run. The membership of the "wide book" is not a
   fixed object — it depends on which panel files happened to be current when the run started.

Verdict: three panel states, one specification, three magnitudes (82.7 / 156.0 / 215.5 bp/yr). Until
E29 makes the panel current and stable, **the wide-book number is a panel snapshot, not an
estimate of a strategy.** This is a data-availability artefact, and it is the single most important
finding of the breadth program — it invalidates quoting any wide-book magnitude, including the ones
in the two preceding digests, until the panel is fixed.

## What this closes and what is left

Closed on this round: breadth-gradient (Q1, negative), bond-block split on the clean window (Q2,
halved but present), cost sensitivity on the clean window (Q3, not binding).

Closed earlier: weighting (E24 r1093), timing (E24 r1092), cadence (E34 r1105), membership, trend
tilt (E25 r1096/r1097), concentration (E36 r1109). Book width remains the only surviving *direction*
of the ladder family — and as of this round it is a level effect ("do not concentrate") with an
unstable magnitude, not a scaling law.

Handoff, explicitly for the next deriver: do **not** open another breadth-N sweep. The useful next
question is the one this round cannot answer from a frozen panel — whether the +156 bp/yr holds on a
panel that is actually current (E29 completion), and whether it is distinguishable from merely
holding the broad universe with no signal at all. That second question needs a prereg with an
explicit comparator arm (broad-eq, no selection) and the D6 gate against `e34_broad_eq`.

## Faces

- `results/e37_breadth_ladder/UNIV-72e908-s20210101-xsh511-20261021.json`
- `results/e37_xsh511_included_2020/UNIV-4170ac-s20200101-20261021.json`
- `results/e37_breadth_x1_2020/UNIV-4170ac-s20200101-xsh511-20261021.json`
- `results/e37_breadth_cost_x3/UNIV-4170ac-s20200101-xsh511-x3-20261021.json`
- `results/e38_panel_cut_0922/UNIV-4170ac-s20200101-e20260922-xsh511-20261021.json`