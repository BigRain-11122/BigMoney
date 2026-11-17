# Panel tail certification

As of 2026-11-18T02:33:38. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-a**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **sample_understated** — 5 panel(s), 10651 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-17 | 2026-11-17 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-17 | 2026-11-17 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-10-19 | 2026-10-13 | **no** (sample_understated) | 5222/5222 | 2 (0.04%) |
| astock_daily | 2026-11-17 | 2026-11-17 | yes | 5222/5222 | 5175 (99.10%) |
| ah_panel | 2026-10-16 | 2026-10-16 | yes | 186/186 | 186 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-17T21:37:21` (10/10 files unchanged)
- **repo**: carried from `2026-11-17T21:37:21` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-17T19:54:28` (5222/5222 files unchanged)
- **ah_panel**: carried from `2026-11-17T19:54:34` (186/186 files unchanged)

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **moneyflow**: `2026-10-19` is held by 2 of 5222 symbols (0.04%); 5220 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (5220 of 5222): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000016.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv …
- **astock_daily** (47 of 5222): 000635.csv, 002717.csv, 002731.csv, 600185.csv, 600919.csv, 603040.csv, 605255.csv, 688121.csv, 688496.csv, 688777.csv, 688778.csv, 688779.csv, 688781.csv, 688783.csv, 688785.csv, 688786.csv, 688787.csv, 688788.csv, 688789.csv, 688790.csv, 688793.csv, 688795.csv, 688796.csv, 688797.csv, 688798.csv …
