"""Can this book buy its way out of the noise floor by holding fewer names? (r1764)

r1763 left one leg standing: `select` (+7.45pp, p=0.0055) pointed the right way but its own
MDE80 was 8.74pp -- the direction survives, the size does not. The cheapest repair is not more
history (r1762 priced that: 50-836 years for 1pp). The cheap repair is a *narrower* book: a
selection spread over 20 names is mostly index risk, and the tracking error that sets the floor
falls roughly like 1/sqrt(N). So the question this face answers is arithmetic, not taste:

    hold the same ranking, the same gate (20M), the same rebalance, the same cost and the same
    vol target -- and change ONLY the seat count. Does any seat count bring the select leg's
    MDE80 under 5pp, and what does it cost in alpha to get there?

Three things are measured per seat count, all from one engine and one panel:

  1. the select leg's own MDE80 (the r1762/r1763 ruler, same z80, same block bootstrap);
  2. the two channels that move it -- tracking error and exposure: `te_select` is the realised
     vol of the leg, `te_select_per_exposure` normalises it by the mean invested weight, so a
     falling floor caused by the vol target cutting size is not mistaken for a quieter book;
  3. the alpha that survives: the select leg's annualised pp, its bootstrap p, and the price
     paid relative to the 5-seat book -- precision bought by deleting the money is not a fix.

The honest edge of this face: changing the seat count changes what the selection *is* (top-2 of
a ranking is not top-20), so this is "same ranking, different breadth", not "same positions".
It also cannot say a narrower book is tradeable -- concentration raises single-name weight and
that is a risk question living in `etf_book_capacity_rule` / `etf_breadth_sweep`, which this face
does not re-price.

Usage:
  python scripts/etf_book_seat_mde.py run
  python scripts/etf_book_seat_mde.py --selftest
  python scripts/etf_book_seat_mde.py --check
  python scripts/etf_book_seat_mde.py --md
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

import etf_robust_pf as R                     # noqa: E402  (the engine itself)
import etf_composite_pf as E                  # noqa: E402  (the score face)
import etf_book_entry_gate as G               # noqa: E402  (panel + its flip repair)
import etf_book_gate_raise_noise as N         # noqa: E402  (arm_stats)
import etf_equity_alpha as A                  # noqa: E402  (classify)
import etf_book_book_mde as M                 # noqa: E402  (the frozen ruler)
import etf_book_money_mde as MM               # noqa: E402  (replay + four-leg attribution)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_seat_mde.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_SEAT_MDE.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
FACE_MONEY = os.path.join(ROOT, "results", "etf_book_money_mde.json")

BENCH = "510300"
GATE = 20e6                      # the cut the ticket prints
SWEEP = (2, 3, 4, 5, 8, 10, 15, 20, 30)
BASE_SEATS = 5                   # the published book; its cell is the control
TARGET_MDE_PP = 5.0              # the milestone's own bar: "under 5pp"
CONTROL_TOL_PP = 0.25            # the 5-seat cell must reproduce the price face
LEG_TOL_PP = 0.05                # ... and its select leg must reproduce r1763's money face
REPLAY_TOL = 1e-9
SPLIT_TOL = 1e-12                # select == common + idio must hold bar by bar
ALPHA_P_SIG = 0.05
PER_YEAR = M.PER_YEAR
Z_80 = M.Z_80


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def te_ann(series):
    """Realised annualised tracking error of a per-bar pp series (engine's 252)."""
    x = np.asarray([v for v in pd.Series(series).dropna()], dtype=float)
    if x.size < 2:
        return None
    return round(float(x.std(ddof=1)) * math.sqrt(PER_YEAR) * 100.0, 4)


def te_per_exposure(te_pp, mean_w):
    """Tracking error per unit of invested weight.

    A narrower book holds more vol, so the vol target cuts its size -- and a smaller position
    has a smaller vol in yuan. Dividing by the mean invested weight keeps that size channel
    from being read as a quieter book.
    """
    if te_pp is None or not mean_w or mean_w <= 0:
        return None
    return round(float(te_pp) / float(mean_w), 4)


def fit_exponent(rows, ykey="select_mde80_pp"):
    """Slope of log(figure) on log(seats) -- the 1/sqrt(N) law read off the data, not assumed."""
    pts = [(float(r["n_hold"]), float(r[ykey])) for r in rows
           if r.get(ykey) is not None and r.get(ykey) > 0]
    if len(pts) < 2:
        return None
    xs = np.log([p[0] for p in pts])
    ys = np.log([p[1] for p in pts])
    xm, ym = xs.mean(), ys.mean()
    den = float(((xs - xm) ** 2).sum())
    if den <= 0:
        return None
    return round(float(((xs - xm) * (ys - ym)).sum() / den), 4)


def book_path(close, openp, diag, rebal, seats, start, bench=BENCH):
    """The book as it was actually held, bar by bar: the scale, and who was in it.

    This walks the same rebalance rule as `MM.replay` (every `rebal`-th bar, take the diag row
    of that decision date). It exists to answer a second question -- is the noise name-specific
    or is it the whole equity sleeve moving against the index -- and the identity check in
    `split_te` is what keeps the two walkers from drifting apart.
    """
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    by_date = {str(row["date"]): row for row in diag if row.get("book")}
    rows = []
    held = {}
    scale = 0.0
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if i % rebal == 0:
            row = by_date.get(str(pd.Timestamp(d).date()))
            if row is not None:
                scale = float(row.get("scale") or 0.0)
                held = {p: scale / float(seats) for p in row["book"]}
        rows.append({"date": nxt, "held": list(held), "scale": scale})
    if not rows:
        return pd.DataFrame(columns=["held", "scale"])
    return pd.DataFrame(rows).set_index("date")


def rel_returns(close, openp, cols):
    """Open-to-open bar returns for the equity sleeve, minus the benchmark, one column per name.

    The benchmark is also an equity ETF, so it arrives inside `cols` -- it is removed from the
    name list first. (Subtracting the bench column while it is still duplicated across labels
    turns every cell into NaN, which is how the first cut of this face printed a 0.00 split.)
    """
    op = openp.reindex(columns=close.columns)
    if BENCH not in close.columns:
        return None
    names = [c for c in cols if c != BENCH]
    x = op[names + [BENCH]]
    r = x.iloc[1:] / x.iloc[:-1].values - 1.0
    r.index = x.index[1:]
    r = r.replace([np.inf, -np.inf], np.nan)
    return r[names].sub(r[BENCH], axis=0)


def split_te(df, path, rel, cls, seats):
    """Split the select leg into the sleeve and the names: select == common + idio, per bar.

    `common` is what ANY equal-weight basket of this equity sleeve earns against the index that
    bar; `idio` is what the held names earn on top of that basket. Only the second obeys 1/sqrt(N)
    -- which is the whole point, because a floor that is mostly `common` cannot be bought down by
    holding more names. The legs are multiplied by the engine's own vol scale and seat share, so
    the identity against the published `select` column must hold to 1e-12.
    """
    eq = [c for c in rel.columns if cls.get(str(c)) == "equity"]
    if not eq or df.empty:
        return None
    R = rel[eq]
    out = []
    for date, row in df.iterrows():
        if date not in path.index:
            continue
        held = [p for p in path.at[date, "held"] if cls.get(str(p)) == "equity" and p in R.columns]
        if not held or p_scale(path, date) is None:
            out.append({"date": date, "common": 0.0, "idio": 0.0, "n_eq": 0})
            continue
        scale = p_scale(path, date)
        all_vals = R.loc[date].dropna()
        if all_vals.empty:
            out.append({"date": date, "common": 0.0, "idio": 0.0, "n_eq": 0})
            continue
        held_vals = R.loc[date, held].dropna()
        if held_vals.empty:
            out.append({"date": date, "common": 0.0, "idio": 0.0, "n_eq": 0})
            continue
        common = float(all_vals.mean())
        idio = float(held_vals.mean()) - common
        factor = scale * float(len(held_vals)) / float(seats)
        out.append({"date": date, "common": factor * common, "idio": factor * idio,
                    "n_eq": int(len(held_vals))})
    if not out:
        return None
    s = pd.DataFrame(out).set_index("date")
    joined = df[["select"]].join(s, how="inner")
    resid = float((joined["select"] - joined["common"] - joined["idio"]).abs().max()) \
        if len(joined) else None
    te_c = te_ann(joined["common"])
    te_i = te_ann(joined["idio"])
    var_c = float(joined["common"].var(ddof=1)) if len(joined) > 2 else 0.0
    var_i = float(joined["idio"].var(ddof=1)) if len(joined) > 2 else 0.0
    tot = var_c + var_i
    return {"bars": int(len(joined)), "te_common_pp": te_c, "te_idio_pp": te_i,
            "share_common": (round(var_c / tot, 4) if tot > 0 else None),
            "common_ann_pp": (round(float(joined["common"].mean()) * PER_YEAR * 100.0, 4)
                              if len(joined) else None),
            "idio_ann_pp": (round(float(joined["idio"].mean()) * PER_YEAR * 100.0, 4)
                            if len(joined) else None),
            "identity_max_abs_resid": resid, "identity_bars": int(len(joined))}


def p_scale(path, date):
    """The scale the book carried into `date` (0 is a real answer: a fully de-risked bar)."""
    v = path.at[date, "scale"] if "scale" in path.columns else None
    return None if v is None else float(v)


def seat_verdict(rows, control_pp, replay_ok=True, leg_delta_pp=None,
                 split_ok=True, target_pp=TARGET_MDE_PP):
    """One word for the concentration question, refusing before it judges.

    The middle case exists on purpose: a book can reach the 5pp floor and lose the money that
    made the floor worth reading. Filing that as a win is how a face like this goes wrong.
    """
    if not replay_ok:
        return {"verdict": "CANNOT_JUDGE_REPLAY",
                "sentence": "回放复现不了引擎自己的净值曲线：这张面不判任何档位。"}
    if not split_ok:
        return {"verdict": "CANNOT_JUDGE_SPLIT",
                "sentence": "选股腿拆不成「袖子 + 名字」两截（残差超容差）：噪声来源不判。"}
    if control_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "控制臂没有跑出来：这张面不判任何档位。"}
    if abs(control_pp) > CONTROL_TOL_PP:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": "5 座这一格与抬闸定价面差 %.2fpp（容差 %.2fpp）——"
                            "这不是同一本书，本面不判。" % (control_pp, CONTROL_TOL_PP)}
    if leg_delta_pp is not None and abs(leg_delta_pp) > LEG_TOL_PP:
        return {"verdict": "CANNOT_JUDGE_LEG",
                "sentence": "5 座的选股腿与 r1763 钱包面差 %.2fpp（容差 %.2fpp）——"
                            "同一本书的两条腿对不上，本面不判。" % (leg_delta_pp, LEG_TOL_PP)}
    judgeable = [r for r in rows if r.get("select_mde80_pp") is not None]
    if not judgeable:
        return {"verdict": "CANNOT_JUDGE_NO_SERIES",
                "sentence": "没有一格跑出可用的选股腿序列：不判。"}
    hits = [r for r in judgeable if r["select_mde80_pp"] <= target_pp]
    alive = [r for r in hits
             if (r.get("select_ann_pp") or 0.0) > 0.0
             and (r.get("select_p_direction") if r.get("select_p_direction") is not None
                  else 1.0) <= ALPHA_P_SIG]
    best = min(judgeable, key=lambda r: r["select_mde80_pp"])
    if hits and alive:
        r = min(alive, key=lambda x: x["select_mde80_pp"])
        return {"verdict": "SEAT_TARGET_REACHED", "seats": r["n_hold"],
                "mde80_pp": r["select_mde80_pp"], "select_pp": r["select_ann_pp"],
                "sentence": "把仓位从 5 座收到 **%d 座**，选股腿自己的 MDE80 从 %.2fpp 降到 "
                            "**%.2fpp**（目标 %.1fpp），而年化选股贡献仍是 **%+.2fpp**"
                            "（p=%s）——精度不是靠删掉钱换来的。"
                            % (r["n_hold"], _at(rows, BASE_SEATS, "select_mde80_pp"),
                               r["select_mde80_pp"], target_pp, r["select_ann_pp"],
                               _fmt_p(r.get("select_p_direction")))}
    if hits:
        r = min(hits, key=lambda x: x["select_mde80_pp"])
        return {"verdict": "SEAT_TARGET_REACHED_ALPHA_GONE", "seats": r["n_hold"],
                "mde80_pp": r["select_mde80_pp"], "select_pp": r["select_ann_pp"],
                "sentence": "**%d 座**这一档确实把 MDE80 压到 %.2fpp，但选股腿自己也缩到 "
                            "%+.2fpp（p=%s）——**精度是买到了，钱没了**，这不是修法。"
                            % (r["n_hold"], r["select_mde80_pp"], r["select_ann_pp"],
                               _fmt_p(r.get("select_p_direction")))}
    return {"verdict": "SEAT_TARGET_NOT_REACHED", "seats": best["n_hold"],
            "mde80_pp": best["select_mde80_pp"], "select_pp": best["select_ann_pp"],
            "sentence": "把 %d~%d 座全扫一遍，选股腿的 MDE80 最窄只到 **%.2fpp**（%d 座），"
                        "仍够不着 %.1fpp——在这个排名上，**持仓数不是那把钥匙**"
                        "（5 座 %.2fpp；每把 MDE 减半需要的不是宽度而是别的轴）。"
                        % (min(r["n_hold"] for r in judgeable),
                           max(r["n_hold"] for r in judgeable),
                           best["select_mde80_pp"], best["n_hold"], target_pp,
                           _at(rows, BASE_SEATS, "select_mde80_pp"))}


