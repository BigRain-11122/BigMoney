"""Where should idle cash sit, asked from seven different lookbacks (r1971 bm-c).

The desk already prices three cash vehicles once, on one window:
`etf_book_cash_vehicle` (GC001 roll vs 511880 buy-and-hold, 2020-07..panel tail)
and `bench_repo_ladder` (eleven repo tenors, daily roll vs weekly/monthly locks).
One window answers "who won over this decade", not "who wins if I start today".

This face asks the same question on a frozen ladder of lookbacks (21 / 63 / 126 /
252 / 504 / 1008 bars, full) and adds the second venue: the same overnight repo on
the Shenzhen exchange (R-001) next to the Shanghai one (GC001). A treasurer with a
Shenzhen-only account cannot buy GC001 at all; the two quotes are not the same
number, and nothing on this desk compared them window by window.

Vehicles (all on one principal, one entry and one exit at the rung's ends):
  gc001_daily_roll   one overnight contract per bar, SSE, 0.1bp/order
  r001_daily_roll    same mechanic, SZSE, 0.1bp/order
  money_etf_511880   buy and hold the price-accumulating money ETF, 0.02%/side, min 5 CNY

What it prints: per rung, each vehicle's net annualised return, the CNY-per-year bill
on 1,000,000 and on the ticket's own cash, the winner, and where the winner changes.
Nothing here changes the book, the ladder, or the ticket: this is a priced question.
"""

import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402

import etf_book_cash_ladder as CL  # noqa: E402
import etf_book_cash_vehicle as CV  # noqa: E402

OUT = os.path.join(ROOT, "results", "bench_cash_vehicle_window.json")
PAGE = os.path.join(ROOT, "research", "BENCH-CASH-VEHICLE-WINDOW.md")

REPO_FILES = {"GC001": os.path.join(ROOT, "data", "repo_daily", "GC001.csv"),
              "R-001": os.path.join(ROOT, "data", "repo_daily", "R-001.csv")}
ETF_FILES = {"511880": os.path.join(ROOT, "data", "daily", "sh511880.csv")}

RUNGS = (21, 63, 126, 252, 504, 1008)   # frozen; "full" is appended by build()
PRINCIPAL_CNY = 1_000_000.0
ETF_COMMISSION_PCT_SIDE = CV.ETF_COMMISSION_PCT_SIDE   # 0.02% per side
ETF_COMMISSION_MIN_CNY = CV.ETF_COMMISSION_MIN_CNY     # 5 CNY
REPRO_TOL_BP = 0.5          # repo arms must reproduce the ladder's published GC001 net
CELL_TOL_PP = 0.01          # stored precision is 4dp; anything coarser is a different number


# ---------------------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inputs_digest() -> dict:
    out = {}
    for name, p in list(REPO_FILES.items()) + list(ETF_FILES.items()):
        out[os.path.basename(p)] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    return out


def _dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, path)


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------------------
# pure helpers (selftest exercises these without touching the panels)
# ---------------------------------------------------------------------------------------
def rung_bars(all_bars: pd.DatetimeIndex, n):
    """The last `n` bars of `all_bars`; None means the whole window."""
    if n is None or n >= len(all_bars):
        return pd.DatetimeIndex(all_bars)
    return pd.DatetimeIndex(all_bars[len(all_bars) - int(n):])


def round_trip_commission(principal_cny: float) -> float:
    return 2.0 * max(ETF_COMMISSION_MIN_CNY, principal_cny * ETF_COMMISSION_PCT_SIDE / 100.0)


def commission_drag_pp(principal_cny: float, days: float) -> float:
    """One entry + one exit, spread over the rung's own calendar length."""
    years = max(days / 365.25, 1e-9)
    return round_trip_commission(principal_cny) / max(principal_cny, 1.0) * 100.0 / years


def cny_per_year(principal_cny: float, pct: float) -> float:
    return round(principal_cny * pct / 100.0, 0)


def winner_of(cell: dict) -> str:
    cands = [("gc001_daily_roll", cell["gc001_net_pct"]),
             ("r001_daily_roll", cell["r001_net_pct"]),
             ("money_etf_511880", cell["money_etf_net_pct"])]
    return max(cands, key=lambda kv: kv[1])[0]


def winners_sequence(cells: list) -> list:
    return [c["winner"] for c in cells]


