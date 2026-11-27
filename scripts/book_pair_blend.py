#!/usr/bin/env python
"""book_pair_blend -- two books, one wallet.

The company now runs two capital books with published numbers:

  cb  = the dual-low convertible-bond book  (scripts/cb_dual_low.py)
        published main cell: N20 / R20 / 10bp per side, close-to-close, 1-bar lag
  etf = the bond-free ETF composite book     (scripts/etf_nobond_vt.py)
        production arm: nobond_vt08, 8% vol target, open-to-open, entry_lag=1

Each of those faces answers "is this book worth following on its own".  Neither
answers the reader's next question: *I have one wallet -- does splitting it
across both books beat putting it all in the better one?*

This face answers only that.  It never re-derives a strategy: it imports each
book's own backtest and reads its daily equity series.  If a parent changes, this
face is stale, and check() says so in the chain's contract words.

Two things it refuses to hide:
  * the two books overlap for 6.9 of cb's 19.4 years -- every blend number is on
    the overlap window only, and each parent's full-history number is printed
    beside it so the reader sees the difference;
  * the two books do not trade at the same price: cb fills at the close of the
    bar after the signal, etf at the open (lag1 arm).  The caliber line says it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FACE = os.path.join(RESULTS, "book_pair_blend.json")
MD = os.path.join(RESULTS, "book_pair_blend.md")


def _rp(rel):
    """Resolve a repo-relative path, so the face lands in the repo, not in cwd."""
    return os.path.join(ROOT, rel)

# Blend weights expressed as the cb book's share of the wallet.
WEIGHTS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

# One annualisation clock for the blend rows.  Each parent's own number is
# reproduced with its own clock (244 for cb, 252 for etf) so the reconciliation
# legs compare like with like; the blend is quoted on 244 because the wallet is
# an A-share calendar wallet.
ANN_DAYS = 244.0


# ---------------------------------------------------------------- parents
def load_cb():
    """The published main cell of the dual-low convertible book."""
    import cb_dual_low as C

    panel = C._load_panel()
    m, eq, dt = C._backtest(panel, n_hold=20, rebal=20, cost_bp=10.0)
    ser = _series(eq, dt)
    return ser, {
        "face": "results/cb_dual_low.json",
        "arm": "n_hold=20 rebal=20 cost=10bp phase=0",
        "execution": "signal at close t, filled at close t+1",
        "full_history": {"cagr": m["cagr"], "sharpe": m["sharpe"],
                         "maxdd": m["maxdd"], "vol": m["vol"],
                         "bars": m["bars"], "first": m["first_bar"],
                         "last": m["last_bar"],
                         "annual_turnover": m["annual_turnover"]},
        "panel": _stamp(_rp("data/cb_panel.csv.gz")),
    }


def load_etf():
    """The published production arm of the bond-free ETF book (entry_lag=1)."""
    import etf_composite_pf as E
    import etf_robust_pf as R
    import etf_equity_alpha as A

    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                      20, 5, 0.0010, vol_target=0.08, entry_lag=1)
    st = A.stats2(ser, "nobond_vt08_lag1")
    return ser, {
        "face": "results/etf_nobond_vt.json",
        "arm": "nobond_vt08 vol_target=8% n_hold=5 rebal=20 cost=10bp entry_lag=1",
        "execution": "decide at close t, own from the open of t+1",
        "full_history": {"cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
                         "maxdd": st.get("maxdd"), "vol": st.get("vol"),
                         "bars": int(len(ser)),
                         "first": str(ser.index[0].date()),
                         "last": str(ser.index[-1].date()),
                         "turnover": round(float(turn), 2)},
        "universe": len(cols), "flips_repaired": int(n_flip),
        "panel": _stamp(_rp("data/daily/510300.csv")),
    }


def _series(eq, dt):
    import pandas as pd

    idx = pd.to_datetime([str(d) for d in dt])
    return pd.Series([float(x) for x in eq], index=idx).dropna()


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size),
            "mtime": _iso(st.st_mtime)}


def _iso(ts):
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


# ---------------------------------------------------------------- statistics
def local_stats(ser, ann=ANN_DAYS, rf=0.0, base=None):
    """Growth against the slice's own first level (the stats2 fix), one clock.

    base=1.0 is used for series this face builds itself (a cumprod that already
    starts at 1.0): normalising those against their own first element would drop
    the first day's return and quietly lift the CAGR by 0.13pp over six years.
    """
    import numpy as np

    ser = ser.dropna()
    if len(ser) < 40:
        return {"note": "short", "bars": int(len(ser))}
    yrs = (ser.index[-1] - ser.index[0]).days / 365.25
    start = float(ser.iloc[0]) if base is None else float(base)
    growth = float(ser.iloc[-1]) / start
    cagr = growth ** (1.0 / yrs) - 1.0 if yrs > 0.1 else float("nan")
    r = ser.pct_change().dropna()
    sd = float(r.std(ddof=1))
    sharpe = ((float(r.mean()) - rf / ann) / sd * math.sqrt(ann)) if sd > 0 else float("nan")
    dd = ser / ser.cummax() - 1.0
    yearly = {}
    for y, g in ser.groupby(ser.index.year):
        if len(g) >= 2:
            yearly[int(y)] = float(g.iloc[-1] / g.iloc[0] - 1.0)
    monthly = ser.resample("ME").last().pct_change().dropna()
    return {
        "bars": int(len(ser)), "years": round(yrs, 3),
        "cagr": float(cagr), "sharpe": float(sharpe),
        "maxdd": float(dd.min()), "vol": float(sd * math.sqrt(ann)),
        "first": str(ser.index[0].date()), "last": str(ser.index[-1].date()),
        "yearly": yearly,
        "worst_year": (min(yearly.values()) if yearly else None),
        "best_year": (max(yearly.values()) if yearly else None),
        "neg_years": sum(1 for v in yearly.values() if v < 0),
        "months": int(len(monthly)),
        "pos_months_pct": (float((monthly > 0).mean()) if len(monthly) else None),
    }


def align(a, b):
    """Keep only the days both books have a level for."""
    import pandas as pd

    idx = a.index.intersection(b.index)
    idx = idx.sort_values()
    if len(idx) < 2:
        return None, None, idx
    return a.reindex(idx), b.reindex(idx), idx


def blend_daily(ra, rb, w):
    """Daily returns, w on book a.  Cost stays inside each parent's series."""
    import pandas as pd

    r = w * ra + (1.0 - w) * rb
    return (1.0 + r).cumprod()


