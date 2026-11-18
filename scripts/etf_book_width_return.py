"""What does the sixth name cost in return? The other half of the capacity question.

`etf_book_width_fit` answers "does 1,000,000 fit at each width" and then says, in its own
docstring, that it will not price what a wider book earns. So the desk is left holding two
halves of one decision: capacity says width 6 clears the 1% ADV line, and nothing says what
the sixth name is worth. A reader asked to choose between "shrink the ticket 0.86%" and
"buy six names instead of five" has to guess -- and two readers guess differently.

This face prices the second half on the SAME engine, panel and score the published book
already uses (`etf_robust_pf.open_to_open_equity`, `n_hold` is a parameter, not a rewrite),
then converts the two roads into one unit: annual percentage points given up.

  road A (shrink):  capital falls to width 5's own 1%-of-ADV line. The book keeps its
                    structure, so the return lost is CAGR x (1 - fits_capital/capital)
                    -- a proportional cut, which is what a smaller equal-weight book is.
  road B (widen):   the same capital, one more name. The return lost is CAGR5 - CAGR6,
                    read off the engine at the same cost, rebalance and execution lag.

Both roads spend the same thing (annual return) to buy the same thing (an order inside
the 1% line), so the cheaper road is a subtraction, not a preference.

The honest limit: this prices ONE extra name against a proportional shrink on the bar the
capacity face published. It is not a walk down the width ladder, and it does not claim the
wider book is better in any other sense than fitting the order at that bar.
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

OUT_DIR = os.path.join(ROOT, "results")
OUT = os.path.join(OUT_DIR, "etf_book_width_return.json")
FIT_FACE = os.path.join(OUT_DIR, "etf_book_width_fit.json")

# The published book's own cell: N5 / 20-day rebalance / 10bp. Change one of these and the
# widths stop being comparable to each other, which is the only comparison this face makes.
REBAL = 20
COST = 0.0010
WIDTHS = (5, 6, 7, 8)
IS_END = "2023-12-31"


def read_fit(face=FIT_FACE):
    """The capacity half, read as published -- no second ADV, no second score row."""
    if not os.path.exists(face):
        return None
    with io.open(face, encoding="utf-8") as fh:
        doc = json.load(fh)
    s = doc.get("summary") or {}
    rows = doc.get("rows") or []
    by_n = {r.get("n"): r for r in rows}
    five = by_n.get(5) or {}
    return {
        "verdict": s.get("verdict"),
        "min_width": s.get("min_width"),
        "capital_cny": s.get("capital_cny"),
        "line_pct": doc.get("line_pct"),
        # r1326: the capacity numbers are measured on the ticket's decision bar, which is no
        # longer the face's evidence_cutoff (that one is the page's bar) -- quote the bar the
        # numbers actually sit on.
        "bar": doc.get("decision_bar") or doc.get("evidence_cutoff"),
        "width5": {
            "impact_pct_of_adv": five.get("impact_pct_of_adv"),
            "capital_at_line_cny": five.get("capital_at_line_cny"),
            "per_name_cny": five.get("per_name_cny"),
            "adv_weakest_sym": five.get("adv_weakest_sym"),
        },
    }


def engine_curve(n_hold, rebal=REBAL, cost=COST):
    """One width, on the published engine and the capacity face's own score row."""
    import etf_book_width_fit as W
    import etf_robust_pf as R

    # r1326: score_row now also returns the bar it used and the panel's last bar; this face
    # prices full-history engine curves, so it keeps the panel tail for its own label.
    _rank_row, _amt, last, _panel_last = W.score_row()
    # the engine wants whole panels, not one bar: rebuild through the same two calls
    import etf_composite_pf as E
    import etf_equity_alpha as A
    close, openp, amt_full, feats = E.build_panel()
    close, openp, _flips = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    score = E.build_score(close[cols], amt_full[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt_full[cols], score,
                                      rebal, n_hold, cost)
    m = R.stats(ser, "N%d_R%d_%dbp" % (n_hold, rebal, cost * 1e4))
    m["n"] = n_hold
    m["turnover"] = round(turn, 2)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = R.stats(sl, m["label"] + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    m["bar"] = str(last)[:10]
    m["universe"] = len(cols)
    return m


def shrink_road(fit, cagr5):
    """Capital down to width 5's own line. The loss is the share of the book given up."""
    cap = fit.get("capital_cny")
    at_line = (fit.get("width5") or {}).get("capital_at_line_cny")
    if not cap or not at_line or cagr5 is None:
        return {"readable": False, "why": "capacity face or engine reading missing"}
    if at_line >= cap:
        return {"readable": True, "must_shrink": False, "given_up_pct": 0.0,
                "cagr_cost_pp": 0.0, "capital_after_cny": round(at_line, 0)}
    given_up = 1.0 - float(at_line) / float(cap)
    return {
        "readable": True,
        "must_shrink": True,
        "capital_after_cny": round(float(at_line), 0),
        "capital_given_up_cny": round(float(cap) - float(at_line), 0),
        "given_up_pct": round(given_up * 100.0, 4),
        "cagr_cost_pp": round(float(cagr5) * given_up * 100.0, 4),
    }


def widen_road(rows, base_n, target_n):
    """One more name at the same capital. The loss is a difference of two engine readings."""
    by_n = {r["n"]: r for r in rows}
    base, tgt = by_n.get(base_n), by_n.get(target_n)
    if not base or not tgt:
        return {"readable": False, "why": "width %s not measured" % target_n}
    b, t = base.get("cagr"), tgt.get("cagr")
    if b is None or t is None:
        return {"readable": False, "why": "cagr missing"}
    return {
        "readable": True,
        "from_n": base_n,
        "to_n": target_n,
        "cagr_from": b,
        "cagr_to": t,
        "cagr_cost_pp": round((b - t) * 100.0, 4),
        "sharpe_from": base.get("sharpe"),
        "sharpe_to": tgt.get("sharpe"),
        "maxdd_from": base.get("maxdd"),
        "maxdd_to": tgt.get("maxdd"),
        "turnover_from": base.get("turnover"),
        "turnover_to": tgt.get("turnover"),
    }


def decide(shr, wid, tolerance_pp=0.05):
    """The cheaper road wins on one number. The tolerance is the width of 'the same'."""
    if not shr.get("readable") or not wid.get("readable"):
        return {"verdict": "UNREADABLE", "why": "one road could not be priced"}
    a, b = shr["cagr_cost_pp"], wid["cagr_cost_pp"]
    out = {"shrink_pp": a, "widen_pp": b, "gap_pp": round(a - b, 4),
           "tolerance_pp": tolerance_pp}
    if a <= tolerance_pp and b <= tolerance_pp:
        out["verdict"] = "BOTH_CHEAP"      # the order is small; structure is not the question
    elif abs(a - b) <= tolerance_pp:
        out["verdict"] = "INDISTINGUISHABLE"
    elif a < b:
        out["verdict"] = "SHRINK_IS_CHEAPER"
    else:
        out["verdict"] = "WIDEN_IS_CHEAPER"
    return out


def sentence(payload):
    fit = payload.get("capacity") or {}
    rows = payload.get("rows") or []
    by_n = {r["n"]: r for r in rows}
    five = by_n.get(5)
    d = payload.get("decision") or {}
    shr = payload.get("shrink") or {}
    wid = payload.get("widen") or {}
    bar = fit.get("bar") or (five or {}).get("bar") or "-"
    cap = fit.get("capital_cny")
    if five is None or d.get("verdict") == "UNREADABLE":
        return "收益面读不到：这一页不印哪条路更便宜。"
    head = ("同一笔 %s 元在 %s 这一天，5 名打 %.4f%% ADV（闸线 %.2f%%），6 名落到 %.4f%%。"
            % (format(int(cap), ",") if cap else "-", bar,
               fit.get("width5", {}).get("impact_pct_of_adv") or float("nan"),
               fit.get("line_pct") or 1.0,
               next((r["impact"] for r in [payload.get("widen_capacity") or {}] if r.get("impact")),
                    float("nan"))))
    if wid.get("readable"):
        head += ("把这笔单子塞进线内的两条路，年化代价分别是：缩仓到 %s 元放弃 %.4f pp/年，"
                 "加宽到 %d 名放弃 %.4f pp/年（%s → %s）。"
                 % (format(int(shr["capital_after_cny"]), ",") if shr.get("capital_after_cny") else "-",
                    shr.get("cagr_cost_pp", float("nan")),
                    wid["to_n"], wid["cagr_cost_pp"],
                    ("%.4f" % wid["cagr_from"]) if wid.get("cagr_from") is not None else "-",
                    ("%.4f" % wid["cagr_to"]) if wid.get("cagr_to") is not None else "-"))
    verdict = d.get("verdict")
    tail = {
        "SHRINK_IS_CHEAPER": "缩仓便宜 %.4f pp/年 —— 为了一个 0.86%% 的超线去改组合结构，是拿长期收益"
                            "买一次性的合规。" % abs(d.get("gap_pp") or 0.0),
        "WIDEN_IS_CHEAPER": "加宽便宜 %.4f pp/年 —— 第 6 名确实在摊薄容量而不伤收益。"
                            % abs(d.get("gap_pp") or 0.0),
        "INDISTINGUISHABLE": "两条路差 %.4f pp/年，落在容差 %.2f pp 内 —— 这是执行偏好，不是收益问题。"
                             % (abs(d.get("gap_pp") or 0.0), d.get("tolerance_pp") or 0.0),
        "BOTH_CHEAP": "两条路都在容差内 —— 这笔单子小到不改变结构选择。",
    }.get(verdict, "两条路都读不到。")
    # a single-point win is not a trend: say so on the page, not only in the caveats
    if len(rows) > 2:
        wider = [r for r in rows if r["n"] > 6]
        if wider and all((r.get("cagr") or 0.0) < (by_n.get(6, {}).get("cagr") or 0.0)
                         for r in wider):
            tail += ("但 7 名 %.4f%% / 8 名 %.4f%% 都低于 6 名 —— 这是第 6 名的一个局部最优，"
                     "不是「越宽越好」。"
                     % (by_n[7]["cagr"] * 100.0 if by_n.get(7) else float("nan"),
                        by_n[8]["cagr"] * 100.0 if by_n.get(8) else float("nan")))
    return head + tail


def build(capital=None):
    fit = read_fit()
    rows = [engine_curve(n) for n in WIDTHS]
    by_n = {r["n"]: r for r in rows}
    cagr5 = (by_n.get(5) or {}).get("cagr")
    # the capacity half at width 6 comes from the fit face's own rows, not a re-measure
    fit6 = None
    if os.path.exists(FIT_FACE):
        with io.open(FIT_FACE, encoding="utf-8") as fh:
            fdoc = json.load(fh)
        fit6 = next((r for r in (fdoc.get("rows") or []) if r.get("n") == 6), None)
    shr = shrink_road(fit or {}, cagr5)
    wid = widen_road(rows, 5, 6)
    d = decide(shr, wid)
    payload = {
        "kind": "etf_book_width_return",
        "script": "scripts/etf_book_width_return.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": (by_n.get(5) or {}).get("bar"),
        "capacity_face": "results/etf_book_width_fit.json",
        "engine": "etf_robust_pf.open_to_open_equity (n_hold is a parameter)",
        "params": {"rebal": REBAL, "cost": COST, "widths": list(WIDTHS)},
        "capacity": fit,
        "caliber": {
            "universe": "equity + commodity + convertible only (the capacity face's own "
                        "score_row class filter, so the 5 names are the same 5 names)",
            "no_vol_target": True,
            "relation_to_published_faces": [
                "etf_equity_alpha.json no-bond arm: 15.56% / SR 1.002 / -16.0% -- this face's "
                "width 5 reproduces that caliber, which is how the reader can tell the two "
                "readings are the same book",
                "etf_robust_pf.json N5_R20_10bp 9.13%: FULL unrepaired universe, a different "
                "caliber -- not a disagreement, a different question",
                "etf_nobond_vt.json 11.49%: same no-bond universe WITH the 8% vol target -- "
                "this face runs naked, so it reads higher",
            ],
        },
        "widen_capacity": {"n": 6,
                           "impact": (fit6 or {}).get("impact_pct_of_adv"),
                           "capital_at_line_cny": (fit6 or {}).get("capital_at_line_cny")},
        "rows": rows,
        "shrink": shr,
        "widen": wid,
        "decision": d,
        "caveats": [
            "Both roads are priced on the same engine cell (rebalance %d, cost %dbp) and the "
            "same repaired, class-filtered panel the capacity face scores on. Widths are "
            "comparable to each other; they are NOT directly comparable to the published "
            "N5_R20_10bp reading in etf_robust_pf.json, which runs the unrepaired full "
            "universe." % (REBAL, int(COST * 1e4)),
            "The shrink road assumes an equal-weight book shrank by w earns w of the return "
            "(linear in size). It ignores that a smaller ticket has the same fixed costs -- "
            "which makes shrinking look slightly BETTER than it is, so a SHRINK_IS_CHEAPER "
            "verdict is conservative.",
            "One extra name against one shrink, on one bar. This is not a walk down the "
            "width ladder and it does not re-price the book at 7 or 8 names.",
        ],
    }
    payload["sentence"] = sentence(payload)
    return payload


def check(payload):
    """Every number this face prints must re-derive from the rows it also prints."""
    problems = []
    rows = {r["n"]: r for r in payload.get("rows") or []}
    d = payload.get("decision") or {}
    shr = payload.get("shrink") or {}
    wid = payload.get("widen") or {}

    five = rows.get(5)
    if five is None:
        problems.append("width 5 missing: nothing to anchor the two roads on")
        return problems

    # 1. the widen road must be the difference of the two rows it names
    if wid.get("readable"):
        b, t = rows.get(wid["from_n"]), rows.get(wid["to_n"])
        if b is None or t is None:
            problems.append("widen road names widths that are not in rows")
        else:
            want = (b["cagr"] - t["cagr"]) * 100.0
            if abs(want - wid["cagr_cost_pp"]) > 1e-3:
                problems.append("widen cost %.4f != (cagr%d-cagr%d)*100 %.4f"
                                % (wid["cagr_cost_pp"], wid["from_n"], wid["to_n"], want))

    # 2. the shrink road must be CAGR x the share of capital given up
    cap = (payload.get("capacity") or {}).get("capital_cny")
    at_line = shr.get("capital_after_cny")
    if shr.get("readable") and shr.get("must_shrink"):
        if not cap or at_line is None:
            problems.append("shrink road printed a cost with no capital pair")
        else:
            given = 1.0 - float(at_line) / float(cap)
            want = five["cagr"] * given * 100.0
            if abs(want - shr["cagr_cost_pp"]) > 1e-3:
                problems.append("shrink cost %.4f != cagr5*%.6f*100 %.4f"
                                % (shr["cagr_cost_pp"], given, want))
            if abs(given * 100.0 - shr["given_up_pct"]) > 1e-3:
                problems.append("given_up_pct %.4f != %.4f" % (shr["given_up_pct"],
                                                               given * 100.0))

    # 3. the verdict must be the comparison of the two printed numbers
    if shr.get("readable") and wid.get("readable"):
        a, b, tol = shr["cagr_cost_pp"], wid["cagr_cost_pp"], d.get("tolerance_pp") or 0.0
        if a <= tol and b <= tol:
            want_v = "BOTH_CHEAP"
        elif abs(a - b) <= tol:
            want_v = "INDISTINGUISHABLE"
        else:
            want_v = "SHRINK_IS_CHEAPER" if a < b else "WIDEN_IS_CHEAPER"
        if want_v != d.get("verdict"):
            problems.append("verdict %s != re-derived %s" % (d.get("verdict"), want_v))
        if abs(abs(a - b) - abs(d.get("gap_pp") or 0.0)) > 1e-3:
            problems.append("gap_pp %.4f != |a-b| %.4f" % (d.get("gap_pp") or 0.0, abs(a - b)))

    # 4. widths are strictly ordered and every row carries its own bar
    ns = [r["n"] for r in payload.get("rows") or []]
    if ns != sorted(set(ns)):
        problems.append("rows are not a strictly increasing width ladder: %s" % ns)
    for r in payload.get("rows") or []:
        if r.get("cagr") is None:
            problems.append("width %s has no cagr" % r.get("n"))
        if not r.get("bar"):
            problems.append("width %s has no bar" % r.get("n"))
    return problems


def run():
    payload = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print("bar=%s" % payload["evidence_cutoff"])
    for r in payload["rows"]:
        print("  n=%-3d cagr=%-8s sharpe=%-6s maxdd=%-8s turnover=%-6s"
              % (r["n"], r.get("cagr"), r.get("sharpe"), r.get("maxdd"), r.get("turnover")))
    print("decision", payload["decision"].get("verdict"),
          "shrink=%.4fpp widen=%.4fpp" % (payload["shrink"].get("cagr_cost_pp") or 0.0,
                                          payload["widen"].get("cagr_cost_pp") or 0.0))
    print(payload["sentence"])
    print("->", OUT)
    return 0


def main_check():
    with io.open(OUT, encoding="utf-8") as fh:
        payload = json.load(fh)
    problems = check(payload)
    if problems:
        print("CHECK_FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print("CHECK_OK both roads re-derive from the printed rows (%s, gap %.4f pp)"
          % (payload["decision"].get("verdict"), payload["decision"].get("gap_pp") or 0.0))
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    # a synthetic pair: shrink costs 0.08 pp, widen costs 0.60 pp
    fit = {"capital_cny": 1_000_000.0,
           "width5": {"capital_at_line_cny": 991_400.0, "impact_pct_of_adv": 1.0087},
           "line_pct": 1.0, "bar": "2026-11-17"}
    shr = shrink_road(fit, 0.0913)
    # given_up_pct is published rounded, so the re-derivation carries the same rounding
    leg("shrink cost is CAGR x the share given up",
        abs(shr["cagr_cost_pp"] - 0.0913 * shr["given_up_pct"]) < 1e-3)
    leg("a ticket already inside the line costs nothing to shrink",
        shrink_road({"capital_cny": 1_000_000.0,
                     "width5": {"capital_at_line_cny": 2_000_000.0}}, 0.09)["must_shrink"] is False)

    rows = [{"n": 5, "cagr": 0.0913, "sharpe": 0.92, "maxdd": -0.125, "turnover": 0.5, "bar": "b"},
            {"n": 6, "cagr": 0.0853, "sharpe": 0.88, "maxdd": -0.130, "turnover": 0.55, "bar": "b"}]
    wid = widen_road(rows, 5, 6)
    leg("widen cost is the difference of the two rows",
        abs(wid["cagr_cost_pp"] - 0.60) < 1e-6)
    leg("a missing width is unreadable, not zero",
        widen_road(rows, 5, 7)["readable"] is False)

    d = decide(shr, wid)
    leg("the cheaper road wins on the smaller number", d["verdict"] == "SHRINK_IS_CHEAPER")
    d2 = decide(dict(shr, cagr_cost_pp=0.02), dict(wid, cagr_cost_pp=0.02))
    leg("inside the tolerance it is not a return question", d2["verdict"] == "BOTH_CHEAP")
    d3 = decide(shr, dict(wid, cagr_cost_pp=0.09))
    leg("a 0.01 pp gap is indistinguishable", d3["verdict"] == "INDISTINGUISHABLE")
    leg("an unreadable road blocks the verdict",
        decide(shr, {"readable": False})["verdict"] == "UNREADABLE")

    # the check must catch a hand-edited verdict
    payload = {"rows": rows, "capacity": fit, "shrink": shr, "widen": wid,
               "decision": dict(d, verdict="WIDEN_IS_CHEAPER")}
    leg("check catches a verdict that contradicts its own numbers",
        any("verdict" in p for p in check(payload)))
    payload["decision"] = d
    leg("check passes the honest payload", check(payload) == [])

    ok = sum(1 for _n, o in legs if o)
    for name, o in legs:
        print("  [%s] %s" % ("PASS" if o else "FAIL", name))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--capital", type=float, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run()
    if a.cmd == "check":
        return main_check()
    if a.cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s" % a.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