def first_switch(cells: list):
    """(from_lookback, to_lookback, from_winner, to_winner) of the first change, or None."""
    w = winners_sequence(cells)
    for i in range(1, len(w)):
        if w[i] != w[i - 1]:
            return (cells[i - 1]["lookback"], cells[i]["lookback"], w[i - 1], w[i])
    return None


def headline_of(cells: list) -> str:
    if not cells:
        return "NO_CELLS"
    seq = winners_sequence(cells)
    if len(set(seq)) == 1:
        return "ONE_VEHICLE_WINS_EVERY_LOOKBACK"
    return "LOOKBACK_DECIDES_THE_VEHICLE"


def today_reading(cells: list) -> dict:
    """The 1-year and 2-year rungs only: the horizons whose cash rate is today's rate."""
    out = {}
    for lb in (252, 504):
        c = next((x for x in cells if x["lookback"] == lb), None)
        if c is not None:
            out[str(lb)] = {"winner": c["winner"], "start": c["start"], "end": c["end"],
                            "gc001_net_pct": c["gc001_net_pct"],
                            "r001_net_pct": c["r001_net_pct"],
                            "money_etf_net_pct": c["money_etf_net_pct"]}
    ws = {v["winner"] for v in out.values()}
    if not ws:
        return {"verdict": "NO_TODAY_RUNG", "rungs": out}
    if len(ws) == 1:
        return {"verdict": "TODAY_READING_ONE_WINNER", "winner": ws.pop(), "rungs": out}
    return {"verdict": "TODAY_READING_SPLIT", "rungs": out}


def reading_of(cells: list, ticket_cash: float, orders_per_year: float) -> dict:
    """The money reading, derived from the cells -- never typed.

    Three numbers a treasurer can act on: what each rung's gap is worth in CNY/year on
    the cash the ticket actually carries, what one repo order buys at that rung's rate,
    and whether today's rung is a tie before friction.
    """
    by = {str(c["lookback"]): c for c in cells}
    gap = {str(lb): round((by[lb]["gc001_net_pct"] - by[lb]["money_etf_net_pct"]) / 100.0 * ticket_cash, 0)
           for lb in by}
    r001 = {str(lb): round((by[lb]["gc001_net_pct"] - by[lb]["r001_net_pct"]) / 100.0 * ticket_cash, 0)
            for lb in by}
    per_order = {str(lb): round(gap[lb] / max(orders_per_year, 1e-9), 2) for lb in gap}
    tie = None
    if "21" in by:
        tie = abs(by["21"]["gc001_net_pct"] - by["21"]["money_etf_gross_pct"]) <= 0.01
    return {"orders_per_year": round(orders_per_year, 2),
            "gap_gc001_minus_etf_cny_per_year": gap,
            "r001_penalty_cny_per_year": r001,
            "cny_per_repo_order": per_order,
            "today_short_rung_is_a_tie_before_friction": tie}


