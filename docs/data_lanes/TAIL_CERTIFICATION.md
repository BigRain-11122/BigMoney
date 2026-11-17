# Panel tail certification

As of 2026-11-17T17:28:18. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10656 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-16 | 2026-11-16 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-13 | 2026-11-13 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-17 | 2026-11-17 | yes | 5226/5227 | 5225 (99.98%) |
| astock_daily | 2026-11-17 | 2026-11-17 | yes | 5221/5221 | 519 (9.94%) |
| ah_panel | 2026-11-16 | 2026-11-16 | yes | 187/187 | 186 (99.47%) |

## 3 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-16T23:25:06` (10/10 files unchanged)
- **repo**: carried from `2026-11-16T23:25:06` (11/11 files unchanged)
- **ah_panel**: carried from `2026-11-16T23:27:51` (187/187 files unchanged)

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **astock_daily**: `2026-11-17` is held by 519 of 5221 symbols (9.94%); 4702 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5227): 002731.csv
- **astock_daily** (4702 of 5221): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv, 000036.csv …
- **ah_panel** (1 of 187): 01812.csv
