# Panel tail certification

As of 2026-11-17T19:54:27. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-a**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **sample_understated** — 5 panel(s), 10651 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-16 | 2026-11-16 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-13 | 2026-11-13 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-10-19 | 2026-10-13 | **no** (sample_understated) | 5222/5222 | 2 (0.04%) |
| astock_daily | 2026-11-16 | 2026-11-16 | yes | 5222/5222 | 1556 (29.80%) |
| ah_panel | 2026-10-16 | 2026-10-16 | yes | 186/186 | 186 (100.00%) |

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **moneyflow**: `2026-10-19` is held by 2 of 5222 symbols (0.04%); 5220 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (5220 of 5222): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000016.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv …
- **astock_daily** (3666 of 5222): 000635.csv, 002606.csv, 002717.csv, 002731.csv, 300073.csv, 300074.csv, 300075.csv, 300076.csv, 300077.csv, 300078.csv, 300079.csv, 300080.csv, 300081.csv, 300082.csv, 300083.csv, 300084.csv, 300085.csv, 300086.csv, 300087.csv, 300088.csv, 300091.csv, 300092.csv, 300093.csv, 300094.csv, 300095.csv …
