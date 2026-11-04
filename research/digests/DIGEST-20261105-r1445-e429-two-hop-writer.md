# DIGEST 2026-11-05 r1445 bm-b -- E429: the directory a face is composed with is one hop from its name

**Card.** E429-WHICH-NO-WRITER-FACE-IS-COMPOSED-BY-A-HELPER-THE-CENSUS-CANNOT-SEE (pool,
cpu-only, ready 2026-11-04)
**Product.** `scripts/E429_two_hop_writer.py` + `results/state_tilt/TWOHOP-2026-11-04.json`
(+ `twohop_latest.json`), smoke leg `# E429 (r1445 bm-b)`, S6 leg `two_hop_writer`,
methodology card E429.

## What was asked

E419 graded 3 of its 9 undated faces `no_writer_in_the_tree` and wrote the limit into its own
method notes: *a face composed from a variable and written by a shared helper is out of reach.*
The E429 card asks for that hop: follow the write call into the helper that receives the path and
resolve its parameter from every call site; publish per face whether a hop was found, who supplied
the name, and the fraction of the corpus a two-hop walk reaches -- refusing to call a hit a writer
unless the helper actually opens for writing.

## What was found

| reading | value |
| --- | --- |
| E419 no-writer rows | 3 |
| became writers once the directory was followed | **3** |
| ... of which the writer carries a payload date | 0 |
| ... of which the face *name* encodes a date | 1 (`AGGATT-%s.json`, via `% cutoff`) |
| path write sites in the corpus | 2,422 |
| ... that spell a literal in the path expression | 409 (16.9%) |
| ... rescued by a constant hop | +1,555 (**1,964 = 81.1% visible**) |
| ... that still need the caller hop | 458 |
| sites taking the directory from a helper parameter | 310 |
| ... caller supplies a literal directory / a constant / none found | 254 / 21 / 35 |

The three rows, with the hop that recovers each:

| face | E419 | now | hop | where the directory comes from |
| --- | --- | --- | --- | --- |
| `results/etf_book_production/CARD.md` | no writer | writer, no payload date | constant | `OUT_DIR = join(results_dir, "etf_book_production")`, two substitutions |
| `docs/futures_lane/TSMOM-%s.md` | no writer | writer, no payload date | constant | `page = join(DOC_DIR, ...)` -> `DOC_DIR = join(ROOT, "docs", "futures_lane")` |
| `results/state_tilt/AGGATT-%s.json` | no writer | writer, no payload date | caller | `_write(face, outdir)` <- `run()`'s `outdir = outdir or OUTDIR` |

## Rules (each one is a selftest leg)

1. **A whole-line source slice is not an expression.** Reusing e419's line slices for *values* put
   the assignment back into every substitution (`join(outdir, name = 'AGG-%s.json' % face)`); exact
   column slices cost nothing and are exact.
2. **A literal-only binding rule hides the default argument.** `outdir = outdir or OUTDIR` carries
   no quote of its own, so the alias that supplies the directory was invisible and the helper graded
   "no caller supplies it".
3. **Opening for reading is not writing.** The first draft attributed `CARD.md` to
   `etf_book_production.py:1050`, which *reads* a CARD.md out of a temp directory.
4. **A shared helper name admits a foreign call site.** The caller hop is name-based; the limit is
   published, and the fixture separates "no caller" from "another caller".
5. **A payload census cannot see a date in a name.** `date_in_the_composed_name` is its own published
   signal, not folded into the class.

## Why it matters

E426 priced the naming side (6,716 of 10,034 faces are reachable only through a variable-built
name). This card prices the attribution side: 83% of write sites do not spell their path, so a
literal write census does not merely miss names -- it manufactures "no writer" verdicts for faces
that have one. Any future "this face has no writer / no date / no refresh" claim is only as strong
as the hop budget behind it, and the budget should be published with the claim.

## Honest walls

- The full ~320-leg smoke suite was **not** re-run this window; the new leg was extracted verbatim
  and run standalone (1/1, red on a doctored tally, face restored byte-identical `54700c6b21767aa0`).
- The corpus numbers are write *sites*, not faces and not run frequency: one function can write
  several names and a hot site is weighted the same as a dead one.
- Constant expansion stops after three substitutions / 4,000 characters; a runtime-built directory
  (env var, date-formatted) is not resolved and is counted in the 458.