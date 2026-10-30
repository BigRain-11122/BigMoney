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