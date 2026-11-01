# DIGEST 2026-11-02 r1231 (bm-a) — the page a person opens now answers "how long"

**What was broken.** The duration face existed (r1230 / E346) and nothing stated it to the
operator: the daily page printed "how much" (9.6%) and "how deep" (-11.77%) and no wait at all.
A number nobody reads is indistinguishable from a number nobody computed.

**What this round does.** `scripts/etf_book_ceo_page.py` gains `underwater_face()` (reads
`results/etf_book_underwater.json`, refuses a payload whose verdict no longer recomputes) and
`underwater_block()` (prints it). Selftest 111 -> 114 (L109 live payload number appears on the
page; L110 a censored entry prints "still under water" and never 0 bars; L111 an absent or
drifted face prints "cannot answer" and no arithmetic).

**Readings (all read from the payload, never typed here).** worst entry bought the 2021-09-14
peak -> **351 trading days** to break even (2023-03-02); median 1; p90 15; **10 entries
(0.61%)** still under water at the last bar and reported as such; longest episode **350 bars**
(53/54 healed); forward 1/2/3y worst **-7.51% / -0.02% / +0.78%**, loss share 8.01% / 0.09% / 0.00%.

**Two laws printed on the page, not just obeyed.** (1) a censored entry never reads as 0;
(2) the sample boundary is printed with the claim — "3 years almost never loses" is a property
of a sample that starts 2020-01-03, not a promise.

**Verification.** page selftest 114/114; final-tree full smoke **321/321 PASS 0 FAIL**
(`.codely-cli/tmp/smoke-r1231b.out`), including the new leg that re-derives the number from
`results/etf_book_underwater.json` and demands it plus the censored disclosure and the sample
start appear in the published page.

**Disclosed.** (1) `etf_book_production` runs upstream of `etf_book_underwater` in the chain, so
the card was deliberately NOT given a duration section this round: same-run it could only quote a
one-run-old payload, and the duration face must reproduce the card's own cell to be canonical.
(2) The first smoke of the round was launched before the edits and killed when noticed; the quoted
run is the settled-tree one. (3) r1230's round report said "1y worst -5.51%" while the payload says
-0.075141 (-7.51%) — this round publishes the payload's value and records the transcript error.

**Next.** Decide how the card carries the duration (chain reorder vs disclosed one-run lag).
