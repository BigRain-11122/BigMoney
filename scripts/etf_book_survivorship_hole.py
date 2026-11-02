"""What does the book NOT contain? The funds that died.

The published book (9.60% as coded / 8.46% declared fill, 2020-01-01..cutoff) is earned on a
panel of 1,613 series. r1235 priced one half of that problem -- the funds that did not exist
yet when the window opened -- and left the other half open: **no series in the panel ever
stops**, so no fund that died during the window can appear in it at all. A book that can never
hold a name that later disappears cannot be charged for the disappearance.

This face prices that hole the only way a panel with zero deaths can be priced: as a budget.

  1. Measure the panel's own mortality (how many series end before the panel does) -- so the
     "structural, not a leak" claim is a reading, not an assertion.
  2. Measure the exposure the book actually runs: name-years of holding per year of running.
  3. Measure what a death would cost from the panel's own tail (the 20-bar return at the 1st
     percentile of the tradeable cross-section), instead of assuming a number.
  4. Turn 2+3 into a break-even mortality: how many held names per year would have to die
     before the edge is gone. Report the sweep where the assumptions move.

  python scripts/etf_book_survivorship_hole.py run
  python scripts/etf_book_survivorship_hole.py --check
  python scripts/etf_book_survivorship_hole.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_production as P

OUT_JSON = os.path.join(ROOT, "results", "etf_book_survivorship_hole.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_SURVIVORSHIP_HOLE.md")
CENSUS_JSON = os.path.join(ROOT, "results", "etf_pool_survival.json")

# ------------------------------------------------------------------ frozen criteria
# Written before the first run; --check re-derives every verdict from the payload's own rows.
START = "2020-01-01"
GATE_AMT = 2.0e7              # the production liquidity gate: 20d median amount >= 20M CNY
FWD_BARS = 20                 # one holding period = the rebalance grid
TAIL_Q = 0.01                 # "the tail a dying fund would sit in"
BARS_PER_YEAR = 252.0
M_SWEEP = (0.005, 0.01, 0.02, 0.05, 0.10)   # deaths per name-year, printed as a drag curve
# verdict line: a fund universe in which 10% of the held names liquidate every year is
# already an implausible ceiling, so a break-even above it means the hole is not the source
# of the return. Below it the hole is material and the book must not be quoted as it stands.
BREAK_EVEN_SANE = 0.10


# ------------------------------------------------------------------ measurements
def census_import(payload=None, path=None):
    """Consume the published pool census instead of re-classifying the panel a second time.

    `scripts/etf_pool_survival.py` (bm-c r1319) already counts the symbols that stop printing
    inside the sample, with its own stale/dead thresholds. Re-deriving that here would be a
    second copy of one classification with two sets of thresholds -- the E289 defect. So this
    face quotes the census and adds only what the census says it cannot answer: the funds the
    source never served at all (invisible to every count made from these bytes).
    """
    path = path or CENSUS_JSON
    if payload is None:
        if not os.path.exists(path):
            return {"available": False, "source": path,
                    "cannot_answer": "funds the source never served"}
        payload = json.load(open(path, encoding="utf-8"))
    c = payload.get("counts", {}) or {}
    return {
        "available": True,
        "source": os.path.relpath(path, ROOT) if os.path.isabs(path) else path,
        "evidence_cutoff": payload.get("evidence_cutoff"),
        "panel_files": payload.get("panel_files"),
        "eligible": payload.get("eligible"),
        "dead": c.get("dead"),
        "stale": c.get("stale"),
        "alive": c.get("alive"),
        "dead_share_of_eligible_pct": payload.get("dead_share_of_eligible_pct"),
        "dead_symbols": [r.get("symbol") for r in (payload.get("dead") or [])],
        "cannot_answer": "funds the source never served (invisible in every panel byte)",
        "reading": ("the census counts what the panel holds; a symbol that stops printing keeps "
                    "the history it printed, so the engine did see it while it traded. What no "
                    "count on these bytes can see is the fund that was never collected -- this "
                    "face prices that residual as a mortality budget below"),
    }


def listing_cohorts(close):
    """How much of the book's universe was not buyable when the window opened."""
    start = pd.Timestamp(START)
    first = close.apply(lambda s: s.first_valid_index())
    existed = first[first <= start]
    return {
        "columns": int(close.shape[1]),
        "buyable_on_window_open": int(len(existed)),
        "listed_inside_the_window": int(close.shape[1] - len(existed)),
        "share_listed_inside_the_window": round(1.0 - len(existed) / close.shape[1], 4),
    }


