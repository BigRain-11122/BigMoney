"""Which names carried which calendar year of the book the desk holds?

r1421 answered what the frozen top-2-years line measures (annual Sharpe wearing a
concentration costume) and found the one statistic that does discriminate: C2 = top-2
|years| / sum |years|, which puts the three ETF books at the 96.9-99.0th percentile of
their own null while the A-share books sit near the median. That reading says the
concentration lives in the MAGNITUDES -- 2025 is a large share of everything that
moved -- but no face says which names produced those magnitudes. "The book had a big
year" and "one bet had a big year" need opposite repairs and, until now, printed the
same number.

This file walks the SAME state machine as etf_robust_pf.open_to_open_equity (one loop
copied, and the copy is verified against the engine by a bit-identity leg) and books
each bar's log return into (year, name) and (year, asset class) buckets, with toll kept
on its own line:

    bar log return  = log1p(sum_c w_c * (open_next/open - 1))   split by contribution
    decision bar   += -log1p(1 - cost * turnover)               named 'toll'

so per calendar year: sum over names + toll == log(last/first within that year) EXACTLY,
and summing the years reproduces the book's log growth. A split that does not add up to
the headline is an attribution of some other book, so the identity is a selftest leg and
a --check against the published receipt.

Two arms, because a number with no yardstick is not a reading (E214/E238 family):
production (nobond_vt08 -- the adopted config, 8% vol target) and base_book (the same
selection at full size, no overlay). The gap between them is the overlay's doing, not
the selection's.

Scope discipline: zero prereg, zero judged face, zero network, zero engine edit, no
production change. L1 deterministic -- a rerun moves only the artifact's own timestamp.

  python scripts/etf_book_year_attribution.py run
  python scripts/etf_book_year_attribution.py --selftest
  python scripts/etf_book_year_attribution.py --check
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_year_attribution.json")
REBAL, N_HOLD, COST, VOL_TARGET = 20, 5, 0.0010, 0.08
TOL = 1e-9
FLAT_EPS = 1e-6   # log points (~1e-4 pp): below this a year has no signed share at all


def _book_vol(op, rets, book, upto, vol_window):
    """Byte-for-byte the engine's helper (same window, same weight order, same cov)."""
    if not book:
        return np.nan
    window = rets.loc[:upto].tail(vol_window)[list(book)]
    if window.shape[0] < 20:
        return np.nan
    w = np.array([book[k] for k in window.columns])
    cov = window.cov().to_numpy()
    return float(np.sqrt(w @ cov @ w) * np.sqrt(252))


def walk(close, openp, amt, score, cls, rebal=REBAL, n_hold=N_HOLD, cost=COST,
         vol_target=VOL_TARGET, start=R.START, vol_window=60, vol_cap=1.0,
         vol_floor=0.0):
    """Reproduce the engine's book and split every bar's log return by name.

    Returns (log_curve, buckets). `log_curve` is the running log equity (its last value
    is log(final level)); `buckets[(year, key)]` accumulates log points, where key is a
    name or 'toll'. A selftest leg asserts the curve equals the engine's own series.
    """
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    rets = op.pct_change()
    equity, held = 1.0, {}
    buckets, curve = {}, []
    by_year = {}
    for i in range(len(dates) - 1):
        d = dates[i]
        toll = 0.0
        if i % rebal == 0:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                scale = 1.0
                if vol_target:
                    v = _book_vol(op, rets, w, d, vol_window)
                    if np.isfinite(v) and v > 0:
                        scale = float(max(vol_floor, min(vol_cap, vol_target / v)))
                w = {k: v * scale for k, v in w.items()}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0))
                           for k in set(w) | set(held))
                toll = cost * turn
                if toll:
                    equity *= (1.0 - toll)
                held = w
                by_year.setdefault(str(d.year), []).append(scale)
        nxt = dates[i + 1]
        if toll:
            # the toll is charged on the step d -> nxt, so it belongs to the year the
            # step lands in; booking it to d.year splits one step across two years and
            # the year rows stop adding up (caught by the identity leg).
            y = str(nxt.year)
            buckets[(y, "toll")] = buckets.get((y, "toll"), 0.0) + np.log1p(-toll)
        contrib, r = {}, 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                c = wt * (b / a - 1.0)
                contrib[p] = c
                r += c
        if r != 0.0:
            bar = np.log1p(r)
            y = str(nxt.year)
            for p, c in contrib.items():
                buckets[(y, p)] = buckets.get((y, p), 0.0) + bar * (c / r)
        equity *= (1.0 + r)
        curve.append((nxt, equity))
    ser = pd.Series(dict(curve)).sort_index()
    return ser, buckets, by_year