def corr_report(a, b):
    import numpy as np

    ra = a.pct_change().dropna()
    rb = b.pct_change().dropna()
    idx = ra.index.intersection(rb.index)
    ra, rb = ra.reindex(idx), rb.reindex(idx)
    daily = float(np.corrcoef(ra.values, rb.values)[0, 1]) if len(idx) > 3 else float("nan")
    ma = a.resample("ME").last().pct_change().dropna()
    mb = b.resample("ME").last().pct_change().dropna()
    mi = ma.index.intersection(mb.index)
    monthly = (float(np.corrcoef(ma.reindex(mi).values, mb.reindex(mi).values)[0, 1])
               if len(mi) > 3 else float("nan"))
    both_down = int(((ma.reindex(mi) < 0) & (mb.reindex(mi) < 0)).sum())
    return {
        "daily": round(daily, 4), "monthly": round(monthly, 4),
        "n_days": int(len(idx)), "n_months": int(len(mi)),
        "months_both_down": both_down,
        "months_both_down_pct": (round(both_down / len(mi), 4) if len(mi) else None),
    }


def verdict_of(blend_best, sr_a, sr_b):
    """Which story the table tells -- named, not implied.

    The band edges are explicit because a blend of a book with itself has a gain
    of exactly 0.0, and that is not a paid diversification.
    """
    best_parent = max(sr_a, sr_b)
    worst_parent = min(sr_a, sr_b)
    gain = blend_best["sharpe"] - best_parent
    if gain > 0.005:
        return "DIVERSIFICATION_PAYS", round(gain, 4)
    if gain > 1e-9:
        return "DIVERSIFICATION_PAYS_A_LITTLE", round(gain, 4)
    if blend_best["sharpe"] >= worst_parent - 1e-9:
        return "NO_FREE_LUNCH", round(gain, 4)
    return "BLENDING_HURTS", round(gain, 4)


