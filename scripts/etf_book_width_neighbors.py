"""Is the sixth name a real edge, or an artifact of the 20-day rebalance it was measured on?

`etf_book_width_return` found width 6 earning 17.00% against width 5's 15.50% at the published
cell (20-day rebalance, 10bp), and printed that 7 and 8 names were worse -- so the win is a
local optimum, not a monotone trend. That leaves the question every local optimum has to
answer before anyone trades it: does it survive a change to the one parameter that shaped it?

The cheap, decisive test: hold everything else and move the rebalance clock. 20 days is a
month; 10 is a fortnight; 40 is two months. A sixth name that beats the fifth at all three is
a width effect. One that only wins at 20 is the calendar talking.

Only widths 5 and 6 are run here on purpose: the question is a pairwise survival test, not a
walk down the ladder.

All three clocks are measured here, including the 20-day one. The earlier version read that
pair out of `etf_book_width_return.json` to save compute, which made "three clocks" three
readings of two measured cells and one quoted cell -- and a survival verdict that rests on a
quoted cell is a verdict about the quotation. So the 20-day pair is now re-derived on this
face's own code path and the published pair is kept as the thing to reproduce: if the two
disagree the clocks are not readings of the same cell, and the verdict says so instead of
averaging them.
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
CLOCKS = (10, 20, 40)
PAIR = (5, 6)
IS_END = "2023-12-31"
# The same engine, panel and score on the same bar is a deterministic computation, so the
# reproduction is exact; a tolerance here would be hiding a real disagreement behind rounding.
REPRO_TOL = 1e-9


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
    m["source"] = "measured"
    m["turnover"] = round(turn, 2)
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = R.stats(sl, m["label"] + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    return m


def read_twenty():
    """The 20-day pair as published -- the thing this face has to reproduce, not quote."""
    if not os.path.exists(WR_FACE):
        return None, "width_return face absent (run scripts/etf_book_width_return.py first)"
    with io.open(WR_FACE, encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = {r.get("n"): r for r in (doc.get("rows") or [])}
    five, six = rows.get(5), rows.get(6)
    if not five or not six:
        return None, "width_return face has no width 5/6 pair"

    def _pick(r):
        return {"n": r.get("n"), "rebal": 20, "cagr": r.get("cagr"),
                "sharpe": r.get("sharpe"), "maxdd": r.get("maxdd"),
                "turnover": r.get("turnover"), "bar": r.get("bar")}

    return {5: _pick(five), 6: _pick(six)}, None


def reproduce(measured, upstream, tol=REPRO_TOL):
    """Does this face's 20-day pair land on the pair the published face printed?

    Three clocks only add up to one answer if the cell they share is the same cell. Reading
    the 20-day number from upstream makes that true by construction and therefore untested --
    the clocks then differ only by a quotation. Re-deriving it here turns "we agree" into a
    number, and a disagreement into a verdict rather than an average.
    """
    if not upstream:
        return {"readable": False, "why": "no published 5/6 pair to reproduce"}
    by_n = {c["n"]: c for c in measured
            if c.get("rebal") == 20 and c.get("source") == "measured"}
    rows, worst = {}, 0.0
    for n in PAIR:
        up, mine = upstream.get(n) or {}, by_n.get(n) or {}
        a, b = up.get("cagr"), mine.get("cagr")
        if a is None or b is None:
            return {"readable": False,
                    "why": "width %s has no cagr on one side (published=%s, measured=%s)"
                           % (n, a, b)}
        d = abs(float(a) - float(b))
        worst = max(worst, d)
        rows[str(n)] = {"upstream_cagr": a, "measured_cagr": b, "abs_diff": d}
    return {"readable": True, "tol": tol, "max_abs_diff": worst,
            "ok": bool(worst <= tol), "rows": rows}


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
    if len(readable) < 2:
        # one clock cannot survive anything: a survival test whose second clock failed to
        # measure reads exactly like a green one, so it gets its own verdict.
        return {"verdict": "ONE_CLOCK_IS_NOT_A_SURVIVAL_TEST", "clocks": clocks,
                "n_readable": len(readable)}
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
    repro = payload.get("reproduction") or {}
    if repro.get("readable") and repro.get("ok"):
        head += "（20 日那格本面重跑，与已发布面逐位一致，最大差 %.1e）" % repro["max_abs_diff"]
    elif repro.get("readable"):
        head += ("（20 日那格本面重跑对不上已发布面，最大差 %.1e —— 三个周期不是同一格的"
                 "三个读数）" % repro["max_abs_diff"])
    else:
        head += "（20 日那格这次没能本面复算：%s）" % (repro.get("why") or "无读数")
    if v == "ONE_CLOCK_IS_NOT_A_SURVIVAL_TEST":
        return head + ("只有 %s 个周期的读数可用 —— **一个钟不能「扛过」任何东西**；"
                       "先把另外两个周期的读数补齐。" % (j.get("n_readable") or 0))
    if v == "CLOCKS_DISAGREE_ON_THE_SAME_CELL":
        return head + ("**这一页不印「第 6 名稳不稳」**：三个周期的共同那格没有复现，"
                       "先把两张面拉到同一格再来问。")
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
    upstream, why = read_twenty()
    cells = []
    close = openp = amt = score = None
    try:
        close, openp, amt, score = panel()
    except Exception as exc:                                  # noqa: BLE001
        why = "panel unavailable: %s" % str(exc)[:80]
    if close is not None:
        for rebal in CLOCKS:
            for n in PAIR:
                cells.append(run_cell(close, openp, amt, score, rebal, n))
    elif upstream:
        for n in PAIR:
            cells.append(dict(upstream[n], source="upstream"))
        why = why or ("panel unavailable: the 20-day pair is the upstream face's reading, "
                      "not this face's")
    repro = reproduce(cells, upstream)
    j = judge(cells)
    if repro.get("readable") and not repro.get("ok"):
        # two clocks that disagree about their shared cell are not three clocks: the verdict
        # about clocks cannot stand on cells that stopped being the same cell.
        j = dict(j, verdict="CLOCKS_DISAGREE_ON_THE_SAME_CELL", reproduced=False,
                 note="the 20-day pair does not reproduce the published face "
                      "(max |diff| %.3e > %.0e), so the clocks are not three readings of one cell"
                      % (repro.get("max_abs_diff") or 0.0, repro.get("tol") or 0.0))
    payload = {
        "kind": "etf_book_width_neighbors",
        "script": "scripts/etf_book_width_neighbors.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": (next((c.get("bar") for c in cells if c.get("bar")), None)),
        "upstream": "results/etf_book_width_return.json",
        "params": {"cost": COST, "clocks": list(CLOCKS), "pair": list(PAIR)},
        "cells": cells,
        "reproduction": repro,
        "judgement": j,
        "why": why,
        "caveats": [
            "Only widths 5 and 6 are run: the question is whether that pair survives the "
            "rebalance clock, not a walk down the ladder.",
            "The 20-day pair is re-derived here and checked against the published pair "
            "(%s). A failed reproduction turns the verdict into a disagreement rather than "
            "an average of two different cells."
            % ("reproduced" if repro.get("ok") else
               ("not readable" if not repro.get("readable") else "NOT reproduced")),
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
        if len(readable) < 2:
            want_v = "ONE_CLOCK_IS_NOT_A_SURVIVAL_TEST"
        elif not wins:
            want_v = "SIX_NAMES_WINS_NOWHERE"
        elif len(wins) == len(readable):
            want_v = "SIX_NAMES_SURVIVES_EVERY_CLOCK"
        else:
            want_v = "SIX_NAMES_IS_A_CLOCK_ARTIFACT"
        if want_v != j.get("verdict") and j.get("verdict") != "CLOCKS_DISAGREE_ON_THE_SAME_CELL":
            problems.append("verdict %s != re-derived %s" % (j.get("verdict"), want_v))

    # 2b. the disagreement verdict is only allowed when the shared cell actually failed to
    #     reproduce -- otherwise it is a verdict that blames a cell which just reproduced.
    repro = payload.get("reproduction") or {}
    if j.get("verdict") == "CLOCKS_DISAGREE_ON_THE_SAME_CELL":
        if not repro.get("readable"):
            problems.append("verdict blames the shared cell while reproduction is unreadable")
        elif repro.get("ok"):
            problems.append("verdict blames the shared cell, but it reproduced it")
    if repro.get("readable") and not repro.get("ok") \
            and j.get("verdict") != "CLOCKS_DISAGREE_ON_THE_SAME_CELL":
        problems.append("reproduction failed but the clock verdict was left standing")

    # 2c. every reproduction row must re-derive from the cells printed beside it
    if repro.get("readable"):
        meas = {c["n"]: c for c in cells
                if c.get("rebal") == 20 and c.get("source") == "measured"}
        worst = 0.0
        for k, row in (repro.get("rows") or {}).items():
            m = meas.get(int(k))
            if not m or m.get("cagr") is None:
                problems.append("reproduction row n=%s has no measured 20-day cell" % k)
                continue
            d = abs(float(row["upstream_cagr"]) - float(m["cagr"]))
            worst = max(worst, d)
            if abs(d - float(row["abs_diff"])) > 1e-12:
                problems.append("reproduction diff for n=%s does not re-derive" % k)
        if abs(worst - float(repro.get("max_abs_diff") or 0.0)) > 1e-12:
            problems.append("max_abs_diff %.3e != %.3e re-derived from the rows"
                            % (repro.get("max_abs_diff") or 0.0, worst))

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
        judge([cell(5, 10, 0.10), cell(6, 10, 0.12),
               cell(5, 20, 0.155), cell(6, 20, 0.17),
               {"n": 5, "rebal": 40, "cagr": None, "bar": "b"},
               {"n": 6, "rebal": 40, "cagr": None, "bar": "b"}])["verdict"]
        == "SIX_NAMES_SURVIVES_EVERY_CLOCK")
    leg("a single readable clock is not a survival test",
        judge([cell(5, 20, 0.155), cell(6, 20, 0.17)])["verdict"]
        == "ONE_CLOCK_IS_NOT_A_SURVIVAL_TEST")

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

    # r1321: three clocks are one cell measured three times only if the cell they share lands
    # where the published face says it landed.
    up = {5: {"n": 5, "rebal": 20, "cagr": 0.155}, 6: {"n": 6, "rebal": 20, "cagr": 0.17}}
    meas = [{"n": 5, "rebal": 20, "cagr": 0.155, "sharpe": 0.99, "maxdd": -0.16,
             "turnover": 1.53, "bar": "2026-11-17", "source": "measured"},
            {"n": 6, "rebal": 20, "cagr": 0.17, "sharpe": 1.08, "maxdd": -0.16,
             "turnover": 1.46, "bar": "2026-11-17", "source": "measured"},
            {"n": 5, "rebal": 10, "cagr": 0.1943, "sharpe": 1.14, "maxdd": -0.15,
             "turnover": 1.33, "bar": "2026-11-17", "source": "measured"},
            {"n": 6, "rebal": 10, "cagr": 0.2018, "sharpe": 1.18, "maxdd": -0.15,
             "turnover": 1.28, "bar": "2026-11-17", "source": "measured"}]
    r = reproduce(meas, up)
    leg("the shared 20-day cell reproduces the published pair", r["readable"] and r["ok"])
    r2 = reproduce([{"n": 5, "rebal": 20, "cagr": 0.1501, "source": "measured"},
                    {"n": 6, "rebal": 20, "cagr": 0.17, "source": "measured"}], up)
    leg("a shared cell that does not reproduce is caught", r2["readable"] and not r2["ok"])
    leg("an absent published pair is unreadable, never a pass", not reproduce(meas, None)["readable"])
    leg("an upstream-quoted cell cannot reproduce itself",
        not reproduce([{"n": 5, "rebal": 20, "cagr": 0.155, "source": "upstream"},
                       {"n": 6, "rebal": 20, "cagr": 0.17, "source": "upstream"}], up)["readable"])
    repro_payload = {"cells": meas, "judgement": judge(meas), "reproduction": r}
    leg("check passes a payload whose shared cell reproduced", check(repro_payload) == [])
    leg("check catches a verdict that blames a cell which just reproduced",
        any("reproduced it" in p for p in check(dict(
            repro_payload,
            judgement=dict(repro_payload["judgement"],
                           verdict="CLOCKS_DISAGREE_ON_THE_SAME_CELL")))))
    leg("check catches a failed reproduction left standing as a survival verdict",
        any("left standing" in p for p in check(dict(repro_payload, reproduction=r2))))
    leg("check catches a reproduction row that does not re-derive",
        any("re-derive" in p for p in check(dict(
            repro_payload,
            reproduction=dict(r, max_abs_diff=0.5,
                              rows=dict(r["rows"], **{"5": dict(r["rows"]["5"],
                                                                abs_diff=0.5)}))))))

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
