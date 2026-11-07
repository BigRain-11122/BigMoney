# DIGEST 2026-11-07 r1536 bm-b — E507: where the residual date symbols bind

**Card**: E507-WHERE-DOES-THE-DATE-COME-FROM-WHEN-THE-MODULE-NEVER-BINDS-IT
**Face**: `results/state_tilt/UNRESOLVEDORIGIN-2026-11-07.json` + `unresolvedorigin_latest.json`
**Script**: `scripts/e507_unresolved_origin.py` (run rc0 / check problems=[] / verify problems=[] / selftest 18/18)
**Chain leg**: `Tools/s6_chain_bmb.py 1536 --only unresolved_origin` — rc0 0.06 s (`results/_r1536bmb_s6_chain.json`)
**Smoke leg**: `# E507 (r1536 bm-b)` run standalone 1/1 green; `--doctor` 1/1 red, face byte-identical after restore (sha 45a076d98e95)

## Question

E504 priced 123 naming sites (885 site/member pairs) and left 169 pairs unresolved because
the date symbol behind the name is not assigned inside the naming expression's own module
scope, plus 61 dated members with no composing expression anywhere. That was a bucket a
name-based retention rule could not read. This study asks, per residual: which binding fills
the symbol — a local helper's return, a right-hand side in the same module, an imported
attribute, an element of loaded data, a selftest fixture writing a temp path, or a script only
git history still holds — and does the resulting name state the run clock or the data day?

## Reading (2026-11-07)

169 residual pairs / 97 members / 14 sites = 19.1 % of E504's 885 pairs. **Every pair now binds
something; none is unreadable.**

| residual class | pairs |
|---|---|
| local helper called by the composition | 79 |
| right-hand side bound in the same module | 24 |
| element of loaded data (series / panel index) | 29 |
| selftest fixture writing a temporary path | 29 |
| the matched gap carries no date at all | 8 |

| track | pairs |
|---|---|
| clock (the name states the run day) | 58 |
| data (the name states the data day) | 61 |
| mixed (the symbol binds more than one way) | 42 |
| neither (no date in that gap) | 8 |

- **119 pairs name exactly one origin** — 58 clock, 61 data — so the residual bucket is not
  clock-flavoured or data-flavoured; it is both, and each pair carries which.
- **42 pairs are ambiguous**, and the ambiguity is mostly a property of the instrument: the
  binding table is module-wide, so one symbol reused in several places (e.g. `_cal` in the
  28k-line census module) collects every assignment. Published as `mixed`, never resolved by
  picking the last one. Card E510 is seeded to price a scope-aware table against these 42.
- **29 pairs live inside a selftest** (`marks_coverage.py::_selftest` writes `marks-<dig>.jsonl`
  into a temp directory). They are published as fixtures, not as published faces — a name-based
  rule that counted them would be counting test strings.
- **8 pairs are not dates at all**: in `NEIGHBORHOOD-…%s%s%s.json` the matched gap is the cost
  tag, not the day; the date slot is filled by `f['evidence_cutoff']` in the same expression.
  That is an E504 gap-selection artefact, published rather than silently re-picked.
- **0 pairs and 0 of the 61 no-site members bind only in history.** The 110 python blobs HEAD
  still holds but the working tree does not name none of the 61 families, so the no-site bucket
  is not "the generator script was deleted". They are written by scripts that never compose a
  dated name at all (`PROFILE-<date>.json` is produced by a loop over a name constant).

## What the two self-caught defects were

1. A module-wide assignment table let a comprehension target (`for d in …`) resolve through
   every other `d` in a 28k-line module, which manufactured a fake mixed answer. Comprehension
   targets are now shadowed.
2. A helper that opens a file and returns a locally accumulated list (`rows.append(...)`) read
   as unknown until file-reading helpers were classified as data-derived, and a date-index
   constructor (`pd.DatetimeIndex`) fell through the import branch into unknown.

## Method limits (on the face)

Static, single-repository, one import hop per level (depth ≤ 8). The history arm is a labelled
snapshot: 110 blobs, lazy fetching disabled, so a zero hit is a statement about this clone, not
about the remote — and the gate re-derives everything except that arm. `mixed` is never folded
into clock or data.