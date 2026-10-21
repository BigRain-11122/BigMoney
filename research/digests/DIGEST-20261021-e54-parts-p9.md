# DIGEST 2026-10-21 — E54 ninths (perpetual livespan, parts = 9)

Evidence cutoff 2026-10-20. Descriptive census only: zero prereg, zero judgement, zero ledger
booking, trial_count 0. Runner unchanged: `scripts/e39_panel_census.py livespan --cost 0|3 --parts 9`.

Faces: `results/e46_live_span/LIVESPAN-20261020-x0-p9.json`,
`results/e46_live_span/LIVESPAN-20261020-x3-p9.json` (~7s per leg, inline).

Sign convention throughout: `spread_bp = wide − ladder`, so a **negative** spread means the
concentrated ladder beat the broad book. Band = max(spread) − min(spread) inside an era.

## 1. Headline

Three readings, one of them a retraction of a retraction:

1. **The internal-sign-flip set stays at 4 of 4 eras** for the fourth consecutive cut
   (sixths → sevenths → eighths → ninths). This is the stable thing in the family; granularity no
   longer adds or removes members.
2. **The band does not measure instability. It is an amplitude sum.** `band == |best part| + |worst
   part|` holds exactly in all four eras this cut (3232/2380/2426/5815). Whenever an era's parts
   straddle zero, the band adds a ladder *win* to a ladder *loss*, so a big favourable swing inflates
   it exactly like a big unfavourable one.
3. **The widest-band era changed hands and the claim flipped with it.** At eighths pre2017 owned the
   band (6332bp) from one 2014Q4–2015Q1 bull part. At ninths pre2017 **halves** to 3232bp (that part
   is cut in two) and 2024_now **triples** to 5815bp — not from a loss but from a *win*: part 8
   (2026-03-10 .. 2026-06-29, 75 bars) has the ladder at **+49.73%/yr vs the wide book at +7.32%/yr**
   (spread −4241bp) with **near-identical drawdown (−9.08% vs −8.08%)**. The era's own average spread
   is a wash (+93bp).

So the sequence of published claims now reads: r1128 "bands keep widening" → r1129 "withdrawn, three
of four narrow" → r1130 "widening again, in a different era, and for a reason that is not risk".
Every one of those was a statement about the cut, not about the strategy.

## 2. Per-era faces (x0)

| era | bars | part spreads (bp/yr, wide − ladder) | band | era spread |
|---|---|---|---|---|
| pre2017 | 1120 | 0, 0, 593, 688, **−2177**, 1055, −188, 796, 185 | 3232 | 239 |
| 2017_2020 | 974 | 497, **−1400**, 877, 962, −1319, 691, 980, −40, 461 | 2380 | 423 |
| 2021_2023 | 727 | 365, −462, −45, 806, −1207, 1219, −262, 469, −170 | 2426 | 247 |
| 2024_now | 675 | 536, 282, −430, 738, 873, −915, −481, **−4241**, 1574 | 5815 | 93 |

Cost x3 (x3 faces): era levels 230 / 410 / 237 / 81, i.e. −9 / −13 / −10 / −12bp versus x0 — the same
fee signature every cut since thirds has carried. Widest-part index is identical at both cost levels
(pre2017 6, 2017_2020 7, 2021_2023 6, 2024_now 9), so the cost axis still reorders nothing.

pre2017 keeps two dead parts at the front (0.0 spread = no invested sessions), so the pre2017 era
really resolves into 7 live pieces, not 9.

## 3. Band by cut — the metric has no cut-invariant meaning

Per-era band (bp), parts 2 → 9, x0:

| era | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| pre2017 | 41 | 403 | 931 | 1569 | 1109 | 2503 | **6332** | 3232 |
| 2017_2020 | 24 | 353 | 761 | 847 | 959 | 1737 | 1171 | **2380** |
| 2021_2023 | 190 | 637 | 512 | 346 | 1017 | 1191 | 1021 | **2426** |
| 2024_now | 593 | 670 | 751 | 1139 | 1051 | 2651 | 2086 | **5815** |
| mean | 212 | 466 | 739 | 975 | 1034 | 2021 | 2653 | 3463 |
| median | 317 | 495 | 756 | 993 | 1034 | 1947 | 1629 | 2829 |

Adjacent cuts move individual era bands by 2× routinely (pre2017 6332 → 3232 from eighths to ninths;
2024_now 2086 → 5815). The mean rises monotonically with granularity from thirds onward; the median
does not (1629 at eighths, 2829 at ninths). A mean band series is therefore not evidence of anything
except how finely the eras were chopped.

The mechanism is arithmetic: an annualised part spread is a difference of annualised returns over
~75–125 sessions, so (a) the annualisation multiplier is large, and (b) the band is a max−min, which
is unbounded in the number of pieces and monotone in `n` under i.i.d. noise on a fixed mean. Widening
with `n` is what a range does; it is not a finding about the ladder.

## 4. What the newest era's outliers actually are

- **part 8, 2026-03-10 .. 2026-06-29 (75 bars): ladder +49.73%/yr, maxDD −9.08%; wide +7.32%/yr,
  maxDD −8.08%.** The ladder ran ~42pp/yr ahead of the broad book for a quarter at the same drawdown.
  This is the single largest favourable part anywhere in the panel and it is *recent*.
- **part 9, 2026-06-30 .. 2026-10-20 (75 bars): ladder −57.37%/yr, maxDD −22.68%; wide −41.63%/yr,
  maxDD −15.16%.** The ladder gave all of it back and worse — 15.7pp/yr behind and a 7.5pp deeper
  drawdown.

So 2024_now is not "a wide band around a dead strategy"; it is **two consecutive quarters of opposite
extreme relative performance**: a strong ladder-favourable quarter followed by a ladder-hostile one in
which the ladder also carried the larger drawdown. The era average (+93bp) hides both. This is the
first cut in the family where a band member is large *in absolute return terms* rather than an
artefact of a high common level — pre2017's −4997bp part had a +203.8% ladder and +153.9% wide, while
this one is +49.7% against +7.3%.

Practical consequence: any consumer of these faces should quote (a) the flip set (stable at 4/4), (b)
the per-part spread vector, and (c) the era mean — and should not quote a band without naming its cut
and its two extreme parts.

## 5. Honest limits

- Parts are equal by bar count, not by calendar span; each era's pieces differ slightly in months.
- A part spread is annualised from as few as 75 sessions; one quarter of relative performance
  annualises to a four-digit basis-point number on its own. Nothing here is a horizon claim.
- Two dead pre2017 parts mean that era has 7 live pieces at this cut, so its band is a range over 7
  values, not 9.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.

## 6. Next

E55 tenths (inline pair) is seeded. The open supply-floor breach (ready 1 < 3) is unchanged and is
attributable to one unit — `E44-MIDMONTH-WEAKNESS` — still having no runner: it needs a mid-month
name-level diff leg in `scripts/e39_panel_census.py`, which is an authoring job, not an ignition job.