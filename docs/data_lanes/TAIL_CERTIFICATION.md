# Panel tail certification

As of 2026-11-07T13:47:58. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Verdict: **sample_understated** — 4 panel(s), 10465 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-06 | 2026-11-06 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-06 | 2026-11-06 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-10-19 | 2026-10-13 | **no** (sample_understated) | 5222/5222 | 2 (0.04%) |
| astock_daily | 2026-11-06 | 2026-11-06 | yes | 5222/5222 | 4783 (91.59%) |

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **moneyflow**: `2026-10-19` is held by 2 of 5222 symbols (0.04%); 5220 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **moneyflow** (5220 of 5222): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000016.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv …
- **astock_daily** (439 of 5222): 000831.csv, 002129.csv, 002623.csv, 002717.csv, 688121.csv, 688209.csv, 688210.csv, 688211.csv, 688212.csv, 688213.csv, 688215.csv, 688216.csv, 688217.csv, 688218.csv, 688219.csv, 688220.csv, 688221.csv, 688222.csv, 688223.csv, 688225.csv, 688226.csv, 688227.csv, 688228.csv, 688229.csv, 688230.csv …
