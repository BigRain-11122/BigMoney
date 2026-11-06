# E458 -- does a face a study writes say which study it is (r1482 bm-b)

**Question.** E451 measured that no study publishes a digest of the prereg note it names, and that the
note is reachable only through prose freeze strings. That presupposes an earlier capability: a
consumer holding a face must be able to tell *which* study it belongs to without opening the producer.
Ask every face a study producer writes whether its payload carries a machine-readable identity -- a
card id (`E4xx`), a study id (`XXX-P1`), or a prereg note path -- in a field a reader can key on, in
which field, and whether that identity resolves to a file or a pool card that exists.

**Answer.** 538 faces under `results/` graded by producer-first attribution against the 12,130-source
corpus.

| class | faces |
|---|---|
| carries a machine-readable identity | 526 |
| identity appears only inside prose fields | 2 |
| carries no study/card/prereg identity at all | 10 |
| unreadable | 0 |

0 declarations fail to resolve. 6 faces carry a declaration that does not resolve to a file or a pool
card; those are published per row and are not folded into the tally.

**What the twelve are.** 10 no-identity rows are 6 distinct studies (`BANDDONORCHOICE`, `BANDFLOOR`,
`BANDSCREENBUDGET`, `CORPUSPIN`, `FACEVINTAGE`, and `unreadstatus_latest`, which has no dated twin) --
five of the ten are the same studies' dated `_latest` twins, so a study-level count is 6. The 2
prose-only rows are `BANDSTRADDLESWEEP`'s dated and `_latest` faces, which name their card twice
inside `summary.hits`: the id is parseable, the field is prose, and a frozen field-name vocabulary
therefore refuses to call it a key. Folding the two classes together would have printed 528 and hidden
the shape E451 is about.

**Why prose is a separate class.** "We saw E451 in the title string" and "the payload has a field a
reader can key on" are different answers to a question about identities a consumer can act on. The
line between them is a rule (an identity-named field), not an opinion about the sentence -- and it is
the rule that produced both the 2 and the 5,466 discounted substring mentions.

**Three rules this cost.**

1. **Population comes from producers, never from a hand list.** A face belongs to a producer when the
   producer's source carries the face name -- the `FACE_NAME` constant, the `DATED_PREFIX` template,
   or the dated sibling -- with both sides normalised (lowercase, drop `.json`, drop a trailing date,
   drop `_latest`). That is why `importclass_latest.json` and `IMPORTCLASS-2026-11-04.json` are graded
   as one study's two files rather than as one file and one stranger.
2. **A mention of another study is not this face's identity.** A study id inside a long value (a face
   path in somebody else's row, a script name) is a quotation. 5,466 such substring mentions on 390
   faces are discounted and sampled in the face, so the classifier change is a measurement and not a
   silent rewrite; a partial match only counts when the field itself is named like an identity.
3. **The unattributed residue is published, not zeroed.** 39 faces under `results/state_tilt` that no
   `scripts/eNNN_*.py` names sit outside the graded population; they are reported as a count with
   samples, never as carrying or lacking an identity.

**Wiring.** `scripts/e458_face_identity.py` (`run` rc0, `check` clean, `selftest` 24/24); faces
`results/state_tilt/faceidentity_latest.json` + `FACEIDENTITY-2026-11-06.json`; S6 leg `face_identity`
(re-derives the tallies and re-resolves every published declaration against the live tree, 0.06 s);
smoke leg `e458 does a study face declare a machine-readable identity (r1482 bm-b)` +
`scripts/run_e458_smoke_leg.py` (standalone 1/1; the leg reds on a doctored copy that promotes a
no-identity row into the machine-readable class); card `knowledge/METHODOLOGY_ASSETS.md` E458.