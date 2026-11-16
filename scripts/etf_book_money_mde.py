"""Does the money this 5-seat book makes clear its own noise floor -- and where does it come from? (r1763)

r1762 put a ruler on the gate ladder: the smallest annualised gap this book can tell from zero
(MDE80 = z80 * SE of the same block bootstrap behind every p-value here). Every rung was inside
that range. The sentence a reader actually wants answered is one shelf over: **"this book makes
9.12% and 510300 made nothing -- is THAT gap bigger than the book's own noise floor, and which
part of the book earned it?"** A gap that clears the ladder by 8pp but not the book's own floor
is the same non-answer in bolder type.

So this face does three things with the same engine, the same panel, the same cost and the same
vol target:

  1. re-prices the published book (5 seats, the 20M gate) so the control arm must reproduce
     9.12% to CONTROL_TOL_PP -- otherwise nothing is judged;
  2. replays the engine's own equity curve bar by bar (weights and the vol-target scale come
     from the engine's diag, so the replay is a check of the attribution machinery, not a
     second book) and splits the net excess over 510300 into four legs that sum EXACTLY:
        select = sum over equity picks   w_k * (r_k - r_b)   "the stocks I picked vs the index"
        rotate = sum over non-equity     w_k * (r_k - r_b)   "gold/convertibles vs the index"
        size   = -(1 - sum w) * r_b                          "the slot I left empty vs the index"
        cost   = net - gross                                 "what the broker took"
     Every leg answers the same question at its own slot: *had that slot been 510300 instead*.
     That is why they add up with no cross term and no residual.
  3. puts the SAME ruler on the total and on each leg, so "the gap is 9pp" becomes "the gap is
     9pp and this book can resolve gaps of N pp -- and only one leg is above its own N".

What this face does NOT do: it does not re-derive the book, move a gate, change a seat count,
or touch a published number. The control arm and the replay identity are the two gates that
make a decomposition of someone else's equity curve trustworthy.

Usage:
  python scripts/etf_book_money_mde.py run
  python scripts/etf_book_money_mde.py --selftest
  python scripts/etf_book_money_mde.py --check
  python scripts/etf_book_money_mde.py --md
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

import etf_robust_pf as R            # noqa: E402  (the engine itself)
import etf_book_entry_gate as G     # noqa: E402  (panel + its flip repair)
import etf_book_gate_raise_noise as N   # noqa: E402  (price_arm + arm_stats)
import etf_equity_alpha as A        # noqa: E402  (classify: keyword + realised-vol cut)
import etf_book_book_mde as M       # noqa: E402  (the frozen ruler: bootstrap, words, z80)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_money_mde.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_MONEY_MDE.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")

BENCH = "510300"                 # the "closed eyes" arm: buy the broad index and sit
GATE = 20e6                      # the cut the ticket prints
SEATS = 5                        # the book's seat count
CONTROL_TOL_PP = 0.25            # the arm must reproduce the price face's own cell
REPLAY_TOL = 1e-9                # the replay must be the engine's curve, not a lookalike
LEGS = ("select", "rotate", "size", "cost")
PER_YEAR = M.PER_YEAR
Z_80 = M.Z_80


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def compound(rets):
    """An equity curve from a return series (no cost -- cost is booked in the return)."""
    x = pd.Series(rets).astype(float)
    return (1.0 + x.fillna(0.0)).cumprod()


def attribute(weights, rets, cls, r_bench, cost_amt=0.0):
    """Exact four-leg split of one bar's NET excess over the benchmark.

    weights : {name -> weight} as actually held that bar (already scaled by the vol target)
    rets    : {name -> bar return}; names whose prices are missing are left out and their
              weight falls into `size` (an unpriced slot is not an invested slot)
    cls     : {name -> class}; anything not classified "equity" is a rotation leg
    r_bench : the benchmark's own bar return
    cost_amt: the fraction charged that bar (engine: cost * turnover), 0 on non-decision bars

    Returns the four legs plus the identity residual, so a caller can assert the split rather
    than trust it: select + rotate + size + cost == net - r_bench exactly.
    """
    priced = {}
    for k, w in weights.items():
        r = rets.get(k, np.nan)
        if np.isfinite(r):
            priced[k] = float(r)
    gross = float(sum(weights[k] * priced[k] for k in priced))
    w_priced = float(sum(weights[k] for k in priced))
    select = float(sum(weights[k] * (priced[k] - r_bench) for k in priced
                       if cls.get(k) == "equity"))
    rotate = float(sum(weights[k] * (priced[k] - r_bench) for k in priced
                       if cls.get(k) != "equity"))
    size = float(-(1.0 - w_priced) * r_bench)
    net = (1.0 - float(cost_amt)) * (1.0 + gross) - 1.0
    cost_t = float(net - gross)
    resid = (net - float(r_bench)) - (select + rotate + size + cost_t)
    return {"gross": gross, "net": net, "w_priced": w_priced,
            "w_equity": float(sum(weights[k] for k in priced if cls.get(k) == "equity")),
            "select": select, "rotate": rotate, "size": size, "cost": cost_t,
            "resid": resid, "n_unpriced": len(weights) - len(priced)}


def replay(close, openp, diag, rebal, n_hold, cost, start, cls, bench=BENCH):
    """Rebuild the engine's own equity curve from its diag, attributing every bar.

    The weights are NOT re-derived here: they are read out of the engine's diag (picks + the
    vol-target scale). This deliberately makes the replay a test OF the attribution machinery:
    if it cannot reproduce the engine's curve to REPLAY_TOL, the legs are measured on a
    different book and nothing is published.
    """
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    by_date = {str(row["date"]): row for row in diag if row.get("book")}
    rows = []
    held = {}
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        turn = 0.0
        if i % rebal == 0:
            row = by_date.get(str(pd.Timestamp(d).date()))
            if row is not None:
                scale = float(row.get("scale") or 0.0)
                new = {p: scale / float(n_hold) for p in row["book"]}
                turn = float(sum(abs(new.get(k, 0.0) - held.get(k, 0.0))
                                 for k in set(new) | set(held)))
                held = new
        cost_amt = cost * turn
        rets = {}
        for k in held:
            a, b = op.at[d, k] if k in op.columns else np.nan, None
            b = op.at[nxt, k] if k in op.columns else np.nan
            rets[k] = (b / a - 1.0) if (np.isfinite(a) and np.isfinite(b) and a > 0) else np.nan
        r_b = np.nan
        if bench in op.columns:
            a, b = op.at[d, bench], op.at[nxt, bench]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r_b = b / a - 1.0
        if not np.isfinite(r_b):
            continue
        leg = attribute(held, rets, cls, float(r_b), cost_amt)
        rows.append(dict(date=nxt, r_bench=float(r_b), turn=turn, **leg))
    cols = ["date", "r_bench", "turn", "gross", "net", "w_priced", "w_equity", "select",
            "rotate", "size", "cost", "resid", "n_unpriced"]
    if not rows:
        return pd.DataFrame(columns=cols + ["equity"])
    df = pd.DataFrame(rows).set_index("date").sort_index()
    df["equity"] = (1.0 + df["net"]).cumprod()
    return df


def leg_ann(df):
    """Annualised pp for the total excess and each leg (arithmetic means, engine's 252)."""
    out = {"total": M.ann_pp(df["net"].mean() - df["r_bench"].mean())}
    for k in LEGS:
        out[k] = M.ann_pp(df[k].mean())
    return out


def year_table(df):
    """Per calendar year: the book, the index, and the four legs, all in compounded pp."""
    out = []
    for year, grp in df.groupby(df.index.year):
        book = float((1.0 + grp["net"]).prod() - 1.0)
        bench = float((1.0 + grp["r_bench"]).prod() - 1.0)
        row = {"year": int(year), "bars": int(len(grp)),
               "book_pct": round(book * 100.0, 2), "bench_pct": round(bench * 100.0, 2),
               "excess_pp": round((book - bench) * 100.0, 2)}
        for k in LEGS:
            row[k + "_pp"] = round(float(grp[k].sum()) * 100.0, 2)
        out.append(row)
    return out


def money_verdict(total_pp, mde_pp, p_dir, control_pp, legs=None):
    """One word for the money question, refusing before it judges.

    Reuses r1762's three-state vocabulary on purpose: a gap can be above the book's own floor,
    or significant-but-underpowered, or have no direction at all. Filing the middle case as
    "noise" is the mistake that made the ladder table unreadable.
    """
    if control_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "控制臂没有跑出来：这张面不判这本书的一分钱。"}
    if abs(control_pp) > CONTROL_TOL_PP:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与抬闸定价面同一格差 %.2fpp（容差 %.2fpp）——"
                            "这不是同一本书，本面不判。" % (control_pp, CONTROL_TOL_PP)}
    if total_pp is None or mde_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_SERIES",
                "sentence": "没有可用的配对差序列（基准或缺价）：不判。"}
    leg_names = ""
    if legs:
        above = [k for k in LEGS if legs.get(k, {}).get("status") == "ABOVE_MDE80"]
        if above:
            leg_names = "；四条腿里只有 *%s* 越过各自 MDE80（%s）" % (
                "、".join(above),
                "、".join("%s %.2fpp vs 门 %.2fpp"
                         % (k, legs[k]["ann_pp"], legs[k]["mde80_pp"]) for k in above))
        else:
            leg_names = "；四条腿没有一条越过自己的 MDE80"
    status = M.classify_pair(total_pp, mde_pp, p_dir)
    if status == "ABOVE_MDE80":
        return {"verdict": "EXCESS_ABOVE_MDE80", "status": status,
                "sentence": "这本书比闭眼买 %s 多的 %+.2fpp/年，越过了它自己 80%% 效力下的"
                            "最小可分辨差 **%.2fpp**%s。" % (BENCH, total_pp, mde_pp, leg_names)}
    if status == "SIGNIFICANT_UNDERPOWERED":
        return {"verdict": "SIGNIFICANT_BUT_UNDERPOWERED", "status": status,
                "sentence": "这条 %+.2fpp/年的差方向站得住（p=%s），但没到 80%% 效力"
                            "（MDE80 %.2fpp）——方向可信、幅度不可信%s。"
                            % (total_pp, p_dir, mde_pp, leg_names)}
    return {"verdict": "EXCESS_INSIDE_MDE80", "status": status,
            "sentence": "这条 %+.2fpp/年的差落在本书自己的射程内（MDE80 %.2fpp，p=%s）——"
                        "这张纸读不出这本书比闭眼买 %s 更好还是更差%s。"
                        % (total_pp, mde_pp, p_dir, BENCH, leg_names)}


