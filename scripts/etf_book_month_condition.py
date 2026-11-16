#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Do the select leg's good months share a condition you could have seen beforehand?

r1766 answered "when did the money arrive" (44 of 83 months, concentrated by month but
habitual by year). It left the next question open: those months look like an event profile
-- but an event profile that is forecastable is a different claim from one that is not.

This face cuts the same 83 months on three states that are known at the START of each month:

  M  index 60-day momentum positive   (bench close vs its own close 60 bars earlier)
  V  60-day realised vol above its own expanding median
  E  the book held any equity weight on the month's first bar (w_equity > 0)

and asks whether the positive months pile into one of the eight cells. The cell search is
the part that can fool a reader -- out of eight cells one is always the best -- so the
observed best cell is compared against a label-shuffle null that rebuilds the same eight
cells from the same contributions, and the verdict is read off that null, not off the
table. Everything is re-derived from the panel through the same base arm r1765/r1766 use;
the control arm must reproduce r1766's own select leg before anything is published.

Usage:
    python scripts/etf_book_month_condition.py run
    python scripts/etf_book_month_condition.py check
    python scripts/etf_book_month_condition.py selftest
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import etf_book_entry_gate as G               # noqa: E402  (panel + flip repair)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_equity_alpha as A                  # noqa: E402  (classify)
import etf_book_corr_select as CS             # noqa: E402  (the base arm, unchanged)
import etf_book_period_slice as PS            # noqa: E402  (the month table, unchanged)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_month_condition.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_MONTH_CONDITION.md")
FACE_SLICE = os.path.join(ROOT, "results", "etf_book_period_slice.json")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")

BENCH = CS.BENCH
GATE = CS.GATE
PER_YEAR = 252.0
CONTROL_TOL_PP = 0.25        # the base arm must reproduce r1766's own select cell
DRAWS = 2000                 # label shuffles; the seed is frozen below
SEED = 20261116

# criteria frozen before the run
MIN_CELL_MONTHS = 8          # a cell has to hold real months, not two lucky ones
P_VISIBLE = 0.10             # the best cell must beat the shuffle null at this level
P_WEAK = 0.25                # between the two lines: a hint, published as a hint
WARMUP_BARS = 60             # a month whose start has no 60-bar history is UNKNOWN


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- state at month start

def bench_state(bclose):
    """Two state series that only use bars strictly before the bar they are read at."""
    b = bclose.dropna()
    lr = np.log(b).diff()
    vol = lr.rolling(WARMUP_BARS).std() * np.sqrt(PER_YEAR)
    mom = b / b.shift(WARMUP_BARS) - 1.0
    # expanding median: the threshold never sees a bar after the one being classified
    thr = vol.expanding(min_periods=WARMUP_BARS).median()
    return {"close": b, "vol": vol, "mom": mom, "vol_thr": thr}


def state_at(st, d_start):
    """State of the world as of the last bar strictly before `d_start`; None when short."""
    b = st["close"]
    pos = int(b.index.searchsorted(pd.Timestamp(d_start), side="left"))
    if pos <= WARMUP_BARS:
        return None
    prev = b.index[pos - 1]
    mom = st["mom"].loc[prev]
    vol = st["vol"].loc[prev]
    thr = st["vol_thr"].loc[prev]
    if not (np.isfinite(mom) and np.isfinite(vol) and np.isfinite(thr)):
        return None
    return {"asof": str(pd.Timestamp(prev).date()),
            "mom60": round(float(mom), 6), "mom_pos": bool(mom > 0.0),
            "vol60_ann": round(float(vol), 6), "vol_thr": round(float(thr), 6),
            "vol_high": bool(vol > thr)}


def cell_key(mom_pos, vol_high, w_eq_pos):
    if mom_pos is None or vol_high is None or w_eq_pos is None:
        return "UNKNOWN"
    return "M%s_V%s_E%s" % ("+" if mom_pos else "-", "+" if vol_high else "-",
                            "+" if w_eq_pos else "-")


def month_starts(dates):
    d = pd.Series(pd.to_datetime(list(dates)))
    first = d.groupby(d.dt.to_period("M")).first()
    return {str(k): v for k, v in first.items()}


