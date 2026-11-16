"""Can the select leg's floor be bought down by picking names that do not move together? (r1765)

r1764 closed the breadth axis: 2..30 seats moved the select leg's MDE80 only 8.74 -> 6.87pp
(slope -0.13, not the -0.5 pure diversification would give) because the residual is this
ranking's own common tilt -- the names it likes lean the same way that month, so the `name`
term cannot shrink while the `sleeve` term sits at +0.08.

This face asks the next question on the same ruler: if the tilt lives in *which names* were
picked and not in how many, then picking names that do not move together -- same ranking, same
gate, same seats, same rebalance, same cost, same vol target -- should move the floor where
breadth could not. The rule tested is a causal greedy de-correlation:

    take the top POOL names by score, keep the highest, then repeatedly add the candidate
    whose 60-bar (window W) return correlation with the already-chosen names is lowest,
    stopping at n_hold.

Everything it needs is visible at the decision bar: the score row at d and returns up to d.
No future data is read; the quote table itself is the engine's own panel and flip repair.

Three things are reported per arm, all from one engine and one panel:

  1. the select leg's own MDE80 (the r1762..r1764 ruler: same z80, same block, same seed);
  2. what it cost or paid in money -- book CAGR, select pp, and the realised tracking error;
  3. whether the book actually changed -- Jaccard overlap against the base book's names.

The honest edge: a de-correlated five is not a *better* five, it is a *quieter* five. If the
floor moves but the alpha does not, the right sentence is "this buys precision", not "this
beats the index"; and if the floor does not move, the answer is that the tilt is not in the
pairwise correlation of the held names either, which is a different (and useful) negative.

Usage:
  python scripts/etf_book_corr_select.py run
  python scripts/etf_book_corr_select.py --selftest
  python scripts/etf_book_corr_select.py --check
  python scripts/etf_book_corr_select.py --md
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

import etf_robust_pf as R                     # noqa: E402  (the engine)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_book_entry_gate as G               # noqa: E402  (panel + flip repair)
import etf_book_gate_raise_noise as N         # noqa: E402  (arm_stats)
import etf_equity_alpha as A                   # noqa: E402  (classify)
import etf_book_book_mde as M                 # noqa: E402  (the frozen ruler)
import etf_book_money_mde as MM               # noqa: E402  (replay)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_corr_select.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CORR_SELECT.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")

BENCH = "510300"
GATE = 20e6                  # the published book's liquidity gate
BASE_SEATS = 5
PRIMARY = (15, 60)           # pool size, correlation window -- named before the run
ARMS = [(15, 60), (10, 60), (25, 60), (15, 120), (15, 40)]
MDE_TARGET_PP = 5.0          # the r1764 target, unchanged
MIN_IMPROVE_PP = 1.0         # a floor move worth a sentence
CAGR_GIVE_BACK_PP = 1.0      # alpha this face refuses to trade for precision
CONTROL_TOL_PP = 0.25
PER_YEAR = 252.0


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def returns_table(openp, cols):
    """Open-to-open bar returns, one column per name. Bar d is known at the open of d."""
    op = openp.reindex(columns=cols).ffill()
    r = op.iloc[1:] / op.iloc[:-1].values - 1.0
    r.index = op.index[1:]
    return r.replace([np.inf, -np.inf], np.nan)


def corr_pick(row, pool, n_hold, rets, win, already=None):
    """Greedy de-correlated pick from the day's top `pool` scores.

    Causal: uses `row` (that bar's score) and returns with index <= the bar. If the window
    is too thin to estimate a correlation, the arm degrades to the plain top-n of the pool --
    never to a look-ahead.
    """
    s = row.dropna()
    if len(s) < n_hold:
        return None
    cands = list(s.nlargest(min(pool, len(s))).index)
    if len(cands) <= n_hold:
        return cands[:n_hold]
    d = s.index.name  # not used; the caller binds the date inside the closure
    picks = [cands[0]]
    rest = [c for c in cands[1:]]
    while len(picks) < n_hold and rest:
        best, best_r = None, None
        for c in rest:
            if c not in rets.columns:
                prior = 1.0
            else:
                sub = rets[list(picks) + [c]].tail(win).dropna()
                if len(sub) < win // 2 or len(sub.columns) < 2:
                    prior = 1.0
                else:
                    cm = sub.corr()
                    prior = float(cm.loc[c, picks].abs().max())
            if best_r is None or prior < best_r - 1e-12:
                best, best_r = c, prior
        picks.append(best)
        rest.remove(best)
    return picks


def make_hook(rets, pool, win):
    """Bind the panel to the engine's select_hook contract."""
    def hook(row, held_names, n_hold, d):
        r = row.copy()
        r.index.name = None
        sub = rets[rets.index <= pd.Timestamp(d)] if len(rets) else rets
        picks = corr_pick(r, pool, n_hold, sub, win)
        if picks is None or len(picks) != n_hold:
            raise RuntimeError("corr_pick returned %r at %s" % (picks, d))
        return picks
    return hook


def arm(close, openp, amt, score, cls, rebal, cost, vol_target, hook=None, seats=BASE_SEATS):
    """One arm: engine equity, its diag, the replay, and the select leg on the frozen ruler."""
    diag = []
    ser, _turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, seats, cost,
                                       vol_target=vol_target, vol_window=60, diag=diag,
                                       select_hook=hook)
    stats = N.arm_stats(ser)
    df = MM.replay(close, openp, diag, rebal, seats, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left").dropna(subset=["engine", "equity"])
    max_rel = (float((joined["equity"] - joined["engine"]).abs().max()
                     / joined["engine"].iloc[-1]) if len(joined) else None)
    sel = df["select"].dropna()
    b = M.bootstrap_se(list(sel)) or {}
    excess = (df["net"] - df["r_bench"]).dropna()
    names = set()
    for row in diag:
        if row.get("book"):
            names.update(str(p) for p in row["book"])
    return {"ser": ser, "stats": stats, "df": df, "replay_max_rel": max_rel, "names": names,
            "select_ann_pp": (round(float(sel.mean()) * PER_YEAR * 100.0, 4) if len(sel) else None),
            "select_se_pp": b.get("se_ann_pp"),
            "select_mde80_pp": b.get("mde80_ann_pp"),
            "select_p_direction": b.get("p_direction"),
            "excess_ann_pp": (round(float(excess.mean()) * PER_YEAR * 100.0, 4)
                              if len(excess) else None),
            "te_select_pp": (round(float(sel.std(ddof=1)) * np.sqrt(PER_YEAR) * 100.0, 3)
                             if len(sel) > 2 else None)}


def _names(arm_out):
    """The set of names the book held over the window, read from the engine's own diag."""
    return set(arm_out.get("names") or ())


def jaccard(a, b):
    if not a and not b:
        return None
    return round(len(a & b) / float(len(a | b)), 4)


def row_for(label, out, base_names=None, published=None):
    stats = out["stats"]
    full = stats.get("full") or {}
    row = {
        "arm": label,
        "book_cagr_pct": round(float(full.get("cagr") or 0.0) * 100.0, 3),
        "book_sharpe": full.get("sharpe"),
        "book_maxdd_pct": round(float((full.get("maxdd") or 0.0)) * 100.0, 2),
        "select_ann_pp": out["select_ann_pp"],
        "select_mde80_pp": out["select_mde80_pp"],
        "select_p_direction": out["select_p_direction"],
        "excess_ann_pp": out["excess_ann_pp"],
        "te_select_pp": out["te_select_pp"],
        "replay_max_rel": out["replay_max_rel"],
        "n_names_held": len(_names(out)),
    }
    if base_names is not None:
        row["jaccard_vs_base"] = jaccard(_names(out), base_names)
    return row


def verdict(rows, control_pp, replay_ok):
    if control_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "控制臂没跑出来：这张面不判。"}
    if abs(control_pp) > CONTROL_TOL_PP:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与在印的同一格差 %.2fpp（容差 %.2fpp），这不是同一本书，本面不判。"
                            % (control_pp, CONTROL_TOL_PP)}
    if not replay_ok:
        return {"verdict": "CANNOT_JUDGE_REPLAY",
                "sentence": "重放与引擎净值对不上，选股腿的数不是这台引擎的，本面不判。"}
    base = next((r for r in rows if r["arm"] == "base"), None)
    if base is None or base["select_mde80_pp"] is None:
        return {"verdict": "CANNOT_JUDGE_NO_BASE",
                "sentence": "没有基线臂的地板读数：不判。"}
    base_mde = base["select_mde80_pp"]
    base_cagr = base["book_cagr_pct"]
    hits, moves = [], []
    for r in rows:
        if r["arm"] == "base" or r["select_mde80_pp"] is None:
            continue
        if r["select_mde80_pp"] < base_mde - MIN_IMPROVE_PP:
            moves.append(r)
        if (r["select_mde80_pp"] < MDE_TARGET_PP
                and r["book_cagr_pct"] >= base_cagr - CAGR_GIVE_BACK_PP):
            hits.append(r)
    if hits:
        best = min(hits, key=lambda r: r["select_mde80_pp"])
        return {"verdict": "CORR_TARGET_MET", "arm": best["arm"],
                "mde80_pp": best["select_mde80_pp"], "cagr_pct": best["book_cagr_pct"],
                "sentence": "相关约束选股把选股腿的 MDE80 压到 **%.2fpp**（%s 臂），"
                            "且年化只让掉 %.2fpp——这条轴是那把钥匙。"
                            % (best["select_mde80_pp"], best["arm"],
                               base_cagr - best["book_cagr_pct"])}
    if moves:
        best = min(moves, key=lambda r: r["select_mde80_pp"])
        return {"verdict": "CORR_MOVES_FLOOR", "arm": best["arm"],
                "mde80_pp": best["select_mde80_pp"], "base_mde80_pp": base_mde,
                "sentence": "相关约束选股把地板从 %.2fpp 挪到 **%.2fpp**（%s 臂，%.2fpp），"
                            "但仍没到 %.1fpp；年化 %.2f%% vs %.2f%%。"
                            % (base_mde, best["select_mde80_pp"], best["arm"],
                               base_mde - best["select_mde80_pp"], MDE_TARGET_PP,
                               best["book_cagr_pct"], base_cagr)}
    return {"verdict": "CORR_NOT_THE_AXIS", "base_mde80_pp": base_mde,
            "sentence": "五个臂一个都没把地板挪过 %.1fpp（基线 %.2fpp）：持仓名字之间的相关"
                        "不是那把钥匙——倾斜在名字之外（同一批因子把整本书推向同一方向）。"
                        % (MIN_IMPROVE_PP, base_mde)}


