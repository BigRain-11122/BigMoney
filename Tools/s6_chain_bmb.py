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
    ("gpu_face", ["python", "Tools/gpu_face.py", "audit"]),
    ("attrition_guard", ["python", "scripts/attrition_ledger_guard.py", "scan"]),
    ("pool_audit", ["python", os.path.join("scripts", "pool_audit.py")]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]


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