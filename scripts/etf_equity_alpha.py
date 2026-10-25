"""ETF composite -- split the book into equity vs bond/money sleeves.

Question this answers: the robust book's 10%/yr is half bond carry. How much of it is
real equity alpha, and how much is just parking in bond ETFs?

Method (same no-lookahead leg engine as etf_robust_pf.open_to_open_equity, not a reimplementation
of the fill maths -- this script re-uses the same per-bar leg chain and adds attribution):
  * classify every ETF by name keywords (bond / money / commodity / equity)
  * run the fixed production cell N5/R20/10bp on three universes: all, equity-only, bond+money-only
  * on the ALL run, split每 bar P&L into equity vs bond/money contribution (gross) and report cost drag
  * report the class mix of holdings over time, and the share of rebalance dates that were fully defensive
  * benchmarks: equal weight of the eligible universe inside each class

Equity-only vs equity EW is the pure-alpha test: if the composite cannot beat its own
universe with the bonds removed, then the money was carry, not stock selection.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
from config import PATHS

IS_END = "2023-12-31"
START = "2020-01-01"
REBAL, N_HOLD, COST = 20, 5, 0.0010
NAME_CSV = os.path.join(PATHS.basic_dir, "etf_list.csv")

# first match wins: a convertible-bond ETF (转债) is counted as its own class, since it is
# equity-like and would otherwise blow up the bond sleeve's volatility.
CLASS_RULES = [
    ("convertible", ("转债",)),
    ("bond", ("债",)),
    ("money", ("货币", "现金")),
    ("commodity", ("黄金", "白银", "原油", "豆粕", "有色", "商品", "能源化工")),
    ("equity", ()),
]

# ETF quotes occasionally flip their face value (per-100 <-> per-unit). 511030 dropped 90%
# on 2021-01-11 and jumped +900% back on 2025-03-19; 511220 dropped 90% on 2023-01-16 and
# never came back. Left alone these print fake +-900% days into the book.
FLIP_THR = 0.35


def repair_flips(close, openp, thr=FLIP_THR):
    """Flatten single-day moves beyond `thr` and rescale both faces to keep levels continuous.

    A flat day at a flip means the raw jump becomes a 0% return; the cumulative factor is
    then applied to the open face as well so open-to-open legs stay consistent.
    """
    r = close.pct_change()
    bad = r.abs() > thr
    r_clean = r.where(~bad, 0.0).fillna(0.0)
    first = close.ffill().bfill().iloc[0]
    adj = (1.0 + r_clean).cumprod().multiply(first, axis=1)
    adj = adj.where(close.notna())
    factor = adj / close
    return adj, openp * factor, int(bad.to_numpy().sum())


def load_class_map():
    """code -> (keyword class, name). Keyword class is only a first pass: plenty of cash
    ETFs are named 短融ETF / 银华日利 / 招商快线 and carry no bond keyword at all, so they
    were being counted as equity (they then topped the live picks as "equity")."""
    d = None
    for enc in ("utf-8-sig", "gb18030", "gbk"):
        try:
            d = pd.read_csv(NAME_CSV, encoding=enc)
            break
        except Exception:
            continue
    code_col, name_col = d.columns[0], d.columns[1]
    out = {}
    for code, name in zip(d[code_col].astype(str), d[name_col].astype(str)):
        c = str(code).lower().replace("sh", "").replace("sz", "").strip()[:6]
        nm = name
        cls = "unclassified"
        for k, kws in CLASS_RULES:
            if not kws or any(x in nm for x in kws):
                cls = k
                break
        out[c] = (cls, nm)
    return out


# realised-vol cut for the names that carry no class keyword: cash funds run <3%/yr,
# bond funds <8%/yr, equity funds sit above that. 511360 (短融ETF) prints ~0.3%.
MONEY_VOL, BOND_VOL = 0.03, 0.08


def classify(cols, cmap, close):
    r = close.pct_change()
    med_vol = (r.rolling(60, min_periods=30).std() * np.sqrt(252)).median()
    out = {}
    for c in cols:
        cls, nm = cmap.get(str(c)[:6], ("unclassified", ""))
        if cls == "equity":
            v = med_vol.get(c, np.nan)
            if np.isfinite(v):
                if v < MONEY_VOL:
                    cls = "money"
                elif v < BOND_VOL:
                    cls = "bond"
        out[c] = cls
    return pd.Series(out)


CLASSES = ("equity", "bond", "money", "commodity", "convertible", "unclassified")


def run_with_attribution(close, openp, amt, score, cls, rebal=REBAL, n_hold=N_HOLD,
                         cost=COST, start=START):
    """Same leg chain as R.open_to_open_equity; additionally books每 bar P&L by class."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]

    equity, held = 1.0, {}
    curve, contrib, turns, mixes = [], [], [], []

    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        cost_paid = 0.0
        if i % rebal == 0:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
                cost_paid = cost * turn
                equity *= (1.0 - cost_paid)
                turns.append(turn)
                held = w
                mixes.append({c: sum(wt for p, wt in w.items() if cls[p] == c)
                              for c in CLASSES})
        r_cls = {c: 0.0 for c in CLASSES}
        r_tot = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                rp = wt * (b / a - 1.0)
                r_tot += rp
                r_cls[cls[p]] += rp
        equity *= (1.0 + r_tot)
        curve.append((nxt, equity))
        contrib.append((nxt, r_tot, r_cls, cost_paid))

    ser = pd.Series(dict(curve)).sort_index()
    return ser, contrib, (float(np.mean(turns)) if turns else 0.0), mixes


