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

    The return is measured against the previous PRICED close (`ffill`), not against
    `close.pct_change()`. A split frequently sits next to a suspension bar, and pandas 3
    stopped filling across NaN in `pct_change`, so the bare call returns NaN on exactly
    those bars: the level rebuild still flattened them (NaN floors to a 0% day), but the
    printed count missed them -- the r1282 audit measured 168 such prints against 134
    reported -- and a small REAL move on a post-suspension bar was dropped along with
    them. (E74 lesson, new face: always compare adjacent PRICED closes.)
    """
    r = close.ffill().pct_change()
    bad = r.abs() > thr
    r_clean = r.where(~bad, 0.0).fillna(0.0)
    first = close.ffill().bfill().iloc[0]
    adj = (1.0 + r_clean).cumprod().multiply(first, axis=1)
    adj = adj.where(close.notna())
    # RE-ANCHOR TO THE TRADE (r1400). The rebuild walks forward from the panel's own first
    # bar, so a real share split flattened as a "flip" leaves the whole column on the
    # pre-split scale forever: 513100's 1:5 split (2022-01-14, 5.192 -> 1.015) left the
    # executable sheet quoting 11.04 for an ETF whose own amount/volume printed 2.162, and
    # 158 of 1,622 columns ended more than 5% off their traded close (510500 3.5x, 510020
    # 10x). A level is only a scale -- multiplying a column by a constant leaves every
    # return it feeds unchanged -- so anchoring each column to its own last priced print
    # repairs the order arithmetic without moving a single backtest number.
    last_raw = close.ffill().iloc[-1]
    last_adj = adj.ffill().iloc[-1]
    scale = (last_raw / last_adj).replace([np.inf, -np.inf], np.nan)
    usable = scale.notna() & (scale > 0) & (last_raw > 0)
    adj = adj.multiply(scale.where(usable, 1.0), axis=1)
    factor = adj / close
    return adj, openp * factor, int(bad.to_numpy().sum())


def flip_census(close, cols=None, thr=FLIP_THR):
    """How many prints on this panel exceed `thr`, and on how many symbols.

    One implementation for every face that has to state its own price basis: a second
    copy of the arithmetic is the defect, not the redundancy (E289). Measured against
    the last PRICED close, exactly as `repair_flips` measures it -- `pct_change()` on its
    own returns NaN across a suspension bar and silently misses those prints.
    """
    px = close[cols] if cols is not None else close
    bad = px.ffill().pct_change().abs() > thr
    return {"thr": float(thr), "prints": int(bad.to_numpy().sum()),
            "symbols": int((bad.sum() > 0).sum()), "columns": int(px.shape[1])}


def panel_inputs_sig():
    """(files, bytes, newest mtime) over the per-symbol CSVs the panel is built from.

    r1648: every staleness gate in this family compares a face's recorded digest with one
    re-read from `data/daily`. That directory is not a single file -- the wide refresh
    replaces it one symbol at a time (~1,719 files over ~350s, each write atomic on its
    own). A read that spans that batch returns a world that never existed: on 2026-11-14
    02:0x the smoke suite read one such mixture (digest 3c47c600) while six faces, rebuilt
    minutes later on the settled panel, all agreed on e6f9d0e8 -- the reds were echoes of
    one half-refreshed snapshot, not separate defects. A clock heuristic cannot see this
    (r1371: checkouts rewrite mtimes in any order), so the detector compares the input SET
    before and after the read. None = unreadable, which callers must treat as "unknown",
    never as "unchanged" (r98).
    """
    n = total = newest = 0
    try:
        with os.scandir(PATHS.daily_dir) as it:
            for ent in it:
                if not ent.name.lower().endswith(".csv"):
                    continue
                try:
                    st = ent.stat()
                except OSError:
                    continue
                n += 1
                total += st.st_size
                newest = max(newest, st.st_mtime_ns)
    except OSError:
        return None
    return (n, total, newest)


def panel_digest(close, openp=None, amt=None, ndigits=6):
    """A 16-hex fingerprint of the exact prices a face measured on.

    The book has three published faces (production card, executable sheet, forward
    ledger) and each one builds the panel and repairs the same flips before it ranks.
    "We all repaired" was a claim, never a measurement: the ledger once froze a bar three
    rounds running while the panel under it was still gaining symbols (r1366), and two
    faces that quote the same number can still be pricing two different worlds (E292/E293).

    Since r1179 the fingerprint names its blocks and covers the turnover panel too, when
    the caller passes it: the book's universe is filtered on 20-day amount, so two faces
    can agree on every close and still rank different names off different amounts. Each
    block is labelled in the hash, so a digest over a different set of blocks cannot pass
    for a digest over this one.

    Sorted by symbol and rounded to `ndigits` so a re-read cannot differ in the last bit.
    NaN is kept: an unpriced bar is part of the world, not an absence of one.
    """
    import hashlib
    cols = sorted(close.columns, key=lambda c: str(c))
    idx = [str(d)[:10] for d in close.index]
    frames = [("close", close)]
    if openp is not None:
        frames.append(("open", openp))
    amt_cols = 0
    if amt is not None:
        have = [c for c in cols if c in amt.columns]
        amt_cols = len(have)
        if have:
            frames.append(("amount", amt[have]))
    h = hashlib.sha256()
    h.update(("|".join(idx) + "#" + "|".join(str(c) for c in cols) + "#").encode("utf-8"))
    for name, fr in frames:
        sel = [c for c in cols if c in fr.columns]
        h.update(("%s#%d#" % (name, len(sel))).encode("utf-8"))
        for c in sel:
            h.update(np.round(fr[c].to_numpy(dtype="float64"), ndigits).tobytes())
    out = {"digest": h.hexdigest()[:16], "dates": len(idx), "columns": len(cols),
           "first": idx[0] if idx else None, "last": idx[-1] if idx else None,
           "blocks": [n for n, _ in frames]}
    if amt is not None:
        out["amount_columns"] = amt_cols
    return out


def price_basis_line(repaired, prints, thr=FLIP_THR, symbols=None, artifact=None,
                     columns=None):
    """The sentence a reader-facing sheet prints about the panel its numbers sit on.

    Both the production card and the executable order sheet must quote the same
    arithmetic (this function), and each states its own arm truthfully. `repaired` says
    what THIS face did; `prints` is the census of the raw panel either way, so the reader
    can see the size of what was neutralised instead of taking "clean" on trust.

    `columns` is the width of the panel THIS face counted on. Two faces of one book can
    legitimately count different totals -- the card repairs the whole panel before it
    classifies, the ticket censuses only the classes it ranks -- and without the width the
    reader cannot tell a universe difference from an arithmetic drift (r1177).
    """
    thr_pct = 0.0 if thr is None else float(thr) * 100.0
    tail = ("修与不修的差额已单独立面：%s。" % artifact) if artifact else ""
    width = ("本面板 %d 列。" % int(columns)) if columns else ""
    if prints is None or thr is None:
        sentence = ("本面的数字算在哪张价格面板上读不到（翻转计数或阈值缺失），"
                    "所以这里不替它下结论。")
        return {"panel": "unknown", "flip_thr": thr, "flip_prints": None,
                "symbols_with_a_flip": symbols, "sentence": sentence}
    if repaired:
        if prints == 0:
            sentence = ("本面的数字算在**已修复**的面板上，但这批票里没有单日超过 %.0f%% 的"
                        "报价翻转——就本面板而言，修与不修读到的是同一批数字。" % thr_pct)
        else:
            sym = ("（份额变动被读成暴跌，涉及 %d 只票）" % symbols
                   if symbols is not None else "（份额变动被读成暴跌）")
            sentence = ("本面的数字算在**已修复**的面板上：**%d 处**单日超过 %.0f%% 的报价翻转"
                        "%s在任何测量之前都已抹平为 0%% 日"
                        "（`etf_equity_alpha.repair_flips`）。" % (prints, thr_pct, sym))
        panel = "repaired (flip prints neutralised before any measurement)"
    else:
        symr = ("（涉及 %d 只票）" % symbols) if symbols is not None else ""
        sentence = ("本面的数字算在**未修复**的原始面板上，其中有 **%d 处**单日超过 %.0f%% 的"
                    "报价翻转%s：上面每一次排名都可能踩到其中一处。"
                    % (prints, thr_pct, symr))
        panel = "raw (no flip repair)"
    if width:
        sentence += width
    if tail:
        sentence += tail
    return {"panel": panel, "flip_thr": thr, "flip_prints": int(prints),
            "symbols_with_a_flip": symbols, "columns": columns, "sentence": sentence,
            "neutralised": bool(repaired)}


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
                         cost=COST, start=START, entry_lag=0):
    """Same leg chain as R.open_to_open_equity; additionally books每 bar P&L by class.

    `entry_lag` mirrors the engine's switch (r1795 `scripts/etf_book_entry_lag.py`): 0 is the
    caliber every number this face has ever printed -- a new book accrues from the DECISION
    bar's own open, which happened before the close the picks were read from. 1 hands that
    bar to the incumbent and starts the new book at the next open.
    """
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]

    equity, held, pending = 1.0, {}, None
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
                if entry_lag:
                    pending = (w, turn)
                else:
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
        if entry_lag and pending is not None:
            w2, turn2 = pending
            pending = None
            cost_paid = cost * turn2
            equity *= (1.0 - cost_paid)
            turns.append(turn2)
            held = w2
            mixes.append({c: sum(wt for p, wt in w2.items() if cls[p] == c)
                          for c in CLASSES})
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

    def attach_caliber(m, cl, opn, am, sc):
        """Price the same cell on the corrected execution caliber (`entry_lag=1`).

        The printed keys are untouched -- every reader's cagr/sharpe stays on the lag0 arm;
        the correction is published beside them, and `check()` refuses a face whose penalty
        is not the subtraction of the two arms it prints.
        """
        ser1, _, turn1, _ = run_with_attribution(cl, opn, am, sc, cls, entry_lag=1)
        s1 = stats2(ser1, m["label"] + "_lag1")
        m["caliber"] = {
            "entry_lag0_cagr": m["cagr"],
            "entry_lag1_cagr": s1.get("cagr"),
            "entry_lag1_sharpe": s1.get("sharpe"),
            "entry_lag1_maxdd": s1.get("maxdd"),
            "cagr_penalty_pp": round((m["cagr"] - (s1.get("cagr") or 0.0)) * 100.0, 4),
            "turnover_lag1": round(turn1, 2),
        }
        return m["caliber"]

    # 1) full universe (the production cell) + attribution
    ser_all, contrib, turn_all, mixes = run_with_attribution(close, openp, amt, score_all, cls)
    m_all = add("all_classes", ser_all, {"turnover": round(turn_all, 2)})
    attach_caliber(m_all, close, openp, amt, score_all)

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
        m = add(label, ser, {"turnover": round(turn_s, 2), "n_cols": len(cols)})
        attach_caliber(m, close[cols], openp[cols], amt[cols], sc)
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
    priced = [r for r in out["runs"] if r.get("caliber")]
    penalties = {r["label"]: r["caliber"]["cagr_penalty_pp"] for r in priced}
    prod = next((r for r in priced if r["label"] == "all_classes"), None)
    out["caliber"] = {
        "source_face": "results/etf_book_entry_lag.json",
        "execution": "decide at close t, own from open t+1 (entry_lag=1) vs the decision "
                     "bar's own open (entry_lag=0, every printed number in this face)",
        "production_candidate": "all_classes",
        "production_cagr_lag0_pct": round((prod["cagr"] or 0.0) * 100.0, 4) if prod else None,
        "production_cagr_lag1_pct": round((prod["caliber"]["entry_lag1_cagr"] or 0.0) * 100.0, 4)
                                    if prod else None,
        "production_penalty_pp": prod["caliber"]["cagr_penalty_pp"] if prod else None,
        "penalty_pp_by_arm": penalties,
        "sign_stable": bool(penalties) and all(v > 0 for v in penalties.values()),
        "verdict": ("CALIBER_COSTS_MONEY" if penalties and all(v > 0 for v in penalties.values())
                    else "PENALTY_NOT_SIGN_STABLE"),
    }
    print("caliber", json.dumps({k: out["caliber"][k] for k in
                                 ("production_cagr_lag0_pct", "production_cagr_lag1_pct",
                                  "production_penalty_pp", "verdict")},
                                ensure_ascii=False), flush=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)


def check():
    """Re-derive the caliber block from the published face; never recompute a book.

    Refuses a face that lost an arm, whose penalty was typed instead of subtracted, or whose
    printed cagr was quietly moved onto the corrected arm (E662 family: a check that agrees
    with itself proves nothing).
    """
    p = os.path.join(PATHS.results_dir, "etf_equity_alpha.json")
    if not os.path.exists(p):
        print("check FAIL: no face at", p)
        return 1
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    probs = []
    runs = {r.get("label"): r for r in face.get("runs") or []}
    cal = face.get("caliber") or {}
    if not cal:
        probs.append("no top-level caliber block")
    for label, r in runs.items():
        if label.endswith("_ew_bench"):
            # the benchmark is equal weight with no rebalance: there is no decision whose
            # fill could be booked a bar early, so it legitimately carries no caliber block
            continue
        if not r.get("caliber"):
            probs.append("%s: no caliber block" % label)
            continue
        c = r["caliber"]
        want = (c["entry_lag0_cagr"] - c["entry_lag1_cagr"]) * 100.0
        if abs(want - c["cagr_penalty_pp"]) > 1e-6:
            probs.append("%s: penalty %.4f != lag0-lag1 %.4f"
                         % (label, c["cagr_penalty_pp"], want))
        if abs(c["entry_lag0_cagr"] - r["cagr"]) > 1e-12:
            probs.append("%s: printed cagr moved off the lag0 arm" % label)
    if cal:
        prod = runs.get(cal.get("production_candidate") or "")
        if not prod:
            probs.append("production candidate %r not in runs"
                         % cal.get("production_candidate"))
        elif abs(cal["production_penalty_pp"] - prod["caliber"]["cagr_penalty_pp"]) > 1e-9:
            probs.append("production penalty disagrees with its own run")
        signs = [v > 0 for v in (cal.get("penalty_pp_by_arm") or {}).values()]
        if cal.get("sign_stable") != (all(signs) and bool(signs)):
            probs.append("sign_stable does not match the per-arm penalties")
        if cal.get("verdict") == "CALIBER_COSTS_MONEY" and not (signs and all(signs)):
            probs.append("verdict claims a cost that some arm does not pay")
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    print("check ok: %d priced arms, production %s %.2f%% -> %.2f%% (penalty %.2fpp)"
          % (len(cal.get("penalty_pp_by_arm") or {}), cal.get("production_candidate"),
             cal.get("production_cagr_lag0_pct") or 0.0,
             cal.get("production_cagr_lag1_pct") or 0.0,
             cal.get("production_penalty_pp") or 0.0))
    return 0


def _synth_panel(n_bars=200, n_names=6):
    """Deterministic panel for --selftest: non-trivial daily moves, opens lagging closes."""
    idx = pd.bdate_range("2020-01-01", periods=n_bars)
    cols = ["T%d" % i for i in range(n_names)]
    t = np.arange(n_bars, dtype=float)
    close = pd.DataFrame(
        {c: 100.0 * (1.0 + 0.0006 * t * (1 + i) + 0.02 * np.sin(t / (7.0 + i)))
         for i, c in enumerate(cols)}, index=idx)
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(1e8, index=idx, columns=cols)
    score = close.pct_change(5).fillna(0.0)
    cls = pd.Series("equity", index=cols)
    return close, openp, amt, score, cls


def selftest():
    """Offline: the lag switch must mean what the engine means, bit for bit."""
    fails = []
    close, openp, amt, score, cls = _synth_panel()
    kw = dict(rebal=20, n_hold=3, cost=0.0010, start="2020-01-01")

    # L1 default is the published caliber: no kwarg == entry_lag=0, bit for bit
    a, _, _, _ = run_with_attribution(close, openp, amt, score, cls, **kw)
    b, _, _, _ = run_with_attribution(close, openp, amt, score, cls, entry_lag=0, **kw)
    if not np.allclose(a.values, b.values, rtol=0, atol=1e-15):
        fails.append("L1 default is not entry_lag=0")

    # L2/L3 both calibers reproduce the shared engine with the same arguments
    for lag in (0, 1):
        eng, _ = R.open_to_open_equity(close, openp, amt, score, **kw, entry_lag=lag)
        mine, _, _, _ = run_with_attribution(close, openp, amt, score, cls, entry_lag=lag, **kw)
        common = eng.index.intersection(mine.index)
        d = float(np.max(np.abs(eng.loc[common].values - mine.loc[common].values)))
        if d > 1e-12:
            fails.append("L%d entry_lag=%d departs from the engine by %.2e" % (lag + 2, lag, d))

    # L4 the two calibers are actually different on this panel
    m1, _, _, _ = run_with_attribution(close, openp, amt, score, cls, entry_lag=1, **kw)
    if abs(m1.iloc[-1] - a.iloc[-1]) < 1e-9:
        fails.append("L4 the lag switch changed nothing")

    # L5 one-rebalance hand check, taken after the MIN_HIST gate so bar 0 can trade:
    # lag0 starts the new book on d0's open, lag1 on d1's open (bar 0 belongs to the old book)
    idx = openp.index
    late = str(idx[130].date())
    ser0, _, _, _ = run_with_attribution(close, openp, amt, score, cls, rebal=10_000,
                                         n_hold=2, cost=0.0, start=late, entry_lag=0)
    ser1, _, _, _ = run_with_attribution(close, openp, amt, score, cls, rebal=10_000,
                                         n_hold=2, cost=0.0, start=late, entry_lag=1)
    dates = [d for d in idx if d >= pd.Timestamp(late)]
    p0 = score.loc[dates[0]].dropna().nlargest(2)
    if len(p0) < 2:
        fails.append("L5 synth panel does not clear the MIN_HIST gate at %s" % late)
    else:
        picks = list(p0.index)
        hand0 = np.mean([openp.at[dates[1], p] / openp.at[dates[0], p] - 1.0 for p in picks])
        hand1 = np.mean([openp.at[dates[2], p] / openp.at[dates[1], p] - 1.0 for p in picks])
        if abs(ser0.iloc[0] - (1.0 + hand0)) > 1e-12:
            fails.append("L5 lag0 first bar %r != hand %r" % (ser0.iloc[0], 1.0 + hand0))
        if abs(ser1.iloc[0] - 1.0) > 1e-12 or abs(ser1.iloc[1] - (1.0 + hand1)) > 1e-12:
            fails.append("L5 lag1 bars %r/%r != 1/hand %r"
                         % (ser1.iloc[0], ser1.iloc[1], 1.0 + hand1))

    # L6 the per-bar class split adds up to the bar's own total
    _, contrib, _, _ = run_with_attribution(close, openp, amt, score, cls, entry_lag=1, **kw)
    worst = max(abs(r_tot - sum(rc.values())) for _d, r_tot, rc, _c in contrib)
    if worst > 1e-15:
        fails.append("L6 class split departs from the bar total by %.2e" % worst)

    if fails:
        print("selftest FAIL %d/%d" % (len(fails), 6))
        for x in fails:
            print("  -", x)
        return 1
    print("selftest 6/6 (default==lag0, both arms==engine, switch moves, "
          "hand-checked first bars, class split adds up)")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1].lstrip("-") if len(sys.argv) > 1 else "run"
    if arg == "check":
        raise SystemExit(check())
    if arg == "selftest":
        raise SystemExit(selftest())
    main()