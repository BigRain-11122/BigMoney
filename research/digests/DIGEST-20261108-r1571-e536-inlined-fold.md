# Digest — E536 (r1571 bm-b): was the refused repo-source callee impure, or was the refusal about the site's argument?

**Question.** E533 followed one hop out of 52 undecidable arms and left four open. Exactly one of
them was refused because "the callee is repo source" — the fold does not inline it, so it stopped
without reading the body:

    scripts/e285_interrange_gap_ceiling.py:505
        ranges_are_row_identical(off["rows"], "tight", interval(off["rows"], "tight"))
        parameter = hull,  argument = interval(off["rows"], "tight")

That label describes what the *fold* does. It does not say whether `interval` reads module state,
reads the tree, or merely moves its parameters around. This study reproduces the refusal by hand:
inline the callee one level with its parameters bound to the arguments the site passes, and see
what the body turns out to be.

**Method.** For every arm E533 published open (4), mark whether E533 refused it over repo source
(1). For that arm, resolve the callee (the site's own module first, then a repo-wide unique match),
classify the body by reading it — parameters only / module state (named) / tree read (named) /
another repo call (named) — then bind the parameters and run the body under a literal interpreter
(constants, containers, subscripts, arithmetic, comparisons, if/for/return/continue/break, a fixed
builtin set, and repo functions whose own body is a supported chain, to four hops). A statement or
expression kind outside the whitelist stops the run and is published with its name. Nothing in the
repository is executed; the tree is read as text.

**Readings.**

| field | reading |
| --- | --- |
| arms in parent | 4 (1 refused over repo source, 3 out of population) |
| `interval` body class | `the_body_only_moves_its_parameters_around` (no module state, no tree read) |
| the site's argument `off['rows']` | `the_site_s_argument_is_a_literal_once_its_binding_is_folded` |
| item stores between binding (503) and site (505) | 1 — line 504 `off['rows'][1]['tight'] = _td(0.9, 1.2)` |
| inlined value | `{'lo': 1.0, 'hi': 1.1, 'spread': 0.1, 'n_rows_with_interval': 2}` |
| arm outcome | closed — the inlined body runs on a literal argument |
| refusal attribution | `the_refusal_was_about_the_site_s_own_arguments` |

**Verdict.**
`every_repo_source_refusal_was_about_the_site_s_own_arguments_rather_than_the_callee`

**What it means.** The one refusal E533 published as "the callee is not a pure chain of literals"
was not about the callee at all: `interval` reads nothing but its two parameters. The obstruction
was the site's own argument — `off["rows"]` is a subscript of a name bound from a repo call, which
E533's fold would not open. Following that one binding (`off = _fixture_arm()` at line 503) makes
the whole argument literal and the inlined body runs to a concrete hull. So the population "arms
refused over repo source" is not homogeneous, and on the one member available it is entirely a
statement about the fold's caution.

**Two limits published on the face, not in a footnote.**

1. **The folded value is the unmutated container's.** Line 504 stores into the very key the hull
   reads (`off["rows"][1]["tight"] = _td(0.9, 1.2)`) between the binding and the site, so the hull
   the assertion at 505 actually consumes has `lo = 0.9`, not the folded `1.0`. The store is
   published per row and the value is labelled; "the arm is closed" must not be read as "the value
   at the site is reproduced". That gap is the next card (E544).
2. **A call inside the callee is not impurity.** `_fixture_arm` calls `_td`, which first made it
   class `the_body_calls_another_repo_function` and read as if it were state. Whether a repo call
   is followable is decided by running it, not by its name; the body class names what the body
   reads, and the interpreter decides what it can fold.

**Instrument lessons.**
- `ast.Name` loads must exclude builtins (`float`, `min`, `max`) before they can be called "module
  state"; without that, every pure function that uses a builtin was classified as reading state.
- Top-level function names must be their own class (`repo_call`), not folded into "module state":
  otherwise a two-line helper like `_td` turns every caller into an impure body.
- Depth counting doubles per call level (expression → call → argument), so a two-row dict literal
  needs a much higher cap than it looks: the first version refused at depth 4 with
  `expression_nested_deeper_than_the_interpreter_follows` on a body that had three levels.

**Wiring.** `scripts/e536_inlined_fold.py` (build / check / verify / selftest 12 arms), S6 leg
`inlined_fold`, smoke leg `# E536`, card E536 in `knowledge/METHODOLOGY_ASSETS.md`, face
`results/state_tilt/INLINEDFOLD-2026-11-08.json` + `inlinedfold_latest.json`. Pool: E536 → done,
E544 (replay the store) and E545 (re-read E533's other three arms with this resolver) seeded.