def stats2(ser, label):
    """Renormalised stats: growth is measured against the slice's own first level.

    R.stats() annualises a sub-window as `last_level ** (1/years) - 1`, which silently
    assumes the slice starts at 1.0; every IS/OOS slice of a running curve starts above
    that, so those CAGRs come out too high. This is the corrected口径.
    """
    ser = ser.dropna()
    if len(ser) < 40:
        return {"label": label, "note": "short"}
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    growth = float(ser.iloc[-1]) / float(ser.iloc[0])
    cagr = growth ** (1 / yrs) - 1
    r = ser.pct_change().dropna()
    vol = float(r.std() * np.sqrt(252))
    dd = (ser / ser.cummax() - 1)
    yearly = ser.groupby(ser.index.year).apply(lambda x: x.iloc[-1] / x.iloc[0] - 1)
    monthly = ser.resample("ME").last().pct_change().dropna()
    return {
        "label": label, "years": round(yrs, 2), "start_level": round(float(ser.iloc[0]), 4),
        "cagr": round(float(cagr), 4), "vol": round(vol, 4),
        "sharpe": round(float(r.mean() * 252 / vol), 3) if vol > 0 else 0.0,
        "maxdd": round(float(dd.min()), 4),
        "worst_year": round(float(yearly.min()), 4),
        "neg_years": int((yearly < 0).sum()),
        "worst_month": round(float(monthly.min()), 4),
        "pos_months_pct": round(float((monthly > 0).mean()), 3),
    }


