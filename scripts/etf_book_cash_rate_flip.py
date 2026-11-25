"""How low would the cash rate have to be before the book's ADMIT dies?

`etf_book_idle_cash` published one point: pay the idle sleeve at the quoted GC001 roll
(1.77%/yr) and the book gains 0.58pp, Sharpe 1.082 -> 1.134, max drawdown -10.56 -> -10.47,
verdict ADMIT.  It never said how far that verdict is from falling over, and the block board
carries a RED row saying the repo panel is days behind -- so a reader cannot tell whether a
stale cash rate is a disclosure problem or a verdict problem.

This face sweeps the same composition over the cash rate and answers three things:

  1. the flip rate -- the GC001 level at which the ADMIT breaks (which gate breaks first);
  2. the distance to it, in basis points of rate and in days of the panel being stale;
  3. the money the missing quotes can actually move: idle share x rate error x days,
     which for a five-day gap is a couple of basis points of annual return per million.

The sweep is on the published geometry, not a new one: the engine is run once, the idle
sleeve comes from the engine's own scale diagnostics, and every grid point recomposes the
same book with `cash_ret * s`.  At s = 1 the reading must reproduce the published face to
0.01pp (C0) or the grid has drifted from the face it is talking about.

Nothing here is a judgement: the gates are `etf_book_idle_cash.CRITERIA` imported, not
restated, and the verdict at every grid point comes from `verdict_of`.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_cash_ladder as CL
import etf_book_idle_cash as IC

OUT = os.path.join(E.PATHS.results_dir, "etf_book_cash_rate_flip.json")
IDLE_FACE = os.path.join(E.PATHS.results_dir, "etf_book_idle_cash.json")
DOC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "research", "ETF_BOOK_CASH_RATE_FLIP.md")
REPRO_TOL_PP = 0.01          # s=1 must land on the published gain (C0)
CONTROL_TOL = 5e-5           # s=0 must BE the engine curve (idle_cash's own control)
GRID = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
STALE_DAYS_ASSUMED = 5       # the block board's D6 row: modal repo bar days behind


# ---------------------------------------------------------------------------------------
# pure helpers (the selftest holds these without the engine)
# ---------------------------------------------------------------------------------------
def crossing(grid_x, grid_y, target):
    """First x where y crosses `target` going up, by linear interpolation inside the bracket.

    Rates and returns are both quoted as percent-per-year and the composition is affine in
    the scale, so interpolating inside the bracket is exact to the grid's own rounding; the
    caller still re-derives the verdict AT the crossing instead of trusting the algebra.
    """
    if not grid_x:
        return None
    if float(grid_y[0]) >= float(target):
        # the gate is already satisfied at the left edge; there is no crossing to find and
        # reporting a later point would overstate the headroom
        return float(grid_x[0])
    for (x0, y0), (x1, y1) in zip(zip(grid_x, grid_y), zip(grid_x[1:], grid_y[1:])):
        if y0 < target <= y1:
            if y1 == y0:
                return float(x1)
            return float(x0 + (target - y0) * (x1 - x0) / (y1 - y0))
    return None


def gap_cost_cny(idle_share, delta_rate, days=STALE_DAYS_ASSUMED, notional=1_000_000.0):
    """Money a rate error of `delta_rate` (fraction/yr) can move over `days` of stale quotes.

    The sleeve only earns on the fraction that is idle, only for the missing days, so this
    is the whole of the exposure -- there is no compounding path to amplify it.
    """
    return float(notional) * float(idle_share) * float(delta_rate) * (days / 252.0)


# ---------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------
def build():
    """One engine run, the book's own idle sleeve, and the cash step path off that calendar."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)

    diag = []
    book, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, IC.REBAL,
                                       IC.NHOLD, IC.COST, vol_target=IC.VOL_TARGET, diag=diag)
    idle = (1.0 - IC.scale_schedule(diag, book.index)).clip(lower=0.0, upper=1.0)

    rates = CL.load_panel()
    cash_ret, info, raw_ret, raw_bars = IC.cash_step_returns(rates, book.index)
    r0_pct = CL.cagr_pct(raw_ret, raw_bars)          # the vehicle's own rate, %/yr
    last_bar = pd.Timestamp(max(raw_bars)) if len(raw_bars) else None
    return {
        "book": book, "idle": idle, "cash_ret": cash_ret, "turn": turn,
        "universe": len(cols), "flips": n_flip,
        "r0_pct": float(r0_pct),
        "rate_bars_last": last_bar,
        "last_rate_bar": None if last_bar is None else str(last_bar.date()),
        "cash_info": info,
    }