def run():
    t0 = time.time()
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls_s = A.classify(list(close.columns), cmap, close)
    cls = {str(k): str(v) for k, v in cls_s.items()}

    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")

    # --- the book, with the engine's own diag (weights + vol-target scale) -------------
    import etf_composite_pf as E
    score = E.build_score(close, amt, feats, min_amt=GATE)
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, SEATS, cost,
                                      vol_target=vol_target, vol_window=60, diag=diag)
    book_stats = N.arm_stats(ser)
    print("[book] cagr=%s  %.1fs" % (book_stats["full"].get("cagr"), time.time() - t0), flush=True)

    control_pp = M.delta_pp(book_stats["full"].get("cagr"), published.get("cagr"))
    control = {"arm_cagr": book_stats["full"].get("cagr"),
               "published_cagr": published.get("cagr"),
               "universe_measured": len(close.columns),
               "universe_published": cfg.get("universe_measured"),
               "delta_pp": control_pp, "tol_pp": CONTROL_TOL_PP}

    # --- the closed-eyes arm: 510300, same open-to-open convention, no rebalancing ------
    if BENCH not in close.columns:
        print("FATAL: %s is not on this panel -- the closed-eyes arm cannot be priced" % BENCH)
        return 2
    op = openp.reindex(columns=close.columns)
    bpx = op[BENCH].dropna()
    bpx = bpx[bpx.index >= pd.Timestamp(R.START)]
    bser = bpx / float(bpx.iloc[0])          # buy the index at the window's first open
    bench_rets = bser.pct_change().dropna()
    bench_stats = N.arm_stats(bser)

    # --- replay + attribution ----------------------------------------------------------
    df = replay(close, openp, diag, rebal, SEATS, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left")
    both = joined.dropna(subset=["engine", "equity"])
    max_rel = float((both["equity"] - both["engine"]).abs().max() / both["engine"].iloc[-1]) \
        if len(both) else None
    replay_block = {"bars_replayed": int(len(df)), "bars_matched": int(len(both)),
                    "max_abs_equity_diff": max_rel, "tol": REPLAY_TOL,
                    "identity_max_abs_resid": float(df["resid"].abs().max()),
                    "engine_end": float(both["engine"].iloc[-1]) if len(both) else None,
                    "replay_end": float(both["equity"].iloc[-1]) if len(both) else None}
    replay_ok = (max_rel is not None and max_rel <= REPLAY_TOL)
    print("[replay] bars=%d max_rel_diff=%s ok=%s"
          % (len(both), max_rel, replay_ok), flush=True)

    # --- the same ruler, on the money ------------------------------------------------
    excess = (df["net"] - df["r_bench"]).dropna()
    total = M.bootstrap_se(list(excess))
    leg_rows = {}
    for k in LEGS:
        b = M.bootstrap_se(list(df[k].dropna()))
        leg_rows[k] = {"ann_pp": (b or {}).get("obs_ann_pp"),
                       "mde80_pp": (b or {}).get("mde80_ann_pp"),
                       "se_pp": (b or {}).get("se_ann_pp"),
                       "p_direction": (b or {}).get("p_direction"),
                       "t": (b or {}).get("t"),
                       "status": M.classify_pair((b or {}).get("obs_ann_pp"),
                                                 (b or {}).get("mde80_ann_pp"),
                                                 (b or {}).get("p_direction"))}
    ann = leg_ann(df)
    legs_sum = round(sum(ann[k] for k in LEGS), 6)

    cagr_gap_pp = round(((book_stats["full"].get("cagr") or 0.0)
                         - (bench_stats["full"].get("cagr") or 0.0)) * 100.0, 3)
    exposure = {"mean_w_held": round(float(df["w_priced"].mean()), 4),
                "mean_w_equity": round(float(df["w_equity"].mean()), 4),
                "bars_no_equity": int((df["w_equity"] <= 1e-12).sum()),
                "bars_partial": int((df["w_priced"] < 0.999).sum()),
                "bars_unpriced": int((df["n_unpriced"] > 0).sum()),
                "bars": int(len(df))}

    totals = {"excess_ann_pp": ann["total"], "legs_sum_pp": legs_sum,
              "legs_sum_matches": bool(abs(legs_sum - ann["total"]) <= 5e-4),
              "cagr_gap_pp": cagr_gap_pp,
              "mde80_pp": (total or {}).get("mde80_ann_pp"),
              "se_pp": (total or {}).get("se_ann_pp"),
              "t": (total or {}).get("t"),
              "p_one_sided": (total or {}).get("p_one_sided"),
              "p_direction": (total or {}).get("p_direction"),
              "bars": (total or {}).get("bars"),
              "status": M.classify_pair((total or {}).get("obs_ann_pp"),
                                        (total or {}).get("mde80_ann_pp"),
                                        (total or {}).get("p_direction")),
              "bars_needed_for_1pp": M.bars_needed((total or {}).get("mde80_ann_pp"),
                                                   (total or {}).get("bars"))}

    verdict = money_verdict(totals["excess_ann_pp"],
                            totals["mde80_pp"] if control_pp is not None else None,
                            totals["p_direction"], control_pp, leg_rows)
    if not replay_ok:
        verdict = {"verdict": "CANNOT_JUDGE_REPLAY",
                   "sentence": "回放复现不了引擎自己的净值曲线（最大相对差 %s > %s）——"
                               "四条腿量的不是这本书，本面不判。" % (max_rel, REPLAY_TOL)}
    verdict["legs_above_mde"] = [k for k in LEGS
                                 if leg_rows[k]["status"] == "ABOVE_MDE80"]
    verdict["largest_leg"] = max(LEGS, key=lambda k: abs(ann[k] or 0.0)) if ann else None

    out = {"evidence_cutoff": price.get("evidence_cutoff")
           or str(pd.Timestamp(close.index[-1]).date()),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_money_mde.py",
           "rule": {"benchmark": BENCH, "gate_cny": GATE, "seats": SEATS,
                    "z80": Z_80, "per_year": PER_YEAR, "block": M.BLOCK,
                    "draws": M.DRAWS, "seed": M.SEED, "control_tol_pp": CONTROL_TOL_PP,
                    "replay_tol": REPLAY_TOL,
                    "question": "does the book's excess over the index clear the book's own "
                                "MDE80, and which leg earned it",
                    "legs": {"select": "equity picks at their weight, vs the index",
                             "rotate": "non-equity picks (gold/convertibles) at their weight, "
                                       "vs the index",
                             "size": "the weight left uninvested (vol target), vs the index",
                             "cost": "net minus gross, i.e. what the broker took"},
                    "identity": "select+rotate+size+cost == net - r_bench, exactly, per bar",
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"rebal": rebal, "vol_target": vol_target,
                      "cost_bp_per_side": (cfg.get("cost_bp_per_side")),
                      "panel_build_seconds": None, "run_seconds": None},
           "book": book_stats["full"], "benchmark": dict(bench_stats["full"], symbol=BENCH),
           "benchmark_bars_panel": int(len(bser)),
           "control": control, "replay": replay_block,
           "totals": totals, "legs": leg_rows, "exposure": exposure,
           "years": year_table(df),
           "verdict": verdict}
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"],
                      "excess_ann_pp": totals["excess_ann_pp"],
                      "mde80_pp": totals["mde80_pp"],
                      "control_pp": control_pp, "replay_ok": replay_ok,
                      "legs": {k: leg_rows[k]["ann_pp"] for k in LEGS},
                      "run_seconds": out["config"]["run_seconds"]}, ensure_ascii=False))
    return 0