def ew_universe(close, amt, cls, want, start=START):
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    cols = [c for c in close.columns if cls[c] in want]
    px = close[cols].ffill()
    ret = px.pct_change()
    equity, curve = 1.0, []
    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    for i, d in enumerate(dates[:-1]):
        nd = dates[i + 1]
        live = [c for c in cols if bool(elig.at[d, c])]
        r = ret.loc[nd, live].mean() if live else 0.0
        if np.isfinite(r):
            equity *= (1.0 + r)
        curve.append((d, equity))
    return pd.Series(dict(curve))


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = repair_flips(close, openp)
    print("repaired flip cells:", n_flip, flush=True)
    cmap = load_class_map()
    cls = classify(close.columns, cmap, close)
    print("panel", close.shape, "class counts:", cls.value_counts().to_dict(), flush=True)

    score_all = E.build_score(close, amt, feats)
    out = {"cell": "N%d_R%d_%dbp" % (N_HOLD, REBAL, COST * 1e4),
           "execution": "decision at close t, execute at open t+1, hold to next open",
           "universe_class_counts": {k: int(v) for k, v in cls.value_counts().items()},
           "runs": [], "attribution": {}, "mixes_note": "weight by class at each rebalance"}

    def add(label, ser, extra=None):
        m = stats2(ser, label)
        for lbl, sl in (("is", ser[ser.index <= IS_END]),
                        ("oos", ser[ser.index > IS_END])):
            mm = stats2(sl, label + "_" + lbl)
            for k in ("cagr", "sharpe", "maxdd"):
                m[k + "_" + lbl] = mm.get(k)
        if extra:
            m.update(extra)
        out["runs"].append(m)
        print(m, flush=True)
        return m

    # 1) full universe (the production cell) + attribution
    ser_all, contrib, turn_all, mixes = run_with_attribution(close, openp, amt, score_all, cls)
    add("all_classes", ser_all, {"turnover": round(turn_all, 2)})

    # 2) equity-only and bond/money-only universes (scores re-ranked inside the sleeve)
    for label, want in (("equity_only", ("equity",)),
                        ("bond_money_only", ("bond", "money")),
                        ("no_bond_equity_mix", ("equity", "commodity", "convertible"))):
        mask = cls.isin(want)
        cols = [c for c in close.columns if mask[c]]
        if len(cols) < 20:
            print("skip", label, len(cols))
            continue
        sc = E.build_score(close[cols], amt[cols], feats)
        ser, contrib_s, turn_s, _ = run_with_attribution(
            close[cols], openp[cols], amt[cols], sc, cls)
        add(label, ser, {"turnover": round(turn_s, 2), "n_cols": len(cols)})
        # the matching benchmark: equal weight of the same sleeve
        add(label + "_ew_bench", ew_universe(close, amt, cls, want))

    # 3) gross P&L split on the ALL run
    df = pd.DataFrame([{"date": d, "total": t, "cost": c,
                        **{("r_" + k): v for k, v in rc.items()}}
                       for d, t, rc, c in contrib]).set_index("date")
    tot_gross = df[[c for c in df.columns if c.startswith("r_")]].sum(axis=0)
    out["attribution"] = {
        "gross_cum_log_by_class": {k.replace("r_", ""): round(float(v), 4)
                                   for k, v in tot_gross.items()},
        "gross_share_pct": {k.replace("r_", ""): round(float(v / tot_gross.sum() * 100), 1)
                            for k, v in tot_gross.items()} if tot_gross.sum() else {},
        "cost_drag_cum": round(float(df["cost"].sum()), 4),
        "bars": int(len(df)),
    }
    print("attribution", json.dumps(out["attribution"], ensure_ascii=False), flush=True)

    # 4) holdings mix over time: how often was the book fully defensive?
    mx = pd.DataFrame(mixes)
    for c in CLASSES:
        if c not in mx:
            mx[c] = 0.0
    defensive = (mx["equity"] <= 1e-9) & (mx["commodity"] <= 1e-9) & (mx["convertible"] <= 1e-9)
    out["book_shape"] = {
        "n_rebalances": int(len(mx)),
        "fully_defensive_pct": round(float(defensive.mean() * 100), 1),
        "avg_equity_weight": round(float(mx["equity"].mean()), 3),
        "avg_bond_money_weight": round(float((mx["bond"] + mx["money"]).mean()), 3),
        "avg_commodity_weight": round(float(mx["commodity"].mean()), 3),
    }
    print("book shape", json.dumps(out["book_shape"], ensure_ascii=False), flush=True)

    # 5) yearly split of the all-class book, for the honest "which years were carry" line
    yr = ser_all.groupby(ser_all.index.year).apply(lambda s: round(s.iloc[-1] / s.iloc[0] - 1, 4))
    out["yearly_all"] = {int(k): float(v) for k, v in yr.items()}
    # per-year gross contribution by class
    per_year = {}
    for y, g in df.groupby(df.index.year):
        per_year[int(y)] = {k.replace("r_", ""): round(float(g[k].sum()), 4)
                            for k in g.columns if k.startswith("r_")}
    out["yearly_gross_by_class"] = per_year
    print("yearly all", out["yearly_all"], flush=True)
    print("yearly gross by class", json.dumps(per_year, ensure_ascii=False), flush=True)

    p = os.path.join(PATHS.results_dir, "etf_equity_alpha.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


if __name__ == "__main__":
    main()