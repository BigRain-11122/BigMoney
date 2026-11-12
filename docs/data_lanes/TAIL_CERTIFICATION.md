# Panel tail certification

As of 2026-11-12T21:19:09. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-a**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **sample_understated** — 5 panel(s), 10651 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-11 | 2026-11-11 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-11 | 2026-11-11 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-10-19 | 2026-10-13 | **no** (sample_understated) | 5222/5222 | 2 (0.04%) |
| astock_daily | 2026-11-10 | 2026-11-10 | yes | 5222/5222 | 4280 (81.96%) |
| ah_panel | 2026-10-16 | 2026-10-16 | yes | 186/186 | 186 (100.00%) |

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **moneyflow**: `2026-10-19` is held by 2 of 5222 symbols (0.04%); 5220 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **moneyflow** (5220 of 5222): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000016.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv …
- **astock_daily** (942 of 5222): 000831.csv, 002129.csv, 002717.csv, 603615.csv, 603616.csv, 603617.csv, 603618.csv, 603619.csv, 603626.csv, 603628.csv, 603629.csv, 603630.csv, 603633.csv, 603636.csv, 603637.csv, 603638.csv, 603639.csv, 603648.csv, 603650.csv, 603655.csv, 603656.csv, 603657.csv, 603658.csv, 603659.csv, 603660.csv …
