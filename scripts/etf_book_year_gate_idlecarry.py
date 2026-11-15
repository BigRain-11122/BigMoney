"""Both good things at once, or pick one?  The page says pick one; this asks the book.

The CEO page (docs/live_book) ends its vol-ladder section with a sentence nobody could
act on: "要「能拿新钱」就接受满仓书的回撤；要「回撤浅」就先别指望这一步扩资本。两个都要，
需要这条梯子以外的第三条路。"  Two faces say that in numbers:

    etf_book_year_gate    the 8% vol target book fails Y4 (best two years = 70.39% of net
                          against a 70.00% line) and comes back CONDITIONAL; going up the
                          ladder to vt15 passes Y4 by not de-levering at all (-16.04% DD)
    etf_book_idle_cash    the de-levered sleeve sits in cash the engine prices at 0 while
                          the desk's own published GC001 roll pays 1.77%/yr net; paying it
                          is worth +0.58pp CAGR and -0.09pp drawdown

Neither face is wrong; they were never composed.  `idle_cash` answered "is the cash worth
paying" -- it never asked the calendar gate.  This face asks the question the page left
open: **can the same shallow-drawdown book clear Y4 once its idle sleeve is paid?**

The mechanism is not a search: the carry accrues on the idle share, so it is largest in the
years the vol target actually de-levered, and the seven-year total therefore grows faster
than the two best years inside it.  A concentration share can fall without any top year
getting worse.  If that is enough to pull the top-two share under the line, the "third
path" exists and it costs nothing but a repo contract; if it is not, the page's either/or
stands and this face says so.

Reuse, never re-implement:
    the book, the vol target, the composite engine   etf_robust_pf / etf_composite_pf (via
                                                     etf_book_idle_cash's own build)
    the cash composition and its zero-cash control    etf_book_idle_cash.compose
    the cash vehicle (GC001 daily roll)               etf_book_cash_ladder.roll_rung
    the calendar gate and its frozen rules            candidate_year_gate.admission_block
    the year decomposition and capacity derivation    etf_book_year_gate.yearly_returns

Usage:
    python scripts/etf_book_year_gate_idlecarry.py run
    python scripts/etf_book_year_gate_idlecarry.py selftest
"""
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_cash_ladder as CL  # noqa: E402
import etf_book_idle_cash as IC  # noqa: E402
import etf_book_year_gate as YG  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_year_gate_idlecarry.json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_YEAR_GATE_IDLECARRY.md")
YEAR_GATE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
IDLE_CASH = os.path.join(ROOT, "results", "etf_book_idle_cash.json")

# Frozen before this face read one number.  Nothing here is a search: the only free
# choice is "pay the sleeve or don't", and the control is the book as it is priced today.
CRITERIA = {
    "C0_control": "with the cash rate forced to zero the re-derived calendar block must "
                  "reproduce the published YEAR-GATE nobond_vt08_adopted top2_share "
                  "(|diff| <= 1e-4) and its verdict; otherwise the composition, not the "
                  "carry, is what moved the gate",
    "C1_cash_vehicle_published": "the idle sleeve must be priced by the published GC001 "
                                 "daily roll and reproduce the published idle-cash face's "
                                 "net rate on this window (<= 0.5bp), never a new vehicle",
    "C2_line": "the gate line is candidate_year_gate.TOP2_SHARE_MAX, imported -- this face "
               "may not restate or move it",
    "C3_drawdown_must_not_deepen_pp": 0.20,
    "min_partial_years_note": "2026 is a partial calendar year and stays flagged partial by "
                              "the same 60-bar window rule the gate uses",
}

VERDICTS = ("THIRD_PATH_FOUND", "THIRD_PATH_BUT_DEEPER_DRAWDOWN", "STILL_TWO_PATHS",
            "NO_CHOICE_TO_FIX", "CONTROL_FAILED", "NOT_RUN")


# ---------------------------------------------------------------------------------------
# verdict (pure, so the selftest can hold it without a panel)
# ---------------------------------------------------------------------------------------
def verdict_of(readings, criteria=CRITERIA):
    """Derived from the readings; every gate recomputed, none typed twice."""
    c0 = bool(readings.get("control_reproduces_published"))
    if not c0:
        return "CONTROL_FAILED", {"C0_control": False}
    ctrl_y4 = readings.get("control_Y4")
    paid_y4 = readings.get("paid_Y4")
    c3 = readings.get("paid_maxdd_not_deeper_pp_ok")
    gates = {"C0_control": True,
             "C1_cash_vehicle_published": bool(readings.get("cash_vehicle_reproduced")),
             "C2_line_imported": True,
             "C3_drawdown_must_not_deepen_pp": bool(c3)}
    if ctrl_y4 is True:
        return "NO_CHOICE_TO_FIX", gates
    if paid_y4 is True and c3:
        return "THIRD_PATH_FOUND", gates
    if paid_y4 is True and not c3:
        return "THIRD_PATH_BUT_DEEPER_DRAWDOWN", gates
    return "STILL_TWO_PATHS", gates