# ---------------------------------------------------------------------------------------
# the arithmetic
# ---------------------------------------------------------------------------------------
def build(write=True, verbose=True) -> int:
    t0 = time.time()
    rates = CL.load_panel()
    etf = CV.load_etf("511880")
    etf_ret_full, jumps = CV.consolidation_returns(etf)

    common_start = max(etf.index[0], pd.Timestamp("2013-04-18"))
    bars = pd.DatetimeIndex(sorted({b for s in rates.values() for b in s.index
                                    if b >= common_start}))
    if len(bars) < 1500:
        print("[cash_vehicle_window] FAIL too few common bars (%d)" % len(bars))
        return 1

    # control: the imported repo engine must reproduce the published GC001 net
    pub_pct, pub_cut = None, None
    ladder_out = os.path.join(ROOT, "results", "etf_book_cash_ladder.json")
    if os.path.exists(ladder_out):
        pj = _load(ladder_out)
        pub_pct = (pj.get("models", {}).get("gc001", {}) or {}).get("net_ann_pct")
        pub_cut = pj.get("evidence_cutoff")
    gap_bp = None
    if pub_pct is not None and pub_cut:
        ctrl_bars = pd.DatetimeIndex([b for b in bars
                                      if b >= max(common_start, pd.Timestamp(CL.WINDOW_START))
                                      and b <= pd.Timestamp(pub_cut)])
        if len(ctrl_bars) > 250:
            r_ctrl, _ = CL.roll_rung(ctrl_bars, rates, None, fees=None, name="GC001")
            gap_bp = abs(CL.cagr_pct(r_ctrl, ctrl_bars) - float(pub_pct)) * 100.0
    if gap_bp is None or gap_bp > REPRO_TOL_BP:
        print("[cash_vehicle_window] REFUSING to publish: repo engine does not reproduce the"
              " published GC001 net (published %s, gap %s bp > %.1f)" % (pub_pct, gap_bp, REPRO_TOL_BP))
        return 2

    principal = PRINCIPAL_CNY
    cash, ticket_file = CV.ticket_cash_cny()

    cells = []
    for n in list(RUNGS) + [None]:
        rb = rung_bars(bars, n)
        if len(rb) < 5:
            continue
        days = int((rb[-1] - rb[0]).days) or 1
        arms = {}
        for name in ("GC001", "R-001"):
            r, info = CL.roll_rung(rb, rates, None, fees=None, name=name)
            arms[name] = {"pct": round(CL.cagr_pct(r, rb), 4),
                          "orders": len(info["contracts"]),
                          "missing": info.get("missing", 0)}
        gross = CL.cagr_pct(etf_ret_full.reindex(rb).fillna(0.0), rb)
        drag = commission_drag_pp(principal, days)
        net = gross - drag
        cell = {
            "lookback": (n if n is not None else "full"),
            "start": str(rb[0].date()),
            "end": str(rb[-1].date()),
            "bars": int(len(rb)),
            "years": round(days / 365.25, 3),
            "gc001_net_pct": arms["GC001"]["pct"],
            "r001_net_pct": arms["R-001"]["pct"],
            "money_etf_gross_pct": round(gross, 4),
            "money_etf_commission_drag_pp": round(drag, 4),
            "money_etf_net_pct": round(net, 4),
            "gap_gc001_minus_etf_pp": round(arms["GC001"]["pct"] - net, 4),
            "gap_r001_minus_etf_pp": round(arms["R-001"]["pct"] - net, 4),
            "gap_gc001_minus_r001_pp": round(arms["GC001"]["pct"] - arms["R-001"]["pct"], 4),
            "cny_per_year_on_1m": {
                "gc001": cny_per_year(principal, arms["GC001"]["pct"]),
                "r001": cny_per_year(principal, arms["R-001"]["pct"]),
                "money_etf": cny_per_year(principal, net),
            },
            "cny_per_year_on_ticket_cash": {
                "gc001": cny_per_year(cash, arms["GC001"]["pct"]),
                "r001": cny_per_year(cash, arms["R-001"]["pct"]),
                "money_etf": cny_per_year(cash, net),
            },
            "orders": {"gc001": arms["GC001"]["orders"], "r001": arms["R-001"]["orders"],
                       "money_etf": 2},
            "missing_quotes": {"gc001": arms["GC001"]["missing"], "r001": arms["R-001"]["missing"]},
        }
        cell["winner"] = winner_of(cell)
        cells.append(cell)

    face = {
        "schema": "bench_cash_vehicle_window/v1",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(bars[-1].date()),
        "question": ("同一笔闲置现金，沪市 GC001 逐日滚 / 深市 R-001 逐日滚 / 511880 买入持有，"
                     "在不同回看窗口下谁更值，答案会不会翻？"),
        "principal_cny": principal,
        "ticket_cash": {"cny": cash, "file": ticket_file},
        "window": {"start": str(bars[0].date()), "end": str(bars[-1].date()), "bars": int(len(bars)),
                   "rungs": [c["lookback"] for c in cells]},
        "vehicles": {
            "gc001_daily_roll": {"venue": "SSE", "fee_bp_per_order": CL.fee_bp("GC001"),
                                 "principal_is_available_intraday": False},
            "r001_daily_roll": {"venue": "SZSE", "fee_bp_per_order": CL.fee_bp("R-001"),
                                "principal_is_available_intraday": False},
            "money_etf_511880": {"venue": "SSE", "commission_pct_side": ETF_COMMISSION_PCT_SIDE,
                                 "commission_min_cny": ETF_COMMISSION_MIN_CNY,
                                 "principal_is_available_intraday": True,
                                 "consolidations_in_window": jumps},
        },
        "headline": headline_of(cells),
        "first_switch": first_switch(cells),
        "today": today_reading(cells),
        "reading": reading_of(cells, cash,
                              (cells[-1]["orders"]["gc001"] / max(cells[-1]["years"], 1e-9))
                              if cells else 0.0),
        "cells": cells,
        "control": {"published_gc001_net_pct": pub_pct, "gap_bp": None if gap_bp is None else round(gap_bp, 4),
                    "tolerance_bp": REPRO_TOL_BP},
        "honesty": [
            "短档（21/63/126 bar）的年化是这几天的收益按日历天外推，天生比 1008/full 吵；"
            "它们是拿来让「翻面点」看得见，不是可比的长期收益率",
            "511880 的收盘是锯齿：每年末份额折算造成一次深跌，本面沿用 etf_book_cash_vehicle "
            "的折算识别（当日收益记 0 并逐条列出），不识别就会把这本每年赚约 1.5% 的资产算成负的",
            "货币 ETF 的双边佣金按一次进一次出算，短档上这笔一次性费用被压进很短的天数里，"
            "所以短档的 net 明显低于 gross；长档上它趋近 4bp/年",
            "逆回购资金到期才可用、且必须收盘前续做；货基可以盘中卖出。这笔「灵活性」不在收益表里",
            "两个交易所的报价不是同一批人报的：GC001 与 R-001 在同一根 bar 上的利率不同，"
            "深市账户买不了 GC001，本面把两条腿并排而不是取平均",
            "511990 / 159001 仍不出数字：它们的收益以份额计，本仓没有每万份收益/净值面",
            "回看梯子是跑之前写死的，没有在看到结果后加档",
        ],
        "inputs": inputs_digest(),
        "elapsed_sec": None,
    }
    face["elapsed_sec"] = round(time.time() - t0, 2)

    if write:
        _dump(OUT, face)
        Path(PAGE).write_text(render_md(face), encoding="utf-8", newline="\n")
    if verbose:
        print("[cash_vehicle_window] %s  window %s..%s (%d bars)  ticket cash %.0f"
              % (face["headline"], face["window"]["start"], face["window"]["end"],
                 face["window"]["bars"], cash))
        for c in face["cells"]:
            print("  %-6s %s..%s  gc001 %7.4f%%  r001 %7.4f%%  etf %7.4f%% (gross %7.4f)  winner=%s"
                  % (c["lookback"], c["start"], c["end"], c["gc001_net_pct"], c["r001_net_pct"],
                     c["money_etf_net_pct"], c["money_etf_gross_pct"], c["winner"]))
        if face["first_switch"]:
            print("  first switch: %s -> %s (%s -> %s)" % face["first_switch"])
        print("  today: %s" % (face["today"]["verdict"],))
    return 0


