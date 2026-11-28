# Panel tail certification

As of 2026-11-28T09:05:19. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10658 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-27 | 2026-11-27 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-27 | 2026-11-27 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-20 | 2026-11-20 | yes | 5227/5228 | 5226 (99.98%) |
| astock_daily | 2026-11-27 | 2026-11-27 | yes | 5221/5221 | 1359 (26.03%) |
| ah_panel | 2026-11-25 | 2026-11-25 | yes | 188/188 | 185 (98.40%) |

## 2 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **moneyflow**: carried from `2026-11-21T02:32:03` (5227/5228 files unchanged)
- **ah_panel**: carried from `2026-11-26T10:25:02` (188/188 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5228): 002731.csv
- **astock_daily** (3862 of 5221): 000426.csv, 001399.csv, 002219.csv, 002565.csv, 002575.csv, 002681.csv, 002717.csv, 002907.csv, 002908.csv, 002909.csv, 002910.csv, 002911.csv, 002912.csv, 002913.csv, 002915.csv, 002916.csv, 002917.csv, 002918.csv, 002919.csv, 002920.csv, 002921.csv, 002922.csv, 002923.csv, 002925.csv, 002926.csv …
- **ah_panel** (3 of 188): 01812.csv, 02249.csv, 02493.csv
