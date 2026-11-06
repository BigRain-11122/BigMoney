# DIGEST 2026-11-06 r1497 bm-b — E474: identity is a stem in 357 of 502 faces, and a stem is the producer's filename in only 86 of them

Card: `E474-HOW-MANY-FACES-NAME-THEIR-STUDY-AS-A-SCRIPT-STEM-AND-DOES-ANY-READER-NORMALISE-IT`
Face: `results/state_tilt/IDENTITYDIALECTCENSUS-2026-11-06.json` (+ `identitydialectcensus_latest.json`)
Code: `scripts/e474_identity_dialect_census.py` (run / check / verify / selftest 22/22)
S6 leg: `identity_dialect_census` (runs `check`)

## What it measured

Population: every parseable top-level-dict JSON under `results/` that declares a top-level field
whose **name** is in E458's frozen identity vocabulary (502 of the tree's faces). Value dialect is
classified per field; stems are resolved through two channels published apart — the script filename,
and the stem-shaped **literal the producer declares in its own source**.

| dialect | instances |
|---|---|
| path (`results/…/x.json`, `research/PREREG.md`) | 60 |
| producer script stem | 357 |
| other (prose) | 85 |
| card id (`E474`) | **0** |

Stem resolution (357 values):

| channel | count |
|---|---|
| names a shipped script (the filename) | **86** |
| declared as a literal by exactly one source | **213** |
| declared by several sources (ambiguous producer) | 56 |
| nobody anywhere names it | 2 |

Readers: 1,075 sources read an identity-named field; **217 (20.2%)** also carry a normaliser idiom
(`splitext` / `basename` / `norm_stem` / a card regex). The other 858 compare identity verbatim.

## The finding

**The study id is not the script name in 71% of the faces that have one.** 213 of 357 stems resolve
only because a single producer declares the string in its own source; if that declaration moves or
the literal is refactored, the face's identity dangles with no edit to the face. 56 ids are declared
by more than one source, so "which script wrote this" is decided by nothing on disk. Exactly 2 faces
have no edge at all: `results/e43_tilt_4member/PLACEBO-unknown.json`
(`e202_tilt3_ladder_drop_edge_placebo`) and `results/e44_midmonth/SCREENGAPERA-20261022.json`
(`e93_gapsplit_era_spread`).

Second half: **no face in the tree spells its identity as a card id.** Every card number lives in
prose or in a field the vocabulary does not cover, so the card↔stem bridge has no machine-read
implementer, which is consistent with E462's dialect result and with E467's docstring channel being
read by nobody.

## Instrument limits (published in the face)

- the population is top-level keys whose **name** is in the frozen vocabulary; a face spelling its
  identity under an unlisted name is invisible here (the E462 hazard, restated);
- "carries a normaliser" is an idiom co-present in a file that also reads an identity field — not a
  proof the idiom is applied to that value (E470's co-occurrence lesson);
- a stem-shaped value that is a study id and a script name at once cannot be told apart by this
  instrument; the two channels are published separately for exactly that reason.

## Pit caught in-window (the whole finding was one artifact first)

The first burn indexed stems under `scripts/` and `Tools/` only and published **271 dangling** of
357. The real number is 2. Two instrument errors stacked: (a) producers living in `monitor/` and
`firm/` were unindexed, and (b) a study id is often **not** its script's filename
(`e202_tilt3_ladder_drop_edge_placebo` vs whatever script writes it), so "no script with this name"
was being read as "nobody wrote this face". Law: a resolution channel must be tested against a
population where the answer is known to be non-zero before it is used to report absence.