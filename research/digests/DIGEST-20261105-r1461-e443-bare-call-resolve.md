# DIGEST 2026-11-05 r1461 (bm-b) -- E443: the 707 "ambiguous" bare calls bind to the caller's own definition

**Question.** E440 published 707 call rows as *bare calls to a name more than one module defines* and
stopped there. A name index knows who defines a word; it cannot know which definition a call reaches.
Which of those 707 rows actually bind to a foreign module's wrapper?

**Method.** For every one of the 707 rows, read the caller file's own AST bindings: `from X import name`
(with `as`), `from X import *`, the caller's own top-level `def`, and `from pkg import submodule` when
`pkg/submodule.py` exists (treated as a module binding, not a function definition). A row resolves to
`the_callers_own_definition`, `one_defining_module`, `more_than_one_defining_module`,
`a_module_that_does_not_define_it`, `a_star_import`, or `no_defining_module`. The population is E440's
own scan re-run live: 3,463 sources, 11 wrappers re-confirmed live, 25,023 dropped rows recomputed,
707 shared rows (`distance_check.agrees = true` against E440's published 707).

**Reading.**

| resolution | rows | share |
|---|---|---|
| `the_callers_own_definition` | **707** | 100.0% |
| `one_defining_module` | 0 | 0.0% |
| `more_than_one_defining_module` | 0 | 0.0% |
| `a_module_that_does_not_define_it` | 0 | 0.0% |
| `a_star_import` | 0 | 0.0% |
| `no_defining_module` | 0 | 0.0% |

Verdict (recomputed by the gate from the rows):
`every_shared_name_call_resolves_once_the_callers_imports_are_read`.

**What the class really is.** A name shadow, not a cross-module hazard. 183 caller files each define
their own helper under the same generic closeout name: `run` 323 rows over 65 files (300 modules define
`run`), `write_json` 184, `write` 91, `write_face` 48, `save` 28, `dump` 21, `_write_csv` 11, `append`
1. 622 rows are production callers, 85 are selftests; the row set compresses to 194 cells.

**The write axis, bounded rather than assumed.** Of the 707 surviving definitions, **0** compose their
directory parameter onto a file path (so a shared name is not hiding a path writer). 322 definitions
could not be resolved from the scan and are published as their own class; of the 385 that resolve, 317
name the directory in a write but compose nothing onto it, 39 do one of each, 29 name it nowhere.

**Instrument notes.**
- A `def` in the caller's own module wins over an import of the same name, and that is the order the
  classifier applies -- checking imports first would have credited these rows to a foreign module.
- `from pkg import submodule` is a module binding when the submodule exists; without that rule a bare
  call to the module's own name is silently credited to a function definition elsewhere.
- `verify` re-derives the whole population (~20 min over 3.4k sources) and is published on demand; the
  S6 chain runs `check`, which re-derives every published tally from the published cells. A guard whose
  only cost is 20 minutes per tick gets switched off -- the leg is the check, not the study.
- The smoke leg is structural: it re-derives the tally, the verdict, the closing sum, that every
  resolved cell names its surviving definition, and it refuses a doctored cell.

**Files.** `scripts/e443_bare_call_resolve.py` (run / verify / check / selftest 16/16),
`results/state_tilt/barecallresolve_latest.json` + `BARECALLRESOLVE-2026-11-04.json`,
S6 leg `bare_call_resolve` (`check`, rc 0), smoke leg in `smoke_test.py`, card E443.