# Panel tail certification

As of 2026-11-16T18:05:31. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10655 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-13 | 2026-11-13 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-13 | 2026-11-13 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-16 | 2026-11-16 | yes | 5221/5221 | 378 (7.24%) |
| ah_panel | 2026-11-13 | 2026-11-13 | yes | 187/187 | 187 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-15T21:25:55` (10/10 files unchanged)
- **repo**: carried from `2026-11-14T10:04:40` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-13T21:01:44` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-15T05:41:03` (187/187 files unchanged)

## The newest bar is held by a handful of symbols

A tail that only a few files reach is not a statement about the panel; it is one symbol's last bar quoted as the panel's.

- **astock_daily**: `2026-11-16` is held by 378 of 5221 symbols (7.24%); 4843 sit behind it.

## Symbols whose last bar is behind the panel's newest bar

- **astock_daily** (4843 of 5221): 000635.csv, 000721.csv, 000955.csv, 000957.csv, 000958.csv, 000959.csv, 000960.csv, 000962.csv, 000963.csv, 000965.csv, 000966.csv, 000967.csv, 000968.csv, 000969.csv, 000970.csv, 000972.csv, 000973.csv, 000975.csv, 000977.csv, 000978.csv, 000980.csv, 000981.csv, 000983.csv, 000985.csv, 000987.csv …
