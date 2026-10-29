# E221 — five census modes existed in the dispatch chain and in none of the CLI (r1338 bm-c)

**Card:** E221 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `scripts/e39_panel_census.py` — two new selftest legs, five names restored to the
argparse `choices=[...]` list, selftest 743 (rc 0, no FAIL line).
**Evidence:** `results/_r1337bmc_s6_chain.json` — the three previously red legs now rc=0.

## What was wrong

The S6 chain ran 81 legs on the 11:44 window and three of them came back `rc=2` with an **empty
tail** in 0.4s:

| leg | rc | elapsed | tail |
|---|---|---|---|
| `ladderdropcarrier` | 2 | 0.4s | "" |
| `reviewwindowcross` | 2 | 0.4s | "" |
| `reviewwindowfloor` | 2 | 0.4s | "" |

A fast rc=2 with no output reads like "the leg ran and the upstream was missing", which is a
supported state in this chain. It was not: the failure was `argparse` refusing the mode name
(`invalid choice: 'reviewwindowfloor'`) and writing it to **stderr**, which the chain does not
fold into the tail. Because the legs never ran, the three published faces kept the numbers from
the round that created them — and a face that is never re-derived is indistinguishable from a
face that is stable.

Root cause: the dispatch chain grew five branches (`tilt3ladderdropfragility`,
`tilt3ladderdropcarrier`, `reviewwindowcross`, `reviewwindowfloor`, `widechurntie`) that were
never added to the hand-maintained `choices=[...]` list. The selftest stayed green throughout
because it calls the `run_*()` functions directly and never goes through the CLI — so the suite
was testing the mode bodies and not the mode *surface*.

## What the fix is

One table, checked. Every `args.mode == "x"` branch in `main` must appear in the argparse
`choices=[...]` slice, and the slice must carry no duplicate names. Both legs read `main`'s own
source, so the gate cannot go stale the way the list did.

The slice starts at `choices=[`, not at `ap.add_argument("mode"` — the latter also matches
`default="all"` and manufactured a duplicate on the first attempt at writing this gate.

## Falsification

Deleting one name from the list makes the leg print
`every dispatched mode is accepted by the CLI (unreachable: ['widechurntie'])` and the suite exit
1. Restoring it returns rc 0 with no FAIL. The three legs were then re-run through the chain
runner itself (`Tools/s6_chain_bmc.py --only=...`): rc=0 in 1.1s / 3.8s / 5.6s, reproducing the
stored numbers exactly — perm_p 0.00225 / 0.00475 / 0.031, pooled 0.1885 (ratio 1.1477), floor
1.4803 at 80% power. Revival is measured, not asserted.