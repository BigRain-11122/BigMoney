# Panel tail certification

As of 2026-11-18T16:52:45. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-a**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **sample_understated** — 5 panel(s), 10651 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-18 | 2026-11-18 | yes | 10/10 | 4 (40.00%) |
| repo | 2026-11-18 | 2026-11-18 | yes | 11/11 | 8 (72.73%) |
| moneyflow | 2026-10-19 | 2026-10-13 | **no** (sample_understated) | 5222/5222 | 2 (0.04%) |
| astock_daily | 2026-11-17 | 2026-11-17 | yes | 5222/5222 | 5214 (99.85%) |
| ah_panel | 2026-10-16 | 2026-10-16 | yes | 186/186 | 186 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-18T16:32:20` (10/10 files unchanged)
- **moneyflow**: carried from `2026-11-17T19:54:28` (5222/5222 files unchanged)
- **astock_daily**: carried from `2026-11-18T16:17:29` (5222/5222 files unchanged)
- **ah_panel**: carried from `2026-11-17T19:54:34` (186/186 files unchanged)

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **moneyflow**: `2026-10-19` is held by 2 of 5222 symbols (0.04%); 5220 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **futures** (6 of 10): AU.csv, IC.csv, IH.csv, SC.csv, T.csv, TF.csv
- **repo** (3 of 11): GC001.csv, R-001.csv, R-007.csv
- **moneyflow** (5220 of 5222): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000016.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv …
- **astock_daily** (8 of 5222): 000635.csv, 002717.csv, 002731.csv, 600185.csv, 605255.csv, 688121.csv, 688496.csv, 688798.csv