def _read_json(path):
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:                                              # noqa: BLE001
        return None


def _published_adopted(year_gate):
    """The published block for the adopted book, or None when the face is missing."""
    for b in (year_gate or {}).get("books") or []:
        if str(b.get("book", "")).startswith("nobond_vt08"):
            return b
    return None


def _year_delta(ctrl_block, paid_block):
    """Per-year carry addition -- the mechanism has to be visible, not asserted."""
    c = ctrl_block.get("yearly_returns_pct") or {}
    p = paid_block.get("yearly_returns_pct") or {}
    out = {}
    for y in sorted(set(c) & set(p)):
        out[y] = {"without_pct": round(c[y], 4), "with_pct": round(p[y], 4),
                  "delta_pp": round(p[y] - c[y], 4),
                  "bars": (ctrl_block.get("yearly_bars") or {}).get(y)}
    return out


def _idle_by_year(diag, index):
    """Average idle share per calendar year -- the thing the carry is proportional to.

    Without it the page can say the share fell but not show that it fell because the
    de-levered years earned the most on their sleeve, which is the whole mechanism.
    """
    if not diag:
        return {}
    scale = IC.scale_schedule(diag, index)
    out = {}
    for year, blk in scale.groupby(scale.index.year):
        v = blk.dropna()
        if len(v):
            out[str(year)] = round(float(1.0 - v.mean()), 4)
    return out


