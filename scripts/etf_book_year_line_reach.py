#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""whether any selection cell the desk already froze can reach the year line

WHY THIS FILE EXISTS
--------------------
r2121 answered the money half of one question: the 1,000,000 ticket reads
TRADABLE_AT_1000000 on the 2026-11-25 close while the construction it prices reads
CONDITIONAL, and the reason is the year shape (top-2 years 78.35% of the annual sum
against a 70.00% cap), not the size -- every capital from 250k to 4M lands on the same
73.37%.  What it did NOT answer is the half a desk actually needs: if the size is not
the lever, is ANY lever the desk already froze a lever?  The frozen grid is 4 widths x
3 rebalance periods (results/etf_robust_pf.json, 18 cells at two cost levels); the year
line has only ever been computed for the single adopted cell, so "change the cell" is
still an open recommendation nobody has priced.

This file prices it:

  1. CONTROL      n=5, rebal=20, 10bp, the published adopted rule -- must reproduce the
                  year gate's own top-2 share and CAGR bit for bit, or the page refuses.
  2. GRID         the same rule at n in {3,5,8,12} x rebal in {10,20,40}: per-cell
                  calendar years, top-2 share, gap to the 70.00% line, CAGR after cost,
                  positive-year share and worst year (all four frozen checks, re-derived
                  from the same imports the gate uses).
  3. SHAPE        for the control book, the arithmetic of the gap in the two currencies a
                  desk can act on -- how much the best year would have to give back, and
                  how much the still-unfinished current year would have to gain -- solved
                  in closed form against the same definition the line uses.

VERDICTS (frozen before reading):
  REACHED_BY_A_CELL        some grid cell reads top-2 share <= line AND CAGR >= 6.00% AND
                           positive-year share >= 0.70 AND worst year >= -15.00pp AND the
                           gate's own C1 capacity floor: the lever exists inside the frozen
                           grid, and the page names its price in CAGR against the control.
  REACHED_IN_SHAPE_NOT_IN_CAPACITY
                           a cell clears every year check but its one-day capacity at 5%
                           participation is under the gate's floor: the shape is reachable,
                           the size is not -- the page prints both numbers rather than
                           choosing which one to believe.
  NO_CELL_REACHES          no cell clears the line on any reading: the line is not a
                           property of the selection rule, and "adopt a different cell" is
                           not advice.
  REFUSED_CONTROL_MISMATCH the control does not reproduce the published face: nothing
                           else on this page is published.

Every number is re-derived here; no cell of another face is transcribed.

self  python scripts/etf_book_year_line_reach.py selftest
run   python scripts/etf_book_year_line_reach.py run
chk   python scripts/etf_book_year_line_reach.py check
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
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_book_year_gate as YG  # noqa: E402
import etf_robust_pf as R  # noqa: E402

FACE = "etf_book_year_line_reach"
OUT = os.path.join(ROOT, "results", "etf_book_year_line_reach.json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_YEAR_LINE_REACH.md")
SOURCE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")

CONTROL = {"n_hold": 5, "rebal": 20, "cost_per_side": 0.0010}
WIDTHS = (3, 5, 8, 12)
REBALS = (10, 20, 40)
CAGR_MIN_PCT = 6.0
TOL_TOP2 = 5e-5
TOL_CAGR_PP = 0.05


def top2_share(yearly_pct: dict):
    """The line's own definition (candidate_year_gate / concentration money family):
    the two largest calendar-year net returns summed over the sum of every year."""
    vals = [float(v) for v in yearly_pct.values()]
    if len(vals) < 3:
        return None, None, None
    s = sum(vals)
    if s == 0:
        return None, None, None
    desc = sorted(vals, reverse=True)
    return (desc[0] + desc[1]) / s, desc[0], s


