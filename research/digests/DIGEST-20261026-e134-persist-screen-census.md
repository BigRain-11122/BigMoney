# E134 — the persistence verdict at census scale is not a weaker screen, it *is* the full screen (and the integer gate is the one that under-repairs)

2026-10-26 — bm-c r1283 — tool `scripts/panel_screen.py` (selftest 31/31) +
`python scripts\e39_panel_census.py screenspread` (census selftest 257/257) —
evidence `results/e42_spread_size_neutral/NEUTRAL-20261023-screened.json`

## The open question this closes

E133 (yesterday's book audit) established two things at once: the integer-ratio heuristic
recognises only 47% of the prints past ±35%, and **level persistence** — does the print's
new level survive the next priced closes — caught all 164 of them, zero reverting. That
left an explicit next item: *does the new verdict rule change any published census line?*

It could go either way. If some census-level print reverts, persistence is a **strictly
safer** screen than repairing everything (it refuses the misprints the full arm repairs);
if none does, persistence is **evidence-backed equality** with the full arm, and the
integer gate is the arm that is wrong. Nothing had measured it.

## What was built

`panel_screen.level_persistence(closes, events, bars=5, tol=0.20)` carries E133's rule as a
first-class citizen of the shared loader (median drift of the next 5 priced closes against
the print close; persisted when |drift| ≤ 20%), and `mode="neutralise_persist"` repairs
exactly the prints whose level holds, whatever the implied ratio. The mode sits beside
`neutralise`, `neutralise_int`, `neutralise_gap` and `drop`; every other caller's default
is untouched, and the arm was added to the `screenspread` leg (E81 leg 2) so the size-neutral
spread — the chain's surviving published claim — is read under all three gates.

Selftest grew 26 → 31 legs (a 3.15:1 conversion repaired by persistence and invisible to the
integer test; a reverting print refused *and counted*; an ordinary integer split still
repaired; a print with no window left undecided rather than guessed).

## Result — three gates, one claim

Size-neutral spread (bp/yr, `exclude sh511*`, 1269 names, monthly book, cutoff 2026-10-23):

| gate | 2021_2023 | 2024_now | full | level mean | band | prints repaired |
|---|---|---|---|---|---|---|
| unscreened | 326.4 | 161.5 | 260.6 | 243.9 | 164.9 | 0 |
| `neutralise_int` | 371.6 | 340.2 | 369.2 | 355.9 | 31.4 | 65 prints (65 names) |
| `neutralise` (all adjacent) | 467.3 | 490.0 | 489.5 | 478.6 | 22.7 | 135 prints (129 names) |
| **`neutralise_persist`** | **467.3** | **490.0** | **489.5** | **478.6** | **22.7** | **135 prints (129 names)** |

- **The persistence arm equals the full arm cell for cell.** Not by construction — it
  evaluated all 135 adjacent prints and refused **0 reverting, 0 undecided** in the whole
  universe. So the answer to the open question is: *no published census line moves.* The
  wide arm was right, and E133's verdict rule says so on evidence rather than by assumption.
- **The integer gate is the arm that is wrong**: it drops 70 of the 135 real repairs (52%),
  which costs the published claim **−122.7bp of level (478.6 → 355.9)** and widens the band
  22.7 → 31.4bp. That is the E81 band-blind story in reverse — the conservative branch was
  not protecting anything here, it was under-repairing.
- The gapped branch is untouched (33 gap-adjacent prints kept by every arm; that is E92's
  question, not this one).

## Honesty about the equality

The equality is a **measurement over one panel at one cutoff**, not a theorem: a single
print whose level reverts inside 5 priced closes would separate the arms again. The
selftest pins that refusal explicitly, and `reverting_adjacent` / `undecided_adjacent` are
published in the screen report so a future reading shows the count the moment it stops
being zero. Reading rule: quote the persistence arm *with its refusal count*, never as
"all prints are corporate actions".

## Reproduction

```
python scripts\panel_screen.py                       # selftest 31/31
python scripts\e39_panel_census.py screenspread       # 4 arms, ~35s
```