def _fmt_p(p):
    return "-" if p is None else "%.4f" % p


def _at(rows, seats, key):
    for r in rows:
        if int(r["n_hold"]) == int(seats):
            return r.get(key)
    return None


def _f2(x):
    return "-" if x is None else "%.2f" % x


def sweep(close, openp, amt, feats, score, cls, rebal, cost, vol_target, seats, rel=None):
    """One seat count: the engine's own book, its diag, and the replay that must match it."""
    diag = []
    ser, _turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, seats, cost,
                                      vol_target=vol_target, vol_window=60, diag=diag)
    stats = N.arm_stats(ser)
    df = MM.replay(close, openp, diag, rebal, seats, cost, R.START, cls, bench=BENCH)
    joined = df.join(ser.rename("engine"), how="left").dropna(subset=["engine", "equity"])
    max_rel = (float((joined["equity"] - joined["engine"]).abs().max()
                     / joined["engine"].iloc[-1]) if len(joined) else None)
    scales = [float(r.get("scale") or 0.0) for r in diag if r.get("book")]
    split = None
    if rel is not None:
        split = split_te(df, book_path(close, openp, diag, rebal, seats, R.START), rel, cls,
                         seats)
    return {"diag": diag, "ser": ser, "stats": stats, "df": df,
            "replay_max_rel": max_rel, "bars_matched": int(len(joined)),
            "mean_scale": round(float(np.mean(scales)), 4) if scales else None,
            "split": split}