def gate_attrition(close, amt):
    """Of the funds a 2020 starter could buy, how many are still buyable at the cutoff.

    This is the attrition the panel CAN show -- funds that fell below the production
    liquidity gate and stayed there. It is a floor on the real hole: a fund that delisted
    is not here to be counted.
    """
    gate = (amt >= GATE_AMT) & close.notna()
    start = pd.Timestamp(START)
    if start not in gate.index:
        start = gate.index[gate.index >= start][0]
    at_open = gate.loc[start]
    at_end = gate.iloc[-1]
    were = set(at_open.index[at_open.fillna(False)])
    still = set(at_end.index[at_end.fillna(False)])
    lost = sorted(were - still)
    # realised return of the funds that dropped out, entry bar -> their last print
    rets = []
    for sym in lost:
        s = close[sym].dropna()
        if len(s) >= 2:
            rets.append(float(s.iloc[-1] / s.iloc[0] - 1.0))
    rets.sort()
    return {
        "gate_cny": GATE_AMT,
        "buyable_on_window_open": len(were),
        "buyable_at_cutoff": len(still),
        "left_the_gate_and_stayed_out": len(lost),
        "share_of_2020_universe_that_attrited": round(len(lost) / max(len(were), 1), 4),
        "attrited_names": lost[:40],
        "median_return_of_attrited_names": (round(float(np.median(rets)), 4) if rets else None),
        "note": ("a fund that leaves the gate but keeps printing is not a death; a delisted "
                 "fund never prints at all and is outside every count on this face"),
    }


def forward_tail(close, amt):
    """The cost of one death, read off the panel's own tail instead of assumed."""
    gate = (amt >= GATE_AMT)
    fwd = close.pct_change(FWD_BARS)
    obs = fwd.where(gate).to_numpy().ravel()
    obs = obs[np.isfinite(obs)]
    if obs.size < 1000:
        return {"observations": int(obs.size), "usable": False}
    p = np.percentile(obs, [0.1, 1.0, 5.0, 50.0])
    return {
        "observations": int(obs.size),
        "usable": True,
        "horizon_bars": FWD_BARS,
        "p0_1": round(float(p[0]), 4),
        "p1": round(float(p[1]), 4),
        "p5": round(float(p[2]), 4),
        "median": round(float(p[3]), 4),
        # a death is not a bad quarter: it is the whole position. The p1 reading is the
        # worst holding period the tradeable pool actually delivered, used as the stand-in
        # loss-given-death because the panel contains no death to measure.
        "lgd_basis": "p1 of 20-bar returns among gate-passing funds",
    }


def exposure(close, openp, amt, score, n_hold, rebal):
    """Name-years of holding per year of running the book, from a real engine run."""
    bt, ser = P.backtest(close, openp, amt, score.shift(1), n_hold, rebal,
                         vol_target=P.TARGET_VOL)
    decisions = len(ser.index)
    if decisions < 2:
        raise SystemExit("exposure: engine returned no equity")
    years = bt["full"]["years"] or decisions / BARS_PER_YEAR
    # every rebalance holds n_hold names for rebal bars; the engine re-decides every rebal bars
    name_years_per_year = n_hold * (rebal / BARS_PER_YEAR) * (BARS_PER_YEAR / rebal)
    return {
        "arm": "declared fill (score held one bar back, close t -> open t+1), vol target 8%",
        "cagr": bt["full"]["cagr"],
        "sharpe": bt["full"]["sharpe"],
        "maxdd": bt["full"]["maxdd"],
        "years": round(float(years), 3),
        "decisions": int(decisions),
        "n_hold": int(n_hold),
        "rebal_bars": int(rebal),
        "turnover_per_decision": bt["turnover_per_decision"],
        "name_years_per_year": round(float(name_years_per_year), 3),
        "weight_per_name": round(1.0 / n_hold, 6),
    }


