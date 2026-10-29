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
    if not argv:
        print("usage: s6_chain_bmb.py <round_no>")
        return 2
    rnd = str(argv[0])
    out = os.path.join("results", "_r%sbmb_s6_chain.json" % rnd)
    rows = []
    t0 = time.time()
    for leg, cmd in LEGS:
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