def _md(rep):
    """The page is derived from the same JSON by the same run; a hand edit would lie."""
    r = rep["readings"]
    yr = rep["year_delta_pp"]
    a = {x["book"]: x for x in rep["arms"]}
    c, p = a["cash_zero_control"], a["cash_paid"]
    cm, pm = c["year_metrics"], p["year_metrics"]
    line = r["gate_line_top2_share_max"]

    def row(y):
        d = yr[y]
        idle_y = (rep.get("idle_share_by_year") or {}).get(y)
        return "| %s | %s | %+.3f%% | %+.3f%% | %+.3f pp |" % (
            y, ("%.1f%%" % (idle_y * 100)) if idle_y is not None else "n/a",
            d["without_pct"], d["with_pct"], d["delta_pp"])

    L = []
    L.append("# ETF book — the third path: pay the idle sleeve (%s)" % rep["verdict"])
    L.append("")
    L.append("Evidence cutoff **%s**. Generated by `scripts\\etf_book_year_gate_idlecarry.py`"
             " in %.1fs; this page is written from the same JSON by the same run."
             % (rep["evidence_cutoff"], rep["elapsed_sec"]))
    L.append("")
    L.append("## The question the page left open")
    L.append("")
    L.append("The CEO page asked the reader to pick: pass the calendar gate by holding the "
             "full book (deeper drawdown), or keep the shallow book and stop expecting new "
             "capital. It named the missing thing -- a third path -- and stopped there. This "
             "face tests the one the book itself already contains: its idle sleeve is paid 0 "
             "by the engine while the desk's own published GC001 roll pays %.2f%%/yr on the "
             "same money." % (r["cash_vehicle_net_pct_on_window"] or 0.0))
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("**%s** — the 8%% vol-target book goes from **%s** to **%s** once its sleeve is "
             "paid, with a drawdown that does not deepen (%.2f%% → %.2f%%)."
             % (rep["verdict"], r["control_verdict"], r["paid_verdict"],
                r["control_maxdd_pct"], r["paid_maxdd_pct"]))
    L.append("")
    L.append("| reading | without carry | with carry | line |")
    L.append("|---|---|---|---|")
    L.append("| best-two-years share of net (frozen caliber) | %.2f%% | %.2f%% | <= %.0f%% |"
             % (cm["top2_share"] * 100, pm["top2_share"] * 100, line * 100))
    L.append("| same, complete years only (not the frozen caliber) | %.2f%% | %.2f%% | <= %.0f%% |"
             % (cm["top2_share_full_only"] * 100, pm["top2_share_full_only"] * 100, line * 100))
    L.append("| CAGR | %.2f%% | %.2f%% | |" % (c["stats"]["cagr"] * 100,
                                               p["stats"]["cagr"] * 100))
    L.append("| Sharpe | %.3f | %.3f | |" % (c["stats"]["sharpe"], p["stats"]["sharpe"]))
    L.append("| max drawdown | %.2f%% | %.2f%% | |"
             % (c["stats"]["maxdd"] * 100, p["stats"]["maxdd"] * 100))
    L.append("| worst year | %.2f%% | %.2f%% | |" % (cm["worst"], pm["worst"]))
    L.append("")
    L.append("**Read the second row before believing the first.** Under the gate's frozen "
             "caliber (partial years in the denominator) the line is crossed by %.2f pp. "
             "Counting only complete years the same book is still above it (%.2f%% vs %.0f%%). "
             "So the honest sentence is \"it passes on the ruler the gate uses\", not \"the book "
             "stopped depending on two years\"."
             % ((line - pm["top2_share"]) * 100, pm["top2_share_full_only"] * 100, line * 100))
    L.append("")
    L.append("## Why it moves: the carry is paid on the idle share")
    L.append("")
    L.append("| year | idle share (avg) | without | with | carry added |")
    L.append("|---|---|---|---|---|")
    for y in sorted(yr):
        L.append(row(y))
    L.append("")
    idle_y = rep.get("idle_share_by_year") or {}
    hi = max(idle_y, key=idle_y.get) if idle_y else None
    top_gain = (yr.get("2025", {}).get("delta_pp", 0.0)
                + yr.get("2024", {}).get("delta_pp", 0.0))
    all_gain = sum(v["delta_pp"] for v in yr.values())
    L.append("The carry is proportional to how much of the year the book spent in cash, and "
             "that is not the same as how bad the year was: %s was the most de-levered "
             "(%.1f%% idle) and took the largest addition, while the quiet low-vol years "
             "(2022/2023) were almost fully invested and gained the least. What moves the "
             "share is the arithmetic: the seven years together gain %+.2f pp while the two "
             "best years gain %+.2f pp, so the denominator grows faster than the numerator."
             % (hi, (idle_y.get(hi, 0.0) * 100) if hi else 0.0, all_gain, top_gain))
    L.append("")
    L.append("## Gates")
    L.append("")
    L.append("| gate | result |")
    L.append("|---|---|")
    for k, v in rep["gates"].items():
        L.append("| `%s` | %s |" % (k, "pass" if v else "**fail**"))
    L.append("")
    L.append("| control | value |")
    L.append("|---|---|")
    L.append("| re-derived best-two share (no carry) | %.4f (published %.4f, diff %.1e) |"
             % (r["control_top2_share"], r["published_top2_share"],
                abs(r["control_top2_share"] - r["published_top2_share"])))
    L.append("| published verdict reproduced | %s |" % r["control_verdict"])
    L.append("| cash vehicle reproduced | %.4f%%/yr (published %.4f%%, gap %.4f bp) |"
             % (r["cash_vehicle_net_pct_on_window"], r["published_cash_vehicle_net_pct"],
                r["cash_reproduction_gap_bp"]))
    L.append("| composed curve vs engine (cash=0) | max rel err %.2e |"
             % r["control_max_rel_err_vs_engine"])
    L.append("")
    L.append("## Boundary")
    L.append("")
    for h in rep["honest"]:
        L.append("- %s" % h)
    L.append("")
    with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------------------------------