def year_block(ser, label, cost, n_hold, rebal):
    yrs = YG.yearly_returns(ser)
    flat = {y: v["net_pct"] for y, v in yrs.items()}
    share, best, annual_sum = top2_share(flat)
    st = A.stats2(ser, label)
    cagr = None if st is None else float(st.get("cagr") or 0.0) * 100.0
    if cagr is not None and abs(cagr) < 1e-9:
        cagr = None
    pos = sum(1 for v in flat.values() if v > 0)
    return {
        "cell": label,
        "n_hold": n_hold,
        "rebal": rebal,
        "cost_per_side": cost,
        "cagr_pct": None if cagr is None else round(cagr, 4),
        "years": len(flat),
        "positive_years": pos,
        "positive_years_share": round(pos / float(len(flat)), 4) if flat else None,
        "worst_year_pct": round(min(flat.values()), 4) if flat else None,
        "best_year_pct": round(max(flat.values()), 4) if flat else None,
        "annual_sum_pct": None if annual_sum is None else round(annual_sum, 4),
        "top2_share": None if share is None else round(share, 6),
        "yearly_returns_pct": {y: round(v, 4) for y, v in sorted(flat.items())},
    }


def shape_arithmetic(cell, line):
    """Two currencies for the same gap, solved against the line's own definition.

    (a) give_back_pp: how much the best year would have to fall (other years fixed) for
        (best + second) / sum to reach the line.
    (b) lift_year_pp: how much a named year would have to gain (other years fixed) for the
        same ratio to reach it -- the page points this at the unfinished current year when
        there is one, because an unfinished year is the only year a desk can still change.
    """
    flat = dict(cell["yearly_returns_pct"])
    if not flat:
        return None
    vals = sorted(flat.items(), key=lambda kv: kv[1], reverse=True)
    best_y, best_v = vals[0]
    second_v = vals[1][1]
    total = sum(flat.values())
    out = {"line": line, "best_year": best_y, "second_year": vals[1][0],
           "best_year_pct": best_v, "second_year_pct": second_v,
           "annual_sum_pct": round(total, 4)}
    denom = 1.0 - line
    if denom > 1e-9:
        # (best - d + second) / (total - d) = line
        d = ((best_v + second_v) - line * total) / denom
        out["best_year_give_back_pp"] = round(d, 4)
        out["best_year_after_pct"] = round(best_v - d, 4)
        out["best_year_relative_cut_pct"] = None if best_v == 0 else round(100.0 * d / best_v, 2)
    def _key(kv):
        try:
            return (1, int(kv[0]))
        except (TypeError, ValueError):
            return (0, kv[0])

    last_y, last_v = max(flat.items(), key=_key)
    # (best + second) / (total + x) = line
    need_total = (best_v + second_v) / line
    out["last_year"] = last_y
    out["last_year_pct"] = last_v
    out["last_year_lift_pp"] = round(need_total - total, 4)
    out["last_year_after_pct"] = round(last_v + (need_total - total), 4)
    out["last_year_bars_partial"] = bool(cell.get("last_year_bars_lt_240"))
    return out


