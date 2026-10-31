# DIGEST 2026-11-01 r1350 bm-b -- E330: which decision between two references no assertion names

**Study:** `E330_unpinned_choice` · face `results/state_tilt/UNPINNEDCHOICE-2026-11-01.json`
**Card:** `E330-WHICH-FALLBACK-IS-UNCOVERED` (seeded by r1349 at E329 close, burned in-round)
**Verdict:** `an_unpinned_decision_would_return_a_different_cut_if_the_order_were_swapped_today`

## What was asked

E329 found exactly one resolver whose order decides which cut a reader gets (e242's `_face_file`:
`*_latest` first, a pinned 2026-10-29 second) and no leg covering that order. The card widened it to a
mechanical census: across the tree, which constructs pick between two references to one family -- the
order of an existence chain, an `or` whose left side can be empty, an argparse default naming a face,
a mutable default argument -- and for each, is the pick asserted anywhere, and what would a two-line
change silently alter?

## What was measured

2,284 sources / 646k code lines. **One** decision: e242's chain. Zero argparse defaults name a face
(39 `add_argument` lines, all numeric or plain paths); zero functions carry a mutable default; zero
`or` fallbacks survive the two-branch test.

That last zero is the interesting one. 35 lines offer an `or` beside a face; 34 carry the face on one
side only, i.e. `os.path.join(outdir or OUTDIR, "x_latest.json")`, which is a value default rather
than a choice between two vintages. The 35th class of case (e260's `_try_load(...) or _try_load(...)`)
puts its two faces on different lines and is out of the single-line population. Both cuts are
published instead of being quietly dropped.

## What a two-line change costs today

Per call-site stem, not as an aggregate:

| stem | pointer holds | pinned fallback | newest on disk | swap changes today |
|---|---|---|---|---|
| AGGATT | 2026-10-29 | 2026-10-29 | 2026-10-29 | no |
| owncross | 2026-10-30 | 2026-10-29 | 2026-10-30 | **yes** |
| sharediff | 2026-10-30 | 2026-10-29 | 2026-10-30 | **yes** |
| per_member_gamma | 2026-10-30 | (cut absent) | 2026-10-30 | no -- the fallback returns None |

So the exposure is live for two stems: swap the two candidates and the reader gets 2026-10-29 where
today it gets 2026-10-30, with every leg still green. Nothing serves a stale cut today (the pointer
exists and is current), which is why this reads as an unpinned decision rather than an active bug.

## Three rules, each earned by a bug in this script

1. **Mask the quoted spans before looking for an operator.** A face handle is inside quotes by
   construction, so grepping the raw line makes a scanner's own test input look like code: e329's
   `handles_in_line('for cand in (...)')` line was counted as a second fallback chain. Blanking
   quoted spans at unchanged length keeps every offset usable for both the mask and the raw line.
2. **`or` needs a face on each side.** Otherwise every `join(a or b, "..._latest.json")` becomes a
   decision. The rejected count (34) belongs in the face, because a silent cut and a clean corpus
   print the same zero.
3. **A chain is one decision but many stems.** The first draft set `outcome_today` from one stem and
   `swap_changes_today` from another (r1234 name-law). The face now publishes `per_stem` and derives
   the row-level reading from the first stem where the branches disagree.

Also measured: a pin must be named by an assertion in the source's own selftest region or in the
chain/smoke files -- a copy of the resolver's name in another study's fixture asserts nothing -- and a
mention inside a comment is not an assertion.

## Wiring

- `scripts/e330_unpinned_choice.py` -- `run` / `verify` (problems=[]) / `selftest` 30/30
- `results/state_tilt/UNPINNEDCHOICE-2026-11-01.json` + `unpinnedchoice_latest.json`
- S6 leg `unpinned_choice` (~40s, corpus scan)
- smoke leg "product: every two-reference decision in the tree is counted, and the ones no assertion
  names are separated from the ones whose branches already disagree" (executed standalone: PASS)
- card E330 in `knowledge/METHODOLOGY_ASSETS.md`

## Not run, stated plainly

The full 330+ leg smoke suite was not re-run this window (~35 min); the new smoke leg was exec'd out
of `smoke_test.py` standalone. GPU untouched (parked, C-20261014-01); no cloud; nothing deleted; no
quarantine action.

## Next

E331: a pointer without a fallback is a reader that returns nothing in a tree where the pointer is
absent -- count pointer-only readers and whether a `None` is handled (explicit branch, raise, or a
silent attribute access).