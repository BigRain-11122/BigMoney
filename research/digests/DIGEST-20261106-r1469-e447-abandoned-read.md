# DIGEST r1469 bm-b -- E447: an abandoned base is harmless only if nobody reads it either

Card: **E447** (follow-up to E446 / r1463). Face:
`results/state_tilt/abandonedread_latest.json` (`ABANDONEDREAD-2026-11-06.json`).

## Question

E446 split the 51 frozen face-home bases into 28 that have a writer somewhere in the corpus
(dormant) and 23 that have none (abandoned). A base with no writer is correct when it holds the
artifacts of a surgical push and wrong when a reader under it is still launched. E447 asks, for each
of the 23: which read sites resolve into that base, is any of them a live consumer, and what class
does the base therefore carry.

## Method

The mirror of E446's write scan, reusing its resolver verbatim (import, never re-implemented) so both
faces share one path vocabulary:

* a **read site** is a call that takes bytes or a listing FROM a path: `open` in a reading mode,
  `read_text`/`read_bytes`, the pandas loaders (`read_csv`, `read_parquet`, `read_json`, ...),
  `np.loadtxt`/`genfromtxt`, `os.listdir`/`scandir`/`walk`, `glob`/`rglob`, and the source argument
  of `copy`/`copy2`/`copyfile`/`move`;
* **liveness** is read from the harnesses, not guessed from filenames: `smoke_leg` = named in
  `smoke_test.py`, `chain_leg` = named in `Tools/s6_chain_bmb.py`, `task_referenced` = named in a
  `Tools/*.ps1|cmd|bat` wrapper, `face_writing_census` = the module publishes a JSON face under
  `results/`, `runnable_script` = a `__main__` guard and no published face, `library_module` = none
  of those.

## Reading

| class | bases |
|---|---|
| `abandoned_and_unread` | 9 |
| `abandoned_but_still_read` | 11 |
| `abandoned_and_only_a_backup` | 3 |

23 bases, 143 read sites, 133 distinct reader faces (98 of them face-writing censuses, 28 libraries,
4 runnable scripts, 2 task-referenced, 1 smoke leg). Seven bases are read by code a harness launches:

* `results/etf_book_production` -- `smoke_test.py:450` opens `CARD.md`
* `results/etf_book_order` -- `smoke_test.py:699` and `:1606` open `latest.json`
* `results/e79` -- `smoke_test.py:985` opens `DOCQUOTES-BASELINE.json`
* `results/g25` -- `strategy_scorecard.py:1325` lists the directory
* `results/t23_census` -- three `alphagen_beam_w18/19/20.py` runs open `CENSUS-...`
* `results/bond_w3a` -- `bond_panel_puller.py` opens `candidates.json` and `conn_fuse.json`
* `results/overnight_gap_census` -- `trial_labor_w21.py:473` opens a leg file (suffix-only match)

The three backup/rollback directories (`_r1024bma_rollback_side`, `_r753bmc_churn_backup`,
`_r903bmc_ff_backup`) are read by nobody, which is the correct answer for an archival copy.
`results/p2cal_ext` is the opposite extreme: 119 read sites, all in per-round builder scripts that
live inside `results/` themselves, zero of them live today.

The headline is not "the repository is broken". It is that **the smoke suite and two lane hosts read
artifacts no code in the tree would recreate**, so the class of those bases is not "abandoned and
harmless" but "abandoned and load-bearing until the artifact disappears". E452 asks the next
question: which of those opens would raise today.

## Pitfalls caught in-window

1. A bare-basename match against `smoke_test.py` classed 65 of 133 readers as smoke legs (a
   `run.py` substring). Requiring the repo-relative or dotted module path (plus the backslash
   spelling for Windows wrappers) reduced it to 1 smoke leg and 2 task-referenced readers.
2. The census discriminator was first taken from E446's `writer_faces` column, which only covers
   writers that touch the 51 frozen bases, so `face_writing_census` was 0 and `runnable_script`
   absorbed everything. Recomputing "publishes a face" over the full corpus moved 98 of 133 faces
   into the census class.
3. `e446.py_corpus` returns absolute paths; feeding those into `module_constants(rel=...)` makes
   `__file__` absolute. Relativising before the walk kept every published path repo-relative.
4. Truncating the published reader list (25 sites per base) also truncated the distinct-face tally
   (41 instead of 133). Counts are now computed over the full list and only the detail rows truncate.

## Reproduce

```
python scripts/e447_abandoned_read.py run       # rebuild the face
python scripts/e447_abandoned_read.py check     # re-derive the tallies from the published rows
python scripts/e447_abandoned_read.py verify    # re-derive from the live tree (~60 s)
python scripts/e447_abandoned_read.py selftest  # 30/30
python scripts/run_e447_smoke_leg.py            # 1/1
python scripts/run_e447_smoke_leg.py --doctor   # 1/1 red, face restored byte-identical
```