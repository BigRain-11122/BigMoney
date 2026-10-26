# DIGEST 2026-10-27 · E94: which of the 33 exposed modes actually read the repaired names

**Leg**: `python scripts\e94_readset_triage.py run` (new tool, 463 lines)
**Face**: `results/e79/triage-20261026.json` (33 rows, evidence cutoff 2026-10-26)
**Selftest**: `python scripts\e94_readset_triage.py selftest` → 19/19
**Reproducibility**: burned twice (03:01 and 03:23 on the same panel). Second burn
reproduces all 33 verdicts, all arm counts, the universe block and the summary
byte-for-byte; the only cell that differs is the `read_set` label on the seven rows
fixed below.

## What the face answers

E79 flagged 33 census modes as *exposed* (they read the per-name loader and publish a
weight-`1/n` number with no `raw=` hook). E81 leg 5 then showed the flag is necessary
and not sufficient — the tilt decomposer is flagged but cannot move, because no
repaired name is a ladder member. This leg asks the same question for every remaining
mode, mechanically, without rewriting any published face.

Three arms per runner (one probe per distinct runner, 19 units):

| arm | universe | what a hit proves |
|---|---|---|
| A `unscreened` | published universe | baseline |
| B `neutralise` | `panel_screen.screen_universe(..., mode="neutralise")`, 131 names | the repaired prints are charged |
| C `perturb_ladder` | A + 5% step on the 5 ladder members | activity control: the diff machinery can see this mode at all |
| D `perturb_repaired` | A + 5% step on 5 repaired names | the repaired names enter the arithmetic |

Every arm runs into a temp dir with `e27.load_universe` pinned; no published face is
regenerated, no ledger row is written, trial 0.

## The split

| verdict | n | meaning |
|---|---|---|
| `moves_under_repair` | 25 | must be quoted with its screen arm |
| `closed` | 4 | already has an E81 screened twin (`tilt`/`era`/`calrob`/`calcost`) |
| `structurally_immune` | 2 | `all` / `ladder` — ladder-local prices only |
| `probe_blind` | 2 | `stalehold` / `weeknames` — no arm moves them; immunity unproven |

So 25 of the 29 open modes are charged by the repaired prints, four were already
closed by twins, two cannot move, and two cannot be read either way. The refusal list
is the useful part: **`stalehold` and `weeknames` print no price arithmetic on any
perturbed name**, so their published numbers cannot be certified in either direction
from this harness. They are the two faces to re-derive by hand if they are ever cited.

## A defect this leg found and fixed

The first burn derived `read_set` from the 5-name step alone. Seven modes
(`cashdrag`, `chase`, `entrydelay`, `earlydelay`, `neighborhood`, `weeklyclash`,
`staletail`) came out as **"no price arithmetic on the probed names" while
`charged_by_repair = true`** — a self-contradicting row: the repair arm moved
`cashdrag` at 20 leaf paths (`wide_x3_delta_bp`, `wide_top9999/x0/ann_return_pct`, …)
yet the label claimed the wide book never enters the arithmetic.

Root cause is a label/evidence mismatch, not a probe bug: a book that averages over
1,317 names can absorb a 5% step on five of them and still move when the *whole* wide
book is repaired. The label now names whichever channel actually moved, and never
prints "no price arithmetic" on a face the repair arm moves (`read_set_label`, four
new selftest legs L16-L19).

Reading rule to carry forward: `intersects_repaired` is a **name-level** reading
(5-name step), `charged_by_repair` is an **arm-level** reading (whole repaired
universe). When they disagree, the arm-level answer governs how the face must be
quoted.

## Honest limits

- a 5% step on five names is a **lower bound** on sensitivity: "repaired" hits are
  detected more reliably than they are sized
- arm B repairs the `neutralise` branch (131 names); `neutralise_int` (67) is a subset,
  so clean-under-B implies clean under it, not the converse
- modes sharing one runner are probed once, with default arguments; a face produced
  with non-default arguments could still differ
- the probe runs to a temp dir, so this face says nothing about the *level* of any
  published number — only about whether that number can be contaminated
- descriptive census only: no gate, no verdict on any strategy, no ledger booking

## Next

25 charged modes is a routing problem, not a burn problem: before any of them is
re-derived, publish which of the 25 already have a screened twin on disk and rank the
rest by consumption (pool row `E97-READSET-TRIAGE-ROUTING`).