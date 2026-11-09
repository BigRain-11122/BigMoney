# DIGEST r1629 bm-b — E600: a bar date is a panel vintage, not an identity

**Study**: `scripts/e600_date_face_unique.py` (selftest 26/26, `check`/`verify` problems=[])
**Face**: `results/state_tilt/DATEFACEUNIQUE.json` (+`-latest.json`), evidence_cutoff 2026-11-09
**Pool card**: E600 burned (done) — seeded E603
**Chain**: `Tools/s6_chain_bmb.py` leg `date_face_unique` (rc0 9.5s) · smoke leg E600 1/1 PASS, 1/1 red under `--doctor`

## The question

E596 (r1627) proved the *name* join is load-bearing on the 18 faces that state a pricing bar and a
decision bar on different dates. But that argument only bites if a consumer could otherwise join on
the date. So: take every date a face states next to a bar name and count how many distinct faces
state it, and under which roles.

## The one number that decides it

Of 13,648 JSON faces under `results/`+`docs/` (461 unreadable, 6 carry a bar name but state no ISO
date), the bar dates collapse into **113 distinct dates** — and **82 of those 113 are stated by more
than one face**:

| class | dates |
|---|---|
| picks out one face | 31 |
| picks out several faces, all under one role | 47 |
| picks out several faces under several roles | 35 |

**The busiest date is 2026-09-22, stated by 6,148 faces** (6,147 of them as `evidence_cutoff`, one
as `as_of`). Next: 2026-09-30 by 354, 2026-10-20 by 166, 2026-11-06 by 161 (and that one is the only
date where all four roles — `as_of` 22 / `decision` 1 / `evidence_cutoff` 147 / `pricing` 8 — meet).

Verdict on the face:
`some_date_is_stated_by_more_than_one_face_so_a_date_keyed_lookup_returns_a_set_and_the_name_join_is_still_required`

The reading that matters: a bar date is a **panel vintage**, not an identity. Six thousand faces
share `2026-09-22` because they were all cut from the same panel, not because they are the same
face. So a date-keyed lookup is not merely ambiguous — it is a lookup over a vintage, and the name
join is the only thing that says *which* face and *which* bar a consumer means. The 31 single-face
dates are almost all `fund_pit_factor_panel.json` month-ends (2011-12-31 …), i.e. dates that are
unique only because one big panel is the only thing in the repo that states them.

## What the instrument refuses

The guard re-derives the three class counts from the published `date_index` (one number per date)
plus the role-bearing rows, so a date index and a row cannot drift apart silently; it also refuses a
row whose `sample_paths` does not match its own `face_count`, a no-date list that disagrees with its
count, and a verdict the counts do not force. `--doctor` strips one face from a row and the smoke leg
goes red on "date row 2026-09-22 states 6147 faces but the index says 6148".

## Provenance chain

- `scripts/e600_date_face_unique.py` — reuses E596's `walk_face`/`date_of`/`KEY_ROLES`, so this study
  cannot grade a spelling the E594 dialect face does not grade.
- `scripts/run_e600_smoke_leg.py` — PASS 1/1; `--doctor` 1/1 red.
- `smoke_test.py` leg E600 (inserted after the E596 block).
- Sibling studies: E594 (dialect join), E595 (alias blast radius), E596 (value vs name join),
  E598 (pointer bar demand), E599 (redirect-target bar), E600 (this), E603 (seeded: does any reader
  join on a date in the first place?).