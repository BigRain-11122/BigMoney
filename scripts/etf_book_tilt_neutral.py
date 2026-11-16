"""Is the select leg's floor this ranking's own price tilt? (r1790)

Two axes are already closed. Breadth (r1764): 2..30 seats moved the select leg's MDE80 only
8.74 -> 6.87pp. Pairwise de-correlation (r1765): picking names that do not move together moved
it to 6.98pp. Both answers pointed the same way -- the residual is not independent name noise
but one common tilt, the direction this ranking leans every month.

This face asks the tilt itself, and asks it in money: **build the tilt as a tradable spread,
measure how much of the select leg that spread explains, then take the spread out of the select
leg with a beta estimated only from bars before the one being hedged.** If the floor falls
under 5pp after the hedge, the floor *was* the tilt; if the residual alpha goes to zero at the
same time, the select leg never was stock picking -- it was the tilt in disguise.

The tilt is read off the same ranking, causally:

    rank(d) = percentile of score at the bar *before* the return bar (the engine's own
              score.shift(1) convention, so the factor sees exactly what the book saw)
    F(t)    = mean return of the top decile of rank(d) minus mean return of the bottom decile,
              measured open(d) -> open(t), one row per realised bar t

    beta(t) = cov(select, F) / var(F) over the trailing W bars, shifted one bar so the hedge
              at t is decided without knowing t
    resid(t)= select(t) - beta(t) * F(t)

Everything is measured on the book's own replay (the r1762..r1765 ruler) so the numbers are
comparable to the published ones: same panel, same gate, same seats, same rebalance, same cost,
same vol target, same z80 / block / seed bootstrap.

Usage:
  python scripts/etf_book_tilt_neutral.py run
  python scripts/etf_book_tilt_neutral.py --selftest
  python scripts/etf_book_tilt_neutral.py --check
  python scripts/etf_book_tilt_neutral.py --md
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

OUT_JSON = os.path.join(ROOT, "results", "etf_book_tilt_neutral.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_TILT_NEUTRAL.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")

BENCH = "510300"
GATE = 20e6                  # the published book's liquidity gate
BASE_SEATS = 5
DECILE = 0.10                # the tilt spread is top decile minus bottom decile
WINDOWS = (252, 504)         # beta estimation windows; 252 is primary
PRIMARY_WIN = 252
MIN_OBS = 120                # no beta at all before this many observations
BETA_CLIP = (-1.0, 3.0)      # a hedge beta outside this is a broken estimate, not a hedge
MDE_TARGET_PP = 5.0          # the r1764 target, unchanged
MIN_IMPROVE_PP = 1.0         # a floor move worth a sentence
CONTROL_TOL_PP = 0.25
PER_YEAR = 252.0


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def returns_table(openp, cols):
    """Open-to-open bar returns, one column per name, indexed by the bar the return lands on."""
    op = openp.reindex(columns=cols).ffill()
    r = op.iloc[1:] / op.iloc[:-1].values - 1.0
    r.index = op.index[1:]
    return r.replace([np.inf, -np.inf], np.nan)


def tilt_returns(score, rets, decile=DECILE, min_names=20, lag=2):
    """Realised return of the ranking's own tilt spread, one row per return bar.

    Two lags, and the second one is the whole point:

      * the engine trades `score.shift(1)`, so the rank at decision bar d is score at d-1;
      * `rets` is indexed by the bar a return LANDS on, so the bar whose return runs open(d) ->
        open(t) is row t, not row d.

    Reading the rank off row t directly (lag=1) is a one-bar look-ahead: it would rank names by
    a score built from the close of d, then book the move from the open of d to the open of t.
    The first run of this face did exactly that and the spread came back at +149pp a year, which
    is how the bug was caught. lag=2 puts the rank back on the bar the book could read.
    """
    pct = (score.shift(lag).reindex(index=rets.index, columns=rets.columns)
           .rank(axis=1, pct=True))
    # strictly above the top cutoff, at-or-below the bottom one: with pct ranks running k/n the
    # two sides then hold the same number of names (n=30, d=0.1 -> 3 and 3, not 4 and 3)
    top = rets.where(pct > 1.0 - decile)
    bot = rets.where(pct <= decile)
    n_top = top.notna().sum(axis=1)
    n_bot = bot.notna().sum(axis=1)
    f = top.mean(axis=1) - bot.mean(axis=1)
    f = f.where((n_top >= min_names) & (n_bot >= min_names))
    f.name = "tilt"
    live = f.notna()
    return f, {"mean_names_top": (float(n_top[live].mean()) if live.any() else None),
               "mean_names_bottom": (float(n_bot[live].mean()) if live.any() else None)}


def rolling_beta(sel, f, win=PRIMARY_WIN, min_obs=MIN_OBS, clip=BETA_CLIP):
    """Causal hedge ratio: cov/var over the trailing window, shifted one bar.

    A NaN beta (not enough history) is written as 0.0 = "no hedge yet", never as a guess.
    """
    s = pd.Series(sel).astype(float)
    x = pd.Series(f).reindex(s.index).astype(float)
    min_obs = min(int(min_obs), int(win))     # pandas refuses min_periods > window
    cov = s.rolling(win, min_periods=min_obs).cov(x).shift(1)
    var = x.rolling(win, min_periods=min_obs).var().shift(1)
    beta = (cov / var).where(var > 0)
    if clip is not None:
        beta = beta.clip(*clip)
    return beta.fillna(0.0)


def hedged(sel, f, beta):
    """select minus beta * F, bar by bar; the product term is zero where the beta is NaN."""
    s = pd.Series(sel).astype(float)
    x = pd.Series(f).reindex(s.index).astype(float)
    b = pd.Series(beta).reindex(s.index).astype(float).fillna(0.0)
    return (s - b * x.fillna(0.0)).rename("resid")


def ruler(series):
    x = pd.Series(series).dropna()
    if len(x) < 40:
        return None
    return M.bootstrap_se(list(x))


def oos_r2(sel, resid):
    """Out-of-sample R^2 of the hedge: 1 - var(resid)/var(select) on hedged bars only."""
    s = pd.Series(sel).dropna()
    r = pd.Series(resid).reindex(s.index)
    mask = r.notna()
    s, r = s[mask], r[mask]
    if len(s) < 40:
        return None
    v = float(s.var(ddof=1))
    if v <= 0:
        return None
    return round(1.0 - float(r.var(ddof=1)) / v, 4)


def held_percentile(diag, score):
    """Where the book's own five sat on the tilt distribution, on average over decisions."""
    pct = score.shift(1).rank(axis=1, pct=True)
    vals = []
    for row in diag:
        book = row.get("book")
        if not book:
            continue
        d = pd.Timestamp(row.get("date"))
        if d not in pct.index:
            continue
        r = pct.loc[d]
        got = [float(r.get(k)) for k in book if k in r.index and np.isfinite(r.get(k, np.nan))]
        if got:
            vals.append(float(np.mean(got)))
    if not vals:
        return {"decisions": 0, "mean_percentile": None}
    return {"decisions": len(vals), "mean_percentile": round(float(np.mean(vals)), 4),
            "median_percentile": round(float(np.median(vals)), 4)}


