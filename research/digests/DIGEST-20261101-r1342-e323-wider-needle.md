# DIGEST -- E323: the wider needle moves the population and names nothing new

Round r1342 (bm-b), 2026-11-01. Face: `results/state_tilt/REACHWIDE-2026-10-31.json`.
Code: `scripts/e323_reach_under_wider_needle.py` (selftest 18/18, verify problems=[]).

## Question

E321 published "21 of 196 unresolved-or-ambiguous gate leaves (10.7 pct) are named by the constant
that publishes them". E322 then showed the same producer lookup refuses four faces for mechanical
reasons (auditor self-exclusion, compact dates, composed names). A needle that refuses faces also
bounds every row it *did* classify, so that 10.7 pct was a lower bound of unknown tightness. Re-run
the five-class census over the whole population under the wider needle and publish what moves.

## Answer

| | literal needle (E321) | wider needle (E323) | naively accumulated |
|---|---|---|---|
| named | 21 | **21** | 28 |
| no producer at all | 25 | 0 | 0 |
| producer found, publishes no such key | 6 | 6 | 6 |
| bare literal | 5 | 5 | 5 |
| constant that names nothing | 139 | 164 | 157 |

- **25 rows move, all in one direction**: `no_producer_names_the_face` -> `published_as_a_constant_
  that_names_nothing`. Every one of those gates now has a writer, and that writer's constant still
  says nothing about what the tolerance is a share of.
- **0 rows regress** under the attribution rule, and **the named count does not move**.
- The 10.7 pct is therefore not a needle artefact: widening the search relocates the unowned rows
  without naming any of them, and 14.3 pct is what the *unfiltered* rule would print.

## Why the unfiltered rule is wrong (and how it is published)

The naive accumulation reports 28 named rows. All 7 extras are cross-script credit:

- `etf_book_bakeoff.json` composes to the prefix `etf_book`, which **106 scripts** contain; any of
  them binding a key called `tolerance_pp` for its own gate gets credited here.
- The same script (`scripts/etf_book_commodity_split.py`) is credited as producer of **seven**
  different book faces, each with a different own writer.

Fix (and the rule this study freezes): narrow steps -- the face's own path, its own filename, its
dated template -- define the producer set whenever they reach anything at all; compact-date and
composed-name steps serve only faces nothing narrow reaches, i.e. exactly the unowned population
E322 measured. `class_naive` is published beside `class_after` and `rejected_name_gains` lists all
seven, so the false-positive volume of the wide rule is a number, not an opinion.

A second defect, caught by a selftest leg after the first burn: `e322.strip_to_needle` basenames on
the way, so the "literal" attempt had become a bare filename. Seeking a face is a path operation;
stripping a name is not.

## Evidence

```
python scripts/e323_reach_under_wider_needle.py run       # 196 rows, 51 faces, 2279 corpus files
python scripts/e323_reach_under_wider_needle.py selftest  # 18/18
python scripts/e323_reach_under_wider_needle.py verify    # problems=[]
python Tools/s6_chain_bmb.py run --only reach_under_wider_needle   # rc=0
python _e323_runleg.py (smoke leg body executed standalone)        # PASS
```

## How to apply

- Before publishing "X of N are unexplained/unowned/unnamed", re-run that census with the *widest*
  needle you can defend and publish both numbers. If the share does not move, the claim is a fact
  about the repository; if it moves, the narrower number was a needle artefact.
- When a census widens a lookup, it must state an attribution rule, not just a needle: a name
  prefix proves family membership, never ownership.
- Publish the naive figure beside the attended one. The delta *is* the measurement.