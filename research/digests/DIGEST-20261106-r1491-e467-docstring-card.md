# E467 -- the card in a producer's docstring is read by exactly one program, and it is the census that asked (r1491 bm-b)

**Card.** E467-IS-THE-CARD-IN-A-PRODUCERS-DOCSTRING-EVER-READ-OR-IS-THE-IDENTITY-HUMAN-ONLY
**Face.** `results/state_tilt/DOCSTRINGCARD-2026-11-06.json` (+ `docstringcard_latest.json`)
**Runner.** `scripts/e467_docstringcard.py` -- run rc0 / `check` problems=[] / `verify` problems=[]
on a live 3.5k-source walk / selftest 73/73
**Method card.** `knowledge/METHODOLOGY_ASSETS.md` E467
**Pool.** E467 done -> E469 seeded (ready 3/3)

## What was asked

E460 (r1489) read the 21 producers of 12 identity-gap faces and found that every one restates its
own card twice: in the module name (`eNNN_`) and again in the module docstring -- while 11 of the
12 payloads carry the identity only as a producer *stem*. If the docstring is where the identity is
written down, does any program in the tree ever read it back?

## What was measured

3,529 `.py` sources (218 with any signal, 3,311 silent), 223 `scripts/eNNN_*.py` producers.

| channel | count |
|---|---|
| producers that restate their own card in the docstring | 212 of 223 |
| producers that never restate it | 0 |
| producers whose card lives **only** in the docstring + module name | 0 |
| producers that write the card as a literal outside the docstring | 44 |
| producers that write an identity-named key but never the card literal | 179 |
| sources that read a docstring at all (3 by call, 3 by `__doc__`) | 6 |
| sources that look for a card shape anywhere | 129 |
| sources that key an identity-named payload field | 112 |
| sources that apply **any** regex to docstring text | 2 |
| sources that apply a **card-shaped** pattern to docstring text | **1** |

The single card join is `scripts/e460_facegap.py` -- the study that raised this question one round
earlier (`CARD_RE.findall(doc)` where `doc = ast.get_docstring(tree) or ""`). The other joins are a
study-id and a prereg pattern in the same file, and two prose patterns in `g2_overlap_census.py`.

Verdict: `at_least_one_source_applies_a_card_shaped_pattern_to_the_text_a_docstring_read_produced`.

## Why it matters

"Human-only" turns out to be too strong and too weak at the same time:

* **Too strong**: the file name carries the card, and any program can read it for free. The
  docstring is redundant, not the last resort.
* **Too weak**: no *product* recovers a card from a docstring. The one that does is a census, i.e.
  the `producer_only` pattern E204 named -- a reader that exists because the auditor wrote it, not
  because any consumer needs it. The repair for an identity-gap face is unchanged: write the card
  into a payload field.

## Pits

1. **A pattern that matches everything is not a pattern.** The first build published 1,203 sources
   as "looking for a card shape" because `""` and `"x|"` compile and match any probe. A pattern now
   counts only when it hits its probe and misses a plain sentence and the other probe.
2. **Co-occurrence is not a join.** The first tier called a source a "docstring-to-face-path joiner"
   when the file read a docstring *and* held a card regex *and* held a path literal. Four sources
   qualified; all four parse module docstrings and none reads a face. The join tier now needs a
   visible dataflow edge: a regex call whose subject is the docstring expression or the variable it
   was assigned to.
3. **`ast.unparse` re-quotes a string constant** -- the compiled pattern then contains apostrophes
   and matches nothing. Read `Constant.value`.
4. **A compiled pattern is not a string constant.** `CARD_RE = re.compile(...)` is how every study
   in this tree spells it, so a join whose receiver is that name grades "other" unless the constant
   table is extended to compiled literals -- which is exactly how the one real card join was missed
   on the second pass.

## Wiring

* `scripts/e467_docstringcard.py` (run / check / verify / selftest)
* `scripts/run_e467_smoke_leg.py` -- extracts the leg verbatim; standalone 1/1 PASS
* `smoke_test.py` leg `e467 is the card in a producer's docstring ever read (r1491 bm-b)` with three
  doctored copies (a producer classed on paper, a join erased from a reader that still claims the
  join tier, a tally whose card-join count stopped matching its rows)
* `Tools/s6_chain_bmb.py` leg `docstring_card` (234 legs, `ghost_legs()` empty)
* pool E467 done with result_ref; E469 seeded

## Not run / stated

The full smoke suite was launched detached at round open (`results/_smoke_r1491.out`) and was still
running at close, so no suite total is claimed here; the new leg was proven standalone instead.