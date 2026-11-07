# DIGEST 2026-11-07 r1534 bm-b -- E505: the "unmeasured" bucket is a naming convention plus a hole

**Question.** E502 (r1531) could not price 183 of 201 studies because the instrument looks for a
literal zero-argument `def corpus()`. That bucket is larger than every priced arm combined, so the
question this round asks is not "what is in it" but "is it a property of the studies or of the
name the instrument looks for".

**Answer.** Neither, entirely: it is 35% a naming convention, 19% a calling convention, 46% a hole.

| class | studies | how it would be read |
| --- | --- | --- |
| zero-arg callable that walks the tree, under another name | 25 | `getattr(mod,'face_files')()` |
| zero-arg callable with a population name, under another name | 24 | `getattr(mod,'census')()` |
| module constant holding the names as literals | 10 | `getattr(mod,'GLOBAL_SOURCES')` |
| module constant computing the names at import | 3 | `getattr(mod,'OWN_FILES')` |
| the corpus arrives through an import | 1 | `from e361_census_corpus_pin import stamp_sources` |
| the only surface needs caller arguments | 35 | no adapter -- the caller supplies it |
| nothing in the module names a population | 82 | no adapter -- there is nothing to read |

Parsed 180 + unreadable 3 = 183 declared. The 3 unreadable rows are themselves BOM-prefixed sources
(`U+FEFF` makes `ast` refuse them): three members of E502's own bucket are unreadable for exactly
the reason E502 was measuring.

**The cross table is the part that prices anything.** Of the 180, 97 never parse source text at all,
so "does a BOM hurt this study" cannot bite them whether or not their corpus is readable; 75 parse
the text as they read it (BOM-fatal) and 8 strip the BOM first. The bucket's size is not its
exposure.

**Four reusable lessons.**
1. An "unmeasured" bucket produced by a name test must be decomposed per study before it is quoted
   again -- a single opaque number (183 > every priced arm combined) reads as "most of the corpus is
   unmeasurable" when a third of it is one `getattr` away.
2. Classification needs a negative-token list first: `SKIP_DIRS` is also a list of strings with a
   `files`-ish name, and without skip/ignore/exclude/deny/block/forbid/ban/black/drop/dead/legacy/tmp
   it is published as a member list.
3. Name the constant class "a list of names the population is built from", not "the member list":
   `PATHS=['scripts','Tools','live']` is a set of roots and `UNIVERSE_KEYS=[...]` is a set of field
   names -- either way it is not a membership list, and a class name that says it is publishes an
   unmeasured claim inside a measurement.
4. Unparseable rows are evidence, not waste: they are published as a list with a reason and counted
   separately (`unreadable_bom_prefixed`), not folded into one "skipped" number.

**Not claimed.** The full smoke suite was not run; the rest of the S6 chain was not re-run; the
adapter strings are suggestions of the cheapest read and do not claim the value equals the study's
corpus (that needs execution). No network, no GPU, nothing deleted.

**Pointers.** `scripts/e505_unmeasured_reach.py` (selftest 32/32) |
`results/state_tilt/UNMEASUREDREACH-2026-11-07.json` (+ `unmeasuredreach_latest.json`) |
`knowledge/METHODOLOGY_ASSETS.md` card E505 | smoke leg `# E505 (r1534 bm-b)` |
S6 leg `unmeasured_reach`.
