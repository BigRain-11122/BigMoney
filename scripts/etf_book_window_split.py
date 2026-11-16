#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""前段只有 6%、后段 18%：是防守档少开了，还是权益选股本身不一样？（r1770）

r1765/r1766 把这本书切成两段来读，并在每一面上都写着同一个事实：2020-2023 段只有 6%
上下，2024 年以来 15~20%。读者下一步一定会问为什么，而过去几面上对这个问题只给过一句
「2024 年以前靠债券防守」，那句话没有数字。

本面在同一台引擎、同一张面板、同一把尺上把它拆成两件事：

  (1) **在场时间**：这本书有多少比例的 bar 是持权益的（w_equity > 0），多少是纯防守档。
  (2) **每档每天的赚钱速度**：在权益档的 bar 上每天平均赚多少，在防守档的 bar 上赚多少。

两段 × 两档 = 四个格子。用 Bennet 中点分解把年化差精确切开：

    mix_s  = (share_oos_s - share_is_s) * (rate_oos_s + rate_is_s)/2      "这一档出现得更少了/更多了"
    rate_s = (share_oos_s + share_is_s)/2 * (rate_oos_s - rate_is_s)      "这一档自己赚得快了/慢了"
    gap    = sum_s (mix_s + rate_s)                                       恒等式，误差 ~1e-13

于是「差在哪」不再是一个故事，而是四个数里最大的那个；并且这个恒等式在 selftest 里钉住，
`--check` 从存下来的逐日序列重算一遍，不读印出来的数字。

差本身能不能被看见，用同一把尺（圆形块自助，块长 20＝一个调仓周期，2000 次，种子冻结）
分三种读法各自答一次：净收益差、权益档内的日收益差、权益档占比差。任何一格不大于它自己的
MDE80，就不许说那一格是原因。

Usage:
    python scripts/etf_book_window_split.py run
    python scripts/etf_book_window_split.py --check
    python scripts/etf_book_window_split.py --selftest
    python scripts/etf_book_window_split.py --md
"""
import json
import math
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

import etf_book_entry_gate as G               # noqa: E402  (panel + flip repair)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_equity_alpha as A                  # noqa: E402  (classify + IS/OOS boundary)
import etf_book_corr_select as CS             # noqa: E402  (the base arm's rule)
import etf_book_money_mde as MM               # noqa: E402  (replay + attribution)
import etf_book_gate_raise_noise as N         # noqa: E402  (arm_stats)
import etf_book_book_mde as BM                # noqa: E402  (the bootstrap ruler)
import etf_robust_pf as R                     # noqa: E402  (the engine)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_window_split.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_WINDOW_SPLIT.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_SLICE = os.path.join(ROOT, "results", "etf_book_period_slice.json")

BENCH = CS.BENCH
GATE = CS.GATE
SEATS = CS.BASE_SEATS
PER_YEAR = 252.0

IS_END = A.IS_END                 # "2023-12-31": the boundary every published face reads
BLOCK = BM.BLOCK                  # 20 == one rebalance period
DRAWS = BM.DRAWS                  # 2000
SEED = BM.SEED
Z80 = BM.Z_80

P_SEP = 0.05                      # frozen separation line
CELL_SHARE_LINE = 0.5             # a cell names the verdict only if it carries this share
STATE_MIN_BARS = 60               # fewer bars than this in a state => its "rate" is not a rate
CONTROL_TOL_PP = 0.25             # the control arm must reproduce the published CAGR cell
SELECT_TOL_PP = 0.05              # and the published select leg
REPLAY_TOL = 1e-9
IDENTITY_TOL = 0.02               # annualised pp; select+rotate+size+cost+r_bench == net

STATES = ("equity", "defense")
CELLS = ("mix_equity", "mix_defense", "rate_equity", "rate_defense")


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- the split

def state_flags(w_equity):
    """One flag per bar: does the book hold any equity weight on this bar?

    The state is decided at the rebalance and held for the period, so this is a step
    function, not a daily guess. NaN weight (a bar the replay could not attribute) is
    counted as defence ONLY if it is really zero -- an unattributable bar is dropped
    upstream by the replay, so anything reaching here is a decision.
    """
    w = pd.Series(w_equity).astype(float)
    return (w > 0.0).to_numpy()


def window_mask(index, which):
    """Calendar split at the boundary every published face uses (r1765/r1766)."""
    idx = np.asarray(pd.DatetimeIndex(index).to_numpy(), dtype="datetime64[ns]")
    cut = np.datetime64(pd.Timestamp(IS_END), "ns")
    return idx <= cut if which == "is" else idx > cut


def seg_stats(eq, label):
    """The published window statistics, borrowed from the face that owns the definition.

    Not re-hand-rolled: r1262's pitfall is a hand-rolled sub-window CAGR that annualises
    with `last^(1/yrs)-1` and silently assumes the slice starts at 1.0. A.stats2 reads the
    slice's own first level AND the calendar (not the bar count), so a window's rate here is
    the same number the printed cell would show -- which is what makes the cross-face
    control below possible at all.
    """
    return A.stats2(pd.Series(eq).dropna(), label)


def window_stats(df, flags, which):
    """Everything one window carries: the book, both states' shares, and both rates."""
    net = df["net"].astype(float)
    mask = window_mask(df.index, which)
    n = int(mask.sum())
    out = {"window": which, "bars": n,
           "first_bar": (str(df.index[mask][0].date()) if n else None),
           "last_bar": (str(df.index[mask][-1].date()) if n else None)}
    if not n:
        return out
    netw = net[mask]
    st = seg_stats(pd.Series(df["equity"])[mask], which)
    out.update({
        "years": st.get("years"),
        "cagr_pct": (None if st.get("cagr") is None
                     else round(float(st["cagr"]) * 100.0, 3)),
        "maxdd_pct": (None if st.get("maxdd") is None
                      else round(float(st["maxdd"]) * 100.0, 2)),
        "vol_pct": (None if st.get("vol") is None else round(float(st["vol"]) * 100.0, 2)),
        "sharpe": st.get("sharpe"),
        "start_level": st.get("start_level"),
        "total_ann_pp": round(float(netw.mean()) * PER_YEAR * 100.0, 4),
        "bench_ann_pp": round(float(df["r_bench"][mask].mean()) * PER_YEAR * 100.0, 4),
        "mean_w_equity": round(float(pd.Series(df["w_equity"])[mask].astype(float)
                                    .fillna(0.0).mean()), 4),
    })
    fw = pd.Series(flags[mask])
    shares = {"equity": float(fw.mean()), "defense": float(1.0 - fw.mean())}
    rates = {}
    for st in STATES:
        sel = fw.to_numpy() == (st == "equity")
        rates[st] = (round(float(netw.to_numpy()[sel].mean()) * PER_YEAR * 100.0, 4)
                     if int(sel.sum()) else None)
        out[st + "_bars"] = int(sel.sum())
        # the legs, but only on this state's own bars -- "在权益档里，选股腿一天给多少"
        for leg in ("select", "rotate", "size", "cost"):
            v = pd.Series(df[leg]).astype(float)[mask].to_numpy()[sel]
            out[leg + "_" + st + "_ann_pp"] = (round(float(v.mean()) * PER_YEAR * 100.0, 4)
                                               if v.size else None)
    out["shares"] = {k: round(v, 6) for k, v in shares.items()}
    out["rates_ann_pp"] = rates
    out["contrib_pp"] = {st: (None if rates[st] is None
                              else round(shares[st] * rates[st], 4)) for st in STATES}
    legs = {k: round(float(df[k][mask].mean()) * PER_YEAR * 100.0, 4)
            for k in ("select", "rotate", "size", "cost", "r_bench")}
    legs["net"] = out["total_ann_pp"]
    legs["identity_gap_pp"] = round(legs["select"] + legs["rotate"] + legs["size"]
                                    + legs["cost"] + legs["r_bench"]
                                    - legs["net"], 4)
    out["legs_ann_pp"] = legs
    # the decomposition's own identity, on the printed numbers
    out["state_identity_gap_pp"] = round(sum(v for v in out["contrib_pp"].values()
                                             if v is not None) - out["total_ann_pp"], 6)
    return out


