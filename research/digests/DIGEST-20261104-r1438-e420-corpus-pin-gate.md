# DIGEST-20261104-r1438 -- E420: the corpus pin is not an equality gate

**Machine** bm-b · **round** r1438 · **subject** `results/state_tilt/PININSTABILITY-2026-11-04.json`
**card** E420 · **pits** `knowledge/METHODOLOGY_ASSETS.md` §E420

## The red that would not heal

r1437 re-ran seven producers and reported `verify problems=[]` for each, but did not re-run the
suite, so the seven `published summary does not re-derive` legs were left unproven. This round
re-ran the suite: the count came back 318/319 with one red, and the red was not one of the seven.
It was E387's consumer leg:

> `siblingentry_latest.json is not published at the re-derived number (corpus_source.pin_id)`

## What the field actually is

The E387 audit re-runs each covered face's producer and records the result as `fresh_today`. The
leg then required the face *on disk* to still equal that record. For `siblingentry_latest.json` the
recorded field is `corpus_source.pin_id` = `e361.stamp(e326.corpus())`, a sha256 over every in-repo
python source, written by the face's own producer. Measured vintages for that one face in one day:

| source | pin | members |
|---|---|---|
| carried at head | `da2a…` | 2467 |
| the audit's re-derivation | `5d53…` | 2491 |
| the face on disk (16:15) | `c5df…` | 2479 |
| the corpus now (after this round's new script) | `95c8…` | 2492 |

So the number the leg pins is moved by the very act that keeps the face honest, and by every round
that adds a script. It cannot be equal tomorrow.

## What was measured, and what it corrected in the first draft

The first hypothesis -- "only the fingerprint moves" -- was wrong. Two of four rows carry moved
**numbers** as well (`summary.sources_read`, `summary.sources_where_the_readings_differ`, and nine
census populations). Those numbers were *lower* on disk than the audit's re-derivation: the faces
had been built against a corpus of 2479 while the audit re-derived at 2491. They were genuinely
stale by one rebuild.

Republishing both producers (`e335` -> 2492 sources, `e364` census) moved every flagged number
**up**, and nothing moved down:

| face | moved fields | went down | verdict moved | agrees with its own pin |
|---|---|---|---|---|
| `siblingentry_latest.json` | 3 | 0 | no | yes |
| `UNSTAMPEDCENSUS-2026-11-02.json` | 9 | 0 | no | — |

## The replacement assertion

Stasis is not the invariant. In `smoke_test.py` the E387 leg now reds on, and only on:

1. a **verdict** that moved since the audit,
2. a published **number that went down** (a silent revert),
3. a face naming a **pin file that disagrees with it** (checked by E420's `_self_agreement`),
4. plus everything `e387.verify()` already re-derives, and `frozen_legs_edited == 0`.

This is a weaker check than byte-equality and is disclosed as such. It is not weaker where it
matters: a face cannot be rebuilt from a *smaller* corpus, cannot flip its verdict, and cannot name
a pin it does not match.

## Pits

1. `int(summary.get(k) or -1)` reds on a legitimate `0`. My first selftest did exactly that; the
   fix was a `_count()` that tests key presence.
2. A verdict must be recomputed from the split, not written from the story: the first published
   verdict here ("unsatisfiable, so a red row is a defect") was contradicted by its own rows.
3. `_self_agreement()` resolving `results/state_tilt` from the repo root made its own fixture test
   fail under `chdir`; a helper used by a test needs its base as a parameter.

## Product

`scripts/e420_corpus_pin_instability.py` (run / verify problems=[] / selftest 10/10) ·
`results/state_tilt/PININSTABILITY-2026-11-04.json` + `pininstability_latest.json` ·
smoke leg `# E420 (r1438 bm-b)` · narrowed E387 leg · republished `siblingentry` and
`UNSTAMPEDCENSUS` · card E420.