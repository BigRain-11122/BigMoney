# DIGEST 2026-11-05 r1448 bm-b -- E428: the 35 "no caller found" sites were a hole in the call index

**Card.** E428-WHICH-PARAMETER-DIRECTORY-HELPER-HAS-NO-CALLER-IN-THE-CENSUS (pool, cpu-only,
ready 2026-11-04; producer committed by r1447, published here)
**Product.** `scripts/e428_no_caller.py` (run / verify problems=[] / selftest 13/13) +
`results/state_tilt/NO_CALLER-2026-11-04.json` (+ `no_caller_latest.json`), smoke leg
`# E428 (r1448 bm-b)` + `scripts/run_e428_smoke_leg.py`, S6 leg `no_caller`, methodology card
**E431**.

## What was asked

E429 (r1445) followed the directory of every "no writer" face one hop and, on the way, billed the
corpus half: 311 parameter-directory write sites, of which 255 were handed a literal directory by a
caller, 21 a constant, and **35 had no caller in the corpus**. The card asks for those 35: is the
helper called from outside the python census, are all its calls supplied a directory no constant
names, or is there no call site at all? Refuse to call a site dead while it is reachable from a
non-python caller.

## What was found

| reading | value |
| --- | --- |
| parameter-directory write sites | 310 (311 at E429's cutoff) |
| unplaced under E429's instrument | **35** |
| unplaced once every parameter-directory helper is indexed | **2** |
| ... unplaced *only because the helper was never indexed* | **33** |
| ... calls exist but never supply the parameter | 1 (a `write=None` default) |
| ... named only outside the python corpus | 1 (a receipt document) |
| helper names the narrow index registered | 75 of 97 |
| corpus half, re-derived | literal 279 / constant 29 / no-caller **2** |
| fixture-shaped sites in the population | 21 |

**The mechanism.** E429 built its call-site index from helper names satisfying
`parameter_directories() and not spells_a_literal()`. A function that writes
`os.path.join(outdir, "x.json")` takes its directory as a parameter *and* spells a literal -- the
commonest writer shape in this tree -- so its name never entered the index, `index.get(name)`
returned `[]`, and the site was published as a site nothing calls. The 35 was therefore mostly a
statement about the index's selector, not about the corpus: 33 of the 35 are supplied by a caller
that spells a literal directory. The two that survive are honest residuals -- one helper whose calls
never pass the parameter (its `write=None` default is the canonical opt-in shape) and one that is
only named in a markdown receipt, which the rule forbids calling dead.

## Why it matters

The headline was wrong by a factor of 17 while every line of code was correct: the defect lived in
which names the index was built for. A published zero is a claim about the instrument until the
instrument's selector is audited (card E431, rule 1).

## What was NOT done

- The full ~330-leg suite was **not** re-run this window; the new leg was extracted verbatim and run
  standalone (1/1), then proved red on a doctored population with the face restored byte-identical.
- `scripts/e428_no_caller.py` was written by r1447 and is **not** this window's authorship; this
  window ran it, published its face, and wired the leg, the S6 leg and the card. A duplicate
  producer was built first and deleted once the committed one was found (card E431, rule 4).
- No writer, reader or face outside this study was edited.

## Pointer

Next card seeded from this study's own residual: the 21 fixture-shaped parameter-directory sites --
does any of them write a path a published reader opens, or are they test-only writers?