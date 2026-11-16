"""What does it cost to raise the liquidity cut to the rung where the pool alarm rings? (r1759)

The seat-alarm face (r1757) ended with a sentence nobody had earned: "抬闸的收益代价：本面只数
名数，不重算收益；已发布的六档扫描里 200M 档的年化是 5.42%（20M 是 8.41%），更高档只会更差".
That "只会更差" is an inference across rungs that were never priced, and it is printed next to
the one number a reader would act on: the rung where the alarm first rings (1000M, thinnest day
3 names against 5 seats).

This face prices that rung and every rung between it and the shipped 20M, through the same
engine and the same panel as the entry-gate sweep, on two seat counts:

  ARM CARD  n_hold = the production card's (12) -- the arm that must reproduce the published
            8.41% declared cell, otherwise this face is not about this book.
  ARM BOOK  n_hold = the seat count the ticket prints (5, read from etf_book_idle_cash.json) --
            the arm whose seats the alarm compares names against.

For each gate it records money (cagr/sharpe/maxdd/oos) plus the width facts that make the seat
question answerable: median/thinnest eligible names and `bars_below_seats` -- how many decision
days the gate leaves fewer names than the book has seats (on those days the book cannot be filled
at that cut, so the arm is holding cash for a reason that is not the volatility target).

Nothing here decides that the cut should move. It answers one question with a number: if the cut
is raised until the alarm can ring, how much a year does that cost -- or is it free.

Usage:
  python scripts/etf_book_gate_raise_price.py run
  python scripts/etf_book_gate_raise_price.py --selftest
  python scripts/etf_book_gate_raise_price.py --check
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import etf_composite_pf as E            # noqa: E402
import etf_book_production as P         # noqa: E402
import etf_book_entry_gate as G         # noqa: E402  (one universe builder, one width expression)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_GATE_RAISE_PRICE.md")
FACE_REACH = os.path.join(ROOT, "results", "etf_book_seat_alarm_reach.json")
FACE_IDLE_CASH = os.path.join(ROOT, "results", "etf_book_idle_cash.json")
CARD_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

SHIPPED = G.SHIPPED                                   # 20M -- the cut the ticket prints
LADDER = [20e6, 40e6, 100e6, 200e6, 400e6, 1000e6]    # shipped rung, then the rungs above it
CONTROL_TOL_PP = 0.25     # the card arm must reproduce the published declared cell
UNIVERSE_TOL = 20         # names; beyond this the panel is not the card's panel
FREE_TOL_PP = 0.25        # a raise within this band is "free" as far as this window can tell


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_inputs():
    """Every number this face borrows, read from the face that owns it (never typed in)."""
    card = _load(CARD_JSON)
    cfg = card.get("config") or {}
    declared = (card.get("execution_basis") or {}).get("declared_cagr")
    card_seats = int(cfg.get("n_hold") or 0) or None
    reach = _load(FACE_REACH)
    ladder = reach.get("ladder") or []
    book = (_load(FACE_IDLE_CASH).get("book") or {})
    book_seats = int(book.get("n_hold") or 0) or None
    reachable = None
    for row in ladder:
        thin = row.get("thin")
        if thin is not None and book_seats is not None and thin < book_seats:
            reachable = row
            break
    return {"card": card, "cfg": cfg, "declared_cagr": declared,
            "card_seats": card_seats, "book_seats": book_seats,
            "reach_ladder": ladder, "reachable": reachable}


def bars_below_seats(series, seats):
    """Decision days on which the gate leaves fewer names than the book has seats."""
    if series is None or series.empty or not seats:
        return None
    return int((series < int(seats)).sum())


def price(close, openp, amt, feats, gate, seats, cfg):
    """One gate, one seat count, through the production engine."""
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")
    score = E.build_score(close, amt, feats, min_amt=gate)
    bt, _ = P.backtest(close, openp, amt, score.shift(1), int(seats), rebal,
                       cost=cost, vol_target=vol_target)
    full = bt.get("full") or {}
    series = G.eligible_series(close, amt, gate)
    return {"cagr": full.get("cagr"), "sharpe": full.get("sharpe"),
            "maxdd": full.get("maxdd"), "vol": full.get("vol"),
            "oos_cagr": (bt.get("oos") or {}).get("cagr"),
            "turnover_per_decision": bt.get("turnover_per_decision"),
            "bars": int(len(series)) if series is not None else None,
            "median": (None if series is None or series.empty
                       else int(np.median(series.values))),
            "thin": (None if series is None or series.empty else int(series.min())),
            "bars_below_seats": bars_below_seats(series, seats)}


def classify(rows, shipped=SHIPPED, declared_cagr=None, control_delta_pp=None,
             universe_delta=None, reachable_gate=None, control_tol_pp=CONTROL_TOL_PP,
             universe_tol=UNIVERSE_TOL, free_tol_pp=FREE_TOL_PP):
    """One of six states. Frozen argument order; no retuning after the run."""
    if control_delta_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "没有控制臂：这组读数不是关于这本书的陈述"}
    if abs(control_delta_pp) > control_tol_pp:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": ("卡臂在 %gM 档偏离已发布可交易臂 %.2fpp（容差 %.2fpp），"
                             "这张面板不是卡片的面板" % (shipped / 1e6, control_delta_pp,
                                                          control_tol_pp))}
    if universe_delta is not None and abs(universe_delta) > universe_tol:
        return {"verdict": "CANNOT_JUDGE_UNIVERSE",
                "sentence": "重建宇宙与卡片差 %+d 名，超出 %d 名容差" % (universe_delta,
                                                                     universe_tol)}
    if reachable_gate is None:
        return {"verdict": "ALARM_STILL_UNREACHABLE",
                "sentence": ("在这条梯子上最薄的一天也没有跌破座位线，所以没有「会响的那一档」"
                             "可以定价——不是这次不为它定价，是它不存在")}
    ok = [r for r in rows if r.get("cagr") is not None and not r.get("error")]
    base = next((r for r in ok if abs(float(r["min_amt_cny"]) - shipped) < 1.0), None)
    target = next((r for r in ok if abs(float(r["min_amt_cny"]) - reachable_gate) < 1.0), None)
    if base is None:
        return {"verdict": "CANNOT_JUDGE_NO_SHIPPED_ARM",
                "sentence": "%gM 这一档没有定价，无法算差额" % (shipped / 1e6)}
    if target is None:
        return {"verdict": "RAISE_UNPRICEABLE",
                "sentence": ("会响的那一档（%gM）在这张面板上定不出价，"
                             "所以抬闸的代价不等于零" % (reachable_gate / 1e6))}
    cost_pp = (float(target["cagr"]) - float(base["cagr"])) * 100.0
    # float noise must not move a band edge: 8.16 - 8.41 prints -25.000000000000004
    cost_pp = round(cost_pp, 6)
    detail = {"reachable_gate_cny": reachable_gate,
              "shipped_cagr": float(base["cagr"]),
              "reachable_cagr": float(target["cagr"]),
              "cost_pp": round(cost_pp, 3),
              "reachable_bars_below_seats": target.get("bars_below_seats")}
    if cost_pp < -free_tol_pp:
        return dict(verdict="RAISE_COSTS_MONEY", **detail,
                    sentence=("把闸抬到会响的那一档（%gM）一年少赚 %.2fpp"
                              "（%.2f%% → %.2f%%）——告警在这一档不可达不是缺陷，"
                              "是这本书买到的容量" % (reachable_gate / 1e6, -cost_pp,
                                                       float(base["cagr"]) * 100,
                                                       float(target["cagr"]) * 100)))
    if cost_pp > free_tol_pp:
        return dict(verdict="RAISE_EARNS_MORE", **detail,
                    sentence=("把闸抬到会响的那一档（%gM）反而一年多赚 %.2fpp——"
                              "所以「不可达」不能用收益代价来正当化，它只是一个未被检验的假设"
                              % (reachable_gate / 1e6, cost_pp)))
    return dict(verdict="RAISE_IS_FREE_IN_WINDOW", **detail,
                sentence=("把闸抬到会响的那一档（%gM）在这个窗口里只差 %+.2fpp（容差 %.2fpp）——"
                          "这条窗口分不出代价，不能拿「会少赚」当理由"
                          % (reachable_gate / 1e6, cost_pp, free_tol_pp)))


def run():
    t0 = time.time()
    src = read_inputs()
    cfg = src["cfg"]
    card_seats = src["card_seats"] or 12
    book_seats = src["book_seats"]
    close, openp, amt, feats, n_flip = G.build_universe()
    t_panel = time.time() - t0
    universe_measured = int(len(close.columns))
    published_universe = cfg.get("universe_size")
    universe_delta = (None if published_universe is None
                      else universe_measured - int(published_universe))
    reachable = src["reachable"]
    reachable_gate = float(reachable["gate_cny"]) if reachable else None

    rows = []
    for gate in LADDER:
        row = {"min_amt_cny": gate, "min_amt_m": round(gate / 1e6, 1)}
        for arm, seats in (("card", card_seats), ("book", book_seats)):
            try:
                row[arm] = price(close, openp, amt, feats, gate, seats, cfg)
            except Exception as exc:   # an unpriceable arm is a reading, never filled in
                row[arm] = {"error": "%s: %s" % (type(exc).__name__, exc)}
            if row[arm].get("cagr") is not None:
                row[arm]["cagr"] = float(row[arm]["cagr"])
        rows.append(row)
        print("[gate %gM] card cagr=%s book cagr=%s (%.1fs)"
              % (gate / 1e6, row["card"].get("cagr"), row["book"].get("cagr"),
                 time.time() - t0), flush=True)

    flat = []
    for r in rows:
        arm = r["card"]
        merged = {"min_amt_cny": r["min_amt_cny"], "min_amt_m": r["min_amt_m"]}
        merged.update({k: v for k, v in arm.items() if k != "error"})
        if arm.get("error"):
            merged["error"] = arm["error"]
        flat.append(merged)

    base = next((r for r in flat if abs(float(r["min_amt_cny"]) - SHIPPED) < 1.0), None)
    control_delta = None
    if src["declared_cagr"] is not None and base and base.get("cagr") is not None:
        control_delta = (float(base["cagr"]) - float(src["declared_cagr"])) * 100.0
    verdict = classify(flat, declared_cagr=src["declared_cagr"],
                       control_delta_pp=control_delta, universe_delta=universe_delta,
                       reachable_gate=reachable_gate)

    out = {"evidence_cutoff": (src["card"].get("evidence_cutoff")
                               or str(pd.Timestamp(close.index[-1]).date())),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_gate_raise_price.py",
           "rule": {"ladder_cny": LADDER, "shipped_cny": SHIPPED,
                    "control_tol_pp": CONTROL_TOL_PP, "universe_tol_names": UNIVERSE_TOL,
                    "free_tol_pp": FREE_TOL_PP,
                    "arm": "decide at close t -> fill at open t+1 (score.shift(1)), two seat counts",
                    "reachable_gate_source": "results/etf_book_seat_alarm_reach.json (first rung "
                                             "whose thinnest day is below the book's seat count)",
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"card_seats": card_seats, "book_seats": book_seats,
                      "rebal": int(cfg.get("rebal") or 20),
                      "vol_target": cfg.get("vol_target"),
                      "cost_bp_per_side": cfg.get("cost_bp_per_side"),
                      "universe_measured": universe_measured,
                      "universe_published": published_universe,
                      "universe_delta_names": universe_delta,
                      "flips_repaired": int(n_flip),
                      "panel_build_seconds": round(t_panel, 1),
                      "run_seconds": None},
           "control": {"published_declared_cagr": src["declared_cagr"],
                       "arm_cagr": (None if base is None else base.get("cagr")),
                       "delta_pp": (None if control_delta is None
                                    else round(control_delta, 4)),
                       "tol_pp": CONTROL_TOL_PP},
           "reach": {"seats_for_reach": book_seats,
                     "gate_cny": reachable_gate,
                     "gate_m": (None if reachable_gate is None else round(reachable_gate / 1e6, 1)),
                     "thin": (None if not reachable else reachable.get("thin")),
                     "thin_date": (None if not reachable else reachable.get("thin_date"))},
           "rows": rows,
           "verdict": verdict}
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"],
                      "cost_pp": verdict.get("cost_pp"),
                      "reachable_gate_m": out["reach"]["gate_m"],
                      "run_seconds": out["config"]["run_seconds"]},
                     ensure_ascii=False))
    return out


def write_md(out):
    v = out["verdict"]
    seats_card = out["config"]["card_seats"]
    seats_book = out["config"]["book_seats"]

    def pct(x):
        return "-" if x is None else "%.2f%%" % (x * 100.0)

    def pp(x):
        return "-" if x is None else "%+.2fpp" % x

    base_card = next((r["card"] for r in out["rows"]
                      if abs(float(r["min_amt_cny"]) - SHIPPED) < 1.0), {})
    base_book = next((r["book"] for r in out["rows"]
                      if abs(float(r["min_amt_cny"]) - SHIPPED) < 1.0), {})
    c0 = base_card.get("cagr")
    b0 = base_book.get("cagr")

    lines = ["# 抬闸的收益代价：把流动性门槛抬到「告警会响」的那一档，一年要付多少（r1759）", "",
             "**结论：%s**" % v["verdict"], "", v["sentence"], "",
             "同一张面板、同一套排名、同一台引擎、同一个网格，只动一个数（20 日成交额中位数门槛），"
             "每条闸按两种座位数各跑一遍：**卡臂 %d 座**（必须复现已发布的 %s 可交易臂）"
             "与**图书 %d 座**（票面告警拿来比名数的那本书）。"
             % (seats_card, pct(out["control"]["published_declared_cagr"]), seats_book), "",
             "| 闸 | 卡臂 %d 座 年化 | 相对 20M | 图书 %d 座 年化 | 相对 20M | 夏普 | 最大回撤 | 可挑名数(中位/最薄) | 装不满的决策日 |"
             % (seats_card, seats_book),
             "|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        card, book = r["card"], r["book"]
        width = "%s / %s" % (card.get("median"), card.get("thin"))
        below = card.get("bars_below_seats")
        below_s = "-" if below is None else "%d / %s" % (below, card.get("bars"))
        dcard = ("-" if (c0 is None or card.get("cagr") is None)
                 else pp((float(card["cagr"]) - float(c0)) * 100.0))
        dbook = ("-" if (b0 is None or book.get("cagr") is None)
                 else pp((float(book["cagr"]) - float(b0)) * 100.0))
        lines.append("| %sM | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["min_amt_m"], pct(card.get("cagr")), dcard,
            pct(book.get("cagr")), dbook,
            "-" if card.get("sharpe") is None else "%.2f" % card["sharpe"],
            pct(card.get("maxdd")), width, below_s))
    ctl = out["control"]
    lines += ["",
              "**控制臂**：卡臂 %gM 这一格必须复现已发布可交易臂 %s；实测 %s，偏差 %s（容差 %.2fpp）。"
              % (SHIPPED / 1e6, pct(ctl["published_declared_cagr"]), pct(ctl["arm_cagr"]),
                 pp(ctl["delta_pp"]), ctl["tol_pp"]),
              "",
              "**座位线那一档从哪来**：%s。本面不自己挑「会响的闸」，"
              "只读席位告警可达面已经算出来的第一档（%s），再给那一档定价。"
              % (out["rule"]["reachable_gate_source"],
                 "无" if out["reach"]["gate_m"] is None else "%gM（最薄 %s 只 @%s）"
                 % (out["reach"]["gate_m"], out["reach"]["thin"], out["reach"]["thin_date"])),
              "",
              "宇宙宽度：实测 %s 名 / 卡片 %s 名（差 %s）。面板末根 bar %s，证据截断 %s。"
              % (out["config"]["universe_measured"], out["config"]["universe_published"],
                 out["config"]["universe_delta_names"], out["panel_last_bar"],
                 out["evidence_cutoff"]),
              "",
              "## 这条面能回答什么、不能回答什么", "",
              "能回答：门槛往上一档，钱差多少；那一档上这本书有几个决策日连座位都填不满。",
              "",
              "不能回答：应该抬还是不该抬。本面只把「抬到会响的代价」变成数字；"
              "改门槛是另一个决定，且这张面板只有 2020 年以后的窗口（更早的面板没有 20 日成交额）。",
              ]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- selftest / check
def _rows(card_cagrs, book_cagrs=None, gates=LADDER):
    book_cagrs = book_cagrs or card_cagrs
    out = []
    for g, c, b in zip(gates, card_cagrs, book_cagrs):
        out.append({"min_amt_cny": g, "min_amt_m": round(g / 1e6, 1),
                    "card": {"cagr": c * 0.01, "sharpe": 0.9, "maxdd": -0.15,
                             "median": 100, "thin": 20, "bars": 1663,
                             "bars_below_seats": 0},
                    "book": {"cagr": b * 0.01, "sharpe": 0.9, "maxdd": -0.15,
                             "median": 100, "thin": 20, "bars": 1663,
                             "bars_below_seats": 0}})
    return out


def _flat(rows):
    out = []
    for r in rows:
        merged = {"min_amt_cny": r["min_amt_cny"], "min_amt_m": r["min_amt_m"]}
        merged.update(r["card"])
        out.append(merged)
    return out


def _check():
    out = _load(OUT_JSON)
    flat = _flat(out["rows"])
    ctl = out["control"]
    delta = ctl.get("delta_pp")
    base = next((r for r in flat if abs(float(r["min_amt_cny"]) - SHIPPED) < 1.0), None)
    if ctl.get("published_declared_cagr") is not None and base and base.get("cagr") is not None:
        delta = (float(base["cagr"]) - float(ctl["published_declared_cagr"])) * 100.0
    again = classify(flat, declared_cagr=ctl.get("published_declared_cagr"),
                     control_delta_pp=delta,
                     universe_delta=out["config"].get("universe_delta_names"),
                     reachable_gate=out["reach"].get("gate_cny"))
    ok = again["verdict"] == out["verdict"]["verdict"]
    print(json.dumps({"check": "OK" if ok else "DRIFT",
                      "published": out["verdict"]["verdict"],
                      "recomputed": again["verdict"],
                      "control_delta_pp": delta}, ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    fails = []
    legs = []

    def chk(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    good = [8.41, 8.40, 8.30, 5.42, 5.10, 3.20]   # the shape the real sweep found
    rows = _rows(good)

    # L1 a raise that costs money is named with its size
    v = classify(_flat(rows), control_delta_pp=0.0, reachable_gate=1000e6)
    chk("L1 costs money", v["verdict"] == "RAISE_COSTS_MONEY", v["verdict"])
    chk("L1 cost is the shipped-minus-rung gap", abs(v["cost_pp"] - (3.20 - 8.41)) < 1e-6,
        v.get("cost_pp"))
    chk("L1 sentence carries the number", "5.21pp" in v["sentence"], v["sentence"])

    # L2 a raise that pays is not allowed to justify itself as a cost
    v = classify(_flat(_rows([8.41, 8.4, 8.5, 8.6, 9.0, 9.9])),
                 control_delta_pp=0.0, reachable_gate=1000e6)
    chk("L2 earns more", v["verdict"] == "RAISE_EARNS_MORE", v["verdict"])

    # L3 inside the band the window cannot tell the difference
    v = classify(_flat(_rows([8.41, 8.41, 8.41, 8.41, 8.41, 8.30])),
                 control_delta_pp=0.0, reachable_gate=1000e6)
    chk("L3 free", v["verdict"] == "RAISE_IS_FREE_IN_WINDOW", v["verdict"])
    edge = _rows([8.41, 8.41, 8.41, 8.41, 8.41, 8.41 - FREE_TOL_PP])
    v_edge = classify(_flat(edge), control_delta_pp=0.0, reachable_gate=1000e6)
    chk("L3b the band is the enforced one",
        v_edge["verdict"] == "RAISE_IS_FREE_IN_WINDOW", v_edge["verdict"])

    # L4 no reachable rung is not a cost of zero
    v = classify(_flat(rows), control_delta_pp=0.0, reachable_gate=None)
    chk("L4 unreachable", v["verdict"] == "ALARM_STILL_UNREACHABLE", v["verdict"])

    # L5 control failures judge nothing
    v = classify(_flat(rows), control_delta_pp=1.2, reachable_gate=1000e6)
    chk("L5 control", v["verdict"] == "CANNOT_JUDGE_CONTROL", v["verdict"])
    v = classify(_flat(rows), control_delta_pp=None, reachable_gate=1000e6)
    chk("L5b no control", v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v["verdict"])
    v = classify(_flat(rows), control_delta_pp=0.0, universe_delta=UNIVERSE_TOL + 1,
                 reachable_gate=1000e6)
    chk("L5c universe", v["verdict"] == "CANNOT_JUDGE_UNIVERSE", v["verdict"])

    # L6 a rung the engine cannot price is not a zero-cost raise
    broken = _flat(rows)
    broken[-1] = {"min_amt_cny": 1000e6, "min_amt_m": 1000.0, "cagr": None,
                  "error": "ValueError: no decisions"}
    v = classify(broken, control_delta_pp=0.0, reachable_gate=1000e6)
    chk("L6 unpriceable", v["verdict"] == "RAISE_UNPRICEABLE", v["verdict"])
    no_base = [r for r in _flat(rows) if abs(float(r["min_amt_cny"]) - SHIPPED) > 1.0]
    v = classify(no_base, control_delta_pp=0.0, reachable_gate=1000e6)
    chk("L6b no shipped arm", v["verdict"] == "CANNOT_JUDGE_NO_SHIPPED_ARM", v["verdict"])

    # L7 "cannot fill the seats" is counted, not asserted
    series = pd.Series([30, 4, 30, 5, 6], index=pd.date_range("2020-01-02", periods=5))
    chk("L7 below seats strict", bars_below_seats(series, 5) == 1,
        str(bars_below_seats(series, 5)))
    chk("L7b equal is a fill", bars_below_seats(series, 4) == 0,
        str(bars_below_seats(series, 4)))
    chk("L7c no seats no count", bars_below_seats(series, None) is None)

    # L8 the reach gate is read from the reach face, never typed into this file
    src = read_inputs() if os.path.exists(FACE_REACH) and os.path.exists(FACE_IDLE_CASH) else None
    if src is not None:
        ladder = src["reach_ladder"]
        seats = src["book_seats"]
        want = next((r["gate_cny"] for r in ladder
                     if r.get("thin") is not None and r["thin"] < seats), None)
        got = None if src["reachable"] is None else src["reachable"]["gate_cny"]
        chk("L8 reach read from face", want == got, "%s vs %s" % (want, got))
        chk("L8b seats from the book face", seats is not None, str(seats))
    else:
        chk("L8 inputs present", False, "reach/idle_cash face missing")

    # L9 the verdict the face publishes is the verdict its own rows imply (tamper test)
    v1 = classify(_flat(rows), control_delta_pp=0.0, reachable_gate=1000e6)["verdict"]
    tampered = _flat(_rows([8.41, 8.4, 8.3, 5.42, 5.1, 12.0]))
    v2 = classify(tampered, control_delta_pp=0.0, reachable_gate=1000e6)["verdict"]
    chk("L9 tamper moves the verdict", v1 != v2, "%s -> %s" % (v1, v2))

    # L10 the two seat arms are priced separately (a card reading cannot stand in for the book)
    two = _rows([8.41, 8.4, 8.3, 5.42, 5.1, 3.2], [7.0, 7.0, 7.0, 7.0, 7.0, 7.0])
    chk("L10 arms are separate", two[0]["card"]["cagr"] != two[0]["book"]["cagr"],
        str(two[0]))

    if fails:
        print("SELFTEST FAIL (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST OK (%d legs)" % len(legs))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        # re-render the page from the published payload (a formatting fix must not need a re-run)
        with open(OUT_JSON, encoding="utf-8") as fh:
            write_md(json.load(fh))
        print("md -> %s" % OUT_MD)
        return 0
    if "run" in argv:
        run()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
