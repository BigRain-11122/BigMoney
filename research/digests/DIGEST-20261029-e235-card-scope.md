# E235 — the card tripwire read one heading level, and a number-keyed loss check cannot see a collided card (r1344 bm-c)

**Card:** E235 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `Tools/card_ledger_guard.py` (reader widened, 3 new selftest legs, `cards_by_level` in the payload),
`smoke_test.py` (one scope leg).
**Faces:** `results/_r1344bmc_card_scope.json`, this digest.

## Why this round exists

The window opened with the merge from bm-b r1253 unfinished. Resolving
`knowledge/METHODOLOGY_ASSETS.md` by union meant reading both sides' card headings, and the two
machines number their cards differently: bm-c writes `## E232`, bm-b writes `### E221`. The
ledger's own tripwire (`Tools/card_ledger_guard.py`, E232, built last night precisely because a
stale-copy publish had eaten every card but two) reads `^## E(\d{3})\b`.

So the guard that exists to notice a vanished card could not see 6 of the 158 cards it was
guarding — and reported `head=152 tree=152 lost=[]`, which reads as a balanced file, not as a
blind spot.

## What was measured

Two readers applied to the same blob (`results/_r1344bmc_card_scope.json`):

| reader | cards visible |
|---|---|
| `^## E(\d{3})\b` (before) | 152 |
| `^#{2,3} E(\d{3})\b` (after) | 158 |

The six invisible cards are `E221, E222, E223, E224, E231, E234` — every card bm-b has filed at
level 3. Four of them (`E221-E224`) share their number with a `##` card this machine filed about
different work, which produces a second, sharper defect: **the loss check compares numbers**
(`set(head_cards) - set(tree_cards)`), so for those four a disappearance moves no number and the
tripwire cannot fire no matter how wide the reader is. Only `E231` and `E234` had numbers that
existed at level 3 alone.

Ledger-level census taken at the same time: 158 cards over **129 distinct numbers** — 27 numbers
carry more than one card (29 excess cards), with triples at 103 and 190. The pre-existing 23 were
inherited history; `221-224` are new (they became visible only with this widening).

## What was changed

1. The reader is level-agnostic (`^#{2,3}`), and the payload publishes `cards_by_level` so a
   future scope change is legible in the output instead of inferred from a total that "looks
   right".
2. Selftest 7 -> 10 legs, each driving the failing case rather than the fixed one: a dropped
   `###` card must be `ACTIVE_LOSS`; both levels must be counted; a level-1 heading, a plain
   `### Notes` heading and a 4-digit number must not be read as cards.
3. One smoke leg that **re-derives** the card count by hand from the ledger bytes and requires the
   guard to agree. It is deliberately not "call the guard and trust its own regex" — a leg that
   asks the reader to check itself would have passed through the whole defect. (The first version
   of that leg did use `CARD.findall` on the whole text and returned 0 cards, because the compiled
   regex has no `re.MULTILINE`; a vacuous count of 0 is exactly the r1261 trap, so the leg scans
   lines instead.)

## What was deliberately not repaired

`bm-b E221-E224` still collide with `bm-c E221-E224`. Renumbering another machine's recorded cards
rewrites its record, so the collision is **published** (named numbers in the warning and in the
face) rather than fixed. The one card with no counterpart on this side — bm-b's `E227` — was
renumbered **E234** on merge, with the reason in its own heading, following the E225->E231
precedent from r1343.

## Merge notes (absorbed, not re-typed)

- 17 conflicting faces. Fourteen are generated: local side kept and re-derived by the chain (a face
  that describes a book is produced, not merged — r1290).
- `results/runnable_pool.json`: origin is a strict superset (699 vs 698 entries, and this machine's
  `E226-TILT-BREAKEVEN-COST` still read `ready` while origin has it `done` with a `result_ref`), so
  origin was taken whole — the local copy was stale, not divergent.
- `knowledge/METHODOLOGY_ASSETS.md`: union, bm-b's card kept verbatim except for the renumber.
- `smoke_test.py`: union of two independent legs (r1343's marker-fragment leg and bm-b r1253's
  break-even-toll leg), verified by `ast.parse` before staging.

## Honest note

The first splice of the ledger during the merge was wrong — an offset-based edit dropped both new
cards and reintroduced three marker lines, and the mistake was caught by the guard itself going
`ACTIVE_LOSS lost=[232, 233]` two seconds later. The repair was to restore HEAD's blob from git and
append only the incoming card block, not to patch the damaged file.