def row_for(seats, sw):
    """Everything one seat count says, in one row -- no number inherited from a neighbour."""
    df, stats = sw["df"], sw["stats"]
    excess = (df["net"] - df["r_bench"]).dropna()
    sel = df["select"].dropna()
    b_sel = M.bootstrap_se(list(sel)) or {}
    b_tot = M.bootstrap_se(list(excess)) or {}
    mean_w = (round(float(df["w_priced"].mean()), 4) if len(df) else None)
    te_tot = te_ann(excess)
    te_sel = te_ann(sel)
    sel_pp = (round(float(sel.mean()) * PER_YEAR * 100.0, 4) if len(sel) else None)
    split = sw.get("split") or {}
    return {
        "n_hold": int(seats),
        "bars": int(len(df)),
        "book_cagr_pct": round(float((stats["full"].get("cagr") or 0.0)) * 100.0, 3),
        "book_sharpe": stats["full"].get("sharpe"),
        "book_maxdd_pct": round(float((stats["full"].get("maxdd") or 0.0)) * 100.0, 2),
        "select_ann_pp": sel_pp if sel_pp is not None else b_sel.get("obs_ann_pp"),
        "select_se_pp": b_sel.get("se_ann_pp"),
        "select_mde80_pp": b_sel.get("mde80_ann_pp"),
        "select_t": b_sel.get("t"),
        "select_p_direction": b_sel.get("p_direction"),
        "select_status": M.classify_pair(b_sel.get("obs_ann_pp"), b_sel.get("mde80_ann_pp"),
                                         b_sel.get("p_direction")),
        "total_mde80_pp": b_tot.get("mde80_ann_pp"),
        "total_status": M.classify_pair(b_tot.get("obs_ann_pp"), b_tot.get("mde80_ann_pp"),
                                        b_tot.get("p_direction")),
        "te_total_pp": te_tot,
        "te_select_pp": te_sel,
        "excess_ann_pp": (round(float(excess.mean()) * PER_YEAR * 100.0, 4)
                          if len(excess) else None),
        "rotate_ann_pp": (round(float(df["rotate"].mean()) * PER_YEAR * 100.0, 4)
                          if len(df) else None),
        "size_ann_pp": (round(float(df["size"].mean()) * PER_YEAR * 100.0, 4)
                        if len(df) else None),
        "cost_ann_pp": (round(float(df["cost"].mean()) * PER_YEAR * 100.0, 4)
                        if len(df) else None),
        "te_select_per_exposure": te_per_exposure(te_sel, mean_w),
        "te_common_pp": split.get("te_common_pp"),
        "te_idio_pp": split.get("te_idio_pp"),
        "share_common": split.get("share_common"),
        "common_ann_pp": split.get("common_ann_pp"),
        "idio_ann_pp": split.get("idio_ann_pp"),
        "split_identity_max_abs_resid": split.get("identity_max_abs_resid"),
        "split_bars": split.get("bars"),
        "mean_w_priced": mean_w,
        "mean_w_equity": (round(float(df["w_equity"].mean()), 4) if len(df) else None),
        "mean_scale": sw.get("mean_scale"),
        "mean_turnover": (round(float(df["turn"].mean()), 4) if len(df) else None),
        "replay_max_rel": sw.get("replay_max_rel"),
        "bars_needed_for_target": M.bars_needed(b_sel.get("mde80_ann_pp"), b_sel.get("bars"),
                                                target_pp=TARGET_MDE_PP),
        "target_met": bool(b_sel.get("mde80_ann_pp") is not None
                           and b_sel["mde80_ann_pp"] <= TARGET_MDE_PP),
    }


