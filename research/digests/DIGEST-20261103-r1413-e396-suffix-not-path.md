# DIGEST 2026-11-03 r1413 (bm-b) — E396: the one same-document pair is a suffix match, not a path match

Study: `E396_last_tick` (`scripts/e396_last_tick.py`, selftest 25/25, verify problems=[])
Face: `results/state_tilt/LASTTICK-2026-11-03.json` + `lasttick_latest.json`
Upstream: E395 `conditionalwrite_latest.json` (39 pairs / 131 reads / 31 keys / 22 faces)
Sibling: `E396_face_basename_suffix` (`scripts/e396_face_basename_suffix.py`, selftest 13/13)
Face: `results/state_tilt/FACENAMESUFFIX-2026-11-03.json` + `facenamesuffix_latest.json`

## What was measured

E395 published exactly one pair in which a producer writes the key *unconditionally into this very
face*: `logs/iteration-loop/state.json` / `last_tick`, written at module level by
`results/_r128bmc_resolve_storm.py:37`. E395 called it an anomaly and left three honest explanations
a reader can tell apart. E396 prices all three instead of believing the cheapest.

| reading | result |
| --- | --- |
| (a) schema regression | the path's own history is available (14 revisions sampled, 14 readable); 0 of them carry the key; key-set difference across the boundary is empty (0 only_before / 0 only_after) — nothing was dropped |
| (b) dump target | the literal target is `results/autofill_state.json`; the face basename `state.json` is a proper **suffix** of it |
| (c) read site | `Tools/_r201_wrap.py:67` reads `last_tick` as a **fallback** (`.get("last_tick", …)` behind an `af` first choice) and does not name this face |
| exact-test re-derivation | 1 same-document pair moves, **0 still hold** |

## Why the pair existed

The dump test that produced the claim was `face_basename in value` over the dump's target string — a
substring test. `state.json` is a suffix of `autofill_state.json`, so every dump of the longer name
counted as a hit for the shorter face. Over E395's own 22-face population there is exactly one such
collision (`state.json` ⊂ `autofill_state.json`, owned by `logs/iteration-loop/state.json` and
`state.json`). Re-running every same-document claim as an exact-basename test leaves none standing.

The sibling study re-resolves the same pair with a *path-segment* matcher and A/Bs E395's own walk:
identical population, 39 pairs in both arms, exactly 1 pair moves, and under the segment arm **no**
pair claims a same-document write — so all 20 unconditional pairs write another document. The
witness producer dumps four documents (`autofill_state`, `compute_audit`, `regime_state`,
`token_usage`) and never mentions the face path it was credited with; its fifth dump call carries no
path-shaped literal and is classified `unresolved` rather than `another_file`.

Tree-wide exposure from the same study: 18,342 faces / 13,999 distinct basenames / **2,253
basename-suffix pairs** over 133 distinct short basenames, plus 183 same-basename-different-directory
groups. That is published as exposure — the idiom is available in 2,253 places — not as 2,253 proven
misreads.

## What a reader should take

1. **A substring test on a basename credits the wrong face, and the wrong reading is the alarming
   one.** The claim reads as a defect ("this face should store the key and does not"), while the truth
   is that the writer never opened that document.
2. **One pair is not a class — and the class size decides whether to edit the classifier.** The blast
   radius is one, so the defect is published and E395's classifier is left unedited (E396 reports the
   defect where it can be measured instead of patching it away).
3. **A boolean that ORs two sources cannot answer a history question.**
   `face_ever_carried_the_key` is `bool(ever) or bool(in_tree_writers)`; here it is `True` while
   `carried_in_the_sampled_revisions` is `False` (the only in-tree writer is
   `Tools/_r201_wrap.py:51`). Read as "the history carried it, then someone dropped it", the flag
   states the opposite of the 14 sampled revisions. The two terms are published separately.
4. **A probe that stops at a cap is a window, not a history.** The sibling inspects 40 of the 390
   revisions touching this path (`capped: true`, `revisions_carrying_the_key: 0`,
   `never_present_in_the_inspected_window: true`). Both studies agree the key is absent from every
   revision looked at; neither claims it was never there.

Verdicts: `the_same_document_claim_is_a_suffix_match_not_a_path_match` (LASTTICK) and
`the_one_unconditional_same_document_pair_is_a_basename_substring_artifact_so_all_20_unconditional_pairs_write_another_document`
(FACENAMESUFFIX).

Verdict: `the_same_document_claim_is_a_suffix_match_not_a_path_match`.