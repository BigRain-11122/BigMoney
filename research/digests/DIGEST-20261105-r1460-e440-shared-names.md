# DIGEST 2026-11-05 r1460 (bm-b) -- E440: what the 25,008 rows E439 dropped actually are

**Question.** E439 published 40 call rows into eleven file-path wrappers and put the other 24,911
under the word *overstated*, on the rule "the caller file must be the defining module or a module
that imports it". That word claims something about the dropped rows. Which is true: the name index
invented them, or the tree has helper names several modules define?

**Method (two axes, neither inferred from the other).**
1. Definitions per name -- imported verbatim from `e439.definition_counts`, no re-implementation:
   `_judge_lock_acquire` 1, `_syn_file` 3, `_write_csv` 8, `append` 2, `apply_close` 1, `dump` 11,
   `run` 300, `save` 18, `write` 26, `write_face` 41, `write_json` 28. **9 of 11 names are defined
   by more than one module.**
2. Spelling at the row's own line -- parsed from the caller's live AST and cached per file as
   `(line, name) -> {attribute, bare}`: an attribute call names a receiver, a bare call names a
   module-level function.

**Reading (25,015 dropped rows, 3,463 sources).**

| class | rows | share |
|---|---|---|
| `shadow_a_method_call_on_some_object` | 24,308 | 97.2% |
| `shadow_a_bare_call_to_a_name_more_than_one_module_defines` | 707 | 2.8% |
| `shadow_a_bare_call_to_a_name_with_a_single_definition` | **0** | 0.0% |
| `shadow_the_call_is_not_at_that_line_any_more` | 0 | 0.0% |

Verdict (recomputed by the gate from the rows):
`every_dropped_row_is_either_a_method_call_or_a_bare_call_to_a_name_that_more_than_one_module_defines`.

**Why the zero is the result and not a null.** A zero residue is only meaningful when the class that
*would* be residue is measured and published. The selftest carries a fixture where a bare call to a
single-definition name must flip the verdict to `some_dropped_rows_are_bare_calls_to_a_name_with_a_
single_definition`, so the zero cannot be produced by a scan that classifies nothing as bare.

**Distance from E439, disclosed rather than reconciled away.** 25,015 today against E439's 24,911:
the corpus grew by 8 sources and the tree moved between the two builds (three consecutive builds this
window read 25,008 / 25,015 / and the published value). `summary.distance_check` publishes
`agrees=false` and the recomputed count beside the published one instead of forcing them equal.

**Instrument notes.**
- One AST parse per file, indexed by line, is what makes 25k per-row questions cheap; the first draft
  walked the tree per row.
- The first draft mapped `both_spellings_at_that_line` into the method class, which silently removed
  a possible residue row; the class is now decided by the definition axis, with the spelling only
  able to short-circuit to method when the call is *exclusively* attribute-qualified.

**Artifacts.**
- `scripts/e440_shared_wrapper_names.py` (run | verify | selftest)
- `results/state_tilt/sharedname_latest.json` + `SHAREDNAME-<cutoff>.json`
- `smoke_test.py` leg `e440 shared wrapper names (r1460 bm-b)`; `scripts/run_e440_smoke_leg.py`
  (extracted verbatim 1/1, doctored class 1/1 red, face restored byte-identical 7abee58ed9b97d4d)
- `Tools/s6_chain_bmb.py` leg `shared_wrapper_names`
- `knowledge/METHODOLOGY_ASSETS.md` card E440 (numstat 38/0, `newline='\n'`, no flattening)

**Bounds.** Definition counts are per file with a top-level def, so a name that exists only as a
method counts zero; the spelling axis does not infer the receiver's type, so a module reached through
an alias reads as attribute-qualified; and a bare call to a single-definition name may still be a
local function -- residue is a floor, and today that floor is empty.