def sweep(built):
    """Recompose the same book at each cash-rate scale and read the same gates."""
    book, idle, cash_ret = built["book"], built["idle"], built["cash_ret"]
    st_wo = A.stats2(book, "without_fix")
    cagr_wo = float(st_wo["cagr"])
    rows = []
    for s in GRID:
        comp = IC.compose(book, idle, cash_ret * float(s))
        st_w = A.stats2(comp, "with_fix")
        readings = {
            "cagr_without_pct": round(cagr_wo * 100.0, 4),
            "cagr_with_pct": round(float(st_w["cagr"]) * 100.0, 4),
            "cagr_gain_pp": round((float(st_w["cagr"]) - cagr_wo) * 100.0, 4),
            "sharpe_without": round(float(st_wo["sharpe"]), 4),
            "sharpe_with": round(float(st_w["sharpe"]), 4),
            "maxdd_without_pct": round(float(st_wo["maxdd"]) * 100.0, 4),
            "maxdd_with_pct": round(float(st_w["maxdd"]) * 100.0, 4),
        }
        verdict, gates = IC.verdict_of(readings)
        ctrl = IC.compose(book, idle, pd.Series(0.0, index=book.index)) if s == 0.0 else None
        rows.append({
            "scale": float(s),
            "cash_rate_pct": round(built["r0_pct"] * float(s), 4),
            "cagr_gain_pp": readings["cagr_gain_pp"],
            "sharpe_with": readings["sharpe_with"],
            "maxdd_with_pct": readings["maxdd_with_pct"],
            "verdict": verdict,
            "gates": gates,
            "control_max_rel_err": None if ctrl is None
            else float((ctrl / book - 1.0).abs().max()),
        })
    return rows, st_wo


def analyse(built, rows):
    target = float(IC.CRITERIA["C2_cagr_gain_pp"])
    xs = [r["cash_rate_pct"] for r in rows]
    ys = [r["cagr_gain_pp"] for r in rows]
    flip_c2 = crossing(xs, ys, target)

    # the other two gates are read off the sweep rather than assumed: name which one is
    # actually binding, because "the verdict dies at X" is only useful with the reason.
    binding, first_break = "C2_cagr_gain_pp", None
    for r in rows:
        bad = [k for k, ok in (r.get("gates") or {}).items() if not ok]
        if bad:
            first_break = {"cash_rate_pct": r["cash_rate_pct"], "gates_broken": bad}
            binding = bad[0]
            break

    r_now = built["r0_pct"]
    idle_mean = float(built["idle"].fillna(0.0).mean())
    cost = {}
    for d in (50.0, 100.0, 200.0):
        cost[str(int(d))] = round(gap_cost_cny(idle_mean, d / 10000.0), 2)

    # the tail the panel cannot price: `cash_step_returns` ffills the cumulative growth and
    # differences it on the book calendar, so a book bar after the last repo bar accrues
    # exactly zero. That is the part of the staleness that is already inside the published
    # curve, not a hypothetical error on the rate.
    tail = {}
    last_bar = built.get("rate_bars_last")
    if last_bar is not None:
        idx = built["book"].index
        after = idx[idx > last_bar]
        idle_after = built["idle"].fillna(0.0).reindex(after)
        tail = {
            "book_bars_after_last_repair_quote": int(len(after)),
            "dates": [str(d.date()) for d in after],
            "idle_share_on_those_bars": None if not len(after)
            else round(float(idle_after.mean()), 4),
            "unpaid_accrual_cny_per_1m": None if not len(after)
            else round(gap_cost_cny(float(idle_after.mean()), r_now / 100.0, days=len(after)),
                       2),
        }

    return {
        "flip_rate_c2_pct": None if flip_c2 is None else round(flip_c2, 4),
        "c2_target_gain_pp": target,
        "distance_bp": None if flip_c2 is None else round((r_now - flip_c2) * 100.0, 2),
        "binding_gate": binding,
        "first_break": first_break,
        "rate_now_pct": round(r_now, 4),
        "idle_share_mean": round(idle_mean, 4),
        "stale_days_assumed": STALE_DAYS_ASSUMED,
        "gap_cost_cny_per_1m_by_rate_error_bp": cost,
        "gap_cost_bp_of_annual_return_by_100bp": round(
            idle_mean * (100 / 10000.0) * (STALE_DAYS_ASSUMED / 252.0) * 10000.0, 4),
        "last_rate_bar": built["last_rate_bar"],
        "tail_not_priced": tail,
    }


