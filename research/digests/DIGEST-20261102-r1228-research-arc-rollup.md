# DIGEST 2026-11-02 r1228 bm-a — a face that refuses to be asked a fourth time

**Round product.** The production card now carries `## What has already been asked about these
numbers`: one row per research case the card's own numbers raised (E25 rebuild, E26 overnight
gap, E27 open slicing), each with its measured state, best arm, best pp/yr and admissible-arm
count, then one derived sentence that says whether the three add up to "no lever". The CEO page
quotes the same roll-up, which is the first time it references E27 at all.

**Why it was needed.** Each answer existed, in its own research file, and neither the card nor
the page ever added them up — so a reader who saw 9.6%/yr beside 8.5%/yr was still invited to
ask a fourth time, and the operator could not tell "not asked" from "asked, did not pay".

**How the roll-up decides.**
- Single implementation in `scripts/etf_book_production.research_exhaustion()`, quoted by
  `scripts/etf_book_ceo_page.research_arc_face()`; the page owns only the Chinese labelling.
- A lever exists iff some face's `admissible_arms` is non-empty (state **names** are printed but
  never used to decide) → `OPEN_LEVER`, naming `CASE:arm`.
- Any unreadable face → `CANNOT_VERIFY`, naming the missing cases: an absent measurement is not
  a negative, exactly as `priced_faces`/`family_coherence` already rule.
- All three read and none carrying an arm → `CLOSED`, and the sentence carries its own boundary:
  "these three do not pay" is not "this book has no other lever".

**Live reading.** `CLOSED`, 3/3 faces, 0 levers, all on evidence cutoff 2026-10-30:
E25 IRRECOVERABLE (+0.07pp, `smooth_k2`), E26 MIXED_ACROSS_PHASES (+0.81pp, `excl_upgap_q80`),
E27 NO_SLICING_EDGE (-0.01pp, `k5`).

**Checks.** production selftest +4 legs (absent faces / three empty asks → CLOSED / one arm →
OPEN_LEVER and the word "closed" never printed / a dropped face reopens the question) and a
card-render leg; ceo_page selftest 111/111 (+L106-L108); smoke 317/317 PASS 0 FAIL with a new
leg that re-derives the verdict from the three published faces and demands each state appear on
the card.

**Disclosure.** The chain doc still calls zt_pool / heat / repo bm-a lanes, while the collectors
themselves refuse on bm-a with "owned by bm-b". Documentation lags the code; the collectors are
the authority, and this round did not move lane ownership.