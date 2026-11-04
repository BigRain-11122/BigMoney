# DIGEST 2026-11-04 r1432 bm-b -- E403: the callers of a family-parameter reader

**Card.** `E403-DO-THE-CALLERS-OF-A-FAMILY-PARAMETER-READER-PASS-THE-RIGHT-FAMILY` (pool `ready`,
entered r1419, lane cpu-only). Seed = E398's 17 read sites whose family is a function parameter
(`family_required_by_the_site`'s sibling class `family_required_by_the_signature`).

**Answer.** Every measured call passes the reader its own family or a scratch directory the caller
just wrote; **0** call sites pass a different published family. 8 of 16 readers are reached only
through a forwarded parameter, so their safety is a property of the caller one level up -- and for
6 of those 8 the caller's own default is a measured published family (`results/state_tilt`).

| reading | value |
|---|---|
| seed read sites / distinct (file, function) readers | 17 / 16 |
| in-repo call sites | 38 |
| argument omitted, reader falls back to `param or DEFAULT` | 11 |
| scratch directory the caller created | 13 |
| forwarded parameter (caller decides) | 14 |
| foreign published family | 0 |
| runtime values left unclassified | 0 |
| readers whose forwarded parameter has a known default family | 6 |
| seed delta against E398's published face | 0 added / 0 dropped / 0 moved |

**Four lessons, all measured in-window.**

1. **A call-site census must price the fallback.** 11 of 38 calls omit the argument entirely and the
   reader then runs `outdir = outdir or OUTDIR` (10 readers measured, 10 resolved). Reading only the
   supplied arguments would have left 30% of the population as "unknown", which is the shape E398's
   class already suffered from.
2. **Scratch detection needs `with` bindings and path-shaped propagation.** `etf_book_order.selftest`
   does `with tempfile.TemporaryDirectory() as td:` and then `cd = os.path.join(td, "prod")`; the first
   draft only recognised a literal `mkdtemp()` in an `Assign` and published 7 of 38 rows as
   `runtime_value`. Fixing it by propagating through *any* referencing assignment marked `rc`, `spent`
   and `tot_w` as scratch directories -- a false-clean, which is worse than an honest unknown. The rule
   that holds: propagate only through path-shaped values (`Name`, `join/Path/str`, `a / b`).
3. **Corpus scope is a cost decision with a falsification test.** Parsing every `.py` in the repo meant
   3337 files and 77 s per chain leg. Excluding `results/` (8621 artefact copies, not importable
   modules) *and then re-publishing the same 38 call sites* is the evidence that the exclusion cost
   nothing; the leg now runs in 3.07 s.
4. **One hop of forwarding is not the answer.** Six `_write(face, outdir)` readers publish as
   "safe here but its own caller decides" -- and the caller is `run(save=True, outdir=None)` whose first
   line is `outdir = outdir or OUTDIR`. Publishing only the first hop would have produced six false
   alarms against readers that cannot in fact land on a foreign family through the chain.

**What this does not claim.** No reader and no caller was edited. Call sites reached through a name
built at runtime, or through a dict of callables, are outside the census; the face says so. The
family universe is the 52 directories that hold a `*latest.json` pointer today.

**Wiring.** `scripts/e403_family_arg.py` (run / `verify` problems=[] / selftest 11/11); faces
`results/state_tilt/FAMILYARG-20261103.json` + `familyarg_latest.json`; smoke leg `# E403:` in
`smoke_test.py`, proved green on the live tree and red on a doctored copy (summary +1 reader), face
restored byte-identical (sha256 unchanged); S6 leg `family_arg` (rc 0, 3.07 s); card E403 in
`knowledge/METHODOLOGY_ASSETS.md`; pool card E403 → done, E414 seeded.