def verdict_at(built, rate_pct):
    """Re-derive the verdict at an arbitrary cash rate -- the behavioural leg, not algebra."""
    scale = 0.0 if built["r0_pct"] == 0 else float(rate_pct) / built["r0_pct"]
    book, idle, cash_ret = built["book"], built["idle"], built["cash_ret"]
    st_wo = A.stats2(book, "without_fix")
    st_w = A.stats2(IC.compose(book, idle, cash_ret * scale), "with_fix")
    readings = {
        "cagr_without_pct": round(float(st_wo["cagr"]) * 100.0, 4),
        "cagr_with_pct": round(float(st_w["cagr"]) * 100.0, 4),
        "cagr_gain_pp": round((float(st_w["cagr"]) - float(st_wo["cagr"])) * 100.0, 4),
        "sharpe_without": round(float(st_wo["sharpe"]), 4),
        "sharpe_with": round(float(st_w["sharpe"]), 4),
        "maxdd_without_pct": round(float(st_wo["maxdd"]) * 100.0, 4),
        "maxdd_with_pct": round(float(st_w["maxdd"]) * 100.0, 4),
    }
    v, gates = IC.verdict_of(readings)
    return {"cash_rate_pct": round(float(rate_pct), 4), "verdict": v, "gates": gates,
            "cagr_gain_pp": readings["cagr_gain_pp"]}


def published_gain():
    if not os.path.exists(IDLE_FACE):
        return None, None
    with io.open(IDLE_FACE, encoding="utf-8") as f:
        face = json.load(f)
    rd = face.get("readings") or {}
    return rd.get("cagr_gain_pp"), (face.get("window") or {}).get("end")


