## E195 Turnover you can only shrink by giving up alpha is not a cost problem -- measure the structural floor first (2026-10-29 r1139 bm-a; numbered E195 because E194 was already taken on origin by bm-c r1330)

WHEN: a face reports that a sleeve only clears at unrealistically low friction, and the
obvious next move is "add a no-trade band and cut turnover".

WRONG: add the band, see turnover drop 5-11%, see the headline wobble, and call it
inconclusive -- or worse, tune the band until some reading turns positive. A band can only
touch the RE-SIZING part of turnover; if the turnover is dominated by entries, exits and
sign flips, the band is measuring its own ceiling, not the problem.

RIGHT: measure the structural floor before crediting any band. Apply an effectively
infinite band (all re-sizing damped), take the turnover that survives, and publish its
share of the total. Then charge every band the full cost ladder on the SAME weights and
publish BOTH sides of the trade: turnover removed AND gross return given up, plus the
breakeven per band. Live reading (ETF book x futures sleeve, f=0.33, 1649 bars to
2026-10-28): the structural floor is 91.9% of turnover for tsmom60 and 86.2% for tsmom120,
so the widest band can cut at most 6.9% / 10.9% -- while giving up 0.41-0.94pp of gross.
The breakeven does not improve; it gets worse (120d 3bp -> 1bp, and the 0.10 band has no
positive cost level at all). Verdict: a band is a two-sided loss here, and the friction
lives in the signal's flip rate, not in rebalance discipline.

GOTCHA: entries/exits/sign flips MUST stay structural in the band implementation, otherwise
the band silently trades participation for turnover and the "cheaper" sleeve is just a
smaller sleeve. Pin it with a selftest leg (a wide band must not block a sign flip or an
exit) and a leg that verifies the band's claimed cut never exceeds the measured re-sizing
share. Also pin that cost does not change the decisions a band leaves -- otherwise the
levels describe different strategies again (E193's sibling).
||||||| parent of e10dc77a02 (round 1331: grade the carrier label by when it is knowable -- the drop family's month is flaggable at close, never predictable)

## E196 Grade a label by WHEN it is knowable, and never pool nested eras (2026-10-29 r1331 bm-c; numbered E196 because E195 was already taken on origin by bm-a r1139)
WHY
---
"The verdict rests on one month" is only actionable if the month can be named before the
verdict is quoted. E190 published the carrier month but not whether that month was
predictable, so the family was stuck between "quotable with a caveat" and "not quotable".
Three classes of label decide it, and they are not interchangeable: scheduled years ahead
(calendar), observable at the month's close (a realised magnitude), and only visible in
the gap itself (hindsight).
READING (four flagged cells, three distinct carrier months, E186 table re-read)
  calendar {6,7,12,1} : 3/3 distinct carriers inside -> p=0.037 under a uniform draw
  window |gap| ratio  : 2.39x, p=0.0022 pooled / 0.0048 dedup / 0.031 disjoint
  per-cell p<=0.10    : 2 of 4
  month-close selector: top-k |full_ret| kills all four reversals at k=2, but
                        Spearman(|full_ret|,|gap|)=0.68, r2=0.47 -> a proxy, not a mechanism
Verdict: review_window_suggestive + month_close_rule_holds_at_k2 (not "established").
RULES
-----
1. Grade the label by when it is knowable. A scheduled calendar and a month-close
   magnitude answer different questions ("could anyone have called it" vs "can it be
   flagged now"); publishing one number for both overstates the strongest of the two.
2. Deduplicating by carrier month is not independence. A "full" era literally contains
   its own sub-eras, so the pooled test counts the same months twice (published n_months
   makes that visible); the gate must read the disjoint subset and the pooled p may stay
   on the face only as a disclosure of how much strength came from nesting.
3. Any selector built on a column that shares variance with the target must publish the
   correlation and r2 beside its hit rate. A 4/4 hit at 0.47 r2 is half a mechanism.
4. A live rule and a hindsight trim are separate experiments: in one cell the largest
   |book return| month and the largest |gap| month are different months, so a rule that
   works on the gap is not a rule anyone could have run.
5. The permutation null keeps the cell's own gap multiset and shuffles only the labels,
   so a cell with one giant month cannot pass by having giant months; publish n_inside /
   n_outside so an empty bucket cannot read as agreement.
Pos: scripts/e39_panel_census.py (selftest 670->682, mode tilt3ladderdropcarrier) +
results/e43_tilt_4member/LADDERDROPCARRIER-20261027.json +
research/digests/DIGEST-20261029-e195-carrier-identifiability.md.

