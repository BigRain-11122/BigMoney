"""Append the E472 methodology card (one-shot writer; kept out of the S6 chain)."""
import io

CARD = """

## E472 — a dated family re-emitted every round is only worth what a study reads of it

**Question.** E471 priced individual never-opened pointer targets. The volume question it left is
different: `results/` is full of *families* re-emitted with a new date stamp every round
(`WIDTHLADDER-20261029` .. `WIDTHLADDER-20261106`). How much of the daily face output is vintages
of a family that no study opens, and how many of those families are re-written on every cutoff
rather than written once?

**Answer (cutoff 2026-11-06).** 97 vintage families / 571 files / 28.5 MB, and **none of the 97**
is opened by a study that does not write it — the residue split is 17 families a study *names* but
no opener call uses, 7 that only a smoke/runner leg or a one-off round script opens, and 73 that
nothing outside the producer names at all. 36 of the 97 carry a `_latest` pointer, i.e. the cheap
retrieval channel exists and still nobody reads through it. Emission is not a one-off: the unread
families account for 10-11 faces on each of the last six cutoffs. Single-vintage stems are counted
separately and never scored (624 stems / 675 files), so "re-emitted" is always a claim about at
least two distinct dates.

**Method.** Population is mechanical: every file under `results/` whose basename carries an 8-digit
or ISO date stamp; the family is the stem with the stamp (and trailing tags) removed; a family
qualifies only with >=2 distinct dates on disk. Readers are measured on the `.py` corpus with three
channels per family — `opens` (an opener call whose evidence literals name the token or its
`_latest` pointer, so a path composed as `"results/state_tilt/" + FAMILY + "-" + cutoff + ".json"`
is visible), `names` (token in literals, no opener), `writes` (the producer). Matching is
case-folded and boundary-anchored, so a family whose name is a prefix of another is not merged.

**Pitfalls (two).**
* **A family can emit several vintages on one day, so files != dates.** The row guard first demanded
  `len(dates) == vintages` and failed 20+ legitimate rows (`MIDSWEEP-20261020.json` and
  `MIDSWEEP-20261020-burnin.json` share a date). Correct bound: one member per vintage, no repeated
  dates, `len(dates) <= vintages`, and the date set exactly equal to what the members' basenames
  name. The doctored leg still bites because a truncated date list no longer covers its members.
* **A leg whose detail string is only assigned on the exception path crashes the moment it goes
  green.** The E472 smoke leg defined `_d472` inside `except`; while the leg was red the
  short-circuit `"; ".join(_bad472)[:240] or _d472` hid it, so the NameError only surfaced after the
  face was correct. A red leg is not evidence that the leg can pass.

**Wiring.** `scripts/e472_vintage_read.py` (run rc0 / `check` problems=[] / `verify` identical /
**selftest 18/18**); faces `results/state_tilt/vintageread_latest.json` +
`VINTAGEREAD-2026-11-06.json`; S6 leg `vintage_read`; smoke leg `e472 vintage families are only
counted unread when no study opens them (r1495 bm-b)` proved 1/1 and 1/1 red on an inflated vintage
count, face restored byte-identical; pool E472 closed with result_ref.

**How to apply.** Before adding another dated family to `results/`, ask which study opens it. A
`_latest` pointer is not a reader. And when a residue says "no consumer", check whether the site
composes the path from a module constant one hop away — the honest failure mode of this measurement
is to call a read family unread, so the limit is printed in the face rather than implied.
"""

with io.open("knowledge/METHODOLOGY_ASSETS.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(CARD)
print("appended %d chars" % len(CARD))