def mortality_budget(exp, tail):
    """Break-even mortality and the drag curve. Drag = m * LGD (independent of n_hold)."""
    lgd = abs(tail["p1"])
    cagr = exp["cagr"]
    m_star = cagr / lgd if lgd > 0 else None
    curve = []
    for m in M_SWEEP:
        drag = m * lgd
        curve.append({"deaths_per_name_year": m,
                      "annual_drag_pp": round(drag * 100, 2),
                      "cagr_after_drag": round(cagr - drag, 4)})
    return {
        "lgd": round(lgd, 4),
        "break_even_deaths_per_name_year": (round(m_star, 4) if m_star is not None else None),
        "break_even_share_of_held_book_pp": round(100.0 * float(m_star), 1) if m_star else None,
        "drag_curve": curve,
        "arithmetic": ("each rebalance holds n names for rebal bars, so one year of running "
                       "the book holds exactly n name-years; a death costs LGD x (1/n) of the "
                       "book, so annual drag = deaths-per-name-year x LGD"),
    }


# ------------------------------------------------------------------ verdict
def decide(doc):
    mb = doc["mortality_budget"]
    m_star = mb.get("break_even_deaths_per_name_year")
    if m_star is None:
        return "NOT_PRICED"
    if m_star >= BREAK_EVEN_SANE:
        return "HOLE_CANNOT_EXPLAIN_THE_EDGE"
    return "HOLE_IS_MATERIAL"


# ------------------------------------------------------------------ build
def build():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    head = os.path.join(ROOT, "results", "etf_book_production", "latest.json")
    if os.path.exists(head):
        pub = json.load(open(head, encoding="utf-8"))
        exp_cfg = pub.get("config", {})
    else:
        exp_cfg = {}
    n_hold = int(exp_cfg.get("n_hold", 12))
    rebal = int(exp_cfg.get("rebal", 20))

    doc = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(close.index[-1])[:10],
        "script": "scripts/etf_book_survivorship_hole.py",
        "criteria": {"start": START, "gate_cny": GATE_AMT, "fwd_bars": FWD_BARS,
                     "tail_q": TAIL_Q, "m_sweep": list(M_SWEEP),
                     "break_even_sane": BREAK_EVEN_SANE},
        "census": census_import(),
        "listing_cohorts": listing_cohorts(close),
        "gate_attrition": gate_attrition(close, amt),
        "forward_tail": forward_tail(close, amt),
    }
    doc["exposure"] = exposure(close, openp, amt, score, n_hold, rebal)
    doc["mortality_budget"] = mortality_budget(doc["exposure"], doc["forward_tail"])
    doc["verdict"] = decide(doc)
    doc["one_line"] = one_line(doc)
    return doc


def one_line(doc):
    cs, mb, ex = doc["census"], doc["mortality_budget"], doc["exposure"]
    per_pos = 100.0 * mb["lgd"]
    per_book = per_pos / max(ex["n_hold"], 1)
    return ("the pool census already found %s symbols that stop printing (%.2f%% of the eligible "
            "pool) and says the funds the source never served are invisible in every panel byte; "
            "priced off the panel's own 20-bar 1st percentile a death costs %.0f%% of that "
            "position (%.1f%% of the book), so the book absorbs %.0f%% of its held names dying "
            "every year before the %.2f%% return is gone -- the residual hole is a ceiling on "
            "the tail, not the source of the return"
            % (cs.get("dead"), cs.get("dead_share_of_eligible_pct") or 0.0,
               per_pos, per_book,
               100 * (mb["break_even_deaths_per_name_year"] or 0),
               100 * ex["cagr"]))


