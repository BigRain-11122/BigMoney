"""Does the panel price-flip defect reach the production candidate's MONEY?

r2146 (`scripts/panel_price_flip_census.py`) found 4 ETF files whose prices sit at 1/10 of
the truth for 3-4 years (sz159901, sh511030, sh510580, sh510180), and that `repair_flips`
is implemented in exactly one script while ~500 scripts read the raw panel. That census
stopped at "confirmed hands": it never asked whether the defect changes a *decision*.

This face asks the money question on the one book we would actually pay for --
`nobond_vt08` (bond-free universe + 8% vol target, the production candidate) -- by
building the same panel twice, repaired vs as-traded, and printing five reach
measurements:

  1. universe : does the bond-free symbol set change?
  2. class    : does `classify` move a symbol between sleeves? (realised vol is a
                classifying input and a -90%/+900% pair inflates it, so this is the
                mechanism by which a price typo becomes a mandate change)
  3. picks    : on how many rebalance dates does a flip-carrying symbol enter the top-5,
                in each arm, and which names enter in one arm only?
  4. money    : cagr / sharpe / maxdd / worst year, repaired vs as-traded.
  5. book     : each arm's own worst day and yearly returns, so an exploded number is
                visible instead of being averaged away.

Verdicts: FLIP_REACHES_MONEY / FLIP_REACHES_MANDATE / FLIP_STAYS_IN_THE_DATA.

`check` re-derives every verdict from the published face (never recomputes a book) and
refuses a face whose verdict does not follow from its own numbers. `selftest` pins the
behaviours on synthetic panels: repair leaves no >35% day and keeps the traded tail,
realised vol really does explode, and a face that hides a gap under the clean verdict is
refused.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

IS_END = "2023-12-31"
FLIP_SYMBOLS = ("sz159901", "sh511030", "sh510580", "sh510180")
VT = 0.08
COST = 0.0010
RANK_DAYS = 20
HOLD = 5


def _no_repair(close, openp):
    return close, openp, 0


def _arm(close, openp, amt, feats, cmap, repair, flip_syms):
    fx = A.repair_flips if repair else _no_repair
    c2, o2, n_flip = fx(close, openp)
    cls = A.classify(c2.columns, cmap, c2)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in c2.columns if cls[c] in want]
    sc = E.build_score(c2[cols], amt[cols], feats)
    diag = []
    ser, turn = R.open_to_open_equity(c2[cols], o2[cols], amt[cols], sc, RANK_DAYS, HOLD, COST,
                                      vol_target=VT, diag=diag)
    m = A.stats2(ser, "nobond_vt08")
    m_is = A.stats2(ser[ser.index <= IS_END], "is")
    m_oos = A.stats2(ser[ser.index > IS_END], "oos")
    for k in ("cagr", "sharpe", "maxdd"):
        m[k + "_is"] = m_is.get(k)
        m[k + "_oos"] = m_oos.get(k)
    # ser is an EQUITY CURVE, not returns: every year/return read below goes through a
    # level ratio or a pct_change, never through (1+x) on the level itself (self-caught:
    # the first version compounded levels and printed a 3.7e76 "worst year").
    lvl = pd.Series(np.asarray(ser, dtype=float), index=pd.DatetimeIndex(ser.index))
    yr = {}
    for y, g in lvl.groupby(lvl.index.year):
        yr[int(y)] = round(float(g.iloc[-1] / g.iloc[0] - 1.0) * 100.0, 4)
    m["worst_year"] = int(min(yr, key=lambda y: yr[y])) if yr else None
    m["worst_year_pct"] = yr.get(m["worst_year"]) if yr else None
    m["years"] = len(yr)
    m["total_pct"] = round(float(lvl.iloc[-1] / lvl.iloc[0] - 1.0) * 100.0, 4)
    m["turnover"] = round(float(turn), 2)
    dret = lvl.pct_change().dropna()
    m["worst_day"] = {"date": str(pd.Timestamp(dret.idxmin()).date()),
                      "ret_pct": round(float(dret.min()) * 100.0, 4)}
    m["best_day"] = {"date": str(pd.Timestamp(dret.idxmax()).date()),
                     "ret_pct": round(float(dret.max()) * 100.0, 4)}
    # held-window flip exposure: walk the engine's own book list and price each window
    # off the arm's own opens, so a fake bar is named on the exact day the book ate it
    exposures = []
    for i in range(len(diag) - 1):
        w = diag[i]
        if w.get("rule") == "hook":
            continue
        d, nxt = pd.Timestamp(w["date"]), None
        # next diag date is the next rebalance; the engine's own windows are those dates
        nxt = pd.Timestamp(diag[i + 1]["date"])
        if nxt <= d:
            continue
        for p in w["book"]:
            if p not in o2.columns:
                continue
            a, b = o2.at[d, p], o2.at[nxt, p]
            if not (np.isfinite(a) and np.isfinite(b)) or a <= 0:
                continue
            rr = float(b / a - 1.0)
            if abs(rr) > A.FLIP_THR:
                exposures.append({"symbol": str(p), "from": str(d.date()), "to": str(nxt.date()),
                                  "ret_pct": round(rr * 100.0, 4)})
    picks_by_date = {}
    for d in sc.index[::RANK_DAYS]:
        row = sc.loc[d].dropna()
        if len(row) == 0:
            continue
        picks_by_date[str(pd.Timestamp(d).date())] = [str(x) for x in row.nlargest(5).index]
    flip_hits = {}
    for sym in flip_syms:
        flip_hits[sym] = (None if sym not in sc.columns
                          else sum(1 for v in picks_by_date.values() if sym in v))
    return {
        "flips_repaired": int(n_flip),
        "universe": sorted(str(c) for c in cols),
        "classes": {str(s): str(cls[s]) for s in c2.columns},
        "stats": m,
        "flip_top5_dates": flip_hits,
        "picks_by_date": picks_by_date,
        "yearly_pct": yr,
        "held_flip_exposures": exposures,
        "live_picks": [{"symbol": str(s), "score": round(float(v), 4)}
                       for s, v in sc.loc[sc.index[-1]].dropna().nlargest(5).items()],
    }


def run():
    close, openp, amt, feats = E.build_panel()
    cmap = A.load_class_map()
    # which columns actually carry a >35% day in the raw panel
    r = close.ffill().pct_change()
    bad = (r.abs() > A.FLIP_THR)
    bad_counts = {str(s): int(n) for s, n in bad.sum().items() if n > 0}
    rep = _arm(close.copy(), openp.copy(), amt, feats, cmap, True, FLIP_SYMBOLS)
    raw = _arm(close.copy(), openp.copy(), amt, feats, cmap, False, FLIP_SYMBOLS)

    u_rep, u_raw = set(rep["universe"]), set(raw["universe"])
    only_raw, only_rep = sorted(u_raw - u_rep), sorted(u_rep - u_raw)
    class_moves = sorted([s for s in (set(rep["classes"]) & set(raw["classes"]))
                          if rep["classes"][s] != raw["classes"][s]])

    def d(key):
        a, b = raw["stats"].get(key), rep["stats"].get(key)
        return None if a is None or b is None or not isinstance(a, (int, float)) \
            or not isinstance(b, (int, float)) else round(float(a) - float(b), 6)

    money = {
        "cagr_pp": round(d("cagr") * 100.0, 4),
        "sharpe": d("sharpe"),
        "maxdd_pp": round(d("maxdd") * 100.0, 4),
        "worst_year_pp": (None if d("worst_year_pct") is None
                          else round(d("worst_year_pct"), 4)),
    }
    # which names sit in the as-traded top-5 but never in the repaired top-5
    only_as_traded_picks = {}
    for day, picks in raw["picks_by_date"].items():
        other = set(rep["picks_by_date"].get(day) or [])
        for sym in picks:
            if sym not in other:
                only_as_traded_picks.setdefault(sym, {"dates": 0, "carries_flip": sym in bad_counts})
                only_as_traded_picks[sym]["dates"] += 1
    for sym in only_as_traded_picks:
        only_as_traded_picks[sym]["flips"] = bad_counts.get(sym, 0)
    flip_picked = {s: n for s, n in (raw["flip_top5_dates"] or {}).items() if n}
    any_pick = max([v for v in (raw["flip_top5_dates"] or {}).values() if v is not None] or [0])

    if abs(money["cagr_pp"] or 0.0) >= 0.5 or any_pick > 0 or raw["held_flip_exposures"]:
        verdict = "FLIP_REACHES_MONEY"
    elif class_moves or only_raw or only_rep:
        verdict = "FLIP_REACHES_MANDATE"
    else:
        verdict = "FLIP_STAYS_IN_THE_DATA"

    keep = ("flips_repaired", "stats", "flip_top5_dates", "yearly_pct",
            "held_flip_exposures", "live_picks")
    face = {
        "evidence_cutoff": str(close.index[-1].date()),
        "production_arm": ("nobond_vt08: vol_target=%.2f, rank %dd, hold %dd, %.0fbp/edge, "
                           "bond-free universe" % (VT, RANK_DAYS, HOLD, COST * 1e4)),
        "flip_symbols_named_by_r2146": list(FLIP_SYMBOLS),
        "panel_columns_with_a_flip": len(bad_counts),
        "panel_flip_bars": int(sum(bad_counts.values())),
        "repaired": dict({k: rep[k] for k in keep}, universe=len(rep["universe"])),
        "as_traded": dict({k: raw[k] for k in keep}, universe=len(raw["universe"])),
        "reach": {
            "universe_only_as_traded": only_raw,
            "universe_only_repaired": only_rep,
            "class_moves": class_moves,
            "class_move_count": len(class_moves),
            "flip_symbols_in_universe": {s: (s in u_raw) for s in FLIP_SYMBOLS},
            "flip_top5_dates_as_traded": raw["flip_top5_dates"],
            "max_flip_top5_dates": int(any_pick),
            "names_picked_only_as_traded": only_as_traded_picks,
            "held_flip_exposures_as_traded": raw["held_flip_exposures"],
            "held_flip_exposures_repaired": rep["held_flip_exposures"],
            "money_as_traded_minus_repaired": money,
        },
        "verdict": verdict,
        "verdict_rule": ("FLIP_REACHES_MONEY if |dcagr|>=0.5pp, or a flip symbol enters the "
                         "top-5, or the engine held a symbol across its own >35% bar; "
                         "else FLIP_REACHES_MANDATE if the universe or a sleeve class moves; "
                         "else FLIP_STAYS_IN_THE_DATA"),
    }
    p = os.path.join(E.PATHS.results_dir, "etf_book_flip_reach.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("verdict", verdict)
    print("panel flips", len(bad_counts), "columns", face["panel_flip_bars"], "bars")
    print("universe %d -> %d class_moves %d max_flip_top5 %d"
          % (face["repaired"]["universe"], face["as_traded"]["universe"], len(class_moves), any_pick))
    print("money", money)
    print("held flip exposures: as-traded %d / repaired %d"
          % (len(raw["held_flip_exposures"]), len(rep["held_flip_exposures"])))
    for e in raw["held_flip_exposures"][:10]:
        print("   ", e)
    print("saved", p)
    return 0


def _rederive(face):
    probs = []
    rep, raw = face.get("repaired") or {}, face.get("as_traded") or {}
    if not rep or not raw:
        return ["face has no repaired/as_traded pair"]
    reach = face.get("reach") or {}
    money = reach.get("money_as_traded_minus_repaired") or {}
    for k in ("cagr", "sharpe", "maxdd"):
        if k not in (rep.get("stats") or {}) or k not in (raw.get("stats") or {}):
            probs.append("stats missing %s" % k)
    if probs:
        return probs
    want_cagr = round((raw["stats"]["cagr"] - rep["stats"]["cagr"]) * 100.0, 4)
    if abs(want_cagr - float(money.get("cagr_pp", 1e18))) > 1e-6:
        probs.append("cagr_pp %.4f != raw-rep %.4f" % (money.get("cagr_pp", 0.0), want_cagr))
    want_sharpe = round(raw["stats"]["sharpe"] - rep["stats"]["sharpe"], 6)
    if abs(want_sharpe - float(money.get("sharpe", 1e18))) > 1e-9:
        probs.append("sharpe delta %.6f != raw-rep %.6f" % (money.get("sharpe", 0.0), want_sharpe))
    any_pick = int(reach.get("max_flip_top5_dates") or 0)
    table = reach.get("flip_top5_dates_as_traded") or {}
    want_pick = max([v for v in table.values() if isinstance(v, int)] or [0])
    if any_pick != want_pick:
        probs.append("max_flip_top5_dates %d != per-symbol max %d" % (any_pick, want_pick))
    expect = ("FLIP_REACHES_MONEY" if (abs(want_cagr) >= 0.5 or any_pick > 0
                                      or (reach.get("held_flip_exposures_as_traded") or []))
              else ("FLIP_REACHES_MANDATE" if (reach.get("class_moves")
                                               or reach.get("universe_only_as_traded")
                                               or reach.get("universe_only_repaired"))
                    else "FLIP_STAYS_IN_THE_DATA"))
    if face.get("verdict") != expect:
        probs.append("verdict %r does not follow: expected %r" % (face.get("verdict"), expect))
    return probs


def check():
    p = os.path.join(E.PATHS.results_dir, "etf_book_flip_reach.json")
    if not os.path.exists(p):
        print("check FAIL: no face at", p)
        return 1
    with open(p, encoding="utf-8") as f:
        face = json.load(f)
    probs = _rederive(face)
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    m = face["reach"]["money_as_traded_minus_repaired"]
    print("check ok: verdict=%s universe %s->%s class_moves=%s dcagr=%.4fpp dsharpe=%.4f max_flip_top5=%s"
          % (face["verdict"], face["repaired"]["universe"], face["as_traded"]["universe"],
             face["reach"]["class_move_count"], m["cagr_pp"], m["sharpe"],
             face["reach"]["max_flip_top5_dates"]))
    return 0


def _synth(n=400, bad_from=200):
    idx = pd.bdate_range("2020-01-01", periods=n)
    rng = np.random.default_rng(7)
    out = {}
    for sym, base in (("good", 3.0), ("bad", 2.0)):
        r = rng.normal(0.0002, 0.012, n)
        close = base * np.cumprod(1 + r)
        if sym == "bad":
            close[bad_from:] = close[bad_from:] / 10.0
        out[sym] = close
    return idx, out


def selftest():
    fails = []
    idx, raw = _synth()
    close = pd.DataFrame(raw, index=idx)
    openp = close.shift(1).bfill()
    c2, o2, n = A.repair_flips(close, openp)
    # leg 1: contract of repair_flips -- no >thr day left, and the column still ends on
    # its traded (raw) last print; it is history that gets rewritten, not the tail
    worst = float(c2["bad"].ffill().pct_change().abs().max())
    if worst > A.FLIP_THR + 1e-9:
        fails.append("leg1 repair left a %.3f day move (> %.2f)" % (worst, A.FLIP_THR))
    tail_ratio = float(c2["bad"].iloc[-1] / close["bad"].iloc[-1])
    if abs(tail_ratio - 1.0) > 1e-9:
        fails.append("leg1 repair moved the traded tail by %.6f" % tail_ratio)
    head_ratio = float(c2["bad"].iloc[0] / close["bad"].iloc[0])
    if not head_ratio < 0.5:
        fails.append("leg1 history was not rewritten onto the traded scale (head %g)" % head_ratio)
    if n < 1:
        fails.append("leg1 repair reported %d flips" % n)
    # leg 2: the damage really does explode realised vol -- the classifier's own input
    v_raw = float(close["bad"].pct_change().std())
    v_fix = float(c2["bad"].pct_change().std())
    if not (v_raw > 3 * v_fix):
        fails.append("leg2 vol_raw %g not >> vol_fixed %g" % (v_raw, v_fix))
    # leg 3: verdict ladder
    base = {"repaired": {"universe": 2, "stats": {"cagr": 0.10, "sharpe": 1.0, "maxdd": -0.1}},
            "as_traded": {"universe": 2, "stats": {"cagr": 0.10, "sharpe": 1.0, "maxdd": -0.1}},
            "reach": {"money_as_traded_minus_repaired": {"cagr_pp": 0.0, "sharpe": 0.0},
                      "flip_top5_dates_as_traded": {"x": 0}, "max_flip_top5_dates": 0,
                      "held_flip_exposures_as_traded": [], "held_flip_exposures_repaired": [],
                      "class_moves": [], "universe_only_as_traded": [],
                      "universe_only_repaired": []},
            "verdict": "FLIP_STAYS_IN_THE_DATA"}
    if _rederive(base):
        fails.append("leg3 clean face was refused: %s" % _rederive(base))
    moved = json.loads(json.dumps(base))
    moved["reach"]["class_moves"] = ["sh511030"]
    moved["verdict"] = "FLIP_REACHES_MANDATE"
    if _rederive(moved):
        fails.append("leg3b mandate face was refused: %s" % _rederive(moved))
    cash = json.loads(json.dumps(base))
    cash["as_traded"]["stats"]["cagr"] = 0.20
    cash["reach"]["money_as_traded_minus_repaired"]["cagr_pp"] = 10.0
    cash["verdict"] = "FLIP_REACHES_MONEY"
    if _rederive(cash):
        fails.append("leg3c money face was refused: %s" % _rederive(cash))
    # leg 4: hiding a 10pp gap under the clean verdict must be refused
    liar = json.loads(json.dumps(cash))
    liar["verdict"] = "FLIP_STAYS_IN_THE_DATA"
    if not _rederive(liar):
        fails.append("leg4 a face that hides a 10pp gap under the clean verdict passed")
    # leg 5: a typed (not subtracted) cagr delta must be refused
    typed = json.loads(json.dumps(base))
    typed["reach"]["money_as_traded_minus_repaired"]["cagr_pp"] = 1.0
    if not _rederive(typed):
        fails.append("leg5 a typed cagr_pp that no arm supports passed")
    if fails:
        print("selftest: FAIL")
        for x in fails:
            print("  -", x)
        return 1
    print("selftest: 5/5 PASS")
    return 0


if __name__ == "__main__":
    arg = (sys.argv[1].lstrip("-") if len(sys.argv) > 1 else "run")
    if arg == "selftest":
        raise SystemExit(selftest())
    if arg == "check":
        raise SystemExit(check())
    raise SystemExit(run())