def bennet(is_w, oos_w):
    """Bennet midpoint decomposition: gap == sum of the four cells, mechanically.

    mix_s  : the state shows up for a different fraction of the time
    rate_s : the state itself pays a different daily rate
    The equity/defence shares sum to 1 in each window, so the share CHANGES are equal and
    opposite -- but the mix cells are those changes times each state's own average rate, so
    mix_defence == -mix_equity only when both states pay the same rate. Both are printed
    because the reader quotes them in opposite directions ("防守档变少了" vs "权益档变多了")
    and must see that they are two different amounts of money, not one number twice.
    """
    cells = {}
    for st in STATES:
        s_is, s_oos = is_w["shares"][st], oos_w["shares"][st]
        r_is, r_oos = is_w["rates_ann_pp"][st], oos_w["rates_ann_pp"][st]
        if r_is is None or r_oos is None:
            cells["mix_" + st] = None
            cells["rate_" + st] = None
            continue
        cells["mix_" + st] = round((s_oos - s_is) * 0.5 * (r_oos + r_is), 4)
        cells["rate_" + st] = round(0.5 * (s_oos + s_is) * (r_oos - r_is), 4)
    gap = round(oos_w["total_ann_pp"] - is_w["total_ann_pp"], 4)
    total = (None if any(v is None for v in cells.values())
             else round(sum(cells.values()), 4))
    return {"cells": cells, "gap_ann_pp": gap, "cells_sum_pp": total,
            "identity_gap_pp": (None if total is None else round(total - gap, 6))}


def cell_readability(is_w, oos_w):
    """Can a cell be quoted at all? A rate built on 20 bars is not a rate.

    The published book is almost always in equity, so the defence state can be a handful of
    bars in one window. Annualising 20 bars by 252 turns a single lucky week into a 60pp
    "daily speed" -- printing it is fine (it is part of the arithmetic), quoting it as a
    reason is not. This gate is what stops that; it is a bar count, not a taste.
    """
    eq_ok = all(int(w.get("equity_bars") or 0) >= STATE_MIN_BARS for w in (is_w, oos_w))
    df_ok = all(int(w.get("defense_bars") or 0) >= STATE_MIN_BARS for w in (is_w, oos_w))
    return {"mix_equity": eq_ok, "rate_equity": eq_ok,
            "mix_defense": df_ok, "rate_defense": df_ok}


def dominant_cell(cells, gap, readable=None, windows=None):
    """Which of the four cells carries the gap -- and by how much of it.

    Printed unconditionally; the verdict only uses it when the gap itself clears its own
    MDE80. A cell is allowed to "explain" only if it carries CELL_SHARE_LINE of |gap| AND
    has enough bars on both sides to be a rate at all.
    """
    live = {k: v for k, v in cells.items() if v is not None and not k.startswith("_")}
    if not live or gap is None or abs(gap) < 1e-12:
        return None
    key = max(live, key=lambda k: abs(live[k]))
    state = "equity" if key.endswith("equity") else "defense"
    bars = None
    if windows:
        bars = {"is": int(windows["is"].get(state + "_bars") or 0),
                "oos": int(windows["oos"].get(state + "_bars") or 0)}
    return {"cell": key, "pp": live[key],
            "share_of_gap": round(abs(live[key]) / abs(gap), 4),
            "readable": True if readable is None else bool(readable.get(key, False)),
            "state_bars": bars}


# ---------------------------------------------------------------- the ruler

def two_sample(a, b, block=BLOCK, draws=DRAWS, seed=SEED):
    """Two-sample circular block bootstrap of mean(b) - mean(a), on the same ruler.

    One sample would be enough for a paired gap; these windows are disjoint in time, so the
    honest read resamples each window's own blocks and looks at the spread of the difference.
    Both sides must have at least two blocks, otherwise the read is refused, not narrowed.
    """
    xa = np.asarray([v for v in np.asarray(a, dtype=float) if np.isfinite(v)], dtype=float)
    xb = np.asarray([v for v in np.asarray(b, dtype=float) if np.isfinite(v)], dtype=float)
    if xa.size < block * 2 or xb.size < block * 2:
        return None
    rng = np.random.default_rng(seed)
    offs = np.arange(block)[None, :]

    def draw_means(x):
        n = x.size
        nb = int(math.ceil(n / float(block)))
        starts = rng.integers(0, n, size=(draws, nb))
        idx = (starts[:, :, None] + offs[None, None, :]).reshape(draws, -1)[:, :n] % n
        return x[idx].mean(axis=1)

    ma, mb = draw_means(xa), draw_means(xb)
    gaps = mb - ma
    obs = float(xb.mean() - xa.mean())
    se = float(gaps.std(ddof=1))
    if obs > 0:
        p_dir = round((int((gaps <= 0.0).sum()) + 1) / (draws + 1.0), 4)
    elif obs < 0:
        p_dir = round((int((gaps >= 0.0).sum()) + 1) / (draws + 1.0), 4)
    else:
        p_dir = 1.0
    p_two = round(min(1.0, 2.0 * min(p_dir, 1.0 - p_dir)), 4)
    return {"a_bars": int(xa.size), "b_bars": int(xb.size),
            "obs_pp": round(obs * PER_YEAR * 100.0, 4),
            "se_pp": round(se * PER_YEAR * 100.0, 4),
            "mde80_pp": round(Z80 * se * PER_YEAR * 100.0, 4),
            "obs_raw": obs, "se_raw": se,
            "t": (round(obs / se, 3) if se > 0 else None),
            "p_direction": p_dir, "p_two_sided": p_two,
            "draws": draws, "block": block, "seed": seed,
            "unit": "pp_of_return_ann"}