def book(close, openp, amt, score, cls, rebal, cost, vol_target):
    """The published book, replayed: engine curve, diag, and the attributed select leg."""
    diag = []
    ser, _turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, BASE_SEATS,
                                       cost, vol_target=vol_target, vol_window=60, diag=diag)
    stats = N.arm_stats(ser)
    df = MM.replay(close, openp, diag, rebal, BASE_SEATS, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left").dropna(subset=["engine", "equity"])
    max_rel = (float((joined["equity"] - joined["engine"]).abs().max()
                     / joined["engine"].iloc[-1]) if len(joined) else None)
    return {"ser": ser, "stats": stats, "df": df, "diag": diag, "replay_max_rel": max_rel}


def verdict(summary):
    control_pp = summary.get("control_delta_pp")
    if summary.get("published_cagr_pct") is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "控制臂没跑出来：这张面不判。"}
    if control_pp is None or abs(control_pp) > CONTROL_TOL_PP:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "控制臂与在印的同一格差 %.2fpp（容差 %.2fpp），这不是同一本书，"
                            "本面不判。" % (control_pp or 0.0, CONTROL_TOL_PP)}
    if not summary.get("replay_ok"):
        return {"verdict": "CANNOT_JUDGE_REPLAY",
                "sentence": "重放与引擎净值对不上，选股腿的数不是这台引擎的，本面不判。"}
    raw = summary.get("select_mde80_pp")
    res = summary.get("resid_mde80_pp")
    res_ann = summary.get("resid_ann_pp")
    if raw is None or res is None or res_ann is None:
        return {"verdict": "CANNOT_JUDGE_NO_RULER",
                "sentence": "选股腿或对冲后的序列够不着尺子（bars 不足）：不判。"}
    improve = raw - res
    if res < MDE_TARGET_PP and res_ann > 0:
        return {"verdict": "TILT_IS_THE_FLOOR", "mde80_pp": res, "improve_pp": round(improve, 4),
                "sentence": "把这张排名的自身倾斜对冲掉，选股腿的 MDE80 从 %.2fpp 落到 "
                            "**%.2fpp**，而对冲后仍留 %.2fpp 年化——地板就是倾斜。"
                            % (raw, res, res_ann)}
    if res < MDE_TARGET_PP and res_ann <= 0:
        return {"verdict": "TILT_IS_THE_BOOK", "mde80_pp": res, "improve_pp": round(improve, 4),
                "sentence": "对冲掉自身倾斜后地板落到 **%.2fpp**，年化也归零（%.2fpp）："
                            "这本「选股」的钱就是倾斜本身，不是选股。" % (res, res_ann)}
    if improve >= MIN_IMPROVE_PP:
        return {"verdict": "TILT_MOVES_FLOOR", "mde80_pp": res, "improve_pp": round(improve, 4),
                "sentence": "对冲自身倾斜把地板从 %.2fpp 挪到 **%.2fpp**（%.2fpp），"
                            "但仍没到 %.1fpp；对冲后年化 %.2fpp。"
                            % (raw, res, improve, MDE_TARGET_PP, res_ann)}
    return {"verdict": "TILT_NOT_THE_AXIS", "mde80_pp": res,
            "improve_pp": round(improve, 4),
            "sentence": "对冲自身倾斜只把地板从 %.2fpp 挪到 %.2fpp（<%.1fpp）：倾斜不是那把钥匙。"
                        % (raw, res, MIN_IMPROVE_PP)}


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
    f, fmeta = tilt_returns(score, rets)
    print("[tilt] %d bars, top names %.0f, bottom names %.0f, ann=%+.2fpp"
          % (len(f.dropna()), fmeta["mean_names_top"] or 0.0, fmeta["mean_names_bottom"] or 0.0,
             (f.dropna().mean() * PER_YEAR * 100.0)), flush=True)

    base = book(close, openp, amt, score, cls, rebal, cost, vol_target)
    sel = base["df"]["select"].dropna()
    raw = ruler(sel) or {}
    cagr = float((base["stats"].get("full") or {}).get("cagr") or 0.0) * 100.0
    control_pp = (None if published.get("cagr") is None
                  else round(cagr - float(published["cagr"]) * 100.0, 3))
    print("[base] cagr=%6.2f%% select=%+6.2fpp mde80=%6.2fpp %.0fs"
          % (cagr, raw.get("obs_ann_pp") or 0.0, raw.get("mde80_ann_pp") or 0.0,
             time.time() - t0), flush=True)

    arms = []
    for win in WINDOWS:
        beta = rolling_beta(sel, f, win=win)
        res = hedged(sel, f, beta)
        r = ruler(res) or {}
        tag = float((beta * f.reindex(sel.index).fillna(0.0)).mean() * PER_YEAR * 100.0)
        arms.append({
            "arm": "hedge_win%d" % win,
            "window": win,
            "beta_mean": round(float(beta.mean()), 4),
            "beta_median": round(float(beta.median()), 4),
            "beta_share_nonzero": round(float((beta.abs() > 1e-12).mean()), 4),
            "resid_ann_pp": r.get("obs_ann_pp"),
            "resid_se_pp": r.get("se_ann_pp"),
            "resid_mde80_pp": r.get("mde80_ann_pp"),
            "resid_p_direction": r.get("p_direction"),
            "floor_improve_pp": (None if raw.get("mde80_ann_pp") is None
                                 or r.get("mde80_ann_pp") is None
                                 else round(raw["mde80_ann_pp"] - r["mde80_ann_pp"], 4)),
            "alpha_given_up_pp": round(tag, 4),
            "oos_r2": oos_r2(sel, res),
            "bars_hedged": int((beta.abs() > 1e-12).sum()),
        })
        print("[%s] resid=%+6.2fpp mde80=%6.2fpp improv=%5.2fpp giveup=%+5.2fpp r2=%s %.0fs"
              % (arms[-1]["arm"], arms[-1]["resid_ann_pp"] or 0.0,
                 arms[-1]["resid_mde80_pp"] or 0.0, arms[-1]["floor_improve_pp"] or 0.0,
                 arms[-1]["alpha_given_up_pp"], arms[-1]["oos_r2"], time.time() - t0),
              flush=True)

    primary = next(a for a in arms if a["window"] == PRIMARY_WIN)

    # Companion reading: the WHOLE book's excess, not the select leg. If the tilt is where this
    # book's money comes from, it must show up here with a much larger loading -- otherwise the
    # negative on the select leg would be misread as "the book has no tilt at all".
    exc = (base["df"]["net"] - base["df"]["r_bench"]).dropna()
    b_x = rolling_beta(exc, f, win=PRIMARY_WIN)
    r_x = hedged(exc, f, b_x)
    ex_ruler = ruler(exc) or {}
    x_ruler = ruler(r_x) or {}
    tag_x = float((b_x * f.reindex(exc.index).fillna(0.0)).mean() * PER_YEAR * 100.0)
    book_excess = {
        "leg": "net - r_bench (the whole book's excess, not the select leg)",
        "ann_pp": ex_ruler.get("obs_ann_pp"),
        "mde80_pp": ex_ruler.get("mde80_ann_pp"),
        "beta_mean": round(float(b_x.mean()), 4),
        "beta_median": round(float(b_x.median()), 4),
        "oos_r2": oos_r2(exc, r_x),
        "hedged_ann_pp": x_ruler.get("obs_ann_pp"),
        "hedged_mde80_pp": x_ruler.get("mde80_ann_pp"),
        "alpha_given_up_pp": round(tag_x, 4),
        "bars_hedged": int((b_x.abs() > 1e-12).sum()),
    }
    print("[book excess] %+6.2fpp beta=%.2f r2=%s hedged=%+6.2fpp giveup=%+6.2fpp"
          % (book_excess["ann_pp"] or 0.0, book_excess["beta_mean"] or 0.0,
             book_excess["oos_r2"], book_excess["hedged_ann_pp"] or 0.0,
             book_excess["alpha_given_up_pp"]), flush=True)

    summary = {
        "select_ann_pp": raw.get("obs_ann_pp"),        "select_se_pp": raw.get("se_ann_pp"),
        "select_mde80_pp": raw.get("mde80_ann_pp"),
        "select_p_direction": raw.get("p_direction"),
        "resid_ann_pp": primary["resid_ann_pp"],
        "resid_mde80_pp": primary["resid_mde80_pp"],
        "control_delta_pp": control_pp,
        "published_cagr_pct": (None if published.get("cagr") is None
                              else round(float(published["cagr"]) * 100.0, 3)),
        "replay_ok": (base["replay_max_rel"] is None or base["replay_max_rel"] <= 1e-9),
        "book_cagr_pct": round(cagr, 3),
        "book_sharpe": (base["stats"].get("full") or {}).get("sharpe"),
        "book_maxdd_pct": round(float((base["stats"].get("full") or {}).get("maxdd") or 0.0)
                                * 100.0, 2),
    }
    v = verdict(summary)
    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "control_face_cutoff": price.get("evidence_cutoff"),
        "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_tilt_neutral.py",
        "rule": {"benchmark": BENCH, "gate_cny": GATE, "seats": BASE_SEATS,
                 "decile": DECILE, "windows": list(WINDOWS), "primary_window": PRIMARY_WIN,
                 "min_obs": MIN_OBS, "beta_clip": list(BETA_CLIP),
                 "mde_target_pp": MDE_TARGET_PP, "min_improve_pp": MIN_IMPROVE_PP,
                 "control_tol_pp": CONTROL_TOL_PP,
                 "z80": 2.802, "block": M.BLOCK, "draws": M.DRAWS, "seed": M.SEED,
                 "question": "build this ranking's own tilt as a top-vs-bottom decile spread, "
                             "hedge it out of the select leg with a beta from bars strictly "
                             "before the hedged bar, and ask whether the select leg's MDE80 "
                             "falls under 5pp -- and what alpha the hedge eats",
                 "causal": "rank at bar t uses the score the book could read at t-2 (engine "
                            "shift(1) plus the return landing on t); beta at t uses bars < t only",
                 "frozen": "criteria written before the run; --check re-derives the verdict"},
        "config": {"rebal": rebal, "vol_target": vol_target,
                   "cost_bp_per_side": cfg.get("cost_bp_per_side"),
                   "universe_measured": len(close.columns),
                   "flips_repaired": int(n_flip),
                   "run_seconds": None},
        "tilt_factor": {"bars": int(len(f.dropna())),
                        "ann_pp": round(float(f.dropna().mean()) * PER_YEAR * 100.0, 4),
                        "vol_pp": round(float(f.dropna().std(ddof=1)) * np.sqrt(PER_YEAR) * 100.0,
                                        3),
                        "mean_names_top": fmeta["mean_names_top"],
                        "mean_names_bottom": fmeta["mean_names_bottom"]},
        "book": {"cagr_pct": summary["book_cagr_pct"], "sharpe": summary["book_sharpe"],
                 "maxdd_pct": summary["book_maxdd_pct"],
                 "replay_max_rel": base["replay_max_rel"],
                 "held_tilt_percentile": held_percentile(base["diag"], score)},
        "select_leg": {"ann_pp": summary["select_ann_pp"], "se_pp": summary["select_se_pp"],
                       "mde80_pp": summary["select_mde80_pp"],
                       "p_direction": summary["select_p_direction"],
                       "bars": raw.get("bars")},
        "control": {"arm_cagr_pct": summary["book_cagr_pct"],
                    "published_cagr_pct": summary["published_cagr_pct"],
                    "delta_pp": control_pp, "tol_pp": CONTROL_TOL_PP,
                    "replay_ok": summary["replay_ok"]},
        "arms": arms,
        "primary": primary,
        "book_excess": book_excess,
        "coverage": {"book_bars": int(len(sel)),
                     "factor_bars": int(len(f.dropna())),
                     "factor_first_bar": (str(f.dropna().index[0].date())
                                          if len(f.dropna()) else None),
                     "hedged_bars": int(primary.get("bars_hedged") or 0)},
        "price_per_1pp_floor": (None if not primary.get("floor_improve_pp")
                                or primary["floor_improve_pp"] <= 1e-9
                                else round(primary["alpha_given_up_pp"]
                                           / primary["floor_improve_pp"], 2)),
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
    tf = d.get("tilt_factor") or {}
    bk = d.get("book") or {}
    sl = d.get("select_leg") or {}
    hp = bk.get("held_tilt_percentile") or {}
    L = []
    L.append("# 选股腿的地板是不是这张排名自己的价格倾斜（r1790）\n")
    L.append("> evidence_cutoff=%s；面板末 bar=%s；脚本 `scripts/etf_book_tilt_neutral.py`；"
             "证据 `results/etf_book_tilt_neutral.json`。\n"
             "> 同一台引擎、同一张面板、同一把尺（z80=2.802·块长 %d·%d 次·种子 %d）。\n"
             % (d.get("evidence_cutoff"), d.get("panel_last_bar"), d["rule"]["block"],
                d["rule"]["draws"], d["rule"]["seed"]))
    L.append("## 问的问题\n")
    L.append("r1764 关掉了「加宽度」，r1765 关掉了「选不相关的名字」，两次都把地板指回同一个方向："
             "残差不是独立名字噪声，而是这张排名的共同倾斜。\n\n")
    L.append("本轮把倾斜本身做成一条可交易的价差（当日打分前 10% 减后 10%），再用**只用被对冲那根 bar "
             "之前的数据**估出的 beta 把它从选股腿里对冲掉：地板落到 5pp 以下，地板就是倾斜；"
             "残差年化同时归零，那这本「选股」的钱就是倾斜本身。\n")
    L.append("## 两把读数\n")
    L.append("| 面 | 年化 | MDE80 | 说明 |\n|---|---|---|---|\n")
    L.append("| 倾斜价差（前 10%% − 后 10%%） | %+0.2fpp | — | 波动 %0.2fpp，%d 根 bar |\n"
             % (tf.get("ann_pp") or 0.0, tf.get("vol_pp") or 0.0, tf.get("bars") or 0))
    L.append("| 选股腿（未经对冲） | %+0.2fpp | **%0.2fpp** | %d 根 bar |\n"
             % (sl.get("ann_pp") or 0.0, sl.get("mde80_pp") or 0.0, sl.get("bars") or 0))
    for a in (d.get("arms") or []):
        L.append("| 选股腿（对冲窗 %d） | %+0.2fpp | **%0.2fpp** | β 均值 %.2f，实对冲 %d 根，"
                 "OOS R² %s |\n"
                 % (a["window"], a["resid_ann_pp"] or 0.0, a["resid_mde80_pp"] or 0.0,
                    a["beta_mean"] or 0.0, a.get("bars_hedged") or 0,
                    a.get("oos_r2")))
    L.append("\n## 判词\n")
    L.append("**%s** — %s\n" % (d.get("verdict"), d.get("sentence")))
    be = d.get("book_excess") or {}
    if be.get("ann_pp") is not None:
        L.append("\n## 对照：全书超额（不是选股腿）\n")
        L.append("只对冲选股腿还不够，得看一眼整本书——否则「选股腿不载倾斜」会被误读成"
                 "「这本书根本没有倾斜」。\n\n")
        L.append("| 面 | 年化 | MDE80 | 对倾斜价差的 β（中位） | OOS R² |\n|---|---|---|---|---|\n")
        L.append("| 全书超额（net − 指数） | %+0.2fpp | %0.2fpp | %.2f | %s |\n"
                 % (be.get("ann_pp") or 0.0, be.get("mde80_pp") or 0.0,
                    be.get("beta_median") or 0.0, be.get("oos_r2")))
        L.append("| 全书超额（对冲倾斜后） | %+0.2fpp | %0.2fpp | — | — |\n"
                 % (be.get("hedged_ann_pp") or 0.0, be.get("hedged_mde80_pp") or 0.0))
        L.append("\n对冲掉倾斜要付 **%+0.2fpp** 年化：本书超额的一半来自倾斜。"
                 "β 只有 %.2f 不是「没暴露」——这本书按 8%% 波动目标降过杠杆，"
                 "而倾斜价差自己是 %.1fpp 波动。\n"
                 % (be.get("alpha_given_up_pp") or 0.0, be.get("beta_median") or 0.0,
                    tf.get("vol_pp") or 0.0))
    c = d.get("control") or {}
    L.append("\n控制臂：基线臂年化 %.2f%%，与在印的同一格差 %.3fpp（容差 %.2fpp）；重放偏差 %s。\n"
             % (c.get("arm_cagr_pct") or 0.0, c.get("delta_pp") or 0.0, c.get("tol_pp") or 0.0,
                bk.get("replay_max_rel")))
    if hp.get("mean_percentile") is not None:
        L.append("\n这本书自己的五只，平均坐在打分分布的 **%.0f 分位**（%d 次决策，中位 %.0f）——"
                 "它不是「在全市场里挑」，它是「在同一个倾斜里挑」。\n"
                 % (hp["mean_percentile"] * 100.0, hp.get("decisions") or 0,
                    (hp.get("median_percentile") or 0.0) * 100.0))
    p = d.get("primary") or {}
    if p.get("floor_improve_pp") and p.get("floor_improve_pp") > 1e-9:
        L.append("\n## 对冲的价签\n")
        L.append("地板改善 %.2fpp，代价是让掉 %+0.2fpp 年化 —— 每 1pp 地板 **%.2fpp** 的 alpha。\n"
                 % (p["floor_improve_pp"], p.get("alpha_given_up_pp") or 0.0,
                    d.get("price_per_1pp_floor") or 0.0))
        L.append("\n价签 >1 意味着这本书在拿多于 1pp 的钱去买 1pp 的精度。\n")
    L.append("\n## 这张面的边界\n")
    L.append("- 倾斜用当日打分的前后 10% 十档读出，是**这张排名的**倾斜，不是全市场的风格因子；"
             "换一本排名要重跑。\n")
    L.append("- beta 是线性对冲：隐含「倾斜暴露与选股腿线性同向」，非线性/状态依赖的暴露只能被部分吃掉。\n")
    L.append("- 对冲只在纸面上成立：真去空前后 10% 价差要融券与做空腿成本，本面没有收这笔钱。\n")
    L.append("- 对冲只在因子可算且滚动窗填满之后生效：%d 根里只有 %d 根真的被对冲，"
             "其余是未对冲的裸腿（%d 根窗、最少 %d 根历史）。\n"
             % ((d.get("coverage") or {}).get("book_bars") or 0,
                (d.get("primary") or {}).get("bars_hedged") or 0,
                int(d["rule"]["primary_window"]), int(d["rule"]["min_obs"])))
    L.append("- ETF 票池为现存标的（幸存者偏差照旧）。\n")
    L.append("- 倾斜价差只从 %s 起可算：之前打分面上的名字不足 20 只/档，"
             "那 %d 根 bar 上对冲是裸腿（本书 %d 根 bar 里有 %d 根落在因子窗内）。\n"
             % ((d.get("coverage") or {}).get("factor_first_bar"),
                int(d["rule"]["primary_window"]), (d.get("coverage") or {}).get("book_bars") or 0,
                (d.get("coverage") or {}).get("factor_bars") or 0))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("".join(L))
    print("[write] %s" % OUT_MD)
    return 0


