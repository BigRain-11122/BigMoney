# DIGEST 2026-10-21 - E75 panel split audit

Leg: `panelsplit` in `scripts/e39_panel_census.py` (selftest 145/145).
Faces: `results/e44_midmonth/PANELSPLIT-20261021.json` (2020 start), `PANELSPLIT-20261021-s20130101.json` (2013 start).
Screen: consecutive PRICED closes (missing bars skipped, never filled), flag |return| > 30%. Charge: one name in an equal-weight book of n live names costs |r|/n.

## Headline

- **161** single-session moves past the screen on **152 names** (2020 start, 1646 sessions, median breadth 716); 135 of them are ADJACENT sessions, which no A-share/ETF print can legally produce.
- Book-level cost of those prints: **1469.80 bp total / 216.12 bp/yr** (max single event 31.91 bp, median 5.16 bp). The 2013 start reads 3076.74 bp total / 223.06 bp/yr over 13.79 years.
- 74 of 161 events land within 2% of an INTEGER share ratio (1/(1+r)), i.e. a corporate action; the other 87 are unclassified (resumption, restatement or misprint) and are listed rather than declared clean.
- Size context: the census chain has been chasing a **-45bp** weekly-vs-monthly residual (E70). The panel-wide artefact surface is **4.8x** that per year, and one 30%-breadth-era print alone can move the newest-era book 25-32bp.
- The panel is ETF-only (`sh510*`/`sz159*`): every flagged print is an ETF unit split, a reverse split or a data restatement, never an ordinary stock move.

## Events per era (2020 start)

| era | events | total book bp | bp/yr | max event bp |
| --- | --- | --- | --- | --- |
| pre2017 | 0 | 0.00 | - | - |
| 2017_2020 | 4 | 103.58 | 467.07 | 30.78 |
| 2021_2023 | 48 | 722.59 | 266.86 | 31.05 |
| 2024_now | 109 | 643.63 | 245.14 | 31.91 |

Era table at the 2013 start (same leg, longer window):

| era | events | total book bp | bp/yr | max event bp |
| --- | --- | --- | --- | --- |
| pre2017 | 3 | 1606.94 | 1227.90 | 706.41 |
| 2017_2020 | 4 | 103.58 | 467.07 | 30.78 |
| 2021_2023 | 48 | 722.59 | 266.86 | 31.05 |
| 2024_now | 109 | 643.63 | 245.14 | 31.91 |

The pre2017 column is the sharp one: **3 events move the book 1606.94bp** because breadth there is 14 names, so a single unadjusted print is worth up to 706bp. Any pre2017 dispersion or ladder number computed on that book inherits the print.

## Events per year (2020 start)

`{"2020": 4, "2021": 29, "2022": 12, "2023": 7, "2024": 11, "2025": 33, "2026": 65}`

## Top 10 events (2020 start)

| name | date | prev close | close | ret %% | implied ratio | book bp | gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sh510580 | 2024-09-02 | 0.5760 | 2.2780 | +295.49 | 3.955 (integer) | 31.91 | 1 |
| sz159975 | 2021-01-29 | 7.6100 | 0.7580 | -90.04 | 10.040 (integer) | 31.05 | 1 |
| sh510230 | 2020-08-17 | 5.6830 | 1.2050 | -78.80 | 4.716 (unclassified) | 30.78 | 2 |
| sz159845 | 2022-08-02 | 0.7580 | 2.0990 | +176.91 | 2.769 (unclassified) | 28.49 | 1 |
| sz159300 | 2024-06-25 | 0.9730 | 3.4620 | +255.81 | 3.558 (unclassified) | 28.30 | 1 |
| sh560010 | 2022-09-14 | 0.9770 | 2.7280 | +179.22 | 2.792 (unclassified) | 28.09 | 2 |
| sh512100 | 2022-09-05 | 0.9820 | 2.7130 | +176.27 | 2.763 (unclassified) | 27.94 | 2 |
| sh510210 | 2021-01-25 | 5.0190 | 1.0060 | -79.96 | 4.989 (integer) | 27.76 | 2 |
| sz159393 | 2025-03-31 | 1.0000 | 3.8880 | +288.80 | 3.888 (unclassified) | 27.37 | 1 |
| sz159909 | 2021-03-11 | 6.8740 | 0.7070 | -89.71 | 9.723 (unclassified) | 27.27 | 1 |

## Which published legs are exposed

- Structural rule: every census leg in this file charges per-name returns out of the same `e27.load_universe()` closes, so an unadjusted print enters any equal-weight number at weight 1/n. Only **staletail (E74)** screens for it.
- Selection channel: `_rank`/`_rank` sorts on traded **amount**, and a split re-prices the share on the same date, so the ranked book's membership is distorted at the return date too -- a screened return with an unscreened ranking still carries the artefact.
- Concretely exposed published families: ladder/wide book (E27-E31), pair, cashdrag, tilt/tiltera, era, spreadsize, tilt4, widecomp, neutralrob, burnin, knife, warmspread, livespan, cutcurve, midmonth, chase, midsweep, entrydelay, earlydelay, neighborhood, weeklyclash, weeknames, stalehold (E72: pre-screen numbers, deliberately kept beside E74's guarded ones).

## Honest boundaries

- the screen flags arithmetic impossibilities, not confirmed corporate actions: an adjacent-session move past 30% cannot be a real A-share return under the 10%/20% limits, but the panel also carries ETFs and bonds whose daily limits differ, so a flagged ETF print may be genuine
- the integer-ratio fingerprint is inferred from the price ratio alone with a 2% band and no announcement feed; non-integer events are listed as unclassified, never as clean
- book impact assumes equal weight at 1/n of the live breadth: it sizes the distortion, it is not a correction to any published number
- gapped events (a resumption after suspension) can be real; the adjacent flag is the hard screen and the gap is published on every row
- pick_n is unused here by design -- the audit covers the whole panel so no book construction can hide a print
- descriptive census only: no gate, no verdict, no ledger booking, trial 0

## Next

E76-PANELSCREEN-REGRADE: add an opt-in screened loader (drop or neutralise the 135 adjacent-impossibility prints) and re-derive one headline leg -- ladder + era spread -- screened vs unscreened, so the size of the correction is measured rather than asserted. Window <=48h.
