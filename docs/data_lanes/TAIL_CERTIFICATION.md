# Panel tail certification

As of 2026-11-27T08:43:50. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10658 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-26 | 2026-11-26 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-25 | 2026-11-25 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-20 | 2026-11-20 | yes | 5227/5228 | 5226 (99.98%) |
| astock_daily | 2026-11-26 | 2026-11-26 | yes | 5221/5221 | 5194 (99.48%) |
| ah_panel | 2026-11-25 | 2026-11-25 | yes | 188/188 | 185 (98.40%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-26T21:07:22` (10/10 files unchanged)
- **repo**: carried from `2026-11-26T10:24:07` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-21T02:32:03` (5227/5228 files unchanged)
- **ah_panel**: carried from `2026-11-26T10:25:02` (188/188 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5228): 002731.csv
- **astock_daily** (27 of 5221): 002383.csv, 002660.csv, 002717.csv, 002761.csv, 002983.csv, 300298.csv, 301013.csv, 301021.csv, 301170.csv, 600053.csv, 600318.csv, 600679.csv, 600681.csv, 600751.csv, 600892.csv, 600982.csv, 603008.csv, 603120.csv, 603122.csv, 603382.csv, 603385.csv, 605007.csv, 605169.csv, 605507.csv, 688121.csv …
- **ah_panel** (3 of 188): 01812.csv, 02249.csv, 02493.csv