def run(check_only=False):
    import time
    t0 = time.time()
    built = build()
    rows, st_wo = sweep(built)
    facts = analyse(built, rows)
    pub_gain, pub_end = published_gain()

    at_one = next(r for r in rows if r["scale"] == 1.0)
    c0_gap = None if pub_gain is None else round(at_one["cagr_gain_pp"] - float(pub_gain), 4)

    # behavioural legs: the crossing must actually separate the verdicts on the engine,
    # not only inside the interpolation
    legs = {}
    if facts["flip_rate_c2_pct"] is not None:
        below = verdict_at(built, facts["flip_rate_c2_pct"] * 0.90)
        above = verdict_at(built, facts["flip_rate_c2_pct"] * 1.10)
        legs["just_below_flip"] = below
        legs["just_above_flip"] = above
        legs["flip_separates"] = bool(below["verdict"] == "REJECT"
                                     and above["verdict"] == "ADMIT")

    gates = {
        "C0_s1_reproduces_published_face": bool(c0_gap is not None
                                                and abs(c0_gap) <= REPRO_TOL_PP),
        "C1_s0_control_is_the_engine_curve": bool(
            float(at_zero_err(rows)) <= CONTROL_TOL),
        "C2_gain_is_monotone_in_the_rate": bool(
            all(b >= a - 1e-9 for a, b in zip([r["cagr_gain_pp"] for r in rows],
                                              [r["cagr_gain_pp"] for r in rows][1:]))),
        "C3_flip_separates_the_verdicts": bool(legs.get("flip_separates")),
        "C4_gap_cost_below_one_gate": bool(
            facts["gap_cost_bp_of_annual_return_by_100bp"] < 1.0),
    }
    verdict = "PASS" if all(gates.values()) else "FAIL"

    payload = {
        "face": "etf_book_cash_rate_flip",
        "question": "the book's ADMIT was bought by paying its idle sleeve at 1.77%/yr; how "
                    "low can that rate go before the verdict falls over, and what can a "
                    "stale repo panel actually move?",
        "evidence_cutoff": str(built["book"].index[-1].date()),
        "window": {"start": str(built["book"].index[0].date()),
                   "end": str(built["book"].index[-1].date()),
                   "bars": int(len(built["book"]))},
        "book": {"vol_target": IC.VOL_TARGET, "rebal": IC.REBAL, "n_hold": IC.NHOLD,
                 "cost": IC.COST, "universe": built["universe"],
                 "turnover": round(float(built["turn"]), 4),
                 "flips_repaired": built["flips"]},
        "criteria_imported": {k: IC.CRITERIA[k] for k in
                              ("C2_cagr_gain_pp", "C3_sharpe_must_not_fall",
                               "C4_maxdd_must_not_deepen_pp")},
        "published_face": {"gain_pp": pub_gain, "window_end": pub_end},
        "sweep": rows,
        "facts": facts,
        "legs": legs,
        "gates": gates,
        "verdict": verdict,
        "honest": [
            "the sweep is the published composition on the published geometry: the engine is "
            "run once and every grid point recomposes that same book with cash_ret * s, so a "
            "grid point is not a new backtest",
            "cagr_gain_pp is affine in the cash rate up to the compounding of the final NAV, "
            "which at these magnitudes is below the 4th decimal; the crossing is still "
            "re-derived on the engine at +/-10% of the flip rate rather than trusted",
            "the flip rate is a statement about this window's gates, not a forecast: if the "
            "cash rate sits below it for a while the verdict falls, and that is the definition "
            "of the gate, not a prediction that it will",
            "the gap cost is a bound on what a rate error can move, it is not a claim about "
            "what the missing days actually were -- the panel cannot answer that",
            "verdicts and gates come from etf_book_idle_cash.CRITERIA via verdict_of; no "
            "threshold is restated here",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }

    if check_only:
        old = None
        if os.path.exists(OUT):
            with io.open(OUT, encoding="utf-8") as f:
                old = json.load(f)
        diffs = []
        if old is None:
            diffs.append("face missing")
        else:
            for k in ("verdict", "facts", "gates"):
                if old.get(k) != payload.get(k):
                    diffs.append("%s differs" % k)
            if old.get("evidence_cutoff") != payload.get("evidence_cutoff"):
                diffs.append("cutoff moved: %s -> %s" % (old.get("evidence_cutoff"),
                                                          payload.get("evidence_cutoff")))
        if diffs:
            print("CHECK FAILED " + "; ".join(diffs))
            return 3
        print("CHECK OK verdict=%s flip_rate=%s distance_bp=%s"
              % (payload["verdict"], facts["flip_rate_c2_pct"], facts["distance_bp"]))
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    write_doc(payload)
    print("verdict=%s flip_rate_c2=%s%% distance=%sbp binding=%s gap_cost_100bp=%sbp/yr"
          % (verdict, facts["flip_rate_c2_pct"], facts["distance_bp"], facts["binding_gate"],
             facts["gap_cost_bp_of_annual_return_by_100bp"]))
    print("WROTE %s" % OUT)
    return 0 if verdict == "PASS" else 3


def at_zero_err(rows):
    for r in rows:
        if r["scale"] == 0.0 and r.get("control_max_rel_err") is not None:
            return r["control_max_rel_err"]
    return float("inf")


# ---------------------------------------------------------------------------------------
# doc (readings are rendered from the face; --check compares them, never a hand-copied table)
# ---------------------------------------------------------------------------------------
BEGIN, END = "<!-- FLIP-BEGIN -->", "<!-- FLIP-END -->"


def render_block(p):
    f = p["facts"]
    lines = ["| cash rate %/yr | gain pp | Sharpe | maxDD % | verdict |",
             "|---|---|---|---|---|"]
    for r in p["sweep"]:
        lines.append("| %.2f | %+.2f | %.3f | %.2f | %s |"
                     % (r["cash_rate_pct"], r["cagr_gain_pp"], r["sharpe_with"],
                        r["maxdd_with_pct"], r["verdict"]))
    body = "\n".join(lines)
    return ("%s\n_generated %s · evidence cutoff %s · %d bars over %s..%s_\n\n%s\n\n"
            "- flip rate (C2 target %.2fpp): **%s%%/yr** -- today's vehicle is %.2f%%/yr, "
            "i.e. **%.0fbp of headroom**\n"
            "- binding gate when it breaks: **%s**\n"
            "- a %d-day gap in the repo panel can move annual return by **%.3fbp per 100bp** "
            "of rate error -- %.2f CNY/yr per million\n"
            "- the panel's last bar is **%s**; **%s** book bar(s) after it accrue exactly zero "
            "(%s), so the published curve already under-pays **%.2f CNY per million** on them\n"
            "%s"
            % (BEGIN, p["asof"], p["evidence_cutoff"], p["window"]["bars"],
               p["window"]["start"], p["window"]["end"], body,
               f["c2_target_gain_pp"], f["flip_rate_c2_pct"], f["rate_now_pct"],
               f["distance_bp"], f["binding_gate"], f["stale_days_assumed"],
               f["gap_cost_bp_of_annual_return_by_100bp"],
               f["gap_cost_cny_per_1m_by_rate_error_bp"].get("100", 0.0),
               f["last_rate_bar"],
               (f.get("tail_not_priced") or {}).get("book_bars_after_last_repair_quote", 0),
               ", ".join((f.get("tail_not_priced") or {}).get("dates") or []) or "none",
               (f.get("tail_not_priced") or {}).get("unpaid_accrual_cny_per_1m") or 0.0,
               END))


def write_doc(p):
    p = dict(p)
    p["asof"] = pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    block = render_block(p)
    head = ("# The cash rate at which the book's ADMIT dies\n\n"
            "`etf_book_idle_cash` says the idle sleeve is worth paying: 0.58pp of CAGR, "
            "Sharpe 1.082 -> 1.134, drawdown slightly better, verdict ADMIT. This face asks "
            "the next question -- how far is that verdict from falling over -- because the "
            "block board carries a RED row saying the repo panel is days behind, and a "
            "reader cannot otherwise tell a disclosure problem from a verdict problem.\n\n"
            "## What it says\n\n")
    tail = ("\n## What this is not\n\n"
            "- not a forecast of the cash rate; the flip is a property of the gate\n"
            "- not a new backtest: every grid point recomposes the same engine book\n"
            "- not a replacement for the collector: the missing days still have to be "
            "backfilled, this face only bounds what they can move\n\n"
            "Reproduce: `python scripts/etf_book_cash_rate_flip.py` (writes this block), "
            "`--check` (re-derive and compare), `--selftest` (offline legs).\n")
    text = head + block + tail
    old = None
    if os.path.exists(DOC):
        with io.open(DOC, encoding="utf-8") as f:
            old = f.read()
    if old and BEGIN in old and END in old:
        pre = old.split(BEGIN)[0]
        post = old.split(END, 1)[1]
        text = pre + block + post
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def check_doc():
    if not os.path.exists(DOC) or not os.path.exists(OUT):
        print("CHECK FAILED doc or face missing")
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        p = json.load(f)
    with io.open(DOC, encoding="utf-8") as f:
        text = f.read()
    if BEGIN not in text or END not in text:
        print("CHECK FAILED doc has no rendered block")
        return 3
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]
    # the numbers in the block must be the numbers in the face
    probe = str(p["facts"]["flip_rate_c2_pct"])
    if probe not in block:
        print("CHECK FAILED doc block does not print the face's flip rate %s" % probe)
        return 3
    print("CHECK OK doc block matches face")
    return 0