def build_rows(table_months, starts, st, w_by_month):
    rows = []
    for rec in table_months:
        m = str(rec["month"])
        s = state_at(st, starts[m]) if m in starts else None
        w = w_by_month.get(m)
        w_pos = (None if w is None else bool(w > 0.0))
        key = cell_key(None if s is None else s["mom_pos"],
                       None if s is None else s["vol_high"], w_pos)
        rows.append({
            "month": m, "bars": int(rec["bars"]), "add_pp": round(float(rec["add_pp"]), 6),
            "positive": bool(float(rec["add_pp"]) > 0.0),
            "mom60": None if s is None else s["mom60"],
            "vol60_ann": None if s is None else s["vol60_ann"],
            "vol_thr": None if s is None else s["vol_thr"],
            "w_equity_start": None if w is None else round(float(w), 6),
            "state_asof": None if s is None else s["asof"],
            "cell": key,
            "mom_pos": None if s is None else s["mom_pos"],
            "vol_high": None if s is None else s["vol_high"],
            "w_eq_pos": w_pos,
        })
    return rows


def cell_table(rows):
    known = [r for r in rows if r["cell"] != "UNKNOWN"]
    out = []
    for key in sorted({r["cell"] for r in known}):
        sub = [r for r in known if r["cell"] == key]
        pp = np.array([r["add_pp"] for r in sub], float)
        out.append({
            "cell": key, "n_months": len(sub),
            "n_positive": int((pp > 0).sum()),
            "pos_ratio": round(float((pp > 0).mean()), 4) if len(pp) else None,
            "total_pp": round(float(pp.sum()), 4),
            "mean_pp": round(float(pp.mean()), 4) if len(pp) else None,
            "median_pp": round(float(np.median(pp)), 4) if len(pp) else None,
            "months": [r["month"] for r in sub],
        })
    return out


def binary_split(rows, field):
    """Mean add_pp when the condition is true vs false, and the gap."""
    hit = [r["add_pp"] for r in rows if r.get(field) is True]
    miss = [r["add_pp"] for r in rows if r.get(field) is False]
    if not hit or not miss:
        return None
    h, m = np.array(hit, float), np.array(miss, float)
    return {"n_true": int(len(h)), "n_false": int(len(m)),
            "mean_true_pp": round(float(h.mean()), 4),
            "mean_false_pp": round(float(m.mean()), 4),
            "gap_pp": round(float(h.mean() - m.mean()), 4),
            "pos_ratio_true": round(float((h > 0).mean()), 4),
            "pos_ratio_false": round(float((m > 0).mean()), 4)}


def shuffle_gap(rows, field, draws=DRAWS, seed=SEED):
    """Two-sided label-shuffle p for one condition's mean gap."""
    obs = binary_split(rows, field)
    if obs is None:
        return None
    known = [r for r in rows if r.get(field) is not None]
    labels = np.array([bool(r[field]) for r in known], bool)
    vals = np.array([r["add_pp"] for r in known], float)
    if labels.sum() == 0 or (~labels).sum() == 0:
        return None
    rng = np.random.default_rng(seed)
    hits = 0
    base = abs(obs["gap_pp"])
    for _ in range(draws):
        perm = rng.permutation(vals)
        g = float(perm[labels].mean() - perm[~labels].mean())
        if abs(g) >= base - 1e-12:
            hits += 1
    return {"gap_pp": obs["gap_pp"], "p_two_sided": round((hits + 1.0) / (draws + 1.0), 4),
            "draws": draws, "seed": seed}