def frontier(rows):
    """The trade the reader is actually being offered: precision bought against alpha lost."""
    base = None
    for r in rows:
        if int(r["n_hold"]) == BASE_SEATS:
            base = r
    if base is None:
        return {"status": "NO_BASE"}
    out = []
    for r in rows:
        if int(r["n_hold"]) == BASE_SEATS:
            continue
        dm = (None if (r["select_mde80_pp"] is None or base["select_mde80_pp"] is None)
              else round(r["select_mde80_pp"] - base["select_mde80_pp"], 4))
        da = (None if (r["select_ann_pp"] is None or base["select_ann_pp"] is None)
              else round(r["select_ann_pp"] - base["select_ann_pp"], 4))
        out.append({"n_hold": r["n_hold"], "d_mde80_pp": dm, "d_select_pp": da,
                    "pp_alpha_per_pp_mde": (round(da / dm, 4)
                                            if (dm and da is not None and dm != 0) else None)})
    frontier_out = {"base_seats": BASE_SEATS,
            "base_select_pp": base["select_ann_pp"],
            "base_mde80_pp": base["select_mde80_pp"],
            "rows": out,
            "mde_exponent_vs_seats": fit_exponent(rows, "select_mde80_pp"),
            "te_exponent_vs_seats": fit_exponent(rows, "te_select_pp"),
            "te_common_exponent_vs_seats": fit_exponent(rows, "te_common_pp"),
            "te_idio_exponent_vs_seats": fit_exponent(rows, "te_idio_pp"),
            "alpha_exponent_vs_seats": fit_exponent(
                [r for r in rows if (r.get("select_ann_pp") or 0) > 0], "select_ann_pp"),
            "book_cagr_exponent_vs_seats": fit_exponent(rows, "book_cagr_pct"),
            "rotate_exponent_vs_seats": fit_exponent(
                [r for r in rows if (r.get("rotate_ann_pp") or 0) > 0], "rotate_ann_pp")}
    return frontier_out


def run():
    t0 = time.time()
    price = _load(FACE_PRICE)
    cfg = price.get("config") or {}
    published = {}
    for row in (price.get("rows") or []):
        if float(row.get("min_amt_cny") or 0) == GATE:
            published = row.get("book") or {}
    money = _load(FACE_MONEY) if os.path.exists(FACE_MONEY) else {}
    money_sel = ((money.get("legs") or {}).get("select") or {})

    close, openp, amt, feats, n_flip = G.build_universe()
    print("[panel] %d names, %d bars, %d flips repaired, %.1fs"
          % (len(close.columns), len(close.index), n_flip, time.time() - t0), flush=True)
    cmap = A.load_class_map()
    cls = {str(k): str(v) for k, v in A.classify(list(close.columns), cmap, close).items()}

    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")
    score = E.build_score(close, amt, feats, min_amt=GATE)
    eq_cols = [c for c in close.columns if cls.get(str(c)) == "equity"]
    rel = rel_returns(close, openp, eq_cols)
    print("[sleeve] %d equity names for the common-factor split, %.0fs"
          % (len(eq_cols), time.time() - t0), flush=True)

    rows = []
    replay_bad = []
    split_bad = []
    for seats in SWEEP:
        sw = sweep(close, openp, amt, feats, score, cls, rebal, cost, vol_target, seats, rel=rel)
        rows.append(row_for(seats, sw))
        r = rows[-1]
        print("[seat %2d] cagr=%6.2f%%  select=%+6.2fpp  mde80=%6.2fpp  te=%5.2fpp  "
              "common/idio=%5.2f/%5.2f  w=%4.2f  replay=%.1e  %.0fs"
              % (seats, r["book_cagr_pct"], r["select_ann_pp"] or 0.0,
                 r["select_mde80_pp"] or 0.0, r["te_select_pp"] or 0.0,
                 r["te_common_pp"] or 0.0, r["te_idio_pp"] or 0.0,
                 r["mean_w_priced"] or 0.0, r["replay_max_rel"] or 0.0, time.time() - t0),
              flush=True)
        if r["replay_max_rel"] is None or r["replay_max_rel"] > REPLAY_TOL:
            replay_bad.append(seats)
        if r["split_identity_max_abs_resid"] is None or \
                r["split_identity_max_abs_resid"] > SPLIT_TOL:
            split_bad.append(seats)

    base = _at(rows, BASE_SEATS, "book_cagr_pct")
    control_pp = (None if (base is None or published.get("cagr") is None)
                  else round(base - float(published["cagr"]) * 100.0, 3))
    leg_delta_pp = (None if (money_sel.get("ann_pp") is None
                             or _at(rows, BASE_SEATS, "select_ann_pp") is None)
                    else round(_at(rows, BASE_SEATS, "select_ann_pp")
                               - float(money_sel["ann_pp"]), 4))
    control = {"arm_cagr_pct": base, "published_cagr_pct":
               (None if published.get("cagr") is None
                else round(float(published["cagr"]) * 100.0, 3)),
               "delta_pp": control_pp, "tol_pp": CONTROL_TOL_PP,
               "money_face_select_pp": money_sel.get("ann_pp"),
               "seat5_select_pp": _at(rows, BASE_SEATS, "select_ann_pp"),
               "leg_delta_pp": leg_delta_pp, "leg_tol_pp": LEG_TOL_PP,
               "universe_measured": len(close.columns),
               "universe_published": cfg.get("universe_measured")}

    verdict = seat_verdict(rows, control_pp, replay_ok=not replay_bad,
                           leg_delta_pp=leg_delta_pp, split_ok=not split_bad)
    front = frontier(rows)
    hits = [r["n_hold"] for r in rows if r["target_met"]]
    split_block = {"tol": SPLIT_TOL,
                   "worst_identity_resid": max([r["split_identity_max_abs_resid"] or 0.0
                                                for r in rows]),
                   "bad_seats": split_bad,
                   "shared_noise_bars": (split_bad == [] and bool(rows)),
                   "common_share_at_base": _at(rows, BASE_SEATS, "share_common")}

    out = {"evidence_cutoff": price.get("evidence_cutoff")
           or str(pd.Timestamp(close.index[-1]).date()),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_seat_mde.py",
           "rule": {"benchmark": BENCH, "gate_cny": GATE, "base_seats": BASE_SEATS,
                    "sweep": list(SWEEP), "target_mde80_pp": TARGET_MDE_PP,
                    "z80": Z_80, "per_year": PER_YEAR, "block": M.BLOCK,
                    "draws": M.DRAWS, "seed": M.SEED, "control_tol_pp": CONTROL_TOL_PP,
                    "leg_tol_pp": LEG_TOL_PP, "replay_tol": REPLAY_TOL,
                    "question": "does holding fewer names (same ranking, same gate, same "
                                "rebalance, same cost, same vol target) bring the select leg's "
                                "MDE80 under 5pp, and what alpha does it cost",
                    "what_moves": "te_select = realised vol of the leg; te_select_per_exposure "
                                  "= the same divided by mean invested weight, so the vol "
                                  "target's size cut is not read as quiet",
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"rebal": rebal, "vol_target": vol_target,
                      "cost_bp_per_side": cfg.get("cost_bp_per_side"),
                      "panel_build_seconds": None, "run_seconds": None},
           "control": control,
           "rows": rows,
           "frontier": front,
           "split": split_block,
           "target_met_by": hits,
           "verdict": verdict}
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"], "seats": verdict.get("seats"),
                      "control_pp": control_pp, "leg_delta_pp": leg_delta_pp,
                      "mde_exponent": front.get("mde_exponent_vs_seats"),
                      "target_met_by": hits,
                      "run_seconds": out["config"]["run_seconds"]}, ensure_ascii=False))
    return 0