def summarise(ser, buckets, by_year, cls, label):
    """Turn buckets into a per-year picture that adds up to the published year rows.

    YEAR BASE (a口径, printed not hidden): a calendar year's return here runs from the
    LEVEL AT THE LAST BAR OF THE PREVIOUS YEAR (1.0 before the book starts) to the level
    at its own last bar. etf_book_year_gate.yearly_returns uses last/first WITHIN the
    year, which silently drops the entering bar of every year -- the two definitions
    differ by that one bar, and only this one can be re-added from the buckets.
    """
    log_curve = np.log(ser.astype(float))
    years = {}
    prev_last = 0.0
    blocks = list(log_curve.groupby(log_curve.index.year))
    for year, blk in blocks:
        y = str(year)
        rows = {k[1]: v for k, v in buckets.items() if k[0] == y}
        total = float(sum(rows.values()))
        last = float(blk.iloc[-1])
        year_log = last - prev_last
        prev_last = last
        sleeves, names = {}, {}
        for nm, v in rows.items():
            if nm == "toll":
                continue
            k = cls.get(nm, "unclassified")
            sleeves[k] = sleeves.get(k, 0.0) + v
            names[nm] = v
        top = sorted(((n, v) for n, v in names.items()), key=lambda kv: -abs(kv[1]))[:3]
        # HHI on ABSOLUTE contributions: a signed denominator explodes when a year's net
        # is near zero (2022 prints 3.06 and 2026 prints 2.42 on the raw definition) --
        # the same defect r1421 found in the top-2 C1 statistic, so shares are quoted on
        # |contributions| and the signed share_of_year is published only when it means
        # something (a year whose log total is positive).
        abs_sum = float(sum(abs(v) for v in names.values()))
        hhi = round(float(sum((abs(v) / abs_sum) ** 2 for v in names.values())), 4) \
            if abs_sum > 0 else None
        scales = by_year.get(y, [])
        years[y] = {
            "log_pp": round(total * 100.0, 4),
            "net_pct": round((np.expm1(year_log)) * 100.0, 3),
            "identity_gap_pp": round((total - year_log) * 100.0, 6),
            "toll_pp": round(rows.get("toll", 0.0) * 100.0, 4),
            "sleeves": {k: round(v * 100.0, 4) for k, v in
                        sorted(sleeves.items(), key=lambda kv: -abs(kv[1]))},
            "top_names": [{"name": n, "log_pp": round(v * 100.0, 3),
                           "share_of_year": (round(v / total, 4)
                                             if total > FLAT_EPS else None),
                           "abs_share": (round(abs(v) / abs_sum, 4)
                                         if abs_sum > 0 else None)}
                          for n, v in top],
            "herfindahl_names": hhi,
            "herfindahl_basis": "absolute (sum of |name log points| = 1)",
            "avg_scale": round(float(np.mean(scales)), 3) if scales else None,
            "decisions": len(scales),
        }
    growth = float(ser.iloc[-1]) / float(ser.iloc[0])
    return {"book": label, "log_growth_pp": round(float(np.log(growth)) * 100.0, 4),
            "years": years}