def _published_refs():
    """What each parent's own face publishes, so a reader sees this face reproduce it.

    If the two disagree the reader is told which number came from where -- this
    face never silently replaces a parent's published figure with its own rerun.
    """
    out = {}
    try:
        with open(_rp("results/cb_dual_low.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        cell = None
        for row in d.get("grid", []):
            if (row.get("n_hold") == 20 and row.get("rebal") == 20
                    and float(row.get("cost_bp") or 0) == 10.0 and row.get("phase", 0) == 0):
                cell = row
                break
        if cell is None and d.get("grid"):
            cell = d["grid"][0]
        out["cb"] = {"face": "results/cb_dual_low.json", "arm": "grid cell N20/R20/10bp",
                     "cagr": (cell or {}).get("cagr"),
                     "sharpe": (cell or {}).get("sharpe"),
                     "maxdd": (cell or {}).get("maxdd")}
    except Exception as exc:  # a missing parent is disclosed, never invented
        out["cb"] = {"face": "results/cb_dual_low.json", "missing": str(exc)}
    try:
        with open(_rp("results/etf_nobond_vt.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        arm = next((r for r in d.get("runs", []) if r.get("label") == "nobond_vt08"), {})
        cal = arm.get("caliber", {})
        out["etf"] = {"face": "results/etf_nobond_vt.json", "arm": "nobond_vt08 lag1",
                      "cagr": cal.get("entry_lag1_cagr"),
                      "sharpe": cal.get("entry_lag1_sharpe"),
                      "maxdd": cal.get("entry_lag1_maxdd")}
    except Exception as exc:
        out["etf"] = {"face": "results/etf_nobond_vt.json", "missing": str(exc)}
    return out


def _diff_pp(mine, theirs):
    if mine is None or theirs is None:
        return None
    try:
        return round((float(mine) - float(theirs)) * 100.0, 4)
    except Exception:
        return None


# ---------------------------------------------------------------- the face
def build(write=True, quiet=False):
    import numpy as np

    cb, cb_meta = load_cb()
    etf, etf_meta = load_etf()

    cb_w, etf_w, idx = align(cb, etf)
    if cb_w is None:
        raise SystemExit("the two books share no days -- refusing to print a blend")

    cb_in = local_stats(cb_w)
    etf_in = local_stats(etf_w)
    rc = cb_w.pct_change().dropna()
    re = etf_w.pct_change().dropna()

    rows = []
    for w in WEIGHTS:
        ser = blend_daily(rc, re, w)
        st = local_stats(ser, base=1.0)
        st.update({"w_cb": round(w, 2), "w_etf": round(1.0 - w, 2),
                   "annual_turnover": round(
                       w * (cb_meta["full_history"]["annual_turnover"] or 0.0)
                       + (1.0 - w) * (etf_meta["full_history"]["turnover"] or 0.0), 3)})
        rows.append(st)

    blend_best = max(rows, key=lambda r: r["sharpe"])
    verdict, gain = verdict_of(blend_best, cb_in["sharpe"], etf_in["sharpe"])
    cr = corr_report(cb_w, etf_w)

    pub = _published_refs()
    for key, mine in (("cb", cb_meta), ("etf", etf_meta)):
        p = pub.get(key, {})
        p["reproduced_here"] = {"cagr": mine["full_history"].get("cagr"),
                                "sharpe": mine["full_history"].get("sharpe"),
                                "maxdd": mine["full_history"].get("maxdd")}
        p["diff_pp"] = {"cagr": _diff_pp(mine["full_history"].get("cagr"), p.get("cagr")),
                        "sharpe": _diff_pp(mine["full_history"].get("sharpe"), p.get("sharpe")),
                        "maxdd": _diff_pp(mine["full_history"].get("maxdd"), p.get("maxdd"))}
    # the blend rows carry the parent's full-history reproduction; keep both on one face
    w0, w1 = rows[0], rows[-1]

    live = _live_split(cb_meta, etf_meta)
    # The blend's own one-lot floor: the convertible sleeve is w_cb of the wallet,
    # so the wallet must be at least the cb book's floor / w_cb to hold both books.
    floor = None
    olf = (live.get("cb") or {}).get("one_lot_floor_cny")
    if olf and blend_best["w_cb"] > 0:
        floor = {
            "cb_one_lot_floor_cny": olf,
            "w_cb": blend_best["w_cb"],
            "min_wallet_cny": round(float(olf) / blend_best["w_cb"], 0),
            "sentence": f"a {blend_best['w_cb']*100:.0f}% convertible sleeve needs the wallet to "
                        f"be at least {float(olf)/blend_best['w_cb']:,.0f} CNY before the "
                        f"twenty-name book fits in it at all",
        }
    else:
        floor = {"note": "the cb one-lot floor is not on its face right now, so the blend's "
                         "own floor cannot be stated (not printed as zero)"}

    face = {
        "face": "book_pair_blend",
        "generated_at": _now_iso(),
        "evidence_cutoff": str(idx[-1].date()),
        "question": "one wallet, two books: does splitting beat picking the better one?",
        "window": {
            "first": str(idx[0].date()), "last": str(idx[-1].date()),
            "bars": int(len(idx)),
            "why": "the overlap only -- cb runs since 2007, etf since 2020; a blend cannot "
                   "be priced on days one of the books does not exist",
            "cb_full_history_years": cb_meta["full_history"].get("years")
            or round((cb.index[-1] - cb.index[0]).days / 365.25, 3),
            "note_on_overlap_bias": "the overlap is the recent six years; cb's full-history "
                                    "CAGR is printed beside it, not blended with it",
        },
        "caliber": {
            "cb": cb_meta["execution"], "etf": etf_meta["execution"],
            "same_cost_floor": "each parent already pays its own 10bp per side; the blend "
                               "adds no rebalancing cost between books (not modelled -- a "
                               "reader who moves money between them pays it)",
            "ann_days": ANN_DAYS,
            "overlap_assets": "the etf book keeps a convertible sleeve, so a few convertible "
                              "ETFs sit in both wallets -- the correlation is not independent "
                              "by construction and is not claimed to be",
        },
        "parents": {
            "cb": {**cb_meta, "in_window": cb_in, "published": pub["cb"]},
            "etf": {**etf_meta, "in_window": etf_in, "published": pub["etf"]},
        },
        "correlation": cr,
        "blends": rows,
        "best": {
            "w_cb": blend_best["w_cb"],
            "cagr": blend_best["cagr"], "sharpe": blend_best["sharpe"],
            "maxdd": blend_best["maxdd"], "vol": blend_best["vol"],
            "worst_year": blend_best["worst_year"],
        },
        "reconciliation": {
            "why": "the two edge weights must land on the two parents measured on this same "
                   "window -- if they do not, this face is not blending the published books",
            "w1_cagr": w1["cagr"], "cb_in_window_cagr": cb_in["cagr"],
            "w1_matches_cb": abs(w1["cagr"] - cb_in["cagr"]) < 5e-4,
            "w0_cagr": w0["cagr"], "etf_in_window_cagr": etf_in["cagr"],
            "w0_matches_etf": abs(w0["cagr"] - etf_in["cagr"]) < 5e-4,
        },
        "verdict": {
            "word": verdict,
            "sharpe_gain_vs_best_parent": gain,
            "sentence": _sentence(verdict, blend_best, cb_in, etf_in, cr, gain),
        },
        "live": live,
        "executable_floor": floor,
        "unverified": [
            "no rebalancing cost between the two wallets is modelled",
            "the overlap window is 6.9 of cb's 19.4 years -- a blend is a recent-years claim",
            "the best weight is chosen on the same window it is scored on (in-sample pick): a "
            "reader who adopts it should expect less than the printed gain",
            "each parent's own unverified list still applies (survivorship in the etf pool, "
            "the cb book's close-fill assumption, its 2026 drawdown being one regime)",
        ],
    }

    if write:
        os.makedirs(RESULTS, exist_ok=True)
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(_plain(face), fh, ensure_ascii=False, indent=1)
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(_md(face))
    if not quiet:
        print(f"[run] window {face['window']['first']} -> {face['window']['last']} "
              f"({len(idx)} bars)", flush=True)
        for r in rows:
            print(f"  w_cb={r['w_cb']:.1f} CAGR {r['cagr']*100:6.2f}% "
                  f"SR {r['sharpe']:.3f} MDD {r['maxdd']*100:7.1f}% "
                  f"vol {r['vol']*100:5.2f}%", flush=True)
        print(f"  corr daily {cr['daily']} monthly {cr['monthly']} "
              f"both-down months {cr['months_both_down']}/{cr['n_months']}", flush=True)
        print(f"  VERDICT {verdict} (best w_cb={blend_best['w_cb']:.1f}, "
              f"SR gain {gain:+.3f} vs best single book)", flush=True)
    return face


def _sentence(word, best, cb_in, etf_in, cr, gain):
    lead = {
        "DIVERSIFICATION_PAYS": "Splitting the wallet beats either book on its own",
        "DIVERSIFICATION_PAYS_A_LITTLE": "Splitting the wallet edges out the best single book",
        "NO_FREE_LUNCH": "Splitting the wallet does not beat the better book",
        "BLENDING_HURTS": "Splitting the wallet is worse than both books",
    }[word]
    wy = best.get("worst_year")
    wy_s = f"{wy*100:.1f}%" if isinstance(wy, (int, float)) else "n/a"
    bd = cr.get("months_both_down_pct")
    bd_s = f"{bd*100:.0f}%" if isinstance(bd, (int, float)) else "n/a"
    return (f"{lead}: {best['w_cb']*100:.0f}% convertible / "
            f"{(1-best['w_cb'])*100:.0f}% ETF gives Sharpe {best['sharpe']:.3f} "
            f"(vs {cb_in['sharpe']:.3f} and {etf_in['sharpe']:.3f}), "
            f"worst year {wy_s}, max drawdown "
            f"{best['maxdd']*100:.1f}%; the two books move together on the daily tape "
            f"(corr {cr['daily']}) and go down in {bd_s} of "
            f"months together -- read the gain as {gain:+.2f} Sharpe, not as insurance")


def _live_split(cb_meta, etf_meta):
    """What the split would hold today, read from each book's own live face."""
    out = {"note": "read from each book's published live picks; this face does not "
                   "re-derive holdings"}
    for key, path in (("cb", "results/cb_book_ticket_floor.json"),
                      ("etf", "results/etf_nobond_vt.json")):
        try:
            with open(_rp(path), encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            out[key] = {"face": path, "missing": True}
            continue
        if key == "etf":
            out[key] = {"face": path, "as_of": d.get("live_picks", {}).get("as_of"),
                        "picks": [p.get("symbol") for p in
                                  d.get("live_picks", {}).get("picks", [])]}
        else:
            olf = d.get("one_lot_floor") if isinstance(d.get("one_lot_floor"), dict) else {}
            out[key] = {"face": path,
                        "bar": d.get("evidence_cutoff") or d.get("bar"),
                        "one_lot_floor_cny": olf.get("rung_cny"),
                        "clean_capital_cny": olf.get("clean_capital_cny"),
                        "why_it_matters": "a 30% convertible sleeve of a small wallet may be "
                                          "below one lot -- read this beside the weight"}
    return out


# ---------------------------------------------------------------- md
def _md(face):
    w, p = face["window"], face["parents"]
    L = []
    A = L.append
    A(f"# Two books, one wallet -- {face['evidence_cutoff']}\n")
    A(f"*generated {face['generated_at']} · window {w['first']} -> {w['last']} "
      f"({w['bars']} bars, the overlap of both books)*\n")
    A(f"**{face['verdict']['word']}** -- {face['verdict']['sentence']}\n")
    A("## What each book does on its own\n")
    A("| book | arm | CAGR | Sharpe | max DD | vol | worst year | years |")
    A("|---|---|---|---|---|---|---|---|")
    for k, lbl in (("cb", "dual-low convertible"), ("etf", "bond-free ETF")):
        iw = p[k]["in_window"]
        A(f"| {lbl} | {p[k]['arm']} | {iw['cagr']*100:.2f}% | {iw['sharpe']:.3f} | "
          f"{iw['maxdd']*100:.1f}% | {iw['vol']*100:.2f}% | "
          f"{iw['worst_year']*100:.1f}% | {iw['years']} |")
    A("")
    A(f"Full-history, outside this window (printed so the overlap is not misread as the book): "
      f"cb {p['cb']['full_history']['cagr']*100:.2f}% / "
      f"SR {p['cb']['full_history']['sharpe']:.3f} over "
      f"{p['cb']['full_history']['first']}..{p['cb']['full_history']['last']}.\n")
    rec = face["reconciliation"]
    A(f"Reconciliation: the edge weights land on the parents read here "
      f"(w=0 -> {rec['w0_cagr']*100:.2f}% vs etf {rec['etf_in_window_cagr']*100:.2f}%, "
      f"{'match' if rec['w0_matches_etf'] else 'MISMATCH'}); "
      f"(w=1 -> {rec['w1_cagr']*100:.2f}% vs cb {rec['cb_in_window_cagr']*100:.2f}%, "
      f"{'match' if rec['w1_matches_cb'] else 'MISMATCH'}).\n")
    pub = p["cb"].get("published", {})
    if pub and not pub.get("missing"):
        d = pub.get("diff_pp", {})
        A(f"Parent reproduction (this face's rerun vs the parent's own published number, "
          f"pp): cb CAGR {d.get('cagr')} Sharpe {d.get('sharpe')} DD {d.get('maxdd')}; "
          f"etf CAGR {p['etf'].get('published', {}).get('diff_pp', {}).get('cagr')} "
          f"Sharpe {p['etf'].get('published', {}).get('diff_pp', {}).get('sharpe')}.\n")
    A("## Does splitting pay?\n")
    A("| convertible share | ETF share | CAGR | Sharpe | max DD | vol | worst year | turnover/yr |")
    A("|---|---|---|---|---|---|---|---|")
    for r in face["blends"]:
        star = " **" if r["w_cb"] == face["best"]["w_cb"] else ""
        A(f"|{r['w_cb']*100:5.0f}%{star} | {r['w_etf']*100:5.0f}% | {r['cagr']*100:.2f}% | "
          f"{r['sharpe']:.3f} | {r['maxdd']*100:.1f}% | {r['vol']*100:.2f}% | "
          f"{r['worst_year']*100:.1f}% | {r['annual_turnover']:.2f} |")
    A("")
    c = face["correlation"]
    A(f"Correlation: daily {c['daily']}, monthly {c['monthly']}; both books fall in "
      f"{c['months_both_down']} of {c['n_months']} months "
      f"({c['months_both_down_pct']*100:.0f}%).\n")
    A("## What it takes to hold this split\n")
    fl = face.get("executable_floor", {})
    if fl.get("min_wallet_cny"):
        A(f"- {fl['sentence']} (the cb book's own one-lot floor is "
          f"{fl['cb_one_lot_floor_cny']:,.0f} CNY for twenty names).")
    else:
        A(f"- {fl.get('note')}")
    lv = face.get("live", {})
    etf_lv = lv.get("etf", {})
    A(f"- Today's ETF picks ({etf_lv.get('as_of')}): "
      f"{', '.join(etf_lv.get('picks') or []) or 'face has no picks'}.")
    A("")
    A("## How to read it\n")
    A(f"- The window is the overlap only ({w['bars']} bars). A blend cannot be priced on days "
      f"one of the books does not exist, so this is a recent-years claim, not a 19-year one.")
    A(f"- Execution differs: {face['caliber']['cb']} vs {face['caliber']['etf']}.")
    A(f"- {face['caliber']['same_cost_floor']}.")
    A(f"- {face['caliber']['overlap_assets']}.")
    A("\n## Unverified\n")
    for u in face["unverified"]:
        A(f"- {u}")
    A("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- check
def check():
    """Cheap contract check: have the parents' bytes moved since this face was written?"""
    import datetime as _dt

    if not os.path.exists(FACE):
        print("STALE: book_pair_blend face missing (run `python scripts/book_pair_blend.py run`)")
        return 3
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    for k in ("cb", "etf"):
        rec = (face.get("parents", {}).get(k, {}) or {}).get("panel")
        if not rec or rec.get("missing"):
            problems.append(f"STALE: {k} panel is not on disk any more ({rec})")
            continue
        now = _stamp(rec["path"])
        if now.get("missing"):
            problems.append(f"STALE: {k} panel {rec['path']} disappeared")
            continue
        if now["size"] != rec["size"] or now["mtime"] != rec["mtime"]:
            problems.append(
                f"STALE: {k} panel bytes moved since this face was written "
                f"({rec['size']}B@{rec['mtime']} -> {now['size']}B@{now['mtime']})")
    if problems:
        for p in problems:
            print(p)
        return 3
    print(json.dumps({"ok": True, "problems": [], "window": face["window"]["last"],
                      "verdict": face["verdict"]["word"]}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    """Offline: the blend arithmetic must show the textbook, not promise it."""
    import numpy as np
    import pandas as pd

    legs, fails = 0, []

    def ok(name, cond, got=""):
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(f"{name}: {got}")

    idx = pd.bdate_range("2020-01-01", periods=600)
    rng = np.random.default_rng(7)

    def mk(mean, sd, seed=None):
        """Exact mean and sd -- a sampled series can miss its own Sharpe by 3se."""
        r = np.random.default_rng(seed) if seed is not None else rng
        x = r.normal(0.0, 1.0, len(idx))
        x = (x - x.mean()) / x.std(ddof=1)
        return pd.Series(mean + sd * x, index=idx)

    # two independent books with the SAME Sharpe: this is the textbook case
    ra = mk(0.00040, 0.0100, 11)
    rb = mk(0.00044, 0.0110, 12)
    A_ = (1 + ra).cumprod()
    B_ = (1 + rb).cumprod()

    st_a, st_b = local_stats(A_), local_stats(B_)
    ok("L1 stats run", "sharpe" in st_a, st_a)

    # independent books: a 50/50 blend must beat the better Sharpe (diversification)
    half = blend_daily(ra, rb, 0.5)
    st_h = local_stats(half)
    ok("L2 independent books blend beats the better Sharpe",
       st_h["sharpe"] > max(st_a["sharpe"], st_b["sharpe"]),
       f"{st_h['sharpe']:.3f} vs {max(st_a['sharpe'], st_b['sharpe']):.3f}")
    ok("L2b and its vol sits below both",
       st_h["vol"] < min(st_a["vol"], st_b["vol"]),
       f"{st_h['vol']:.4f} vs {min(st_a['vol'], st_b['vol']):.4f}")

    # the same book twice: blending buys nothing and must not be sold as a gain
    same = blend_daily(ra, ra, 0.5)
    st_s = local_stats(same)
    ok("L3 the same book twice = no gain",
       abs(st_s["sharpe"] - st_a["sharpe"]) < 1e-9, f"{st_s['sharpe']} vs {st_a['sharpe']}")
    ok("L3b verdict on identical books is NO_FREE_LUNCH",
       verdict_of(st_s, st_a["sharpe"], st_a["sharpe"])[0] == "NO_FREE_LUNCH",
       verdict_of(st_s, st_a["sharpe"], st_a["sharpe"]))

    # opposite books: a blend cancels the swing but also the return
    opp = blend_daily(ra, -ra, 0.5)
    ok("L4 opposite books blend to a flat line",
       abs(local_stats(opp)["vol"]) < 1e-12, local_stats(opp)["vol"])

    # edge weights must reproduce the parents exactly
    e0, e1 = blend_daily(ra, rb, 0.0), blend_daily(ra, rb, 1.0)
    ok("L5 w=0 reproduces the etf book", abs(e0.iloc[-1] - B_.iloc[-1]) < 1e-12,
       f"{e0.iloc[-1]} vs {B_.iloc[-1]}")
    ok("L5b w=1 reproduces the cb book", abs(e1.iloc[-1] - A_.iloc[-1]) < 1e-12,
       f"{e1.iloc[-1]} vs {A_.iloc[-1]}")

    # alignment must intersect, never invent days
    la = A_.iloc[:400]
    lb = B_.iloc[200:]
    xa, xb, ix = align(la, lb)
    ok("L6 align intersects both books", xa is not None and len(ix) == len(la.index[200:]),
       len(ix) if xa is not None else None)
    ok("L6b align refuses an empty overlap", align(A_.iloc[:10], B_.iloc[20:], )[0] is None,
       "returned a series")

    # correlation of a book with itself is 1, and the both-down counter is honest
    c1 = corr_report(A_, B_)
    ok("L7 correlation is in [-1,1]", -1.0 <= c1["daily"] <= 1.0, c1["daily"])
    c2 = corr_report(A_, A_)
    ok("L7b self-correlation is 1", abs(c2["daily"] - 1.0) < 1e-9, c2["daily"])

    # a deliberately hurtful pair: a losing book must drag the blend below the good book
    rl = mk(-0.0020, 0.0080, 13)
    L_ = (1 + rl).cumprod()
    st_l = local_stats(L_)
    worst_pair = blend_daily(rb, rl, 0.5)
    st_w = local_stats(worst_pair)
    ok("L8 a losing book drags the blend below the good book",
       st_w["sharpe"] < st_b["sharpe"],
       f"{st_w['sharpe']:.3f} vs {st_b['sharpe']:.3f}")
    ok("L8b and the verdict refuses to call that a gain",
       verdict_of(st_w, st_b["sharpe"], st_l["sharpe"])[0]
       in ("NO_FREE_LUNCH", "BLENDING_HURTS"),
       verdict_of(st_w, st_b["sharpe"], st_l["sharpe"]))

    # a short slice must be refused rather than annualised into nonsense
    ok("L9 a short slice is refused", local_stats(A_.iloc[:20]).get("note") == "short",
       local_stats(A_.iloc[:20]))

    # cost inside parents: a 10bp drag must lower the blended CAGR, not be silently dropped
    rc = ra - 0.0010
    C_ = (1 + rc).cumprod()
    st_c = local_stats(C_)
    ok("L10 costs inside a parent lower its CAGR",
       st_c["cagr"] < st_a["cagr"], f"{st_c['cagr']:.4f} vs {st_a['cagr']:.4f}")

    # L11: the contract word. check() is what the chain pays attention to (r1850):
    # a moved parent must be called STALE, and a matching one must not be.
    import contextlib
    import io
    import tempfile

    saved = globals().get("FACE")
    tmpdir = tempfile.mkdtemp()
    try:
        real = {"cb": _stamp(_rp("data/cb_panel.csv.gz")),
                "etf": _stamp(_rp("data/daily/510300.csv"))}
        good = os.path.join(tmpdir, "good.json")
        with open(good, "w", encoding="utf-8") as fh:
            json.dump({"parents": {k: {"panel": v} for k, v in real.items()},
                       "window": {"last": "x"}, "verdict": {"word": "X"}}, fh)
        globals()["FACE"] = good
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_good = check()
        ok("L11 matching parent stamps pass the check (and say ok, not STALE)",
           rc_good == 0 and "STALE" not in buf.getvalue(), buf.getvalue()[:120])

        moved = os.path.join(tmpdir, "moved.json")
        bad = {"parents": {k: {"panel": dict(v, size=v["size"] + 1)} for k, v in real.items()},
               "window": {"last": "x"}, "verdict": {"word": "X"}}
        with open(moved, "w", encoding="utf-8") as fh:
            json.dump(bad, fh)
        globals()["FACE"] = moved
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_moved = check()
        out = buf.getvalue()
        ok("L11b a moved parent is called STALE and exits 3",
           rc_moved == 3 and "STALE" in out, f"{rc_moved} {(out or '')[:120]}")

        absent = os.path.join(tmpdir, "none.json")
        globals()["FACE"] = absent
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_absent = check()
        ok("L11c a missing face says STALE + face missing",
           rc_absent == 3 and "STALE" in buf.getvalue() and "missing" in buf.getvalue(),
           buf.getvalue()[:140])
    finally:
        if saved is not None:
            globals()["FACE"] = saved

    print(f"selftest: {legs - len(fails)}/{legs} PASS")
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def _now_iso():
    import datetime as _dt

    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _plain(o):
    """JSON-safe, and byte-stable across reruns.

    Floats are rounded to 10 decimals: the reruns agree to ~1e-15 but not bit-for-bit
    (accumulation order in two different pandas paths), and a face that changes its
    last digit on every run cannot be byte-compared by the chain or by a reader.
    1e-10 is far below any number here that a reader would act on.
    """
    import numpy as np

    if isinstance(o, dict):
        return {str(k): _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return round(float(o), 10)
    if isinstance(o, float):
        return round(o, 10)
    return o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="re-derive and publish the face")
    sub.add_parser("check", help="cheap contract check against parent bytes")
    sub.add_parser("selftest", help="offline arithmetic legs")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "run":
        build(write=True)
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
