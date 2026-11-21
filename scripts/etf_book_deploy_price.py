"""What the other side of the wait costs -- deploying now, priced at its own worst case.

r1891/r1892 answered one half of the question: waiting 13.6 years for a 5pp ruler would
forgo CNY 1,860,100 per million and could save at most CNY 781.  The reader is still left
with the second half -- "if not waiting, then what am I actually buying, and what does it
cost when I am wrong?"  This face prices that alternative, using only numbers the book has
already published (results/etf_book_seat_mde.json's 5-seat row, carried in
results/etf_book_target_price.json's rule block):

  now          the select leg as measured: 7.6858pp/yr on a 3.1199pp standard error
  lower95      the one-sided 95% floor of that same measurement
  worst        the book's own cost leg, -1.392pp/yr, which is what it pays if the edge is
               exactly zero -- the harshest defensible reading of "I am wrong"
  wait         the wait's own price, converted to the same per-year per-million lens

No panel read, no new backtest, no new claim.  It would rather say STALE than price an
input that moved, and it never re-decides whether the edge is real -- that question stays
on the seat-MDE face.

Modes: run (default) | --check | --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAT_FACE = "results/etf_book_seat_mde.json"
WAIT_FACE = "results/etf_book_target_price.json"
OUT = os.path.join(BASE, "results", "etf_book_deploy_price.json")
MD = os.path.join(BASE, "research", "ETF_BOOK_DEPLOY_PRICE.md")

SEATS = 5
LENS_CNY = 1_000_000.0
Z_ONE_SIDED_95 = 1.6449            # the floor is one-sided: the question is "how wrong"
HALF_EDGE = 0.5                    # selection-bias allowance: the row was the best seat
RATIO_CHEAP_WAIT = 1.0             # below this the wait buys cheaper insurance than it costs
TOL = 1e-9


def _read_json(rel):
    path = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seat_row(face, seats=SEATS):
    for r in (face or {}).get("rows") or []:
        if int(r.get("n_hold", -1)) == int(seats):
            return r
    return None


def scenario(name, net_pp, se_pp, lens=LENS_CNY):
    """One hypothesis about the book's net annual return, carried to the floor and to money.

    net_pp is the cost-after figure (7.6858 as measured, half of it, or the cost leg
    alone for "no edge").  The floor uses the measurement's own standard error, which does
    not shrink when the hypothesis does: a book with no edge still has a 3.1pp standard
    error around that zero -- that width is what a coarse ruler means.
    """
    if None in (net_pp, se_pp):
        return None
    lower_pp = float(net_pp) - Z_ONE_SIDED_95 * float(se_pp)
    return {
        "name": name,
        "net_pp": round(float(net_pp), 4),
        "annual_pp": round(float(net_pp), 4),
        "lower95_pp": round(lower_pp, 4),
        "annual_cny": round(float(net_pp) / 100.0 * float(lens), 1),
        "lower95_cny": round(lower_pp / 100.0 * float(lens), 1),
        "yearly_loss_if_floor": round(max(0.0, -lower_pp) / 100.0 * float(lens), 1),
    }


def verdict_for(ratio, lower95_positive):
    if ratio is None:
        return "NO_VERDICT"
    if ratio >= RATIO_CHEAP_WAIT:
        return "WAITING_IS_THE_EXPENSIVE_INSURANCE"
    return "WAITING_IS_THE_CHEAPER_INSURANCE"


def price(seat, wait_face, lens=LENS_CNY):
    row = seat_row(seat)
    if row is None:
        return {"verdict": {"verdict": "NO_5_SEAT_ROW"},
                "vertex": "the seat-MDE face has no 5-seat row; nothing to price"}
    rule = (seat or {}).get("rule") or {}
    select_pp = float(row["select_ann_pp"])
    se_pp = float(row["select_se_pp"])
    cost_pp = float(row["cost_ann_pp"])
    bars = int(row.get("bars") or 0)

    # the measured row already has the cost leg inside it: 7.6858 / 3.1199 == its own t
    edge_measured = select_pp - cost_pp
    scen = [scenario("as_measured", select_pp, se_pp, lens),
            scenario("half_edge", select_pp * HALF_EDGE, se_pp, lens),
            scenario("no_edge", cost_pp, se_pp, lens)]
    scen = [s for s in scen if s]

    wv = (wait_face or {}).get("verdict") or {}
    wrule = (wait_face or {}).get("rule") or {}
    wait_years = wv.get("wait_years")
    wait_total = wv.get("forgo_cny")
    wait_annual = None
    if wait_total is not None and wait_years:
        wait_annual = float(wait_total) / float(wait_years)

    measured = scen[0] if scen else None
    # Two prices, deliberately not added together:
    #   zero_edge  what the book actually pays per year if the edge is exactly zero -- the
    #              cost leg, a realised loss, the harshest defensible reading of "I am wrong"
    #   tail       the 95% floor of that same zero-edge hypothesis -- not a loss anybody
    #              would book, but the width of what this ruler cannot tell apart
    zero_edge_loss = abs(float(cost_pp)) / 100.0 * float(lens)
    tail_loss = None
    zero_row = [s for s in scen if s["name"] == "no_edge"]
    if zero_row:
        tail_loss = zero_row[0]["yearly_loss_if_floor"]
    ratio = None
    if wait_annual is not None and zero_edge_loss > 0:
        ratio = wait_annual / zero_edge_loss
    ratio_tail = None
    if wait_annual is not None and tail_loss:
        ratio_tail = wait_annual / tail_loss

    v = {
        "verdict": verdict_for(ratio, bool(measured and measured["lower95_pp"] >= 0)),
        "select_ann_pp": round(select_pp, 4),
        "select_se_pp": round(se_pp, 4),
        "select_t": round(select_pp / se_pp, 4) if se_pp else None,
        "cost_ann_pp": round(cost_pp, 4),
        "edge_measured_pp": round(edge_measured, 4),
        "z_one_sided_95": Z_ONE_SIDED_95,
        "lower95_pp": measured["lower95_pp"] if measured else None,
        "lower95_positive": bool(measured and measured["lower95_pp"] >= 0),
        "worst_case": "no_edge",
        "zero_edge_yearly_loss_cny": round(zero_edge_loss, 1),
        "tail_yearly_loss_cny": None if tail_loss is None else round(tail_loss, 1),
        "wait_total_cny": wait_total,
        "wait_years": wait_years,
        "wait_yearly_cny": None if wait_annual is None else round(wait_annual, 1),
        "ratio_wait_over_worst": None if ratio is None else round(ratio, 4),
        "ratio_wait_over_tail": None if ratio_tail is None else round(ratio_tail, 4),
        "wait_cheaper_if_ratio_below": RATIO_CHEAP_WAIT,
    }
    sentence = None
    if measured is not None and wait_annual is not None:
        floor_word = ("仍是正的 %+.2fpp" % measured["lower95_pp"]) if measured["lower95_pp"] >= 0 \
            else ("是 %+.2fpp" % measured["lower95_pp"])
        sentence = (
            "现在就用这把尺子下单，按它自己的标准误 %.2fpp，95%% 单边下界 %s"
            "（每百万每年 %s 元）；就算这本书的 edge 恰好为零，它每年只付 %s 元成本——"
            "而「它可能没有 edge」这件事，这把尺子本身分不清的量级是每年 %s 元。"
            "等 13.6 年换更准的尺子，每年要付 %s 元等待费：是最硬的那笔年损失的 %s 倍，"
            "也仍是这把尺子分不清量级的 %s 倍。"
            % (se_pp, floor_word,
               format(int(round(measured["lower95_cny"])), ","),
               format(int(round(zero_edge_loss)), ","),
               format(int(round(tail_loss or 0.0)), ","),
               format(int(round(wait_annual)), ","),
               ("%.1f" % ratio) if ratio is not None else "?",
               ("%.1f" % ratio_tail) if ratio_tail is not None else "?"))
    return {
        "evidence_cutoff": (seat or {}).get("evidence_cutoff"),
        "panel_last_bar": (seat or {}).get("panel_last_bar"),
        "input_faces": {"seat_mde": SEAT_FACE, "wait_price": WAIT_FACE},
        "input_script": (seat or {}).get("script"),
        "rule": {
            "lens_cny": lens,
            "seats": SEATS,
            "bars": bars,
            "z_one_sided_95": Z_ONE_SIDED_95,
            "half_edge_factor": HALF_EDGE,
            "ratio_cheap_wait": RATIO_CHEAP_WAIT,
            "wait_years": wait_years,
            "wait_total_cny": wait_total,
            "wait_face_verdict": wv.get("verdict"),
            "wait_target_pp": wv.get("target_pp"),
            "wait_p_star": wv.get("p_star"),
            "select_p_direction": row.get("select_p_direction"),
            "select_status": row.get("select_status"),
            "mde80_now_pp": rule.get("target_mde80_pp"),
        },
        "scenarios": scen,
        "verdict": v,
        "sentence": sentence,
    }


def md_lines(d):
    v = d["verdict"]
    r = d["rule"]
    out = ["# 现在部署的诚实价格：等的保险费是它最坏情形的几倍（r1912）", "",
           "**结论：%s**" % v["verdict"], ""]
    if d.get("sentence"):
        out += [d["sentence"], ""]
    out.append("上游读数全部来自 `%s`（%s 那次测量，cutoff %s）：5 座选股腿 %.4fpp、"
               "自己的标准误 %.4fpp（t=%.3f）、成本腿 %.4fpp/年、样本 %s 根 bar。等待价来自 "
               "`%s`（%s）。本面不重算回测，只把「现在」与「等」摆在同一把尺子上。"
               % (d["input_faces"]["seat_mde"], d.get("input_script"), d.get("evidence_cutoff"),
                  v["select_ann_pp"], v["select_se_pp"], v["select_t"] or 0.0,
                  v["cost_ann_pp"], format(r["bars"], ","),
                  d["input_faces"]["wait_price"], r.get("wait_face_verdict")))
    out += ["", "## 1. 三种假设下，「现在下单」每年值多少", "",
            "| 假设 | 成本后年化（pp/年） | 95% 单边下界（pp） | 下界折算（元/百万/年） | 下界同时是年损失吗 |",
            "|---|---|---|---|---|"]
    for s in d["scenarios"]:
        out.append("| %s | %+.2f | %+.2f | %s | %s |" % (
            s["name"], s["net_pp"], s["lower95_pp"],
            "{:,.0f}".format(s["lower95_cny"]),
            "{:,.0f}".format(s["yearly_loss_if_floor"]) if s["yearly_loss_if_floor"] else "不亏"))
    out += ["", "下界 = 成本后年化 - 1.6449 × 标准误。标准误不随假设缩小：一本没有 edge 的书，"
            "标准误仍是那 %.2fpp——这正是「粗尺子」的全部含义。" % v["select_se_pp"], ""]
    out += ["## 2. 两个价格并排", "",
            "| 买什么 | 每年每百万付多少 | 一共付多少 |", "|---|---|---|",
            "| 等 13.6 年换 5pp 尺子 | %s | %s（%s 年） |" % (
                "{:,.0f}".format(v["wait_yearly_cny"] or 0.0),
                "{:,.0f}".format(v["wait_total_cny"] or 0.0), r.get("wait_years")),
            "| 现在就下单，且 edge 恰好为零（实际付出的成本腿） | %s | 每年重付一次，不封顶 |" % (
                "{:,.0f}".format(v["zero_edge_yearly_loss_cny"] or 0.0)),
            "| 这把尺子分不清的量级（edge=0 时的 95%% 下界，不是记账损失） | %s | 量级，不是账单 |" % (
                "{:,.0f}".format(v["tail_yearly_loss_cny"] or 0.0)),
            "", "比值：等的年费是最硬那笔年损失的 **%.1f 倍**，也仍是尺子分不清量级的 **%.1f 倍**。"
            % (v["ratio_wait_over_worst"] or 0.0, v["ratio_wait_over_tail"] or 0.0),
            "",
            "## 3. 这张面说什么、不说什么", "",
            "- 说：**不等**有价格，而且这个价格可以只用这本书自己的两个已发布数字算出来。",
            "- 说：读数本身的 95%% 单边下界%s——%s。" % (
                "是正的" if v["lower95_positive"] else "是负的",
                "等的保险买的是一个在这把尺子上看不见的尾部" if v["lower95_positive"]
                else "等的保险确实对应一个真实的尾部，但它仍然更贵"),
            "- 不说：edge 是否真实。t=%.2f、p=%.4f 留在上游面，本面只搬不改。" % (
                v["select_t"] or 0.0, r.get("select_p_direction") or 0.0),
            "- 不说：打对折这一档是唯一的选择偏差修正——它只是把「5 座里挑最好」这件事标出一个"
            "下限量级，不是估计量。",
            "- 边界：标准误是整段样本上的，不随资金规模变化；元/100 万是固定镜头，不是建议规模；"
            "成本腿只算交易成本，不含冲击与税收。",
            "",
            "（本面自带 `--check`：从上游两面重新推导每一个数；上游 cutoff 一动即判 STALE。）"]
    return out


def check():
    rec = _read_json(OUT)
    if not rec:
        print("[check] STALE: no receipt at %s (face missing)" % OUT)
        return 2
    seat = _read_json(SEAT_FACE)
    wait = _read_json(WAIT_FACE)
    if not seat or not wait:
        print("[check] STALE: upstream face missing (%s / %s)" % (SEAT_FACE, WAIT_FACE))
        return 2
    if rec.get("evidence_cutoff") != seat.get("evidence_cutoff"):
        print("[check] STALE: receipt priced cutoff %r, seat face is now %r"
              % (rec.get("evidence_cutoff"), seat.get("evidence_cutoff")))
        return 3
    redo = price(seat, wait, lens=(rec.get("rule") or {}).get("lens_cny", LENS_CNY))
    fails = []
    a, b = redo.get("verdict") or {}, rec.get("verdict") or {}
    for k in ("verdict", "select_ann_pp", "select_se_pp", "cost_ann_pp", "lower95_pp",
              "lower95_positive", "worst_case", "zero_edge_yearly_loss_cny",
              "tail_yearly_loss_cny", "wait_total_cny",
              "wait_years", "wait_yearly_cny", "ratio_wait_over_worst", "ratio_wait_over_tail"):
        x, y = b.get(k), a.get(k)
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            if abs(float(x) - float(y)) > max(TOL, abs(float(y)) * 1e-9):
                fails.append("%s: receipt=%r rederive=%r" % (k, x, y))
        elif x != y:
            fails.append("%s: receipt=%r rederive=%r" % (k, x, y))
    sa = {s["name"]: s for s in redo.get("scenarios") or []}
    sb = {s["name"]: s for s in rec.get("scenarios") or []}
    if set(sa) != set(sb):
        fails.append("scenario names: receipt=%r rederive=%r" % (sorted(sb), sorted(sa)))
    for n in sorted(set(sa) & set(sb)):
        for k in ("net_pp", "annual_pp", "lower95_pp", "annual_cny", "lower95_cny",
                  "yearly_loss_if_floor"):
            x, y = sb[n].get(k), sa[n].get(k)
            if (x is None) != (y is None) or (x is not None
                                              and abs(float(x) - float(y)) > max(TOL, abs(float(y)) * 1e-9)):
                fails.append("%s.%s: receipt=%r rederive=%r" % (n, k, x, y))
    print("[check] %d scenario(s) re-derived, %d mismatch" % (len(sb), len(fails)))
    for f in fails:
        print("  MISMATCH " + f)
    return 0 if not fails else 1


def _fixture():
    return ({"evidence_cutoff": "2026-11-13", "panel_last_bar": "2026-11-13",
             "script": "scripts/etf_book_seat_mde.py",
             "rule": {"per_year": 252.0, "block": 20, "z80": 2.802, "target_mde80_pp": 5.0},
             "rows": [{"n_hold": 5, "bars": 1662, "select_ann_pp": 7.6858,
                       "select_se_pp": 3.1199, "select_mde80_pp": 8.7419,
                       "select_p_direction": 0.0045, "cost_ann_pp": -1.392,
                       "select_status": "SIGNIFICANT_UNDERPOWERED"}]},
            {"verdict": {"verdict": "WAITING_COSTS_MORE_THAN_IT_INSURES", "target_pp": 5.0,
                         "wait_years": 13.606, "forgo_cny": 1860099.6, "p_star": 10.7122},
             "rule": {"lens_cny": 1000000.0}})


def selftest():
    fails = []

    def leg(cond, msg):
        if not cond:
            fails.append(msg)

    seat, wait = _fixture()
    d = price(seat, wait)
    v = d["verdict"]
    sc = {s["name"]: s for s in d["scenarios"]}

    # L1 the measured row's own identity: annual / se reproduces the published t
    leg(abs(v["select_t"] - 2.4635) <= 0.001, "L1 t identity, got %r" % (v["select_t"],))

    # L2 the floor is one-sided 95%, not two-sided and not the MDE
    expect = 7.6858 - 1.6449 * 3.1199
    leg(abs(sc["as_measured"]["lower95_pp"] - expect) <= 0.001,
        "L2 floor arithmetic, got %r vs %r" % (sc["as_measured"]["lower95_pp"], expect))
    leg(abs(sc["as_measured"]["lower95_pp"] - 2.5539) <= 0.001,
        "L2 must land on 2.5539pp, got %r" % (sc["as_measured"]["lower95_pp"],))

    # L3 the cost leg is inside the published select figure, not added twice
    leg(abs(v["edge_measured_pp"] - (7.6858 + 1.392)) <= 1e-9,
        "L3 edge = select - cost, got %r" % (v["edge_measured_pp"],))
    leg(abs(sc["as_measured"]["annual_pp"] - 7.6858) <= 1e-9,
        "L3 as_measured annual must return the published 7.6858, got %r" % (sc["as_measured"]["annual_pp"],))

    # L4 zero edge means the cost leg, exactly; the floor of that hypothesis is a width,
    #    not a loss, and both numbers are printed under different names
    leg(abs(sc["no_edge"]["annual_pp"] - (-1.392)) <= 1e-9, "L4 no_edge annual, got %r"
        % (sc["no_edge"]["annual_pp"],))
    leg(abs(v["zero_edge_yearly_loss_cny"] - 13920.0) <= 0.5, "L4 zero-edge loss, got %r"
        % (v["zero_edge_yearly_loss_cny"],))
    leg(abs(v["tail_yearly_loss_cny"] - 65239.2) <= 1.0, "L4 tail width, got %r"
        % (v["tail_yearly_loss_cny"],))
    leg(v["tail_yearly_loss_cny"] > v["zero_edge_yearly_loss_cny"],
        "L4 the width of the ruler must exceed the realised cost")

    # L5 half edge is the midpoint of the two, and its floor is negative (that is the point)
    leg(abs(sc["half_edge"]["net_pp"] - 0.5 * v["select_ann_pp"]) <= 1e-9, "L5 half edge")
    leg(sc["half_edge"]["lower95_pp"] < 0 < sc["as_measured"]["lower95_pp"],
        "L5 half edge must straddle zero, got %r / %r"
        % (sc["half_edge"]["lower95_pp"], sc["as_measured"]["lower95_pp"]))

    # L6 the wait is converted to the same per-year lens, and it is ~10x the realised
    #    worst case while still ~2x the width the ruler cannot resolve
    leg(abs(v["wait_yearly_cny"] - 1860099.6 / 13.606) <= 0.2, "L6 wait per year, got %r"
        % (v["wait_yearly_cny"],))
    leg(8.5 < v["ratio_wait_over_worst"] < 11.0, "L6 the wait must be ~9.8x the realised worst, "
        "got %r" % (v["ratio_wait_over_worst"],))
    leg(1.8 < v["ratio_wait_over_tail"] < 2.4, "L6 the wait must still be ~2.1x the ruler's own "
        "width, got %r" % (v["ratio_wait_over_tail"],))
    leg(v["ratio_wait_over_worst"] > v["ratio_wait_over_tail"],
        "L6 the realised cost is the smaller denominator -- if not, the two prices were swapped")

    # L7 verdict is a function of the ratio, in both directions
    leg(verdict_for(9.0, True) == "WAITING_IS_THE_EXPENSIVE_INSURANCE", "L7 high ratio")
    leg(verdict_for(0.5, True) == "WAITING_IS_THE_CHEAPER_INSURANCE", "L7 low ratio")
    leg(verdict_for(None, True) == "NO_VERDICT", "L7 no ratio must not read as cheap")

    # L8 the positive floor is carried as a flag, not swallowed by the verdict word
    leg(v["lower95_positive"] is True, "L8 positive floor flag, got %r" % (v["lower95_positive"],))
    short = price(seat, wait)
    short["scenarios"] = []
    leg(price({"rows": [{"n_hold": 5, "bars": 1662, "select_ann_pp": 1.0,
                         "select_se_pp": 5.0, "cost_ann_pp": -1.392}]}, wait)
        ["verdict"]["lower95_positive"] is False, "L8 negative floor must flip the flag")

    # L9 a missing 5-seat row is answered, never priced
    none_row = price({"rows": [{"n_hold": 2}]}, wait)
    leg(none_row["verdict"]["verdict"] == "NO_5_SEAT_ROW", "L9 missing row -> %r"
        % (none_row["verdict"]["verdict"],))
    leg("scenarios" not in none_row, "L9 no row must not print scenarios")

    # L10 a wait face without a forgo date cannot be turned into a per-year price
    no_wait = price(seat, {"verdict": {"verdict": "WAITING_COSTS_MORE_THAN_IT_INSURES"}})
    leg(no_wait["verdict"]["ratio_wait_over_worst"] is None
        and no_wait["verdict"]["verdict"] == "NO_VERDICT", "L10 no wait data -> %r"
        % (no_wait["verdict"],))

    # L11 the sentence carries both numbers -- the realised loss and the ruler's width --
    #     plus the break-even ratio, not just the verdict word
    leg(d["sentence"] and ("%s 元" % format(int(round(v["zero_edge_yearly_loss_cny"])), ","))
        in d["sentence"], "L11 sentence must carry the realised worst-case yuan")
    leg(d["sentence"] and ("%s 元" % format(int(round(v["tail_yearly_loss_cny"])), ","))
        in d["sentence"], "L11 sentence must carry the ruler's width")
    leg(d["sentence"] and ("%.1f 倍" % v["ratio_wait_over_worst"]) in d["sentence"],
        "L11 sentence must carry the ratio")

    # L12 provenance: two named faces, one cutoff
    leg(d["input_faces"]["seat_mde"] == SEAT_FACE and d["input_faces"]["wait_price"] == WAIT_FACE,
        "L12 provenance")
    leg(d["evidence_cutoff"] == "2026-11-13", "L12 cutoff")

    # L13 the three scenarios are ordered by net return, and the worst case is the no_edge one
    leg([s["net_pp"] for s in d["scenarios"]] == sorted([s["net_pp"] for s in d["scenarios"]],
                                                        reverse=True), "L13 order")
    leg(v["worst_case"] == "no_edge", "L13 worst case, got %r" % (v["worst_case"],))

    print("[selftest] %d/%d PASS" % (13 - len(fails), 13))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


def run():
    seat = _read_json(SEAT_FACE)
    wait = _read_json(WAIT_FACE)
    if not seat:
        raise SystemExit("[run] missing %s" % SEAT_FACE)
    if not wait:
        raise SystemExit("[run] missing %s" % WAIT_FACE)
    d = price(seat, wait)
    d["script"] = "scripts/etf_book_deploy_price.py"
    return d


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    argv = ["check" if a == "--check" else "selftest" if a == "--selftest" else a for a in argv]
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    t0 = time.time()
    d = run()
    d["elapsed_sec"] = round(time.time() - t0, 1)
    d["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)) + "\n")
    print(json.dumps({k: d["verdict"].get(k) for k in
                      ("verdict", "lower95_pp", "lower95_positive", "worst_case",
                       "zero_edge_yearly_loss_cny", "tail_yearly_loss_cny",
                       "wait_yearly_cny", "ratio_wait_over_worst", "ratio_wait_over_tail")},
                     ensure_ascii=False, indent=1))
    return 0 if d["verdict"].get("verdict") not in ("NO_5_SEAT_ROW",) else 1


if __name__ == "__main__":
    sys.exit(main())