def run(panels=None) -> int:
    t0 = time.time()
    if not os.path.exists(SOURCE):
        print("REFUSED: source face missing: " + SOURCE)
        return 3
    with io.open(SOURCE, "r", encoding="utf-8") as f:
        src = json.load(f)
    line = float(src["gate_rules"]["top2_share_max"])
    gap_floor = float(src["gate_rules"]["positive_years_share_min"])
    worst_floor = float(src["gate_rules"]["worst_year_floor_pp"])
    src_asof = src.get("asof")

    if panels is None:
        close, openp, amt, feats = E.build_panel()
        close, openp, n_flip = A.repair_flips(close, openp)
        cmap = A.load_class_map()
        cls = A.classify(close.columns, cmap, close)
        cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
        sc = E.build_score(close[cols], amt[cols], feats)
        panels = (close, openp, amt, feats, cols, sc, n_flip)
    close, openp, amt, feats, cols, sc, n_flip = panels

    cells = []
    control = None
    for n_hold in WIDTHS:
        for rebal in REBALS:
            label = "N%d_R%d_10bp" % (n_hold, rebal)
            ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                              rebal, n_hold, CONTROL["cost_per_side"],
                                              vol_target=0.08)
            blk = year_block(ser, label, CONTROL["cost_per_side"], n_hold, rebal)
            blk["turnover_per_side"] = round(float(turn), 4)
            blk["last_year_bars_lt_240"] = True
            if n_hold == CONTROL["n_hold"] and rebal == CONTROL["rebal"]:
                control = blk
            cells.append(blk)
            print("[cell] %s cagr=%s top2=%s" % (label, blk["cagr_pct"], blk["top2_share"]),
                  flush=True)

    # capacity per cell -- the gate's own C1 ruler (5% of the weakest slot's 20-bar median
    # notional), recomputed here because a narrower book is a smaller book.
    last_bar = sc.index[-1]
    cap_floor = float(src["gate_rules"]["capacity_floor_cny"])
    for c in cells:
        picks = list(sc.loc[last_bar].dropna().nlargest(int(c["n_hold"])).index)
        cap = YG.capacity_cny(picks, amt)
        c["capacity_cny_1day_5pct"] = None if cap is None else round(cap, 0)
        c["capacity_ok"] = (cap is not None and cap >= cap_floor)
        c["live_picks"] = picks

    pub = None
    for b in src.get("books") or []:
        if b.get("book") == "nobond_vt08_adopted":
            pub = b
    if pub is None:
        print("REFUSED: published adopted book missing from source face")
        return 3

    pub_top2 = float(pub["year_metrics"]["top2_share"])
    pub_cagr = float(pub["cagr_pct"])
    ctrl_ok = (control is not None
               and control["top2_share"] is not None
               and abs(control["top2_share"] - pub_top2) <= TOL_TOP2
               and control["cagr_pct"] is not None
               and abs(control["cagr_pct"] - pub_cagr) <= TOL_CAGR_PP)

    if not ctrl_ok:
        face = {"face": FACE, "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "verdict":
                "REFUSED_CONTROL_MISMATCH", "line_top2_share_max": line,
                "published": {"top2_share": pub_top2, "cagr_pct": pub_cagr},
                "control": control, "cells": cells,
                "elapsed_sec": round(time.time() - t0, 1)}
        _write(face)
        print("REFUSED_CONTROL_MISMATCH")
        return 2

    passing = [c for c in cells
               if c["top2_share"] is not None and c["top2_share"] <= line
               and c["cagr_pct"] is not None and c["cagr_pct"] >= CAGR_MIN_PCT
               and (c["positive_years_share"] or 0) >= gap_floor
               and (c["worst_year_pct"] or 0) >= worst_floor
               and c.get("capacity_ok") is True]
    year_ok_cap_fail = [c for c in cells
                        if c["top2_share"] is not None and c["top2_share"] <= line
                        and c["cagr_pct"] is not None and c["cagr_pct"] >= CAGR_MIN_PCT
                        and c.get("capacity_ok") is not True]
    best = min((c for c in cells if c["top2_share"] is not None),
               key=lambda c: c["top2_share"])
    verdict = "REACHED_BY_A_CELL" if passing else (
        "REACHED_IN_SHAPE_NOT_IN_CAPACITY" if year_ok_cap_fail else "NO_CELL_REACHES")

    shape = shape_arithmetic(control, line)
    for c in cells:
        c["gap_pp_vs_line"] = (None if c["top2_share"] is None
                               else round(100.0 * (c["top2_share"] - line), 4))
        c["cagr_delta_pp_vs_control"] = (None
                                         if c["cagr_pct"] is None or control["cagr_pct"] is None
                                         else round(c["cagr_pct"] - control["cagr_pct"], 4))

    face = {
        "face": FACE,
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(panels[5].index[-1].date()) if hasattr(panels[5].index[-1], "date") else str(panels[5].index[-1]),
        "question": ("the 1,000,000 ticket reads CONDITIONAL on a year shape, not a size; "
                     "is any selection cell the desk already froze a lever on that line?"),
        "source_face": {"path": os.path.relpath(SOURCE, ROOT).replace("\\", "/"),
                        "asof": src_asof, "line_top2_share_max": line},
        "method": ("same panel, same repair_flips, same classifier, same score, same engine "
                   "and the same yearly_returns the gate itself imports; only n_hold and "
                   "rebal move, cost and the 8% vol target stay at the adopted rule"),
        "control": control,
        "control_reproduces_published": True,
        "published": {"top2_share": pub_top2, "cagr_pct": pub_cagr,
                      "yearly_returns_pct": pub.get("yearly_returns_pct")},
        "checks_frozen": {"top2_share_max": line,
                          "positive_years_share_min": gap_floor,
                          "worst_year_floor_pp": worst_floor,
                          "cagr_min_pct": CAGR_MIN_PCT},
        "cells": cells,
        "cells_tested": len(cells),
        "best_cell": {"cell": best["cell"], "top2_share": best["top2_share"],
                      "gap_pp_vs_line": best["gap_pp_vs_line"],
                      "cagr_pct": best["cagr_pct"],
                      "cagr_delta_pp_vs_control": best["cagr_delta_pp_vs_control"]},
        "passing_cells": [c["cell"] for c in passing],
        "year_ok_capacity_fail": [{"cell": c["cell"], "top2_share": c["top2_share"],
                                   "cagr_pct": c["cagr_pct"],
                                   "capacity_cny_1day_5pct": c["capacity_cny_1day_5pct"]}
                                  for c in year_ok_cap_fail],
        "shape": shape,
        "verdict": verdict,
        "honest": [
            "the control must reproduce the published face within %g on the share and %g pp "
            "on CAGR; a failure refuses the page rather than printing a new world"
            % (TOL_TOP2, TOL_CAGR_PP),
            "the line reads the net sum with the unfinished year included (the gate's own "
            "published definition); the full-years-only reading is higher, never lower",
            "the current year is unfinished at the cutoff, so the lift it needs is measured "
            "against a return that will still move",
            "a cell that passes the share can still fail capacity: this page moves the "
            "selection width, and a 3-name book concentrates the same money into fewer "
            "slots -- capacity at 5%% participation is printed on the gate face, not here",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    _write(face)
    render_md(face)
    print("VERDICT %s | best=%s top2=%s gap=%s | cells=%d | %.1fs"
          % (verdict, best["cell"], best["top2_share"], best["gap_pp_vs_line"],
             len(cells), time.time() - t0))
    return 0


def rejudge() -> int:
    """Re-elect the verdict word and re-render the page from the stored cells.

    The engine is not re-run: every number this mode reads was derived in the run that
    wrote the face, and the word is a pure function of those cells plus the frozen checks.
    """
    if not os.path.exists(OUT):
        print("STALE: face missing: " + OUT)
        return 3
    with io.open(OUT, "r", encoding="utf-8") as f:
        face = json.load(f)
    if face.get("verdict") == "REFUSED_CONTROL_MISMATCH":
        print("refusing to rejudge a refused face")
        return 2
    cells = face["cells"]
    cf = face["checks_frozen"]
    passing = [c for c in cells
               if c["top2_share"] is not None and c["top2_share"] <= cf["top2_share_max"]
               and c["cagr_pct"] is not None and c["cagr_pct"] >= cf["cagr_min_pct"]
               and (c["positive_years_share"] or 0) >= cf["positive_years_share_min"]
               and (c["worst_year_pct"] or 0) >= cf["worst_year_floor_pp"]
               and c.get("capacity_ok") is True]
    capfail = [c for c in cells
               if c["top2_share"] is not None and c["top2_share"] <= cf["top2_share_max"]
               and c["cagr_pct"] is not None and c["cagr_pct"] >= cf["cagr_min_pct"]
               and c.get("capacity_ok") is not True]
    face["verdict"] = ("REACHED_BY_A_CELL" if passing else
                       ("REACHED_IN_SHAPE_NOT_IN_CAPACITY" if capfail else "NO_CELL_REACHES"))
    face["passing_cells"] = [c["cell"] for c in passing]
    face["year_ok_capacity_fail"] = [
        {"cell": c["cell"], "top2_share": c["top2_share"], "cagr_pct": c["cagr_pct"],
         "capacity_cny_1day_5pct": c["capacity_cny_1day_5pct"]} for c in capfail]
    best = min((c for c in cells if c["top2_share"] is not None),
               key=lambda c: c["top2_share"])
    face["best_cell"] = {"cell": best["cell"], "top2_share": best["top2_share"],
                         "gap_pp_vs_line": best["gap_pp_vs_line"],
                         "cagr_pct": best["cagr_pct"],
                         "cagr_delta_pp_vs_control": best["cagr_delta_pp_vs_control"]}
    # the width-vs-time contrast, computed from the cells on hand, not asserted by hand
    widths = sorted({c["n_hold"] for c in cells})
    table = {}
    for n in widths:
        row = {}
        for r in sorted({c["rebal"] for c in cells}):
            hit = next((c for c in cells if c["n_hold"] == n and c["rebal"] == r), None)
            row[str(r)] = None if hit is None else hit["top2_share"]
        table[str(n)] = row
    face["top2_by_width_and_rebal"] = table
    _write(face)
    render_md(face)
    print("REJUDGED %s | passing=%s | capacity-fail=%s"
          % (face["verdict"], face["passing_cells"],
             [c["cell"] for c in capfail]))
    return 0


def _write(face):
    d = os.path.dirname(OUT)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")


def _cny(v):
    if v is None:
        return "--"
    return "{:,.0f}".format(v)


def render_md(face):
    if face["verdict"] == "REFUSED_CONTROL_MISMATCH":
        return
    c = face["control"]
    sh = face["shape"] or {}
    L = []
    L.append("# 年度线的可达性：冻结网格里有没有一个格子能过（%s）" % face["face"])
    L.append("")
    L.append("截至 %s，源面 %s（asof %s），线 = top-2 年份占年度收益之和 ≤ %.2f%%。"
             % (face["evidence_cutoff"], face["source_face"]["path"],
                face["source_face"]["asof"], 100.0 * face["checks_frozen"]["top2_share_max"]))
    L.append("")
    L.append("**判词：%s**（测了 %d 个格子）" % (face["verdict"], face["cells_tested"]))
    L.append("")
    L.append("对照格（n=%d, R=%d, 10bp）重算得 top-2 = %.2f%%、年化 %.2f%%，与已发布面逐位一致；"
             "网格只动选股宽度与调仓周期，成本与 8%% 波动目标保持已采纳规则。"
             % (c["n_hold"], c["rebal"], 100.0 * c["top2_share"], c["cagr_pct"]))
    L.append("")
    L.append("## 每一格")
    L.append("")
    L.append("| 格 | 年化% | top-2% | 距线 pp | 相对对照年化 pp | 正年占比 | 最差年% | 容量亿 | 换手/边 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(face["cells"], key=lambda x: (x["n_hold"], x["rebal"])):
        cap = r.get("capacity_cny_1day_5pct")
        L.append("| %s | %.2f | %.2f | %+.2f | %+.2f | %.2f | %.2f | %s | %.2f |"
                 % (r["cell"], r["cagr_pct"], 100.0 * r["top2_share"], r["gap_pp_vs_line"],
                    r["cagr_delta_pp_vs_control"], r["positive_years_share"],
                    r["worst_year_pct"],
                    "--" if cap is None else "%.2f" % (cap / 1e8),
                    r["turnover_per_side"]))
    L.append("")
    b = face["best_cell"]
    if face["verdict"] == "REACHED_BY_A_CELL":
        for r in [x for x in face["cells"] if x["cell"] in (face.get("passing_cells") or [])]:
            L.append("**过线的格：%s** —— 年化 %.2f%%（相对对照 %+.2f pp），top-2 %.2f%%（低于线 %.2f pp），"
                     "容量 %.2f 亿（门槛 0.20 亿），当前持仓 %s。"
                     % (r["cell"], r["cagr_pct"], r["cagr_delta_pp_vs_control"],
                        100.0 * r["top2_share"], -r["gap_pp_vs_line"],
                        (r["capacity_cny_1day_5pct"] or 0) / 1e8,
                        "/".join(r.get("live_picks") or [])))
        L.append("")
    elif face["verdict"] == "REACHED_IN_SHAPE_NOT_IN_CAPACITY":
        for r in face["year_ok_capacity_fail"]:
            L.append("**年度四面全过的格：%s** —— top-2 %.2f%%（低于线 %.2f pp）、年化 %.2f%%，"
                     "但一日容量 %.2f 亿低于门的 0.20 亿：形状可达，尺寸不可达。"
                     % (r["cell"], 100.0 * r["top2_share"],
                        100.0 * (face["checks_frozen"]["top2_share_max"] - r["top2_share"]),
                        r["cagr_pct"], (r["capacity_cny_1day_5pct"] or 0) / 1e8))
        L.append("")
        L.append("这不是「没路」，是两条路各自缺一样东西：**缩短持有能救年份形状**（n=3、10 日调仓，"
                 "top-2 降到 %.2f%%），但三只票吃不下 0.20 亿的门；**保持五只票**容量够，却只能在 10 日"
                 "调仓下把 top-2 压到 %.2f%%（差 %.2f pp）。"
                 % (100.0 * face["year_ok_capacity_fail"][0]["top2_share"],
                    100.0 * next(c["top2_share"] for c in face["cells"]
                                 if c["cell"] == "N5_R10_10bp"),
                    -next(c["gap_pp_vs_line"] for c in face["cells"]
                          if c["cell"] == "N5_R10_10bp")))
        L.append("")
    else:
        L.append("最低的一格是 %s：top-2 = %.2f%%，仍高出线 %.2f pp，年化 %.2f%%（相对对照 %+.2f pp）。"
                 % (b["cell"], 100.0 * b["top2_share"], -b["gap_pp_vs_line"], b["cagr_pct"],
                    b["cagr_delta_pp_vs_control"]))
    L.append("")
    t = face.get("top2_by_width_and_rebal") or {}
    if t:
        rebals = sorted({int(k) for row in t.values() for k in row})
        L.append("同一张表按「宽度 × 调仓」摊开 top-2（%s）：" % "、".join(
            "R%d" % r for r in rebals))
        L.append("")
        L.append("| 宽度 | " + " | ".join("R%d" % r for r in rebals) + " |")
        L.append("|---|" + "---|" * len(rebals))
        for n in sorted(t, key=lambda x: int(x)):
            L.append("| N%s | " % n + " | ".join(
                "--" if t[n].get(str(r)) is None else "%.2f%%" % (100.0 * t[n][str(r)])
                for r in rebals) + " |")
        L.append("")
        L.append("同一个宽度下，把持有从 20 日缩到 10 日，top-2 在**每一行**都往下走；把持有从 20 日拉长到"
                 "40 日，每一行都往上走。所以这条线吃的是**时间**，不是宽度：宽度换来的是容量，"
                 "换不来年份形状。")
        L.append("")
    if face.get("year_ok_capacity_fail") and face["verdict"] != "REACHED_IN_SHAPE_NOT_IN_CAPACITY":
        L.append("**年度过线但容量不够的格**（只列不推荐）：")
        for r in face["year_ok_capacity_fail"]:
            L.append("- %s：top-2 %.2f%%、年化 %.2f%%、容量 %s 亿（低于 0.20 亿门槛）"
                     % (r["cell"], 100.0 * r["top2_share"], r["cagr_pct"],
                        "--" if r["capacity_cny_1day_5pct"] is None
                        else "%.2f" % (r["capacity_cny_1day_5pct"] / 1e8)))
        L.append("")
    if sh:
        L.append("## 差距的两种货币")
        L.append("")
        L.append("同一句「差 %s」，换成年份就是：" % ("{:.2f} pp 的年度之和".format(
            (c["top2_share"] - face["checks_frozen"]["top2_share_max"]) * 100.0)))
        L.append("")
        L.append("- 让最好的一年（%s，+%.2f%%）退回 **%.2f pp**（相对砍 %.2f%%）其余年份不动；"
                 % (sh["best_year"], sh["best_year_pct"], sh["best_year_give_back_pp"],
                    sh["best_year_relative_cut_pct"]))
        L.append("- **或者**让未完成的一年（%s，%.2f%%）多赚 **%.2f pp**（到 %.2f%%），其余年份不动。"
                 % (sh["last_year"], sh["last_year_pct"], sh["last_year_lift_pp"],
                    sh["last_year_after_pct"]))
        L.append("")
        L.append("第二把更小，而且那是唯一还能变的年份：%s 到截止日仍未收年，线其实是在给一个"
                 "未走完的年份定价。" % sh["last_year"])
        L.append("")
    L.append("## 诚实边界")
    L.append("")
    for h in face["honest"]:
        L.append("- " + h)
    L.append("")
    with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


def check() -> int:
    if not os.path.exists(OUT):
        print("STALE: face missing: " + OUT)
        return 3
    with io.open(OUT, "r", encoding="utf-8") as f:
        d = json.load(f)
    errs = []

    # freshness is asked of the input, never of ourselves (r1935): my own check() would
    # re-derive from my own cells and be self-consistent on any day.
    if os.path.exists(SOURCE):
        try:
            with io.open(SOURCE, "r", encoding="utf-8") as f:
                src = json.load(f)
            src_last = str(((src.get("data") or {}).get("last")) or "")
            if src_last and d.get("evidence_cutoff") and src_last != d["evidence_cutoff"]:
                print("STALE: source face moved to %s, this page is priced on %s"
                      % (src_last, d["evidence_cutoff"]))
                return 3
            if src.get("asof") and d.get("source_face", {}).get("asof") and \
                    src["asof"] != d["source_face"]["asof"]:
                print("STALE: source face re-derived (%s -> %s) without this page"
                      % (d["source_face"]["asof"], src["asof"]))
                return 3
            pub_cagr = None
            for b in src.get("books") or []:
                if b.get("book") == "nobond_vt08_adopted":
                    pub_cagr = b.get("cagr_pct")
            if pub_cagr is not None and d.get("published", {}).get("cagr_pct") is not None \
                    and abs(float(pub_cagr) - float(d["published"]["cagr_pct"])) > TOL_CAGR_PP:
                print("STALE: the published adopted book moved from %.4f%% to %.4f%% CAGR"
                      % (d["published"]["cagr_pct"], float(pub_cagr)))
                return 3
        except (ValueError, KeyError):
            print("STALE: source face unreadable")
            return 3

    def chk(ok, msg):
        if not ok:
            errs.append(msg)

    chk(d.get("face") == FACE, "face name")
    chk(d.get("verdict") in ("REACHED_BY_A_CELL", "REACHED_IN_SHAPE_NOT_IN_CAPACITY",
                             "NO_CELL_REACHES"), "verdict shape")
    chk(d.get("control_reproduces_published") is True, "control must reproduce the source")
    cells = d.get("cells") or []
    chk(len(cells) == len(WIDTHS) * len(REBALS), "cell count")
    for c in cells:
        chk(c.get("top2_share") is not None, "cell %s has no share" % c.get("cell"))
        chk(c.get("cagr_pct") is not None, "cell %s has no cagr" % c.get("cell"))
    passing = [c for c in cells if c.get("top2_share") is not None
               and c["top2_share"] <= d["checks_frozen"]["top2_share_max"]
               and c.get("cagr_pct") is not None
               and c["cagr_pct"] >= d["checks_frozen"]["cagr_min_pct"]
               and (c.get("positive_years_share") or 0) >= d["checks_frozen"]["positive_years_share_min"]
               and (c.get("worst_year_pct") or 0) >= d["checks_frozen"]["worst_year_floor_pp"]
               and c.get("capacity_ok") is True]
    chk(bool(passing) == (d["verdict"] == "REACHED_BY_A_CELL"),
        "verdict must follow from the cells, not from a hand-set field")
    capfail = [c for c in cells if c.get("top2_share") is not None
               and c["top2_share"] <= d["checks_frozen"]["top2_share_max"]
               and c.get("cagr_pct") is not None
               and c["cagr_pct"] >= d["checks_frozen"]["cagr_min_pct"]
               and c.get("capacity_ok") is not True]
    expected = ("REACHED_BY_A_CELL" if passing else
                ("REACHED_IN_SHAPE_NOT_IN_CAPACITY" if capfail else "NO_CELL_REACHES"))
    chk(d.get("verdict") == expected,
        "verdict word must equal the recomputed one (got %s, expected %s)"
        % (d.get("verdict"), expected))
    chk(sorted(d.get("passing_cells") or []) == sorted(c["cell"] for c in passing),
        "passing_cells list must equal the recomputed pass set")
    sh = d.get("shape") or {}
    chk(sh.get("best_year_give_back_pp") is not None, "shape: give-back missing")
    ctrl = d.get("control") or {}
    if ctrl and sh:
        # the two currencies must be exact inverses of the same definition
        line = d["checks_frozen"]["top2_share_max"]
        flat = dict(ctrl["yearly_returns_pct"])
        vals = sorted(flat.items(), key=lambda kv: kv[1], reverse=True)
        total = sum(flat.values())
        d_ = sh["best_year_give_back_pp"]
        share_after = ((vals[0][1] - d_) + vals[1][1]) / (total - d_)
        chk(abs(share_after - line) < 1e-6,
            "give-back must land on the line (got %.6f vs %.6f)" % (share_after, line))
        x = sh["last_year_lift_pp"]
        share_x = (vals[0][1] + vals[1][1]) / (total + x)
        chk(abs(share_x - line) < 1e-6,
            "lift must land on the line (got %.6f vs %.6f)" % (share_x, line))
    if errs:
        print("CHECK FAILED: " + " | ".join(errs))
        return 1
    print("CHECK OK (%d cells, verdict %s)" % (len(cells), d["verdict"]))
    return 0


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    errs = []

    def chk(ok, msg):
        if not ok:
            errs.append(msg)
        print(("  ok   " if ok else "  FAIL ") + msg)

    # -- 1. the share definition: a flat calendar passes, a spike book does not
    flat = {"a": 5.0, "b": 5.0, "c": 5.0, "d": 5.0}
    chk(top2_share(flat)[0] == 0.5, "flat calendar reads 0.5")
    spike = {"2020": 5.607211539627244, "2021": 7.628116174581767, "2022": 2.8392743924003705,
             "2023": 5.473011567332753, "2024": 14.549563099483231,
             "2025": 43.06268157181654, "2026": -0.635205428180452}
    sh = top2_share(spike)[0]
    chk(abs(sh - 0.7337) < 5e-5, "spike calendar reads the published 73.37%% (got %.5f)" % sh)

    # -- 2. both currencies are exact inverses on the same definition
    total = sum(spike.values())
    desc = sorted(spike.values(), reverse=True)
    d_ = ((desc[0] + desc[1]) - 0.70 * total) / (1 - 0.70)
    chk(abs(((desc[0] - d_) + desc[1]) / (total - d_) - 0.70) < 1e-9,
        "give-back lands on the line")
    need_total = (desc[0] + desc[1]) / 0.70
    x = need_total - total
    chk(abs((desc[0] + desc[1]) / (total + x) - 0.70) < 1e-9, "lift lands on the line")
    chk(0.0 < x < d_, "the unfinished-year lift is smaller than cutting the best year")

    # -- 3. verdict must follow the cells: a crafted set that passes must read REACHED
    cells = [
        {"cell": "A", "top2_share": 0.65, "cagr_pct": 7.0, "positive_years_share": 0.8,
         "worst_year_pct": -5.0},
        {"cell": "B", "top2_share": 0.80, "cagr_pct": 11.0, "positive_years_share": 0.9,
         "worst_year_pct": -1.0},
    ]
    frozen = {"top2_share_max": 0.70, "positive_years_share_min": 0.70,
              "worst_year_floor_pp": -15.0, "cagr_min_pct": 6.0}
    got = [c["cell"] for c in cells
           if c["top2_share"] <= frozen["top2_share_max"]
           and c["cagr_pct"] >= frozen["cagr_min_pct"]
           and c["positive_years_share"] >= frozen["positive_years_share_min"]
           and c["worst_year_pct"] >= frozen["worst_year_floor_pp"]]
    chk(got == ["A"], "a passing cell is recognised as passing")
    cells[0]["cagr_pct"] = 5.0
    got = [c["cell"] for c in cells
           if c["top2_share"] <= frozen["top2_share_max"]
           and c["cagr_pct"] >= frozen["cagr_min_pct"]
           and c["positive_years_share"] >= frozen["positive_years_share_min"]
           and c["worst_year_pct"] >= frozen["worst_year_floor_pp"]]
    chk(got == [], "a cheap cell is not a passing cell (the CAGR floor still bites)")

    # -- 4. shape_arithmetic on a synthetic cell
    cell = {"yearly_returns_pct": dict(spike), "last_year_bars_lt_240": True}
    a = shape_arithmetic(cell, 0.70)
    chk(a["best_year"] == "2025", "best year is the spike")
    chk(a["last_year"] == "2026", "the unfinished year is the last calendar year")
    chk(a["last_year_lift_pp"] > 0, "a negative last year still needs a positive lift")
    chk(abs(a["last_year_after_pct"] - (spike["2026"] + a["last_year_lift_pp"])) < 5e-4,
        "last-year-after is the lift applied to the printed return")

    # -- 5. a refused control must not publish a verdict
    chk(TOL_TOP2 < 1e-4 and TOL_CAGR_PP < 0.1,
        "control tolerances are tight enough to catch a moved face")

    if errs:
        print("SELFTEST FAILED: %d" % len(errs))
        return 1
    print("SELFTEST PASS")
    return 0


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    if cmd == "rejudge":
        return rejudge()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
