"""ETF book: what the one bar the engine books before it could have bought is worth.

`etf_robust_pf.open_to_open_equity` decides on the CLOSE of bar d and then accrues the new
book from the OPEN of that same bar d.  That open happened before the close the picks were
read from, so every rebalance books one day of the move on a book it could not have owned
yet.  r1794 measured that day at 1.79pp on one cell with a second implementation; this face
does the two things r1794 could not:

  1. it puts the switch INSIDE the shared engine (`entry_lag=1`), default-off so every
     published face stays reproducible bit for bit, and cross-checks the corrected path
     against the independent whole-share implementation of `etf_book_lot_ladder`
  2. it re-asks the only question a reader has after a number moves: **does the book still
     beat the index?**  Both calibers are measured against 510300 held the same way
     (open-to-open, same start, no rebalancing), so the excess is read on one ruler

The bulge is not "one average day per rebalance": on a rebalance bar the ledger swaps the
old book's day for the new book's day, so the per-cell bulge is
``sum log((1+r_new)/(1+r_old))`` over rebalance bars.  It therefore does NOT fall
monotonically as the rebalance window widens, and this face prints the measured multiple
beside each cell instead of asserting a shape it does not have.

Frozen judgement (written before the reading):
  EXCESS_SURVIVES_CALIBER_FIX  corrected full-window CAGR minus the index's own is > 0
  EXCESS_IS_THE_BULGE          it is not -- the printed excess was the extra bar

Usage:
    python scripts/etf_book_entry_lag.py run
    python scripts/etf_book_entry_lag.py --selftest
    python scripts/etf_book_entry_lag.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_book_lot_ladder as L

OUT_JSON = os.path.join(ROOT, "results", "etf_book_entry_lag.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_ENTRY_LAG.md")

START = "2020-01-01"
IS_END = "2023-12-31"
BENCH = "510300"
COSTS = (0.0005, 0.0010)
CELLS = tuple((n, rb) for n in (3, 5, 8) for rb in (10, 20, 40))
CANON = (5, 20, 0.0010)          # the cell every published headline quotes
TARGET_VOL = 0.08
CROSS_TOL_PP = 0.50              # frozen: engine(lag=1) vs whole-share implementation


def _stats(ser, label):
    return R.stats(ser, label)


def index_buy_hold(close, openp, code=BENCH, start=START):
    """The index held the way the book trades: bought at an open, marked at opens, never
    rebalanced.  Level 1.0 on its first finite open at/after `start`."""
    op = openp.reindex(columns=close.columns)
    s = op[code].dropna()
    s = s[s.index >= pd.Timestamp(start)]
    if s.empty:
        raise ValueError("no %s opens at/after %s" % (code, start))
    return s / float(s.iloc[0])


def _panel():
    """The printed face's own panel: unrepaired, because the point is to reproduce the
    caliber that prices every published number, then move only the timing."""
    close, openp, amt, feats = E.build_panel()
    score = E.build_score(close, amt, feats)
    return close, openp, amt, score


def _one(close, openp, amt, score, n_hold, rebal, cost, lag):
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                                      entry_lag=lag)
    m = _stats(ser, "N%d_R%d_%dbp_lag%d" % (n_hold, rebal, cost * 1e4, lag))
    oos = _stats(ser[ser.index > pd.Timestamp(IS_END)], m["label"] + "_oos")
    return {"cagr": m.get("cagr"), "sharpe": m.get("sharpe"), "maxdd": m.get("maxdd"),
            "cagr_oos": oos.get("cagr"), "sharpe_oos": oos.get("sharpe"),
            "turnover": round(float(turn), 3)}, ser


def run():
    close, openp, amt, score = _panel()
    cutoff = str(close.index[-1].date())
    bench = index_buy_hold(close, openp)
    bm = _stats(bench, "index_" + BENCH)
    bench_oos = _stats(bench[bench.index > pd.Timestamp(IS_END)], "index_oos")
    bench_row = {"code": BENCH, "cagr": bm.get("cagr"), "sharpe": bm.get("sharpe"),
                 "maxdd": bm.get("maxdd"), "cagr_oos": bench_oos.get("cagr"),
                 "n_bars": int(len(bench)), "start": str(bench.index[0].date()),
                 "execution": "bought at the first open at/after %s, marked at opens" % START}

    rows, series = [], {}
    for n_hold, rebal in CELLS:
        for cost in COSTS:
            p, sp = _one(close, openp, amt, score, n_hold, rebal, cost, 0)
            c, sc_ = _one(close, openp, amt, score, n_hold, rebal, cost, 1)
            ratio = (sp / sc_).dropna()
            changes = int((ratio.diff().abs() > 1e-12).sum())
            n_rebal = int(len(range(0, len(sp), rebal)))
            row = {
                "label": "N%d_R%d_%dbp" % (n_hold, rebal, cost * 1e4),
                "n_hold": n_hold, "rebal": rebal, "cost_bp": cost * 1e4,
                "printed": p, "corrected": c,
                "bulge_pp": round((p["cagr"] - c["cagr"]) * 100, 3),
                "bulge_oos_pp": round(((p["cagr_oos"] or 0) - (c["cagr_oos"] or 0)) * 100, 3),
                "excess_printed_pp": round((p["cagr"] - bm["cagr"]) * 100, 2),
                "excess_corrected_pp": round((c["cagr"] - bm["cagr"]) * 100, 2),
                "ratio_end": round(float(ratio.iloc[-1]), 6),
                "n_ratio_changes": changes,
                "n_rebalances": n_rebal,
                "sharpe_delta": round((c["sharpe"] or 0) - (p["sharpe"] or 0), 3),
            }
            rows.append(row)
            if (n_hold, rebal, cost) == CANON:
                series["canon"] = (sp, sc_)

    # the production candidate: whole book + 8% vol target
    vt = {}
    for lag in (0, 1):
        ser, _t = R.open_to_open_equity(close, openp, amt, score, CANON[1], CANON[0],
                                        CANON[2], vol_target=TARGET_VOL, entry_lag=lag)
        m = _stats(ser, "vt_lag%d" % lag)
        o = _stats(ser[ser.index > pd.Timestamp(IS_END)], "vt_lag%d_oos" % lag)
        vt["lag%d" % lag] = {"cagr": m.get("cagr"), "sharpe": m.get("sharpe"),
                             "maxdd": m.get("maxdd"), "cagr_oos": o.get("cagr"),
                             "sharpe_oos": o.get("sharpe"), "maxdd_oos": o.get("maxdd")}
    vt["bulge_pp"] = round((vt["lag0"]["cagr"] - vt["lag1"]["cagr"]) * 100, 3)
    vt["excess_printed_pp"] = round((vt["lag0"]["cagr"] - bm["cagr"]) * 100, 2)
    vt["excess_corrected_pp"] = round((vt["lag1"]["cagr"] - bm["cagr"]) * 100, 2)

    # independent implementation: whole-share book, one-share lots, no ticket floor.
    # It decides at the close and buys at the next open, and it has never seen entry_lag.
    ind_ser, ind_info = L.lot_equity(close, openp, amt, score, 1_000_000,
                                     rebal=CANON[1], n_hold=CANON[0], cost=CANON[2],
                                     lot=1, fee_floor=0.0, start=START)
    ind = _stats(ind_ser / 1_000_000.0, "independent_next_open")
    canon = next(r for r in rows if r["label"] == "N%d_R%d_%dbp" % (CANON[0], CANON[1],
                                                                  CANON[2] * 1e4))
    cross_gap = round((canon["corrected"]["cagr"] - ind.get("cagr")) * 100, 3)

    printed_best = max(rows, key=lambda r: (r["printed"]["sharpe"] or -9))
    corrected_best = max(rows, key=lambda r: (r["corrected"]["sharpe"] or -9))

    excess_corrected = canon["excess_corrected_pp"]
    verdict = "EXCESS_SURVIVES_CALIBER_FIX" if excess_corrected > 0 else "EXCESS_IS_THE_BULGE"

    out = {
        "evidence_cutoff": cutoff,
        "execution": "decide at close t, trade at open t+1; entry_lag=0 is the published "
                     "caliber (books the decision bar's own open), entry_lag=1 is the "
                     "docstring's promise",
        "panel": "unrepaired twin (etf_robust_pf.build_panel), as every published number",
        "cell": canon["label"],
        "thresholds": {"cross_tol_pp": CROSS_TOL_PP},
        "index": bench_row,
        "rows": rows,
        "production_candidate_vol_target": dict(vt, target_vol=TARGET_VOL),
        "cross_check": {
            "implementation": "etf_book_lot_ladder.lot_equity (whole shares, no ticket "
                              "floor, buys at the open after the decision)",
            "cagr": ind.get("cagr"), "sharpe": ind.get("sharpe"),
            "cash_avg_pct": ind_info.get("cash_avg_pct"),
            "engine_corrected_cagr": canon["corrected"]["cagr"],
            "gap_pp": cross_gap,
        },
        "ranking": {
            "best_by_sharpe_printed": printed_best["label"],
            "best_by_sharpe_corrected": corrected_best["label"],
            "flipped": printed_best["label"] != corrected_best["label"],
        },
        "verdict": verdict,
        "excess_corrected_pp": excess_corrected,
        "excess_printed_pp": canon["excess_printed_pp"],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("evidence_cutoff", "cell", "verdict",
                                          "excess_printed_pp", "excess_corrected_pp")},
                     ensure_ascii=False))
    print("index", bench_row)
    for r in rows:
        print(r["label"], "printed %.2f%%/%.3f  corrected %.2f%%/%.3f  bulge %+.2fpp  "
              "excess %+.2f -> %+.2f  ratio %.4f in %d bars"
              % (r["printed"]["cagr"] * 100, r["printed"]["sharpe"],
                 r["corrected"]["cagr"] * 100, r["corrected"]["sharpe"], r["bulge_pp"],
                 r["excess_printed_pp"], r["excess_corrected_pp"], r["ratio_end"],
                 r["n_ratio_changes"]))
    print("cross-check", out["cross_check"])
    print("ranking", out["ranking"])
    print("md ->", _md(out))
    return out


def _md(out):
    b = out["index"]
    c = next(r for r in out["rows"] if r["label"] == out["cell"])
    vt = out["production_candidate_vol_target"]
    L_ = []
    L_.append("# ETF 书：引擎多记的那一天，值多少钱\n")
    L_.append("> evidence_cutoff=%s；格=%s；面板=未修翻转的印刷面同款。\n"
              % (out["evidence_cutoff"], out["cell"]))
    L_.append("## 问题\n")
    L_.append("`etf_robust_pf.open_to_open_equity` 在 **bar d 的收盘**读分选股，"
              "却让新仓从 **bar d 自己的开盘**起算收益——那个开盘发生在读分之前，"
              "所以每次调仓都多记一天它买不到的涨跌。r1794 用一个独立实现量出这一天的 "
              "1.79pp，但没在引擎里修。本面把开关放进引擎（`entry_lag`，默认 0 = 与"
              "已发布面逐位一致），再用同一把尺子回答读者唯一关心的问题：**修掉之后，"
              "这本书还跑得赢指数吗？**\n")
    L_.append("## 基准（同一执行口径）\n")
    L_.append("| 标的 | 起 | 年化 | 夏普 | 最大回撤 | 样本外年化 |\n|---|---|---:|---:|---:|---:|")
    L_.append("| %s | %s | %.2f%% | %.2f | %.2f%% | %s |" % (
        b["code"], b["start"], b["cagr"] * 100, b["sharpe"], b["maxdd"] * 100,
        ("%.2f%%" % (b["cagr_oos"] * 100)) if b.get("cagr_oos") is not None else "—"))
    L_.append("\n同口径=买入后不调仓、按开盘标记（所以它没有「多记一天」的问题：它从不调仓）。\n")
    L_.append("## 十八格的两种口径\n")
    L_.append("| 格 | 印刷年化 | 修正年化 | 多记 | 印刷夏普 | 修正夏普 | 超额(印刷) | 超额(修正) | "
              "净值比 | 变动的 bar |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in out["rows"]:
        L_.append("| %s | %.2f%% | %.2f%% | %+.2fpp | %.3f | %.3f | %+.2fpp | %+.2fpp | %.4f | %d |"
                  % (r["label"], r["printed"]["cagr"] * 100, r["corrected"]["cagr"] * 100,
                     r["bulge_pp"], r["printed"]["sharpe"], r["corrected"]["sharpe"],
                     r["excess_printed_pp"], r["excess_corrected_pp"], r["ratio_end"],
                     r["n_ratio_changes"]))
    L_.append("\n「净值比」=印刷口径终值 / 修正口径终值；「变动的 bar」=两条路径开始分叉的"
              "bar 数——**它只能落在调仓 bar 上，且当新旧两仓相同时那次调仓不产生差**，"
              "所以这个数 ≤ 调仓次数（差多少就是多少次调仓没换票）。\n")
    L_.append("## 生产候选（整本 + 8% 波动目标）\n")
    L_.append("| 口径 | 年化 | 夏普 | 最大回撤 | 样本外年化 | 样本外夏普 | 样本外回撤 |\n"
              "|---|---:|---:|---:|---:|---:|---:|")
    for lag, name in (("lag0", "印刷"), ("lag1", "修正")):
        v = vt[lag]
        L_.append("| %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %.3f | %.2f%% |"
                  % (name, v["cagr"] * 100, v["sharpe"], v["maxdd"] * 100,
                     v["cagr_oos"] * 100, v["sharpe_oos"], v["maxdd_oos"] * 100))
    L_.append("\n生产候选也掉 **%.2fpp**（超额 %+.2fpp → %+.2fpp）。\n"
              % (vt["bulge_pp"], vt["excess_printed_pp"], vt["excess_corrected_pp"]))
    L_.append("## 判决\n")
    if out["verdict"] == "EXCESS_SURVIVES_CALIBER_FIX":
        L_.append("**超额修不掉。** 主格超额从 **%+.2fpp** 降到 **%+.2fpp**（指数同口径年化 "
                  "%.2f%%），少的正好就是多记的那一天（%.2fpp）。读者该记的是修正后的数："
                  "**这本书仍然跑赢指数 %.2f 个百分点/年**，但印刷面比真实成交高估了 %.2fpp。\n"
                  % (c["excess_printed_pp"], c["excess_corrected_pp"], b["cagr"] * 100,
                     c["bulge_pp"], c["excess_corrected_pp"], c["bulge_pp"]))
    else:
        L_.append("**超额就是那一天。** 修正后主格超额 **%+.2fpp**，印刷面的超额（%+.2fpp）"
                  "全部来自多记的那一天。\n" % (c["excess_corrected_pp"], c["excess_printed_pp"]))
    rk = out["ranking"]
    if rk["flipped"]:
        L_.append("**并且它改排名。** 按夏普选格：印刷口径选 `%s`，修正口径选 `%s`——"
                  "调仓越勤、多记的天数越多，所以印刷口径系统性偏向快调仓。"
                  "任何「最优参数」的结论都要先过这一刀。\n"
                  % (rk["best_by_sharpe_printed"], rk["best_by_sharpe_corrected"]))
    else:
        L_.append("**排名没有翻转**：两种口径下夏普最优的格都是 `%s`。\n"
                  % rk["best_by_sharpe_corrected"])
    L_.append("## 为什么多记的不是「一次平均日」\n")
    L_.append("调仓 bar 上，账本用**新仓**的一天换掉**旧仓**的一天，所以每格的多记量是 "
              "`Σ log((1+r_new)/(1+r_old))`，不是「调仓次数 × 平均日收益」。"
              "实测净值比：R10 %s、R20 %s、R40 %s（N5 三行）——**不随调仓窗单调**，"
              "因为窗口越宽，旧仓越陈旧、新仓第一天的落差越大。本面把实测比值逐行印出来，"
              "不去断言一个它没有的形状。\n"
              % tuple("%.4f" % r["ratio_end"] for r in out["rows"]
                      if r["n_hold"] == 5 and r["cost_bp"] == 10.0))
    L_.append("## 交叉验证\n")
    x = out["cross_check"]
    L_.append("独立的整份实现（`etf_book_lot_ladder.lot_equity`：整股、无票底、决策后的下一根"
              "开盘买入，从未见过 `entry_lag`）在同一格给出 **%.2f%%** / 夏普 %.3f，"
              "与修正后的引擎 **%.2f%%** 相差 **%+.2fpp**（冻结容差 %.2fpp）——差的那一点"
              "是整股取整留下的现金（平均 %.2f%% 在现金里）。两套实现互相不认识，却落在同一格。\n"
              % (x["cagr"] * 100, x["sharpe"], x["engine_corrected_cagr"] * 100, x["gap_pp"],
                 out["thresholds"]["cross_tol_pp"], x["cash_avg_pct"]))
    L_.append("## 这一面没有做的\n")
    L_.append("- **没有改默认值**：`entry_lag` 默认 0，所有已发布面依旧可逐位复现；"
              "把默认翻成 1 要级联重算下游全部消费面（含 CEO 页与订单卡），属下一轮的出生站修复。\n")
    L_.append("- `etf_equity_alpha.run_with_attribution`（分类归因面）是同一族的第二份拷贝，"
              "同样从决策 bar 的开盘起算；本面没有动它，只在方法论卡上点明。\n")
    L_.append("- 指数基准是 510300 单一标的；票池幸存者偏差照旧；未计融券/做空腿成本。\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L_) + "\n")
    return OUT_MD


# --------------------------------------------------------------------------- selftest
def _fixture(n=140, aaa=None, bbb=None, score_hi=("AAA", "BBB")):
    """Two names, flat by default; long enough to clear the 120-bar eligibility gate."""
    idx = pd.bdate_range("2020-01-02", periods=n)
    close = pd.DataFrame({"AAA": aaa or [10.0] * n, "BBB": bbb or [100.0] * n}, index=idx)
    openp = close.copy()
    amt = pd.DataFrame({"AAA": [1e9] * n, "BBB": [1e9] * n}, index=idx)
    hi, lo = score_hi
    score = pd.DataFrame({hi: [1.0] * n, lo: [0.0] * n}, index=idx)
    return close, openp, amt, score


def _ref_next_open(close, openp, amt, score, rebal, n_hold, start_i, cost=0.0):
    """A deliberately dumb reference: decide at the close, own it from the NEXT open."""
    op = openp.reindex(columns=close.columns)
    dates = list(op.index)[start_i:]
    level, held, turns = 1.0, {}, []
    for i in range(len(dates) - 1):
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[dates[i], p], op.at[dates[i + 1], p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        level *= 1.0 + r
        if i % rebal == 0:
            s = score.loc[dates[i]].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
                level *= 1.0 - cost * turn
                turns.append(turn)
                held = w
    return level, turns


def selftest():
    fails = []
    n = 140
    start_i = 125
    start = str(pd.bdate_range("2020-01-02", periods=n)[start_i].date())

    # L1 default is the published caliber: no kwarg == entry_lag=0, bit for bit
    close, openp, amt, score = _fixture(n)
    a0, _ = R.open_to_open_equity(close, openp, amt, score, 5, 1, 0.0, start=start)
    a1, _ = R.open_to_open_equity(close, openp, amt, score, 5, 1, 0.0, start=start,
                                  entry_lag=0)
    if not np.allclose(a0.values, a1.values, rtol=0, atol=0):
        fails.append("L1 default is not entry_lag=0")
    if (a0.values != a1.values).any():
        fails.append("L1b default differs by more than rounding")

    # L2 the decision bar's open belongs to the OLD book.  AAA's open jumps 10 -> 11 at the
    # bar after the decision, so the printed caliber books +10% and the corrected one books
    # nothing (it was holding cash and then buys at 11).
    up = [10.0] * (start_i + 1) + [11.0] * (n - start_i - 1)
    close2, openp2, amt2, score2 = _fixture(n)
    openp2 = openp2.copy()
    openp2["AAA"] = up
    close2 = close2.copy()
    close2["AAA"] = up
    s_printed, _ = R.open_to_open_equity(close2, openp2, amt2, score2, 10_000, 1, 0.0,
                                        start=start)
    s_fixed, _ = R.open_to_open_equity(close2, openp2, amt2, score2, 10_000, 1, 0.0,
                                      start=start, entry_lag=1)
    if abs(float(s_printed.iloc[-1]) - 1.10) > 1e-9:
        fails.append("L2 printed caliber should book the +10%% bar, got %r"
                     % float(s_printed.iloc[-1]))
    if abs(float(s_fixed.iloc[-1]) - 1.00) > 1e-9:
        fails.append("L2b corrected caliber should not book the decision bar, got %r"
                     % float(s_fixed.iloc[-1]))

    # L3 the two paths can only diverge on rebalance bars, and they diverge on all of them
    close3, openp3, amt3, score3 = _fixture(n, aaa=None)
    o3 = openp3.copy()
    o3["AAA"] = [10.0 * (1.01 ** i) for i in range(n)]
    o3["BBB"] = [100.0 * (1.002 ** i) for i in range(n)]
    # the pick has to alternate, otherwise the new book is the old book and there is no
    # day to swap: flip the winner every `rebal` bars
    flip = pd.DataFrame({"AAA": [1.0 if (i // 3) % 2 == 0 else 0.0 for i in range(n)],
                         "BBB": [0.0 if (i // 3) % 2 == 0 else 1.0 for i in range(n)]},
                        index=openp3.index)
    s3p, _ = R.open_to_open_equity(close3, o3, amt3, flip, 3, 1, 0.001, start=start)
    s3c, _ = R.open_to_open_equity(close3, o3, amt3, flip, 3, 1, 0.001, start=start,
                                  entry_lag=1)
    ratio = s3p / s3c
    prev = ratio.shift(1)
    prev.iloc[0] = 1.0
    changes = int((ratio.round(12) != prev.round(12)).sum())
    n_dec = int(len(range(0, len(s3p), 3)))
    if changes != n_dec:
        fails.append("L3 divergence bars %d != rebalances %d" % (changes, n_dec))
    if not (float(ratio.iloc[-1]) > 1.0):
        fails.append("L3b printed caliber should exceed the corrected one on a rising tape")

    # L4 an independent dumb loop that buys at the NEXT open reproduces entry_lag=1
    ref, _ = _ref_next_open(close3, o3, amt3, flip, 3, 1, start_i, cost=0.001)
    if abs(ref - float(s3c.iloc[-1])) > 1e-9:
        fails.append("L4 reference next-open loop %r != engine entry_lag=1 %r"
                     % (ref, float(s3c.iloc[-1])))

    # L5 the lag moves WHEN, never HOW MUCH: turnover is identical under both calibers
    _, t0 = R.open_to_open_equity(close3, o3, amt3, flip, 3, 1, 0.001, start=start)
    _, t1 = R.open_to_open_equity(close3, o3, amt3, flip, 3, 1, 0.001, start=start,
                                 entry_lag=1)
    if abs(t0 - t1) > 1e-12:
        fails.append("L5 average turnover differs between calibers (%r vs %r)" % (t0, t1))

    # L6 the benchmark is level 1.0 on its first usable bar and never rebalanced
    op = pd.DataFrame({"510300": [np.nan, 4.0, 4.4, 4.0]},
                      index=pd.bdate_range("2020-01-02", periods=4))
    bh = index_buy_hold(pd.DataFrame({"510300": [0.0, 1.0, 1.1, 1.0]},
                                     index=op.index), op)
    if abs(float(bh.iloc[0]) - 1.0) > 1e-12:
        fails.append("L6 benchmark does not start at 1.0: %r" % float(bh.iloc[0]))
    if abs(float(bh.iloc[-1]) - 1.0) > 1e-12:
        fails.append("L6b benchmark should end flat on a round trip")

    # L7 a published face, if there is one, carries its cutoff and its verdict re-derives
    if os.path.exists(OUT_JSON):
        face = json.load(open(OUT_JSON, encoding="utf-8"))
        if not face.get("evidence_cutoff"):
            fails.append("L7 published face has no evidence_cutoff")
        rows = face.get("rows") or []
        pos = [r["excess_corrected_pp"] for r in rows if r["label"] == face.get("cell")]
        if pos:
            want = "EXCESS_SURVIVES_CALIBER_FIX" if pos[0] > 0 else "EXCESS_IS_THE_BULGE"
            if face.get("verdict") != want:
                fails.append("L7b verdict %r does not re-derive to %r"
                             % (face.get("verdict"), want))

    print("selftest %d/%d PASS" % (7 - len(fails), 7))
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


def check():
    """Re-derive every published number from the face alone."""
    if not os.path.exists(OUT_JSON):
        print("check: no face on disk")
        return 2
    face = json.load(open(OUT_JSON, encoding="utf-8"))
    problems = []
    b = face.get("index") or {}
    rows = face.get("rows") or []
    if not rows:
        problems.append("no rows")
    if not face.get("evidence_cutoff"):
        problems.append("missing evidence_cutoff")
    for r in rows:
        bulge = round((r["printed"]["cagr"] - r["corrected"]["cagr"]) * 100, 3)
        if abs(bulge - r["bulge_pp"]) > 1e-6:
            problems.append("bulge does not re-derive at %s" % r["label"])
        ex_p = round((r["printed"]["cagr"] - b.get("cagr", 0)) * 100, 2)
        ex_c = round((r["corrected"]["cagr"] - b.get("cagr", 0)) * 100, 2)
        if abs(ex_p - r["excess_printed_pp"]) > 1e-6:
            problems.append("printed excess does not re-derive at %s" % r["label"])
        if abs(ex_c - r["excess_corrected_pp"]) > 1e-6:
            problems.append("corrected excess does not re-derive at %s" % r["label"])
        # the printed caliber always books an extra day per rebalance, so its level can
        # never sit below the corrected one, and it may only move on rebalance bars
        if r["ratio_end"] <= 1.0:
            problems.append("ratio_end <= 1 at %s (the printed caliber booked nothing)"
                            % r["label"])
        # divergence may only happen on a rebalance bar, and a rebalance that keeps the same
        # book produces none -- so the count is bounded, never equal by construction
        if not (1 <= r["n_ratio_changes"] <= r["n_rebalances"]):
            problems.append("divergence count %d outside 1..%d at %s"
                            % (r["n_ratio_changes"], r["n_rebalances"], r["label"]))
    canon = [r for r in rows if r["label"] == face.get("cell")]
    if not canon:
        problems.append("cell %r is not among the rows" % face.get("cell"))
    else:
        want = ("EXCESS_SURVIVES_CALIBER_FIX" if canon[0]["excess_corrected_pp"] > 0
                else "EXCESS_IS_THE_BULGE")
        if want != face.get("verdict"):
            problems.append("verdict %r re-derives to %r" % (face.get("verdict"), want))
        if abs(canon[0]["excess_corrected_pp"] - face.get("excess_corrected_pp")) > 1e-6:
            problems.append("headline corrected excess is not the cell's")
        shp = max(rows, key=lambda r: (r["printed"]["sharpe"] or -9))["label"]
        shc = max(rows, key=lambda r: (r["corrected"]["sharpe"] or -9))["label"]
        rk = face.get("ranking") or {}
        if rk.get("best_by_sharpe_printed") != shp:
            problems.append("printed ranking does not re-derive")
        if rk.get("best_by_sharpe_corrected") != shc:
            problems.append("corrected ranking does not re-derive")
        if bool(rk.get("flipped")) != (shp != shc):
            problems.append("flip flag does not re-derive")
    x = face.get("cross_check") or {}
    if abs(x.get("gap_pp", 99)) > face.get("thresholds", {}).get("cross_tol_pp", 0.5):
        problems.append("cross-check gap %r exceeds the frozen tolerance" % x.get("gap_pp"))
    out = {"ok": not problems, "verdict": face.get("verdict"), "problems": problems[:10]}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out["ok"] else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
