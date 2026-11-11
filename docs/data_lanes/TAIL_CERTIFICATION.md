# Panel tail certification

As of 2026-11-12T01:10:17. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-11 | 2026-11-11 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-10 | 2026-11-10 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-11 | 2026-11-11 | yes | 5223/5223 | 341 (6.53%) |
| ah_panel | 2026-11-10 | 2026-11-10 | yes | 187/187 | 187 (100.00%) |

## 3 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **repo**: carried from `2026-11-10T20:50:13` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-10T20:50:14` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-10T20:53:28` (187/187 files unchanged)

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **astock_daily**: `2026-11-11` is held by 341 of 5223 symbols (6.53%); 4882 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **astock_daily** (4882 of 5223): 000831.csv, 000900.csv, 000901.csv, 000902.csv, 000903.csv, 000905.csv, 000906.csv, 000908.csv, 000909.csv, 000910.csv, 000911.csv, 000912.csv, 000913.csv, 000915.csv, 000917.csv, 000919.csv, 000920.csv, 000921.csv, 000922.csv, 000923.csv, 000925.csv, 000926.csv, 000927.csv, 000928.csv, 000929.csv …
