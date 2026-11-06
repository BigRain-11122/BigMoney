# DIGEST 2026-11-07 r1505 bm-b — E477: what a vintage retirement actually costs

**Line**: E472 (97 unread vintage families, 571 files, 27.2 MB, no study opens any of them) →
E473 (47 of them have no write-call evidence) → E476 (14 of 47 name a writer, all via a card id,
0 via a script) → **E477: before a publishing policy retires them, are the bytes still the only copy?**

**Measurement**: sha256 of every member file against every `results/` payload (json/jsonl/csv/md,
14,048 files at build time). One class per file:

| class | files | bytes |
|---|---|---|
| repeat of another member of the same family | 0 | 0 |
| exact copy of a `*_latest.json` twin (survives retirement) | 40 | 3,190,685 |
| copy of a file outside the unread membership | 0 | 0 |
| bytes nothing else in `results/` holds | 531 | 25,362,319 |
| **total** | **571** | **28,553,004** |

**Reading**: the unread vintage families are not self-duplicating — not one of the 571 files is a
repeat of a sibling vintage, so every daily emission carries different bytes. Only 11.2% of the
bytes (3.19 MB) are copies of a twin that would survive. **Retiring the 97 families destroys
25.36 MB of content nothing else holds**; it is not the deletion of a duplicate pile.

**Heaviest unique families**: `results/state_tilt/BANDPATH` 7 files / 3.46 MB,
`results/paper/marks/marks` 29 / 1.67 MB, `results/e79/DECOMLEVELQUOTES` 2 / 1.49 MB,
`results/state_tilt/READERTIERS` 3 / 1.28 MB, `results/rev_osc_live/BARS` 19 / 1.13 MB.

**Pit (self-caught in-window)**: the population was built with `os.path.join(ROOT, "results/...")`
(mixed separators) while `os.walk` returns backslashes, so the first build's `p in members` never
matched and 531 files were published as "same bytes as a file outside the unread families" — a
verdict that flipped from "mostly unique" to "everything is reclaimable". Fixed with
`os.path.normpath` on both sides before any set test (E366 family: one population, one address
form); the selftest keeps one population in both spellings so the class can only land one way.

**Wiring**: `scripts/e477_vintage_retire.py` — `run` rc0, `check` problems=0, `verify` rebuild
problems=0, `selftest` green on five class assignments + the empty population + a doctored tally + a
`unique` row that names a partner. Face: `results/state_tilt/VINTAGERETIRE-2026-11-07.json`
(117 KB) + `vintageretire_latest.json`.

**Limits published on the face**: byte identity is a lower bound on redundancy (a payload that
differs only in `generated` reads as unique — that is E478), the corpus is `results/` payload
extensions only, and `bytes_lost_if_retired` counts same-family repeats as lost even when the family
is retired as a whole.

**Next**: E478 (semantic diff vs the family's own twin after removing clock fields), E479 (are the
`*_latest.json` twins themselves opened by a consumer?), E480 (does the payload's date agree with the
date in the file name?). All three are seeded `ready` in `results/runnable_pool.json`.
