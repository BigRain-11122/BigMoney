"""Is the sixth name a real edge, or an artifact of the 20-day rebalance it was measured on?

`etf_book_width_return` found width 6 earning 17.00% against width 5's 15.50% at the published
cell (20-day rebalance, 10bp), and printed that 7 and 8 names were worse -- so the win is a
local optimum, not a monotone trend. That leaves the question every local optimum has to
answer before anyone trades it: does it survive a change to the one parameter that shaped it?

The cheap, decisive test: hold everything else and move the rebalance clock. 20 days is a
month; 10 is a fortnight; 40 is two months. A sixth name that beats the fifth at all three is
a width effect. One that only wins at 20 is the calendar talking.

Only widths 5 and 6 are run here on purpose: the question is a pairwise survival test, not a
walk down the ladder. The 20-day pair is read from `etf_book_width_return.json` rather than
re-run, so the three clocks are measured on the same code path but only two of them cost
compute this round.
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
OUT = os.path.join(OUT_DIR, "etf_book_width_neighbors.json")
WR_FACE = os.path.join(OUT_DIR, "etf_book_width_return.json")

COST = 0.0010
CLOCKS = (10, 20, 40)          # the 20 is read from the width_return face, not re-run
PAIR = (5, 6)
IS_END = "2023-12-31"


def panel():
    """The same repaired, class-filtered panel the capacity and return faces score on."""
    import etf_composite_pf as E
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, _flips = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    score = E.build_score(close[cols], amt[cols], feats)
    return close[cols], openp[cols], amt[cols], score


def run_cell(close, openp, amt, score, rebal, n_hold):
    import etf_robust_pf as R

    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, COST)
    m = R.stats(ser, "N%d_R%d_%dbp" % (n_hold, rebal, COST * 1e4))
    m["n"] = n_hold
    m["rebal"] = rebal
    m["turnover"] = round(turn, 2)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = R.stats(sl, m["label"] + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    return m


def read_twenty():
    """The 20-day pair as published -- re-running it would be a second measurement of one cell."""
    if not os.path.exists(WR_FACE):
        return None, "width_return face absent (run scripts/etf_book_width_return.py first)"
    with io.open(WR_FACE, encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = {r.get("n"): r for r in (doc.get("rows") or [])}
    five, six = rows.get(5), rows.get(6)
    if not five or not six:
        return None, "width_return face has no width 5/6 pair"
    return ({"n": 5, "rebal": 20, "cagr": five.get("cagr"), "sharpe": five.get("sharpe"),
             "maxdd": five.get("maxdd"), "turnover": five.get("turnover"),
             "bar": five.get("bar")},
            {"n": 6, "rebal": 20, "cagr": six.get("cagr"), "sharpe": six.get("sharpe"),
             "maxdd": six.get("maxdd"), "turnover": six.get("turnover"),
             "bar": six.get("bar")}), None


def judge(cells):
    """Does the sixth name beat the fifth at every clock, or only at the one it was found on?"""
    by_rebal = {}
    for c in cells:
        by_rebal.setdefault(c["rebal"], {})[c["n"]] = c
    clocks = []
    for rebal in sorted(by_rebal):
        pair = by_rebal[rebal]
        five, six = pair.get(5), pair.get(6)
        if not five or not six or five.get("cagr") is None or six.get("cagr") is None:
            clocks.append({"rebal": rebal, "readable": False})
            continue
        clocks.append({
            "rebal": rebal,
            "readable": True,
            "cagr5": five["cagr"],
            "cagr6": six["cagr"],
            "delta_pp": round((six["cagr"] - five["cagr"]) * 100.0, 4),
            "six_wins": bool(six["cagr"] > five["cagr"]),
        })
    readable = [c for c in clocks if c["readable"]]
    if not readable:
        return {"verdict": "UNREADABLE", "clocks": clocks}
    wins = [c for c in readable if c["six_wins"]]
    losses = [c for c in readable if not c["six_wins"]]
    if not losses:
        v = "SIX_NAMES_SURVIVES_EVERY_CLOCK"
    elif not wins:
        v = "SIX_NAMES_WINS_NOWHERE"
    else:
        v = "SIX_NAMES_IS_A_CLOCK_ARTIFACT"
    return {
        "verdict": v,
        "clocks": clocks,
        "n_readable": len(readable),
        "wins": [c["rebal"] for c in wins],
        "losses": [c["rebal"] for c in losses],
        "min_delta_pp": round(min(c["delta_pp"] for c in readable), 4),
        "max_delta_pp": round(max(c["delta_pp"] for c in readable), 4),
    }


def sentence(payload):
    j = payload.get("judgement") or {}
    v = j.get("verdict")
    clocks = [c for c in (j.get("clocks") or []) if c.get("readable")]
    if not clocks:
        return "邻域稳健性读不到：这一页不印「第 6 名稳不稳」的结论。"
    parts = "、".join("%d 日 %+.4f pp" % (c["rebal"], c["delta_pp"]) for c in clocks)
    head = "把调仓钟从 20 日挪到别处再问一次第 6 名（5 名→6 名的年化差）：%s。" % parts
    if v == "SIX_NAMES_SURVIVES_EVERY_CLOCK":
        return head + ("三个周期里第 6 名都赢 —— 这不是 20 日调仓的巧合，是宽度效应。"
                       "最差一格仍有 %+.4f pp。" % j["min_delta_pp"])
    if v == "SIX_NAMES_WINS_NOWHERE":
        return head + "哪个周期都不赢 —— 20 日那一格的正号本身就该重新审。"
    if v == "SIX_NAMES_IS_A_CLOCK_ARTIFACT":
        return head + ("赢在 %s、输在 %s —— **第 6 名的「更好」是调仓钟给的，不是宽度给的**；"
                       "按 20 日那一格去改组合结构，等于把一个日历参数当成alpha。"
                       % ("/".join(str(x) for x in j["wins"]),
                          "/".join(str(x) for x in j["losses"])))
    return head + "判词读不出。"


def build():
    twenty, why = read_twenty()
    cells = []
    if twenty is not None:
        cells.extend(twenty)
    close = openp = amt = score = None
    try:
        close, openp, amt, score = panel()
    except Exception as exc:                                  # noqa: BLE001
        why = "panel unavailable: %s" % str(exc)[:80]
    if close is not None:
        for rebal in CLOCKS:
            if rebal == 20:
                continue
            for n in PAIR:
                cells.append(run_cell(close, openp, amt, score, rebal, n))
    j = judge(cells)
    payload = {
        "kind": "etf_book_width_neighbors",
        "script": "scripts/etf_book_width_neighbors.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": (next((c.get("bar") for c in cells if c.get("bar")), None)),
        "upstream": "results/etf_book_width_return.json",
        "params": {"cost": COST, "clocks": list(CLOCKS), "pair": list(PAIR)},
        "cells": cells,
        "judgement": j,
        "why": why,
        "caveats": [
            "Only widths 5 and 6 are run: the question is whether that pair survives the "
            "rebalance clock, not a walk down the ladder.",
            "The 20-day pair is READ from the upstream face, not re-measured, so the three "
            "clocks are not three independent measurements of the same cell.",
            "Same repaired, class-filtered panel and the same 10bp one-way cost as the "
            "upstream face. A different panel would make the deltas incomparable.",
        ],
    }
    payload["sentence"] = sentence(payload)
    return payload


def check(payload):
    problems = []
    j = payload.get("judgement") or {}
    cells = payload.get("cells") or []
    by = {}
    for c in cells:
        by.setdefault(c.get("rebal"), {})[c.get("n")] = c

    # 1. every judging clock must re-derive its own delta from the cells it also prints
    for clk in j.get("clocks") or []:
        if not clk.get("readable"):
            continue
        pair = by.get(clk["rebal"]) or {}
        five, six = pair.get(5), pair.get(6)
        if not five or not six:
            problems.append("clock %s judged but its cells are absent" % clk["rebal"])
            continue
        want = round((six["cagr"] - five["cagr"]) * 100.0, 4)
        if abs(want - clk["delta_pp"]) > 1e-3:
            problems.append("clock %s delta %.4f != %.4f" % (clk["rebal"], clk["delta_pp"], want))
        if bool(six["cagr"] > five["cagr"]) != clk["six_wins"]:
            problems.append("clock %s winner does not match its cagrs" % clk["rebal"])

    # 2. the verdict must be the sign pattern of the readable clocks
    readable = [c for c in (j.get("clocks") or []) if c.get("readable")]
    if readable:
        wins = [c for c in readable if c["six_wins"]]
        if not wins:
            want_v = "SIX_NAMES_WINS_NOWHERE"
        elif len(wins) == len(readable):
            want_v = "SIX_NAMES_SURVIVES_EVERY_CLOCK"
        else:
            want_v = "SIX_NAMES_IS_A_CLOCK_ARTIFACT"
        if want_v != j.get("verdict"):
            problems.append("verdict %s != re-derived %s" % (j.get("verdict"), want_v))

    # 3. the three clocks are distinct and the pair is exactly 5/6
    rebals = sorted({c.get("rebal") for c in cells})
    if len(rebals) < 2:
        problems.append("only %d clock(s) measured: a survival test needs more than one" % len(rebals))
    for c in cells:
        if c.get("n") not in PAIR:
            problems.append("cell width %s is outside the pair" % c.get("n"))
        if c.get("cagr") is None:
            problems.append("cell n=%s rebal=%s has no cagr" % (c.get("n"), c.get("rebal")))
    return problems


def run():
    payload = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    for c in payload["cells"]:
        print("  rebal=%-3s n=%d cagr=%-8s sharpe=%-6s maxdd=%-8s"
              % (c.get("rebal"), c.get("n"), c.get("cagr"), c.get("sharpe"), c.get("maxdd")))
    print("judgement", payload["judgement"].get("verdict"))
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
    print("CHECK_OK %s across clocks %s"
          % (payload["judgement"].get("verdict"),
             "/".join(str(c["rebal"]) for c in payload["judgement"]["clocks"]
                      if c.get("readable"))))
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    def cell(n, rebal, cagr):
        return {"n": n, "rebal": rebal, "cagr": cagr, "sharpe": 0.9, "maxdd": -0.15,
                "turnover": 1.4, "bar": "2026-11-17"}

    j = judge([cell(5, 10, 0.10), cell(6, 10, 0.12),
               cell(5, 20, 0.155), cell(6, 20, 0.17),
               cell(5, 40, 0.08), cell(6, 40, 0.09)])
    leg("a sixth name that wins everywhere survives", j["verdict"] == "SIX_NAMES_SURVIVES_EVERY_CLOCK")
    j = judge([cell(5, 10, 0.12), cell(6, 10, 0.10),
               cell(5, 20, 0.155), cell(6, 20, 0.17),
               cell(5, 40, 0.09), cell(6, 40, 0.08)])
    leg("a sixth name that wins only at 20 days is a clock artifact",
        j["verdict"] == "SIX_NAMES_IS_A_CLOCK_ARTIFACT" and j["wins"] == [20])
    j = judge([cell(5, 10, 0.12), cell(6, 10, 0.10),
               cell(5, 20, 0.17), cell(6, 20, 0.155)])
    leg("a sixth name that wins nowhere is its own verdict",
        j["verdict"] == "SIX_NAMES_WINS_NOWHERE")
    leg("an unreadable clock does not vote",
        judge([cell(5, 20, 0.155), cell(6, 20, 0.17),
               {"n": 5, "rebal": 10, "cagr": None, "bar": "b"},
               {"n": 6, "rebal": 10, "cagr": None, "bar": "b"}])["verdict"]
        == "SIX_NAMES_SURVIVES_EVERY_CLOCK")

    payload = {"cells": [cell(5, 20, 0.155), cell(6, 20, 0.17),
                         cell(5, 10, 0.10), cell(6, 10, 0.12)],
               "judgement": judge([cell(5, 20, 0.155), cell(6, 20, 0.17),
                                   cell(5, 10, 0.10), cell(6, 10, 0.12)])}
    leg("check passes an honest payload", check(payload) == [])
    bad = dict(payload)
    bad["judgement"] = dict(payload["judgement"], verdict="SIX_NAMES_WINS_NOWHERE")
    leg("check catches a verdict that contradicts its clocks",
        any("verdict" in p for p in check(bad)))
    bad2 = dict(payload)
    bad2["cells"] = payload["cells"] + [cell(7, 20, 0.14)]
    leg("check catches a width outside the pair",
        any("outside the pair" in p for p in check(bad2)))
    one = {"cells": [cell(5, 20, 0.155), cell(6, 20, 0.17)],
           "judgement": judge([cell(5, 20, 0.155), cell(6, 20, 0.17)])}
    leg("one clock is not a survival test", any("survival test" in p for p in check(one)))

    ok = sum(1 for _n, o in legs if o)
    for name, o in legs:
        print("  [%s] %s" % ("PASS" if o else "FAIL", name))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
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