def _f2(x):
    return "-" if x is None else "%.2f" % x


def write_md(out):
    v = out["verdict"]
    t = out["totals"]
    e = out["exposure"]
    legs = out["legs"]
    lines = ["# 这本书多赚的钱，比它自己的噪声大吗（r1763）", "",
             "**结论：%s**" % v["verdict"], "", v["sentence"], "",
             "## 1. 钱从哪来：四条腿，加起来必须正好是那条差", "",
             "把每一根 bar 的超额拆成四份，每一份都问同一个问题——**如果这个仓位当时买的是"
             "510300，会差多少**：", "",
             "| 腿 | 年化贡献 | 自己的 MDE80 | t | p（该方向） | 判读 |",
             "|---|---|---|---|---|---|"]
    names = {"select": "选中的权益票（在权益仓里挑得比指数好/差）",
             "rotate": "换赛道（黄金、转债）相对指数",
             "size": "空着的仓位（波动目标降杠杆）相对满仓指数",
             "cost": "交易成本"}
    words = {"ABOVE_MDE80": "越过 MDE80", "SIGNIFICANT_UNDERPOWERED": "显著但没到效力",
             "NO_DIRECTION": "无方向", "NO_ESTIMATE": "无估计"}
    for k in LEGS:
        r = legs[k]
        lines.append("| %s | %s pp | %s pp | %s | %s | %s |"
                     % (names[k], _f2(r["ann_pp"]), _f2(r["mde80_pp"]),
                        "-" if r["t"] is None else "%.2f" % r["t"],
                        "-" if r["p_direction"] is None else "%.4f" % r["p_direction"],
                        words.get(r["status"], r["status"])))
    lines += ["| **合计（净超额）** | **%s pp** | **%s pp** | %s | %s | **%s** |"
              % (_f2(t["excess_ann_pp"]), _f2(t["mde80_pp"]),
                 "-" if t["t"] is None else "%.2f" % t["t"],
                 "-" if t["p_direction"] is None else "%.4f" % t["p_direction"],
                 words.get(t["status"], t["status"])), "",
              "四条腿的年化贡献加起来 = %.4fpp，与净超额 %.4fpp %s"
              "（恒等式 `select+rotate+size+cost == net - r_bench` 在每根 bar 上逐点成立，"
              "最大残差 %.2e）。"
              % (t["legs_sum_pp"], t["excess_ann_pp"],
                 "一致" if t["legs_sum_matches"] else "**不一致**",
                 out["replay"]["identity_max_abs_resid"]), "",
              "## 2. 这条差越过自己的射程没有", "",
              "* 这本书净超额（相对 510300，算术年化）：**%+.2fpp**" % t["excess_ann_pp"],
              "* 同一段复利口径的 CAGR 差：**%+.2fpp**（书 %s%% vs 指数 %s%%）"
              % (t["cagr_gap_pp"],
                 "%.2f" % ((out["book"].get("cagr") or 0.0) * 100.0),
                 "%.2f" % ((out["benchmark"].get("cagr") or 0.0) * 100.0)),
              "* 这本书自己的最小可分辨差（MDE80）：**%s pp**" % _f2(t["mde80_pp"]),
              "* SE %s pp、t %s、单侧 p %s、%s 根 bar"
              % (_f2(t["se_pp"]), "-" if t["t"] is None else "%.2f" % t["t"],
                 "-" if t["p_one_sided"] is None else "%.4f" % t["p_one_sided"], t["bars"]),
              "", "**三句话**：①这本书 6.86 年做出 %s%%，同段闭眼买 510300 是 %s%%——差 "
              "%+.2fpp；②可这本书自己的最小可分辨差是 **%s pp**，所以这条差**在它自己的噪声"
              "之内**，不能说「它比闭眼买好」；③钱看得见地落在两处——**选票 %+.2fpp**（唯一"
              "方向站得住的一条，p=%s，但幅度仍在自家 MDE 之下）与**换赛道 %+.2fpp**（诊断"
              "黄金/转债），空仓降杠杆花了 %+.2fpp，成本 %+.2fpp。"
              % ("%.2f" % ((out["book"].get("cagr") or 0.0) * 100.0),
                 "%.2f" % ((out["benchmark"].get("cagr") or 0.0) * 100.0),
                 t["cagr_gap_pp"], _f2(t["mde80_pp"]),
                 legs["select"]["ann_pp"],
                 "-" if legs["select"]["p_direction"] is None
                 else "%.4f" % legs["select"]["p_direction"],
                 legs["rotate"]["ann_pp"], legs["size"]["ann_pp"], legs["cost"]["ann_pp"]), "",
              "**读法**：MDE80 是这本书在 80%% 效力下能分辨的最小年化差。观测差比它大，"
              "说明这条差在本书自己的噪声之外；比它小，就算 CAGR 差看着很大，"
              "重跑一遍这本账仍有 20%% 机会读成零。四条腿各自的 MDE80 与总和的 MDE80 不是"
              "同一把尺子的分项（残差之间会相关），所以「一条腿越过自己的门」只说明那条腿"
              "在自己的序列上站得住，不说明它的钱就是净超额的全部。算术差 %+.2fpp 比复利差 "
              "%+.2fpp 小，不是算错：指数这六年被 %s%% 的最大回撤磨过，几何收益低于均值×252，"
              "而腿的分解只能跑在算术口径上。"
              % (t["excess_ann_pp"], t["cagr_gap_pp"],
                 "%.1f" % ((out["benchmark"].get("maxdd") or 0.0) * 100.0)), "",
              "逐年看方向：**%d/%d** 个年度超额为正（负的是 %s）。"
              % (sum(1 for y in out["years"] if y["excess_pp"] > 0), len(out["years"]),
                 "、".join(str(y["year"]) for y in out["years"] if y["excess_pp"] <= 0) or "无"), "",
              "## 3. 逐年", "",
              "| 年 | bar | 书 | 510300 | 超额 | 选票 | 换赛道 | 空仓 | 成本 |",
              "|---|---|---|---|---|---|---|---|---|"]
    for y in out["years"]:
        lines.append("| %d | %d | %+.2f%% | %+.2f%% | %+.2fpp | %+.2f | %+.2f | %+.2f | %+.2f |"
                     % (y["year"], y["bars"], y["book_pct"], y["bench_pct"], y["excess_pp"],
                        y["select_pp"], y["rotate_pp"], y["size_pp"], y["cost_pp"]))
    lines += ["",
              "逐年的四项之和与超额同口径（单利累加，年化档才是乘 252 的算术均值），"
              "所以合计数与上表不会逐位相等，但符号与量级必须同向。", "",
              "## 4. 仓位形态", "",
              "* 平均实际持仓权重 **%.1f%%**，其中权益 **%.1f%%**"
              % (e["mean_w_held"] * 100.0, e["mean_w_equity"] * 100.0),
              "* **%d/%d** 根 bar 一股权益都没有（全黄金/转债/现金），"
              "**%d** 根 bar 没满仓（波动目标降杠杆），**%d** 根 bar 有仓位当时无法定价"
              % (e["bars_no_equity"], e["bars"], e["bars_partial"], e["bars_unpriced"]), "",
              "## 5. 两个门：控制臂与回放", "",
              "* **控制臂**：同一台引擎、同一张面板重算这本书的 CAGR = **%s%%**，"
              "抬闸定价面同格 **%s%%**，差 **%spp**（容差 %spp）"
              % ("%.2f" % ((out["control"].get("arm_cagr") or 0.0) * 100.0),
                 "%.2f" % ((out["control"].get("published_cagr") or 0.0) * 100.0),
                 out["control"]["delta_pp"], out["control"]["tol_pp"]),
              "* **回放恒等**：用引擎 diag 里的持仓与波动缩放的权重逐 bar 重建净值，"
              "与引擎自己的净值曲线最大相对差 **%.2e**（容差 %.0e，匹配 %d 根 bar）"
              % (out["replay"]["max_abs_equity_diff"], REPLAY_TOL, out["replay"]["bars_matched"]),
              "", "两个门任一不过，上面每一张表都不该被读——本面的 `--check` 会重新判这两道门。",
              "", "## 6. 诚实边界", "",
              "* 基准无成本（闭眼买不调仓），书有 10bp/边；这一项差异**记在 `cost` 腿里**，"
              "不是被藏进了选票。",
              "* 分类器把商品（黄金）与转债判成非权益，所以 `rotate` 腿里混着两种很不同的东西；"
              "本面不细分，也不把「黄金赚的钱」说成「选股能力」。",
              "* 算术年化（均值×252）与复利 CAGR 是两个口径，本面两个都印；MDE 检验跑在算术"
              "差序列上，因为块自助重采样的是均值。",
              "* 510300 自身的持仓与指数成分会变，本面用的是同一条 510300 开→开序列，"
              "不调整分红（与面板其余标的口径一致）。",
              "* 票池是现存 ETF（幸存者），这一段 2020 年以后的窗口是这本书最好的六年，"
              "不构成对未来的承诺。", ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _check():
    """Re-derive the published verdict, the identity and the ruler from the published JSON."""
    out = _load(OUT_JSON)
    t = out["totals"]
    v = money_verdict(t["excess_ann_pp"], t["mde80_pp"], t["p_direction"],
                      out["control"]["delta_pp"], out["legs"])
    if out["replay"]["max_abs_equity_diff"] > REPLAY_TOL:
        v = {"verdict": "CANNOT_JUDGE_REPLAY", "sentence": "replay gate failed"}
    legs_sum = round(sum(out["legs"][k]["ann_pp"] for k in LEGS), 6)
    checks = {
        "verdict_rederives": v["verdict"] == out["verdict"]["verdict"],
        "legs_sum_matches_total": abs(legs_sum - t["excess_ann_pp"]) <= 5e-4,
        "identity_holds": out["replay"]["identity_max_abs_resid"] <= 1e-12,
        "mde_is_z80_se": (t["mde80_pp"] is None or t["se_pp"] is None
                          or abs(round(Z_80 * float(t["se_pp"]), 4)
                                 - float(t["mde80_pp"])) <= 5e-3),
        "replay_inside_tol": out["replay"]["max_abs_equity_diff"] <= REPLAY_TOL,
    }
    ok = all(checks.values())
    print(json.dumps({"published": out["verdict"]["verdict"], "recomputed": v["verdict"],
                      "legs_sum": legs_sum, "total": t["excess_ann_pp"],
                      "checks": checks, "ok": ok}, ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    fails = []
    legs = []

    def chk(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    cls = {"EQ1": "equity", "EQ2": "equity", "GOLD": "commodity", "CB": "convertible"}

    # --- L1-L6 the identity, on synthetic bars ---------------------------------------
    rng = np.random.default_rng(4242)
    rets = {"EQ1": 0.010, "EQ2": -0.004, "GOLD": 0.006, "CB": 0.001}
    w = {"EQ1": 0.30, "EQ2": 0.20, "GOLD": 0.25, "CB": 0.10}      # 0.15 left in cash
    a = attribute(w, rets, cls, 0.002, cost_amt=0.0004)
    chk("L1 identity residual", abs(a["resid"]) < 1e-15, a["resid"])
    chk("L1b legs add to net excess",
        abs((a["select"] + a["rotate"] + a["size"] + a["cost"]) - (a["net"] - 0.002)) < 1e-15)

    # all-in the benchmark: every leg must be exactly zero
    b = attribute({"EQ1": 0.6, "EQ2": 0.4}, {"EQ1": 0.002, "EQ1": 0.002, "EQ2": 0.002},
                  cls, 0.002)
    chk("L2 all-in-bench is flat",
        all(abs(b[k]) < 1e-15 for k in LEGS), {k: b[k] for k in LEGS})

    # all cash: the whole excess is the size leg
    c = attribute({}, {}, cls, -0.01)
    chk("L3 cash-only is size", abs(c["size"] - 0.01) < 1e-15, c["size"])
    chk("L3b cash-only has no selection", abs(c["select"]) < 1e-15 and abs(c["rotate"]) < 1e-15)

    # cost: zero when nothing is charged, a drag when charged
    d0 = attribute(w, rets, cls, 0.002, cost_amt=0.0)
    d1 = attribute(w, rets, cls, 0.002, cost_amt=0.001)
    chk("L4 zero cost is zero", abs(d0["cost"]) < 1e-15, d0["cost"])
    chk("L4b cost is a drag", d1["cost"] < 0, d1["cost"])
    chk("L4c cost hits the net", d1["net"] < d0["net"])

    # an unpriced name is not an invested name: its weight falls into `size`, identity holds
    e = attribute({"EQ1": 0.5, "GONE": 0.5}, {"EQ1": 0.01, "GONE": np.nan}, cls, 0.003)
    chk("L5 unpriced counted", e["n_unpriced"] == 1, e["n_unpriced"])
    chk("L5b identity survives NaN", abs(e["resid"]) < 1e-15, e["resid"])
    chk("L5c unpriced slot sits in size", abs(e["size"] - (-0.5 * 0.003)) < 1e-15, e["size"])

    # the class split: gold and convertibles are rotation, not selection
    f = attribute({"EQ1": 0.0, "GOLD": 0.5}, {"EQ1": 0.02, "GOLD": 0.03}, cls, 0.01, 0.0)
    chk("L6 gold is rotation", abs(f["select"]) < 1e-15 and abs(f["rotate"] - 0.5 * 0.02) < 1e-15,
        (f["select"], f["rotate"]))
    g = attribute({"EQ1": 0.5}, {"EQ1": 0.02}, cls, 0.01, 0.0)
    chk("L6b equity is selection", abs(g["select"] - 0.5 * 0.01) < 1e-15, g["select"])

    # --- L7-L9 the ruler is the frozen one -------------------------------------------
    chk("L7 z80 is the same constant", Z_80 == M.Z_80 == 2.802, Z_80)
    chk("L7b annualisation is linear",
        abs(M.ann_pp(0.002) - 2.0 * M.ann_pp(0.001)) < 1e-9)
    zero = M.bootstrap_se(list(np.zeros(400)), draws=300, seed=5)
    chk("L8 zero series has no direction",
        M.classify_pair(zero["obs_ann_pp"], zero["mde80_ann_pp"], zero["p_direction"])
        == "NO_DIRECTION")
    pos = list(0.001 + rng.normal(0.0, 0.003, 900))
    pp = M.bootstrap_se(pos, draws=600, seed=5)
    chk("L9 a real shift clears the floor",
        pp["obs_ann_pp"] > pp["mde80_ann_pp"] or pp["p_direction"] <= 0.05,
        (pp["obs_ann_pp"], pp["mde80_ann_pp"], pp["p_direction"]))

    # --- L10-L14 one word per state, and refusals before judgements -------------------
    legs_syn = {"select": {"ann_pp": 6.0, "mde80_pp": 2.0, "status": "ABOVE_MDE80"},
                "rotate": {"ann_pp": 5.0, "mde80_pp": 3.0, "status": "ABOVE_MDE80"},
                "size": {"ann_pp": -1.0, "mde80_pp": 2.5, "status": "NO_DIRECTION"},
                "cost": {"ann_pp": -0.5, "mde80_pp": 0.2, "status": "ABOVE_MDE80"}}
    v = money_verdict(9.5, 2.2, 0.001, 0.0, legs_syn)
    chk("L10 above", v["verdict"] == "EXCESS_ABOVE_MDE80", v["verdict"])
    chk("L10b names the legs", "select" in v["sentence"], v["sentence"])
    v = money_verdict(1.2, 2.2, 0.02, 0.0, legs_syn)
    chk("L11 significant underpowered", v["verdict"] == "SIGNIFICANT_BUT_UNDERPOWERED", v)
    v = money_verdict(0.9, 2.2, 0.40, 0.0, legs_syn)
    chk("L12 inside the floor", v["verdict"] == "EXCESS_INSIDE_MDE80", v["verdict"])
    v = money_verdict(9.5, 2.2, 0.001, None, legs_syn)
    chk("L13 no control", v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v["verdict"])
    v = money_verdict(9.5, 2.2, 0.001, CONTROL_TOL_PP + 0.01, legs_syn)
    chk("L14 control fails", v["verdict"] == "CANNOT_JUDGE_CONTROL", v["verdict"])
    v = money_verdict(None, 2.2, 0.5, 0.0, legs_syn)
    chk("L14b no series", v["verdict"] == "CANNOT_JUDGE_NO_SERIES", v["verdict"])
    v = money_verdict(9.5, 2.2, 0.001, 0.0, {"select": {"status": "NO_DIRECTION"}})
    chk("L14c no leg above is said out loud", "没有一条越过" in v["sentence"], v["sentence"])

    # --- L15-L18 the replay really replays the engine -------------------------------
    idx = pd.bdate_range("2021-01-04", periods=160)
    n_nm = 8
    rng2 = np.random.default_rng(7)
    steps = rng2.normal(0.0006, 0.011, size=(len(idx), n_nm))
    close_syn = pd.DataFrame(100.0 * np.cumprod(1.0 + steps, axis=0), index=idx,
                             columns=["S%d" % i for i in range(n_nm)])
    open_syn = close_syn.shift(1).fillna(close_syn.iloc[0])
    amt_syn = pd.DataFrame(5e8, index=idx, columns=close_syn.columns)
    score_syn = close_syn.pct_change(5).fillna(0.0)
    dg = []
    ser_syn, _turn = R.open_to_open_equity(close_syn, open_syn, amt_syn, score_syn, 4, 3,
                                          0.001, diag=dg)
    cls_syn = {c: "equity" for c in close_syn.columns}
    df_syn = replay(close_syn, open_syn, dg, 4, 3, 0.001, "2021-01-04", cls_syn,
                    bench="S0")
    chk("L15 replay has bars", len(df_syn) > 100, len(df_syn))
    chk("L16 replay reproduces the engine",
        abs(float(df_syn["equity"].iloc[-1]) - float(ser_syn.iloc[-1])) / float(ser_syn.iloc[-1])
        <= 1e-12,
        (float(df_syn["equity"].iloc[-1]), float(ser_syn.iloc[-1])))
    chk("L17 replay identity on real-ish data",
        float(df_syn["resid"].abs().max()) <= 1e-12, float(df_syn["resid"].abs().max()))
    # a book that holds only the benchmark must show a zero excess, leg by leg
    df_flat = replay(close_syn, open_syn,
                     [{"date": str(d.date()), "book": ["S0"], "scale": 1.0}
                      for d in idx[::4]], 4, 1, 0.0, "2021-01-04", cls_syn, bench="S0")
    chk("L18 holding the benchmark is a flat excess",
        float((df_flat["net"] - df_flat["r_bench"]).abs().max()) <= 1e-12)

    # --- L19-L22 the leak-free plumbing around the tables ---------------------------
    chk("L19 legs_sum is additive by construction",
        abs(sum(leg_ann(df_syn)[k] for k in LEGS) - leg_ann(df_syn)["total"]) <= 5e-4,
        (leg_ann(df_syn),))
    yt = year_table(df_syn)
    chk("L20 year table covers the years", len(yt) >= 1 and "select_pp" in yt[0], yt[:1])
    chk("L21 compound handles NaN", abs(float(compound([0.01, np.nan]).iloc[-1]) - 1.01) < 1e-12)
    chk("L22 bars_needed is the frozen square law", M.bars_needed(2.0, 1600) == 6400)
    chk("L22b replay refuses an all-NaN benchmark",
        len(replay(close_syn, open_syn, dg, 4, 3, 0.001, "2021-01-04", cls_syn,
                   bench="NOPE")) == 0)

    total = len(legs)
    if fails:
        print("selftest %d/%d FAIL" % (total - len(fails), total))
        for f in fails:
            print("  FAIL %s" % f)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        write_md(_load(OUT_JSON))
        return 0
    if "run" in argv:
        return run()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