def shuffle_best_cell(rows, draws=DRAWS, seed=SEED):
    """How often a shuffle of the same contributions makes a cell at least this good.

    The table has eight cells by construction, so the best one is always flattering.
    This rebuilds the eight cells from shuffled contributions (labels fixed) and asks how
    often the best cell's mean beats the overall mean by at least what the real table does.
    """
    known = [r for r in rows if r["cell"] != "UNKNOWN"]
    if not known:
        return None
    cells = np.array([r["cell"] for r in known])
    vals = np.array([r["add_pp"] for r in known], float)
    groups = {c: (cells == c) for c in sorted(set(cells))}
    sizes = {c: int(mask.sum()) for c, mask in groups.items()}

    def best_gap(v):
        overall = float(v.mean())
        best, best_cell = -1e9, None
        for c, mask in groups.items():
            if sizes[c] < MIN_CELL_MONTHS:
                continue
            g = float(v[mask].mean()) - overall
            if g > best:
                best, best_cell = g, c
        return best, best_cell

    obs_gap, obs_cell = best_gap(vals)
    if obs_cell is None:
        return {"obs_best_cell": None, "obs_gap_pp": None, "p_shuffle": None,
                "note": "no cell holds MIN_CELL_MONTHS months; the eight-cell search does not apply"}
    rng = np.random.default_rng(seed + 1)
    hits = 0
    for _ in range(draws):
        g, _c = best_gap(rng.permutation(vals))
        if g >= obs_gap - 1e-12:
            hits += 1
    return {"obs_best_cell": obs_cell, "obs_n_months": int(sizes[obs_cell]),
            "obs_gap_pp": round(float(obs_gap), 4),
            "p_shuffle": round((hits + 1.0) / (draws + 1.0), 4),
            "draws": draws, "seed": seed + 1, "min_cell_months": MIN_CELL_MONTHS}


def classify(best, splits):
    """Three states, read off the shuffle null -- never off the table."""
    if not best or best.get("p_shuffle") is None:
        return {"verdict": "CANNOT_JUDGE",
                "sentence": "这张面拼不出可判的格子（月份或格数不足），不判。"}
    p = float(best["p_shuffle"])
    lead = None
    if splits:
        lead = max((s for s in splits if s), key=lambda s: abs(s["gap_pp"]), default=None)
    lead_txt = ("最像的一条是 %s（真 %.2fpp/月 vs 假 %.2fpp/月，差 %+.2fpp，置换 p=%.3f）"
                % (lead.get("field_label", lead.get("field")), lead["mean_true_pp"],
                   lead["mean_false_pp"], lead["gap_pp"], lead["p_two_sided"])
                if lead else "三条条件都没有可判的对照")
    if p <= P_VISIBLE:
        return {"verdict": "CONDITION_VISIBLE",
                "sentence": "正贡献月确实堆在某一格里：最好的一格 %s（%d 个月）月均比全表高 %+.2fpp，"
                            "而把同样的钱打乱 2000 次、只有 %.0f%% 造得出这么好的一格——"
                            "这条差异不是八选一的运气。%s。"
                            % (best["obs_best_cell"], best["obs_n_months"],
                               best["obs_gap_pp"], p * 100.0, lead_txt)}
    if p <= P_WEAK:
        return {"verdict": "CONDITION_WEAK",
                "sentence": "某一格看着更好（%s，%d 个月，月均高 %+.2fpp），但打乱 2000 次里有 "
                            "%.0f%% 也能造出同样好的一格——这个差别落在八选一的噪声里，"
                            "只能当线索不能当条件。%s。"
                            % (best["obs_best_cell"], best["obs_n_months"],
                               best["obs_gap_pp"], p * 100.0, lead_txt)}
    return {"verdict": "NO_VISIBLE_CONDITION",
            "sentence": "正贡献月没有堆在任何事前可见的格子里：最好的一格 %s（%d 个月）月均只高 "
                        "%+.2fpp，而打乱 2000 次里有 %.0f%% 能造出一样好或更好的一格。"
                        "-- 这本书的钱是在场时赚到的，不是在某种可预告的天气里赚到的。%s。"
                        % (best["obs_best_cell"], best["obs_n_months"], best["obs_gap_pp"],
                           p * 100.0, lead_txt)}


# ---------------------------------------------------------------- run

def read_inputs():
    price = _load(FACE_PRICE)
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    sl = _load(FACE_SLICE) if os.path.exists(FACE_SLICE) else {}
    return {
        "cost": (price.get("config", {}).get("cost_bp_per_side") or 10.0) / 1e4,
        "rebal": int(price.get("config", {}).get("rebal") or 20),
        "vol_target": price.get("config", {}).get("vol_target"),
        "evidence_cutoff": price.get("evidence_cutoff"),
        "slice_select_pp": (sl.get("months") or {}).get("total_pp"),
        "slice_months": (sl.get("months") or {}).get("n_windows"),
        "slice_positive": (sl.get("months") or {}).get("n_positive"),
        "slice_verdict": sl.get("verdict"),
    }


