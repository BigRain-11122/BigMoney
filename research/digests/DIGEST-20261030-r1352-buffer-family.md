# r1352 — the buffer family is closed, and the word "REJECT" turned out to be the default

**Pos:** `scripts/etf_book_phase_atlas_arms.py` (two arms added, selftest 25 → 38) ·
`scripts/etf_book_rule_null.py` (new, selftest 10/10) · `results/etf_book_phase_atlas_buffer_k10.json`
+ `_k20.json` (280 engine runs each, 4 workers) · `results/etf_book_rule_null.json` ·
S6 legs `etf_book_phase_atlas_arms` / `etf_book_rule_null` · smoke legs for both ·
card E261.

## Absorbed from the dead window

The r1351 window left three pool rows written onto a face that was already behind origin. They
were landed by id (max-merge; ids are unique, origin carries none of them) rather than by
replaying the file, and the two rows this round could actually answer were stamped `done` only
after their faces existed and their audit carried the declared knob.

## What was priced

The pool asked the rest of the buffer family that r1325 named and r1351 left open. Both arms ran
the whole 12-cell grid over every decision origin of its own cycle (280 engine runs each):

| arm | median per-cell Δ | cells beyond own band | median band | not-worse share | verdict |
|---|---|---|---|---|---|
| buffer k=0.05 | −0.030pp | 0 / 12 | 6.85pp | 0.667 | REJECT |
| buffer k=0.10 | +0.072pp | 0 / 12 | 6.99pp | 0.833 | NOT-SEPARABLE |
| buffer k=0.20 | +0.138pp | 0 / 12 | 6.58pp | 0.917 | NOT-SEPARABLE |

**0 of 36** cell-level deltas clear their own band, and the sign flips between the outermost arms
in 3 of 12 cells (k=0.05 negative where k=0.20 is positive in 2 of them). The knob is not
"small but real"; on this design it is not measurable at all.

## The part that changes how this repo reads every verdict

Two readings were open: (a) the family is a tiny real effect and the rule sorts it honestly;
(b) the family is noise and the rule's label is a coin toss at this ruler. The only question that
separates them is what the rule says when the data provably has no effect, so the labeler was run
on the same 12 cells with each delta replaced by a zero-mean normal of that cell's own width
(σ = band / 3.2905), 20,000 seeded trials, `judge()` imported from the arms module rather than
copied:

| label | share under an effect-free panel |
|---|---|
| REJECT | **96.48%** |
| NOT-SEPARABLE | 3.52% |
| ADOPT | 0.00% |

Mechanism, and it is arithmetic: the rule's cell floor is −0.15pp while one sigma of these cells
is **2.03pp** (13.5× larger), so roughly half the cells land under the floor by chance and the
"not-worse share ≥ 0.80" condition then fails by construction.

Consequences, published as such:

1. **A REJECT on this ruler is not a measurement.** The k=0.05 REJECT published last round, and
   the cost 20bp / 40bp REJECTs in E260, are all the label an empty panel receives 96.5% of the
   time (`null_p_same_or_worse = 0.9648` each).
2. **NOT-SEPARABLE is the rare branch, so it is the informative one.** The three arms reading it
   (cost 5bp, buffer k=0.10, k=0.20) are the only ones saying something a null panel says 3.5% of
   the time: these arms are *not worse* — a statement about sign, still useless about size.
3. **The family is closed.** Not adopted, not re-stocked. Adding arms cannot fix a degenerate
   label distribution; only the ruler can be fixed (report Δ/band, or derive the floor from the
   band), and that is a new pre-registered rule, not an edit to the frozen one.

## Supply and wiring

Three ignitable rows stocked, all on the runner that already exists, each writing its own face so
two ignited rows cannot clobber each other: buffer k=0.02 (near-zero end), buffer k=0.40 (far
end — the point where a real knob would finally leave the band), and buffer k=0.05 at 20bp/side
(the interaction the two closed families were never judged against). `fill_ladder` reads
ready 3 / floor 3.

The null face is read back by the chain (`--check`, 2s, engine-free) and pinned by the smoke
suite (10 legs: seeded reproducibility, two activity preconditions so a "rule that never ran"
cannot pass, verdict-follows-from-frequencies, and the gate's three states).

## Two things this round learned about its own tools

1. **A verdict string must be derived, not narratable.** The first version of the null verdict
   assumed the label it would find and printed "separability is not" with the numbers pointing the
   other way; the selftest leg for the branch caught it because it asserts the *shape* the branch
   requires, not the sentence.
2. **`x` vs `1/x` is the same bug as a unit error.** The first reason line read "the floor is
   0.1x smaller than one sigma" from `floor/sigma` (0.074) where the sentence needed `sigma/floor`
   (13.5). Numbers that are merely *plausible* survive review; the sentence around them does not.