def _check():
    d = _load(OUT_JSON)
    summary = {
        "control_delta_pp": (d.get("control") or {}).get("delta_pp"),
        "published_cagr_pct": (d.get("control") or {}).get("published_cagr_pct"),
        "replay_ok": (d.get("control") or {}).get("replay_ok"),
        "select_mde80_pp": (d.get("select_leg") or {}).get("mde80_pp"),
        "resid_mde80_pp": (d.get("primary") or {}).get("resid_mde80_pp"),
        "resid_ann_pp": (d.get("primary") or {}).get("resid_ann_pp"),
    }
    v = verdict(summary)
    ok = v.get("verdict") == d.get("verdict")
    notes = []
    if not ok:
        notes.append("verdict re-derivation %s != stored %s"
                     % (v.get("verdict"), d.get("verdict")))
    arms = d.get("arms") or []
    if len(arms) != len(WINDOWS):
        ok = False
        notes.append("arms %d != windows %d" % (len(arms), len(WINDOWS)))
    for a in arms:
        if a.get("resid_mde80_pp") is None:
            ok = False
            notes.append("%s has no residual ruler" % a.get("arm"))
    if (d.get("select_leg") or {}).get("mde80_pp") is None:
        ok = False
        notes.append("no select-leg ruler")
    # the hedge must be causal: no bar may be hedged with fewer than MIN_OBS prior bars
    for a in arms:
        if (a.get("bars_hedged") or 0) <= 0:
            notes.append("%s hedged nothing (beta never estimated)" % a.get("arm"))
    if not ok:
        print("CHECK FAILED: " + "; ".join(notes))
        return 1
    print("check ok: verdict=%s arms=%d select_mde=%.2f resid_mde=%.2f control_delta=%.3fpp"
          % (v["verdict"], len(arms),
             (d.get("select_leg") or {}).get("mde80_pp") or 0.0,
             (d.get("primary") or {}).get("resid_mde80_pp") or 0.0,
             (d.get("control") or {}).get("delta_pp") or 0.0))
    for n in notes:
        print("  note:", n)
    return 0


