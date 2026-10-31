# DIGEST 2026-11-01 r1352 (bm-b) -- E332: what lives in the text the corpus helper cannot see

**Question.** E331 closed by publishing a bound on itself: 22 of 2,284 sources lose their tail to the
corpus helper's docstring rule, "so a load site written there is invisible". Two things were unmeasured:
what is in those tails, and which published E3xx count moves if the helper is corrected.

**Root cause, sharper than the card stated.** `e326.code_lines` enters doc mode on any stripped line
that *starts* with a triple quote and carries an odd number of triple marks. The
`TEXT = ("""...""".split())` idiom closes on a line that begins with the closing delimiter, so a
closing delimiter is read as an opener. Exit condition is the same odd-count test on any line, so the
flag re-synchronises on the next `X = ("""` — the file alternates in and out of a docstring that never
existed. Two consequences, in opposite directions: real code is dropped, and docstring prose is kept
(a one-line docstring counts two triple marks and is appended as "code").

**Measured.** 30 of 2,286 sources carry 4,284 real code lines the helper never shows: 157 defs, 0
classes, 18 face handles, 103 load-site lines, 187 selftest mentions. 22 sources hide code in several
disjoint spans (up to 91 in one file: `e231`, 550 hidden lines of 795). All 30 are blinded before their
last line; 8 of them E331's own tail metric reads as zero, because the file ends on a line the helper
does show.

**Re-pricing E331 (its own `build()`, run twice over one file list).** pointer-only readers 24 -> 25;
families reached only through a pointer 120 -> 125; readers that raise at the file 9 -> 10; pairs 44 ->
44 with exactly one pair reclassified: `scripts/e312_gate_operand_identity.py` / `gatetol` moves from
`reference_without_a_reader` to `pointer_only_reader` once its load site is visible. The verdict does
not move. E331's `sources_whose_tail_the_scanner_cannot_see` reads 22 with the shipped helper and 0 with
the corrected one — the metric is a property of the helper, not of the tree.

**Pits recorded.**
1. A metric that only looks at the file's end cannot see a mid-file loss (`tail_is_invisible` = 0 on a
   file with a `def` missing). Recover from an independent oracle and publish both numbers.
2. A helper defect has two directions; only one is a loss. The converse one (single-line docstrings
   shown as code) is disclosed, not silently normalised.
3. "Pairs visible only with the shipped helper = 1" was not a phantom pair: it was a reclassification.
   A net count hides which number moved — publish (source, family, from, to).
4. The re-pricing must run the consumer, and the patched helper must be restored in a `finally` with an
   assertion; a leak here silently re-prices every later study in the same process.

**Products.** `scripts/e332_invisible_tail_recovery.py` (run / verify 0 problems / selftest 16/16);
`results/state_tilt/INVISIBLETAIL-2026-11-01.json` + `invisibletail_latest.json`; S6 leg
`invisible_tail_recovery` rc=0 74.7s; smoke leg passes standalone, 3/3 mutations caught (zeroed
recovery, row without spans, inflated delta); methodology card E332.