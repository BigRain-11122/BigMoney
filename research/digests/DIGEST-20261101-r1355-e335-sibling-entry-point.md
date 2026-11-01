## E335 -- a repair that lands "inert" must be shown inert on three axes, and one of them is a source scan because the failure is a future edit

E334's frozen rule sent the fix of `e326.code_lines` to a sibling entry point. E335 is that landing and its proof:
`code_lines` keeps its exact behaviour, `code_lines_legacy` pins it by alias (not a copy, which would freeze
silently), and `code_lines_tokenized` exports the tokenizer reading that E332 counts as the repaired half. No
consumer is switched — E334 priced that as a separate and much larger decision (6 faces / 37 numbers).

Three axes, all published rather than asserted. (a) **Coexist**: the two readings disagree on **1,369 of 2,294
sources**; an entry point that agrees everywhere is an alias, not a second reading. The largest gaps are the
defect families the corpus already knows (`perpetual_faces_n1.py` 114,302 shipped lines vs 73,680 tokenized;
`e39_panel_census.py` -1,400; `e330_unpinned_choice.py` +595, where the shipped helper under-reads). (b) **Re-derive**:
all **30 of 30** per-source deltas E334 published are recomputed *through the new name* and land at **max abs diff
0.0** against a 1e-9 tolerance — the new entry point is the reading E334 priced, not a lookalike. (c) **Inert**: an
AST scan of every `.py` in the corpus finds **0 permanent rebinds** of a reading name and **0 consumers** of the new
one.

Two rules about what "rebind" means, both found by running the check against the tree instead of assuming it.
(1) **The studies this card protects patch the helper on purpose.** E332, E333 and E334 all assign
`e326.code_lines` and restore it in a `finally`; a naive scan called those 14 assignments rebinds and failed the
landing on exactly the code it exists to keep measuring. A rebind is an assignment *no enclosing scope restores*;
a restored patch is disclosed as its own count. (2) **The failure mode is a future edit, so the guard is a source
scan plus one runtime identity check** — a runtime probe alone cannot see a module that nobody imports yet, and
the static scan alone cannot see a runtime rebind of a module already imported. The legacy identity check
(`code_lines_legacy is code_lines`) is the cheap second half.

Evidence: scripts/e335_sibling_entry_point.py (selftest 20/20, verify 0 problems) -> results/state_tilt/SIBLINGENTRY-2026-11-01.json -> research/digests/DIGEST-20261101-r1355-e335-sibling-entry-point.md -> Tools/s6_chain_bmb.py leg sibling_entry_point -> smoke_test.py leg E335