def selftest():
    fails = []
    n = [0]

    def chk(name, cond, detail=""):
        n[0] += 1
        if not cond:
            fails.append("%s %s" % (name, detail))

    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    names = ["N%02d" % i for i in range(30)]
    rng = np.random.default_rng(11)
    base = rng.normal(0.001, 0.004, (len(idx), len(names)))
    rets = pd.DataFrame(base, index=idx, columns=names)
    score = pd.DataFrame(np.tile(np.linspace(0.9, 0.1, len(names)), (len(idx), 1)),
                         index=idx, columns=names)

    # L1: the spread is top-decile minus bottom-decile, on the same rows
    f, meta = tilt_returns(score, rets, decile=0.10, min_names=3)
    top = rets[names[:3]].mean(axis=1)
    bot = rets[names[-3:]].mean(axis=1)
    chk("L1 spread shape", len(f.dropna()) == len(idx) - 2, len(f.dropna()))
    d_spread = (f - (top - bot)).dropna()
    chk("L2 spread value", len(d_spread) > 50 and float(d_spread.abs().max()) < 1e-12)

    # L3: two lags -- the rank at return bar t is the score at t-2 (engine's shift(1) plus the
    # return landing on t). This is the leg that catches the one-bar look-ahead that produced
    # the +149pp first reading.
    score2 = score.copy()
    score2.iloc[-2] = np.linspace(0.1, 0.9, len(names))   # the bar the LOOK-AHEAD would use
    f2, _ = tilt_returns(score2, rets, decile=0.10, min_names=3)
    chk("L3 the look-ahead bar is not read",
        float(abs(f2.iloc[-1] - f.iloc[-1])) < 1e-12, (f2.iloc[-1], f.iloc[-1]))
    score3 = score.copy()
    score3.iloc[-3] = np.linspace(0.1, 0.9, len(names))   # the bar the book could actually read
    f3, _ = tilt_returns(score3, rets, decile=0.10, min_names=3)
    chk("L3b the bar the book could read does move the last row",
        float(abs(f3.iloc[-1] - f.iloc[-1])) > 1e-9, (f3.iloc[-1], f.iloc[-1]))
    chk("L3c the row before it is untouched", float(abs(f3.iloc[-2] - f.iloc[-2])) < 1e-12)

    # L4: a pure-tilt select leg is recovered by the hedge
    f_al = f.reindex(rets.index[1:]).dropna()
    sel_pure = (1.5 * f_al).rename("select")
    beta = rolling_beta(sel_pure, f_al, win=20, min_obs=10)
    res = hedged(sel_pure, f_al, beta)
    chk("L4 beta recovers 1.5", abs(float(beta.iloc[-1]) - 1.5) < 1e-6, beta.iloc[-1])
    chk("L5 residual of a pure tilt is ~0 after the warm-up",
        float(res.iloc[25:].abs().max()) < 1e-9, res.iloc[25:].abs().max())
    chk("L5b the warm-up bars stay unhedged",
        float(res.iloc[0]) == float(sel_pure.iloc[0]))

    # L6: a select leg with no tilt exposure is left alone
    rng2 = np.random.default_rng(99)
    idio = pd.Series(rng2.normal(0.0005, 0.004, len(f_al)), index=f_al.index)
    beta_i = rolling_beta(idio, f_al, win=20, min_obs=10)
    chk("L6 no tilt -> ~no hedge", float(beta_i.iloc[25:].abs().mean()) < 0.6,
        float(beta_i.iloc[25:].abs().mean()))

    # L7: the beta at bar t must not use bar t (a spike after t cannot move it)
    spiked = f_al.copy()
    spiked.iloc[-1] = 100.0
    b_before = rolling_beta(sel_pure, f_al, win=20, min_obs=10)
    b_after = rolling_beta(sel_pure, spiked, win=20, min_obs=10)
    chk("L7 causal beta", float(abs(b_before.iloc[-1] - b_after.iloc[-1])) < 1e-12,
        (b_before.iloc[-1], b_after.iloc[-1]))

    # L8: no beta before min_obs -> 0.0, never a guess
    b_thin = rolling_beta(sel_pure, f_al, win=40, min_obs=40)
    chk("L8 thin history hedges nothing", float(b_thin.iloc[0]) == 0.0)
    chk("L8b once the window fills, the beta appears", float(b_thin.iloc[-1]) != 0.0)

    # L9: accounting identity -- resid mean = select mean - mean(beta*F)
    tag = float((rolling_beta(sel_pure, f_al, win=20, min_obs=10)
                 * f_al).mean())
    chk("L9 hedge identity", abs(float(res.mean()) - (float(sel_pure.mean()) - tag)) < 1e-12)

    # L10: OOS R^2 is 1 when the leg is exactly the hedge and 0 when it is not
    warm = slice(15, None)
    chk("L10 r2 of pure tilt", oos_r2(sel_pure.iloc[warm], res.iloc[warm]) > 0.999,
        oos_r2(sel_pure.iloc[warm], res.iloc[warm]))
    res_i = hedged(idio, f_al, beta_i)
    chk("L11 r2 of unrelated leg", abs(oos_r2(idio.iloc[warm], res_i.iloc[warm])) < 0.15,
        oos_r2(idio.iloc[warm], res_i.iloc[warm]))

    # L12: percentile of the book's own names
    diag = [{"date": idx[10], "book": names[:5]}, {"date": idx[20], "book": names[-5:]}]
    hp = held_percentile(diag, score)
    chk("L12 held percentile sane", 0.0 < hp["mean_percentile"] < 1.0, hp)

    # L13..L17: verdict branches
    good = {"control_delta_pp": 0.0, "published_cagr_pct": 9.12, "replay_ok": True,
            "select_mde80_pp": 8.74, "resid_mde80_pp": 4.2, "resid_ann_pp": 6.0}
    chk("L13 target met", verdict(good)["verdict"] == "TILT_IS_THE_FLOOR")
    chk("L14 tilt is the book",
        verdict(dict(good, resid_ann_pp=-0.1))["verdict"] == "TILT_IS_THE_BOOK")
    chk("L15 floor moved",
        verdict(dict(good, resid_mde80_pp=7.0))["verdict"] == "TILT_MOVES_FLOOR")
    chk("L16 not the axis",
        verdict(dict(good, resid_mde80_pp=8.5))["verdict"] == "TILT_NOT_THE_AXIS")
    chk("L17 control refuses", verdict(dict(good, control_delta_pp=2.0))["verdict"]
        == "CANNOT_JUDGE_CONTROL")
    chk("L18 replay refuses", verdict(dict(good, replay_ok=False))["verdict"]
        == "CANNOT_JUDGE_REPLAY")
    chk("L19 empty ruler refuses", verdict(dict(good, resid_mde80_pp=None))["verdict"]
        == "CANNOT_JUDGE_NO_RULER")
    chk("L20 no control face", verdict(dict(good, published_cagr_pct=None))["verdict"]
        == "CANNOT_JUDGE_NO_CONTROL")

    total = n[0]
    print("selftest %d/%d PASS" % (total - len(fails), total))
    for f_ in fails:
        print("  FAIL", f_)
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