def run():
    t0 = time.time()
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")

    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}
    score = E.build_score(close, amt, feats, min_amt=GATE)
    rets = returns_table(openp, close.columns)
    print("[returns] %d bars x %d names" % (len(rets), len(rets.columns)), flush=True)

    base = arm(close, openp, amt, score, cls, rebal, cost, vol_target)
    base_names = _names(base)
    rows = [row_for("base", base)]
    print("[base] cagr=%6.2f%% select=%+6.2fpp mde80=%6.2fpp %.0fs"
          % (rows[-1]["book_cagr_pct"], rows[-1]["select_ann_pp"] or 0.0,
             rows[-1]["select_mde80_pp"] or 0.0, time.time() - t0), flush=True)

    for pool, win in ARMS:
        out = arm(close, openp, amt, score, cls, rebal, cost, vol_target,
                  hook=make_hook(rets, pool, win))
        r = row_for("pool%d_win%d" % (pool, win), out, base_names=base_names)
        r["pool"] = pool
        r["window"] = win
        rows.append(r)
        print("[%s] cagr=%6.2f%% select=%+6.2fpp mde80=%6.2fpp jac=%.3f %.0fs"
              % (r["arm"], r["book_cagr_pct"], r["select_ann_pp"] or 0.0,
                 r["select_mde80_pp"] or 0.0, r.get("jaccard_vs_base") or 0.0,
                 time.time() - t0), flush=True)

    control_pp = (None if published.get("cagr") is None
                  else round(rows[0]["book_cagr_pct"] - float(published["cagr"]) * 100.0, 3))
    replay_ok = all((r["replay_max_rel"] is None or r["replay_max_rel"] <= 1e-9) for r in rows)
    v = verdict(rows, control_pp, replay_ok)
    primary = next((r for r in rows if r["arm"] == "pool%d_win%d" % PRIMARY), None)
    out = {
        "evidence_cutoff": price.get("evidence_cutoff")
        or str(pd.Timestamp(close.index[-1]).date()),
        "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_corr_select.py",
        "rule": {"benchmark": BENCH, "gate_cny": GATE, "seats": BASE_SEATS,
                 "primary_arm": "pool%d_win%d" % PRIMARY,
                 "arms": [{"pool": p, "window": w} for p, w in ARMS],
                 "mde_target_pp": MDE_TARGET_PP, "min_improve_pp": MIN_IMPROVE_PP,
                 "cagr_give_back_pp": CAGR_GIVE_BACK_PP, "control_tol_pp": CONTROL_TOL_PP,
                 "z80": M.classify_pair.__doc__ is not None and 2.802,
                 "block": M.BLOCK, "draws": M.DRAWS, "seed": M.SEED,
                 "question": "with the seat count fixed, does picking the top-pool names that do "
                             "not move together move the select leg's MDE80, and what does it "
                             "cost in CAGR",
                 "causal": "the pick reads that bar's score row and returns up to that bar only",
                 "frozen": "criteria written before the run; --check re-derives the verdict"},
        "config": {"rebal": rebal, "vol_target": vol_target,
                   "cost_bp_per_side": cfg.get("cost_bp_per_side"),
                   "universe_measured": len(close.columns),
                   "flips_repaired": int(n_flip),
                   "run_seconds": None},
        "control": {"arm_cagr_pct": rows[0]["book_cagr_pct"],
                    "published_cagr_pct": (None if published.get("cagr") is None
                                          else round(float(published["cagr"]) * 100.0, 3)),
                    "delta_pp": control_pp, "tol_pp": CONTROL_TOL_PP,
                    "replay_ok": replay_ok},
        "rows": rows,
        "primary": primary,
        **v,
    }
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[verdict] %s -- %s" % (v["verdict"], v["sentence"]), flush=True)
    print("[write] %s (%.1fs)" % (OUT_JSON, time.time() - t0), flush=True)
    return 0


