"""bm-b S6 chain runner (reusable).

Same shape and same reason as Tools/s6_chain_bmc.py: the per-round S6 chain used
to be an ad-hoc script rebuilt every window, which spent the round's wall time
on generation instead of measurement. This copy carries the legs bm-b actually
owns (R31 lane law: astock daily + ETF five-member panel are bm-b lanes) plus the
shared data/panel and guard legs, and leaves the bm-c-hosted ETF production-book
family to bm-c's own runner so the two machines do not refresh one book twice.

Usage: python Tools\\s6_chain_bmb.py <round_no>
Exit 0 always (legs are recorded; a non-zero leg is reported, not fatal) -- the
round report must surface any rc!=0 leg verbatim.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

LEGS = [
    ("dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    # E217: run before anything that reads "pool ready N" -- four cards sat open with
    # their declared deliverable already on disk, so the watermark counted work that
    # was finished. apply is evidence-gated (face written after the card entered) and
    # idempotent, so a clean pool costs one glob pass and writes nothing.
    ("pool_deliverable", ["python", os.path.join("Tools", "pool_deliverable_audit.py"),
                          "apply"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    # the official exchange calendar, so "no new bar" is not ambiguous
    ("cal_audit", ["python", "scripts/exchange_calendar_audit.py", "run"]),
    # r1339: E30's standing coverage census existed since r1106 and was never in
    # the chain -- its last published face was 11 days old while data/daily sat at
    # 96% on 2026-10-28 with no 10-29/10-30 bars and cal_audit could only say
    # "panel_gap" without naming the share. Counts dates already on disk, zero
    # network, so it is cheap enough to hold the histogram current every round.
    ("panel_coverage", ["python", "scripts/panel_coverage_report.py", "run"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("market_clock", ["python", "scripts/market_clock_call.py", "run"]),
    # bm-b lanes (R31): the A-share daily panel and the five-member ETF panel
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    # bm-b faces that read those panels
    ("regime_thermo", ["python", "scripts/regime_thermo_build.py"]),
    ("regime_gate_dualarm", ["python", "scripts/regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("etf_book_forward", ["python", "scripts/etf_book_forward.py"]),
    # E214: the E60 off-book liquidity split carried across every era the panel
    # covers, so a two-era sign disagreement is not read as a flip on a sample of 2
    ("offbookera", ["python", "scripts/e39_panel_census.py", "offbookera"]),
    # E61: the mid-month calendar gap split into a timing part and a selection
    # part, with the month-end book's holdings as the per-session candidate pool
    ("sharedbook", ["python", "scripts/e39_panel_census.py", "sharedbook"]),
    # E218: E61's "selection" part also carried a width change (the shared arm
    # chose from <=10 names, both full arms from ~1,274), so the split is re-read
    # with both matched arms on one seeded draw of the same size -- and read as a
    # distribution, because a single ten-name draw is noisier than the gap
    ("sharedbookwidth", ["python", "scripts/e39_panel_census.py",
                         "sharedbookwidth"]),
    # E219: the same matched-width control on a width ladder. Idempotent on the
    # cutoff (a face for this cutoff is a no-op), so the chain does not re-pay four
    # burns per round for identical numbers.
    ("sharedbookwidthladder", ["python", "scripts/e39_panel_census.py",
                               "sharedbookwidthladder"]),
    # E220: the ladder's rungs disagree, so this reads them through the E61 identity
    # and names the part that carries the movement. Pure arithmetic over the face
    # above -- no burn -- so it re-derives every round instead of caching to a cutoff.
    ("sharedbookwidthsplit", ["python", "scripts/e39_panel_census.py",
                              "sharedbookwidthsplit"]),
    # E221: the same calendar question asked where the sample is wide enough to
    # matter -- the whole ETF universe instead of one ten-name book. Deterministic,
    # zero network, ~10s on the full panel, so it re-derives every round rather than
    # caching to a cutoff.
    ("dom_profile", ["python", "scripts/e221_dom_profile.py", "run"]),
    # E222: E221 left the turn-of-month shape as a post-hoc candidate; this leg asks
    # whether it survives as a tradable rule with costs, a frozen IS/OOS split and a
    # decision rule in code. Same panel, deterministic, ~2s, so it re-derives each round.
    ("tom_overlay", ["python", "scripts/e222_tom_overlay.py", "run"]),
    # E223: E222's power block said the calendar question needs ~110 years because the
    # rule is observed once a month. This leg runs the same accounting on a frequency
    # ladder (the monthly anchor against three weekly ones) and publishes the resolution
    # each reaches, so "observe more often" is measured rather than assumed.
    ("obs_rate_ladder", ["python", "scripts/e223_obs_rate_ladder.py", "run"]),
    # E224: E223 said a faster anchor does not buy resolution because the hold sets both
    # the count and the per-period signal. This leg tests the successor it named -- a
    # continuously-sampled volatility gate -- and separates the DAYS the gate is on from
    # the EPISODES that produced them, because only the episodes are independent.
    ("vol_gate", ["python", "scripts/e224_vol_gate.py", "run"]),
    # E225: E224's cap was the hold, not the sampling rate, so its named successor was
    # the design the accounting does not throttle -- a weight that varies continuously
    # with the state, no per-episode round trip. This leg prices that on the same signal
    # and the same toll, and publishes the effective sample size so "more sessions" is
    # never mistaken for "more independent observations".
    ("state_tilt", ["python", "scripts/e225_state_tilt.py", "run"]),
    ("tilt_breakeven", ["python", "scripts/e226_tilt_breakeven.py", "run"]),
    # E228: E226 showed the drift split can hand a losing rule a positive residual,
    # because an attributed share of the null's drift is not a benchmark. This leg
    # builds the benchmark -- a flat arm at the gate's own average weight under the
    # same toll -- and judges the PAIRED daily difference, so the timing term finally
    # carries a standard error instead of standing alone.
    ("matched_exposure", ["python", "scripts/e228_matched_exposure.py", "run"]),
    # E229: E228 gave the pair a standard error but not a source. This leg splits the
    # same paired series three ways (selection = which days, sizing = how much, toll =
    # what the movement costs) as an exact identity, so a losing pair can be attributed
    # to the days it dodged, the weights it held or the toll it paid.
    ("timing_selection", ["python", "scripts/e229_timing_selection.py", "run"]),
    # E230: E229 named the toll as the only channel that clears its bar, and the toll is
    # charged on |dw|, so the mechanical follow-up is whether the rule can move less
    # often. This leg ladders a hysteresis deadband on the same volatility signal,
    # publishes all three channels per rung at x1 and x2 costs, and refuses to call a
    # band a fix unless the toll saving covers the selection it gives up.
    ("hysteresis_toll", ["python", "scripts/e230_hysteresis_toll.py", "run"]),
    # E231: exactly one of E230's thirty rungs cleared the bar, and it was the smallest
    # band in the grid -- the shape E188 warns about. This leg re-measures the whole fine
    # grid on other paths (split offsets, execution lags, calendar eras) and publishes the
    # share of paths that keep the sign instead of the best cell.
    ("band_path_test", ["python", "scripts/e231_band_path_test.py", "run"]),
    # E232: every toll number in this family charges |dw| at a fixed 13.041 bp, so the
    # conclusion that the toll is the only separating channel rests on a LINEAR charge.
    # This leg sweeps gamma in 0.75/1.00/1.25/1.50 (a 1.0 move costs the same at every
    # point) and asks which conclusions are curvature-invariant and which are the cost
    # model's.
    ("cost_curvature", ["python", "scripts/e232_cost_curvature.py", "run"]),
    # E233: E232's four curvature points were assumed, so this leg estimates the exponent
    # from the panel (|r_oc| ~ k * amount ** gamma, HAC interval, era split) and then
    # re-reads the same family verdicts on the measured interval AND across the whole
    # estimator-identification span, so a verdict decided by where gamma is placed shows up
    # as such instead of riding a grid.
    ("empirical_gamma", ["python", "scripts/e233_empirical_gamma.py", "run"]),
    # E234: E233 measured ONE exponent per panel, but the book holds five instruments with
    # different liquidity and history, so the book-level number may be a mixture charged to
    # four sleeves that do not share it. This leg estimates gamma per member, tests whether
    # the five intervals are mutually compatible, and re-prices the movement bill with each
    # sleeve on its own exponent -- against a same-granularity control so the split of one
    # move into five concave charges is never read as the mixture effect.
    ("per_member_gamma", ["python", "scripts/e234_per_member_gamma.py", "run"]),
    # E235: the split E234 priced has two possible readings -- each sleeve priced on its
    # own turnover, or the book priced on its aggregate turnover. This leg measures which
    # one the panel supports and re-prices the arms under both, disclosing when the level
    # specification cannot tell them apart.
    ("charge_granularity", ["python", "scripts/e235_charge_granularity.py", "run"]),
    # E236: the granularity question re-asked with stationary regressors (differences,
    # frozen-standardised level, two-way fixed effects). It refuses a verdict when the
    # designs agree only about a channel's SIGN and not its SIZE.
    ("share_difference", ["python", "scripts/e236_share_difference.py", "run"]),
    # E237: E236 named the mechanism behind its own 25x size gap (a session priced against
    # its own turnover CHANGE co-moves with the information arrival that sets |r|) but did
    # not measure it. This leg separates the channels directly -- common vs relative return
    # components, plus a market-return control on the share coefficient -- and refuses a
    # granularity bill unless both components clear the bar with overlapping intervals.
    ("information_structure", ["python", "scripts/e237_information_structure.py", "run"]),
    # E238: every member's own turnover sits inside the book turnover its share is divided
    # by, so the family's own-channel coefficient may be the share arithmetic rather than a
    # market object. This leg rebuilds the book EXCLUDING each member and re-runs the same
    # three designs against it, publishing the gap with a block-bootstrap interval next to
    # the gap the share arithmetic predicts.
    ("leave_one_out_book", ["python", "scripts/e238_leave_one_out_book.py", "run"]),
    # E239: E238's ordering (own 0.596 < rest 0.771) could be a units artefact -- the rest is
    # a SUM of four members, so one log point of it is four participants' worth. Rescaling the
    # sum by 1/4 only multiplies a coefficient, so this leg prices the own channel against ONE
    # counterparty per pair, pooled with pair fixed effects and again with member+date FE.
    ("own_vs_cross", ["python", "scripts/e239_own_vs_cross.py", "run"]),
    # E243: E240's rest_channel_is_additive came from ONE window. This leg re-runs the same
    # identified design on the pre-2020 four, three five-member eras, five leave-one-out cells and
    # a labelled k=3 degenerate cell, publishing the difference interval in every one -- and it
    # publishes the pooled aggregator as identifies:false, because the pooled stack replicates one
    # member's response across its counterfactual blocks and annihilates the very direction that
    # separates the one from the rest channel.
    ("additivity_out_of_sample", ["python", "scripts/e243_additivity_out_of_sample.py", "run"]),
    # E244: E243's headline cell excludes zero on 9 of 20 ordered pairs in mixed signs. This leg
    # reads those published intervals (machine-read, never transcribed) and asks where the spread
    # sits -- counterparty identity, own identity, or pair idiosyncrasy. A member that pays more
    # than the rest casts a NEGATIVE mirror on every ordinary member because it sits inside the
    # sum they are priced against, so a sign split alone cannot name two channels.
    ("pair_heterogeneity", ["python", "scripts/e244_pair_heterogeneity.py", "run"]),
    # E245: every reading above came out of a SUM design, where `rest` is one member against an
    # average of the others -- a number no single counterparty reports. This leg fits the
    # un-summed matrix (own + each other member separately, jointly, one HAC per cell), tests row
    # equality against column concentration, and publishes the resolution the matrix carries.
    ("pair_slope_matrix", ["python", "scripts/e245_pair_slope_matrix.py", "run"]),
    # E246: the matrix leg named a star but could not say whether that sleeve's flow moves the
    # book or whether all five load on one driver it happens to read best. This leg refits every
    # row with the counterparties' PAST turnover in the same regression as their present one, so
    # the lag coefficient is a lead rather than a proxy for a persistent column.
    ("star_direction", ["python", "scripts/e246_star_direction.py", "run"]),
    # E247: three of E246's undecided cells sit in CLOSED calendar windows, so "collect more
    # data" is not available to them. This leg turns each cell's published half-width into the
    # session count a verdict would need, and names which cells can never reach it -- derived
    # from the published face only, no re-estimation, no network.
    ("era_power", ["python", "scripts/e247_era_cell_power.py", "run"]),
    # E248: E246 published the star lead as a lag0/lag1/lag2 sign flip, each coefficient against
    # its own HAC interval. This leg spends the same design's null instead -- 200 shuffled-star
    # draws, family-wise over lags 1..5 -- and needs ~8s because the fits run in numpy.
    ("star_lag_band", ["python", "scripts/e248_star_lag_band.py", "run"]),
    # E249: E248 found exactly one crossing and named the star. This leg re-fits the same row
    # with EACH member as the column of interest -- five readings of one design, each against
    # its own 200-draw shuffled band -- because "the star is negative" and "every column is
    # negative" are the same number until the columns are read side by side. ~14s.
    ("lead_counterfactual", ["python", "scripts/e249_lead_counterfactual.py", "run"]),
    # E250: E249 read every column negative, so the naming was never the star's. This leg asks
    # the open question directly -- is the shared lead the book's own lagged aggregate turnover?
    # -- with the aggregate in the row alone, beside each column, and as a LEAVE-ONE-OUT sum
    # (the column's turnover is a component of the aggregate, so the inclusive share is the
    # E238 denominator-contains-the-numerator reading). ~30s.
    ("book_echo", ["python", "scripts/e250_book_turnover_echo.py", "run"]),
    # E251: E250 left exactly one number unexplained -- the star kept ~90% of its lag-1 once the
    # book aggregate was in the row, against 0.10-0.60 everywhere else. This leg decomposes that
    # residual (own turnover vs the star's own lagged |move| vs member age) and decides each
    # addition against the band its OWN time-shuffle produces, so an addition that merely fits
    # cannot claim the coefficient. ~20s.
    ("star_own_component", ["python", "scripts/e251_star_own_component.py", "run"]),
    # E252: E251 priced the star's effect on OTHER members and settled its shape (its own lagged
    # turnover, with volatility and age taking nothing). This leg turns the same design around --
    # the star as the outcome -- and reads the coefficient it carries for others beside the one it
    # carries for itself, with the difference on a paired block bootstrap. The burn costs minutes
    # (200 permutation + 400 bootstrap draws on six cells), so the chain runs --verify: re-derive
    # every published verdict from the face's own numbers and pin the cross column to E251's
    # published statistic. Re-burning each cycle would be a re-measurement, not a check. <1s.
    ("star_self_price", ["python", "scripts/e252_star_prices_itself.py", "verify"]),

    # E280: the star_self_price leg went red at r1303 claiming an RNG drift (177 fields moved
    # between E251's face and its rerun). Measured: the two implementations are one regression on
    # one panel (0.0 difference), and the move came from one extra bar -- the verify was comparing
    # faces priced on different worlds. This leg re-publishes the decision and re-pins E251's draw
    # stream: same (panel, seed, draws) must reproduce the band, another seed must move it. ~4s.
    ("star_own_rng_repin", ["python", "scripts/e280_e251_rng_drift_repin.py", "selftest"]),

    # E253: E252 left one cell unmeasured (era_2025_now: the star's self coefficient -0.463 sits
    # inside its own shuffled band while its cross column stays outside its own). This leg does
    # the arithmetic that face did not: every band becomes the session count its own width implies,
    # so "waiting for sessions" and "the channel weakened" stop being the same sentence. It reads
    # the published face only -- no panel, no refit -- and the chain runs --verify, which re-derives
    # every published number from the saved face. <1s.
    ("self_row_resolution", ["python", "scripts/e253_self_row_resolution.py", "verify"]),

    # E254: E253's session counts rest on edge(n) ~ n**-0.5, an exponent it only checked ACROSS
    # heterogeneous eras (0.244). This leg rebuilds the shuffled band inside ONE cell at seven
    # session counts and fits the exponent on the cell's own rungs; it answers with the ladder,
    # not a date, and refuses to claim an exponent the rungs do not carry. Reads the published
    # face only -- no panel, no refit -- and runs --verify. <1s.
    ("band_exponent_inside_cell", ["python", "scripts/e254_band_exponent_inside_cell.py", "verify"]),
    # E255: E254 could not name the exponent and blamed either too few permutation draws or too
    # few rungs. This leg measures the same seven rungs at 60/120/240/480 draws, reading every
    # smaller count as the PREFIX of one 480-draw stream so the four ladders are one experiment.
    # Result: the band endpoint is still rising with draws (a 5% quantile read off too few draws
    # sits inside the true boundary), so the shortfall is DRAWS, not rungs -- and the exponent
    # itself has not converged either. Reads the published face only, no panel, no refit. <1s.
    ("band_draw_starvation", ["python", "scripts/e255_band_draw_starvation.py", "verify"]),
    # E256: E255 left the endpoint rising 9.8%/11.7% per doubling at 480 draws and asked at which
    # count no rung moves more than 2%, or whether the increment per doubling is flat. This leg
    # carries the answer: on the same prefix-nested ladder stretched to 960 and 1920 draws the
    # endpoint moves 5.2/7.0% and then 10.3/8.8% per doubling -- it never settles, and the rise is
    # not decaying (later doublings add more than earlier ones), so the band has no countable
    # stopping point inside the budget and every session target divided by it is a floor.
    # Reads the published faces only, no panel, no refit. <1s.
    ("band_draw_continuation", ["python", "scripts/e256_band_draw_continuation.py", "verify",
                                "--tag=-d1920"]),
    # E257: E255/E256 showed the band's 5% endpoint was still rising at 1920 draws, so every
    # published "outside the band" verdict had been judged against an edge read off a smaller
    # grid. This leg re-judges every published (coefficient, band) pair in the star family against
    # a band widened by the measured draw multiplier, at EVERY multiplier the ladder carries (2
    # families x 7 rungs) rather than nominating one, and publishes which verdicts flip, which
    # survive, and which only flip for some measurement. Reads published faces only, no panel,
    # no refit, no coefficient re-priced. <1s.
    ("band_at_top_flips", ["python", "scripts/e257_band_at_top_flips.py", "verify"]),

    # E258: E257 borrowed era_2025_now's draw ladder and applied it to every window as a RANGE,
    # because a fixed published window is neither that era's head nor its tail. This leg rebuilds
    # the band INSIDE each published window (same dates, same published star, same published
    # members, prefix-nested draw streams) and measures that window's OWN multiplier. The measured
    # spread (1.27..1.84 at each window's own base count, ratio 1.45) is the finding: the borrowed
    # range was not one object, and early_three's band was under-widened by the borrowed table
    # range. Reads the panel (five-member ETF basket only), 3 seeds x 4 windows, ~85s.
    ("band_multiplier_in_each_window",
     ["python", "scripts/e258_band_multiplier_per_window.py", "verify"]),

    # E259: E258 published each window's multiplier as min..max over THREE seeds. Three draws are
    # not a distribution: this leg re-derives, from the published 40-stream sample, that every
    # interval [p05,p95] is wider than the three-seed range it replaces (16/16, ratio median 2.25)
    # and that three published rows change verdict between the tight and the wide end inside their
    # own interval. Reads the published face only (raw per-seed edge tables are on it), no panel,
    # no refit, no re-pricing. <1s.
    ("band_multiplier_distribution",
     ["python", "scripts/e259_band_multiplier_distribution.py", "verify"]),

    # E260: E259 published 52 of 640 per-seed multipliers reading exactly 1.0 -- that is a
    # prefix-nested endpoint which already arrived before the base count. This leg re-derives the
    # arrival count per seed off E259's own edge tables and pins the arm-by-arm cross-check
    # (16 arms x 40 seeds = 52), so "the published base count sits below the arrival count" cannot
    # go stale silently. Reads the published face only, no panel, no refit, no re-pricing. <1s.
    ("band_endpoint_arrival",
     ["python", "scripts/e260_band_endpoint_arrival.py", "verify"]),

    # E261: E259 published that 52 of 640 per-seed multipliers read exactly 1.0 (the band's lower
    # endpoint had already stopped moving) and that they dragged p05 to 1.0 in 14 of 16 arms. This
    # leg re-derives each interval twice -- over all seeds and over the seeds still free to move --
    # and pins that (a) all 16 arms reproduce E259 bit-for-bit, (b) the 8 arms whose lower end sits
    # at one are exactly the 8 whose floor moves off one once the bucket is removed, and (c) no
    # published row verdict depends on the bucket. Reads E259's published per-seed tables only, no
    # panel, no draw, no re-pricing. <1s.
    ("degenerate_seeds_leave_one_bucket",
     ["python", "scripts/e261_degenerate_seeds_leave_one_bucket.py", "verify"]),

    # E262: E259 published a p05..p95 interval per (window, leg, base count). A reader borrows one:
    # judge a row with another window's wide end. This leg re-derives that 2 of 48 ordered
    # (donor, recipient) pairs move a verdict -- all_five's cross:60 p95 (2.2963, +13.9%/+16.7%)
    # flips two cross rows outside->inside -- and that no single window is the widest at every
    # (leg, base count) (all_five at base 60 both legs, early_three at self:200, era_2025_now at
    # cross:200). Reads the published E259 face only, no draw, no panel, no re-pricing. <1s.
    ("p95_transfer_across_windows",
     ["python", "scripts/e262_p95_transfer_across_windows.py", "verify"]),

    # E264: a row's whole verdict is its threshold m* = |b|/max(|lo|,|hi|) (outside <=> m < m*),
    # so the row side needs no draws. This leg re-derives which published row sits closest to its
    # band (era_2025_now cross:60, m*=1.9583 against its own p95=1.9678, a 0.0095 gap) and that
    # the p05 == 1 floor the near-one seeds create is NOT load-bearing for any of the 4 rows that
    # end on it (their thresholds are all >= 2.1). Also re-derives that both rows E262 moved by
    # borrowing sit inside the top-3 closest. Reads the published E259 face only, no draw. <1s.
    ("near_one_seed_reading",
     ["python", "scripts/e264_near_one_seeds_reading.py", "verify"]),

    # E266: E265's per-row screen ("any donor p95 above the row's threshold m* flips it") scored
    # against E262's 48 published ordered pairs. This leg re-derives that the written screen flags
    # 18 of 36 comparisons while only 2 move (precision 0.111), that guarding on the row's own end
    # removes the false positives but loses one real move, and that only the BRACKET with the row's
    # OWN SIDE reproduces the moved set exactly -- 18 of the 36 comparisons carry a side-dependent
    # threshold, so max(|lo|,|hi|) is not a detail. Reads the published transfer face only. <1s.
    ("wide_end_screen",
     ["python", "scripts/e266_wide_end_screen_holdout.py", "verify"]),

    # E267: E266's bracket screen is exact but is a knife edge -- a donor 0.0001 above the row's
    # own-side threshold counts the same as one 0.3 above. This leg re-derives the clearance curve
    # "donor_p95 > t*(1+b)" over 4 rules: the unbuffered single rule flags 14 of 36 comparisons
    # with 2 moves (precision 0.143); a buffer alone peaks at 0.154 in a 0.0012-wide b window and
    # never reaches 1, because a non-move clearing by 246% of its threshold answers to no margin;
    # the own-side guard alone is 2/2 exact and tolerates a buffer up to the closest move's 0.0455.
    # Re-reads the published faces only, no draw, no panel, no re-pricing. <1s.
    ("screen_buffer_margin",
     ["python", "scripts/e267_screen_buffer_margin.py", "verify"]),

    # E268: E267's operative half is the own-side guard, which needs the row's own p95 -- the one
    # number a reader of the table does not have. This leg re-derives the two substitutes that do
    # live in the published face: the (leg, base) pooled TIGHT end answers the guard identically on
    # all 36 comparisons (24 below t, 12 above) and reproduces both published moves, while the
    # pooled WIDE end flips 6 comparisons (misses both moves) and the per-row published BOOLEAN
    # flips 3 (it inherits E259's self-arm judgement on row 13, which E262 disclosed as
    # interval-dependent). It also re-derives that the equivalence is carried by distance -- the
    # nearest comparison sits 0.0835 off its threshold -- so it holds only outside that band.
    # Reads the published transfer face only, no draw, no panel. <1s.
    ("screen_on_pooled_end",
     ["python", "scripts/e268_screen_on_pooled_end.py", "verify"]),

    # E269: every arm in E259 also publishes a p05 and every row a verdict_tight, so the tight half
    # of the same transfer question had never been scored. This leg re-derives that the tight end
    # moves no verdict on any of the 48 ordered pairs while the wide end moves 2 -- and, so that
    # "zero moves" is not a tautology, that no measured row could flip at ANY p05 its group
    # actually published (each row publishes its flip multiplier; the nearest one sits 13.5%
    # outside the widest observed p05 swing). The reading is inertness on this population, not a
    # clean transfer, which is why the verdict is named that way. Published faces only. <1s.
    ("tight_end_transfer",
     ["python", "scripts/e269_tight_end_transfer.py", "verify"]),

    # E274: E271's mechanism was a case report on one axis. This leg turns it into a family census:
    # for every measured BAND* row it re-derives the flip multiplier, the multiplier range that axis
    # actually offers and a four-way straddle reading, then scores the flag against the moved sets
    # the faces themselves published -- wide_donor (E271's set), tight_p05 and top_ladder. All three
    # reproduce exactly (4 moved observations, 4 hits, 0 missed, 0 flagged-but-inert). It also pins
    # the "same name, different quantity" trap that broke the first cut: BANDTOPFLIP publishes
    # flipped_ids (flips at EVERY measurement, empty) and depends_ids (flips at SOME, 2 rows); the
    # flag answers "can move", so the SOME set is the one to score and both are carried. <1s.
    ("spread_straddle_sweep",
     ["python", "scripts/e274_spread_straddle_sweep.py", "verify"]),

    # E275: E274's screen is binary -- a cleared row is 'safe' and nothing is said about how
    # much room is left. This leg puts a budget on the cleared set from the same two published
    # numbers: the share of the flip threshold the group's widest offered multiplier already
    # eats, plus a five-way zone. On 12 measured rows the cleared set splits 4 open / 2 spent /
    # 4 spent-by-build while the 2 straddlers are exactly the guard screen's moved rows, and
    # none of the near-spent rows is a row the near-one or guard screen already names -- so
    # "outside the range" is one reading with room and another with almost none. Faces only.
    ("screen_margin_budget",
     ["python", "scripts/e275_screen_margin_budget.py", "verify"]),

    # E272: E269 measured the tight half's draw budget and left the wide half's unmeasured on the
    # same ruler. One flip multiplier per row, then each tail's own published multiplier range in
    # the row's (leg, base) group placed on it: the wide tail reaches 2 rows (exactly E262's two
    # moved rows, re-derived from that face), the tight tail reaches none because every published
    # p05 sits at >= 1.0 while 10 of 12 flips need a LARGER multiplier -- and on the normalised
    # ruler (gap / that tail's own spread) the wide tail is closer on 10 of 12. The leg re-derives
    # the face and crosses it against E269's published gaps plus E262's moved set. <1s.
    ("flip_budget_two_tails",
     ["python", "scripts/e272_flip_budget_two_tails.py", "verify"]),

    # E277: why the tight tail is inert -- it is a property of the BAND BUILD, not of the windows.
    # lo is the MINIMUM of a nested draw prefix (BAND_PCT 0..100), so |lo| can only widen and
    # m = |lo|(top)/|lo|(base) cannot fall below 1 while the published draw exponent is positive
    # (0.348 head / 0.647 tail, endpoint never narrowed on 6 of 7 rungs). All 140 published
    # multiplier lower ends on disk sit >= 1.0, 39 of them exactly 1.0 (the degenerate branch: one
    # seed away they lift to 1.11..1.20). A 5% band on the same stream yields m = 0.92, so the
    # floor comes from the build. The leg re-derives the census and the counterfactual. <1s.
    ("tight_multiplier_floor",
     ["python", "scripts/e277_tight_multiplier_floor.py", "verify"]),

    # E278: the normalised ruler divides a gap by the spread a tail offers, so a spread of exactly
    # 0 leaves it undefined. Census every published arm-table group at both tails: 4 groups, 3
    # measurable on both; the ONE zero spread is cross:200's tight tail where all four cells sit on
    # the 1.0 floor (E277). 8 of 16 published tight values are exactly 1.0 and 7 of those 8 are at
    # base 200, so the hole is the floor landing where the percentile has least support -- not one
    # bad group. Wide tail: no zero anywhere, min spread 9.1%. The 2 published E272 rows that sit
    # in it stay unmeasured. Verify re-derives and crosses the spreads against E272. <1s.
    ("spread_floor",
     ["python", "scripts/e278_spread_floor.py", "verify"]),

    # E279: E278 left a policy nobody had tested -- when a tail's spread is 0, "read the other
    # tail". Both substitution events agree, and both agree vacuously: a stranded tail publishes a
    # degenerate multiplier range (min == max), so its "unreachable" is mechanical and the
    # substitute had nothing to contradict. Where the two tails genuinely differ (2 rows) the tail
    # you read decides the answer, and the swap view names the same rows in both directions --
    # substitution is monotone (it can only add a "can move"), never a proof a row cannot. Verify
    # re-derives reachability from the published ranges and crosses the stranded set against E278. <1s.
    ("substitution_soundness",
     ["python", "scripts/e279_substitution_soundness.py", "verify"]),

    # E281: the dependency question E279's scoping left open -- does any published conclusion rest
    # on a stranded tail to say "cannot"? Structural scan of all 27 dated BAND* faces: only 1 face
    # carries reachability booleans for BOTH tails (24 claims, 22 of them "cannot"), and exactly 2
    # of those rest on a stranded tail -- both in a face that already labels the tail inert/dead by
    # construction, with a substitute that agrees vacuously. Zero load-bearing claims. It also
    # re-derives E279's census row by row (24/24) and finds E279's summary field is keyed on the
    # GROUP label, so a group with 1 disagreeing cell of 4 is published whole. Published faces
    # only, no draw. <1s.
    ("substitution_dependency_audit",
     ["python", "scripts/e281_substitution_dependency_audit.py", "verify"]),

    # E282: the seed read the two disagreement cells' gap of 0.0 as "the substitute lands on the
    # flip" and hypothesised a rounding boundary artefact. The gap reads 0.0 for EVERY interior
    # reading because it is clamped inside the range, so the census re-measures the flip's position
    # instead: both cells sit at 0.52/0.70 of the way into the reaching range while the other tail
    # is 48-50 pct away. Range difference, not a tie. Published faces only, no draw. <1s.
    ("substitution_disagreement_census",
     ["python", "scripts/e282_substitution_disagreement_census.py", "verify"]),

    # E283: E279's contradiction branch (the substitute DEFLATES the conclusion) reported 0 events
    # on 2 substitution events. A degenerate tail can only reach a row when the flip equals its
    # single multiplier, so this leg measures the shape that event would need: both candidates sit
    # 2.70x / 3.25x from their degenerate value, the tolerance band that would fire the branch is
    # [63.03 pct, +inf), and at that tolerance 21 of 24 published readings read reachable against 2
    # published -- the test that fires the branch is not the test that published the family. It
    # also re-derives 24/24 published booleans and E279's stranded set. Published faces only. <1s.
    ("degenerate_range_reachable",
     ["python", "scripts/e283_degenerate_range_reachable.py", "verify"]),

    # E284: E281 found one summary field whose NAME says rows while its VALUE is a list of group
    # labels (cross and star_lag1_residual each hold 4 cells, one of which disagrees). This leg
    # re-derives the disagreeing CELLS out of E279's own per-tail booleans (landing exactly on the
    # face's published swap rows, identity True) and sweeps the whole family for the same shape:
    # 30 dated faces, 1 flagged field -- the slip is unique -- while 1338 integer count fields are
    # reported as NOT assessed rather than guessed at. Published faces only. <1s.
    ("disagreement_field_scope",
     ["python", "scripts/e284_disagreement_field_scope.py", "verify"]),

    # E285: the two tails' ranges leave a gap between them, and a flip landing in that gap is
    # reachable by NEITHER. This leg measures that gap per (leg, base) arm and, more importantly,
    # separates it from the rows that sit above the family's published ceiling entirely: of 12
    # rows, 2 fall in a positive gap (20 pct of the 10 unresolvable) while 6 sit above the ceiling
    # of 2.2963 (up to 1.417x it) -- any widening that stays inside the published evidence can add
    # at most those 2 rows, so the substitution's headroom is spent on the gap, not on the
    # extrapolation zone. Published faces only, no draw. <1s.
    ("interrange_gap_ceiling",
     ["python", "scripts/e285_interrange_gap_ceiling.py", "verify"]),

    # E286 (r1311 bm-b): E284 had to leave 1338 integer fields unjudged because an integer count's
    # scope depends on that face's own census semantics. This leg judges the half that can be judged
    # without guessing: of 894 unit-named counts across 32 dated faces, only 27 (3.0 pct) publish the
    # records they name in the SAME scope -- and all 27 count the unit they claim, so the name is a
    # checkable claim for a minority. The other 867 split into 301 where the face publishes that unit
    # elsewhere (the name lacks a scope) and 566 where it publishes no records of that unit at all
    # (the name is a design parameter) -- two different fixes that must never be reported as one
    # number. 557 subset-named counts are disclosed as not judged (E208: a naive unit-word match
    # rejects real quotes). Published faces only, no draw. <1s.
    ("count_field_scope",
     ["python", "scripts/e286_count_field_scope.py", "verify"]),

    # E290 (r1312 bm-b): E286 could say which counts are checkable but not whether copying the
    # checkable faces would help. This leg profiles the shape: all 27 sit beside a same-parent list of
    # exactly the unit their name claims, and every one equals that list -- but 12 of the 27 carry an
    # equal-length same-unit list elsewhere in the same face, so those agreements cannot be told from
    # coincidence, and the exemplar faces are only 17.9 pct self-auditable (27 of 151 of their own
    # counts) against 3.0 pct family-wide. The 867 un-derivable counts split into 301 rows over 299
    # scopes (move the count into the scope that already publishes the unit) and 566 rows over just 8
    # keys (no record face exists, so no naming convention can rescue them). Published faces only,
    # no draw. <1s.
    ("self_auditable_face_profile",
     ["python", "scripts/e290_selfauditable_face_profile.py", "verify"]),

    # E291 (r1313 bm-b): E290 flagged 12 of 27 counts as ambiguous because another same-unit list in
    # the same face has the same length -- which only informs if equal lengths can be accidents. They
    # cannot, or not mostly: 104 of 125 eligible lists (83.2 pct) have an equal-length sibling against
    # 67.4 pct expected from the pooled length distribution (tail p<0.001), and of the 746 equal-length
    # pairs 605 share a record schema and 135 are the very same content -- only 6 differ in content.
    # At the flag's own level 12 of 27 is exactly the null (39.9 pct expected) and all 12 come from
    # just 2 scopes, so "ambiguous" marks a shared shape (and 135 duplicated lists) rather than two
    # lists competing for one meaning. Published faces only, no draw. <1s.
    ("ambiguity_by_length_chance",
     ["python", "scripts/e291_ambiguity_chance.py", "verify"]),

    # E287 (r1314 bm-b): E285 called 6 rows above the family ceiling 2.2963 "extrapolation", which
    # only holds if nothing wider is already published. Six dated band faces publish a number called
    # a multiplier; signed by axis, only two are band-edge supplies and both tops sit BELOW the
    # ceiling (1.8383 median per window / 2.2457 at a single best seed), so no above-ceiling row is
    # reachable (nearest self|200|0 needs 3.8 pct more). Both gap rows ARE reachable by that same
    # supply (cross|60|11 at the median, star_lag1_residual|60|15 only at the single seed), and the
    # published narrowing instrument (0.9220) misses the nearest below-floor row by 3.7 pct. The
    # 63.0 pct tolerance and the 2.0327 spread threshold that look wider are published as off-axis.
    # Published faces only, no draw. <1s.
    ("supply_ceiling_axes",
     ["python", "scripts/e287_supply_ceiling_axes.py", "verify"]),

    # E288 (r1317 bm-b): the mirror of the ceiling question -- a flip BELOW the published floor of
    # 1.0 needs the band NARROWED. Two rows sit 11.06 and 36.96 pct under the floor; the family
    # publishes exactly one sub-1.0 band-edge multiplier (0.9220216) and it misses the nearest row
    # by 3.67 pct and the farthest by 46.26 pct, so the verdict is "reaches none". Scored against
    # all 12 rows on each row's own polarity the same instrument reaches 0, so tightening is not a
    # free fix for the widening side either. E285's per-row "distance below tight lo" column is
    # published with its implied reference (1.0283 / 1.5815, both ABOVE the floor) because it
    # gauges a narrowing demand with a widening instrument. Published faces only, no draw. <1s.
    ("below_floor_narrowing",
     ["python", "scripts/e288_below_floor_narrowing.py", "verify"]),

    # E293 (r1314 published, wired r1318 bm-b): E291 showed equal-length lists are the family's
    # SHAPE; the open question was whether a copy makes a number count one thing twice. Six alias
    # groups over 32 censused faces (38 members, 26.6 pct of all lists): 2 are schema-driven (the
    # same slot across arms) and 4 accidental, and no scope anywhere publishes a total that sums an
    # alias group -- so the duplicate lists cost nothing in double counting, they just are one list
    # printed more than once. Wiring leg: the published face had no chain leg and no smoke leg, and
    # its derivation had in fact stopped running (E291's frozen census_names returns a tuple).
    # Published faces only, no draw. <1s.
    ("duplicate_list_census",
     ["python", "scripts/e293_duplicate_list_census.py", "verify"]),

    # E295 (r1319 bm-b): E287's two margins asked for "one more rung" of the published draw ladder.
    # Priced: the ladder spans 1.000..1.925 central (2.427 at a single seed) over 70 rung-readings,
    # its median adjacent step buys 6.99 pct, and 37 of 70 steps are finer than the widening margin
    # -- so the margin was never a resolution problem. Both gradable demands live in the ladder's
    # OWN window (star_lag1_residual|60|14 widen 5.98 pct short of the nearest rung, self|60|8
    # narrow with no sub-1.0 rung at all), and neither the rung nor a narrowing rung exists, so the
    # face declares the interpolation aborted instead of fitting one. Also witnesses E258's
    # era_2025_now|60 multiplier reproduce off the ladder to 0.0. Published faces only. <1s.
    ("supply_gap_closure",
     ["python", "scripts/e295_supply_gap_closure.py", "verify"]),

    # E300 (r1320 bm-b): E295 had to call 9 of 12 demand rows not_graded because only era_2025_now
    # owns a draw ladder, and the widening margin it read (5.98 pct) differed from E287's headline
    # (3.80 pct) purely by which window's cap was the denominator. Re-priced every published demand
    # row against the multiplier its own window published at its own base draws (E258 measured all
    # four cells): 10 of 12 are graded on their own window, 3 reach verdicts flip (rows that looked
    # reachable only under a borrowed cap), and the borrowed-cap denominator understates the margin
    # by up to 147 pct. The 2 narrowing rows stay ungraded with a named face because the family
    # publishes no window-local narrowing instrument (BANDFLOOR is one synthetic seed). Witnesses
    # that E295's own margins reproduce on the cross-window column. Published faces only. <1s.
    ("window_local_margin_census",
     ["python", "scripts/e300_window_local_margin_census.py", "verify"]),

    # E292 (r1321 bm-b): E290 handed the 301 'the face already publishes this unit elsewhere' rows on
    # as "move the count, no new data needed". Priced: 24 of them name the unit AS the key (so no
    # sibling list of that name can exist), 76 have the unit published in more than one scope (a
    # choice, not a move), and of the 201 single-target rows 126 agree with the candidate list while 75
    # do not -- but ZERO of the 201 land beside a list in their own scope or a scope that contains /
    # sits under it, and every one of the 126 agreements is against a list holding at most one item in
    # an unrelated subtree. So the premise fails: those counts measure a collection the face never
    # enumerates. Published faces only, no draw, no engine. <1s.
    ("scope_fix_plan",
     ["python", "scripts/e292_scope_fix_plan.py", "verify"]),

    # E294 (r1322 bm-b): r1314 froze the family census to stop the drift, which answered "how do we
    # stop it" but not "did it matter". This leg asks the question under the freeze: for every study
    # that censuses the BAND directory, re-derive it twice -- once against the vintage it published
    # (faces stamped no later than its own) and once against the live directory -- and classify the
    # verdict as stable / flips / does-not-reproduce / not-measurable. 12 of the family's 54 study
    # scripts census the directory at all (the other 42 read named sibling faces and cannot move);
    # 9 of the 12 can be varied, and every one prints the same verdict with up to 34 more faces in
    # view, so the drift r1314 fixed was a reproducibility problem, not a conclusion problem. Each
    # study runs in its own process under a wall-clock cap, self-inclusion is refused, and nothing in
    # results/state_tilt is written by the measurement. ~70s (13 child processes).
    ("live_universe_drift",
     ["python", "scripts/e294_live_universe_drift.py", "verify"]),

    # E302 (r1325 bm-b): E294's own finding was that three directory-censusing studies publish
    # build() with no universe argument, so for them the universe question was UNASKED. This leg
    # prices the switch instead of assuming it: the universe reaches each study through a
    # module-level directory global, so redirecting every module binding of that global re-derives
    # the study against a staged vintage without editing a line -- the price is 31 bindings, and a
    # real `outdir=` parameter would instead thread 6 functions and 10 module-default load() calls.
    # All three reproduce their published verdict and none flips (staged 118/120/132 faces against
    # the live 170). Each row publishes both file counts so a staging that is not narrower cannot be
    # read as "stable", and the real directory's mtimes are asserted unchanged. ~5s.
    ("universe_switch_backfill",
     ["python", "scripts/e302_universe_switch_backfill.py", "verify"]),

    # E298 (r1323 bm-b): r1316 taught ONE replay control (E243's) to say which panel it re-derived
    # on, which fixed a face and not the class. This leg censuses every control block published in
    # results/state_tilt (90 dated faces; 67 mirrors and its own two faces excluded): 26 containers,
    # 12 identity checks (re-derived from the face's own records, so a vintage cannot move them) and
    # 14 replays. Of the 14 replays only 7 declare a basis -- 6 carry their own window/pin, 1 names
    # the live panel and its overshoot (ADDOS 2026-10-30) -- so 7 replays are published reacting to
    # an unknown panel. They are published as UNMEASURABLE, never as safe or broken. The ADDOS pair
    # also shows the repair landing: the same block went undeclared (10-29) -> live_declared (10-30).
    # Published faces only; no panel re-read, no draw, no engine. <3s.
    ("replay_control_census",
     ["python", "scripts/e298_replay_control_census.py", "verify"]),

    # E303: E298 published seven replay controls as unmeasurable because their face names no panel.
    # This leg asks the writer instead: of the seven, 1 is computed by its writer and dropped from a
    # stale face (the same block in a newer vintage carries window_used/window_source and the
    # sessions past the pin), 4 have the basis declared beside the block (basis_note, source_faces,
    # windows_measured, bar_*_basis, panels), and 2 derive on the live panel with nothing said --
    # and those two are the ones whose own numbers move between vintages (BANDPATH 285.88 ->
    # 289.83 bp/yr; REPRO rows 13,911 -> 13,916). 5 of 7 are recoverable without re-running a
    # study. Source + published JSON only; no panel re-read, no draw, no engine. <1s.
    ("basis_recovery",
     ["python", "scripts/e303_recover_unmeasurable_basis.py", "verify"]),

    # E299: r1316 repaired one leg that compared a 6-dp point set against a full-precision
    # interval at 1e-9. This leg prices the class: 42 of smoke_test.py's 320 legs carry a numeric
    # comparison against a published face, 29 of their 62 sites compare at a tolerance finer than
    # the quantum the field they read is printed with (21 on the field's own decimals, 8 on the
    # face-level bound only), and 37 of the 42 faces read publish no precision declaration. Zero
    # measured rounded/full sibling pairs survive -- the one the family had is the one r1316 fixed.
    # Source + published JSON only; no study re-run, no draw, no engine. ~55s (the face reads and
    # the per-key leaf walks dominate; measured in round 1324, not estimated).
    ("precision_census",
     ["python", "scripts/e299_rounded_vs_tolerance_census.py", "verify"]),

    # E305: E299 could only bound 8 of its 29 at-risk rows at face level, because the key the leg
    # reads was not found as a leaf. This leg prices those 8: 3 read a key that lives in a sibling
    # face the same leg names (15 dp at the producer, so neither is at risk), 3 read a container or
    # a label rather than a printed number, 1 reads a key the producer writes inside per-record
    # lists that are empty on this vintage, and 1 reads a boolean flag. All 8 are withdrawn.
    # Published faces + producer text only; no study re-run. <0.2s.
    ("face_level_row_pricing",
     ["python", "scripts/e305_face_level_row_pricing.py", "verify"]),

    # E308: pricing the last of E305's rows surfaced the guess this leg tests -- the open-fill leg
    # compares two session_open values at 1e-9 while the face publishes rel_tol=0.002 as its gate.
    # Of 55 face files named by the 93 comparison sites, 11 publish a real tolerance gate; 30
    # (leg, gate) pairs, 18 arithmetically tighter. A scope reading of the scripts that name each
    # face (is the gate USED in a comparison?) leaves 1 standing, and that one's gate holds the same
    # number as an excluded key on the same face (verdict_inputs.tol 0.1 == frozen_spec.gamma_tol
    # 0.1) -- so it is name-fragile too. Source + published JSON only; no study re-run, no engine.
    ("gate_tolerance_census",
     ["python", "scripts/e308_leg_vs_producer_tolerance.py", "verify"]),

    # E312: those pairings were keyed on the DECLARED key, but a writer publishes a constant
    # ("tolerance": TOL) and compares with the constant or with a parameter defaulted from it, so
    # 29 of the 30 pairs E308 called "declared but never compared" do have a producer comparison.
    # Being compared is still not being compared to the leg's quantity: the one band E308 let stand
    # compares the window edges lo/hi against FROZEN_GAMMA +- tol (a feasibility test of the
    # ladder), while the open-fill band it rejected compares abs(cost - session_open)/session_open,
    # the very price the leg reads (relative vs absolute: disclosed). Verify rebuilds from source
    # and the published face; seconds.
    ("gate_operand_identity",
     ["python", "scripts/e312_gate_operand_identity.py", "verify"]),

    # E313: a shared NAME is not a shared UNIT. E312's single surviving pair (t35 open-fill) matches
    # rel = abs(cost - session_open)/session_open against rel_tol 0.002 while the leg compares an
    # absolute 1e-09, so the gate can only reach the leg through the scale -- and reads them at the
    # producer's own comparison lines: 3 of 30 rows multiply the gate by a clamped scale
    # (tol * max(1.0, x) is relative above 1.0 and absolute below it), one normalises by a fixed 100.0
    # (percent->fraction, so the gate is absolute in the fraction unit), and a count leg cannot be
    # joined to any tolerance by a multiplicative scale. Verify rebuilds from source + both faces.
    ("gate_form_and_scale",
     ["python", "scripts/e313_gate_form_and_scale.py", "verify"]),

    # E314: E313's clamp is a promise about the zero end of a domain and nothing more. This leg
    # publishes, per clamped gate, the switch point in the scale's own units and the tolerance in
    # BOTH regimes in BOTH units (tol*floor flat below the switch, tol*x above it, meeting exactly
    # there), plus the quantity at which a tol*x gate reaches half a unit (0.5/tol). On the three
    # clamped rows that is 5e11 against a face whose largest number is 1,920, so the clamp never
    # engages and the gate is exact equality in disguise; the same pass measures that no face
    # publishes the scale (0 of 30 rows reproducible) and that one row names a face path with an
    # unformatted %s in it. Verify rebuilds from the E313 face and the producers' own faces.
    ("clamped_gate_census",
     ["python", "scripts/e314_clamped_gate_census.py", "verify"]),

    # E315: a two-regime gate only governs a comparison, and the comparison belongs to a leg that
    # carries its OWN epsilon. Joining the five quantity-dependent gates to their legs: four legs
    # publish 0.0, which is exact equality, so no gate tolerance can ever be as tight and the
    # gate's flat regime is merely where it is loosest; the fifth leg (1e-09) crosses a 0.002
    # gate at 5e-07 units of session_open -- below any share price -- so the leg binds across the
    # live range. The leaf measurement is published as NOT-ASSESSED (0 attributable magnitudes)
    # because neither face carries the quantity its gate is rated in: `prev` and `session_open`
    # are not keys there. Verify rebuilds from the E314 face and re-counts. <1s.
    ("leg_epsilon_vs_flat_regime",
     ["python", "scripts/e315_leg_epsilon_vs_flat_regime.py", "verify"]),

    # E316: the constructive half of E315. Per row it derives the smallest reader set from the
    # regime model -- identifier, unit, one magnitude, the scale expression, plus the floor where
    # the gate is piecewise -- and asks which of those the face already prints under another name.
    # The answer splits the two faces by failure mode: three rows sit on a face that publishes 57
    # numbers in the gated quantity's unit and none of them is that quantity (the tolerance a
    # reader would substitute spans 1.5 orders of magnitude), while two rows sit on a face that
    # covers a day with no comparisons at all, where the identifier exists only as a payload key
    # in the producer. 0 of 5 rows lets a reader compute its own gate. Verify rebuilds from the
    # E315 face and re-derives the elements, the decoys and the producer citation. <2s.
    ("gate_print_requirements",
     ["python", "scripts/e316_gate_print_requirements.py", "verify"]),

    # E317: E316 priced the reader set on five rows chosen by E315. This leg carries the same test
    # to every face in results/ that publishes a tolerance leaf: 289 faces, 1108 gates, and the
    # element almost nobody prints turns out to be the unit (1047 of 1108). Only 33 gates are
    # readable from their own face (2.98%) and they sit on two faces, both of them gate tables --
    # while 225 gates publish a same-unit decoy, whose substitution span reaches 19.6 orders of
    # magnitude. Verify re-derives the counts from the published rows and re-checks that the study
    # excluded its own face and script. ~20s (it re-reads all 289 faces to recount).
    ("print_coverage_census",
     ["python", "scripts/e317_print_coverage_census.py", "verify"]),

    # E318: E317's zero-tolerance headline read every tolerance-named leaf as a gate, including
    # leaves that COUNT gates (`n_tolerance_named_not_gate`). This leg re-counts the census under
    # a count-word guard frozen before any number was read: 62 of the 1108 leaves are counts and
    # 53 of the 122 "exactly zero" gates are those counts, so the zero band halves to 69 -- and 68
    # of the survivors sit on this programme's own study faces (E299/E305/E308/E312), leaving a
    # single gate on a real data face (t18 known-answer, whose published observed max is 0.0).
    # The unpruned control must still reproduce E317's five published numbers exactly. ~2s.
    ("zero_tolerance_prune",
     ["python", "scripts/e318_count_named_gate_leaves.py", "verify"]),

    # E319: E318 found 68 of the 69 surviving zero-tolerance gates sitting on four earlier study
    # faces because the exclusion list predated them. That is the shape of the mechanism, not one
    # bad constant: 31 of 45 study faces are censuses, they make 120 census->census row edges, and
    # NO declared exclusion list reaches any of them (19 censuses declare nothing; 8 guard only
    # their own two filenames; the single family-prefix list still counts 7 censuses outside it).
    # This leg rebuilds the graph from the published faces under the frozen pointer rule and
    # re-checks the exclusion audit and the granularity-aware vintage audit. ~3s (reads all faces).
    ("census_self_inclusion",
     ["python", "scripts/e319_census_self_inclusion_sweep.py", "verify"]),

    # E320: of the 219 substitution-span gates E318 left standing, is the gated quantity itself
    # published in the block? 23 are (16 by the gate key's own stem, 7 by the magnitude printed
    # twice), 62 are ambiguous and 134 are not -- so E317's span is a careless-reader bound on a
    # tenth of them and the reading on the rest. Verify re-reads every face from the PRINTCOV
    # commit and re-derives all 219 spans. ~12s (57 faces read through git, not the worktree).
    ("decoy_resolution",
     ["python", "scripts/e320_decoy_resolution.py", "verify"]),

    # E322: E321's verdict sentence says 25 gates "have no producer that publishes the key at
    # all". They do not: the 25 rows are 4 faces and every one of them has a writer on disk. One
    # face is written by the census machinery's own module and was lost to E312's source
    # self-exclusion, one carries a compact date (CASHLeg-20261027) the ISO-only substitution
    # never touches, and two are composed from a format string so the published filename appears
    # nowhere in the writer. Verify re-derives every cause from the sources and re-checks that a
    # caused face carries a writer and an uncaused face does not. <1s.
    ("refusal_cause",
     ["python", "scripts/e322_residual_refusal_causes.py", "verify"]),

    # E323: E322 showed the needle refuses four faces, so E321's 21-of-196 named share was an
    # untested lower bound. Re-priced over the whole population under the wider needle: the 25
    # unowned rows all move to "a producer is found but its constant names nothing" and the named
    # count does not move (21 -> 21), so the share is a repository fact, not a needle artefact.
    # A naively accumulated producer set would report 28 named rows -- the 7 extra names all come
    # from family needles (`etf_book` composes out of `etf_book_bakeoff.json` and matches 106
    # scripts), which is why the study publishes class_naive beside class_after. Verify re-derives
    # every class from the sources under both rules. ~1min (2279 corpus files, 51 faces; the
    # tokenisation is memoised per source, which took the leg from 198s to 58s).
    ("reach_under_wider_needle",
     ["python", "scripts/e323_reach_under_wider_needle.py", "verify"]),

    # E324: E323 left six gates classed "a producer is found but it publishes no key of that
    # name". This leg re-locates all six: four keys are copied wholesale into the card from a
    # sub-face writer (the card embeds `"control": doc.get("control")` and the key is published
    # against the sub-face), one is an accumulation whose key is a data value
    # (`by_kind[r["kind"]]`), and one exists only inside the published face -- no source in the
    # tree mentions the string at all, so that face is not reproducible from the tree it is
    # committed in. Verify re-derives every cause, reason and value identity. ~5s.
    ("unpublished_key_causes",
     ["python", "scripts/e324_unpublished_key_causes.py", "verify"]),

    # E325: the layer under E321..E324 -- every one of those studies took the FACE for granted.
    # 25 of 196 gate rows (12.76 pct) read a face with no writer under the published lookup; a
    # writer-evidence rule reports 164, format templates 11, composed paths 0. Verify re-derives
    # every rung's counts from the tree so the ladder cannot drift from its published face. ~22s.
    ("orphan_gate_faces",
     ["python", "scripts/e325_orphan_gate_faces.py", "verify"]),

    # E326: the layer under E325 -- a template face has a FREE PARAMETER, so a consumer that
    # never carries it quotes a number whose question it cannot state. Of 30 faces, 20 are
    # parameterised, 18 republish the parameter beside their numbers, and all 14 consumers
    # outside the writers pin it or supply it from their own constant (0 unpinned); 11 faces
    # stay reachable through 143 *_latest pointers, which is the next study's population.
    # Verify re-derives every consumer class from the tree so the census cannot drift. ~2s.
    ("template_parameter_consumers",
     ["python", "scripts/e326_template_parameter_consumers.py", "verify"]),

    # E327: the 143-pointer layer E326 measured and did not traverse. Traversing it shows most
    # of it is not a pointer layer: of 143 (pointer, face) pairs only 3 are pointers (the sibling
    # is a content-identical copy of the dated face); 3 cite it through source_faces and 137 are
    # other faces that merely CENSUSED it (faces_censused / rows[].face). The helper's substring
    # test counted "a face that measures it" as "a pointer to it". The 3 real pointers all carry
    # evidence_cutoff, so the parameter survives one indirection. Verify re-derives every pair
    # class from parsed content, so the count cannot drift. ~2s.
    ("who_reads_a_face_through_a_pointer",
     ["python", "scripts/e327_who_reads_a_face_through_a_pointer.py", "verify"]),

    # E328: a stated cutoff is not a fresh one. 550 dated faces group into 416 (directory, stem)
    # families; 68 hold more than one cut, so 133 faces sit on a cutoff their own family has
    # outgrown. Only 4 of those are actually quoted by code (a non-writer source names the literal
    # basename and subscripts a key); those 4 carry 1,430 numbers of which 536 disagree with the
    # newest cut and 0 have no fresh counterpart. Verify re-derives the verdict, the summary and
    # every row's cutoff and change count. ~3s.
    ("quoted_number_staleness",
     ["python", "scripts/e328_quoted_number_staleness.py", "verify"]),

    # E329: E328 measured numbers on a stale cut and assumed one file per source. A source can name
    # two: 9 of 597 (source, family) pairs name two vintages of one stem (8 with two dated cuts,
    # 1 pointer pair), only 2 have both cuts on disk, and 2 more bind them to separately named roles
    # (ASOF/FRESH) so nothing races. One pair is order-decided: e242's _face_file tries the
    # *_latest pointer first and falls back to a pinned 2026-10-29 cut -- and that order has no leg
    # covering it. On today's disk all 4 of its call-site stems are served from the pointer, but 2
    # of them (owncross, sharediff) hold a newer 2026-10-30 cut that the pinned fallback would
    # silently miss if the pointer ever disappeared. Verify re-derives the pair classes, the call
    # sites and every on-disk exposure from the tree. ~7s.
    ("two_vintage_binding",
     ["python", "scripts/e329_two_vintage_binding.py", "verify"]),

    # E330: E329 named one order-decided resolver; this asks the wider mechanical question -- across
    # the tree, which constructs pick between two references to one family, and which of those
    # decisions no assertion names? Four classes (existence chain, `or` fallback, argparse default,
    # mutable default arg). Of 1 decision the tree actually makes (e242's _face_file), 0 are pinned,
    # and 2 of its 4 call-site stems hold a pointer one cut ahead of the pinned fallback, so a
    # two-line swap would return 2026-10-29 instead of 2026-10-30 today. 34 `or` lines carried a face
    # on one side only and are published as rejected rather than silently dropped; 0 mutable
    # defaults exist in 646k code lines. Verify re-derives every row, both pin indexes and the
    # per-stem evidence. ~40s (corpus scan).
    ("unpinned_choice",
     ["python", "scripts/e330_unpinned_choice.py", "verify"]),

    # E331: E330's sibling question for the pointer layer -- who resolves a family through a
    # *_latest pointer and nothing else, and what a missing pointer does to them? 44 (source,
    # family) pairs reach a family only through a pointer: 3 only write it, 6 are chains whose
    # first candidate is a variable, 11 publish the name without loading it, and 24 are real
    # pointer-only readers over 19 families. None is silent: 9 raise at the file and 15 branch
    # first (existence 6 / try 4 / `or {}` 2 / None branch 2 / callee absorbs 1). The disk half
    # finds no absent pointer and no pointer whose stated cut lacks a dated sibling; 3 families
    # cannot be judged because the pointer is their only published form. It also measures a bound
    # that touches every corpus study: 22 sources lose their tail to the scanner's docstring rule
    # (up to 531 lines), so a load site written there is invisible. Verify re-derives every row,
    # the handling classes, the disk half and the tail list. ~45s (corpus scan).
    ("pointer_only_readers",
     ["python", "scripts/e331_pointer_only_readers.py", "verify"]),

    # E332: E331's tail count (22 sources) is only the part of the helper's blind spot that reaches
    # the end of a file. The tokenizer finds 30 sources carrying 4,284 real code lines the helper
    # never shows (157 defs, 103 load lines, 18 face handles, 187 selftest mentions), 22 of them in
    # several disjoint spans. Re-pricing E331 against the recovered corpus moves the pointer-only
    # reader count 24 -> 25 (e312's gatetol pointer is a reader once its load site is visible) and
    # flips that pair out of reference_without_a_reader; the verdict itself does not move.
    # Verify re-derives every source row and the whole re-pricing block. ~2 min (corpus scan x2).
    ("invisible_tail_recovery",
     ["python", "scripts/e332_invisible_tail_recovery.py", "verify"]),

    # E333: four other consumers read the same helper (E326 template parameters, E328 quoted-number
    # staleness, E329 two-vintage binding, E330 unpinned choice), so their counts are floors of the
    # same shape. All four are rebuilt twice over ONE file list (shipped helper vs tokenizer) and
    # every numeric leaf is diffed: 17 of 69 published numbers move, NO verdict flips, and every
    # moved number is reproduced by recovering a single source (11 of them exactly by that source).
    # The face also carries the other axis as a control: the shipped half does not reproduce the
    # published faces because the corpus has grown since they were written. Verify re-runs all four
    # consumers twice plus the ablation. ~6 min (12 builds + 17 single-source builds).
    ("surviving_e3xx_conclusions",
     ["python", "scripts/e333_surviving_e3xx_conclusions.py", "verify"]),

    # E334: E333 answers "do the conclusions survive" for four consumers; it does not answer
    # "should the helper be fixed today". That is a blast-radius question, so six consumers
    # (E326/E327/E328/E329/E330/E331) are rebuilt twice over ONE corpus and the radius is measured
    # on three axes: the delta (numbers the repair moves), the published faces (what a reader of
    # today's face would have to re-read), and the evidence (what the repair erases). The last axis
    # is the decisive one: E332 exists to state the defect's size and collapses to zero under the
    # repair, and E333 compares two functions that become one. The decision rule is code
    # (decide()), so the recommendation cannot drift from the numbers. Verify re-runs six consumers
    # twice plus the shared ablation. ~5 min.
    ("helper_repair_blast_radius",
     ["python", "scripts/e334_helper_repair_blast_radius.py", "verify"]),

    # E335: the landing E334's rule asked for. e326 exports code_lines_tokenized beside the shipped
    # code_lines (pinned as code_lines_legacy), no consumer is switched, and the face proves it:
    # both readings differ on 1369 of 2294 sources, E334's 30 published deltas re-derive through the
    # new name at 1e-9, and an AST scan finds zero permanent rebinds and zero readers of the new
    # name. Verify re-derives the face over the corpus (~10 s, no builds).
    ("sibling_entry_point",
     ["python", "scripts/e335_sibling_entry_point.py", "verify"]),

    # E336: E335 landed the reading and E334 priced the repository; this prices ONE consumer at a
    # time, twice. Reading A (delta) rebuids each of the six consumers against the landed name and
    # counts how much of its own answer is the helper's defect; reading B (publish) compares the
    # consumer's published face with that tokenized build and counts what a reader must re-read.
    # The two orders agree on the head (E330, 0 delta / 1 published number) and swap E328/E329 in
    # the middle, so the verdict refuses to name a candidate and publishes the disagreement.
    # Verify re-prices all six consumers twice (12 builds, ~2-3 min).
    ("consumer_optin_ranking",
     ["python", "scripts/e336_consumer_optin_ranking.py", "verify"]),

    # E337: E336 refused to rank but published a floor -- E330 is cheapest on both readings -- and a
    # recommendation that names a floor is not a measurement of the opt-in.  This leg executes that
    # opt-in: E330 reads the tokenized name through one local accessor, its face is republished, and
    # the diff is published in three arms so corpus drift cannot be billed to the reading (drift =
    # before -> shipped control, total = before -> republished, switch = control -> republished).
    # On today's tree the opt-in moves 0 of 21 numbers and no decision row; the one number a bare
    # diff shows (sources_scanned 2292 -> 2297) is the corpus.  A moved verdict or a failed
    # re-derivation reverts the source and the face, so verify also asserts that the consumer file
    # is in the state the published verdict claims.  Verify rebuilds all three arms (~75s).
    ("optin_executed",
     ["python", "scripts/e337_optin_executed.py", "verify"]),

    # E338: E337 showed the opt-in itself was free and the only cost the diff carried was the
    # corpus -- a population-definition claim.  Every census face counts its population off the
    # disk, so it re-derives only while no .py moves.  This measures that on the repo's own
    # history: landing commit -> the next commit touching any .py, two readings (all touches /
    # touches outside the census family), and pinning priced on size + a measured read + the
    # object dependency it creates.  On today's history 15/15 windows close on the next census
    # sibling and both readings pick the same commit, so the split is published as vacuous:
    # research ships its own S6 wiring in the same commit as the face.  Verify re-derives the
    # face over git history (~5s, no builds).
    ("census_green_window",
     ["python", "scripts/e338_census_green_window.py", "verify"]),

    # E339: E337 repaired one hard-coded inertness guard and its digest named the silent branch --
    # a guard that hard-codes a count gets quietly loosened rather than repaired.  This counts the
    # literal-count guards in smoke_test.py and the S6 leg table (86 at head) and reads git history
    # for every commit that *deletes* a line in those files (41 commits, the only place a relaxation
    # can happen): 2 relaxations, both predicate replacements of the T+1 invariant, 0 literal raises,
    # and none of the 7 exact-count guards counts a corpus.  The "was it paid for by a republished
    # face" reading is priced against a base rate -- 39 of 41 such commits move a results/ number
    # anyway -- so it is published as uninformative rather than as evidence.  Verify re-derives the
    # whole face (~7s).
    ("literal_count_guards",
     ["python", "scripts/e339_literal_count_guards.py", "verify"]),

    # E340: E337's repair read a study's own published allowlist back out of its face, one hop from
    # self-authorization.  This walks every published face (12,519 parsed) and keeps the 409 entries
    # whose key carries a permission word over 98 keys, classifying each by access shape: does the
    # script that publishes the face read the key back, and is the value compared against a fresh
    # one, asserted, gated, or merely bound (use invisible downstream)?  22 entries over 22 faces
    # are read back by their own producer, and 17 of the 18 gated/bound grants have no selftest leg
    # quoting the key -- customary, not pinned.  Verify re-derives the face off disk (~90s).
    ("permission_allowances",
     ["python", "scripts/e340_who_authorizes_whose_allowance.py", "verify"]),

    # E341: E338 measured 15/15 census windows closing on the next sibling and could not split
    # research from production because one commit lands a study and its wiring. This takes that
    # closer apart: every one of the 16 closers adds a census study AND edits Tools/s6_chain; the
    # added member always introduces a name nothing named before (its own face, 16/16) and names
    # an already-published stem in 8/16; the wiring half moves 0 names while editing 360 lines in
    # place, so it is visible to every counting face and invisible to the name census. At the
    # pinned tree, dropping the 16 family files costs 0.7% of sources / 1.3% of lines and leaves
    # 15 of 22 measured names with no writer at all. Verify re-derives the whole face (~55s).
    ("sibling_closer", ["python", "scripts/e341_sibling_closer_what_changed.py", "verify"]),

    # E342: E339 priced the loosening of literal-count guards and its pay-for reading was almost
    # vacuous (39/41 commits touch a face and move a number anyway).  This asks the general
    # question over every *named* assertion: smoke_test.py's check(label, condition, detail) calls
    # and the S6 LEGS table.  41 commits scanned -> 8 events (5 rewrites under the same name, 3
    # checks that vanished and came back).  0 of 5 rewrites left the new acceptance set in a
    # published face, 1 left a commit message, 1 left nothing at all -- c169c702, the shape the
    # card named, reproduced independently.  2 rewrites are renames and 1 moved its reach behind a
    # helper name, so the check's text no longer says what it accepts.  Verify re-derives the face
    # off git history (~40s).
    ("guard_rewrite_records",
     ["python", "scripts/e342_guard_rewrite_records.py", "verify"]),

    # E342's part (c), shipped as the mechanism itself: a staged-tree claw that refuses a commit
    # changing a gate's reach with no results/ change staged and no GUARD-REACH: line naming the
    # new reach.  Selftest only (it judges the index, and the chain runs while the tree is dirty).
    ("guard_reach_claw", ["python", os.path.join("Tools", "guard_reach_claw.py"), "selftest"]),

    # E270: the screen E267/E268 published is a rule over four per-row numbers (b, band_lo,
    # band_hi, own_p95), so its reach is bounded by which published faces actually carry them.
    # This leg walks all 17 dated BAND* faces (mirrors and its own face excluded) and finds the
    # triple on 4 collections / 72 record-readings while 26 verdict-bearing collections (536
    # records) state a judgement without any of the four -- and cross-checks the shared values
    # instead of assuming presence: 420 of 420 joined cells agree with the canonical row
    # (max |diff| 0.0), so the gap is coverage, not disagreement. Published faces only. <1s.
    ("guard_field_audit",
     ["python", "scripts/e270_guard_field_audit.py", "verify"]),

    # E273: the guard's missing triple is not a barrier -- outside(m) <=> m < t_max_end is exact,
    # so a face publishing the threshold plus own_p95 (and donor_p95 for pair screens) is fully
    # re-runnable (36/36 on all three published rules, residual 0.0/0.0, zero band columns
    # consulted). What it cannot survive is dropping the RULE: 18 of 36 rows carry two different
    # published thresholds and 6 read a different verdict on them. Verify mode re-derives from the
    # sources, never from its own summary. <1s.
    ("guard_from_threshold",
     ["python", "scripts/e273_guard_from_threshold.py", "verify"]),

    # E271: the 48 published (donor, recipient) pairs were always read ONE donor at a time, so a
    # reader of a single recipient could not tell whether "do not borrow" or "do not borrow from
    # THIS cell" was the finding. This leg sweeps every donor end each (leg, base) group offers
    # for every measured row (own cell as the control) and asks whether the moved ROW SET is the
    # same across donors: 3 of 4 groups are invariant, cross:60 is not -- only all_five (the
    # widest end 2.2963, and E262's published dominator there) moves anything, the 2 rows it
    # moves are exactly the 2 whose flip multiplier (2.1965 / 2.1384) falls inside the group's
    # p95 spread [1.9678, 2.2963], so the published choice is the LEAST conservative in that
    # group. Verify mode re-derives from the source face, never from its own summary. <1s.
    ("donor_choice_sensitivity",
     ["python", "scripts/e271_donor_choice_sensitivity.py", "verify"]),

    # E343: E340 published 18 "bound" self-reads whose use is invisible on the access line. This
    # leg follows each bound name to its first downstream use. Two corrections fall out of it: 10 of
    # those 18 are stores into the loaded dict (``st["expected_cutoff"] = expected``), not reads, and
    # of the 14 real reads only 1 has no comparison and no test anywhere downstream. Verify re-derives
    # the face from E340's source face (~1s, no builds).
    ("bound_grant_decisions",
     ["python", "scripts/e343_bound_grant_decisions.py", "verify"]),

    # E344: E341 measured that fifteen names lose every *writer* outside the census family, which
    # is a statement about producers. The consumer question is a different one and it is answered
    # here: no source outside the family loads one of these faces by name, five directory censuses
    # read every published face without naming it, and exactly one carries a published `verdict`
    # forward. The leg re-checks each cited reader's evidence at the pin, so a rewritten reader
    # turns this red instead of leaving a stale claim behind (~4s, no builds).
    ("face_consumer_census",
     ["python", "scripts/e344_face_consumer_census.py", "verify"]),

    # E345: E342 measured that three deleted smoke checks came back. This leg measures the window
    # they were gone: the 29-mainline-commit / 67-commit, 9.26-hour gap between r1227's removal and
    # r1243's union-merge restore spans 10 rounds in which the suite ran 37 times and in which NO
    # other check on the futures-TSMOM face asserted the property. Verify re-derives the windows
    # from git and logs/ (never from the face it is checking) -- a rewritten restore or a gate that
    # reappears earlier turns it red (~3s, no builds).
    ("gate_absence_windows",
     ["python", "scripts/e345_gate_absence_windows.py", "verify"]),

    # E346: E343 excluded ten `st['key'] = value` stores from its bound-read count because they
    # write into the dict that was just loaded. Those stores are still statements a reader may
    # trust, so this leg asks the other half: of everything the status writers file, which keys
    # does NO consumer read, which are fed only by the writer's own next run, and which of those
    # a branch actually tests (a latch: a hand-edited status file changes the next decision).
    # Verify re-derives the census from the producers' ASTs and the reader corpus (~5s, no builds).
    ("status_writer_unread",
     ["python", "scripts/e346_status_writer_unread.py", "verify"]),

    # E347: E344 measured who reads a face; this asks whether the number decides anything. Every
    # dated face under results/ is followed from its load site (named literal or directory sweep)
    # to the comparison that consumes it, with the decision class and where the bound is pinned.
    # Verify re-derives the census from the pinned corpus and face listing (~40s, no builds).
    ("published_number_gates",
     ["python", "scripts/e347_published_number_gate_census.py", "verify"]),

    # E348: E345 measured that the futures-TSMOM check was gone for 9.26h and asked whether
    # anything else covered it. This leg asks whether there was anything to be wrong about: it
    # replays every commit of the window from its own tree and evaluates the five clauses the
    # restored check literally compares. Reading: the face is absent for all 28 window commits,
    # and it first appears in the SAME merge that restores the check -- so the window was empty,
    # not clean. After the restore the gate is green in all 279 commits for a reason worth
    # keeping: one distinct face blob and one panel tail (2026-10-28, unchanged since), i.e. 279
    # green runs are one observation repeated. Verify re-derives from git through the face's own
    # replay_head (~2s, no builds).
    ("restored_gate_retrospect",
     ["python", "scripts/e348_restored_gate_retrospect.py", "verify"]),

    # E349: E347 found no dated face gates an operational decision and published the bound -- the
    # live readers sit on the *_latest mirrors and the live state files a round rewrites in place.
    # This leg measures that channel: 87.8% of its 139 files are opened by an in-repo source and
    # 45.3% reach a comparison, but the one comparison only a mirror can carry -- "is this pointer
    # current?" -- appears in 14 of 840 non-fixture comparisons and in 2 of 235 operational ones.
    # Of the 119 sources the chain itself names, 2 read the channel and neither asks freshness.
    # Verify re-derives the whole census from the face's pin (~2 min, AST over 1109 sources).
    ("latest_mirror_channel",
     ["python", "scripts/e349_latest_mirror_census.py", "verify"]),

    # E350: the FIELD, not the file, is what a hand edit touches. 2289 (face, field) pairs are
    # read across 2341 sources; 230 are read by a guard and 131 of those have no writer anywhere
    # in the corpus, so the guard can only fire on a missing value. Verify re-derives the census
    # from the face's pin (~3 min, AST over the corpus).
    ("field_level_branch_census",
     ["python", "scripts/e350_field_branch_census.py", "verify"]),

    # E351: of the 92 `product:` smoke gates, 37 read a literal subject face and 6 of those have
    # never seen their subject change -- but all 6 subjects are younger than 50 commits, so no
    # gate here has been green against a subject that stopped moving long ago. Verify replays the
    # blob history at the face's own pin (~10 s of git object reads, no evaluation).
    ("gate_state_census",
     ["python", "scripts/e351_gate_state_census.py", "verify"]),

    # E358: E351 left 55 gates unresolved because a subject written as ``os.path.join(...)`` is
    # three literals, none of which looks like a path. Folding one step resolves 40 of them (31 of
    # those subjects never moved in 300 commits), 8 read whatever a directory holds and 7 name no
    # file at all. Verify re-derives the folding and the state classes at the face's own pin
    # (~5 s, one git replay + AST).
    ("subject_resolution",
     ["python", "scripts/e358_subject_resolution.py", "verify"]),

    # E359: E353 recorded that part of E350's unwritten-guard population names files only a
    # selftest writes.  Measured: scaffolding is 3.7 pct of 5,444 read sites and 10 of 139
    # unwritten guards, so E350's headline survives at 129 -- but 24 faces are read ONLY by
    # scaffolding (fixture dirs, .tmp trees, short-name copies of real status faces), and
    # 23.5 pct of reads report a face their own function never names. Verify re-derives both
    # populations, both deltas and the leak axis off the current corpus (~50 s of AST).
    ("census_scaffolding_split",
     ["python", "scripts/e359_census_scaffolding_split.py", "verify"]),

    # E364: E363 stamped two faces and found replay needs a files= seam. This leg holds the whole
    # published census family to that question every round: of the studies that enumerate a
    # directory, which quote a population, which name the corpus they counted, and which have no
    # seam so their number can never be rechecked. ~4 s (121 faces, no builds). A study that loses
    # its address is a regression (rc 1); a study new to the queue is reported, not failed, because
    # the queue is allowed to grow with the repository.
    ("unstamped_census",
     ["python", "scripts/e364_unstamped_census.py", "check"]),

    # E365: E364 named this queue head and left it open -- can a *published-face* population be
    # pinned and replayed like a source population?  It can, and the first draft proved why the
    # address must be byte level: one of 591 faces is UTF-16, so a text digest gave it two
    # identities depending on which decoder read it.  Every round this leg rebuilds the population
    # from git blobs + the inline store only (no work-tree read, ~8 s) and asserts the pin
    # reproduces, the store covers exactly the un-suppliable members, and the study's own faces
    # stay out of its own population (E319 applied at the pinning layer).
    ("face_population_pin",
     ["python", "scripts/e365_face_population_pin.py", "check"]),

    # E366: E365 proved the pin works but priced it per study, and E364's queue read as thirteen
    # rounds.  This leg re-derives the bill every round: the thirteen queued studies walk TWO
    # populations (2,387 in-repo sources, 593 published faces), so the pin work is two pins and the
    # rest is seam repair -- and it separates a real build(files=) parameter from a local named
    # files and from prose that says the word (a text grep calls six of eleven seams; none of them
    # is one).  Decision keys must be bit-stable; the bill is published as drift because other
    # lanes write this working tree all day (~2.5 s: six cached imports, two git passes).
    ("pinable_queue_size",
     ["python", "scripts/e366_pinable_queue_size.py", "check"]),

    # E370: E368 compared four keys and found one stable, one moving 20% -- a result about four
    # keys, not a rule.  This leg re-derives the whole per-key table from the published arms
    # (no scan: verify re-classifies the stored summaries and re-counts the classes, ~1 s) so an
    # edited summary, rule or class cannot leave the face claiming a shape the numbers lost.
    ("key_sensitivity",
     ["python", "scripts/e370_key_sensitivity.py", "verify"]),

    # E371: E370 priced keys, E372 paid the bulk store, and the single store_needed member was
    # still unpriced.  This leg re-derives the footprint counts, the moved sets and the verdict
    # from the published face (~1 s), so a hand-edited delta or a verdict that no longer follows
    # from its own rows cannot ship.
    ("store_member",
     ["python", "scripts/e371_one_store_member.py", "verify"]),

    # E352: E349 priced the channel as a population and found 14 of 840 comparisons ask whether
    # what they read is current; this prices the window instead, in the repository's own clock.
    # 60 deciding channel files, 59 measurable: median file lag 80 commits / p90 111, worst
    # state-bm-c.json at 216 commits (59.3 h), 54 with a decide-time stale instance, 7 gated.
    # Verify re-derives the summary at the face's own pin (~40 s of first-parent git walks).
    ("staleness_window",
     ["python", "scripts/e352_staleness_window.py", "verify"]),

    # E353: E350 published 131 guard fields no source writes and could only say "the guard can
    # fire on a missing value". Against the tree today: 23 raise before the guard runs (16 name a
    # file that is nowhere, 7 a basename several files share, each refused rather than
    # first-matched), 5 read a field that is absent or null, 103 read a value of which 34 read
    # falsy -- so 4 faces of one writer each close the whole alert class, and a fifth of the
    # population cannot be fixed by any writer because its face name is not one file. Verify
    # re-reads the disk for the published pairs (~4 s, no AST).
    ("unwritten_guard_presence",
     ["python", "scripts/e353_unwritten_guard_presence.py", "verify"]),

    # E241: E238's pair does not reproduce on the common grid, and the ladder rung that carries
    # it is the READER, not the market: E240's share/book design paired a y vector indexed by
    # the kept session with increments re-paired from k=1, so the dependent variable sat one
    # session behind its regressors (6630 of 6635 rows). One change per rung, and every rung
    # publishes a_share, the denominator coefficient and the derived rest channel.
    ("pair_reproduction", ["python", "scripts/e241_pair_reproduction.py", "run"]),
    # E242: every design in this family whose regressor set leaves a member out inherits an
    # omission factor (E240 measured 1.89 on one design). This leg walks the published slopes,
    # classifies them by how many members they omit, re-prices them on one identified grid and
    # states which published numbers are LEVEL artefacts and whether each verdict survives.
    ("omission_inflation", ["python", "scripts/e242_omission_inflation_sweep.py", "run"]),
    # CEO-facing pages
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    # E210: the pages above are the ones the CEO opens, so the leg that asks whether
    # their numbers can be traced to a face cell has to run after them, not before.
    ("docquotes", ["python", "scripts/e97_routing.py", "docquotes", "--publish"]),
    # E211: the same sweep as a ratchet -- a page family that starts printing a number
    # no face produces turns this leg red instead of waiting for the next audit.
    ("pagegate", ["python", "scripts/e97_routing.py", "pagegate", "--publish"]),
    # fleet / bookkeeping guards
    ("machine_health", ["python", "Tools/machine_health_face.py", "check"]),
    # r1336: this leg used to be `audit` -- it reported a drifted GPU face and did nothing, so
    # the face stayed half-owned (33 aliases written at four different samples; smoke read
    # free=3789 beside free=3025 MiB, spread 764 MiB) until a human ran repair by hand. A verdict
    # that no next step consumes is not a gate (r1288). `apply` re-probes once and rewrites every
    # alias from that one sample; on probe failure the GPU keys are dropped with a warning rather
    # than invented, so the leg is fail-safe on a parked machine.
    ("gpu_face", ["python", "Tools/gpu_face.py", "apply"]),
    ("attrition_guard", ["python", "scripts/attrition_ledger_guard.py", "scan"]),
    ("pool_audit", ["python", os.path.join("scripts", "pool_audit.py")]),
    ("token_meter", ["python", "scripts/token_meter.py"]),

    # E352: E349 counted the channel and left the window unsized -- 14 of 840 comparisons ask
    # whether what was read is current. Verify re-walks the first-parent history over 240 commits
    # and re-derives, per deciding file, the blob a reader would take at each boundary plus the
    # boundaries where gate code ran newer than the artifact it read. Contents come from the
    # working tree only (this clone is blob:none; `git show` / `git grep` start a lazy fetch and
    # hang the round) and only `git log` / `ls-tree` metadata is asked of git. ~4-6 min.
    ("staleness_window", ["python", "scripts/e352_staleness_window.py", "verify"]),

    # E357: E352 measured how far behind the copy a reader takes is, but not why. Against the same
    # 240-commit first-parent window and the same 59 files: 46 are written exactly ONCE in the
    # window (a face published and never refreshed -- an age, not a cadence), so only 8 files have
    # a rewrite interval to compare a lag against, and those split 4 inside / 4 beyond. 1237 of
    # 1291 declared writer pairs never co-changed with the file they are said to write, and 54 of
    # them are the suite itself. Verify re-derives classes and the partition (~2 s, one git log).
    ("channel_writer_cadence", ["python", "scripts/e357_channel_writer_cadence.py", "verify"]),

    # E371: E366 billed the store as the expensive half of a pin and left the store_needed members
    # as a footnote. The footprint is measured twice (the pin's bytes carry a BOM, so "unparseable"
    # and "contributes nothing" are two different zeros), the missing-writer question is asked by
    # name against the E350 guard table, and the bill is a replay with the store excluded. Verify
    # re-derives both footprints and the source-count arithmetic (~2 s, no corpus scan).
    ("store_member_cost", ["python", "scripts/e371_store_member_cost.py", "verify"]),
    # E377: the tree-wide version of the same question -- 542 of 2,121 json.dump destinations in
    # the corpus cannot be named, and 36 published faces are reached only by those writers. Verify
    # re-adds every writer row and re-derives the verdict from the published summary (~0.3 s).
    ("unresolved_destination", ["python", "scripts/e377_unresolved_destination.py", "verify"]),
    # E381: E377's blind-spot list ships one face a resolved load already reads -- the census keys a
    # join by its operands, so a three-component path lands under a bare basename. Verify re-adds the
    # rows and the three named causes, and re-derives the verdict (~2 s, no corpus scan).
    ("component_key_blind_spot", ["python", "scripts/e381_component_key_blind_spot.py", "verify"]),
    # E382: prices the repair of that keying before anyone patches it -- two arms over the
    # same corpus; 10 of 11 published headlines move and E350's verdict string changes
    # 131 -> 148, so the fix is a republish decision. Verify re-derives every delta from the
    # stored rows (~1 s, no corpus scan).
    ("key_projection_delta", ["python", "scripts/e382_key_projection_delta.py", "verify"]),
    # E383: the same key set asked the collision question -- how many distinct files on disk one key
    # names. Three keys merge 40 identified files (the trial-labor family alone puts 20
    # prep_state.json under one key), five keys are coarser than any one file, and seven merged keys
    # are quoted from a published face's key list. Verify re-adds the four states and the table
    # (~0 s, no corpus scan, no disk walk).
    ("shared_key_collision", ["python", "scripts/e383_shared_key_collision.py", "verify"]),
    # E387: a red that compares a published face with a fresh build has two causes -- the corpus
    # moved (republish) or the face never reproduced (seam). Verify re-derives the frozen verdict
    # set and the tally from the published face (~0 s, no corpus scan, no disk walk).
    ("republish_audit", ["python", "scripts/e387_republish_audit.py", "verify"]),
    # E388: E386 published that the two merged trial-labor basenames hold 31 key sets but not
    # which failure that is. Measured per consecutive wave: 26 walls only add fields and 3 remove
    # them (16 and 18 at w16->w17, one at w19->w21), 0 fields are ever re-added, and 2 of the 4
    # dropped numerics are gone (n_survivors 40, n_distinct 173) while 2 survive under another
    # name. Verify re-reads the family and re-derives every published count (~0.3 s).
    ("schema_accretion", ["python", "scripts/e388_schema_accretion.py", "verify"]),
    # E390: E388 priced which fields each wall drops but not who reads them. Measured statically
    # over every .py in the repo: 0 readers ask a dropped field of a wave past its last sighting;
    # the 148 live reads are historical runners on waves 10-16, 45 rows open another face, 33 read
    # a local dict and 80 cannot be resolved. Verify re-derives every row and count (~1 s).
    ("wrong_side_reader", ["python", "scripts/e390_wrong_side_reader.py", "verify"]),
    # E391: E390 showed that a matching key name is not a face read; this asks the other question
    # about the same names -- which published key name is a number in one face and a container in
    # another. 12,313 faces / 80,411 key names -> 7,797 structural conflicts, split into 3,877
    # field-shaped names and 3,920 row-map index keys (an index is not a name: measured, not assumed
    # away); 2,216 field-shaped conflicts are named by >=1 in-repo literal (132,588 sites, a
    # name-matched upper bound and not a face resolution) and 1,661 are latent. Verify re-derives
    # every published count from the listed conflict rows (~1 s, no corpus walk).
    ("key_name_two_meanings", ["python", "scripts/e391_key_name_two_meanings.py", "verify"]),
    # E392: E391 published a name-matched bound and said so in the field name; this prices it.
    # 112,910 reads name one of the 3,877 conflicted keys, but only 25,461 of those reads are on a
    # container the resolver can call a face at all (22,714 read a local dict, 64,735 cannot be
    # typed), 9,243 reach a face path, and 5,763 open a face that stores the key -- 5.1% of the
    # name-matched bound, or 22.6% of the reads that are demonstrably on a face. 188 open a face
    # that does not carry it; 3,292 land on a face above the 1 MB read cap, so the largest faces are
    # exactly the ones the check cannot see (3,271 too_large / 21 unparseable). 711 keys have <=3
    # reads and only 29 of them are confirmed sightings. Verify re-adds every published count from
    # the per-key rows (~0 s, no corpus walk).
    ("read_resolve", ["python", "scripts/e392_read_resolve.py", "verify"]),
    # E393: prices the 1 MB read cap E392 named as the reason 3,292 of its resolved reads were
    # unreadable. 3,271 of those were size refusals; a byte-level presence scan over the 195 faces
    # they open finds 3,241 store the key and 30 do not, on a byte-identical name-matched total, so
    # the 0.051 share is a lower bound and becomes 0.0797. Verify re-adds the cap arithmetic and
    # both shares from the per-key rows (~0 s, no corpus walk, no byte scan).
    ("read_cap_price", ["python", "scripts/e393_read_cap_price.py", "verify"]),
    # E394: the other direction -- 218 reads resolve to a face that does not store their key (188
    # under the cap, 30 the cap had been hiding). Each is classified as depth / producer-writes /
    # a face another read witnesses / counted-but-unwitnessed / unparsed / dead, and only the last
    # is a broken reader. The producer test is structural (dict literal, subscript store,
    # setdefault), never co-occurrence of the face name and the literal. No published ratio moves.
    # Verify re-adds the per-key rows and the class counts (~0 s, no corpus walk).
    ("phantom_why", ["python", "scripts/e394_phantom_why.py", "verify"]),
    # E395: E394's producer-named class, asked the honest follow-up -- does the producer write the
    # key on every path? Measured as an AST path position (if/try/loop/with -> a branch, function
    # body -> inside_a_callable, module body -> unconditional) AND as a dump target: a dict literal
    # carrying the key is only evidence about this face if it reaches a dump of this face's file
    # (direct argument or one name hop). 131 reads / 39 (key,face) pairs: 19 pairs are attribution
    # failures -- the unconditional writer writes ANOTHER document -- 6 are on a branch, 5 only
    # inside a callable, 8 mixed, and 1 writes this very face unconditionally. Verify re-derives
    # every pair verdict from the published producer rows (~0 s, no corpus walk).
    ("conditional_write", ["python", "scripts/e395_conditional_write.py", "verify"]),

    # E396 prices the single same-document pair E395 published instead of believing it: the dump
    # target is published as a literal string (results/autofill_state.json), the face's own history
    # is read over exactly that path, and the read site is quoted.  The claim existed because the
    # dump test was `face_basename in value` -- a substring test -- and `state.json` is a proper
    # suffix of `autofill_state.json`, so E395's one "writes this very face" pair re-derives to
    # zero under an exact-basename test.  Verify re-derives each dump-target class and each moved
    # pair from the published rows (a few s, one history walk).
    ("last_tick", ["python", "scripts/e396_last_tick.py", "verify"]),

    # E396's sibling re-resolves the same pair with a path-segment matcher and A/Bs E395's own walk
    # (identical population, 39 pairs both arms, exactly 1 pair moves and loses its same-document
    # claim), then publishes the tree-wide basename exposure as a census instead of one anecdote:
    # 18,342 faces, 2,253 basename-suffix pairs, 133 distinct short basenames.  Verify re-derives
    # the witness' dump classes and the A/B arithmetic from the published rows.
    ("face_basename_suffix", ["python", "scripts/e396_face_basename_suffix.py", "verify"]),

    # E385 answers the question E383 left open for a republish decision: would splitting the keys
    # that name two or more files move a published NUMBER?  Four headlines are re-derived under two
    # keyings from the same population -- E350 faces_named (862 names carry 1002 documents, 19 names
    # merge >=2, largest 28), E353 pairs (131 key-level pairs -> 210 document-level, by_class
    # 5/103/23 -> 80/108/22), and the two face lists (E377/E381), whose unit is a path and so cannot
    # move.  Of the 7 pairs on an ambiguous key, 2 are settled by naming the single in-census member
    # (the other member sits outside the census walk) and 5 stay undecidable inside it -- so the
    # split both prices a republish and says which part of the ambiguity is the index's.  Verify
    # re-derives every arm's delta, the class sums and the decision gate without the corpus walk.
    ("merged_key_split", ["python", "scripts/e385_merged_key_split.py", "verify"]),

    # E397 takes E385's untested sentence ("merged names whose ambiguity is only outside the census
    # walk = 0") and measures it per NAME over all 884 published keys (862 read half + 22
    # write-only), resolving each key to files and testing that set against BOTH walk rules the
    # tree contains: E350's whole-tree drops (Money02/legacy/media/Money0923) and E391's path-part
    # drops (.git/__pycache__/_quarantine/node_modules/.codely-cli/_smoke).  20 keys are ambiguous:
    # 19 keep two or more files inside every walk (the ambiguity is the DATA -- naming a member is
    # a decision, not a cleanup), 1 (`p1d_gates.json`) flips class depending on the rule because one
    # of its two files is a quarantine snapshot, and 0 collapse under a rule, so the repair list is
    # empty and the bill is a rule (pick one skip set = the union) rather than a split.  Verify
    # re-resolves every published row from the tree and re-derives the classes and the gate.
    ("walk_ambiguity", ["python", "scripts/e397_walk_ambiguity.py", "verify"]),

    # E399 prices the residual E397 left as a bare count: 98 published keys resolve to no file, and
    # "no file" is not one bill.  Each one is tested against a wider index (only .git/__pycache__
    # skipped), a form test (repo-relative path vs bare basename vs bare token vs template vs
    # absolute), and -- for the repo-relative ones -- a neighbourhood test (does the directory
    # exist, is the "directory" in fact a FILE, is there a same-stem sibling under another date).
    # 66 of the 98 were never path claims (52 basename fragments whose directory is a runtime
    # variable, 13 templates, 1 bare token), 1 is a Money02 file the census index skips, and 31 are
    # real repo-relative absences (16 in an existing directory, 14 with no such directory, 1 whose
    # "directory" is a file).  0 dated siblings, so the date-shift hypothesis is ruled out rather
    # than assumed.  The git-history arm is published unavailable, not as zero deletions: this clone
    # is a promisor/partial clone and any history walk starts a lazy fetch (r1224 family).  Verify
    # re-derives every published row's class from the tree.
    ("unresolved_names", ["python", "scripts/e399_unresolved_names.py", "verify"]),

    # E402 tests the inference E399 left standing: 52 published keys are bare basenames "whose
    # directory is supplied by a runtime variable at the one site that writes it".  The producer side
    # says otherwise for most of them -- 27 are fixture names inside a temporary directory deleted by
    # design, 3 are not whole filenames at all (a piece of a concatenated name), 6 are cwd-relative
    # reads, 2 are joined onto a constant base that does not hold the file, 6 could not be traced,
    # and none composes to a path that exists.  Verify re-derives every site count, every class and
    # the landing test from the tree.
    ("fragment_producers", ["python", "scripts/e402_fragment_producers.py", "verify"]),

    # E404 prices the constant side of E402's untraceable fragments: for each one the directory
    # expression is followed to the binding that supplies it (function scope, then module
    # assignment, then one import hop) and the joined file tested against the tree.  Verify
    # re-derives every class, every count and the landing test from the tree.
    ("constant_directory_resolution",
     ["python", "scripts/e404_constant_directory_resolution.py", "verify"]),

    # E405 asks the follow-up E404 left open: an absent read target is only a defect if a reader
    # would fail.  For each of the three published joins it re-derives what the line is doing (write
    # / module constant / read), walks every later use of that constant in the same file (writer,
    # existence gate, gated read, bare read, status table, landing helper) and reads the failure mode
    # from the AST plus an existence test on the target.  Verify re-derives every class and the
    # verdict against the live tree.
    ("dead_read_failure_mode",
     ["python", "scripts/e405_dead_read_failure_mode.py", "verify"]),

    # E401 re-runs E384's own key-site classifier with every project-local callable that opens a
    # file added to the call table (patched for one run, restored in a finally).  It publishes the
    # keys that change class, the site lines the stdlib table could not see, and the other arm:
    # every site the stdlib table calls "other" is a git-object read.  Verify re-derives every
    # count, the from->to tally and the verdict, and refuses a classifier left patched.
    ("local_reader_table",
     ["python", "scripts/e401_local_reader.py", "verify"]),

    # E398 asks who reads a latest.json pointer and whether the reader knows which family wrote
    # last.  E385 found 28 files under the name latest.json; a reader that resolves the pointer
    # against a free runtime base opens whichever family published last and looks healthy doing it
    # (the file exists, it parses).  The leg classifies every in-repo read site by where its family
    # comes from -- literal/constant at the site, a function parameter, a value the same function
    # just wrote, or nothing at all -- and publishes the fan-out each unsupplied reader can reach
    # plus the schema cost of a wrong landing.  Verify re-derives every published row and its class
    # from the tree.
    ("latest_family", ["python", "scripts/e398_latest_family.py", "verify"]),

    # E384 asks the reverse question of E381: a published key is only "read" if some site actually
    # opens or dumps a file.  A string in a source is not a decision to open one -- the same literal
    # can feed a caption, a comparison or a Path that is never read.  The leg classifies each key's
    # sites by the call around the SITE line (a key is usually a module constant opened elsewhere,
    # so reading the literal's own line called 90% of a healthy population "never opened" on the
    # first burn), then prints how many published census faces carry each never-opened key.  Verify
    # re-classifies every published row and re-derives the gate without the corpus walk.
    ("never_opened_key", ["python", "scripts/e384_never_opened_key.py", "verify"]),

    # E407 answers the pool card seeded after E305 re-red twice in one window.  The hypothesis was
    # that the E305 leg reads a face an earlier leg of the same suite republishes.  Measured: the
    # build opens exactly the 13 faces its census names, all 13 have a writer in the tree, and no
    # attributable leg of the suite executes one of those writers -- the input is stable inside a
    # run, and what is pinned is the audit column (E387), which is why re-running the audit clears
    # the leg and re-committing the face without it does not.  Verify re-derives the leg census,
    # the movers and the order pairs from source.
    ("leg_input_stability", ["python", "scripts/e407_leg_input_stability.py", "verify"]),
    # E408: E407 proved the writer exists in the tree; this asks on WHICH signal it runs.  The
    # seed's writer list is name-based (its own docstring says a face is "written by the module
    # that names its basename"), so 7 of the 26 named modules only read the face.  Of the 14 that
    # really write, 12 run on this chain and 2 only run from a session script -- and 0 run on the
    # signal that reads them (the suite).  Verify re-derives every role and count from source.
    ("writer_refresh_signal", ["python", "scripts/e408_writer_refresh_signal.py", "verify"]),
    # E409: E408 named the two writers that only run from a session script.  This prices what
    # a reader sees when nobody ran them: 5 reader sites open the two faces and 0 ask how old
    # they are, while the suite prices the age of 6 of 192 faces it opens.  Verify re-derives
    # the ledger and refuses a reader site it can no longer find.
    ("unfloored_faces", ["python", "scripts/e409_unfloored_faces.py", "verify"]),
    # E410: E409 found nobody prices those two faces' age; this is the implementation, not
    # another census.  Two different forms because the faces answer different questions: the
    # open-fill face gets one bar of allowance (the shape the suite already uses for the ETF
    # book page -- a hard day gate is excluded by E185 at :593-597), the source census gets a
    # week.  Both bounds come off the exchange calendar, so a weekend cannot red the suite.
    # The leg runs the prover, which requires each bound red on a doctored copy and green on
    # the live tree -- a gate only ever seen green is not yet a gate.
    ("freshness_bound", ["python", "scripts/run_e410_freshness_legs.py"]),
    # E406: the blob-vs-file census behind E401's residue. `verify` re-derives every headline from
    # the published rows and refuses a face that was published at a midpoint; it is read-only and
    # one `git show` per measured face, so it stays cheap enough for the chain.
    ("blob_readers", ["python", "scripts/e406_blob_vs_tree_readers.py", "verify"]),
    # E412: the guard decision over E406's measured faces. `verify` re-derives every choice from
    # the row it was made from and refuses a face called guard-free while a consumer reads it at
    # HEAD; it re-measures blob-vs-file per face, so it belongs after `blob_readers`.
    ("blob_guard_decision", ["python", "scripts/e412_blob_guard_decision.py", "verify"]),
    # E403: E398 stopped at "somebody must pass the directory" for the 17 read sites whose family
    # is a function parameter. This walks the callers: 38 call sites, 11 land on a published
    # family, 13 on a scratch directory the caller just wrote, 14 forward their own caller's
    # parameter (8 readers), 0 pass a foreign family. Verify re-derives every call row from source.
    ("family_arg", ["python", "scripts/e403_family_arg.py", "verify"]),
    # E414 (r1433): E398 published exactly one read of a `*latest.json` pointer whose family is
    # supplied nowhere -- a bare basename at smoke_test.py:7971. E403's rule (read the landing off
    # `param or DEFAULT` in the callee body) answers it: the callee pins its OUTDIR to its own
    # module directory, so four process cwds resolve to one path that exists, and the leg that
    # reads it fails red rather than skipping. Verify re-runs the callee at each surface instead
    # of re-deriving the join here.
    ("unsupplied_read", ["python", "scripts/e414_unsupplied_read.py", "verify"]),
    # E411: E409 priced five reader sites over two faces; this prices every face the suite opens
    # (199 faces / 231 sites, 4 of which can go red on age). It legs `run` rather than `verify`
    # on purpose: the population *is* smoke_test.py, so every leg added or moved changes the
    # summary, and a verify-only leg would go red on any suite edit and stay red until someone
    # republished by hand. It republishes from the live tree in ~46 s (2.5k modules priced).
    ("reader_tiers", ["python", "scripts/e411_reader_tiers.py", "run"]),
    # E415 (r1434): E414 named the accident shape and left it unpriced. This censuses every read
    # in the durable corpus whose path argument is a bare basename (2 sites): 1 is directed by its
    # callee (E414's), 1 is directed by the launch directory and would read a DIFFERENT document of
    # the same basename from another surface -- CODELY.md, which exists with different content in
    # the CLI home. Verify re-scans the corpus (cheap: one AST pass over ~900 files) and re-checks
    # every published class against its resolver.
    ("cwd_accident", ["python", "scripts/e415_cwd_accident.py", "verify"]),
    # E428 (r1448): the 35 parameter-directory sites E429 billed as "no caller found" are re-billed
    # with a call index built for every helper that takes its directory as a parameter (75 -> 97
    # names). Verify re-derives the verdict from the rows and re-runs the wide index.
    ("no_caller", ["python", "scripts/e428_no_caller.py", "verify"]),
    # E416 (r1435): E411's four red-capable sites are re-read from their own source blocks and none
    # of them prices the AGE of the face it reads -- two pin a frozen date literal (so an honest
    # refresh is what reds the suite), one prices a copy lag against an upstream mtime, one carries
    # no date comparison at all. A verify leg costs one suite pass plus a bounded writer scan over
    # scripts/, and refuses a summary that no longer re-derives.
    ("fresh_aim", ["python", "scripts/e416_fresh_aim.py", "verify"]),
    # E418 (r1436): the 45 faces E416 left blind (no reader that can go red, no chain writer) are
    # priced by stamp age in bars against the exchange calendar, and each leg's green sentence is
    # classified as a frozen literal number / a value recomputed at read / no number. Verify
    # re-reads the 45 faces, the calendar and the suite lines and refuses a summary or verdict that
    # no longer re-derives. Read-only: no face is refreshed and no reader is edited.
    ("face_age", ["python", "scripts/e418_face_age.py", "verify"]),
    # E419 (r1437): the 9 faces E418 could not age are attributed to a writer, and each row says
    # whether that writer holds a date it never writes (strong basis only: a write target must
    # spell the basename, in the face's own directory, and must not be a fixture). Verify
    # re-derives every class from the AST of the census corpus (~30 s over 2.4k modules).
    ("unstampable", ["python", "scripts/e419_unstampable.py", "verify"]),
    # E420 (r1438): the E387 leg used to pin a corpus fingerprint as if it were a decision number.
    # Verify re-derives the audited faces' accretion / down / verdict-move split from the live tree.
    ("corpus_pin", ["python", "scripts/e420_corpus_pin_instability.py", "verify"]),
    # E421 (r1439): the 33 names E406 could not resolve are resolved by the directory their literal
    # is joined against. Verify re-scans the module corpus (~900 files, one AST pass each) and
    # refuses a summary, a control arm or a verdict that no longer re-derives.
    ("name_resolve", ["python", "scripts/e421_strong_basis_resolution.py", "verify"]),
    # E422 (r1440): the same bare-basename question asked of the other three basename-keyed
    # censuses. Verify re-reads all four faces and one-pass-parses the python corpus, so a row
    # whose reading would change, a tally that stopped adding up or a verdict that no longer
    # derives from the summary all refuse the chain.
    ("basename_census", ["python", "scripts/e422_basename_census_audit.py", "verify"]),
    # E417 (r1443): the shadow question of E415 asked of every face E411 priced -- which faces
    # have a same-named copy with different bytes in a directory a reader could be launched from,
    # and which of those names is actually read as a bare literal. Verify re-derives the
    # population, the class table, the generic/specific split and the verdict from the live tree.
    ("shadow_face", ["python", "scripts/e417_shadow_face.py", "verify"]),
    # E426 (r1444): E417 wrote the method limit "a reader that builds the name from a variable is
    # invisible to it".  This leg prices it -- every template that produces a *.json name from a
    # non-constant part, made specific enough to name a face, matched against the published tree
    # and against the faces E411 priced.  Verify re-parses the whole python corpus, so a corpus
    # that grew (a new literal legitimately reclassifies a face) refuses the chain instead of
    # leaving a stale reading in place.
    ("dynamic_face_names", ["python", "scripts/e426_dynamic_face_names.py", "verify"]),
    # E420 (r1445): E419's own method limit -- "a face composed from a variable and written by a
    # shared helper is out of reach" -- was exactly the shape of all three of its no-writer rows.
    # Verify re-derives every class from the live tree: the constant hop (module/function bindings,
    # three substitutions) and the caller hop (every call site of the helper, resolved with the
    # caller's own constants), plus the corpus split and the two reach tables (~4 min over 3.4k
    # modules).
    ("two_hop_writer", ["python", "scripts/e429_two_hop_writer.py", "verify"]),
    # E423 (r1446): E422 priced 11 rows that publish a FILE path in a field named
    # resolved_directory. Verify re-derives the read-site classes over the live corpus (one AST
    # pass) and re-checks the doubling intersection against the published rows, so a new consumer
    # that joins such a field with a row name refuses the chain instead of leaving a stale "no
    # consumer joins it" reading in place.
    ("dirfield_join", ["python", "scripts/e423_dirfield_join.py", "verify"]),
    # E432 (r1450): E428 counted 21 fixture-shaped parameter-directory write sites and never asked
    # where their callers point them. Verify re-derives the class table over the live corpus (one
    # AST pass for the sites, one prefiltered pass for readers) and re-checks that live rows plus
    # rows no longer a live site still equal the population E428 published, so a fixture helper
    # that moves or disappears refuses the chain instead of leaving a stale tally.
    ("fixture_write", ["python", "scripts/e432_fixture_write.py", "verify"]),
    # E434 (r1455): E428 counted "fixture-shaped" over the 35 rows its narrow index could not
    # place, not over the 310 parameter-directory write sites it scanned. Verify re-counts the
    # whole population with the same heuristic, re-prices the sites outside the already-published
    # rows (the priced set is the union of E428's and E432's faces, read not guessed), and
    # re-checks that inside + outside still equals the total, so a total that drifts back to a
    # statement about 35 rows refuses the chain.
    ("fixture_beyond", ["python", "scripts/e434_fixture_beyond.py", "verify"]),
    # E437 (r1456): E428's fixture word list is a name test on the callee, and E434 published its
    # count without asking how much of the temp-directory population a name test can even see.
    # Verify re-derives the call-row cross-cut over the live corpus and re-checks that the four
    # cells still add up to the call rows and that every published row still supplies a temp
    # directory, so a row that drops back to a site-level aggregate refuses the chain.
    ("name_recall", ["python", "scripts/e437_name_recall.py", "verify"]),
    # E438 (r1457, wired at r1458): the grading of temp-supplying rows against what the callee
    # writes had no chain leg when it shipped.  Verify re-derives the live class table and refuses
    # a face whose inside count, share or file-path block no longer re-adds from the rows.
    ("temp_write_base", ["python", "scripts/e438_temp_write_base.py", "verify"]),
    # E439 (r1458): E438's 56 rows were counted by callee name, and a name-keyed index counts
    # every `lst.append(x)` as a call to a wrapper named `append`.  Verify re-derives the call-slot
    # shapes over the live corpus, re-runs the wrapper recheck, and re-closes the attribution
    # (kept + dropped == name-index total) and the E438 re-pricing, so a face that keeps the old
    # denominator refuses the chain instead of publishing a share of same-name calls.
    ("file_slot_callers", ["python", "scripts/e439_file_slot_callers.py", "verify"]),
    # E440 (r1460): E439 called the rows it dropped "overstated" without reading them.  A dropped
    # row is either an attribute call (the receiver is an object, not a module wrapper) or a bare
    # call to a name several modules define -- and the difference decides whether the reachability
    # rule was right.  Verify re-derives both axes over the live corpus and refuses a published
    # class that no longer follows from its own axes, so a face carrying a carried verdict or a
    # name block that does not close refuses the chain instead of republishing the old label.
    ("shared_wrapper_names", ["python", "scripts/e440_shared_wrapper_names.py", "verify"]),
    # E443 (r1461): E440's shared-name class is a name fact; a bare call resolves through the
    # caller's own imports.  `check` re-derives every published tally from the published cells
    # (fast); `verify` re-runs E440's scan over ~3.4k sources (~20 min) and is published on demand,
    # because a guard whose only cost is 20 minutes per tick gets switched off.
    ("bare_call_resolve", ["python", "scripts/e443_bare_call_resolve.py", "check"]),
    # E442 (r1462): E436 named 18 path-only sites and never asked whether the composed value is
    # consumed.  `check` re-derives every published tally from the published rows (fast); the scan
    # itself walks the whole corpus (~90 s) and is published on demand, because a guard whose only
    # cost is a full corpus parse per tick gets switched off.
    ("dead_path_composition", ["python", "scripts/e442_deadpath.py", "check"]),
    # E448 (r1466): E442 left its 85 dropped compositions ungraded -- superseded by another open in
    # the same file, or opened nowhere.  `check` re-derives every published class and every basis
    # from the published rows (fast, no file walk), so a face whose class was edited without its
    # evidence refuses the chain; `verify` is the ~4 s rebuild against the live tree.
    ("dropped_path_open", ["python", "scripts/e448_dropped_path.py", "check"]),
    # E444 (r1467): E440 dropped 24,618 attribute call rows as "a method on some object, not
    # evidence about the wrapper", which reads the spelling and never the receiver.  This leg
    # re-derives every published tally from the published rows (fast, no corpus walk) and refuses a
    # face whose receiver split, hit count, class census or verdict no longer follows from its own
    # cells -- in particular a row that claims a method of the attributed module while the census
    # finds no class in that module at all.  `verify` is the ~6 min live rebuild, on demand.
    ("attr_call_module_method", ["python", "scripts/e444_attr_method.py", "check"]),
    # E449 (r1468): E448 left 30 dropped compositions that are opened nowhere in their file; the
    # largest family is a research-note pointer.  `check` re-derives every published class, tally
    # and verdict from the published rows (fast, no walk); `verify` is the ~8 s corpus walk and
    # refuses a face whose note is no longer named or opened the way it published.
    ("dead_prereg_pointer", ["python", "scripts/e449_dead_document_pointer.py", "check"]),
    # E441 (r1461): E435 published 626 directory values that are a published face's home and 0 of
    # 489 composable joins that lands -- a zero that reads two opposite ways.  This leg grades every
    # base live (a member was written after the carrier) or frozen, and cross-tabs the composable
    # subset against that grading.  Verify re-derives the member families over the live tree and
    # refuses a published base class its own carriers no longer support, so a face holding a stale
    # population refuses the chain instead of republishing the old split.  Read-only: it writes
    # nothing under results/, cost is one directory walk plus E435's face scan (~35s).
    ("face_home_family", ["python", "scripts/e441_facehome_family.py", "verify"]),
    # E445 (r1462): E441 called the live-base rows "one round away" from a landing target and never
    # composed the row's own name field.  Verify re-derives the three target classes and every
    # candidate from the live tree, so a face whose target has since appeared (or vanished)
    # refuses the chain instead of republishing the old class.  Read-only.
    ("face_home_target", ["python", "scripts/e445_facehome_target.py", "verify"]),
    # E446 (r1463): E441 called 51 bases "frozen" and stopped at the mtime of the directory, which
    # says nothing about whether any code would ever write there again.  Verify re-derives the
    # dormant/abandoned class of every frozen base from its own writer sites and the live corpus,
    # so a base that gained a writer (or lost its last one) refuses the chain instead of
    # republishing the old class.  Read-only; cost is one AST walk of the corpus (~25s).
    ("frozen_writer", ["python", "scripts/e446_frozen_writer.py", "verify"]),
    # E447 (r1469): E446 called a base with no writer "abandoned" and stopped at the write side, so
    # an abandoned base a harness-launched reader still opens was published as harmless.  Verify
    # re-derives every read site under each of the 23 bases over the live tree and refuses a base
    # whose class, site count or live-reader count has moved, so a base that lost its last reader
    # (or gained one) refuses the chain instead of republishing the old class.  Read-only; cost is
    # one AST walk of the corpus plus E446's writer pass (~60s).
    ("abandoned_read", ["python", "scripts/e447_abandoned_read.py", "verify"]),
    # E452 (r1470): E447 published 7 abandoned bases still read by harness-launched code and left
    # the safety question open -- an open on a file nobody writes is only safe if it is guarded or
    # the artifact is still on disk.  Verify re-derives every guard shape from the reader's own AST
    # and every artifact's presence from the disk, so a guard added, removed or moved refuses the
    # chain instead of republishing the old class.  Read-only; cost is one corpus walk plus E447's
    # face scan (~60s).
    ("abandoned_guard", ["python", "scripts/e452_abandoned_guard.py", "verify"]),
    # E451 (r1477): E449 published seven research notes named by a PREREG constant nobody loads,
    # leaving "does the study publish any digest of the note it claims to follow" unanswered.
    # Verify re-derives the naming set, the producers' faces and the sha256 of every note over the
    # live tree, so a note edited after publication (or a face that gained a digest) refuses the
    # chain instead of republishing the old split.  Read-only; one corpus walk plus 84 face loads.
    ("prereg_digest", ["python", "scripts/e451_prereg_digest.py", "verify"]),
    # E435 (r1458): E423 priced where a directory-named field points but never asked whether the
    # value is itself the name of a published face.  Verify re-derives the three value classes over
    # the live tree and refuses a published join whose target no longer resolves, so a face holding
    # a stale population (or a landing row whose file has since disappeared) refuses the chain
    # instead of republishing the old zero.
    ("dir_is_a_face", ["python", "scripts/e435_dir_is_a_face.py", "verify"]),
    # E427 (r1451): E426 published 2,818 templates as "inside a function that opens a file" and
    # stopped at location. Verify re-derives the state table over the live corpus (the scanner's own
    # AST walk plus E426's collector for the unfiltered base) and re-checks that the state table,
    # the bound/read totals and the direct-argument count all re-add from the published rows, so a
    # template whose binding moves refuses the chain instead of leaving a stale read count.
    ("opener_flow", ["python", "scripts/e427_opener_flow.py", "verify"]),
    # E433 (r1453): E423 named the republish sites and stopped before the chain. Verify re-derives
    # the code side (the republish sites' own dict literals) AND re-reads only the writer faces the
    # same modules open for writing, re-checking the headline counts and the verdict, so a site
    # that starts (or stops) carrying a name beside a file-capable directory field refuses the
    # chain instead of leaving a stale "the name rides along" claim in place.
    ("republication_chain", ["python", "scripts/e433_republication_chain.py", "verify"]),
    # E450 (r1475): E444 answered the wrapper side; this one re-derives the caller side of the same
    # attribute population and pins itself to E444's published receiver distribution under the
    # E455 growth rule (a superset may grow, a lost kind is a refusal). `check` rather than
    # `verify` for the same reason E444's leg uses it: the chain leg must not re-walk the corpus
    # (that rebuild is ~9 min); the full `verify` is the manual/closeout gate.
    ("caller_class", ["python", "scripts/e450_caller_class.py", "check"]),
    # E456 (r1478): E450 left the cross-module half of its own population unread -- 6,875 receivers
    # bound to a call to something outside the caller's classes.  This leg checks the published
    # resolution face: every count re-derives from the rows, an import form is present exactly when
    # an import was involved, the name hits sit inside the resolved population, and the population
    # pins to E450's published arm under the growth rule.  `check` rather than `verify` for the same
    # reason caller_class uses it: the chain leg must not re-walk the corpus (~7 min rebuild); the
    # full `verify` is the closeout gate.
    ("import_class", ["python", "scripts/e456_import_class.py", "check"]),
    # E459 (r1480): import_class left 928 rows whose callee module is not in the tree, and the module
    # name is the only handle on their class.  This leg re-derives the tallies from the published
    # rows, then puts the *live* module table back under the published examples: every published hit
    # must resolve as a hit and every published residue must still fail to import.  No corpus walk
    # (the population is inherited), so the chain can afford the live re-resolution that keeps the
    # "importable" column from being a constant nobody checks.
    ("stdlib_class", ["python", "scripts/e459_stdlib_class.py", "verify"]),
    # E458 (r1482): E451 showed no study publishes a digest of its prereg note, which presupposes a
    # consumer can already tell which study a face belongs to.  This leg re-derives the identity
    # tallies from the published rows, holds the three classes apart (machine / prose-only / none),
    # and re-resolves every published declaration against the live tree so the "resolves" column is
    # not a constant.  `check` rather than `verify` for the same reason caller_class uses it: the
    # full rebuild loads 538 faces and walks their producers.
    ("face_identity", ["python", "scripts/e458_face_identity.py", "check"]),
    # E461: the link side of the same question -- `check` because a full rebuild parses the whole
    # .py corpus, while the published tallies must still re-derive from the published rows.
    ("identity_consumers", ["python", "scripts/e461_identity_consumers.py", "check"]),
    # E462: the dialect side of the same question -- `check` for the same reason; the tallies must
    # re-derive from the published rows without re-walking the corpus.
    ("identity_dialect", ["python", "scripts/e462_identity_dialect.py", "check"]),
    # E463: which study a face joins when two read names disagree -- `check` for the same reason.
    ("identity_split", ["python", "scripts/e463_identity_split.py", "check"]),
    # E464: which identity a producer intends when it writes two names -- `check` re-derives every
    # tally from the published rows (writer/non-writer split, intent classes, pointer-key counts).
    ("producer_intent", ["python", "scripts/e464_producer_intent.py", "check"]),
    # E465: does a face pointer resolve, and is it the join anyone uses.  `check` re-derives every
    # tally, the residue split, the reader layers and the verdict from the published rows; the live
    # rebuild walks 13k faces plus the whole .py corpus, so `verify` is the manual/closeout gate.
    ("pointer_join", ["python", "scripts/e466_pointer_join.py", "check"]),
    # E457 (r1488): a name test's optimism is the part of its vocabulary that is a method name in a
    # module that never imports the function. `check` re-derives every tally from the published rows
    # because the full rebuild parses ~3.5k sources (~60s) and would make this leg the chain's
    # most expensive; `verify` is the manual/closeout gate for the live corpus walk.
    ("name_collide", ["python", "scripts/e457_namecollide.py", "check"]),
    # E460 (r1489): E458's residue -- 12 faces with no machine-readable identity -- priced against
    # what their own producers know.  `check` re-derives every tally and every row's class and
    # reading from the published rows; the population is inherited from E458's face, so the live
    # rebuild is cheap (12 payloads + 21 sources) and `verify` re-reads it byte-for-byte.
    ("face_gap", ["python", "scripts/e460_facegap.py", "check"]),
]


def ghost_legs(legs=None):
    """Legs whose script does not exist on disk.

    D-20261101-13: ``Tools/s6_chain_bmc.py`` registered three commands pointing at
    ``scripts/etf_book_width_cross.py``, which no commit ever contained, so three machines stayed
    red in the "chain runner is the shared leg list" smoke leg.  A leg table without an existence
    assertion is a wish list.  Check at registration time (this module's own table, before any leg
    runs) so a ghost is a refusal here rather than a red smoke everywhere.

    ``python -m pkg.module`` legs are skipped: their target is a module, not a path.
    """
    missing = []
    for name, cmd in (legs if legs is not None else LEGS):
        if len(cmd) < 2 or cmd[0] != "python" or cmd[1].startswith("-"):
            continue
        if cmd[1] == "-m":
            continue
        if not os.path.exists(cmd[1]):
            missing.append((name, cmd[1]))
    return missing


def main(argv):
    # --only <name>[,<name>...] runs a subset of legs. r1281 recorded that the absence of this
    # selector meant the whole chain could not be spot-run inside a round, so a single leg could
    # only be verified by hand-copying its argv. Filtering here keeps the leg table the single
    # source of truth: the subset runs exactly the commands the full chain would run.
    only = None
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--only":
            i += 1
            only = set(x.strip() for x in (argv[i] if i < len(argv) else "").split(",") if x.strip())
        elif a.startswith("--only="):
            only = set(x.strip() for x in a.split("=", 1)[1].split(",") if x.strip())
        else:
            rest.append(a)
        i += 1
    if not rest:
        print("usage: s6_chain_bmb.py <round_no> [--only leg1,leg2]")
        return 2
    rnd = str(rest[0])
    ghosts = ghost_legs()
    if ghosts:
        for name, target in ghosts:
            print("ghost leg registered: %s -> %s (the script does not exist)" % (name, target))
        print("refusing to run a leg table that names a script no commit contains "
              "(D-20261101-13: register only what is on disk)")
        return 2
    legs = LEGS
    if only is not None:
        unknown = sorted(only - {name for name, _cmd in LEGS})
        if unknown:
            print("unknown leg(s): %s" % ", ".join(unknown))
            print("available: %s" % ", ".join(name for name, _cmd in LEGS))
            return 2
        legs = [(name, cmd) for name, cmd in LEGS if name in only]
    out = os.path.join("results", "_r%sbmb_s6_chain.json" % rnd)
    rows = []
    t0 = time.time()
    for leg, cmd in legs:
        s = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               errors="replace", timeout=900)
            rc, tail = p.returncode, (p.stdout or "").strip().splitlines()[-1:] or [""]
        except Exception as exc:      # a leg that cannot even start is a leg, not a crash
            rc, tail = 99, [str(exc)[:200]]
        rows.append({"leg": leg, "rc": rc,
                     "elapsed_sec": round(time.time() - s, 2),
                     "tail": (tail[0][:300] if tail else "")})
        print("%-22s rc=%-3s %6.2fs  %s" % (leg, rc, time.time() - s,
                                            rows[-1]["tail"][:110]))
    bad = [r for r in rows if r["rc"] != 0]
    payload = {"round": rnd, "machine": "bm-b",
               "ts": datetime.now().isoformat(timespec="seconds"),
               "elapsed_sec": round(time.time() - t0, 2),
               "legs_total": len(rows), "legs_rc0": len(rows) - len(bad),
               "legs": rows}
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("\nS6 %d/%d rc=0  (%.1fs)  receipt=%s"
          % (payload["legs_rc0"], payload["legs_total"], payload["elapsed_sec"], out))
    for r in bad:
        print("NONZERO %s rc=%s %s" % (r["leg"], r["rc"], r["tail"][:200]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))