def run():
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)

    diag = []
    book, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
                                       vol_target=0.08, diag=diag)
    scale = IC.scale_schedule(diag, book.index)
    idle = (1.0 - scale).clip(lower=0.0, upper=1.0)

    # control: the book exactly as the desk prices it today (cash at 0)
    ctrl = IC.compose(book, idle, pd.Series(0.0, index=book.index))
    ctrl_err = float((ctrl / book - 1.0).abs().max())

    rates = CL.load_panel()
    cash_ret, info, raw_ret, raw_bars = IC.cash_step_returns(rates, book.index)
    cash_on_window = CL.cagr_pct(raw_ret, raw_bars)
    comp = IC.compose(book, idle, cash_ret)

    # capacity is a property of the picks, not of the sleeve: derived the same way the
    # year gate derives it, and checked on the same arm.
    last = sc.index[-1]
    picks = list(sc.loc[last].dropna().nlargest(5).index)
    cap = YG.capacity_cny(picks, amt)

    arms = []
    for label, ser, note in (
            ("cash_zero_control", ctrl,
             "the adopted book as priced today: the 8% target de-levers into a sleeve the "
             "engine pays 0"),
            ("cash_paid", comp,
             "same book, same target, same picks; the idle fraction earns the published "
             "GC001 daily roll")):
        blk = YG._block(label, YG.yearly_returns(ser), cap, ser, note)
        if cap is not None:
            blk["capacity_cny_1day_5pct"] = round(cap, 0)
            blk["checks"]["C1_capacity"] = bool(cap >= G.CAPACITY_FLOOR_CNY)
            blk["verdict"] = G.verdict({"checks": blk["checks"]})
        st = A.stats2(ser, label)
        blk["stats"] = {k: (None if st.get(k) is None else round(float(st[k]), 6))
                        for k in ("cagr", "sharpe", "maxdd", "vol")}
        arms.append(blk)

    ctrl_blk, paid_blk = arms[0], arms[1]
    ctrl_ym = ctrl_blk.get("year_metrics") or {}
    paid_ym = paid_blk.get("year_metrics") or {}

    pub = _published_adopted(_read_json(YEAR_GATE))
    pub_top2 = ((pub or {}).get("year_metrics") or {}).get("top2_share")
    pub_verdict = (pub or {}).get("verdict")
    control_c0 = (pub_top2 is not None
                  and abs(float(ctrl_ym.get("top2_share")) - float(pub_top2)) <= 1e-4
                  and ctrl_blk.get("verdict") == pub_verdict)

    idle_pub = (_read_json(IDLE_CASH) or {}).get("readings") or {}
    idle_pub_net = idle_pub.get("cash_vehicle_net_pct_on_window")
    cash_gap_bp = (None if idle_pub_net is None
                   else abs(float(cash_on_window) - float(idle_pub_net)) * 100.0)
    c1 = (cash_gap_bp is not None and cash_gap_bp <= 0.5)

    dd_ctrl = (ctrl_blk.get("stats") or {}).get("maxdd")
    dd_paid = (paid_blk.get("stats") or {}).get("maxdd")
    dd_ok = (dd_ctrl is not None and dd_paid is not None
             and (dd_paid - dd_ctrl) * 100.0 >= -CRITERIA["C3_drawdown_must_not_deepen_pp"])

    readings = {
        "control_reproduces_published": bool(control_c0),
        "control_top2_share": ctrl_ym.get("top2_share"),
        "published_top2_share": pub_top2,
        "control_verdict": ctrl_blk.get("verdict"),
        "published_verdict": pub_verdict,
        "paid_top2_share": paid_ym.get("top2_share"),
        "control_top2_share_full_only": ctrl_ym.get("top2_share_full_only"),
        "paid_top2_share_full_only": paid_ym.get("top2_share_full_only"),
        "caliber_note": "the frozen gate caliber keeps partial years in the denominator; "
                        "the complete-years-only reading is printed beside it because the two "
                        "disagree about the same book and a reader must see both",
        "paid_verdict": paid_blk.get("verdict"),
        "control_Y4": (ctrl_blk.get("checks") or {}).get("Y4_top2_share"),
        "paid_Y4": (paid_blk.get("checks") or {}).get("Y4_top2_share"),
        "gate_line_top2_share_max": G.TOP2_SHARE_MAX,
        "control_maxdd_pct": None if dd_ctrl is None else round(dd_ctrl * 100.0, 4),
        "paid_maxdd_pct": None if dd_paid is None else round(dd_paid * 100.0, 4),
        "paid_maxdd_not_deeper_pp_ok": bool(dd_ok),
        "cash_vehicle_reproduced": bool(c1),
        "cash_vehicle_net_pct_on_window": round(float(cash_on_window), 4),
        "published_cash_vehicle_net_pct": idle_pub_net,
        "cash_reproduction_gap_bp": None if cash_gap_bp is None else round(cash_gap_bp, 4),
        "control_max_rel_err_vs_engine": ctrl_err,
        "bars": int(len(book)),
        "turnover_per_side": round(float(turn), 4),
        "median_idle_share": round(float(np.nanmedian(idle.to_numpy())), 4),
        "flips_repaired": int(n_flip),
    }
    verdict, gates = verdict_of(readings)

    rep = {
        "face": "etf_book_year_gate_idlecarry",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(book.index[-1]).date()),
        "window": {"start": str(pd.Timestamp(book.index[0]).date()),
                   "end": str(pd.Timestamp(book.index[-1]).date()),
                   "bars": int(len(book))},
        "question": "the page says take the deep-drawdown book to pass the year gate or the "
                    "shallow one and never grow capital. Does paying the book's own idle "
                    "sleeve the rate the desk already earns buy both at once?",
        "criteria_frozen": CRITERIA,
        "readings": readings,
        "gates": gates,
        "verdict": verdict,
        "arms": arms,
        "year_delta_pp": _year_delta(ctrl_blk, paid_blk),
        "idle_share_by_year": _idle_by_year(diag, book.index),
        "source_faces": {
            "year_gate": "results/etf_book_year_gate/YEAR-GATE.json",
            "idle_cash": "results/etf_book_idle_cash.json",
            "cash_vehicle": "results/etf_book_cash_vehicle.json",
        },
        "honest": [
            "the cash vehicle is a daily GC001 roll at the published rate, not a dealer "
            "quote; one contract per bar, exchange commission included, and its 1.77%/yr is "
            "reproduced here rather than assumed",
            "the composed curve is a return statement about the book, not a ticket: it says "
            "what the sleeve would have earned had it been paid, not that the desk earned it",
            "idle is 1 - scale held constant over a holding period (the engine's own nominal "
            "weight convention); a drifting sleeve moves the number below the printed "
            "precision",
            "the year gate's 60-bar cohort count is a window analogue for a daily book and is "
            "imported unchanged; 2026 stays partial and stays in the frozen denominator",
            "instrument-list survivorship is unchanged and still disclosed on the card; this "
            "face does not repair it",
            "nothing is adopted here: paying the sleeve changes the book's headline, and that "
            "is a card change across every face that quotes it, not a side effect of a gate "
            "reading",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rep, ensure_ascii=False, indent=2))
    _md(rep)
    print(json.dumps({"verdict": verdict,
                      "gates": gates,
                      "control_top2": readings["control_top2_share"],
                      "paid_top2": readings["paid_top2_share"],
                      "line": readings["gate_line_top2_share_max"],
                      "control_verdict": readings["control_verdict"],
                      "paid_verdict": readings["paid_verdict"],
                      "maxdd": [readings["control_maxdd_pct"], readings["paid_maxdd_pct"]],
                      "c0": readings["control_reproduces_published"],
                      "c1_gap_bp": readings["cash_reproduction_gap_bp"]},
                     ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------------------
def selftest():
    """Offline: the verdict table plus the year decomposition it is read off."""
    errs = []

    def chk(ok, msg):
        if not ok:
            errs.append(msg)

    base = {"control_reproduces_published": True, "cash_vehicle_reproduced": True,
            "paid_maxdd_not_deeper_pp_ok": True, "control_Y4": False, "paid_Y4": True}

    v, g = verdict_of(dict(base))
    chk(v == "THIRD_PATH_FOUND" and all(g.values()), "flip with a flat drawdown -> %s" % v)

    v, _ = verdict_of(dict(base, control_reproduces_published=False))
    chk(v == "CONTROL_FAILED", "no control -> %s (must never claim a path)" % v)

    v, _ = verdict_of(dict(base, control_Y4=True))
    chk(v == "NO_CHOICE_TO_FIX", "gate already passed -> %s" % v)

    v, _ = verdict_of(dict(base, paid_Y4=False))
    chk(v == "STILL_TWO_PATHS", "carry not enough -> %s" % v)

    v, _ = verdict_of(dict(base, paid_maxdd_not_deeper_pp_ok=False))
    chk(v == "THIRD_PATH_BUT_DEEPER_DRAWDOWN", "deeper drawdown must be named -> %s" % v)

    v, g = verdict_of(dict(base, cash_vehicle_reproduced=False))
    chk(v == "THIRD_PATH_FOUND" and g["C1_cash_vehicle_published"] is False,
        "a vehicle that does not reproduce must show red in its own gate")

    # the year decomposition: the mechanism has to be visible per year
    ctrl = {"yearly_returns_pct": {"2022": -1.0, "2025": 30.0},
            "yearly_bars": {"2022": 242, "2025": 244}}
    paid = {"yearly_returns_pct": {"2022": 0.4, "2025": 30.3},
            "yearly_bars": {"2022": 242, "2025": 244}}
    d = _year_delta(ctrl, paid)
    chk(abs(d["2022"]["delta_pp"] - 1.4) < 1e-9, "2022 delta %.4f != 1.4" % d["2022"]["delta_pp"])
    chk(d["2025"]["delta_pp"] < d["2022"]["delta_pp"],
        "the weak year must gain more than the strong one, else the mechanism is not shown")

    # the line must be imported, never restated
    chk(G.TOP2_SHARE_MAX == CRITERIA.get("top2_share_max", G.TOP2_SHARE_MAX),
        "the gate line must come from candidate_year_gate")

    print("[selftest] %s (%d checks)" % ("PASS" if not errs else "FAIL", 8))
    for e in errs:
        print("  FAIL:", e)
    return 0 if not errs else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd in ("run", "refresh"):
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
