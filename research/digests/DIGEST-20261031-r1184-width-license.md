# DIGEST 2026-10-31 r1184 bm-a -- the width's licence reaches the faces a reader holds

**Subject.** r1183 taught the production card to print `Family coherence: ONE_WORLD -- all 10 width
arms priced a1a42aee64453839 (cutoff 2026-10-30)`. The executable sheet (`ORDER-*.md`) and the CEO
page (`docs/live_book/LIVE-BOOK-*.md`) quote the same width family and printed none of it.

**Why it mattered.** Both pages are read as "this width was measured". The card was the only face that
said which panel the family's ten verdicts were priced on, so on the other two a measured width and a
configured one were textually identical. That is the r1108 "produced but unread" family, one level out:
the verdict existed and had a consumer -- the consumer that matters (the sheet in the operator's hand)
did not.

**What changed.**
- `scripts/etf_book_order.py`: thin reader over `etf_book_production.family_coherence()` (single
  implementation, E289), quoted in the ticket payload and on both order documents (5-name ticket and
  12-name card-config ticket). Two new selftest legs (46g/46h) prove the three render states differ.
- `scripts/etf_book_ceo_page.py`: same reader, carried in the page payload, rendered as
  "这张表里的名数，是不是有实测撑腰" with three mutually exclusive readings (有。/没有。/不知道。).
  Three new selftest legs (L54-L56), fixture = the LIVE page with one field swapped.
- `smoke_test.py`: one leg recomputing the verdict from `results/etf_book_phase_atlas_arms.json` and
  requiring card + ticket + page to agree, arm count included; plus the falsifiability probes (missing
  family is not a verdict; a MIXED fixture must read `priced_same_panel=False`).

**Live readings.** arms 10, verdict ONE_WORLD, panel `a1a42aee64453839`, cutoff 2026-10-30.

**Red healed on the way in.** The inherited tree failed `product: E271 the width ruler reaches both
order documents` (want +0.12pp present in both sheets: beta=False card=False) -- the previous window
moved the ruler face but did not re-render the two ORDER documents. Regenerating them (ticket + card
ticket) turned it green without touching the assertion.

**Honest gaps.** (1) The new sentence exists only on bm-a's writer face (the CEO page is single-writer
bm-a); bm-b/bm-c have no same-named face to print it on. (2) "All three faces priced the same DAY" is
still only enforced pairwise through the card-agreement block -- the page does not print its own
`priced_bar` beside the family cutoff. (3) The supply floor stays red by choice: the only launchable
unit would re-burn, on the same panel, the family burned at 04:42.