def _fixture(seed=7, n_bars=320, n_names=8):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-02", periods=n_bars)
    cols = ["s%02d" % i for i in range(n_names)]
    ret = rng.normal(0.0003, 0.006, size=(n_bars, n_names))
    px = np.cumprod(1.0 + ret, axis=0) * 10.0
    close = pd.DataFrame(px, index=idx, columns=cols)
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    feats = pd.DataFrame({"a": rng.normal(size=n_bars),
                          "b": rng.normal(size=n_bars)}, index=idx)
    score = pd.DataFrame(rng.normal(size=(n_bars, n_names)), index=idx, columns=cols)
    cls = {c: "equity" for c in cols}
    return close, openp, amt, score, cls


def _legs():
    out = []

    def leg(name, fn):
        try:
            detail = fn()
            out.append((name, True, detail))
        except AssertionError as exc:
            out.append((name, False, str(exc)))

    close, openp, amt, score, cls = _fixture()

    def l_identity_engine():
        ser, _, _ = walk(close, openp, amt, score, cls)
        ref, _ = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                       vol_target=VOL_TARGET)
        gap = float(np.max(np.abs(ser.to_numpy() - ref.reindex(ser.index).to_numpy())))
        assert gap == 0.0, "replica drifts from the engine by %r" % gap
        return "max|diff| %.1e" % gap
    leg("replica reproduces the engine bit for bit", l_identity_engine)

    def l_split_sums():
        ser, buckets, by_year = walk(close, openp, amt, score, cls)
        total = float(sum(buckets.values()))
        want = float(np.log(ser.iloc[-1]))
        assert abs(total - want) < 1e-9, "buckets %r vs log equity %r" % (total, want)
        years = {}
        for (y, _k), v in buckets.items():
            years[y] = years.get(y, 0.0) + v
        lc = np.log(ser.astype(float))
        prev_last = 0.0
        for y, blk in lc.groupby(lc.index.year):
            got = years.get(str(y), 0.0)
            last = float(blk.iloc[-1])
            want = last - prev_last
            prev_last = last
            assert abs(got - want) < 1e-9, "year %s: %r vs %r" % (y, got, want)
        return "%d buckets, %d years" % (len(buckets), len(years))
    leg("the split adds up to the headline, overall and per year", l_split_sums)

    def l_single_mover():
        c2, o2, a2, s2, k2 = _fixture(seed=11)
        rets = pd.DataFrame(0.0, index=c2.index, columns=c2.columns)
        rets.iloc[10:, 0] = 0.001
        px = np.cumprod(1.0 + rets.to_numpy(), axis=0) * 10.0
        c2 = pd.DataFrame(px, index=c2.index, columns=c2.columns)
        o2 = c2.shift(1).bfill()
        ser, buckets, by_year = walk(c2, o2, a2, s2, k2, vol_target=None, cost=0.0)
        names = {k[1]: v for k, v in buckets.items() if k[1] != "toll"}
        moved = names.get("s00", 0.0)
        rest = sum(v for k, v in names.items() if k != "s00")
        assert abs(rest) < 1e-12, "a name that never moved was credited %r" % rest
        assert moved != 0.0, "the moving name got nothing"
        return "only-mover credited %.4fpp, others 0" % (moved * 100.0)
    leg("attribution credits the mover and only the mover", l_single_mover)

    def l_toll_line():
        ser, buckets, _ = walk(close, openp, amt, score, cls, cost=0.0)
        toll = sum(v for (y, k), v in buckets.items() if k == "toll")
        assert abs(toll) < 1e-15, "zero cost still charged toll %r" % toll
        ser2, buckets2, _ = walk(close, openp, amt, score, cls)
        toll2 = sum(v for (y, k), v in buckets2.items() if k == "toll")
        assert toll2 < 0.0, "toll should be negative log points, got %r" % toll2
        c3, o3, a3, s3, k3 = _fixture(seed=13, n_bars=150)
        ser3, buckets3, _ = walk(c3, o3, a3, s3, k3)
        assert len(ser3) > 0, "a short panel produced no curve"
        assert sum(v for (_y, kk), v in buckets3.items() if kk != "toll") != 0.0, \
            "a 150-bar panel credited nothing to any name"
        return "toll %.2fpp over the fixture" % (toll2 * 100.0)
    leg("toll is its own line and vanishes at zero cost", l_toll_line)

    def l_no_fabricated_year():
        ser, buckets, by_year = walk(close, openp, amt, score, cls)
        empty = [y for y in by_year if not any(k[0] == y for k in buckets)]
        assert not empty, "years with decisions but no buckets: %r" % empty
        return "no empty-year buckets"
    leg("every year with a decision carries its buckets", l_no_fabricated_year)

    def l_flat_year_no_signed_share():
        # two names that cancel: the year's log total is near zero, so a signed share is
        # undefined (r1421's C1 lesson) -- /total would print 8.4 and -7.4, and an HHI on
        # the signed denominator explodes. Absolute shares must stay a distribution.
        c4, o4, a4, s4, k4 = _fixture(seed=17, n_bars=260, n_names=2)
        rets = pd.DataFrame(0.0, index=c4.index, columns=c4.columns)
        rets.iloc[130:, 0] = 0.002
        rets.iloc[130:, 1] = -0.002
        px = np.cumprod(1.0 + rets.to_numpy(), axis=0) * 10.0
        c4 = pd.DataFrame(px, index=c4.index, columns=c4.columns)
        o4 = c4.shift(1).bfill()
        s4 = pd.DataFrame(1.0, index=c4.index, columns=c4.columns)
        ser, buckets, by_year = walk(c4, o4, a4, s4, k4, n_hold=2, vol_target=None, cost=0.0)
        arm = summarise(ser, buckets, by_year, k4, "flat")
        for y, row in arm["years"].items():
            if abs(row["log_pp"]) < 5.0:
                for t in row["top_names"]:
                    assert t["share_of_year"] is None, "signed share %r on a flat year %s" % (
                        t["share_of_year"], y)
            if row["herfindahl_names"] is not None:
                assert 0.0 <= row["herfindahl_names"] <= 1.0, "HHI %r outside [0,1] on %s" % (
                    row["herfindahl_names"], y)
        return "flat years publish absolute shares only"
    leg("a flat year never publishes a signed share or an exploded HHI",
        l_flat_year_no_signed_share)

    return out


