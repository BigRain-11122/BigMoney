## E337 -- executing a named floor: a before/after diff over a corpus-derived face bills corpus growth to the change, so rebuild the old arm as a control over today's corpus

Round r1357 (bm-b). Pool card `E337-TAKE-THE-FLOOR-AND-OPT-IN-ONE`, seeded by r1356 at E336's close. E336 refused
to rank the six consumers but published a floor -- `E330_unpinned_choice` cheapest on both readings (0 delta
numbers, 1 published number) with its verdict intact -- and a recommendation that names a floor is not a
measurement of the opt-in. This round executed it.

**What moved.** `scripts/e330_unpinned_choice.py` now reads `e326.code_lines_tokenized` through one **local**
accessor (`_lines`); `e329._code_lines` and every other reader of it keep the shipped reading, so the switch is one
file wide by construction. Reverting is atomic: a moved verdict or a failed re-derivation restores the source bytes
and the archived pre-switch face, and `verify` additionally asserts that the source on disk is in the state the
published verdict claims.

**The diff a reader would have accepted is wrong.** A bare before/after comparison shows one number moving --
`sources_scanned` 2292 -> 2297 -- and that number is not the opt-in. E330's population is `e326.corpus()` (every
`.py` under scripts/Tools/live/monitor/firm), so any script that lands after a face is written moves it by one,
including the study doing the work. Three arms over ONE file list, published separately:

| arm | reading | numbers moved |
| --- | --- | --- |
| drift | published-before -> shipped control on today's corpus | 1 of 21 (`sources_scanned` +5) |
| total | published-before -> republished | 1 of 21 |
| **switch** | control -> republished | **0 of 21, 0 of 1 decision row** |

The verdict is unchanged on both arms (`an_unpinned_decision_would_return_a_different_cut_if_the_order_were_swapped_today`),
so the opt-in is in. The E336 "1 published number" it was named on was the same corpus artifact -- reading B looked
non-zero for the cheapest consumer in the set for a reason that had nothing to do with the reading.

**Two guards repaired, not relaxed.** (a) E335's inertness scan counted *mentions* as *consumers*: E336 holds the
name in a string constant, so the landing had been red before this round touched anything (`2 consumer(s) read the
new name`, both phantom). Masking quoted spans on tokenized code lines (E330's `code_mask` over
`e332.true_lines`) splits the population into **1 reader + 1 mention**, and a real opt-in is published as a new
frozen verdict `V_OPTIN` whose allowance comes from an allowlist read out of this study's published face -- a study
cannot award itself an allowance, and a reader outside it still fails `V_DIRTY`. (b) "Inert" is a state, not a
property: a guard that hard-codes "nothing moved" either goes red when something legitimately moves or gets
quietly loosened; publishing the transition is the only honest third option.

**A republish is a cascade, and it is counted rather than claimed.** E330's published face is an input to 2 direct
studies (E333, E334) and 2 one import hop away (E335, and E336 which reaches it through E334's registry -- exactly
the study that named the floor). E336's per-consumer reading could not see this by construction: it compared one
face at a time. The measured price of an opt-in is the transitive set of faces that rebuild it, plus the
corpus-inflation of landing the `.py` that does the work; hence the `green_window` limit on the face instead of a
permanence claim.

Three reusable rules. (1) **A change measured against a corpus-derived face needs a control arm rebuilt on today's
corpus**, or drift, total and the change under test are one number. (2) **A name-based guard cannot tell a mention
from a read** -- mask literals on tokenized code lines before counting, or it reports phantom consumers. (3)
**Executing a recommendation debts the faces that consume the executed one**; count that debt explicitly instead
of meeting it as red legs.

Follow-ups queued (not claimed here): republish E333/E334/E336 over today's corpus so their legs re-derive against
the republished face (their red is pre-existing corpus drift, widened by the one `.py` this round landed).

Evidence: scripts/e337_optin_executed.py (selftest 18/18, verify 0 problems) -> results/state_tilt/OPTINSWITCH-2026-11-01.json (+ `OPTINSWITCH-before-UNPINNEDCHOICE-2026-11-01.json`) -> scripts/e335_sibling_entry_point.py (selftest 24/24, verify 0 problems, `V_OPTIN`) -> Tools/s6_chain_bmb.py leg `optin_executed` -> smoke_test.py leg E337 -> card E337 in knowledge/METHODOLOGY_ASSETS.md