def share_gap(a_flags, b_flags, block=BLOCK, draws=DRAWS, seed=SEED):
    """The same two-sample read on a 0/1 series: did the state show up more often?

    A share is a mean of an indicator, so the same machinery applies -- but the unit is
    pp of TIME, not pp of return, and the face keeps the two apart in every sentence. The
    annualisation is therefore NOT applied here: 10pp more equity days is 10pp of time.
    """
    r = two_sample(np.asarray(a_flags, dtype=float), np.asarray(b_flags, dtype=float),
                   block=block, draws=draws, seed=seed)
    if r is None:
        return None
    return {"a_bars": r["a_bars"], "b_bars": r["b_bars"],
            "obs_pp": round(r["obs_raw"] * 100.0, 4),
            "se_pp": round(r["se_raw"] * 100.0, 4),
            "mde80_pp": round(Z80 * r["se_raw"] * 100.0, 4),
            "t": r["t"], "p_direction": r["p_direction"],
            "p_two_sided": r["p_two_sided"], "draws": r["draws"],
            "block": r["block"], "seed": r["seed"], "unit": "pp_of_time"}


# ---------------------------------------------------------------- verdict

def classify(control, gapstat, cells, dom):
    """Frozen decision tree. Control first, then "can the gap be seen", then "which cell"."""
    if not control.get("ok"):
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与在印的书对不上（年化差 %s pp / 选股腿差 %s pp），"
                            "这不是同一本书，本面不判。"
                            % (control.get("delta_pp"), control.get("select_delta_pp"))}
    if not control.get("replay_ok"):
        return {"verdict": "CANNOT_JUDGE_REPLAY",
                "sentence": "重放重建不出引擎净值，逐日序列不是这台引擎的，本面不判。"}
    if gapstat is None:
        return {"verdict": "CANNOT_JUDGE_NO_GAP",
                "sentence": "两段的逐日净收益差读不出来（样本不足以分块），本面不判。"}
    separable = (gapstat["p_two_sided"] <= P_SEP
                 and abs(gapstat["obs_pp"]) >= gapstat["mde80_pp"])
    if not separable:
        return {"verdict": "WINDOW_GAP_NOT_SEPARABLE",
                "sentence": "两段的年化差是 %+.2fpp，可这把尺在这本书上要看见 %.2fpp 才算数"
                            "（块自助 %d 次，双向 p=%.2f）——差落在噪声里，不给原因。"
                            % (gapstat["obs_pp"], gapstat["mde80_pp"],
                               gapstat["draws"], gapstat["p_two_sided"])}
    if not dom or dom.get("share_of_gap", 0.0) < CELL_SHARE_LINE:
        return {"verdict": "NO_SINGLE_CELL",
                "sentence": "两段的年化差是 %+.2fpp 且能被看见，但没有哪一格能独占它"
                            "（最大的一格只占 %.0f%%）——差是几件事叠出来的，不给单一原因。"
                            % (gapstat["obs_pp"], 100.0 * (dom or {}).get("share_of_gap", 0.0))}
    if not dom.get("readable", True):
        bars = dom.get("state_bars") or {}
        return {"verdict": "NO_SINGLE_CELL",
                "sentence": "最大的一格是 `%s`（%+.2fpp，占全场 %.0f%%），可它建在 %s/%s 根 bar 上"
                            "——少于 %d 根的档，年化出来的「日速度」是那一周的运气，本面不拿它当原因。"
                            % (dom["cell"], dom["pp"], 100.0 * dom["share_of_gap"],
                               bars.get("is"), bars.get("oos"), STATE_MIN_BARS)}
    key = dom["cell"]
    if key == "mix_equity":
        return {"verdict": "TIME_IN_EQUITY_EXPLAINS",
                "sentence": "差主要是**在场时间**：权益档占比从 %.0f%% 变成 %.0f%%，"
                            "按两段各自的日收益速度换算，这一件事贡献 %+.2fpp（占全场 %+.2fpp 的 %.0f%%）。"
                            % (100.0 * (cells.get("_share_is_equity") or 0.0),
                               100.0 * (cells.get("_share_oos_equity") or 0.0),
                               dom["pp"], gapstat["obs_pp"], 100.0 * dom["share_of_gap"])}
    if key == "mix_defense":
        return {"verdict": "TIME_IN_DEFENCE_EXPLAINS",
                "sentence": "差主要是**防守档占比变了**：占比的变化与权益档那一格是同一个变化，"
                            "但乘的是防守档自己的速度，所以金额不同——这一格 %+.2fpp，占全场的 %.0f%%。"
                            % (dom["pp"], 100.0 * dom["share_of_gap"])}
    if key == "rate_equity":
        return {"verdict": "EQUITY_DAY_RATE_EXPLAINS",
                "sentence": "差主要是**权益档自己每天赚多少变了**：这一格 %+.2fpp，"
                            "占全场 %+.2fpp 的 %.0f%%——不是少开了权益，是开着的时候也不一样了。"
                            % (dom["pp"], gapstat["obs_pp"], 100.0 * dom["share_of_gap"])}
    return {"verdict": "DEFENCE_DAY_RATE_EXPLAINS",
            "sentence": "差主要是**防守档自己每天赚多少变了**：这一格 %+.2fpp，"
                        "占全场 %+.2fpp 的 %.0f%%——钱差在躲出去以后那段时间的利息上。"
                        % (dom["pp"], gapstat["obs_pp"], 100.0 * dom["share_of_gap"])}


# ---------------------------------------------------------------- run