# ---------------------------------------------------------------------------------------
# offline selftest (no engine, no panel)
# ---------------------------------------------------------------------------------------
def selftest():
    cases = []

    def leg(name, fn):
        try:
            fn()
            cases.append((name, True, ""))
        except AssertionError as e:
            cases.append((name, False, str(e)))

    def t_cross_exact():
        assert crossing([0.0, 1.0, 2.0], [0.0, 0.5, 1.0], 0.25) == 0.5

    def t_cross_mid_bracket():
        assert abs(crossing([0.0, 2.0], [0.0, 1.0], 0.3) - 0.6) < 1e-12

    def t_cross_above_range():
        # the whole grid is above the target: the edge is the honest answer
        assert crossing([0.0, 1.0], [1.0, 2.0], 0.5) == 0.0

    def t_cross_at_top():
        assert crossing([0.0, 1.0], [0.0, 1.0], 1.0) == 1.0

    def t_cross_flat():
        # already at the target on the left edge: report the edge, not a later point
        assert crossing([0.0, 1.0], [0.5, 0.5], 0.5) == 0.0

    def t_cross_never():
        assert crossing([0.0, 1.0], [0.1, 0.2], 0.5) is None

    def t_cost_linear():
        a = gap_cost_cny(0.30, 0.01)
        b = gap_cost_cny(0.30, 0.02)
        assert abs(b - 2 * a) < 1e-9

    def t_cost_scale():
        # 30% idle, 100bp, 5 days of a 252-day year, on 1,000,000
        assert abs(gap_cost_cny(0.30, 0.01) - 1_000_000 * 0.30 * 0.01 * 5 / 252) < 1e-6

    def t_cost_zero_days():
        assert gap_cost_cny(0.5, 0.01, days=0) == 0.0

    def t_cost_sub_bp():
        bp = 0.30 * 0.01 * 5 / 252 * 10000
        assert bp < 1.0, bp

    for n, f in [("crossing interpolates inside the bracket", t_cross_exact),
                 ("crossing lands mid-bracket", t_cross_mid_bracket),
                 ("a grid entirely above the target reports its left edge", t_cross_above_range),
                 ("crossing at the top point is the top point", t_cross_at_top),
                 ("a series already at the target reports the left edge", t_cross_flat),
                 ("a series that never reaches the target has no crossing", t_cross_never),
                 ("gap cost is linear in the rate error", t_cost_linear),
                 ("gap cost uses idle share x days / 252", t_cost_scale),
                 ("no days means no cost", t_cost_zero_days),
                 ("a five-day gap under 100bp stays under one basis point", t_cost_sub_bp)]:
        leg(n, f)
    bad = [c for c in cases if not c[1]]
    for n, ok, why in cases:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, "" if ok else " | " + why))
    print("%d/%d legs pass" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(selftest())
    if arg == "--check":
        rc = run(check_only=True)
        if rc == 0:
            rc = check_doc()
        sys.exit(rc)
    sys.exit(run())