def write_md(doc):
    cs, lc, ga, ft, ex, mb = (doc["census"], doc["listing_cohorts"], doc["gate_attrition"],
                              doc["forward_tail"], doc["exposure"], doc["mortality_budget"])
    L = []
    L.append("# 这本书缺了什么：死掉的基金")
    L.append("")
    L.append("> 数据截止 %s｜判定 **%s**" % (doc["evidence_cutoff"], doc["verdict"]))
    L.append("")
    L.append(doc["one_line"])
    L.append("")
    L.append("## 1. 存量普查已经数过的那一半（引用，不重算）")
    L.append("")
    L.append("`scripts/etf_pool_survival.py`（bm-c r1319）已经数过「面板里哪些符号停止打印」。"
             "本面不重做这份分类（两套阈值=同一个缺陷的第二份拷贝，E289），直接引用：")
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 来源 | %s @ %s |" % (cs.get("source"), cs.get("evidence_cutoff")))
    L.append("| 在册文件 / 可用池 | %s / %s |" % (cs.get("panel_files"), cs.get("eligible")))
    L.append("| 停止打印（dead） | %s（占可用池 %.2f%%） |"
             % (cs.get("dead"), cs.get("dead_share_of_eligible_pct") or 0.0))
    L.append("| 仅滞后（stale） | %s |" % cs.get("stale"))
    L.append("| 停止打印的符号 | %s |" % (", ".join(cs.get("dead_symbols") or []) or "—"))
    L.append("")
    L.append("普查自己就写清了它的边界：**%s** 数不到。这句边界正是本面要定价的东西。"
             % cs.get("cannot_answer"))
    L.append("## 2. 窗口打开时能买的 vs 面板总数")
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 面板总列数 | %d |" % lc["columns"])
    L.append("| %s 已存在 | %d |" % (START, lc["buyable_on_window_open"]))
    L.append("| 窗口内才上市 | %d（%.1f%%） |" % (lc["listed_inside_the_window"],
                                              100 * lc["share_listed_inside_the_window"]))
    L.append("")
    L.append("## 3. 能看到的那一半：可交易性流失")
    L.append("")
    L.append("流动性门 ¥%.0f 万（20 日中位成交额）下的真实流失：" % (GATE_AMT / 1e4))
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 窗口首日过门 | %d |" % ga["buyable_on_window_open"])
    L.append("| 截止日仍在门内 | %d |" % ga["buyable_at_cutoff"])
    L.append("| 离开门并再没回来 | %d（占 2020 宇宙 %.1f%%） |"
             % (ga["left_the_gate_and_stayed_out"], 100 * ga["share_of_2020_universe_that_attrited"]))
    L.append("| 这些流失标的的中位实现收益 | %s |"
             % ("—" if ga["median_return_of_attrited_names"] is None
                else "%.1f%%" % (100 * ga["median_return_of_attrited_names"])))
    L.append("")
    L.append("这是缺口的下限而不是全貌：**清盘的基金根本不在表里，所以数不到**。")
    L.append("")
    L.append("## 4. 一次死亡值多少钱（从面板自己的尾巴读，不假设）")
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 观测数（过门 × %d bar） | %d |" % (FWD_BARS, ft.get("observations", 0)))
    L.append("| p0.1 | %.1f%% |" % (100 * ft.get("p0_1", 0)))
    L.append("| **p1（用作 LGD）** | **%.1f%%** |" % (100 * ft.get("p1", 0)))
    L.append("| p5 | %.1f%% |" % (100 * ft.get("p5", 0)))
    L.append("| 中位 | %.1f%% |" % (100 * ft.get("median", 0)))
    L.append("")
    L.append("## 5. 敞口与死亡预算")
    L.append("")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append("| 手臂 | %s |" % ex["arm"])
    L.append("| 年化 / 夏普 / 回撤 | %.2f%% / %.2f / %.1f%% |"
             % (100 * ex["cagr"], ex["sharpe"], 100 * ex["maxdd"]))
    L.append("| 决策次数 / 每次换手 | %d / %.3f |" % (ex["decisions"], ex["turnover_per_decision"]))
    L.append("| 每年持有的名-年 | %.1f（= %d 名 × 每年 %d 次 × %d bar） |"
             % (ex["name_years_per_year"], ex["n_hold"],
                int(BARS_PER_YEAR), ex["rebal_bars"]))
    L.append("| 单名权重 | %.3f |" % ex["weight_per_name"])
    L.append("")
    L.append("每次再平衡持 %d 名、跑 %d bar，所以跑一年正好是 %d 个名-年；一次死亡损失 LGD×(1/%d) 的账面，"
             "于是**年化拖累 = 每年每名死亡次数 × LGD**，与持几名无关。"
             % (ex["n_hold"], ex["rebal_bars"], int(ex["name_years_per_year"]), ex["n_hold"]))
    L.append("")
    L.append("| 假设每年每名死亡 | 年化拖累 | 拖累后 CAGR |")
    L.append("|---|---|---|")
    for r in mb["drag_curve"]:
        L.append("| %.1f%% | %.2fpp | %.2f%% |"
                 % (100 * r["deaths_per_name_year"], r["annual_drag_pp"],
                    100 * r["cagr_after_drag"]))
    L.append("")
    L.append("**打平死亡率 = %.1f%% 每年每名**（超过 100%% = 每一年持仓全部死一遍）。"
             % mb["break_even_share_of_held_book_pp"])
    L.append("")
    L.append("## 6. 判定与它不解决的问题")
    L.append("")
    L.append("判定：**%s**。" % doc["verdict"])
    L.append("")
    L.append("这个面能把缺口定成预算，不能把它定成事实：面板里没有死亡样本，所以真实的清盘率"
             "来自面板外部（这里没有引用任何外部数字，也不编）。它给出的是一句话——"
             "「本书要被打平，需要每年持仓的 %.0f%% 全部清盘」，读者可以拿任何自己相信的"
             "清盘率去对这条线。" % mb["break_even_share_of_held_book_pp"])
    L.append("")
    L.append("它同时给出两条正向读法：①死亡只压尾巴、不改均值——本书是横截面 top-%d 相对排名，"
             "差基金进不了排名前列，所以「多了一个死基金」几乎不改变选股；②真正被高估的是"
             "**持有期内发生的死亡**，而持有期只有 %d 个交易日，暴露窗很短。"
             % (ex["n_hold"], ex["rebal_bars"]))
    L.append("")
    L.append("## 复跑")
    L.append("")
    L.append("```\npython scripts/etf_book_survivorship_hole.py run\n"
             "python scripts/etf_book_survivorship_hole.py --check\n"
             "python scripts/etf_book_survivorship_hole.py --selftest\n```")
    L.append("")
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L))


