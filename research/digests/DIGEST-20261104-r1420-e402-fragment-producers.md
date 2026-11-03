# DIGEST r1420 (bm-b) -- E402: the 52 "bare basename fragments" are mostly fixtures, and 2 joins can never land

**Face:** `results/state_tilt/FRAGMENTPRODUCERS-2026-11-04.json` (+ `fragmentproducers_latest.json`)
**Script:** `scripts/e402_fragment_producers.py` (run / verify problems=[] / selftest 19/19)
**Card:** `knowledge/METHODOLOGY_ASSETS.md` E402
**Seeded by:** pool card `E402-WHICH-SITES-COMPOSE-A-BASENAME-FRAGMENT-AND-CAN-THE-JOIN-EVER-RESOLVE`

## The question

E399 published 52 of 884 keys (5.9%) as `bare_basename_whose_directory_is_a_runtime_variable` and
described them as "a fragment whose directory is supplied by a runtime variable at the one site that
writes it". That sentence is an inference, not a reading: it asserts a producer exists. This study
prices the producer side -- for each fragment, the sites that carry it as an exact string constant,
whether the site writes or reads, the directory expression it is joined onto, and whether the
composed path exists right now.

## Why the match has to be exact

Substring matching is wrong here. `_judge.json` occurs inside `w13_judge.json` at thirteen sites that
have nothing to do with the key, and `census.json` inside `multicore_census.json`. The arm matches
`ast.Constant` values equal to the fragment, nothing else.

## Result -- 100 producer sites over 52 fragments

| class | sites | fragments (primary) |
|---|---|---|
| C4 temporary directory, deleted by design | **67** | **27** |
| C7 directory expression not traceable statically | 16 | 6 |
| C2 constant directory that does not hold the file | 7 | **2** |
| C3 cwd-relative, no directory supplied | 7 | 6 |
| C8 not a whole filename at all | 3 | **3** |
| C1 constant directory that holds the file | **0** | **0** |
| C5 runtime value (parameter / env temp) | 0 | 0 |

Site kinds: 19 write sites, 14 read sites, 67 untagged; 11 fragments have a write site, 32 are
classifiable only from an untagged site, 9 have read sites only, 8 appear nowhere in the corpus.

## The two joins that can never land

| fragment | site | expression | composed |
|---|---|---|---|
| `_r789bmc_adopt_facts.json` | `Tools/_r789bmc_adopt.py:91` | `os.path.join(REPO, "results", ...)` | `K:\Fluxgroup\FluxGroup\quant\bigmoney\results\...` -- `REPO` is a hard-coded `K:` literal and `K:` is absent on this machine |
| `idle_trigger.bm-c.json` | `Tools/_r731bmc_s3probe.py:50` | `os.path.join(ROOT, "results", ...)` | `results/idle_trigger.bm-c.json` -- not in this tree, and no file with that basename exists anywhere |

Both are one-off scripts, which is the honest scope of the finding: the dead-join class is real but
small, and neither is production tooling.

## The three that are not filenames

`-sender.json` at `Tools/_r421bmc_mf_assist.py:264` (`f"{TICKET}-sender.json"`), `_paper.json` at
`scripts/t35_paper_export.py:312` (`f"{tid}_paper.json"`) and `_x1.json` at
`scripts/regime_matrix_p0.py:459` (`c + "_x1.json"`) are *pieces* of a name built by formatting or
concatenation -- two of them at write sites, so the real files carry a prefix the key does not.
E399's form test (no slash + known extension) read the piece as a bare basename, so "resolves to no
file" is a category error for them, not an absence. C8 names that.

## What the study refuses to claim

- It does not claim the fragments are attrition. Zero compose to an existing path, 27 are temp-dir
  fixtures, 3 are not filenames -- the residual is scaffolding.
- It does not fold "untraceable" into "absent": 6 fragments have a directory expression this tracer
  cannot follow (module constants imported from the excluded `Money02` tree, `PATHS.root`,
  `os.environ`-keyed values), and C7 is published as the instrument's own limit.
- It does not treat a read site as a producer: `classified_from` is published per fragment
  (11 write_site / 32 untagged_site / 1 read_site_only / 8 nothing).

## Measured side effect on a neighbour face

Publishing `fragmentproducers_latest.json` added one family-named pointer to E398's population, so
`named_pointers` moved 175 -> 176 and the E398 leg failed. The face was **re-derived from the live
build** (`e398 run` + `verify problems=[]`) rather than the leg being loosened; E398's read-site
count (187) and bare-pointer count (28) did not move.

## Wiring

- S6 leg `fragment_producers` -> `python scripts/e402_fragment_producers.py verify` (rc 0, 20.8 s).
- smoke leg E402 (extracted verbatim by `scripts/run_e402_smoke_leg.py`, 1/1 PASS): refuses a class
  outside the frozen set, a class table that does not sum to the producer total, a per-fragment table
  that does not add up, a dead-join headline that is not the length of its own list, a landing
  claimed for a class that has none, and a study whose own verify is not clean.
- The full ~330-leg suite and the full S6 chain were **not** re-run this window; the new legs were
  exercised standalone and the study's own verify is clean.