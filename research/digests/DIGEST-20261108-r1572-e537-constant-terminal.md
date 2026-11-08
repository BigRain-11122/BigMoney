# DIGEST 2026-11-08 r1572 bm-b — E537: what the constant that replaced the sentinel actually names

**Card.** `E537-WHICH-SENTINEL-REPLACED-BY-A-MODULE-CONSTANT-ONE-HOP-OUT-LANDS-ON-A-TERMINAL-THAT-IS-NOT-THE-CALLEE-S-OWN-ROOT`
(seeded by r1571's supply floor from E532).

**Face.** `results/state_tilt/CONSTTERM-2026-11-08.json` (94 KB) + `constantterminal_latest.json`.
**Tool.** `scripts/e537_constant_terminal.py` — `run` / `check` / `verify` / `selftest` (42 legs).
**Wiring.** S6 leg `constant_terminal` (rc0 0.05s, receipt `results/_r1572bmb_s6_chain.json`), smoke leg
`# E537` (standalone runner `scripts/run_e537_smoke_leg.py` 1/1 green, `--doctor` 1/1 red).

## Verdict

```
the_arms_terminal_on_one_directory_and_that_name_reaches_one_directory_across_the_tree
```

Both arms E532 published as rescued by a module constant do read the same directory — the repo root —
and their published chains are exactly what the tree reads (2 of 2, link for link).

## Readings

| question | answer |
|---|---|
| arms rescued by a module constant | 2 (`e328_quoted_number_staleness::verify(root)`, `e489_write_wire::build(root)`) |
| chains | `e328:ROOT → e326.ROOT → e312.ROOT`; `e489:ROOT` |
| terminal expression (both) | `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` |
| terminal directory (both) | `.` (repo root), asserted to exist on disk |
| chains that agree with the tree | 2 / 2 |
| `__file__`-derived module constants in `scripts/` | 899 across 887 modules, 24 distinct names |
| names reaching more than one directory | 1 — `HERE` (220 → `scripts/`, 1 → repo root) |
| names that name a file rather than a directory | 6 names / 35 constants (`SRC` 23, `OUT_PATH` 5, `SELF` 5, `CAL_PATH`, `EW_PATH`, `RESULTS_JSON`) |
| names the whitelist could not fold | 5 (`BARS_DIR`, `OWN_SOURCES`, `SELF_MODULE`, `UNIVERSE`, part of `SELF`) |
| constants bound twice | 1 (`scripts/e495_doctorpub.py:37` then `:38`) |

`ROOT` is 576 constants over four different expressions (546 os.path chains, 28 pathlib `parents[1]`,
1 `join(dirname(__file__), '..')`, 1 module directory) and **one** directory: the repo root.

The single split is deliberate, not stale: `scripts/fund_p2_burn_progress.py:18` defines
`HERE = dirname(dirname(abspath(__file__)))` — the repo root — and then `RES = join(HERE, "results")`.

## The reader defect this round produced and fixed in-window

The first build read each name's **first** module-level binding. On that reading
`scripts/e495_doctorpub.py` publishes `ROOT → scripts/`, i.e. a second directory for a name that has
one, and the verdict was `..._while_the_name_itself_reaches_several_directories_in_this_tree`.

The module's actual shape is the two-line idiom:

```
37: ROOT = os.path.dirname(os.path.abspath(__file__))   # scripts/
38: ROOT = os.path.dirname(ROOT)                        # repo root
39: OUTDIR = os.path.join(ROOT, "results", "state_tilt")
```

So the face now publishes, per row, the binding the module holds (`directory`) **and** the binding a
first-reader would have stopped at (`first_directory`, 1 row), plus `bindings`. The false split is a
published row instead of a published directory, and the gate refuses a first binding reported as the
final one.

## Why this matters beyond the two arms

"The sentinel is replaced by `ROOT`" is a sentence about a name. E532 could not tell whether two arms
that look identically rescued read the same population; the answer required evaluating the name, not
counting it. Here the answer is that they do — but the same method finds `HERE`, where 1 module in 221
means the repo root by that name, and finds one rebinding that a natural reader would turn into a
second population.

## Limits

Whitelist only (`os.path.dirname/abspath/realpath/normpath/join/expanduser`, pathlib
`Path/PurePath` + `.resolve/.absolute/.parent/.parents[n]/.joinpath`, `str`, `+`); anything else is
published as `could_not_be_evaluated` with the reason, never folded. Corpus is `scripts/` only. A
directory is only published when the evaluation exists on disk. Nothing in the repository is executed
and no source is rewritten.

## Next

E544 (item store between binding and site), E545 (E533's three open arms through the E536 resolver),
E546 (the six names that name a file, read as directories) are in the pool.