def cross_check(arms):
    """Same-口径 rows of the published yearly gate, and how far this face stands from them.

    etf_book_year_gate reads each year last/first WITHIN the year; this face reads it from
    the previous year's last level. The two differ by the entering bar of every year, and
    that difference is printed here instead of being left for a reader to trip over.
    """
    path = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
    if not os.path.exists(path):
        return {"available": False, "note": "yearly gate receipt absent; nothing to check"}
    with open(path, encoding="utf-8") as fh:
        gate = json.load(fh)
    published = {b["book"]: b.get("yearly_returns_pct") or {} for b in gate.get("books", [])}
    out = {"available": True, "source": "results/etf_book_year_gate/YEAR-GATE.json",
           "definition_gap": "this face includes the entering bar of each year; the gate "
                             "starts at the year's own first bar",
           "rows": [], "max_abs_diff_pp": 0.0}
    for arm in arms:
        pub = published.get(arm["book"])
        if pub is None:
            out["rows"].append({"book": arm["book"], "note": "not published by the gate"})
            continue
        for y, row in arm["years"].items():
            want = pub.get(y)
            if want is None:
                continue
            diff = round(row["net_pct"] - float(want), 4)
            out["rows"].append({"book": arm["book"], "year": y,
                                "here_pct": row["net_pct"], "gate_pct": round(float(want), 4),
                                "diff_pp": diff})
            out["max_abs_diff_pp"] = max(out["max_abs_diff_pp"], abs(diff))
    return out