def _run_base(close, openp, amt, score, cls, rebal, cost, vol_target):
    diag = []
    ser, mean_turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, SEATS,
                                          cost, vol_target=vol_target, vol_window=60,
                                          diag=diag)
    df = MM.replay(close, openp, diag, rebal, SEATS, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left").dropna(subset=["engine", "equity"])
    max_rel = (float((joined["equity"] - joined["engine"]).abs().max()
                     / joined["engine"].iloc[-1]) if len(joined) else None)
    return {"ser": ser, "stats": N.arm_stats(ser), "df": df, "diag": diag,
            "replay_max_rel": max_rel, "mean_turn": mean_turn}


def vt_pointer(is_w, oos_w):
    """What the 8% vol overlay is worth in each window, read from the face that owns it.

    results/etf_equity_alpha.json runs the same panel, seats and gate WITHOUT the vol
    target (`all_classes`). Subtracting it here answers a question this face would
    otherwise leave hanging: the earlier window is not just "smaller", it is smaller in
    part because the overlay de-levered through it. Nothing is typed in: if the face is
    absent the pointer is absent, never zero.
    """
    path = os.path.join(ROOT, "results", "etf_equity_alpha.json")
    if not os.path.exists(path):
        return {"face": None, "note": "the no-overlay face is not on disk"}
    face = _load(path)
    row = {}
    for r in (face.get("runs") or []):
        if r.get("label") == "all_classes":
            row = r
    if not row:
        return {"face": "results/etf_equity_alpha.json",
                "note": "the face has no all_classes run"}
    out = {"face": "results/etf_equity_alpha.json", "label": "all_classes",
           "no_overlay_cagr_is_pct": (None if row.get("cagr_is") is None
                                      else round(float(row["cagr_is"]) * 100.0, 3)),
           "no_overlay_cagr_oos_pct": (None if row.get("cagr_oos") is None
                                       else round(float(row["cagr_oos"]) * 100.0, 3)),
           "no_overlay_cagr_pct": (None if row.get("cagr") is None
                                   else round(float(row["cagr"]) * 100.0, 3))}
    if out["no_overlay_cagr_is_pct"] is not None and is_w.get("cagr_pct") is not None:
        out["overlay_effect_is_pp"] = round(
            is_w["cagr_pct"] - out["no_overlay_cagr_is_pct"], 3)
    if out["no_overlay_cagr_oos_pct"] is not None and oos_w.get("cagr_pct") is not None:
        out["overlay_effect_oos_pp"] = round(
            oos_w["cagr_pct"] - out["no_overlay_cagr_oos_pct"], 3)
    out["note"] = ("the same panel / seats / gate without the vol target; the difference is "
                   "what the sizing overlay did in that window, not a claim about why")
    return out


def run():
    t0 = time.time()
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    cut = price.get("evidence_cutoff")
    slice_face = _load(FACE_SLICE) if os.path.exists(FACE_SLICE) else {}
    published_select = (slice_face.get("months") or {}).get("total_pp")
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")

    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}
    score = E.build_score(close, amt, feats, min_amt=GATE)
    base = _run_base(close, openp, amt, score, cls, rebal, cost, vol_target)
    flags = state_flags(base["df"]["w_equity"])
    print("[book] cagr=%.3f%% sharpe=%s turn=%.4f replay_rel=%.2e"
          % (float(base["stats"]["full"]["cagr"]) * 100.0,
             base["stats"]["full"].get("sharpe"), base["mean_turn"],
             base["replay_max_rel"] or 0.0), flush=True)

    is_w = window_stats(base["df"], flags, "is")
    oos_w = window_stats(base["df"], flags, "oos")
    dec = bennet(is_w, oos_w)
    dec["cells"]["_share_is_equity"] = is_w["shares"]["equity"]
    dec["cells"]["_share_oos_equity"] = oos_w["shares"]["equity"]
    readable = cell_readability(is_w, oos_w)
    dom = dominant_cell({k: v for k, v in dec["cells"].items() if not k.startswith("_")},
                        dec["gap_ann_pp"], readable, {"is": is_w, "oos": oos_w})
    print("[is ] %s..%s cagr=%+.2f%% net=%+.2fpp eq_share=%.1f%% eq_rate=%s def_rate=%s"
          % (is_w["first_bar"], is_w["last_bar"], is_w["cagr_pct"], is_w["total_ann_pp"],
             100.0 * is_w["shares"]["equity"], is_w["rates_ann_pp"]["equity"],
             is_w["rates_ann_pp"]["defense"]), flush=True)
    print("[oos] %s..%s cagr=%+.2f%% net=%+.2fpp eq_share=%.1f%% eq_rate=%s def_rate=%s"
          % (oos_w["first_bar"], oos_w["last_bar"], oos_w["cagr_pct"], oos_w["total_ann_pp"],
             100.0 * oos_w["shares"]["equity"], oos_w["rates_ann_pp"]["equity"],
             oos_w["rates_ann_pp"]["defense"]), flush=True)
    print("[cells] %s gap=%+.2fpp identity_gap=%s dom=%s"
          % (dec["cells"], dec["gap_ann_pp"], dec["identity_gap_pp"], dom), flush=True)

    df = base["df"]
    m_is, m_oos = window_mask(df.index, "is"), window_mask(df.index, "oos")
    net = df["net"].astype(float).to_numpy()
    eqdays_sel = flags == True                                        # noqa: E712
    reads = {
        "net": two_sample(net[m_is], net[m_oos]),
        "equity_day_rate": two_sample(net[m_is & eqdays_sel], net[m_oos & eqdays_sel]),
        "defence_day_rate": two_sample(net[m_is & ~eqdays_sel], net[m_oos & ~eqdays_sel]),
        "equity_share": share_gap(flags[m_is], flags[m_oos]),
    }
    for k, v in reads.items():
        if v:
            print("[read %s] obs=%+.2f p_two=%.3f mde80=%.2f bars=%d/%d"
                  % (k, v["obs_pp"], v["p_two_sided"], v["mde80_pp"],
                     v["a_bars"], v["b_bars"]), flush=True)

    published_cagr = (None if published.get("cagr") is None
                      else round(float(published["cagr"]) * 100.0, 3))
    full_cagr = round(float(base["stats"]["full"]["cagr"]) * 100.0, 3)
    delta_pp = None if published_cagr is None else round(full_cagr - published_cagr, 3)
    control_select = is_w["legs_ann_pp"]["select"]  # placeholder, replaced below
    # the select leg on the WHOLE sample is what r1766 published; read it off the df
    select_full = round(float(df["select"].dropna().mean()) * PER_YEAR * 100.0, 4)
    select_delta = (None if published_select is None
                    else round(select_full - float(published_select), 4))
    control = {
        "published_cagr_pct": published_cagr, "cagr_pct": full_cagr,
        "delta_pp": delta_pp,
        "published_select_ann_pp": published_select,
        "select_ann_pp": select_full, "select_delta_pp": select_delta,
        "select_full_note": "the whole-sample select leg (what r1766 published), not a "
                            "window slice: %s" % (control_select is not None),
        "published_oos_cagr_pct": (None if published.get("oos_cagr") is None
                                   else round(float(published["oos_cagr"]) * 100.0, 3)),
        "oos_cagr_pct": oos_w.get("cagr_pct"),
        "oos_delta_pp": (None if published.get("oos_cagr") is None
                         or oos_w.get("cagr_pct") is None
                         else round(oos_w["cagr_pct"]
                                    - float(published["oos_cagr"]) * 100.0, 3)),
        "oos_note": "the second control: this face's OOS window must reproduce the printed "
                    "oos_cagr cell (same arm, same boundary) -- a window statistic that "
                    "disagrees with the cell it is made of would make every cell unreadable",
        "replay_max_rel": base["replay_max_rel"],
        "replay_ok": (base["replay_max_rel"] is not None
                      and base["replay_max_rel"] <= REPLAY_TOL),
        "ok": (delta_pp is not None and abs(delta_pp) <= CONTROL_TOL_PP
               and (select_delta is None or abs(select_delta) <= SELECT_TOL_PP)
               and (oos_w.get("cagr_pct") is not None
                    and published.get("oos_cagr") is not None
                    and abs(oos_w["cagr_pct"]
                            - float(published["oos_cagr"]) * 100.0) <= CONTROL_TOL_PP)
               and (base["replay_max_rel"] is not None
                    and base["replay_max_rel"] <= REPLAY_TOL)),
    }
    verdict = classify(control, reads["net"], dec["cells"], dom)
    pointer = vt_pointer(is_w, oos_w)

    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": (cut or str(close.index[-1].date())),
        "panel_last_bar": str(close.index[-1].date()),
        "config": {"bench": BENCH, "gate_cny": GATE, "seats": SEATS, "rebal": rebal,
                   "cost_bp_per_side": round(cost * 1e4, 3), "vol_target": vol_target,
                   "is_end": IS_END, "start": str(R.START)},
        "control": control,
        "windows": {"is": is_w, "oos": oos_w},
        "decomposition": dec,
        "dominant_cell": dom,
        "vt_pointer": pointer,
        "reads": reads,
        "read_units": {"net": "pp of annualised net return",
                       "equity_day_rate": "pp of annualised net return on equity bars",
                       "defence_day_rate": "pp of annualised net return on defence bars",
                       "equity_share": "pp of time"},
        "identity": {"legs_ok": all(abs(w["legs_ann_pp"]["identity_gap_pp"]) <= IDENTITY_TOL
                                    for w in (is_w, oos_w)),
                     "legs_tol_pp": IDENTITY_TOL,
                     "state_ok": all(abs(w["state_identity_gap_pp"]) <= 1e-6
                                     for w in (is_w, oos_w)),
                     "decomp_ok": (dec["identity_gap_pp"] is not None
                                   and abs(dec["identity_gap_pp"]) <= 1e-4)},
        "series": {
            "note": "the single input of every bootstrap in this face: per-window daily net "
                    "returns and the equity flag, rounded to 8dp, so --check re-derives the "
                    "bootstrap, the cells and the verdict instead of trusting the print",
            "is": {"net": [round(float(v), 8) for v in net[m_is]],
                   "flag": [int(v) for v in flags[m_is]]},
            "oos": {"net": [round(float(v), 8) for v in net[m_oos]],
                    "flag": [int(v) for v in flags[m_oos]]},
            "dates": {"is": [str(d.date()) for d in df.index[m_is]],
                      "oos": [str(d.date()) for d in df.index[m_oos]]},
        },
        "verdict": verdict["verdict"],
        "sentence": verdict["sentence"],
        "ruler": {"block": BLOCK, "draws": DRAWS, "seed": SEED, "z80": Z80,
                  "p_sep": P_SEP, "cell_share_line": CELL_SHARE_LINE},
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[verdict] %s | identity=%s | %.1fs"
          % (out["verdict"], out["identity"], out["elapsed_sec"]), flush=True)
    return out


