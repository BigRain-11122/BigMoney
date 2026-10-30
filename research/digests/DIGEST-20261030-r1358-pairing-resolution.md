# r1358 — the ruler now publishes what it could have seen, not only what it saw

**Ask.** r1357 put the live-width ruler on the second order document and taught each sheet which
face of the pair it is. The number it prints is a **paired** statistic over 20 decision origins of
one R20 cycle: median +0.09pp, per-phase sd 1.255pp, 10 up / 10 down. Every face in this family
then says "inside the engine disagreement", which reads to an operator as "the two widths are
equivalent".

**The defect.** Those are two different sentences. With 20 pairs and sd 1.255pp the smallest
paired difference this design could detect at 80% power (two-sided 5%, z=2.802) is

    2.802 * 1.255 / sqrt(20) = 0.786pp

The measured gap is 0.09pp = **11% of the floor**. So "the widths do not differ" and "this pairing
cannot tell them apart" produce the same headline, and only the second one is supported — the
first is the one an operator would act on.

**Fix.** The resolution is published beside the gap and re-derived at every consumer from the
numbers the face already carries (z is frozen in `LIVE_RULE`, the sd and phase count come off the
face). Nothing reads a stored `mde`: a number that can be edited independently of the numbers that
produce it is a receipt (r1266). Both order sheets print the floor and the ratio; a face that
publishes no dispersion says so instead of printing 0.00.

**What a reader now learns.** The 20-phase pairing cannot resolve anything under ~0.79pp, so
card-vs-ticket is answerable only as a volatility-budget choice (the +0.09pp median is 4.4% of the
engines' own 2.045pp disagreement) and never as a return difference — and any future arm must reach
~0.79pp before this ruler may call it separated.

**Verified.** arms selftest 88→**91 legs 0 failed** (floor = z*sd/sqrt(n) from the fixture's own
numbers; a sub-floor fixture reads unreadable, a point above the same floor reads readable);
`etf_book_order.py --selftest` 56→**59/59** (floor re-derived with a poisoned stored mde in the
face; the wide-dispersion fixture flips below_own_resolution; a face with no dispersion prints the
absence, not a zero); `--live-widths-check` green on cutoff 2026-10-29; both sheets regenerated and
carry the same floor string; smoke leg **E272** recomputes the floor from the face's sd and
requires it on both documents.

Card: **E272**.