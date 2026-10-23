# T27 availability repair, measured: the first-announce face buys real ordering — and it needs an era gate

- Date: 2026-10-24 (bm-a r1099)
- Code: `scripts/fund_avail_dispersion.py` (selftest 3/3) + `scripts/fund_avail_notice.py`
  `build_face` notice-window gate (selftest 10/10)
- Evidence: `results/fund_avail_dispersion.json`, `results/fund_avail_notice.json`

## Why this measurement

r1097/r1098 established that the collected `avail_date` is a **latest-revision**
stamp, so the published `avail_pit = min(revision, statutory deadline)` puts
almost every row of a period on the same statutory date. That destroys the
cross-sectional disclosure order any PIT event study needs, but saying so is
not enough: before wiring the first-announce repair into consumers we need the
size of the change on real rows.

This measures, on the same row set, `avail_pit` (deadline fallback) vs
`avail_first = min(source NOTICE_DATE, stored)` per (face, period), over the
periods whose NOTICE_DATE cache already exists.

## Headline (income, 43/86 staged periods, 123,933 rows)

| | deadline fallback (`avail_pit`) | first-announce (`avail_first`) |
|---|---|---|
| distinct announce dates per period (median) | 9 | 32 |
| rows available **earlier** | — | 43.8% |
| rows available **later** | — | 1.5% |
| rows unchanged | — | 54.7% |

A period with 9 usable dates gives a 9-step event-time grid; 32 gives a real
ordering. That is the difference between "everyone reports on 30 April" and a
usable disclosure-drift cross-section.

## The finding that changed the builder: pre-2010 NOTICE_DATE is a restatement stamp

Naively consuming the cache delayed **51%** of the rows, with a median shift of
~360 days, which is obviously wrong for a quarterly report. The distribution
explains it: on income 2005-03-31, 1,387 of 1,437 codes carry their first notice
in **2006-04** — the EM income table stores old quarters as they appear in later
filings, so the earliest NOTICE_DATE it exposes for a 2005 quarter is the
restatement-era stamp.

The builder now accepts a notice only inside the plausible disclosure window
`(period_end, statutory_deadline + 90d]` and reports everything else as
`notice_status = out_of_window`, falling back to the deadline bound (the
pre-existing, already-disclosed optimism). `results/fund_avail_dispersion.json`
carries the equivalent arithmetic per period so the gate itself is re-derivable.

After the gate, split by era:

| era | periods | rows | distinct dates (pit → first) | earlier | later | unchanged |
|---|---|---|---|---|---|---|
| pre-2010 | 20 | 37,858 | 9.4 → 23.6 | 1.0% | 0.4% | 98.6% |
| 2010+ | 23 | 86,075 | 11.3 → 59.1 | 62.7% | 1.9% | 35.4% |

Honest reading: **the repair is a 2010+ asset**. Before 2010 the channel
contributes essentially nothing (98.6% of rows keep the deadline bound), so any
consumer wiring must not expect pre-2010 gains, and pre-2010 event studies still
inherit the deadline-compliance assumption.

## Caveats carried, not hidden

1. Rows that stay on the deadline bound (98.6% pre-2010, 35.4% 2010+) still
   assume the filer met the statutory deadline. The face reports
   `notice_status` per row so a consumer can restrict to `ok` rows.
2. Only income has cache coverage at measurement time (43/86 periods); cashflow
   and balance are 0/86 and the background refresh (`pid 110552`, spawned
   00:56:53, ~1 period/25s) is still filling them. Re-run
   `python scripts/fund_avail_dispersion.py run` to extend the table.
3. Spearman between the two date vectors stays low (median 0.11) — expected:
   the deadline face has ~9 distinct values per period, so rank agreement is
   dominated by ties. The distinct-date count, not the correlation, is the
   load-bearing metric here.
4. `build` still refuses to publish the derived faces while coverage is
   incomplete (exit 3). This round therefore ships the gate + the measurement,
   not the face.

## Next

- When the cache completes, `python scripts/fund_avail_notice.py build` publishes
  `data/fund_statement_export/pit_avail/<face>_avail_first.parquet` and this
  measurement should be re-run to confirm the era pattern on all three faces.
- Consumer question still open: does the restored ordering change any headline
  factor result? That needs one cell re-burned with `notice_status == ok` rows
  only — the honest test of whether T27 was worth it.