# ---------------------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------------------
def render_md(face: dict) -> str:
    w = face["window"]
    lines = []
    lines.append("# 现金该停在哪支车上——同一问题，七个回看窗口（r1971 bm-c）")
    lines.append("")
    lines.append("同窗口 %s -> %s（%d 根 bar），本金 1,000,000；票面现金 %.0f 元（%s）。"
                 % (w["start"], w["end"], w["bars"], face["ticket_cash"]["cny"], face["ticket_cash"]["file"]))
    lines.append("")
    lines.append("## 七档回看（每档一次进一次出，各自独立计价）")
    lines.append("")
    lines.append("| 回看 | 窗口 | GC001 滚 | R-001 滚 | 511880 毛 | 511880 净 | 差（GC001−511880, pp） | 赢家 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in face["cells"]:
        lines.append("| %s | %s -> %s | %.4f%% | %.4f%% | %.4f%% | %.4f%% | %+.4f | %s |"
                     % (c["lookback"], c["start"], c["end"], c["gc001_net_pct"], c["r001_net_pct"],
                        c["money_etf_gross_pct"], c["money_etf_net_pct"],
                        c["gap_gc001_minus_etf_pp"], c["winner"]))
    lines.append("")
    lines.append("## 年账单（票面现金口径，元/年）")
    lines.append("")
    lines.append("| 回看 | GC001 | R-001 | 511880 净 | 最高 − 最低（元/年） |")
    lines.append("|---|---|---|---|---|")
    for c in face["cells"]:
        t = c["cny_per_year_on_ticket_cash"]
        lines.append("| %s | %.0f | %.0f | %.0f | %.0f |"
                     % (c["lookback"], t["gc001"], t["r001"], t["money_etf"],
                        max(t.values()) - min(t.values())))
    lines.append("")
    lines.append("## 判词")
    lines.append("")
    lines.append("**%s**" % face["headline"])
    if face["first_switch"]:
        lines.append("")
        lines.append("翻面点：%s → %s（%s → %s）" % face["first_switch"])
    lines.append("")
    lines.append("今日口径（只看 1 年 / 2 年两档，它们的现金利率还是今天能拿到的利率）：%s"
                 % face["today"]["verdict"])
    for lb, r in face["today"].get("rungs", {}).items():
        lines.append("- %s bar（%s -> %s）：GC001 %.4f%%，R-001 %.4f%%，511880 %.4f%%，赢家 %s"
                     % (lb, r["start"], r["end"], r["gc001_net_pct"], r["r001_net_pct"],
                        r["money_etf_net_pct"], r["winner"]))
    rd = face.get("reading") or {}
    if rd:
        lines.append("")
        lines.append("## 读法（票面现金 %.0f 元，逆回购 %.0f 单/年）"
                     % (face["ticket_cash"]["cny"], rd["orders_per_year"]))
        lines.append("")
        lines.append("| 回看 | GC001 比 511880 多（元/年） | 每下一单赚回（元） | 深市 R-001 比沪市少（元/年） |")
        lines.append("|---|---|---|---|")
        for c in face["cells"]:
            lb = str(c["lookback"])
            lines.append("| %s | %+.0f | %+.2f | %+.0f |"
                         % (lb, rd["gap_gc001_minus_etf_cny_per_year"][lb],
                            rd["cny_per_repo_order"][lb],
                            -rd["r001_penalty_cny_per_year"][lb]))
        lines.append("")
        c21 = next((c for c in face["cells"] if str(c["lookback"]) == "21"), None)
        if c21 is not None:
            gappp = c21["gc001_net_pct"] - c21["money_etf_gross_pct"]
            lines.append("注：短档（21/63/126）的「每单」把货币 ETF 的一次性双边佣金摊进了极短窗口，"
                         "读数被放大；这几档看毛差更诚实——21 档毛差 %.4fpp（票面现金口径约 %.0f 元/年），"
                         "也就是按今天的利率，多下 %d 单/年换回来的接近零。"
                         % (gappp, gappp / 100.0 * face["ticket_cash"]["cny"], round(rd["orders_per_year"])))
        lines.append("")
        if rd.get("today_short_rung_is_a_tie_before_friction"):
            lines.append("最近 21 根 bar 上逆回购与货基**税前几乎打平**（差 ≤1bp）：也就是说"
                         "按今天的利率，那 %d 单/年换回来的钱接近零，赚的是历史窗口里的差。"
                         % round(rd["orders_per_year"]))
        else:
            lines.append("最近 21 根 bar 上两者已经分开：滚逆回购仍然领先，见上表第一行。")
        lines.append("")
    lines.append("")
    lines.append("## 这张面不说的（印出来才不会说谎）")
    lines.append("")
    for h in face["honesty"]:
        lines.append("- " + h)
    lines.append("")
    lines.append("控制：本面导入的逆回购引擎复现已发布的 GC001 净收益（差 %.4f bp，容差 %.1f bp）。"
                 % ((face["control"]["gap_bp"] or 0.0), face["control"]["tolerance_bp"]))
    lines.append("")
    lines.append("复跑：")
    lines.append("")
    lines.append("```")
    lines.append("python scripts/bench_cash_vehicle_window.py selftest")
    lines.append("python scripts/bench_cash_vehicle_window.py run")
    lines.append("python scripts/bench_cash_vehicle_window.py check")
    lines.append("```")
    lines.append("")
    lines.append("Generated %s by `scripts/bench_cash_vehicle_window.py`."
                 % face["generated"])
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------
# check: re-derive, and refuse to look self-consistent when the inputs moved
# ---------------------------------------------------------------------------------------
def check(path=None) -> int:
    path = path or OUT
    if not os.path.exists(path):
        print("[cash_vehicle_window] STALE face missing: %s" % path)
        return 3
    face = _load(path)

    now_inputs = inputs_digest()
    recorded = face.get("inputs") or {}
    moved = []
    for name, meta in now_inputs.items():
        old = (recorded.get(name) or {}).get("sha256")
        if old != meta["sha256"]:
            moved.append("%s (%s -> %s)" % (name, (old or "missing")[:12], meta["sha256"][:12]))
    if moved:
        print("[cash_vehicle_window] STALE input bytes moved since this face was written: %s"
              % ", ".join(moved))
        return 3

    # re-derive every number from the panels, not from the face
    rates = CL.load_panel()
    etf = CV.load_etf("511880")
    etf_ret_full, _jumps = CV.consolidation_returns(etf)
    first = max(etf.index[0], pd.Timestamp("2013-04-18"))
    bars = pd.DatetimeIndex(sorted({b for s in rates.values() for b in s.index if b >= first}))
    principal = float(face["principal_cny"])
    bad = []
    for c in face["cells"]:
        n = None if c["lookback"] == "full" else int(c["lookback"])
        rb = rung_bars(bars, n)
        days = int((rb[-1] - rb[0]).days) or 1
        for nm, key in (("GC001", "gc001_net_pct"), ("R-001", "r001_net_pct")):
            r, _info = CL.roll_rung(rb, rates, None, fees=None, name=nm)
            got = round(CL.cagr_pct(r, rb), 4)
            if abs(got - float(c[key])) > CELL_TOL_PP:
                bad.append("%s/%s face %.4f re-derived %.4f" % (c["lookback"], key, c[key], got))
        gross = CL.cagr_pct(etf_ret_full.reindex(rb).fillna(0.0), rb)
        drag = commission_drag_pp(principal, days)
        if abs(round(gross - drag, 4) - float(c["money_etf_net_pct"])) > CELL_TOL_PP:
            bad.append("%s/money_etf_net_pct face %.4f re-derived %.4f"
                       % (c["lookback"], c["money_etf_net_pct"], gross - drag))
        if c["winner"] != winner_of(c):
            bad.append("%s/winner face %s derived %s" % (c["lookback"], c["winner"], winner_of(c)))
        if c["end"] != str(rb[-1].date()):
            bad.append("%s/end face %s derived %s" % (c["lookback"], c["end"], rb[-1].date()))
    if bad:
        print("[cash_vehicle_window] CHECK FAILED (%d):" % len(bad))
        for b in bad[:12]:
            print("  - " + b)
        return 1

    # verdicts must be derived from the numbers, not typed
    if face.get("headline") != headline_of(face["cells"]):
        print("[cash_vehicle_window] CHECK FAILED headline is not what the cells say")
        return 1
    if face.get("first_switch") != first_switch(face["cells"]):
        print("[cash_vehicle_window] CHECK FAILED first_switch is not what the cells say")
        return 1
    if face.get("today") != today_reading(face["cells"]):
        print("[cash_vehicle_window] CHECK FAILED today block is not what the cells say")
        return 1
    cash = float((face.get("ticket_cash") or {}).get("cny") or 0.0)
    orders = float(face["cells"][-1]["orders"]["gc001"]) / max(float(face["cells"][-1]["years"]), 1e-9)
    if face.get("reading") != reading_of(face["cells"], cash, orders):
        print("[cash_vehicle_window] CHECK FAILED reading block is not derived from the cells"
              " (ticket cash or order count moved)")
        return 1
    if [c["lookback"] for c in face["cells"]] != list(RUNGS) + ["full"]:
        print("[cash_vehicle_window] CHECK FAILED rung list is not the frozen ladder")
        return 1
    print("[cash_vehicle_window] CHECK OK %d cells, %d rungs, headline %s"
          % (len(face["cells"]), len(RUNGS) + 1, face["headline"]))
    return 0


# ---------------------------------------------------------------------------------------
# selftest: offline, and behavioural where it matters
# ---------------------------------------------------------------------------------------
def selftest() -> int:
    import tempfile
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    idx = pd.DatetimeIndex(pd.date_range("2020-01-01", periods=40, freq="D"))
    leg("L1 rung_bars(None) = whole window", len(rung_bars(idx, None)) == 40)
    leg("L2 rung_bars(21) = last 21 bars, ends on the cut",
        len(rung_bars(idx, 21)) == 21 and rung_bars(idx, 21)[-1] == idx[-1])
    leg("L3 rung_bars(9999) degrades to the whole window", len(rung_bars(idx, 9999)) == 40)

    leg("L4 commission: 1M round trip = 400 CNY", round_trip_commission(1_000_000) == 400.0)
    leg("L5 commission: small principal pays the 5 CNY floor on each side",
        round_trip_commission(10_000) == 10.0)
    leg("L6 drag shrinks with the window (one-year drag < short-rung drag)",
        commission_drag_pp(1_000_000, 365) < commission_drag_pp(1_000_000, 30))

    cell = {"gc001_net_pct": 1.6, "r001_net_pct": 1.5, "money_etf_net_pct": 1.52}
    leg("L7 winner_of picks the max arm", winner_of(cell) == "gc001_daily_roll")

    stable = [{"lookback": 21, "winner": "gc001_daily_roll"},
              {"lookback": 63, "winner": "gc001_daily_roll"}]
    flipped = [{"lookback": 21, "winner": "money_etf_511880"},
               {"lookback": 63, "winner": "money_etf_511880"},
               {"lookback": 252, "winner": "gc001_daily_roll"}]
    leg("L8 one winner everywhere -> STABLE headline", headline_of(stable) == "ONE_VEHICLE_WINS_EVERY_LOOKBACK")
    leg("L9 a changed winner -> FLIPS headline + first_switch naming both rungs",
        headline_of(flipped) == "LOOKBACK_DECIDES_THE_VEHICLE"
        and first_switch(flipped) == (63, 252, "money_etf_511880", "gc001_daily_roll"))
    leg("L10 no switch -> first_switch None", first_switch(stable) is None)

    # L11: the money ETF's consolidation reset must not be booked as a loss
    ser = pd.Series([100.0, 100.1, 100.2, 98.4, 98.5], index=idx[:5])
    ret, jumps = CV.consolidation_returns(ser)
    leg("L11 consolidation bar booked at zero and listed", len(jumps) == 1 and abs(ret.iloc[3]) < 1e-12
        and abs(jumps[0]["apparent_pct"] + 1.796) < 0.05)

    # L11b: the money reading is arithmetic on the cells, not a typed opinion
    fake = [{"lookback": "21", "gc001_net_pct": 1.10, "r001_net_pct": 1.00,
             "money_etf_net_pct": 1.00, "money_etf_gross_pct": 1.105}]
    rd = reading_of(fake, 500_000.0, 242.0)
    leg("L11b reading: 10bp on 500k = 500 CNY/year, 500/242 = 2.07 CNY per order",
        rd["gap_gc001_minus_etf_cny_per_year"]["21"] == 500.0
        and rd["cny_per_repo_order"]["21"] == 2.07
        and rd["today_short_rung_is_a_tie_before_friction"] is True)

    # L12 behavioural: a face whose numbers disagree with a re-derivation fails, without the STALE word
    face = _load(OUT) if os.path.exists(OUT) else None
    if face is None:
        legs.append(("L12 check() behavioural on a tampered face", False))
        legs.append(("L13 check() calls moved input bytes STALE", False))
    else:
        with tempfile.TemporaryDirectory() as td:
            p1 = os.path.join(td, "tampered.json")
            f1 = json.loads(json.dumps(face))
            f1["cells"][0]["gc001_net_pct"] = f1["cells"][0]["gc001_net_pct"] + 1.5
            with io.open(p1, "w", encoding="utf-8") as fh:
                json.dump(f1, fh, ensure_ascii=False)
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                rc1 = check(p1)
            finally:
                sys.stdout = old
            txt = buf.getvalue()
            legs.append(("L12 check() behavioural: tampered number -> rc1, no STALE wording",
                         rc1 == 1 and "CHECK FAILED" in txt and "STALE" not in txt))

            p2 = os.path.join(td, "moved.json")
            f2 = json.loads(json.dumps(face))
            k = list(f2["inputs"])[0]
            f2["inputs"][k]["sha256"] = "0" * 64
            with io.open(p2, "w", encoding="utf-8") as fh:
                json.dump(f2, fh, ensure_ascii=False)
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                rc2 = check(p2)
            finally:
                sys.stdout = old
            legs.append(("L13 check() behavioural: moved input bytes -> rc3 and the word STALE",
                         rc2 == 3 and "STALE" in buf.getvalue()))
    if os.path.exists(OUT):
        face = _load(OUT)
        md = render_md(face)
        rows = sum(1 for c in face["cells"] if ("| %s |" % c["lookback"]) in md)
        legs.append(("L14 rendered page carries every rung row and the headline",
                     rows == len(face["cells"]) and face["headline"] in md))

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print("  %-4s %s" % ("OK" if ok else "FAIL", n))
    print("[cash_vehicle_window] selftest %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd in ("selftest", "--selftest"):
        return selftest()
    if cmd == "check":
        return check(argv[1] if len(argv) > 1 else None)
    if cmd in ("run", "build"):
        return build(write=True)
    if cmd == "--dry":
        return build(write=False)
    print("usage: bench_cash_vehicle_window.py [run|check [path]|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
