# DIGEST-20261110-r1669-e651-template-fold

- study: **E651** — do the 14 expression-built strings E647 left unresolved name a counted read module once their operands are folded from the module's own bindings?
- round: **r1669 bm-b** (2026-11-10) · machine `bm-b` · lane `cpu-only`
- face: `results/state_tilt/TEMPLATEFOLD.json` + `templatefold_latest.json`
- tool: `scripts/e651_template_fold.py` (selftest 26/26, `run`/`check`/`verify` rc0, `problems=[]`, rebuild byte-identical sha `71bd3d998f63506e`)
- legs: `smoke_test.py` leg E651 (`scripts/run_e651_smoke_leg.py` 1/1 PASS, `--doctor` 1/1 red with the face restored byte-identically, sha `71bd3d998f63506e` in = out) + `Tools/s6_chain_bmb.py` leg `template_fold` (rc=0 0.06s)

## Why the question exists

E647 measured every string its six hit modules can be asked to spell (480 literals, all-constant
f-strings, `"a" + "b"` folds) and published the remaining 14 — f-strings with a formatted value,
`%` formatting, `str.format` — as `unresolved`, naming that count as a limit of its own arm. A limit
that names a measurable population is a hole, not a disclaimer (E453/E488/E462 family), and this
round is the walk that closes it.

## What was measured

An expression-built string can carry a target name in two disjoint places, and they are measured
apart on purpose:

- **the template** — the literal text the expression starts from. It is measurable for all three
  forms (the left operand of `%`, the receiver of `.format`, and the constant fragments of an
  f-string) and it is matched **before** any operand is resolved, so a name written into the text is
  published on the template arm and is never hidden behind a fold that failed;
- **the operands** — a value substituted into the template can only be a name if the value is
  knowable. Every operand is resolved against the scope chain the site sits in: a literal, the
  module's own string constant (including one assigned inside a module-level `try:` / `if:` block,
  because the module body is a block tree), an alias of one, or a string constant assigned in the
  enclosing function. The operands that cannot be resolved are published with their binding class —
  loop target, comprehension target, except-arm name, module-level non-constant, call result,
  attribute/subscript, other expression, unbound name — rather than folded into one "unresolved"
  counter.

Only a site whose operands are all resolved is folded, and the fold applies the **real Python
operator**, so a `"%d"` template fed a string constant raises and is published as `operator_raised`
instead of being read as a folded value. Conversion (`!r`) and a format spec inside an f-string are
their own published reasons.

## Reading

- 14 expression-built sites in 6 modules (12 `%`, 2 f-strings), re-derived; E647 published 14;
- 7 hits re-derived, matching E646/E647's published 7;
- **0 template fragment names a counted read module** and **0 folded string names one**;
- 29 operands, **1 resolvable** → **1 site folds, 13 stay residual**; the one folded value is
  `"N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN"`, consumed by `text.find` (an `ENTRY_ID` lookup, not a module);
- operand bindings: `other_expression 19`, `attribute_or_subscript 5`, `module_level_non_constant 3`,
  `module_level_string_constant 1`, `exception_target 1`, everything else 0;
- **all 14 sites are consumed by `no_call` 7 / `other_call` 7** (print, join, find) — **0 by import or
  file machinery**.

## Verdict

> no template fragment and no folded string names a counted read module, and every site that cannot
> be folded is consumed by formatting or by nothing at all rather than by import or file machinery,
> so the residual cannot be a route to a module even if a value named one

## Lessons

1. **"Cannot be folded" and "folded and empty" are two quantities and must be published apart.**
   Folding the 13 residual sites into the zero would let a reader hear "the arm is closed"; the face
   publishes `sites_folded` / `sites_not_foldable` / `sites_by_fold_reason` side by side and the
   verdict names the residual as a residual.
2. **The template is an independent measurement that precedes the value.** The first build only
   matched the folded value, so a site like `f"scripts/x.py/{q}"` — where the name is written in the
   text and no operand matters — would have been published as "could not fold, so unknown". The two
   arms (`template_fragment`, `folded_value`) are separate buckets in the counts and in the pairs.
3. **The module body is a block tree, not a list of top-level assignments** (E643's lesson reused).
   The first resolver scanned `tree.body` only, so a constant assigned inside `try:` was published as
   `unbound_name` (two sites mis-named). Descending through `if`/`try`/`with`/`for`/`while`/`match`
   while refusing to enter functions, lambdas and classes took `unbound_name 2 → 0`, and the except
   handler's name became its own class (`exception_target`).
4. **An f-string folds as fragments interleaved with values, not as values joined.** The first build
   produced `e382_x` for `f"{N}.py"`, dropping the constant tail — the selftest caught it because
   the expected value was the string the source would actually build.
5. **Whether a name exists and whether it is a route to a module are two questions.** Seven sites are
   not even consumed by a call; the other seven are consumed by `print`/`join`/`find`. A string
   naming a module and never handed to import machinery is a spelling, not a reach.