def run():
    t0 = time.time()
    cfg = read_inputs()
    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}
    score = E.build_score(close, amt, feats, min_amt=GATE)

    base = CS.arm(close, openp, amt, score, cls, cfg["rebal"], cfg["cost"], cfg["vol_target"])
    df = base["df"]
    sel = df["select"].dropna()
    total_pp = PS.ann_pp(sel.mean())
    print("[base] select=%+6.2fpp bars=%d %.0fs" % (total_pp, len(sel), time.time() - t0),
          flush=True)

    months = PS.month_frame(pd.to_datetime(sel.index), sel)
    starts = month_starts(sel.index)

    w_frame = df["w_equity"].dropna() if "w_equity" in df else pd.Series(dtype=float)
    w_by_month = {}
    if len(w_frame):
        per = pd.PeriodIndex(pd.to_datetime(w_frame.index), freq="M")
        w_by_month = {str(k): float(v) for k, v in
                      pd.Series(w_frame.to_numpy(), index=per).groupby(level=0).first().items()}

    st = bench_state(close[BENCH] if BENCH in close else close.iloc[:, 0])
    rows = build_rows(months.to_dict(orient="records"), starts, st, w_by_month)
    cells = cell_table(rows)

    splits = []
    for field, label in (("mom_pos", "指数 60 日动量为正"),
                         ("vol_high", "60 日波动高于自己的历史中位"),
                         ("w_eq_pos", "月初持仓里有权益")):
        one = binary_split(rows, field)
        p = shuffle_gap(rows, field)
        if one:
            one = dict(one, field=field, field_label=label,
                       p_two_sided=(None if p is None else p["p_two_sided"]))
            splits.append(one)
    best = shuffle_best_cell(rows)
    v = classify(best, splits)

    known = [r for r in rows if r["cell"] != "UNKNOWN"]
    control_pp = (None if cfg["slice_select_pp"] is None
                  else round(total_pp - float(cfg["slice_select_pp"]), 4))
    control_ok = control_pp is not None and abs(control_pp) <= CONTROL_TOL_PP
    months_ok = (cfg["slice_months"] is None
                 or (len(months) == cfg["slice_months"]
                     and int((months["add_pp"] > 0).sum()) == cfg["slice_positive"]))

    out = {
        "evidence_cutoff": cfg["evidence_cutoff"] or str(pd.Timestamp(close.index[-1]).date()),
        "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_month_condition.py",
        "rule": {
            "benchmark": BENCH, "gate_cny": GATE, "seats": CS.BASE_SEATS,
            "rebal": cfg["rebal"], "cost_bp_per_side": round(cfg["cost"] * 1e4, 3),
            "vol_target": cfg["vol_target"],
            "question": "do the select leg's positive months share a condition that was "
                        "knowable at the start of the month",
            "conditions": {
                "M": "bench close vs its own close 60 bars earlier > 0, read at the last bar "
                     "strictly before the month's first bar",
                "V": "60-bar realised vol (annualised) above its own EXPANDING median, same bar",
                "E": "the book's w_equity on the month's first bar > 0",
            },
            "cells": "2x2x2 = 8 (M x V x E); months with no 60-bar history are UNKNOWN",
            "min_cell_months": MIN_CELL_MONTHS, "draws": DRAWS, "seed": SEED,
            "p_visible": P_VISIBLE, "p_weak": P_WEAK,
            "null": "label shuffle: the same contributions rebuilt into the same eight cells; "
                    "the verdict is read off that null, never off the best row of the table",
            "frozen": "criteria written before the run; --check re-derives the verdict",
        },
        "control": {
            "select_ann_pp": round(total_pp, 4),
            "r1766_select_ann_pp": cfg["slice_select_pp"],
            "delta_pp": control_pp, "tol_pp": CONTROL_TOL_PP, "ok": control_ok,
            "months": int(len(months)),
            "months_match_r1766": bool(months_ok),
            "r1766_months": cfg["slice_months"], "r1766_positive": cfg["slice_positive"],
        },
        "identity": {"sum_month_add_pp": round(float(months["add_pp"].sum()), 6),
                     "select_ann_pp": round(total_pp, 6),
                     "abs_error": abs(float(months["add_pp"].sum()) - total_pp),
                     "ok": bool(abs(float(months["add_pp"].sum()) - total_pp) <= 1e-9)},
        "coverage": {"months_total": int(len(rows)), "months_known": len(known),
                     "months_unknown": int(len(rows) - len(known)),
                     "windows": sorted({r["cell"] for r in known})},
        "positive_months_known": int(sum(1 for r in known if r["positive"])),
        "cells": cells,
        "splits": splits,
        "best_cell": best,
        "table_months": rows,
        **v,
    }
    if not control_ok or not months_ok:
        out["verdict"] = "CANNOT_JUDGE_CONTROL"
        out["sentence"] = ("基座臂与 r1766 对不上（select 差 %s pp，容差 %.2fpp；月表 %d/%d vs %s/%s），"
                           "这不是同一本书，本面不判。"
                           % (control_pp, CONTROL_TOL_PP, len(months),
                              int((months["add_pp"] > 0).sum()),
                              cfg["slice_months"], cfg["slice_positive"]))
    out["run_seconds"] = round(time.time() - t0, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[verdict] %s" % out["verdict"], flush=True)
    print("[cells] %d cells over %d known months (unknown %d)"
          % (len(cells), len(known), len(rows) - len(known)), flush=True)
    if best and best.get("p_shuffle") is not None:
        print("[best-cell] %s n=%d gap=%+.2fpp p=%.3f"
              % (best["obs_best_cell"], best["obs_n_months"], best["obs_gap_pp"],
                 best["p_shuffle"]), flush=True)
    for s in splits:
        print("[split] %-28s true %+6.2f false %+6.2f gap %+6.2f p=%s"
              % (s["field"], s["mean_true_pp"], s["mean_false_pp"], s["gap_pp"],
                 s["p_two_sided"]), flush=True)
    print("[write] %s (%.1fs)" % (OUT_JSON, time.time() - t0), flush=True)
    return 0


# ---------------------------------------------------------------- write-up

def write_md():
    d = _load(OUT_JSON)
    L = []
    L.append("# 正贡献月有没有事前可见的天气（r1767）\n")
    L.append("问题：r1766 说这本书的超额是「月度事件、年度习惯」——%s。"
             "可这句话没回答下一句：那些月份**事前能不能认出来**？\n"
             % (d["control"]["r1766_months"] and "83 个月里 44 个为正，按年是 6/7" or ""))
    L.append("本轮把同一张月表按三个**月初就能看到**的状态切开：指数 60 日动量为正（M）、"
             "60 日已实现波动高于自己的历史中位（V）、月初持仓里有权益（E）。"
             "2×2×2 = 8 格。\n")
    L.append("## 判据（先冻后跑）\n")
    L.append("- 空假设＝标签打乱：同样的月贡献、同样的格子大小，只把「哪个月是哪格」打乱 %d 次；\n"
             % d["rule"]["draws"])
    L.append("- 判词只从空分布读：最好的一格月均超出全表的幅度，在空分布里出现的比例 ≤%.0f%% → "
             "**CONDITION_VISIBLE**；≤%.0f%% → **CONDITION_WEAK**；否则 **NO_VISIBLE_CONDITION**；\n"
             % (d["rule"]["p_visible"] * 100, d["rule"]["p_weak"] * 100))
    L.append("- 一格的月数 < %d 不参与「最佳格」评选（两个月的好运气不算条件）。\n"
             % d["rule"]["min_cell_months"])
    L.append("\n## 读数\n")
    L.append("%s\n" % d.get("sentence", ""))
    L.append("\n| 格（M/V/E） | 月数 | 为正 | 正比例 | 合计 pp | 月均 pp | 中位 pp |")
    L.append("|---|---|---|---|---|---|---|")
    for c in d["cells"]:
        L.append("| %s | %d | %d | %.0f%% | %+.2f | %+.2f | %+.2f |"
                 % (c["cell"], c["n_months"], c["n_positive"], (c["pos_ratio"] or 0) * 100,
                    c["total_pp"], c["mean_pp"], c["median_pp"]))
    b = d.get("best_cell") or {}
    L.append("\n- 最好的一格：%s（%d 个月），月均比全表高 %+.2fpp；打乱 2000 次里有 %.0f%% "
             "也能造出一样好或更好的一格。\n"
             % (b.get("obs_best_cell"), b.get("obs_n_months") or 0, b.get("obs_gap_pp") or 0.0,
                (b.get("p_shuffle") or 1.0) * 100))
    L.append("\n## 三条条件各自的对照\n")
    L.append("| 条件 | 真（月数/月均） | 假（月数/月均） | 差 | 置换 p |")
    L.append("|---|---|---|---|---|")
    for s in d["splits"]:
        L.append("| %s | %d / %+.2fpp | %d / %+.2fpp | %+.2fpp | %.3f |"
                 % (s["field_label"], s["n_true"], s["mean_true_pp"],
                    s["n_false"], s["mean_false_pp"], s["gap_pp"], s["p_two_sided"]))
    L.append("\n## 覆盖与对账\n")
    L.append("- 月份 %d 个，其中 %d 个拼出格、%d 个因缺 60 日历史记 UNKNOWN；\n"
             % (d["coverage"]["months_total"], d["coverage"]["months_known"],
                d["coverage"]["months_unknown"]))
    L.append("- 控制臂：select 腿 %+.4fpp vs r1766 在印 %s pp（差 %s pp，容差 %.2f），月表 %d 月/%d 正；\n"
             % (d["control"]["select_ann_pp"], d["control"]["r1766_select_ann_pp"],
                d["control"]["delta_pp"], d["control"]["tol_pp"],
                d["control"]["months"], d["positive_months_known"]))
    L.append("- 加性恒等式 Σ月贡献 == 年化 select，误差 %.2e。\n" % d["identity"]["abs_error"])
    L.append("\n## 这张表最容易读错的地方\n")
    rows_all = d["table_months"]
    sizes = sorted((c["n_months"] for c in d["cells"]), reverse=True)
    empty = 8 - len(d["cells"])
    vals = np.array([r["add_pp"] for r in rows_all], float)
    L.append("- **八格里只有 %d 格有人，而且极不均**：最大的一格装了 %d 个月（占 %d 个月的 %.0f%%），"
             "最小的有人的格只有 %d 个月，另有 %d 格整月缺席——三个条件彼此不独立"
             "（动量与波动同向变动，这本书 %.0f%% 的月份都持着权益），所以「八格」不是八种独立的天气。\n"
             % (len(d["cells"]), sizes[0], d["coverage"]["months_total"],
                sizes[0] * 100.0 / max(1, d["coverage"]["months_total"]), sizes[-1], empty,
                100.0 * max(s["n_true"] for s in d["splits"] if s["field"] == "w_eq_pos") 
                / max(1, d["coverage"]["months_total"])))
    L.append("- **格与格之间的差是零点几个 pp，而单月噪声是它的几十倍**：全表 %.2fpp / %d 月 = "
             "%.2fpp/月，月贡献的标准差 %.2fpp（最小 %+.2f、最大 %+.2f）。"
             "任何一格「更好」都只有百分之几 pp 的幅度，读表时别把 0.13 和 0.03 的差当成信号。\n"
             % (d["control"]["select_ann_pp"], d["coverage"]["months_total"],
                d["control"]["select_ann_pp"] / max(1, d["coverage"]["months_total"]),
                float(vals.std(ddof=1)), float(vals.min()), float(vals.max())))
    L.append("\n## 这条面不说什么\n")
    L.append("- 不说「加上这个条件就能多赚」。它只量「在场时赚到的钱」有没有天气预报；"
             "即便判 VISIBLE，也只是把一本书的收益描述得更准，不是一条新策略。\n")
    L.append("- 不用未来的分钟/日线数据反推状态：三个状态都读自月初之前最后一根 bar，"
             "波动的阈值用的是只含过去的扩展中位。\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("[md] %s" % OUT_MD, flush=True)
    return 0


def _check():
    """Re-derive the verdict from the table on disk; fail if the table and the words differ."""
    d = _load(OUT_JSON)
    problems = []
    rows = d["table_months"]
    known = [r for r in rows if r["cell"] != "UNKNOWN"]
    if len(known) != d["coverage"]["months_known"]:
        problems.append("coverage months_known %d != table %d"
                        % (d["coverage"]["months_known"], len(known)))
    cells = cell_table(rows)
    for c in cells:
        old = next((x for x in d["cells"] if x["cell"] == c["cell"]), None)
        if old is None or old["n_months"] != c["n_months"] or abs(old["mean_pp"] - c["mean_pp"]) > 1e-6:
            problems.append("cell %s disagrees with the table" % c["cell"])
    best = shuffle_best_cell(rows)
    if best and d.get("best_cell"):
        if best.get("p_shuffle") is not None and d["best_cell"].get("p_shuffle") is not None:
            if abs(best["p_shuffle"] - d["best_cell"]["p_shuffle"]) > 1e-9:
                problems.append("best-cell p re-derives to %s, face says %s"
                                % (best["p_shuffle"], d["best_cell"]["p_shuffle"]))
        if best.get("obs_best_cell") != d["best_cell"].get("obs_best_cell"):
            problems.append("best cell re-derives to %s, face says %s"
                            % (best.get("obs_best_cell"), d["best_cell"].get("obs_best_cell")))
    v = classify(best, d["splits"])
    if v["verdict"] != d["verdict"]:
        problems.append("verdict re-derives to %s, face says %s" % (v["verdict"], d["verdict"]))
    ident = abs(sum(r["add_pp"] for r in rows) - d["control"]["select_ann_pp"])
    if ident > 1e-4:   # table values land at 6 decimals; 83 months sum can drift ~8e-5
        problems.append("sum(month add_pp) != select_ann_pp (%.2e)" % ident)
    if d["control"]["delta_pp"] is not None and not d["control"]["ok"]:
        problems.append("control arm does not reproduce r1766")
    ok = not problems
    print(json.dumps({"ok": ok, "problems": problems, "verdict": v["verdict"],
                      "best_cell": (best or {}).get("obs_best_cell"),
                      "p_shuffle": (best or {}).get("p_shuffle")}, ensure_ascii=False))
    return 0 if ok else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # L1 the month table is additive: sum of months == the annualised leg
    rng = np.random.default_rng(7)
    days = pd.date_range("2021-01-04", periods=260, freq="B")
    s = pd.Series(rng.normal(3e-4, 0.01, len(days)), index=days)
    mf = PS.month_frame(days, s)
    leg("L1 month table stays additive", abs(float(mf["add_pp"].sum()) - PS.ann_pp(s.mean())) < 1e-9)

    # L2 the eight cells are addressed correctly
    leg("L2 cell key maps 3 booleans", cell_key(True, False, True) == "M+_V-_E+"
        and cell_key(False, True, False) == "M-_V+_E-" and cell_key(None, True, True) == "UNKNOWN")

    # L3 state_at never reads the bar it classifies
    bclose = pd.Series(np.linspace(1.0, 2.0, 200), index=pd.date_range("2020-01-01", periods=200, freq="B"))
    stx = bench_state(bclose)
    d_start = stx["close"].index[120]
    sa = state_at(stx, d_start)
    prev = stx["close"].index[119]
    leg("L3 state reads the bar before the month start",
        sa is not None and sa["asof"] == str(pd.Timestamp(prev).date()))

    # L4 warm-up months are UNKNOWN, not silently classified
    leg("L4 short history is UNKNOWN",
        state_at(stx, stx["close"].index[30]) is None)

    # L5 a planted condition gives a small shuffle p / no condition gives a large one
    planted = [{"add_pp": 1.0, "mom_pos": True, "vol_high": True, "w_eq_pos": True}
               for _ in range(12)] + \
              [{"add_pp": -0.5, "mom_pos": False, "vol_high": False, "w_eq_pos": False}
               for _ in range(12)]
    sp = shuffle_gap(planted, "mom_pos", draws=400, seed=11)
    leg("L5 planted condition is separated", sp is not None and sp["p_two_sided"] <= 0.01)
    flat = [{"add_pp": (-0.5 if i % 2 else 0.5), "mom_pos": bool(i % 3 == 0),
             "vol_high": bool(i % 5 == 0), "w_eq_pos": bool(i % 2 == 0)} for i in range(24)]
    sf = shuffle_gap(flat, "mom_pos", draws=400, seed=11)
    leg("L5b unplanted condition is not", sf is not None and sf["p_two_sided"] > 0.10)

    # L6 the best-cell null punishes an eight-way search
    same = [{"month": "m%02d" % i, "add_pp": 0.1000001, "cell": "M+_V+_E+"} for i in range(11)]
    same = [{"month": "m%02d" % i, "add_pp": 0.1, "cell": "M+_V+_E+" if i < 10 else "M-_V-_E-"}
            for i in range(12)]
    nocell = shuffle_best_cell(same, draws=200, seed=5)
    leg("L6 a cell with too few months is not the best cell",
        nocell is not None and nocell["obs_n_months"] >= MIN_CELL_MONTHS)

    # L7 planted best cell reads VISIBLE, flat reads NOT_VISIBLE
    strong = [{"month": "a%02d" % i, "add_pp": (2.0 if i < 10 else -0.5),
               "cell": ("M+_V+_E+" if i < 10 else "M-_V-_E-")} for i in range(20)]
    w_strong = shuffle_best_cell(strong, draws=400, seed=3)
    leg("L7 a planted cell clears the null", w_strong is not None and w_strong["p_shuffle"] <= P_VISIBLE)
    rng2 = np.random.default_rng(21)
    flat_vals = rng2.normal(0.0, 0.5, 40)
    flat_rows = [{"month": "f%02d" % i, "add_pp": float(flat_vals[i]),
                  "cell": ["M+_V+_E+", "M+_V-_E+", "M-_V+_E+", "M-_V-_E+"][i % 4]} for i in range(40)]
    w_flat = shuffle_best_cell(flat_rows, draws=400, seed=3)
    leg("L7b a flat table does not", w_flat is not None and w_flat["p_shuffle"] > P_WEAK)

    # L8 the three verdicts are reachable
    leg("L8 verdict states",
        classify({"p_shuffle": 0.02, "obs_best_cell": "x", "obs_n_months": 9,
                  "obs_gap_pp": 1.0}, [])["verdict"] == "CONDITION_VISIBLE"
        and classify({"p_shuffle": 0.18, "obs_best_cell": "x", "obs_n_months": 9,
                      "obs_gap_pp": 1.0}, [])["verdict"] == "CONDITION_WEAK"
        and classify({"p_shuffle": 0.60, "obs_best_cell": "x", "obs_n_months": 9,
                      "obs_gap_pp": 1.0}, [])["verdict"] == "NO_VISIBLE_CONDITION"
        and classify(None, [])["verdict"] == "CANNOT_JUDGE")

    # L9 unknown months are counted but never enter a cell
    rows = [{"month": "2020-01", "add_pp": 0.5, "cell": "UNKNOWN", "positive": True,
             "mom_pos": None, "vol_high": None, "w_eq_pos": None},
            {"month": "2020-02", "add_pp": 0.5, "cell": "M+_V+_E+", "positive": True,
             "mom_pos": True, "vol_high": True, "w_eq_pos": True}]
    ct = cell_table(rows)
    leg("L9 unknown months are not in any cell", len(ct) == 1 and ct[0]["n_months"] == 1)

    passed = sum(1 for _n, ok in legs if ok)
    for name, ok in legs:
        print("  %s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d %s" % (passed, len(legs), "PASS" if passed == len(legs) else "FAIL"))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower().lstrip("-")
    if cmd == "run":
        rc = run()
        if rc == 0:
            write_md()
        return rc
    if cmd == "check":
        return _check()
    if cmd == "selftest":
        return selftest()
    print("usage: etf_book_month_condition.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