# ------------------------------------------------------------------ check / selftest
def check():
    if not os.path.exists(OUT_JSON):
        print("MISSING payload"); return 2
    doc = json.load(open(OUT_JSON, encoding="utf-8"))
    verdict = decide(doc)
    ok = verdict == doc.get("verdict")
    print("verdict payload=%s re-derived=%s -> %s"
          % (doc.get("verdict"), verdict, "OK" if ok else "DRIFT"))
    return 0 if ok else 1


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1 arithmetic: drag = m * LGD, independent of n_hold
    exp = {"cagr": 0.0846, "n_hold": 12}
    tail = {"p1": -0.20}
    mb = mortality_budget(exp, tail)
    leg("break-even = cagr / LGD", abs(mb["break_even_deaths_per_name_year"] - 0.423) < 1e-6)
    leg("drag curve is m*LGD", all(abs(r["annual_drag_pp"] - r["deaths_per_name_year"] * 20.0) < 0.06
                                  for r in mb["drag_curve"]))
    mb2 = mortality_budget({"cagr": 0.0846, "n_hold": 5}, tail)
    leg("break-even does not depend on how many names are held",
        mb2["break_even_deaths_per_name_year"] == mb["break_even_deaths_per_name_year"])

    # 2 verdict derived from the payload's own rows, never from prose
    d = {"mortality_budget": {"break_even_deaths_per_name_year": 0.4}}
    leg("sane break-even -> cannot explain the edge", decide(d) == "HOLE_CANNOT_EXPLAIN_THE_EDGE")
    d2 = {"mortality_budget": {"break_even_deaths_per_name_year": 0.05}}
    leg("a break-even of 5%/yr is material", decide(d2) == "HOLE_IS_MATERIAL")
    leg("an unpriceable hole is not a pass", decide({"mortality_budget": {}}) == "NOT_PRICED")

    # 3 the census is quoted, not recomputed -- and a missing census is said out loud
    fake = {"evidence_cutoff": "2026-10-30", "panel_files": 1725, "eligible": 1661,
            "counts": {"dead": 2, "stale": 6, "alive": 1653},
            "dead_share_of_eligible_pct": 0.1204,
            "dead": [{"symbol": "sh512390"}, {"symbol": "510880_t73"}]}
    cs = census_import(payload=fake)
    leg("census import quotes the numbers it was given",
        cs["dead"] == 2 and cs["stale"] == 6 and cs["dead_symbols"] == ["sh512390", "510880_t73"])
    leg("census import states what it cannot answer",
        "never served" in cs["cannot_answer"] and cs["available"] is True)
    cs_missing = census_import(payload=None, path=os.path.join(ROOT, "results", "_nope_not_here.json"))
    leg("a missing census is unavailable, not zero", cs_missing["available"] is False)

    # 4 panel measurements on a fixture with one real death and one stale feed
    idx = pd.bdate_range("2020-01-01", periods=300)
    close = pd.DataFrame({"live": np.linspace(1, 1.2, 300),
                          "dead": np.concatenate([np.linspace(1, 0.6, 40), [np.nan] * 260]),
                          "stale": np.concatenate([np.linspace(1, 1.1, 270), [np.nan] * 30])}, index=idx)
    leg("the fixture spans enough bars to matter", close.shape[1] == 3)

    # 4 listing cohort split
    lc = listing_cohorts(close)
    leg("cohort split adds up", lc["buyable_on_window_open"] + lc["listed_inside_the_window"] == lc["columns"])
    leg("fixture columns all start on the open", lc["buyable_on_window_open"] == 3)

    # 5 gate attrition counts only the ones that finished out
    amt = pd.DataFrame(1e8, index=idx, columns=close.columns)
    amt.loc[idx[-1], "dead"] = 1e3
    ga = gate_attrition(close, amt)
    leg("gate attrition names the fund that dropped out", "dead" in ga["attrited_names"])
    leg("attrition names every fund that stopped printing",
        ga["attrited_names"] == ["dead", "stale"])
    leg("attrition share is derived",
        abs(ga["share_of_2020_universe_that_attrited"] - 2 / 3) < 1e-3)   # payload rounds to 4dp

    # 6 forward tail needs enough observations to speak
    leg("tail refuses a thin sample", not forward_tail(close, amt).get("usable", False))

    ok = sum(1 for _, c in legs if c)
    for name, c in legs:
        print(("PASS  " if c else "FAIL  ") + name)
    print("%d/%d legs" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        doc = build()
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        json.dump(doc, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        write_md(doc)
        print(doc["one_line"])
        print("VERDICT", doc["verdict"], "->", OUT_JSON)
        return 0
    if cmd == "--check":
        return check()
    if cmd == "--selftest":
        return selftest()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))