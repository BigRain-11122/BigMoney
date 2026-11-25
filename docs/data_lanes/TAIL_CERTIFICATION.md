# Panel tail certification

As of 2026-11-25T20:12:49. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-25 | 2026-11-25 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-20 | 2026-11-20 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-20 | 2026-11-20 | yes | 5227/5228 | 5226 (99.98%) |
| astock_daily | 2026-11-25 | 2026-11-25 | yes | 5221/5221 | 497 (9.52%) |
| ah_panel | 2026-11-24 | 2026-11-24 | yes | 187/187 | 184 (98.40%) |

## 3 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **repo**: carried from `2026-11-22T13:57:28` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-21T02:32:03` (5227/5228 files unchanged)
- **ah_panel**: carried from `2026-11-25T09:04:21` (187/187 files unchanged)

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **astock_daily**: `2026-11-25` is held by 497 of 5221 symbols (9.52%); 4724 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5228): 002731.csv
- **astock_daily** (4724 of 5221): 000031.csv, 000820.csv, 000932.csv, 001339.csv, 001356.csv, 001358.csv, 001359.csv, 001360.csv, 001365.csv, 001366.csv, 001367.csv, 001368.csv, 001369.csv, 001373.csv, 001376.csv, 001378.csv, 001379.csv, 001380.csv, 001382.csv, 001386.csv, 001387.csv, 001388.csv, 001389.csv, 001390.csv, 001391.csv …
- **ah_panel** (3 of 187): 01812.csv, 02249.csv, 02493.csv