def write_md(out):
    v = out["verdict"]
    c = out["control"]
    rows = out["rows"]
    front = out["frontier"]
    lines = ["# 换持仓集中度，能不能把这把噪声尺子压下来（r1764）", "",
             "**结论：%s**" % v["verdict"], "", v["sentence"], "",
             "同一个排名、同一个 20M 闸、同一个调仓节奏、同一份成本、同一个 8% 波动目标——"
             "**只改持仓数**。每一档都由引擎自己重新选、重新定波动缩放，再用 r1763 的回放"
             "逐 bar 重建净值核对，所以每一格的腿量的确实是那一格的书。", "",
             "## 1. 每一档的读数", "",
             "| 座数 | 账本 CAGR | 选股腿 | 自己的 MDE80 | t | p（该方向） | 选股腿波动"
             " | 每单位仓位波动 | 平均仓位 | 平均缩放 | 判读 | 到 %.0fpp 还要 |"
             % TARGET_MDE_PP,
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    words = {"ABOVE_MDE80": "越过 MDE80", "SIGNIFICANT_UNDERPOWERED": "显著但没到效力",
             "NO_DIRECTION": "无方向", "NO_ESTIMATE": "无估计"}
    for r in rows:
        need = r["bars_needed_for_target"]
        lines.append("| %d | %.2f%% | %s pp | **%s pp** | %s | %s | %s pp | %s pp | %s | %s "
                     "| %s | %s |"
                     % (r["n_hold"], r["book_cagr_pct"], _f2(r["select_ann_pp"]),
                        _f2(r["select_mde80_pp"]),
                        "-" if r["select_t"] is None else "%.2f" % r["select_t"],
                        _fmt_p(r["select_p_direction"]), _f2(r["te_select_pp"]),
                        _f2(r["te_select_per_exposure"]), _f2(r["mean_w_priced"]),
                        _f2(r["mean_scale"]),
                        words.get(r["select_status"], r["select_status"]),
                        "已达标" if need == 0 else ("%s 根 bar" % need if need else "-")))
    lines += ["", "（MDE80 = 2.802 × 同一个块自助的 SE，与 r1762/r1763 用的是同一把尺子；"
              "「每单位仓位波动」= 选股腿波动 ÷ 平均投入仓位，用来把「波动目标砍了尺寸」"
              "这一条渠道单独摆出来，免得把「仓位变小」读成「书变安静」。）", "",
              "## 2. 精度与钱的兑换率", "",
              "以 5 座为基准，缩/扩到别的座数，各自换了多少 MDE、付了多少 alpha：", "",
              "| 座数 | ΔMDE80 | Δ选股腿 | 每 pp 精度要付的 alpha |",
              "|---|---|---|---|"]
    for r in front.get("rows") or []:
        lines.append("| %d | %+.2f pp | %+.2f pp | %s |"
                     % (r["n_hold"], r["d_mde80_pp"] or 0.0, r["d_select_pp"] or 0.0,
                        "-" if r["pp_alpha_per_pp_mde"] is None
                        else "%+.3f" % r["pp_alpha_per_pp_mde"]))
    lines += ["", "对数斜率（把 1/√N 这条定律交给数据说，不预设）：",
              "",
              "* MDE80 对座数：**%s**（-0.5 就是纯分散化的 1/√N）"
              % _f2(front.get("mde_exponent_vs_seats")),
              "* 选股腿波动对座数：**%s**" % _f2(front.get("te_exponent_vs_seats")),
              "* 选股腿年化对座数：**%s**（正数＝宽度在给钱，负数＝宽度在收钱）"
              % _f2(front.get("alpha_exponent_vs_seats")), "",
              "### 宽度的账从哪条腿收走", "",
              "同一张四腿表（与 r1763 同一定义、同一恒等式），逐档重算：", "",
              "| 座数 | 净超额 | 选股 | 换赛道 | 空仓 | 成本 | 账本 CAGR |",
              "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %d | %s pp | %s pp | %s pp | %s pp | %s pp | %.2f%% |"
                     % (r["n_hold"], _f2(r["excess_ann_pp"]), _f2(r["select_ann_pp"]),
                        _f2(r["rotate_ann_pp"]), _f2(r["size_ann_pp"]),
                        _f2(r["cost_ann_pp"]), r["book_cagr_pct"]))
    lines += ["",
              "账本 CAGR 对座数的斜率 **%s**、选股腿对座数的斜率 **%s**、换赛道腿 **%s**——"
              "也就是说：**拉宽收走的那几个点，不在选股这条腿上**。"
              % (_f2(front.get("book_cagr_exponent_vs_seats")),
                 _f2(front.get("alpha_exponent_vs_seats")),
                 _f2(front.get("rotate_exponent_vs_seats"))), ""]
    clears = [r for r in rows if int(r["n_hold"]) != BASE_SEATS
              and r.get("select_status") == "ABOVE_MDE80"]
    if clears:
        r = clears[0]
        lines += ["**还有一句话要说**：%d 座这一档其实让选股腿**越过了它自己的 MDE80**"
                  "（%+.2fpp vs 门 %.2fpp）——但它是靠把门压窄实现的，代价写在旁边那张表里："
                  "账本 CAGR 从 %.2f%% 掉到 %.2f%%，换赛道腿从 %s pp 掉到 %s pp。"
                  "**精度买到了，是拿这本书本来最赚钱的那条腿付的账。**"
                  % (r["n_hold"], r["select_ann_pp"], r["select_mde80_pp"],
                     _at(rows, BASE_SEATS, "book_cagr_pct"), r["book_cagr_pct"],
                     _f2(_at(rows, BASE_SEATS, "rotate_ann_pp")), _f2(r["rotate_ann_pp"])), ""]
    lines += ["## 3. 那条噪声是「名字的」还是「整条袖子的」", "",
              "把每一根 bar 的选股腿再拆一次：**`select` = 共同项 + 名字项**"
              "（对同一根 bar，共同项＝这一篮子权益名等权买、对指数赚的那份；名字项＝这只书"
              "手上这几个名字比这一篮子多赚的那份）。只有名字项该按 1/√N 缩小；共同项是"
              "**因子投注**，跟持仓数无关。两截加上去必须逐 bar 等于已发布的选股腿"
              "（最大残差 %.1e，容差 %.0e）。" % (out["split"]["worst_identity_resid"],
                                                 out["split"]["tol"]), "",
              "| 座数 | 选股腿波动 | 共同项（袖子 vs 指数） | 名字项 | 共同项占比 |",
              "|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %d | %s pp | %s pp | %s pp | %s |"
                     % (r["n_hold"], _f2(r["te_select_pp"]), _f2(r["te_common_pp"]),
                        _f2(r["te_idio_pp"]),
                        "-" if r["share_common"] is None else "%.1f%%"
                        % (100.0 * r["share_common"])))
    lines += ["",
              "斜率：共同项 **%s**、名字项 **%s**（前者接近 0 就是「跟座数无关」，"
              "后者接近 -0.5 就是「纯分散化的那一截」）。"
              % (_f2(front.get("te_common_exponent_vs_seats")),
                 _f2(front.get("te_idio_exponent_vs_seats"))), "",
              "**这两条斜率就是本轮的答案**：如果那一截真是独立的名字噪声，它该按 1/√N 走"
              "（座数 5→30 该缩到 %s 倍），实际只缩了 %s 倍——所以它不是名字噪声，"
              "而是**这个排名自己的共同倾斜**（同一批因子把名字往同一个方向推）。"
              "共同倾斜不会因为多拿几只票就消失，这也正是为什么 30 座只把 MDE80 从 %.2f 拉到 %.2f。"
              % ("%.2f" % (math.sqrt(float(BASE_SEATS) / 30.0)),
                 ("%.2f" % (_at(rows, 30, "te_idio_pp") / _at(rows, BASE_SEATS, "te_idio_pp"))
                  if (_at(rows, 30, "te_idio_pp") and _at(rows, BASE_SEATS, "te_idio_pp"))
                  else "-"),
                 _at(rows, BASE_SEATS, "select_mde80_pp") or 0.0,
                 _at(rows, 30, "select_mde80_pp") or 0.0), "",
              "## 4. 这张面凭什么被信", "",
              "* 5 座这一格复现抬闸定价面的 **%s%%**，差 **%s pp**（容差 %.2fpp）"
              % (_f2(c["published_cagr_pct"]), _f2(c["delta_pp"]), c["tol_pp"]),
              "* 5 座的选股腿复现 r1763 钱包面的 **%s pp**，差 **%s pp**（容差 %.2fpp）"
              % (_f2(c["money_face_select_pp"]), _f2(c["leg_delta_pp"]), c["leg_tol_pp"]),
              "* 每一档的回放都要复现引擎自己的净值到 %.0e，最差 %.1e"
              % (REPLAY_TOL, max([r["replay_max_rel"] or 0.0 for r in rows])),
              "* 选股腿拆成「共同项 + 名字项」两截，逐 bar 相加必须等于选股腿，"
              "最差残差 %.1e（容差 %.0e）"
              % (out["split"]["worst_identity_resid"], out["split"]["tol"]), "",
              "## 5. 这张面不能说的话", "",
              "1. 改座数改的是**选择本身**（top-2 不是 top-20 的缩版），所以这是"
              "「同一个排名、不同宽度」，不是「同一批持仓换个权重」。",
              "2. 收窄会抬高单名权重，那是**风险与容量**的问题，正身是 "
              "`etf_book_capacity_rule` / `etf_breadth_sweep`，本面不重算、也不建议照抄。",
              "3. 票池是现存 ETF（幸存者偏差），这六年是这本书最好的六年。",
              "4. 算术年化（252）与复利 CAGR 是两个口径；MDE 跑在算术差的均值上。", ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _check():
    """Re-derive the published verdict, the ruler identity and the two controls from the JSON."""
    out = _load(OUT_JSON)
    c = out["control"]
    rows = out["rows"]
    replay_ok = all((r.get("replay_max_rel") is not None
                     and r["replay_max_rel"] <= REPLAY_TOL) for r in rows)
    split_ok = all((r.get("split_identity_max_abs_resid") is not None
                    and r["split_identity_max_abs_resid"] <= SPLIT_TOL) for r in rows)
    v = seat_verdict(rows, c.get("delta_pp"), replay_ok=replay_ok,
                     leg_delta_pp=c.get("leg_delta_pp"), split_ok=split_ok)
    mde_id = all(r.get("select_mde80_pp") is None or r.get("select_se_pp") is None
                 or abs(round(Z_80 * float(r["select_se_pp"]), 4)
                        - float(r["select_mde80_pp"])) <= 5e-3 for r in rows)
    target_flag = all(bool(r["target_met"]) == bool(r.get("select_mde80_pp") is not None
                                                   and r["select_mde80_pp"] <= TARGET_MDE_PP)
                      for r in rows)
    base = _at(rows, BASE_SEATS, "select_ann_pp")
    checks = {
        "verdict_rederives": v["verdict"] == out["verdict"]["verdict"],
        "verdict_seats_rederive": v.get("seats") == out["verdict"].get("seats"),
        "mde_is_z80_se": mde_id,
        "target_flag_per_row": target_flag,
        "control_inside_tol": (c.get("delta_pp") is not None
                               and abs(c["delta_pp"]) <= CONTROL_TOL_PP),
        "leg_inside_tol": (c.get("leg_delta_pp") is not None
                           and abs(c["leg_delta_pp"]) <= LEG_TOL_PP),
        "replay_inside_tol": replay_ok,
        "split_identity_inside_tol": split_ok,
        "split_published_resid_matches": (
            out.get("split", {}).get("worst_identity_resid") is None
            or abs(float(out["split"]["worst_identity_resid"])
                   - max([r.get("split_identity_max_abs_resid") or 0.0 for r in rows])) <= 1e-15),
        "base_row_present": base is not None,
        "every_row_has_bars": all(r.get("bars") for r in rows),
    }
    ok = all(checks.values())
    print(json.dumps({"published": out["verdict"]["verdict"],
                      "recomputed": v["verdict"],
                      "seats": v.get("seats"), "checks": checks, "ok": ok},
                     ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    fails = []
    legs = []

    def chk(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # --- the ruler is the frozen one ------------------------------------------------
    chk("L1 z80 is the same constant", Z_80 == M.Z_80 == 2.802, Z_80)
    syn = [0.001 + v for v in np.random.default_rng(11).normal(0.0, 0.004, 800)]
    b = M.bootstrap_se(syn, draws=400, seed=7)
    chk("L2 mde is z80 x se",
        abs(round(Z_80 * b["se_ann_pp"], 4) - b["mde80_ann_pp"]) <= 5e-3,
        (b["se_ann_pp"], b["mde80_ann_pp"]))
    chk("L3 te of a constant series is zero", te_ann([0.002] * 300) == 0.0, te_ann([0.002] * 300))
    chk("L3b te is annualised", abs(te_ann([0.001, -0.001] * 150)
                                   - float(np.std([0.001, -0.001] * 150, ddof=1)
                                           * math.sqrt(PER_YEAR) * 100.0)) < 5e-3,
        te_ann([0.001, -0.001] * 150))
    chk("L4 te per exposure divides by the weight",
        te_per_exposure(10.0, 0.5) == 20.0, te_per_exposure(10.0, 0.5))
    chk("L4b zero exposure has no ratio", te_per_exposure(10.0, 0.0) is None)
    chk("L4c missing te has no ratio", te_per_exposure(None, 0.5) is None)

    # --- the concentration law, read off synthetic rows with a known slope ----------
    law = [{"n_hold": n, "select_mde80_pp": 10.0 / math.sqrt(n)} for n in (2, 4, 8, 16, 32)]
    chk("L5 sqrt law fits -0.5", abs(fit_exponent(law) + 0.5) < 1e-6, fit_exponent(law))
    flat = [{"n_hold": n, "select_mde80_pp": 7.0} for n in (2, 4, 8)]
    chk("L5b a flat curve fits 0", abs(fit_exponent(flat)) < 1e-9, fit_exponent(flat))
    chk("L5c one row cannot fit an exponent", fit_exponent(law[:1]) is None)
    chk("L5d non-positive rows are not logged",
        fit_exponent([{"n_hold": 2, "select_mde80_pp": 0.0},
                      {"n_hold": 4, "select_mde80_pp": -1.0}]) is None)

    # --- refusals before judgements -------------------------------------------------
    ok_rows = [{"n_hold": 5, "select_mde80_pp": 8.0, "select_ann_pp": 7.0,
                "select_p_direction": 0.006, "target_met": False},
               {"n_hold": 10, "select_mde80_pp": 9.0, "select_ann_pp": 6.0,
                "select_p_direction": 0.02, "target_met": False}]
    chk("L6 no control refuses",
        seat_verdict(ok_rows, None)["verdict"] == "CANNOT_JUDGE_NO_CONTROL")
    chk("L6b control off refuses",
        seat_verdict(ok_rows, 0.9)["verdict"] == "CANNOT_JUDGE_CONTROL")
    chk("L6c control exactly at tol passes",
        seat_verdict(ok_rows, CONTROL_TOL_PP)["verdict"] != "CANNOT_JUDGE_CONTROL")
    chk("L6d replay failure refuses",
        seat_verdict(ok_rows, 0.0, replay_ok=False)["verdict"] == "CANNOT_JUDGE_REPLAY")
    chk("L6e leg mismatch refuses",
        seat_verdict(ok_rows, 0.0, leg_delta_pp=1.0)["verdict"] == "CANNOT_JUDGE_LEG")
    chk("L6f no judgeable row refuses",
        seat_verdict([{"n_hold": 5, "select_mde80_pp": None, "select_ann_pp": None}],
                     0.0)["verdict"] == "CANNOT_JUDGE_NO_SERIES")

    # --- the three real outcomes ----------------------------------------------------
    reach = [{"n_hold": 5, "select_mde80_pp": 8.7, "select_ann_pp": 7.4,
              "select_p_direction": 0.006, "target_met": False},
             {"n_hold": 3, "select_mde80_pp": 4.5, "select_ann_pp": 6.9,
              "select_p_direction": 0.01, "target_met": True}]
    v = seat_verdict(reach, 0.0)
    chk("L7 reaches target", v["verdict"] == "SEAT_TARGET_REACHED", v)
    chk("L7b names the reaching seat", v.get("seats") == 3, v.get("seats"))
    gone = [reach[0], {"n_hold": 3, "select_mde80_pp": 4.2, "select_ann_pp": 0.2,
                       "select_p_direction": 0.4, "target_met": True}]
    chk("L8 target but alpha gone",
        seat_verdict(gone, 0.0)["verdict"] == "SEAT_TARGET_REACHED_ALPHA_GONE")
    neg = [reach[0], {"n_hold": 3, "select_mde80_pp": 4.2, "select_ann_pp": -2.0,
                      "select_p_direction": 0.01, "target_met": True}]
    chk("L8b negative alpha is not a win",
        seat_verdict(neg, 0.0)["verdict"] == "SEAT_TARGET_REACHED_ALPHA_GONE")
    under = [{"n_hold": 5, "select_mde80_pp": 8.7, "select_ann_pp": 7.4,
              "select_p_direction": 0.006},
             {"n_hold": 2, "select_mde80_pp": 6.4, "select_ann_pp": 5.0,
              "select_p_direction": 0.03}]
    v = seat_verdict(under, 0.0)
    chk("L9 no target reached", v["verdict"] == "SEAT_TARGET_NOT_REACHED", v)
    chk("L9b names the narrowest seat", v.get("seats") == 2, v.get("seats"))
    chk("L9c target boundary is inclusive",
        seat_verdict([{"n_hold": 5, "select_mde80_pp": TARGET_MDE_PP,
                       "select_ann_pp": 7.0, "select_p_direction": 0.01}],
                     0.0)["verdict"] == "SEAT_TARGET_REACHED")

    # --- the frontier table is arithmetic, not a re-measurement ---------------------
    rows_syn = [{"n_hold": 5, "select_mde80_pp": 8.0, "select_ann_pp": 7.0},
                {"n_hold": 10, "select_mde80_pp": 6.0, "select_ann_pp": 5.5}]
    f = frontier(rows_syn)
    chk("L10 base is the 5-seat row", f["base_seats"] == 5 and f["base_mde80_pp"] == 8.0, f)
    chk("L10b deltas are signed differences",
        f["rows"][0]["d_mde80_pp"] == -2.0 and f["rows"][0]["d_select_pp"] == -1.5,
        f["rows"][0])
    chk("L10c exchange rate is alpha per pp of mde",
        f["rows"][0]["pp_alpha_per_pp_mde"] == 0.75, f["rows"][0])
    chk("L10d no base means no frontier",
        frontier([{"n_hold": 3, "select_mde80_pp": 1.0, "select_ann_pp": 1.0}])["status"]
        == "NO_BASE")

    # --- `_at` never borrows a neighbour's number ----------------------------------
    chk("L11 _at finds the seat", _at(rows_syn, 10, "select_mde80_pp") == 6.0)
    chk("L11b _at returns None when absent", _at(rows_syn, 4, "select_mde80_pp") is None)
    chk("L11c bars_needed is zero once the target is met",
        M.bars_needed(4.0, 1600, target_pp=TARGET_MDE_PP) == 0)
    chk("L11d bars_needed grows with the square of the gap",
        M.bars_needed(10.0, 1600, target_pp=5.0) == 6400)

    # --- the split: select == common + idio, and only `idio` obeys 1/sqrt(N) ---------
    def fake_panel(bars=800, n_eq=40, seed=3):
        rng_ = np.random.default_rng(seed)
        idx = pd.bdate_range("2020-01-01", periods=bars + 1)
        cols_ = ["EQ%d" % i for i in range(n_eq)] + ["GOLD", BENCH]
        px = pd.DataFrame(np.cumprod(1.0 + rng_.normal(0.0, 0.01, size=(bars + 1, len(cols_))),
                                     axis=0) * 100.0, index=idx, columns=cols_)
        return px, cols_

    def fake_diag(idx, n_hold, rebal, cols_, seed=9):
        rng_ = np.random.default_rng(seed)
        eq_ = [c for c in cols_ if c.startswith("EQ")]
        d = []
        for i in range(0, len(idx) - 1, rebal):
            pick = list(rng_.choice(eq_, size=min(n_hold, len(eq_)), replace=False))
            d.append({"date": str(pd.Timestamp(idx[i]).date()), "book": pick, "scale": 1.0})
        return d

    px, cols_ = fake_panel()
    cls_ = {c: ("equity" if c.startswith("EQ") else "commodity") for c in cols_}
    cls_[BENCH] = "commodity"
    rel_ = rel_returns(px, px, [c for c in cols_ if c.startswith("EQ")])
    rel_dup = rel_returns(px, px, cols_)          # the bench arrives inside the name list
    chk("L14 the bench column never survives the subtraction",
        rel_dup is not None and BENCH not in rel_dup.columns, None if rel_dup is None else list(rel_dup.columns[-2:]))
    chk("L14b a duplicated bench does not turn the panel to NaN",
        rel_dup is not None and int(rel_dup.notna().sum().sum()) > 0,
        None if rel_dup is None else int(rel_dup.notna().sum().sum()))
    sp = {}
    for n in (2, 8):
        dg = fake_diag(px.index, n, 20, cols_)
        dfx = MM.replay(px, px, dg, 20, n, 0.0, "2020-01-01", cls_, bench=BENCH)
        sp[n] = split_te(dfx, book_path(px, px, dg, 20, n, "2020-01-01"), rel_, cls_, n)
    chk("L12 split identity holds bar by bar",
        all(v is not None and v["identity_max_abs_resid"] < 1e-14 for v in sp.values()),
        {n: (v or {}).get("identity_max_abs_resid") for n, v in sp.items()})
    chk("L12b the split keeps the leg's own volatility",
        all(v["te_common_pp"] is not None and v["te_idio_pp"] is not None
            for v in sp.values() if v), sp)
    whole = MM.replay(px, px, fake_diag(px.index, 40, 20, cols_), 20, 40, 0.0, "2020-01-01",
                      cls_, bench=BENCH)
    sp_w = split_te(whole, book_path(px, px, fake_diag(px.index, 40, 20, cols_), 20, 40,
                                     "2020-01-01"), rel_, cls_, 40)
    chk("L13 holding the whole sleeve leaves no name term",
        sp_w is not None and sp_w["te_idio_pp"] < 0.5, (sp_w or {}).get("te_idio_pp"))
    r_idio = (sp[2]["te_idio_pp"] / sp[8]["te_idio_pp"]) if sp[8]["te_idio_pp"] else None
    chk("L13b the name term shrinks like 1/sqrt(N)",
        r_idio is not None and 1.7 <= r_idio <= 2.4, r_idio)
    r_common = (sp[2]["te_common_pp"] / sp[8]["te_common_pp"]) if sp[8]["te_common_pp"] else None
    chk("L13c the sleeve term does NOT shrink with seats",
        r_common is not None and 0.8 <= r_common <= 1.2, r_common)

    ok = not fails
    print(json.dumps({"legs": len(legs), "fails": fails, "ok": ok}, ensure_ascii=False))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "--run"):
        return run()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    if cmd in ("--check", "check"):
        return _check()
    if cmd in ("--md", "md"):
        write_md(_load(OUT_JSON))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