def run():
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls_all = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls_all[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    cls = {c: cls_all[c] for c in cols}

    arms = []
    ident = []
    for label, vt in (("nobond_vt08_adopted", VOL_TARGET), ("nobond_base", None)):
        ser, buckets, by_year = walk(close[cols], openp[cols], amt[cols], sc, cls,
                                     vol_target=vt)
        ref, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                          REBAL, N_HOLD, COST, vol_target=vt)
        gap = float(np.max(np.abs(ser.to_numpy() - ref.reindex(ser.index).to_numpy())))
        ident.append({"book": label, "max_abs_gap_vs_engine": gap,
                      "turnover_per_side": round(turn, 4)})
        assert gap == 0.0, "%s replica drifts %.3e" % (label, gap)
        arms.append(summarise(ser, buckets, by_year, cls, label))

    cross = cross_check(arms)
    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(close.index[-1].date()),
        "what": "calendar-year (and name/asset-class) attribution of the adopted book and "
                "its un-overlaid twin, split off the engine's own state machine",
        "config": {"rebal": REBAL, "n_hold": N_HOLD, "cost_per_side": COST,
                   "vol_target": VOL_TARGET, "start": R.START,
                   "classes_in_book": sorted(set(cls.values()))},
        "identity": ident,
        "arms": arms,
        "cross_check_vs_year_gate": cross,
        "reading_note": "log_pp are log points; sleeves + toll equal the year's log "
                        "return exactly (identity_gap_pp). A year whose top name carries "
                        "most of it is a bet, not a book.",
        "elapsed_sec": round(time.time() - t0, 2),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    for arm in arms:
        y25 = arm["years"].get("2025", {})
        top = (y25.get("top_names") or [{}])[0]
        print("%s: log growth %.2fpp | 2025 top name %s %.2fpp (share %s) | HHI %s"
              % (arm["book"], arm["log_growth_pp"], top.get("name"), top.get("log_pp", 0.0),
                 top.get("share_of_year"), y25.get("herfindahl_names")))
    print("wrote", OUT)
    return 0


def check():
    """Re-derive the identity from the published receipt's own rows."""
    with open(OUT, encoding="utf-8") as fh:
        doc = json.load(fh)
    bad = []
    for arm in doc["arms"]:
        for y, row in arm["years"].items():
            parts = sum(row["sleeves"].values()) + row["toll_pp"]
            if abs(parts - row["log_pp"]) > 1e-3:
                bad.append("%s %s sleeves+toll %.4f != %s" % (arm["book"], y, parts,
                                                             row["log_pp"]))
            if row["identity_gap_pp"] and abs(row["identity_gap_pp"]) > 1e-3:
                bad.append("%s %s identity gap %s" % (arm["book"], y,
                                                      row["identity_gap_pp"]))
    for row in doc["identity"]:
        if row["max_abs_gap_vs_engine"] != 0.0:
            bad.append("%s replica gap %r" % (row["book"],
                                              row["max_abs_gap_vs_engine"]))
    cross = doc.get("cross_check_vs_year_gate") or {}
    if cross.get("available") and cross.get("max_abs_diff_pp", 0.0) > 5.0:
        bad.append("口径 drift vs published gate: %.4fpp" % cross["max_abs_diff_pp"])
    if bad:
        print("FAIL", *bad, sep="\n ")
        return 1
    print("PASS: %d arms, every year's sleeves+toll re-adds to its own log row"
          % len(doc["arms"]))
    return 0


def selftest():
    legs = _legs()
    for name, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + name + " -- " + detail)
    print("%d/%d" % (sum(1 for _n, ok, _d in legs if ok), len(legs)))
    return 0 if all(ok for _n, ok, _d in legs) else 1


if __name__ == "__main__":
    arg = (sys.argv[1] if len(sys.argv) > 1 else "run").lstrip("-")
    if arg in ("selftest", "self-test"):
        sys.exit(selftest())
    if arg == "check":
        sys.exit(check())
    sys.exit(run())