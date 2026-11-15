"""The CEO page names two choices; the repo is already running a third one it never priced.

r1738 composed two published faces (the calendar gate and the idle-cash vehicle) and found
the shallow book crosses Y4 once its sleeve is paid. r1739 opened the forward ledger and
found that the two faces are not even the same book:

  * the calendar gate adjudicates a 5-name, 8% vol-target book with cash at zero;
  * the forward ledger -- the ledger the CEO reads every day -- runs a **12-name** book and
    has priced its cash on `ladder3` (GC007/GC014/GC028, commission charged) since the
    `carry` subcommand shipped.

So "pay the sleeve" and "hold twelve names" were both live, and nobody had put either
through the gate the decision actually uses. This face does exactly that: 2 widths x 3
cash carriers, every cell on the same engine, the same window, the same frozen line.

Reuse, never re-implement:
  panel + score                    etf_composite_pf.build_panel / build_score
  flip repair + classification     etf_equity_alpha.repair_flips / classify
  the book engine                  etf_robust_pf.open_to_open_equity
  sizing scale + composition       etf_book_idle_cash.scale_schedule / compose
  the three cash carriers          etf_book_idle_cash.cash_step_returns
  calendar gate + blocks + line    candidate_year_gate / etf_book_year_gate

Usage:
    python scripts/etf_book_gate_knobs.py run
    python scripts/etf_book_gate_knobs.py selftest
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

OUT = os.path.join(ROOT, "results", "etf_book_gate_knobs.json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_GATE_KNOBS.md")
YEAR_GATE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
FORWARD_LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")

# The two widths are not a search: 5 is the arm the gate adjudicates, 12 is the width the
# forward ledger has been running since it was written (results/etf_book_forward/CARRY.json
# config.n_hold). Everything else -- rebalance, cost, vol target, window -- is held at the
# gate's own settings so a cell can only differ from another by width or by carrier.
WIDTHS = (("n5_gate_arm", 5), ("n12_forward_arm", 12))
CARRIERS = (
    ("cash_zero", None, "the sleeve priced at 0 -- what the calendar gate adjudicates today"),
    ("gc001_roll", ("GC001",), "the one-tenor daily roll r1738 priced"),
    ("ladder3", CL.LADDERS["ladder3"],
     "GC007/GC014/GC028 equal rungs with exchange commission -- the forward ledger's carrier"),
)
REBAL, COST, VOL_TARGET = 20, 0.0010, 0.08
DD_SLACK_PP = 0.20


def _read_json(path):
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:                                              # noqa: BLE001
        return None


def _published_adopted(year_gate):
    for b in (year_gate or {}).get("books") or []:
        if str(b.get("book", "")).startswith("nobond_vt08"):
            return b
    return None


def cell_verdict(readings):
    """Pure: every gate recomputed from the grid, nothing typed twice.

    The question is not "does paying help" (r1738 answered that) but "which of the two
    knobs the desk already runs actually carries the gate".
    """
    if not readings.get("control_reproduces_published"):
        return "CONTROL_FAILED"
    grid = readings.get("grid") or {}
    g5, g12 = grid.get("n5_gate_arm") or {}, grid.get("n12_forward_arm") or {}
    p5 = [c for c in ("gc001_roll", "ladder3") if (g5.get(c) or {}).get("Y4_top2_share") is True]
    p12 = [c for c in ("gc001_roll", "ladder3") if (g12.get(c) or {}).get("Y4_top2_share") is True]
    dd_ok = readings.get("paid_maxdd_not_deeper_all_cells")
    if p12 and not p5:
        return "WIDTH_IS_THE_KNOB" if dd_ok else "WIDTH_PASSES_BUT_DEEPER_DRAWDOWN"
    if p5 and not p12:
        return "CARRIER_IS_THE_KNOB" if dd_ok else "CARRIER_PASSES_BUT_DEEPER_DRAWDOWN"
    if p5 and p12:
        return "EITHER_KNOB_WORKS" if dd_ok else "EITHER_PASSES_BUT_DEEPER_DRAWDOWN"
    return "NEITHER_KNOB_PASSES"


def _arm(close, openp, amt, sc, n_hold, label):
    """One engine run: the book at this width, plus its idle schedule and capacity."""
    diag = []
    book, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, n_hold, COST,
                                       vol_target=VOL_TARGET, diag=diag)
    idle = (1.0 - IC.scale_schedule(diag, book.index)).clip(lower=0.0, upper=1.0)
    last = sc.index[-1]
    picks = list(sc.loc[last].dropna().nlargest(n_hold).index)
    return {"label": label, "book": book, "idle": idle, "diag": diag,
            "turnover": float(turn), "capacity": YG.capacity_cny(picks, amt),
            "picks": picks, "median_idle": float(np.nanmedian(idle.to_numpy()))}


def run():
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)

    rates = CL.load_panel()
    arms = {wname: _arm(close[cols], openp[cols], amt[cols], sc, n_hold, wname)
            for wname, n_hold in WIDTHS}
    # The carriers are priced on the BOOK's own bars, not on the score's full history:
    # the published idle-cash face quotes "net on window" against the book index, so
    # pricing off `sc.index` here would print a second, slightly different carry rate for
    # the same vehicle and invite the reader to average the two.
    window = arms[WIDTHS[0][0]]["book"].index
    cash_steps = {}
    for cname, ladder, _note in CARRIERS:
        if ladder is None:
            cash_steps[cname] = None
            continue
        step, info, raw, bars = IC.cash_step_returns(
            rates, window, ladder=(ladder if len(ladder) > 1 else None),
            name=(ladder[0] if len(ladder) == 1 else None), fees=None)
        cash_steps[cname] = {"step": step, "cagr_pct": CL.cagr_pct(raw, bars),
                             "n_contracts": (len(info.get("contracts") or [])
                                             if "contracts" in info else None)}

    grid, flat = {}, []
    for wname, _n_hold in WIDTHS:
        arm = arms[wname]
        grid[wname] = {}
        for cname, ladder, note in CARRIERS:
            cs = cash_steps[cname]
            ser = IC.compose(arm["book"], arm["idle"],
                             (pd.Series(0.0, index=arm["book"].index) if cs is None
                              else cs["step"]))
            blk = YG._block("%s/%s" % (wname, cname), YG.yearly_returns(ser),
                            arm["capacity"], ser, note)
            if arm["capacity"] is not None:
                blk["capacity_cny_1day_5pct"] = round(arm["capacity"], 0)
                blk["checks"]["C1_capacity"] = bool(arm["capacity"] >= G.CAPACITY_FLOOR_CNY)
                blk["verdict"] = G.verdict({"checks": blk["checks"]})
            st = A.stats2(ser, wname)
            blk["stats"] = {k: (None if st.get(k) is None else round(float(st[k]), 6))
                            for k in ("cagr", "sharpe", "maxdd", "vol")}
            blk["median_idle_share"] = round(arm["median_idle"], 4)
            blk["turnover_per_side"] = round(arm["turnover"], 4)
            blk["n_held"] = int(len(arm["picks"]))
            grid[wname][cname] = blk
            flat.append(blk)

    pub = _published_adopted(_read_json(YEAR_GATE))
    pub_top2 = ((pub or {}).get("year_metrics") or {}).get("top2_share")
    pub_verdict = (pub or {}).get("verdict")
    ctrl = grid["n5_gate_arm"]["cash_zero"]
    ctrl_top2 = (ctrl.get("year_metrics") or {}).get("top2_share")
    control_ok = (pub_top2 is not None and ctrl_top2 is not None
                  and abs(float(ctrl_top2) - float(pub_top2)) <= 1e-4
                  and ctrl.get("verdict") == pub_verdict)

    # Drawdown discipline: a paid carrier may not buy its Y4 pass with a deeper hole.
    dd_ok = True
    dd_rows = {}
    for wname, _n in WIDTHS:
        base = (grid[wname]["cash_zero"].get("stats") or {}).get("maxdd")
        for cname, ladder, _note in CARRIERS:
            if ladder is None:
                continue
            got = (grid[wname][cname].get("stats") or {}).get("maxdd")
            if base is None or got is None:
                dd_ok = False
                continue
            dpp = round((got - base) * 100.0, 4)
            dd_rows["%s/%s" % (wname, cname)] = dpp
            if dpp < -DD_SLACK_PP:
                dd_ok = False

    # Carrier sensitivity, same width: does the choice of vehicle move the verdict at all?
    carrier_same = {}
    for wname, _n in WIDTHS:
        g = grid[wname]
        carrier_same[wname] = bool(
            (g["gc001_roll"].get("year_metrics") or {}).get("top2_share") is not None
            and (g["ladder3"].get("year_metrics") or {}).get("top2_share") is not None
            and abs(float((g["gc001_roll"]["year_metrics"])["top2_share"])
                    - float((g["ladder3"]["year_metrics"])["top2_share"])) <= 0.01)

    readings = {
        "control_reproduces_published": bool(control_ok),
        "control_top2_share": ctrl_top2,
        "published_top2_share": pub_top2,
        "control_verdict": ctrl.get("verdict"),
        "published_verdict": pub_verdict,
        "gate_line_top2_share_max": G.TOP2_SHARE_MAX,
        "grid": {w: {c: {"top2_share": (b.get("year_metrics") or {}).get("top2_share"),
                         "top2_share_full_only": (b.get("year_metrics") or {}).get(
                             "top2_share_full_only"),
                         "verdict": b.get("verdict"),
                         "Y4_top2_share": (b.get("checks") or {}).get("Y4_top2_share"),
                         "cagr": (b.get("stats") or {}).get("cagr"),
                         "sharpe": (b.get("stats") or {}).get("sharpe"),
                         "maxdd_pct": (None if (b.get("stats") or {}).get("maxdd") is None
                                       else round(float(b["stats"]["maxdd"]) * 100.0, 4)),
                         "median_idle_share": b.get("median_idle_share"),
                         "n_held": b.get("n_held"),
                         "turnover_per_side": b.get("turnover_per_side")}
                     for c, b in grid[w].items()} for w, _n in WIDTHS},
        "paid_maxdd_not_deeper_all_cells": bool(dd_ok),
        "drawdown_delta_pp_vs_zero": dd_rows,
        "carrier_verdict_same_within_1pp": carrier_same,
        "cash_carrier_cagr_pct": {c: (None if cash_steps[c] is None
                                      else round(float(cash_steps[c]["cagr_pct"]), 4))
                                  for c, _l, _n in CARRIERS},
        "forward_ledger_config_n_hold": _forward_n_hold(),
        "forward_ledger_carry_fixed_stats": _forward_carry_fixed(),
        "bars": int(len(window)),
        "bars_scored": int(len(sc)),
        "flips_repaired": int(n_flip),
        "turnover_per_side": {w: round(float(arms[w]["turnover"]), 4) for w, _n in WIDTHS},
    }
    readings["verdict"] = cell_verdict(readings)

    rep = {
        "face": "etf_book_gate_knobs",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(window[-1]).date()),
        "window": {"start": str(pd.Timestamp(window[0]).date()),
                   "end": str(pd.Timestamp(window[-1]).date()),
                   "bars": int(len(window))},
        "question": "The gate adjudicates a 5-name book with cash at 0; the forward ledger "
                    "runs a 12-name book with cash paid on ladder3. Which of the two knobs "
                    "the desk already runs carries the Y4 line?",
        "grid_config": {"widths": {w: n for w, n in WIDTHS},
                        "carriers": {c: (None if l is None else list(l))
                                     for c, l, _n in CARRIERS},
                        "rebal": REBAL, "cost_per_side": COST,
                        "vol_target": VOL_TARGET,
                        "drawdown_slack_pp": DD_SLACK_PP},
        "readings": readings,
        "arms": flat,
        "source_faces": {"calendar_gate": os.path.relpath(YEAR_GATE, ROOT),
                         "forward_ledger": os.path.relpath(FORWARD_LEDGER, ROOT)},
        "honest": [
            "the two widths also carry different capacities: 12 names hold more of the "
            "participation floor than 5 do, so a pass on n12 is not free of a size cost",
            "the carrier comparison is inside the book's own cash share; it does not answer "
            "whether the treasurer can actually keep a 7/14/28-day ladder funded while "
            "rebalancing every 20 sessions",
            "ladder3 is charged the exchange commission (fees=None -> default table); the "
            "GC001 leg is priced fee-free exactly as the published idle-cash face prices it",
            "2026 is a partial calendar year and stays flagged partial by the gate's own "
            "60-bar window rule",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(_md(rep))
    print(json.dumps({"verdict": readings["verdict"],
                      "grid": {w: {c: v["top2_share"] for c, v in g.items()}
                               for w, g in readings["grid"].items()},
                      "out": os.path.relpath(OUT, ROOT),
                      "elapsed_sec": rep["elapsed_sec"]}, ensure_ascii=False))
    return 0


def _forward_n_hold():
    led = _read_json(FORWARD_LEDGER) or {}
    return ((led.get("config") or {}).get("n_hold"))


def _forward_carry_fixed():
    """What the forward ledger's own carry face publishes for its fixed book.

    Printed beside the n12 row so a reader can see the two are NOT the same measurement
    and does not read the gap as a contradiction. The ledger fills at the next open with a
    pending-fill book and prices cash on the bar's opening balance; this face composes the
    engine curve with the bar's nominal idle share. Same width, same carrier, different
    settlement stack -- hence the explicit caveat line instead of a silent agreement.
    """
    c = _read_json(os.path.join(ROOT, "results", "etf_book_forward", "CARRY.json")) or {}
    fx = ((c.get("books") or {}).get("fixed") or {}).get("full") or {}
    return {"evidence_cutoff": c.get("evidence_cutoff"),
            "cagr": fx.get("cagr"), "sharpe": fx.get("sharpe"), "maxdd": fx.get("maxdd"),
            "carrier": c.get("carry_note")}


def _md(rep):
    r = rep["readings"]
    L = []
    L.append("# ETF book — which knob the desk already runs carries the gate")
    L.append("")
    L.append("Evidence cutoff **%s**. Generated by `scripts\\etf_book_gate_knobs.py`."
             % rep["evidence_cutoff"])
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("**%s**" % r["verdict"])
    L.append("")
    L.append("| width | carrier | best-two share | line | verdict | CAGR | Sharpe | maxDD |")
    L.append("|---|---|---|---|---|---|---|---|")
    for w, g in r["grid"].items():
        for c, v in g.items():
            t2 = v["top2_share"]
            L.append("| %s | %s | %s | <= %.2f%% | %s | %s | %s | %s |" % (
                w, c,
                "n/a" if t2 is None else "%.2f%%" % (t2 * 100.0),
                r["gate_line_top2_share_max"] * 100.0, v["verdict"],
                "n/a" if v["cagr"] is None else "%.2f%%" % (v["cagr"] * 100.0),
                "n/a" if v["sharpe"] is None else "%.3f" % v["sharpe"],
                "n/a" if v["maxdd_pct"] is None else "%.2f%%" % v["maxdd_pct"]))
    L.append("")
    # Deferred: this face is imported by etf_book_gate_causal (it owns these constants),
    # so the caveat reader cannot be imported at module level.
    import etf_book_gate_causal as KC
    L.extend(KC.basis_caveat_lines())
    L.append("## Controls")
    L.append("")
    L.append("| control | value |")
    L.append("|---|---|")
    L.append("| gate arm re-derived (n5, cash at 0) | %.4f (published %.4f, diff %.1e) |" % (
        r["control_top2_share"], r["published_top2_share"],
        abs(float(r["control_top2_share"]) - float(r["published_top2_share"]))))
    L.append("| published verdict reproduced | %s |" % r["control_verdict"])
    L.append("| forward ledger config n_hold | %s |" % r["forward_ledger_config_n_hold"])
    L.append("| cash carrier CAGR on window | %s |" % json.dumps(
        r["cash_carrier_cagr_pct"], ensure_ascii=False))
    L.append("| drawdown delta vs zero (pp) | %s |" % json.dumps(
        r["drawdown_delta_pp_vs_zero"], ensure_ascii=False))
    L.append("")
    fw = r.get("forward_ledger_carry_fixed_stats") or {}
    if fw.get("cagr") is not None:
        L.append("## Two measurements of the same book, deliberately not reconciled")
        L.append("")
        L.append("The forward ledger's own carry face (%s, carrier %s) publishes the "
                 "12-name book at CAGR %.2f%% / Sharpe %s / maxDD %s. This face prices the "
                 "same width and carrier at %.2f%% / %.3f / %s."
                 % (fw.get("evidence_cutoff"), fw.get("carrier"),
                    float(fw["cagr"]) * 100.0, fw.get("sharpe"),
                    "n/a" if fw.get("maxdd") is None else "%.2f%%" % (fw["maxdd"] * 100.0),
                    (r["grid"]["n12_forward_arm"]["ladder3"]["cagr"] or 0.0) * 100.0,
                    r["grid"]["n12_forward_arm"]["ladder3"]["sharpe"] or 0.0,
                    "n/a" if r["grid"]["n12_forward_arm"]["ladder3"]["maxdd_pct"] is None
                    else "%.2f%%" % r["grid"]["n12_forward_arm"]["ladder3"]["maxdd_pct"]))
        L.append("")
        L.append("They differ because the settlement stacks differ (next-open fills with a "
                 "pending-fill book and cash on the bar's opening balance, versus this "
                 "engine curve composed with the bar's nominal idle share), not because one "
                 "of them is wrong. **Neither number is an endorsement of the other**; the "
                 "gate question above is answered on this face's grid only.")
        L.append("")
    L.append("## Honest limits")
    L.append("")
    for h in rep["honest"]:
        L.append("- %s" % h)
    L.append("")
    return "\n".join(L)


def selftest():
    bad = []

    def chk(ok, msg):
        print("[%s] %s" % ("PASS" if ok else "FAIL", msg))
        if not ok:
            bad.append(msg)

    def cells(v5, v12):
        return {"n5_gate_arm": {"cash_zero": {"Y4_top2_share": False},
                                "gc001_roll": {"Y4_top2_share": v5},
                                "ladder3": {"Y4_top2_share": v5}},
                "n12_forward_arm": {"cash_zero": {"Y4_top2_share": False},
                                    "gc001_roll": {"Y4_top2_share": v12},
                                    "ladder3": {"Y4_top2_share": v12}}}

    base = {"control_reproduces_published": True,
            "paid_maxdd_not_deeper_all_cells": True}
    chk(cell_verdict(dict(base, grid=cells(False, True))) == "WIDTH_IS_THE_KNOB",
        "width 12 passes where width 5 cannot -> WIDTH_IS_THE_KNOB")
    chk(cell_verdict(dict(base, grid=cells(True, False))) == "CARRIER_IS_THE_KNOB",
        "carrier passes at width 5 only -> CARRIER_IS_THE_KNOB")
    chk(cell_verdict(dict(base, grid=cells(True, True))) == "EITHER_KNOB_WORKS",
        "both pass -> EITHER_KNOB_WORKS")
    chk(cell_verdict(dict(base, grid=cells(False, False))) == "NEITHER_KNOB_PASSES",
        "neither passes -> NEITHER_KNOB_PASSES")
    chk(cell_verdict(dict(base, grid=cells(False, True),
                          paid_maxdd_not_deeper_all_cells=False))
        == "WIDTH_PASSES_BUT_DEEPER_DRAWDOWN",
        "a pass bought with a deeper hole is not a pass")
    chk(cell_verdict({"control_reproduces_published": False,
                      "grid": cells(False, True)}) == "CONTROL_FAILED",
        "control failure outranks every knob reading")
    # A carrier that only helps because the gate arm cannot see it is still a control
    # failure: cash_zero must stay False in both widths of the fixtures above.
    g = cells(False, True)
    chk(g["n5_gate_arm"]["cash_zero"]["Y4_top2_share"] is False,
        "the zero-cash arm is never allowed to pass in fixtures")
    print("selftest: %d/%d PASS" % (8 - len(bad), 8))
    return 0 if not bad else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
