# Digest — E543 (r1570 bm-b): can the published line close E542's ambiguity by itself?

**Question.** E542 measured 32 ambiguous census rows and found their survivors sit in different
statements. That makes a zero-cost question available: if the census row already publishes a `line`,
what happens when that line is read as a *statement anchor* — keep only the survivors whose innermost
statement opens on it? Does the row get decided, does it stay ambiguous, or would the rule empty it?

**Method.** Take E542's 32 rows and their 73 survivors (recomputed by running E542's own build over
the faces on disk, not copied from a card). For every row select the survivors whose `statement_line`
equals the row's `published_line`:

    one selected   -> decided
    two or more    -> still ambiguous
    none           -> refused (the rule would empty the row)
    missing field  -> unresolved

For every decided row also recompute E540's nearest-to-published rule — through E541's own
implementation — and publish whether it picks the same node (line + column) the statement anchor keeps.

**Readings.** 32 rows / 73 survivors. **The rule decides only 6 rows** (6 survivors kept, 67 ruled
out), **0 rows stay ambiguous, 26 rows would be emptied and are published as refused**, 0 rows carry
an unresolved statement line. On the 6 rows it does decide, **E540 agrees 6 out of 6**.

**Verdict.** `reading_the_published_line_as_a_statement_anchor_would_empty_most_ambiguous_rows_because_no_survivor_sits_in_it`

**What it means.** The published line is *not* a general statement anchor. On 26 of 32 rows the
published line does not open the innermost statement of any survivor — typically the published line is
a block line while each survivor's innermost statement is the `Assign`/`Expr` inside that block, which
opens on its own line. So "close the ambiguity for free with a field the census already publishes"
holds on 6 of 32 rows only; E542's account cannot be closed by this one field and still needs new
evidence or another published field.

**Methodology (three rules).**
1. **An empty set is not a decision.** 26 rows would be emptied by the rule; they are counted as
   `refused` and published as "this rule does not apply here", never as "zero candidates = decided".
   A rule that empties a row is evidence against the rule, not a win for it.
2. **A block header line is not a statement opening line.** The AST's innermost statement of an
   expression inside an `if`/`for` body is the `Assign`/`Expr` in that body, not the `if`/`for` node
   line. Any "line number as statement anchor" criterion must first name which `ast.stmt` it anchors
   on (fixture-proved: with the published line on an `if` header, none of the three survivors match).
3. **An agreement rate is only computed over rows the rule actually decides.** 6 of 6 is not "the two
   rules are equivalent"; the denominator is 6, not 32 — so the face publishes
   `decided_rows_compared_with_e540` next to `rows`.

**Artifacts.** `scripts/e543_statement_anchor.py` (run/check/verify + selftest 28 arms),
`results/state_tilt/STATEMENTANCHOR-2026-11-08.json`, `results/state_tilt/statementanchor_latest.json`,
smoke leg `# E543`, card `knowledge/METHODOLOGY_ASSETS.md` E543.