# ---------------------------------------------------------------- markdown

def write_md():
    d = _load(OUT_JSON)
    is_w, oos_w = d["windows"]["is"], d["windows"]["oos"]
    dec, dom, reads = d["decomposition"], d.get("dominant_cell"), d["reads"]
    cut = d["evidence_cutoff"]
    L = []
    L.append("# 前段 6%、后段 18%：差在在场时间还是权益自己（r1770）")
    L.append("> evidence_cutoff=%s；面板末 bar=%s；脚本 `scripts/etf_book_window_split.py`；"
             "证据 `results/etf_book_window_split.json`。" % (cut, d["panel_last_bar"]))
    L.append("> 分界=%s（与 r1765/r1766 同一口径）；尺子=圆形块自助 块长 %d／%d 次／种子 %d。"
             % (d["config"]["is_end"], d["ruler"]["block"], d["ruler"]["draws"],
                d["ruler"]["seed"]))
    L.append("## 问的问题")
    L.append("前几面把这本书切成两段读时都记着同一件事：2020-2023 只有 6% 上下，2024 年以来"
             "15~20%。过去对此只给过一句「2024 年以前靠债券防守」，没有数字。本轮把年化差"
             "精确切成四格：**在场时间**（权益档出现得多不多）与**每档日收益速度**"
             "（开着的时候和躲着的时候各自赚多少）。")
    L.append("")
    L.append("## 两段各自的样子")
    L.append("| 段 | 区间 | bars | 年化 | 夏普 | 最大回撤 | 净收益(年化pp) | 指数项 | 权益档占比 | 权益档日速度 | 防守档日速度 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for w in (is_w, oos_w):
        L.append("| %s | %s→%s | %d | %s | %s | %s | %+.2f | %+.2f | %.1f%% | %s | %s |"
                 % (w["window"], w["first_bar"], w["last_bar"], w["bars"],
                    ("%+.2f%%" % w["cagr_pct"]) if w["cagr_pct"] is not None else "-",
                    ("%.3f" % w["sharpe"]) if w["sharpe"] is not None else "-",
                    ("%+.2f%%" % w["maxdd_pct"]) if w["maxdd_pct"] is not None else "-",
                    w["total_ann_pp"], w["bench_ann_pp"], 100.0 * w["shares"]["equity"],
                    ("%+.2fpp" % w["rates_ann_pp"]["equity"])
                    if w["rates_ann_pp"]["equity"] is not None else "-",
                    ("%+.2fpp" % w["rates_ann_pp"]["defense"])
                    if w["rates_ann_pp"]["defense"] is not None else "-"))
    L.append("")
    L.append("「日速度」= 该档上的日净收益均值年化到 pp（252 口径，与全书同一条尺）；"
             "它不是可复利的年化收益，只是让两段的速度可比。")
    L.append("")
    L.append("## 四格分解（Bennet 中点，恒等式钉死）")
    L.append("| 格 | 含义 | pp | 占全场 |")
    L.append("|---|---|---|---|")
    mean_of = {"mix_equity": "权益档占比变化 × 两段平均权益日速度",
               "mix_defense": "防守档占比变化 × 两段平均防守日速度（占比变化相同，金额不同）",
               "rate_equity": "权益档日速度变化 × 两段平均占比",
               "rate_defense": "防守档日速度变化 × 两段平均占比"}
    gap = dec["gap_ann_pp"]
    for k in CELLS:
        v = dec["cells"].get(k)
        share = ("%.0f%%" % (100.0 * abs(v) / abs(gap))) if (v is not None and gap) else "-"
        L.append("| %s | %s | %s | %s |"
                 % (k, mean_of[k], ("%+.2f" % v) if v is not None else "-", share))
    L.append("| **合计** | 恒等式：四格之和 == 两段年化差 | %s | 差 %s pp |"
             % (("%+.2f" % dec["cells_sum_pp"]) if dec["cells_sum_pp"] is not None else "-",
                dec["identity_gap_pp"]))
    L.append("")
    L.append("读这个表只有一条纪律：**占比变化那一格本身不是原因**，它必须乘上日速度才是钱。"
             "「权益档从 %.0f%% 变成 %.0f%%」听上去像原因，可如果两档日速度差不多，"
             "换档就换不来钱。"
             % (100.0 * is_w["shares"]["equity"], 100.0 * oos_w["shares"]["equity"]))
    L.append("")
    L.append("## 差能不能被看见（三种读法各自答一次）")
    L.append("| 读法 | 观测差 | 标准误 | MDE80 | t | 双向 p | 单位 |")
    L.append("|---|---|---|---|---|---|---|")
    for k in ("net", "equity_day_rate", "defence_day_rate", "equity_share"):
        r = reads.get(k)
        if not r:
            L.append("| %s | 读不出（该档在某一段少于 40 根 bar，分块自助拒答） | - | - | - | - | - |"
                     % k)
            continue
        L.append("| %s | %+.2f | %.2f | %.2f | %s | %.3f | %s |"
                 % (k, r["obs_pp"], r["se_pp"], r["mde80_pp"],
                    ("%.2f" % r["t"]) if r["t"] is not None else "-",
                    r["p_two_sided"], d["read_units"][k]))
    L.append("")
    L.append("「占比」那一行的单位是时间 pp，不是收益 pp——它只回答「多开了多久」，"
             "而多开的那些时间值不值钱，看前一节的两格。")
    L.append("")
    L.append("## 判词")
    L.append("**%s** — %s" % (d["verdict"], d["sentence"]))
    if dom:
        L.append("")
        L.append("最大的那一格是 `%s`（%+.2fpp，占全场 %.0f%%）%s。"
                 % (dom["cell"], dom["pp"], 100.0 * dom["share_of_gap"],
                    "" if dom.get("readable", True)
                    else "，但它建在 %s/%s 根 bar 上，本面不拿它当原因"
                         % ((dom.get("state_bars") or {}).get("is"),
                            (dom.get("state_bars") or {}).get("oos"))))
    vp = d.get("vt_pointer") or {}
    if vp.get("no_overlay_cagr_is_pct") is not None:
        L.append("")
        L.append("## 横向：8% 波动目标在两段各值多少")
        L.append("同一张面板、同一批座位与流动性闸、**不带**波动目标的那本书"
                 "（`%s` 的 `all_classes`）前段 %+.2f%%／后段 %+.2f%%；"
                 "带上波动目标以后是 %+.2f%%／%+.2f%%——"
                 "**波动目标在前段拿走 %.2fpp、在后段给回 %.2fpp**。"
                 % (vp["face"], vp["no_overlay_cagr_is_pct"], vp["no_overlay_cagr_oos_pct"],
                    is_w["cagr_pct"], oos_w["cagr_pct"],
                    abs(vp.get("overlay_effect_is_pp") or 0.0),
                    abs(vp.get("overlay_effect_oos_pp") or 0.0)))
        L.append("")
        L.append("这条只说明「缩放层在两段各做了什么」，不说明为什么：前段波动高、降杠杆降得多，"
                 "后段波动低、几乎不降——但两段的环境不同，不能据此说波动目标是好政策还是坏政策。")
    L.append("")
    L.append("## 控制臂")
    c = d["control"]
    L.append("- 全书年化 %+.2f%%（在印 %s%%，差 %s pp，容差 %.2fpp）"
             % (c["cagr_pct"], c["published_cagr_pct"], c["delta_pp"], CONTROL_TOL_PP))
    L.append("- 选股腿 %+.4fpp（在印 %s，差 %s pp）"
             % (c["select_ann_pp"], c["published_select_ann_pp"], c["select_delta_pp"]))
    L.append("- 重放重建引擎净值：最大相对偏差 %.2e（容差 %.0e）"
             % (c["replay_max_rel"] or 0.0, REPLAY_TOL))
    L.append("- 四腿加性：`select+rotate+size+cost+r_bench == net`，两段缺口 %s / %s pp"
             "（容差 %.2fpp）；状态加权恒等：`Σ 占比×速度 == 该段净收益`，缺口 %s / %s pp"
             % (is_w["legs_ann_pp"]["identity_gap_pp"],
                oos_w["legs_ann_pp"]["identity_gap_pp"], IDENTITY_TOL,
                is_w["state_identity_gap_pp"], oos_w["state_identity_gap_pp"]))
    L.append("")
    L.append("## 局限（读之前先读这段）")
    L.append("- 两段是按日历切的，不是随机切的：所谓「前段差」里包含 2021-2022 那一轮下跌"
             "与 2020 的建仓期，不是干净的对照实验。")
    L.append("- 面板是现存 ETF（幸存者偏差照旧）；越靠后的段，面板里的标的越「活下来」，"
             "这件事对后段只会更有利，本面无法扣除。")
    L.append("- 四格分解是恒等式，不是因果：它只说差从哪几项数出来，不说为什么会这样。")
    L.append("- 「日速度」是算术年化，不是可复利收益；两段 bar 数不同，直接比日速度比年化安全。")
    L.append("- 债券 carry 与权益趋势都是外生环境，本面不区分「风格好」与「环境好」。")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("[md] %s (%d lines)" % (OUT_MD, len(L)), flush=True)
    return OUT_MD


# ---------------------------------------------------------------- check

def _check():
    d = _load(OUT_JSON)
    problems = []
    c = d["control"]
    if not c.get("ok"):
        problems.append("the control arm does not reproduce the published book")
    if not c.get("replay_ok"):
        problems.append("the replay does not rebuild the engine curve")
    ident = d.get("identity") or {}
    for key in ("legs_ok", "state_ok", "decomp_ok"):
        if not ident.get(key):
            problems.append("identity leg %s does not hold" % key)

    ser = d["series"]
    is_net = ser["is"]["net"]
    oos_net = ser["oos"]["net"]
    is_flag = ser["is"]["flag"]
    oos_flag = ser["oos"]["flag"]

    # 1) the windows' own stats must re-derive from the stored series
    for wkey, net, flag in (("is", is_net, is_flag), ("oos", oos_net, oos_flag)):
        w = d["windows"][wkey]
        if int(w["bars"]) != len(net) or len(net) != len(flag):
            problems.append("%s bars do not match the stored series" % wkey)
            continue
        ann = float(np.mean(net)) * PER_YEAR * 100.0
        if abs(ann - float(w["total_ann_pp"])) > 1e-3:
            problems.append("%s annualised net re-derives to %.4f, face says %.4f"
                            % (wkey, ann, w["total_ann_pp"]))
        share = float(np.mean([1.0 if f else 0.0 for f in flag]))
        if abs(share - float(w["shares"]["equity"])) > 1e-6:
            problems.append("%s equity share re-derives to %.6f, face says %.6f"
                            % (wkey, share, w["shares"]["equity"]))

    # 2) the four cells must re-derive, and the identity must close
    again = bennet(d["windows"]["is"], d["windows"]["oos"])
    for k in CELLS:
        got, want = again["cells"].get(k), d["decomposition"]["cells"].get(k)
        if (got is None) != (want is None):
            problems.append("cell %s missing on one side" % k)
        elif got is not None and abs(got - float(want)) > 1e-3:
            problems.append("cell %s re-derives to %s, face says %s" % (k, got, want))
    if again["gap_ann_pp"] != d["decomposition"]["gap_ann_pp"]:
        problems.append("gap re-derives to %s, face says %s"
                        % (again["gap_ann_pp"], d["decomposition"]["gap_ann_pp"]))
    if again["identity_gap_pp"] is None or abs(again["identity_gap_pp"]) > 1e-4:
        problems.append("the four cells no longer sum to the gap")

    # 3) every published p / MDE80 re-derives from the stored series
    eqis = np.asarray(is_net, dtype=float)[np.asarray(is_flag, dtype=bool)]
    eqoos = np.asarray(oos_net, dtype=float)[np.asarray(oos_flag, dtype=bool)]
    dfis = np.asarray(is_net, dtype=float)[~np.asarray(is_flag, dtype=bool)]
    dfoos = np.asarray(oos_net, dtype=float)[~np.asarray(oos_flag, dtype=bool)]
    pairs = {
        "net": (np.asarray(is_net, dtype=float), np.asarray(oos_net, dtype=float)),
        "equity_day_rate": (eqis, eqoos),
        "defence_day_rate": (dfis, dfoos),
    }
    for k, (a, b) in pairs.items():
        face = (d["reads"] or {}).get(k)
        got = two_sample(a, b)
        if face is None:
            continue
        if got is None:
            problems.append("%s no longer re-derives but the face prints it" % k)
            continue
        if abs(got["obs_pp"] - float(face["obs_pp"])) > 1e-3:
            problems.append("%s obs re-derives to %s, face says %s"
                            % (k, got["obs_pp"], face["obs_pp"]))
        if int(got["p_two_sided"] * 10000 + 0.5) != int(float(face["p_two_sided"]) * 10000 + 0.5):
            problems.append("%s p re-derives to %s, face says %s"
                            % (k, got["p_two_sided"], face["p_two_sided"]))
        if abs(got["mde80_pp"] - float(face["mde80_pp"])) > 1e-3:
            problems.append("%s MDE80 re-derives to %s, face says %s"
                            % (k, got["mde80_pp"], face["mde80_pp"]))
    sg_face = (d["reads"] or {}).get("equity_share")
    if sg_face is not None:
        sg = share_gap(is_flag, oos_flag)
        if sg is None:
            problems.append("the equity-share read no longer re-derives")
        elif int(sg["p_two_sided"] * 10000 + 0.5) != int(float(sg_face["p_two_sided"]) * 10000 + 0.5):
            problems.append("share p re-derives to %s, face says %s"
                            % (sg["p_two_sided"], sg_face["p_two_sided"]))

    # 4) the verdict must re-derive, and the dominant cell must still be the same one
    readable = cell_readability(d["windows"]["is"], d["windows"]["oos"])
    dom = dominant_cell({k: v for k, v in again["cells"].items() if not k.startswith("_")},
                        again["gap_ann_pp"], readable,
                        {"is": d["windows"]["is"], "oos": d["windows"]["oos"]})
    v = classify(c, (d["reads"] or {}).get("net"), again["cells"], dom)
    if v["verdict"] != d["verdict"]:
        problems.append("verdict re-derives to %s, face says %s" % (v["verdict"], d["verdict"]))
    if (dom or {}).get("cell") != (d.get("dominant_cell") or {}).get("cell"):
        problems.append("dominant cell re-derives to %s, face says %s"
                        % ((dom or {}).get("cell"), (d.get("dominant_cell") or {}).get("cell")))
    if (dom or {}).get("readable") != (d.get("dominant_cell") or {}).get("readable"):
        problems.append("dominant cell readability re-derives to %s, face says %s"
                        % ((dom or {}).get("readable"),
                           (d.get("dominant_cell") or {}).get("readable")))
    ok = not problems
    print(json.dumps({"ok": ok, "problems": problems, "verdict": v["verdict"],
                      "gap_pp": again["gap_ann_pp"],
                      "dominant_cell": (dom or {}).get("cell")}, ensure_ascii=False))
    return 0 if ok else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # L1 the state is the engine's own w_equity, not a re-derivation
    f = state_flags([0.0, 0.4, 1.0, 0.0])
    leg("L1 w_equity>0 is equity, ==0 is defence", list(f) == [False, True, True, False])

    # L2 the boundary: the last IS bar is in, the first OOS bar is out
    idx = [pd.Timestamp("2023-12-29"), pd.Timestamp("2023-12-31"), pd.Timestamp("2024-01-02")]
    leg("L2 the calendar split puts 2023-12-31 in IS and 2024-01-02 in OOS",
        list(window_mask(idx, "is")) == [True, True, False]
        and list(window_mask(idx, "oos")) == [False, False, True])

    # L3 the window rate is the published definition (A.stats2), not a hand-rolled one:
    # a slice of a running curve must be normalised on ITS OWN first level (the r1262 trap),
    # and the year count is the calendar, not bars/252.
    eq = pd.Series(np.linspace(1.23, 1.50, 260),
                   index=pd.bdate_range("2020-01-01", periods=260))
    st = seg_stats(eq, "t")
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    want = (1.50 / 1.23) ** (1.0 / yrs) - 1.0
    naive = eq.iloc[-1] ** (1.0 / yrs) - 1.0          # blind to the slice's own start level
    leg("L3 the window rate is normalised on the slice's own first level",
        abs(float(st["cagr"]) - want) < 5e-5 and abs(naive - float(st["cagr"])) > 0.10)

    # L4 the state identity: shares x rates reproduce the window's own net
    is_w = {"shares": {"equity": 0.75, "defense": 0.25},
            "rates_ann_pp": {"equity": 10.0, "defense": 2.0},
            "total_ann_pp": 8.0}
    oos_w = {"shares": {"equity": 0.90, "defense": 0.10},
             "rates_ann_pp": {"equity": 20.0, "defense": 3.0},
             "total_ann_pp": 18.3}
    dec = bennet(is_w, oos_w)
    leg("L4 the four cells sum to the window gap",
        dec["cells_sum_pp"] is not None and abs(dec["identity_gap_pp"]) < 1e-6
        and abs(dec["gap_ann_pp"] - 10.3) < 1e-9)

    # L5 a pure share change lands in the mix cells; mix_defence is NOT its mirror image
    # (they differ by the two states' rates), which is why both are printed separately.
    pure = bennet({"shares": {"equity": 0.5, "defense": 0.5},
                   "rates_ann_pp": {"equity": 10.0, "defense": 2.0},
                   "total_ann_pp": 6.0},
                  {"shares": {"equity": 1.0, "defense": 0.0},
                   "rates_ann_pp": {"equity": 10.0, "defense": 2.0},
                   "total_ann_pp": 10.0})
    leg("L5 a pure time shift is carried by the mix cells, and the two mix cells differ",
        abs(pure["cells"]["mix_equity"] - 5.0) < 1e-6
        and abs(pure["cells"]["mix_defense"] + 1.0) < 1e-6
        and abs(pure["cells"]["rate_equity"]) < 1e-9
        and abs(pure["cells"]["mix_defense"] + pure["cells"]["mix_equity"]) > 1.0)

    # L6 a pure rate change lands in the rate cells and the reader can name it
    pr = bennet({"shares": {"equity": 1.0, "defense": 0.0},
                 "rates_ann_pp": {"equity": 5.0, "defense": 0.0},
                 "total_ann_pp": 5.0},
                {"shares": {"equity": 1.0, "defense": 0.0},
                 "rates_ann_pp": {"equity": 12.0, "defense": 0.0},
                 "total_ann_pp": 12.0})
    dom = dominant_cell(pr["cells"], pr["gap_ann_pp"])
    leg("L6 a pure rate change is named rate_equity with a 100% share",
        dom and dom["cell"] == "rate_equity" and abs(dom["share_of_gap"] - 1.0) < 1e-9)

    # L7 no gap => no dominant cell, never "explained"
    leg("L7 a zero gap has no dominant cell",
        dominant_cell({"mix_equity": 0.0, "rate_equity": 0.0}, 0.0) is None)

    # L8 the two-sample ruler refuses thin samples instead of narrowing them
    leg("L8 a thin sample returns None rather than a number",
        two_sample(np.zeros(10), np.zeros(10)) is None
        and two_sample(np.zeros(80), np.zeros(80)) is not None)

    # L9 the same distribution on both sides must not claim a direction
    rng = np.random.default_rng(11)
    a = rng.normal(0.0003, 0.01, 900)
    b = rng.normal(0.0003, 0.01, 600)
    r = two_sample(a, b)
    leg("L9 identical distributions read p_two > 0.05", r and r["p_two_sided"] > 0.05)

    # L10 a planted gap must be found, with a big t
    b2 = rng.normal(0.0025, 0.01, 600)
    r2 = two_sample(a, b2)
    leg("L10 a planted gap reads the right sign with p_two < 0.01",
        r2 and r2["obs_pp"] > 0 and r2["p_two_sided"] < 0.01 and r2["t"] > 3.0)

    # L11 an all-zero difference cannot claim a direction (r1768's lesson, same ruler)
    z = two_sample(np.zeros(900), np.zeros(600))
    leg("L11 an all-zero pair reads p=1.0 and obs=0", z and z["p_direction"] == 1.0
        and z["obs_pp"] == 0.0)

    # L12 a share read is the same machinery on 0/1, and its unit says so
    sa = share_gap(np.zeros(900), np.zeros(600))
    sb = share_gap(np.zeros(900), np.ones(600))
    leg("L12 the share read keeps its own unit and finds a planted 100pp shift",
        sa and sa["unit"] == "pp_of_time" and sb and abs(sb["obs_pp"] - 100.0) < 1e-9)

    # L13 verdict mapping: the frozen decision tree
    good = {"ok": True, "replay_ok": True, "delta_pp": 0.0, "select_delta_pp": 0.0}
    big = {"obs_pp": 10.0, "mde80_pp": 2.0, "p_two_sided": 0.001, "draws": DRAWS}
    small = {"obs_pp": 1.0, "mde80_pp": 5.0, "p_two_sided": 0.40, "draws": DRAWS}
    cells = {"mix_equity": 8.0, "mix_defense": -8.0, "rate_equity": 1.0, "rate_defense": 1.0}
    leg("L13 a gap inside its own MDE80 is never explained",
        classify(good, small, cells, dominant_cell(cells, 10.0))["verdict"]
        == "WINDOW_GAP_NOT_SEPARABLE")
    leg("L13b a time-shift gap is named TIME_IN_EQUITY_EXPLAINS",
        classify(good, big, cells, dominant_cell(cells, 10.0))["verdict"]
        == "TIME_IN_EQUITY_EXPLAINS")
    cells2 = {"mix_equity": 0.5, "mix_defense": -0.5, "rate_equity": 8.0, "rate_defense": 0.5}
    leg("L13c a rate gap is named EQUITY_DAY_RATE_EXPLAINS",
        classify(good, big, cells2, dominant_cell(cells2, 9.0))["verdict"]
        == "EQUITY_DAY_RATE_EXPLAINS")
    flat = {"mix_equity": 3.0, "mix_defense": -3.0, "rate_equity": 3.0, "rate_defense": 3.0}
    leg("L13d a gap spread over every cell is named NO_SINGLE_CELL",
        classify(good, big, flat, dominant_cell(flat, 12.0))["verdict"] == "NO_SINGLE_CELL")

    # L14 a broken control is never judged, whatever the cells say
    leg("L14 a control off the published cell blocks the verdict",
        classify(dict(good, ok=False), big, cells, dominant_cell(cells, 10.0))["verdict"]
        == "CANNOT_JUDGE_CONTROL")

    # L14b a cell built on a handful of bars may be printed but never named as the reason
    thin_w = {"is": {"equity_bars": 900, "defense_bars": 500},
              "oos": {"equity_bars": 700, "defense_bars": 20}}
    thin_read = cell_readability(thin_w["is"], thin_w["oos"])
    thin_cells = {"mix_equity": 0.5, "mix_defense": -0.5,
                  "rate_equity": 1.0, "rate_defense": 9.0}
    thin_dom = dominant_cell(thin_cells, 10.0, thin_read, thin_w)
    leg("L14b a 20-bar state cannot be named as the reason",
        thin_read["rate_defense"] is False and thin_read["rate_equity"] is True
        and thin_dom["cell"] == "rate_defense" and thin_dom["readable"] is False
        and classify(good, big, thin_cells, thin_dom)["verdict"] == "NO_SINGLE_CELL")

    # L15 the attribution identity is the replay's own contract (r1764's trap)
    at = MM.attribute({"X": 0.5, "Y": 0.5}, {"X": 0.02, "Y": -0.01},
                      {"X": "equity", "Y": "equity"}, 0.005, 0.0001)
    gapv = (at["select"] + at["rotate"] + at["size"] + at["cost"] + 0.005) - at["net"]
    leg("L15 select+rotate+size+cost+r_bench == net", abs(gapv) < 1e-12)

    # L16 the ruler constants are the published ones
    leg("L16 ruler constants are the published ones",
        (BLOCK, DRAWS, SEED) == (20, 2000, 20261116))

    # L17 the defence/equity split has no third state hiding in it
    f2 = state_flags([0.0, 0.0, 0.33])
    leg("L17 every bar is exactly one of the two states",
        all(bool(x) in (True, False) for x in f2)
        and int((f2 == True).sum()) + int((f2 == False).sum()) == 3)   # noqa: E712

    ok = sum(1 for _n, c in legs if c)
    for name, cond in legs:
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
    print("etf_book_window_split selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "run":
        d = run()
        print(json.dumps({"verdict": d["verdict"], "evidence_cutoff": d["evidence_cutoff"]},
                         ensure_ascii=False))
        return 0
    if cmd == "md":
        write_md()
        return 0
    if cmd in ("check", "verify"):
        return _check()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
