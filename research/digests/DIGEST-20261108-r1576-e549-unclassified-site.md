# DIGEST 2026-11-08 r1576 bm-b -- E549: the four unclassified sites, read out of their enclosing functions

**Study**: `scripts/e549_unclassified_site.py` (card E549) · **Face**: `results/state_tilt/UNCLASSIFIEDSITE-2026-11-08.json` (+ `unclassifiedsite_latest.json`) · **Pool card**: E549 -> done.

## What the card asked

E546 (r1575) classified 35 constants whose terminal is the module file itself by what each *site* says the
constant is. Four rows came out `the_name_is_consumed_but_no_site_says_what_it_is` -- consumed, but no site
says whether it is a file or a directory. The card is explicit that the fix is not more sites but a read of
the enclosing function, and that a comparison which is the whole use must become a class of its own so that
"unknown" stops standing in for "we never read the enclosing function".

## What it found

| row | constant | enclosing function | read |
|---|---|---|---|
| `scripts/e391_key_name_two_meanings.py` | `SELF` @62 | `py_corpus` (222) and `selftest` (551) | identity token -- `os.path.abspath(p) == SELF` |
| `scripts/e392_read_resolve.py` | `SELF` @62 | `scan` (236) | identity token -- `os.path.abspath(path) == SELF` |
| `scripts/e446_frozen_writer.py` | `SELF` @37 | `py_corpus` (101) | identity token -- `os.path.abspath(p) == SELF` |
| `scripts/marks_coverage.py` | `CAL_PATH` @44 | `load_calendar` (150) | default argument; body does `os.path.exists(path)` (153) then `open(path)` (156) |

3 rows are identity tokens (4 comparison sites over 3 rows), 1 row is a file read through a default
parameter. Residual rows: **0**. Verdict:
`every_unclassified_site_was_read_out_of_its_enclosing_function_and_no_row_stays_unknown`.

## The three laws this round adds

1. **"unknown" is a statement about the instrument, not about the world.** A residual class has to be read
   in its smallest enclosing context before it is called a class; after that read, no row should stay
   unknown. The gate is `residual_rows == 0`, not "looks about right".
2. **A comparison is its own class.** Normalising the constant with `abspath` and comparing it makes the
   path an *identity token* (here: the module excluding its own file from the corpus it would otherwise scan
   itself into) -- not a file anybody reads. Leaving it in "unknown" makes a normal idiom read as a defect.
3. **A default argument is one hop, not "unfollowed".** The callee is the very function the default belongs
   to, so that row is exactly the allowed hop; classing it with "handed to a callee this scan does not
   follow" would report the readable as unreadable.

## Two defects caught before the gate

- The first `analyze()` bound parameter defaults into the walk with a broken comprehension
  (`for n in _classified(fn.body, p) for p in via_default`), which raised on every site -- fixed to
  `for p in via_default for n in ...`.
- The face problem list carried a leftover branch that checked "an identity row contains no opening load"
  against the **cross-row** use list, i.e. it could never fire. Replaced with a per-row `row_uses` check in
  both directions (identity row with a reading load, opened row with no `open`).

## Gates

`selftest 17/17` · `check` `problems=[]` (re-derives every row and the verdict from the sources now) ·
`verify` two builds identical · smoke leg `# E549` standalone `PASS`, `--doctor` `FAIL` (the gate can
refuse a hand-written verdict) · S6 leg `unclassified_site rc=0`.

## Limits published with the face

One enclosing function per site: a load handed to another callee is published as passed, not followed.
For the default-argument row the callee *is* the enclosing function, so that row is exactly one hop and no
further. A comparison class says what the AST does, not what the compared value means at run time. No
execution: "read as a file" means a load reaches `open()`, not that the file exists.

## Next

E550 seeded (supply floor back to 3/3): follow the 17 passed-to-a-callee sites from E546 one hop into the
callee and publish whether the callee opens, joins, tests, or passes it further -- the container failure mode
E546 was looking for, one layer down. E547 and E548 stay ready.