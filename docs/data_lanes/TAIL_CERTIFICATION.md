# Panel tail certification

As of 2026-11-25T09:08:32. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-24 | 2026-11-24 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-20 | 2026-11-20 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-20 | 2026-11-20 | yes | 5227/5228 | 5226 (99.98%) |
| astock_daily | 2026-11-24 | 2026-11-24 | yes | 5221/5221 | 3777 (72.34%) |
| ah_panel | 2026-11-24 | 2026-11-24 | yes | 187/187 | 184 (98.40%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **repo**: carried from `2026-11-22T13:57:28` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-21T02:32:03` (5227/5228 files unchanged)
- **astock_daily**: carried from `2026-11-25T09:03:28` (5221/5221 files unchanged)
- **ah_panel**: carried from `2026-11-25T09:04:21` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5228): 002731.csv
- **astock_daily** (1444 of 5221): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv, 000036.csv …
- **ah_panel** (3 of 187): 01812.csv, 02249.csv, 02493.csv