def write_md():
    d = _load(OUT_JSON)
    rows = d.get("rows") or []
    L = []
    L.append("# 相关约束选股能不能把选股腿的地板买下来（r1765）\n")
    L.append("> evidence_cutoff=%s；面板末 bar=%s；脚本 `scripts/etf_book_corr_select.py`；"
             "证据 `results/etf_book_corr_select.json`。\n"
             "> 同一台引擎、同一张面板、同一把尺（z80=2.802·块长 %d·%d 次·种子 %d）。\n"
             % (d.get("evidence_cutoff"), d.get("panel_last_bar"), d["rule"]["block"],
                d["rule"]["draws"], d["rule"]["seed"]))
    L.append("## 问的问题\n")
    L.append("r1764 把「加宽度」这条轴关了：2~30 座只把选股腿的 MDE80 从 8.74pp 挪到 6.87pp，"
             "因为残差不是独立的名字噪声，而是这张排名的共同倾斜。\n")
    L.append("本轮问同一个问题换一条轴：**座数不变**，改「挑哪几只」——从当日分数最高的 "
             "pool 只里，贪心挑与已选名字 60 日收益相关最低的 5 只。若地板在这条轴上动，"
             "钥匙就在持仓之间的相关里；若不动，倾斜在名字之外。\n")
    L.append("## 结果\n")
    L.append("| 臂 | 年化 | 夏普 | 回撤 | 选股腿 | MDE80 | 与基线持仓重合 | 重放偏差 |\n")
    L.append("|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        L.append("| %s | %s%% | %s | %s%% | %spp | %spp | %s | %s |\n"
                 % (r["arm"], r["book_cagr_pct"], r["book_sharpe"], r["book_maxdd_pct"],
                    r["select_ann_pp"], r["select_mde80_pp"],
                    r.get("jaccard_vs_base"), r["replay_max_rel"]))
    L.append("\n## 判词\n")
    L.append("**%s** — %s\n" % (d.get("verdict"), d.get("sentence")))
    c = d.get("control") or {}
    L.append("控制臂：基线臂年化 %.2f%%，与在印的同一格差 %.3fpp（容差 %.2fpp）。\n"
             % (c.get("arm_cagr_pct") or 0.0, c.get("delta_pp") or 0.0, c.get("tol_pp") or 0.0))
    base = next((r for r in rows if r["arm"] == "base"), None)
    if base and base.get("select_mde80_pp") and base.get("select_ann_pp"):
        prices = []
        for r in rows:
            if r["arm"] == "base" or r.get("select_mde80_pp") is None:
                continue
            dfloor = base["select_mde80_pp"] - r["select_mde80_pp"]
            dalpha = base["select_ann_pp"] - r["select_ann_pp"]
            if dfloor > 1e-9:
                prices.append((r["arm"], round(dfloor, 3), round(dalpha, 3),
                               round(dalpha / dfloor, 2)))
        if prices:
            L.append("\n## 每 1pp 地板改善的代价\n")
            L.append("降噪不是免费的，这张面把价签挂出来——地板每挪 1pp，选股腿让掉多少 pp：\n\n")
            L.append("| 臂 | 地板改善 | 选股腿让掉 | 每 1pp 地板的 alpha 代价 |\n|---|---|---|---|\n")
            for name, dfloor, dalpha, ratio in prices:
                L.append("| %s | %.2fpp | %.2fpp | %.2f |\n" % (name, dfloor, dalpha, ratio))
            L.append("\n比价 1.0 是盈亏平衡线：代价 >1 意味着这本书用超过 1pp 的钱去买 1pp 的精度，"
                     "换来的是一个更确定但更小的数。\n")
    L.append("## 这张面的边界\n")
    L.append("- 安静的五只不等于更好的五只：地板降而 alpha 不涨，正确说法是「买到了精度」，"
             "不是「跑赢了指数」。\n")
    L.append("- 相关只用已实现收益估计（60 日窗），换手因此上升，成本按 10bp/边实收。\n")
    L.append("- 只测座数=5；座数与相关约束的交互（例如 10 座 + 去相关）不在本面。\n")
    L.append("- ETF 票池为现存标的（幸存者偏差照旧）；2020-2023 段收益薄，结论主要落在 2024 后。\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("".join(L))
    print("[write] %s" % OUT_MD)
    return 0


def _check():
    d = _load(OUT_JSON)
    rows = d.get("rows") or []
    ok = True
    notes = []
    control_pp = (d.get("control") or {}).get("delta_pp")
    replay_ok = all((r["replay_max_rel"] is None or r["replay_max_rel"] <= 1e-9) for r in rows)
    v = verdict(rows, control_pp, replay_ok)
    if v.get("verdict") != d.get("verdict"):
        ok = False
        notes.append("verdict re-derivation %s != stored %s" % (v.get("verdict"), d.get("verdict")))
    base = next((r for r in rows if r["arm"] == "base"), None)
    if base and base.get("select_mde80_pp") is not None:
        pass
    for r in rows:
        if r.get("select_mde80_pp") is not None and r.get("select_ann_pp") is not None:
            if r["select_mde80_pp"] <= 0:
                ok = False
                notes.append("%s mde80 non-positive" % r["arm"])
    if base is None:
        ok = False
        notes.append("no base arm")
    if not ok:
        print("CHECK FAILED: " + "; ".join(notes))
        return 1
    print("check ok: verdict=%s rows=%d control_delta=%.3fpp replay_ok=%s"
          % (v["verdict"], len(rows), control_pp or 0.0, replay_ok))
    return 0


def selftest():
    fails = []
    n = [0]

    def chk(name, cond, detail=""):
        n[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    rng = np.random.default_rng(7)
    # two blocks: a/b nearly identical, c independent -- a de-correlating pick must avoid b
    a = rng.normal(0, 0.01, len(idx))
    b = a + rng.normal(0, 0.0005, len(idx))
    c = rng.normal(0, 0.01, len(idx))
    d = rng.normal(0, 0.01, len(idx))
    e = rng.normal(0, 0.01, len(idx))
    rets = pd.DataFrame({"A": a, "B": b, "C": c, "D": d, "E": e}, index=idx)
    row = pd.Series({"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.6, "E": 0.5})
    row.index.name = None
    picks = corr_pick(row, 5, 3, rets, 60)
    chk("L1 first pick is the top score", picks[0] == "A", picks)
    chk("L2 avoids the twin of the first pick", "B" not in picks, picks)
    chk("L3 returns exactly n_hold", len(picks) == 3, picks)
    chk("L4 distinct names", len(set(picks)) == 3, picks)

    # pool smaller than n_hold -> None (never a silent short book)
    chk("L5 pool<n_hold refuses", corr_pick(pd.Series({"A": 1.0, "B": 2.0}), 2, 3, rets, 60) is None)

    # a row with too few scores -> None
    chk("L6 thin row refuses", corr_pick(pd.Series({"A": 1.0}), 5, 3, rets, 60) is None)

    # causal: returns after the decision bar must not be needed
    sub = rets[rets.index <= idx[40]]
    picks_causal = corr_pick(row, 5, 2, sub, 60)
    chk("L7 causal window still picks", picks_causal is not None and len(picks_causal) == 2,
        picks_causal)

    # ties break towards the higher score
    flat = pd.DataFrame(np.zeros((80, 5)), index=idx, columns=list("ABCDE"))
    picks_tie = corr_pick(row, 5, 2, flat, 60)
    chk("L8 flat correlations keep score order", picks_tie == ["A", "B"], picks_tie)

    # jaccard
    chk("L9 jaccard identity", jaccard({"a", "b"}, {"a", "b"}) == 1.0)
    chk("L10 jaccard disjoint", jaccard({"a"}, {"b"}) == 0.0)
    chk("L11 jaccard empty is None", jaccard(set(), set()) is None)

    # verdict states
    rows_ok = [{"arm": "base", "book_cagr_pct": 9.12, "select_mde80_pp": 8.74},
               {"arm": "pool15_win60", "book_cagr_pct": 9.0, "select_mde80_pp": 4.2}]
    chk("L12 target met", verdict(rows_ok, 0.0, True)["verdict"] == "CORR_TARGET_MET")
    rows_move = [{"arm": "base", "book_cagr_pct": 9.12, "select_mde80_pp": 8.74},
                 {"arm": "pool15_win60", "book_cagr_pct": 8.9, "select_mde80_pp": 7.0}]
    chk("L13 floor moved", verdict(rows_move, 0.0, True)["verdict"] == "CORR_MOVES_FLOOR")
    rows_flat = [{"arm": "base", "book_cagr_pct": 9.12, "select_mde80_pp": 8.74},
                 {"arm": "pool15_win60", "book_cagr_pct": 8.9, "select_mde80_pp": 8.5}]
    chk("L14 not the axis", verdict(rows_flat, 0.0, True)["verdict"] == "CORR_NOT_THE_AXIS")
    chk("L15 control refuses", verdict(rows_ok, 2.0, True)["verdict"] == "CANNOT_JUDGE_CONTROL")
    chk("L16 replay refuses", verdict(rows_ok, 0.0, False)["verdict"] == "CANNOT_JUDGE_REPLAY")
    chk("L17 target needs the money kept",
        verdict([{"arm": "base", "book_cagr_pct": 9.12, "select_mde80_pp": 8.74},
                 {"arm": "pool15_win60", "book_cagr_pct": 4.0, "select_mde80_pp": 3.0}],
                0.0, True)["verdict"] != "CORR_TARGET_MET")

    # the hook contract: exactly n_hold distinct names
    hook = make_hook(rets, 5, 60)
    got = hook(row, [], 3, idx[-1])
    chk("L18 hook shape", len(got) == 3 and len(set(got)) == 3, got)

    total = n[0]
    print("selftest %d/%d PASS" % (total - len(fails), total))
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        return write_md()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
