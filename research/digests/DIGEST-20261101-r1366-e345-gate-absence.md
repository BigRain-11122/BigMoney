# DIGEST 2026-11-01 · r1366 bm-b · E345 — how long a gate was absent, and what stayed green

Source face: `results/state_tilt/GATEABSENCE-2026-11-01.json` (+ `gateabsence_latest.json`)
Runner: `scripts/e345_gate_absence_windows.py` (selftest 22/22, verify 0 problems)
Input: `results/state_tilt/REPAIRRECORD-2026-11-01.json` (E342's three `kind=removed` events)

## What was asked

E342 showed that three deleted smoke checks came back with the same
`(name, condition)`. That measures the restore. The window in between is what a diff
cannot answer, so this face asks it in four parts: how long the gate was gone, whether
another check covered the same property while it was gone, whether the suite even ran
in those rounds, and one verdict per window.

## What was measured

Two names, three removal sites (one name was deleted twice: the assertion and its
`except` fallback), all removed by **one** commit — `9f8010c78` (round 1227,
2026-10-29T00:19:50+08:00).

| | |
|---|---|
| restore commit | `b768f2176` — *merge origin/main into bm-b: union the lane legs* (round 1243, 09:35:11) |
| wall clock | **9.26 hours** |
| commits | **29** on the mainline, **67** reachable |
| rounds inside | **10** (1228, 1229, 1230, 1232, 1233, 1234, 1235, 1236, 1237, 1239) |
| smoke runs inside | **37**, in **10 of 10** rounds (share 1.0) |
| those runs' outcome | 2 of 37 had a non-zero fail count; pass counts 122..128 |
| surviving checks on the same face | **none**, for either name |
| verdict | `nothing` ×2 |

The suite was not idle: it ran at least once in every round of the window. What it was
running was 122–128 checks, and not one of them touched the futures-TSMOM face — both
checks on that face had been deleted together, so there was no sibling left to cover
the property. The value the deleted check compared was not published by this line
either: the face (`results/futures_tsmom_signal.json`) is not in the tree at the window
tip, because its producer came in through the same union merge that restored the gates.
So during 9.26 hours and 10 rounds the machine was green about a face it did not hold
and did not check.

## Three things this catches that the earlier readings did not

1. **A restore can be a merge, and a merge has no textual diff of its own.** `git log -S`
   reports exactly two commits for these labels: the add (r1136) and the removal
   (r1227). The restoration is the r1243 union merge, which pickaxe cannot see. Walking
   `--full-history` in date order does not fix it either — the other host's commits on
   this line carry author dates *before* the removal, so "the first commit that has the
   label again" resolved to `dca8c2b0d`, a foreign commit authored **48 minutes before**
   the deletion (`wall_hours: -0.8`). The only walk that answers the question is
   **`--first-parent`**, i.e. this machine's own line.
2. **Reading the cover at the restore commit makes every window trivially covered.**
   At the restore commit the sibling checks are back by definition. The state during the
   window is the **window tip** (`restore^1`), and at that commit the count of surviving
   checks on the face is zero. Verify now refuses a face whose gate is present at its own
   window tip.
3. **A face carrying the value is not a check asserting it.** This is the E344/E204
   family at a new site. `parse_claim()` reads the three clauses the deleted check
   compared (`actionable is False`, `shadow is True`, `book.gross <= 3.0`) off the face
   JSON. That value is published as `self_report_*` and the verdict stays `nothing`;
   promoting it to `covered_by_a_published_face` would need a producer **other than the
   writer** to publish the property as a claim, and none does.

## Rule for the next card of this family

"Removed then restored" is an event on **one line of history**. Ask it of the
first-parent walk, close the window at the restore's first parent, and classify coverage
only from what the tree held then. And ask whether the suite ran at all before asking
whether anything covered the property: an unrun suite is an unmeasured window, not a
measurable absence — the vocabulary already has the word for it.

Gate: `nothing` on both windows is the answer, and the label matters — "covered" was the
reading available from the wrong commit.