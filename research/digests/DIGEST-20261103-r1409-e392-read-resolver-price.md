# Digest r1409 -- E392: the bound E391 published, priced

Face: `results/state_tilt/READRESOLVE-2026-11-03.json` (+ `readresolve_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E392. Study: `scripts/e392_read_resolve.py`.

## What was asked

E391 published 132,604 in-repo literal sites that name one of the 3,877 field-shaped keys carrying
two structural meanings, and named the figure honestly in the field itself:
`read_bound_is_name_matched_not_face_resolved`. A bound is not something a reader can act on, so
this round prices it: for each read, follow the container through E390's resolver to the face the
expression actually builds, then open that face and ask whether it stores the key.

## What it measured

| arm | count | share of the name-matched bound |
|---|---|---|
| literal sites naming a conflicted key (all uses) | 399,668 | -- |
| **name-matched reads** (subscript / getter, never a write) | **112,910** | 100% |
| reads whose container the resolver can call a face | 25,461 | 22.5% |
| ...that reach a face path | 9,243 | 8.2% |
| **...that open a face that stores the key** | **5,763** | **5.1%** |
| ...that open a face *without* the key (phantom) | 188 | 0.17% |
| ...that land on a face the check cannot read | 3,292 | 2.9% |

Of the reads that are demonstrably on a face container, 22.6% store the key -- the honest
denominator for anyone who wants a rate rather than a bound.

The remaining 87,449 name-matched reads are published, not dropped: 22,712 read a local dict (a
construct, e.g. `per_face[f]["cap"]`), 64,730 cannot be typed (a function parameter, a loop over an
untyped value), 15,357 build a path the resolver refuses (`%`-format, glob), 856 match more than one
face.

## The two things this round refuses to flatter

**(1) The unreadable bucket is where the biggest faces live.** 3,271 of the 3,292 land on a face
above the 1 MB read cap and 21 on a face that does not parse. Those are exactly the aggregate faces
(`runnable_pool.json`, the wide panels) a reader is most likely to be talking about, so the check is
blind precisely where the stakes are highest. Published per reason, not folded into "unresolved".

**(2) The small-site slice is worse than the aggregate.** 711 keys are named by at most three reads
-- the ones a reader could actually go and verify by hand. Only 29 of them have a read that opens a
face storing the key (4.1%), against 5.1% overall: the keys that look most actionable are the most
likely to be a name that no site opens.

Reconciliation: reads + writes = 132,617 against E391's published 132,604, i.e. the two censuses see
the same corpus (gap -13, sites the tree gained E391's text prefilter misses). This required switching the site
walk to `e391.py_corpus`, which excludes `.codely-cli/` and `_smoke/`; on E390's wider walk the gap
was 125 and would have been an unexplained artefact.

## Verdict

`some_name_matched_reads_open_a_face_that_stores_the_key_and_the_remainder_are_published_as_phantom_unresolved_or_ambiguous`

Wiring: `scripts/e392_read_resolve.py` (run / verify problems=[] / selftest 23/23); smoke leg E392
(1/1, exec'd verbatim by `scripts/run_e392_smoke_leg.py`); S6 leg `read_resolve`. Successor: E393
(does the 1 MB read cap hide the faces the storing count is blind to -- re-price the 3,271 with a
streaming read before the 5.1% is quoted as a ceiling).