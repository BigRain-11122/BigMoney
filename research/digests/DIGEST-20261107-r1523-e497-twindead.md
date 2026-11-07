# DIGEST 2026-11-07 r1523 bm-b -- E497: the one "write-only" twin is read by three S6 producers

**Card**: E497-IS-THE-ONE-WRITE-ONLY-TWIN-S-RETIREMENT-FREE-BECAUSE-ITS-DATED-MEMBERS-ARE-WHAT-GETS-READ
**From**: E496 (r1522) classed `results/market_clock/CALL_latest.json` as
`never_opened_by_any_site_in_the_corpus` -- 7 write sites, 0 reads -- and priced its retirement as
free.
**To**: the whole CALL family, measured across three opener arms.

## What was measured

| arm | what it sees | result on the twin |
|---|---|---|
| A literal at an opener | `open("results/market_clock/call_latest.json")` | 0 reads, 7 writes (agrees with E496 exactly) |
| B path handed to a helper | `_read_json(CLOCK_JSON)` where the helper does `open(path)` | **3 reads** |
| C lane face key to `config/lane_io` | `write_lane("market_clock/call_latest", ...)` composes `<face>.<machine>.json` | 3 machine twins, 1 write each, 0 reads |

## Reading

- Twin `results/market_clock/call_latest.json`: 3 helper readers, all S6 chain producers --
  `scripts/ceo_live_usage.py:400`, `scripts/daily_report.py:91`,
  `scripts/system_v1_paper.py:681`. Retirement breaks 3 sites. `ceo_live_usage` raises a
  `RuntimeError` when the face is absent, so this is not a soft dependency.
- 16 dated `CALL-<asof>.md` members, 30,743 B: read by **no** site (0 literal, 0 helper). Their
  writer is one composed f-string (`market_clock_call.py:403`), plus one literal write in a
  one-off round script (`results/_r392_resolve6.py:97` writes `CALL-2026-09-28.md`).
- 3 per-machine lanes: written by `lane_io.write_lane`, and nothing calls `mirror_shared*` with
  this key, so the lane snapshot is written every run and never unioned back or read.

So the family answers the card's question in the opposite direction to the twin: what nobody reads
is the dated members, not the twin.

## Why the parent is not wrong

The direct arm reproduces E496's zero exactly (`direct_arm_agrees_with_the_parent=true`); the
disagreement lives entirely in arm B. A literal census can only see a reader that spells the file
name at the opener, and all three readers hand a module constant to a helper instead.

## Reusable

1. "Nobody reads it" has to name the arm. `_read_json(<path constant>)` is the cheapest way to
   read a face and the one arm a literal census structurally cannot see.
2. A twin's answer is not the family's. The parent published `members: 16` as a count; the 16 dated
   members were never measured, and they carry the opposite verdict.
3. A run-time composed write (`f"CALL-{asof}.md"`) proves the family has a writer and cannot say
   which member it wrote. Publish the spelling and the site; do not duplicate it across members.

## Pitfalls hit in this window

- **Quadratic mode resolution**: calling `e483.mode_of_site()` per site keeps a full-source
  `ast.walk` per node; over 12,338 sources the run produced no output for five minutes and was
  killed. Resolve the mode from the call node already in hand and pin equivalence to the shared
  implementation with a three-line selftest fixture.
- **`json.load(fh)` is not a path opener**: counting it as one made the helper arm report two
  openers where the file has one, and the first selftest went red on it. Only an opener whose
  first argument is the helper's parameter carries the member.
- **The composed-write arm needs two conditions**: requiring only "a literal ending in .md" put
  1,900 unrelated round-report writers into the family's write arm. Requiring the family prefix
  *and* the family directory in the same call leaves exactly one site.

## Artefacts

- `scripts/e497_twindead.py` -- run rc0 / check problems=[] / verify problems=[] / selftest 26/26
- `results/state_tilt/TWINDEAD-2026-11-07.json` + `twindead_latest.json` (20 rows)
- `scripts/run_e497_smoke_leg.py` -- 1/1 green, 1/1 red under `--doctor` (face sha restored)
- `smoke_test.py` leg `E497 ...`
- `Tools/s6_chain_bmb.py` leg `twin_dead` (rc0 0.07 s)
- `knowledge/METHODOLOGY_ASSETS.md` card E497