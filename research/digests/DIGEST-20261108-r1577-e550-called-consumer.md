# DIGEST 2026-11-08 r1577 bm-b -- E550: the seventeen handed-on sites, followed one hop into the callee

**Study**: `scripts/e550_called_consumer.py` (card E550) · **Face**: `results/state_tilt/CALLEDCONSUMER-2026-11-08.json` (+ `calledconsumer_latest.json`) · **Pool card**: E550 -> done.

## What the card asked

E546 (r1575) published 49 direct sites over 35 file-naming constants: 32 read the constant as a file, 0 as a
container, and **17 hand it to a callee the site scan does not follow**. E549 (r1576) read four *other* rows
out of their enclosing functions; these 17 were never opened at all. The card asks for each of them one hop
into the callee it names (same module first, then an in-repo module), publishing whether that callee opens the
parameter, joins it as a container, only tests or compares it, or passes it further -- plus how many are
containers one hop out (the failure mode, one layer down) and how many are dead ends the caller builds and
never reads.

## What it found

17 parent sites fold into **15 distinct source locations**: two lines were recorded by the parent as two
spellings of one call (the call node and its argument, `scan_site(NAME)` + `NAME` at `e390:816`, and
`os.path.abspath(NAME)` + `NAME` at `e390:818`).

| one hop out | locations | what it means |
|---|---|---|
| opened | 2 | `e390.scan_site` opens its first parameter (412); `marks_coverage.load_calendar(path=CAL_PATH)` probes (153) then opens (156) |
| container base | **0** | the E546 failure mode does not materialise one layer down |
| builtin render | 6 | every `print("wrote", OUT_PATH, ...)` in the six `etf_phase_*` scripts -- the constant is printed, never read |
| identity token | 7 | `os.path.abspath(p) == SELF` family over `e390` (3 locations), `e391` (2), `e392` (1), `e446` (1) |
| not settled | 0 | |

Verdict: `no_site_that_hands_the_constant_on_reads_it_as_a_container_one_hop_out`.

## The four laws this round adds

1. **Ask whether the parent's "site count" is a location count.** One call is two parent spellings (the call
   node and its argument), so "read 17 sites" is a double count unless rows carry `parent_site_count` and the
   face publishes 17 parent sites beside 15 distinct locations.
2. **The failure mode must outrank the benign arm at aggregation.** A callee that both joins and opens the
   same parameter would hide the defect if `open` won; the container arm wins, and both uses stay on the row
   so the priority is a judgement while the evidence is complete.
3. **A builtin is a callee, and it is the most common one here.** `print` never reads a path, yet it catches
   six of the seventeen loads. Without a `renders_only` class those sites would silently count as "followed
   into a function" and read as if somebody consumed the value.
4. **A clean verdict must prove it looked.** The verdict is recomputed from rows; the smoke leg additionally
   refuses a no-container verdict that sits beside no followed callee at all or no builtin renderer at all,
   so a scan that followed nothing cannot produce the clean word.

## Defects caught before the gate

- `_param_for_position` carried a leftover `args[0].arg if False else args[pos].arg`; simplified to
  `args[pos].arg`.
- `loads_analysed` was read off the *hop* dict, where the count never lived -- the row now carries
  `loads_at_this_line` from the site itself, and the summary re-derives from the rows.
- The default-argument arm set `rows_whose_value_is_a_default_argument` twice (a placeholder sum plus an
  overwrite); the placeholder was removed so the key has exactly one derivation.

## Gates

`selftest 23/23` · `check` `problems=[]` (re-derives every site class and the verdict from the sources now) ·
`verify` two builds identical · smoke leg `# E550` standalone `PASS`, `--doctor` `FAIL` (a hand-written
verdict is refused) · S6 leg `called_consumer rc=0` (0.23s).

## Limits published with the face

Exactly one hop: a parameter handed on again is published as forwarded, not followed. The repository fallback
indexes `def <name>(` in `scripts/*.py` only, so a miss is "not found by this scan", not "absent". The
container class wins when a callee both joins and opens. No execution: "opened" means a load reaches
`open()`, not that the file exists.

## Next

The six render sites are one idiom: `print("wrote", OUT_PATH, ...)`. The natural next question is whether
anything in the repo parses that line back -- if no reader keys on it, the message is a human convenience and
the constant's only machine use is the `open()` that precedes it. E551 seeded; E547 and E548 stay ready.