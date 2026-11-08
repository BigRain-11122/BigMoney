"""Does capping one sleeve in the bond-free book buy anything?

The 2026-11-08 next pointer ("per-sleeve commodity cap") asked a question the book has
never been able to answer: its sleeve mix is *emergent* (one cross-sleeve score, plain
top-5), so "the commodity sleeve carries 30% of the gross return" was never a knob --
it was an outcome. This run turns it into a knob with the engine's own `select_hook`
(the same hook the hysteresis buffer uses) and prices it:

    arm 0  plain top-5                       (identity leg: must reproduce nobond_vt08)
    arm 1  at most 1 commodity name in top-5
    arm 2  at most 2 commodity names in top-5
    arm 3  at most 1 commodity AND at most 1 convertible

Every arm runs on the same panel, the same score, the same 20-bar calendar, the same
8% vol target and the same 10bp/side cost. Nothing else changes, so the difference is
the cap and only the cap.

The identity leg is the point of the exercise: if arm 0 does not reproduce the
published nobond_vt08 numbers to 1e-9, the caps are measuring a different book and the
whole run is refused (rc=3, no file written). Run `--selftest` for the offline proofs.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_composite_pf as E  # noqa: E402
import etf_robust_pf as R  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

IS_END = "2023-12-31"
N_HOLD = 5
REBAL = 20
COST = 0.0010
VT = 0.08
TOL = 1e-9

# The published face is rounded before it is published (4 dp for returns, 3 dp for the
# Sharpe), so the identity leg is "same number at the precision the reader was given",
# not "same float". Half an ulp of the published rounding is the whole tolerance.
PUBLISHED_LABEL = "nobond_vt08"
PUBLISHED_ULP = {"cagr": 5e-5, "sharpe": 5e-4, "maxdd": 5e-5}


def load_published(results_dir):
    """Read the published arm from its own product file -- never a hand-copied constant.

    Returns the numbers *and* the panel window they were computed on: the panel keeps
    growing, so an identity leg that re-derives on today's panel is comparing two
    different books (2026-10-23 cutoff, 1499 names vs today). The window travels with
    the number.
    """
    p = os.path.join(results_dir, "etf_nobond_vt.json")
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    for r in d.get("runs", []):
        if r.get("label") == PUBLISHED_LABEL:
            nums = {k: r[k] for k in ("cagr", "sharpe", "maxdd")}
            return {"numbers": nums,
                    "as_of": (d.get("live_picks") or {}).get("as_of"),
                    "universe": d.get("universe")}
    raise KeyError("%s not in %s" % (PUBLISHED_LABEL, p))


def identity_deviation(measured, published):
    """|measured - published| per key; the leg passes when each is inside half an ulp."""
    return {k: abs(measured[k] - published[k]) for k in published}


def identity_ok(measured, published, ulp=None):
    ulp = ulp or PUBLISHED_ULP
    return all(v <= ulp[k] for k, v in identity_deviation(measured, published).items())


def capped_select(row, held_names, n_hold, d, cls, caps):
    """engine select_hook: score-ranked, at most `caps[class]` names per sleeve.

    The hook may only look at this bar's score row, which is what it does. When the
    caps leave fewer than n_hold eligible names the shortfall is filled by the plain
    score order -- a cap that silently shrinks the book would be a different experiment
    (cash is not free here: the sizing rule already owns leverage).
    """
    s = row.dropna()
    if s.empty:
        raise ValueError("empty score row at %s" % d)
    order = s.sort_values(ascending=False)
    picked = []
    used = {}
    for sym in order.index:
        if len(picked) == n_hold:
            break
        c = cls[sym]
        cap = caps.get(c)
        if cap is not None and used.get(c, 0) >= cap:
            continue
        picked.append(sym)
        used[c] = used.get(c, 0) + 1
    if len(picked) < n_hold:
        for sym in order.index:
            if len(picked) == n_hold:
                break
            if sym not in picked:
                picked.append(sym)
    if len(picked) != n_hold:
        raise ValueError("universe too small to fill %d at %s" % (n_hold, d))
    return picked


def run_arm(close, openp, amt, score, cls, caps, label, diag=None):
    hook = None
    if caps:
        hook = lambda row, held, n, d: capped_select(row, held, n, d, cls, caps)
    ser, turn = R.open_to_open_equity(
        close, openp, amt, score, REBAL, N_HOLD, COST, vol_target=VT,
        select_hook=hook, diag=diag)
    m = A.stats2(ser, label)
    m["label"] = label
    for lbl, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        mm = A.stats2(sl, label + "_" + lbl)
        for k in ("cagr", "sharpe", "maxdd"):
            m[k + "_" + lbl] = mm.get(k)
    m["turnover"] = round(turn, 2)
    m["caps"] = dict(caps) if caps else None
    return m, ser


def sleeve_share(ser_diag, cls):
    """Share of decision bars in which a sleeve held the most names."""
    out = {}
    n = 0
    for row in ser_diag:
        # the engine's diag rows call the selection "book"; older fixtures used "picks"
        picks = row.get("book") or row.get("picks") or []
        if not picks:
            continue
        n += 1
        counts = {}
        for sym in picks:
            c = cls.get(sym, "?")
            counts[c] = counts.get(c, 0) + 1
        top = max(counts.items(), key=lambda kv: kv[1])[0]
        out[top] = out.get(top, 0) + 1
    return {"bars": n, "top_sleeve_bars": out,
            "top_sleeve_share": {k: round(v / n, 3) for k, v in out.items()} if n else {}}


def _selftest():
    cls = {"A": "equity", "B": "equity", "C": "commodity", "D": "commodity",
           "E": "commodity", "F": "convertible", "G": "equity"}
    row = pd.Series({"A": 9.0, "B": 8.0, "C": 7.5, "D": 7.0, "E": 6.0,
                     "F": 5.5, "G": 5.0})
    # L1 plain order
    got = capped_select(row, [], 5, pd.Timestamp("2020-01-01"), cls, {})
    assert got == ["A", "B", "C", "D", "E"], got
    # L2 commodity cap 1 -> C skipped, D/E skipped, F and G pulled in
    got = capped_select(row, [], 5, pd.Timestamp("2020-01-01"), cls, {"commodity": 1})
    assert got == ["A", "B", "C", "F", "G"], got
    assert sum(1 for s in got if cls[s] == "commodity") == 1
    # L3 two caps stack
    got = capped_select(row, [], 5, pd.Timestamp("2020-01-01"), cls,
                        {"commodity": 1, "convertible": 1})
    assert got == ["A", "B", "C", "F", "G"], got
    # L4 shortfall is filled, never a short book
    cls2 = dict(cls)
    cls2["A"] = cls2["B"] = cls2["G"] = "commodity"
    got = capped_select(row, [], 5, pd.Timestamp("2020-01-01"), cls2, {"commodity": 1})
    assert len(got) == 5 and len(set(got)) == 5, got
    # L5 held_names is accepted and does not change a stateless rule
    a_ = capped_select(row, ["F"], 5, pd.Timestamp("2020-01-01"), cls, {})
    b_ = capped_select(row, [], 5, pd.Timestamp("2020-01-01"), cls, {})
    assert a_ == b_
    # L6 a too-small universe raises instead of returning a short book
    small = pd.Series({"C": 1.0, "D": 0.5})
    try:
        capped_select(small, [], 5, pd.Timestamp("2020-01-01"), cls, {})
    except ValueError:
        pass
    else:
        raise AssertionError("short book must raise")
    # L7 negative/NaN scores are dropped, not ranked last silently
    row2 = pd.Series({"A": np.nan, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.5, "F": 0.4, "G": 0.3})
    got = capped_select(row2, [], 5, pd.Timestamp("2020-01-01"), cls, {})
    assert "A" not in got, got
    # L8 sleeve_share counts the majority sleeve per bar
    sh = sleeve_share([{"picks": ["A", "B", "C", "D", "E"]},
                       {"picks": ["C", "D", "E", "A", "B"]},
                       {"picks": ["A", "B", "G", "F", "C"]}], cls)
    assert sh["bars"] == 3, sh
    assert sh["top_sleeve_bars"] == {"commodity": 2, "equity": 1}, sh
    assert sh["top_sleeve_share"]["commodity"] == 0.667, sh
    # L9 the identity rule: a re-derived float inside the published rounding passes, an
    # off-by-one-in-the-last-place miss fails (this is the leg that decides whether the
    # caps price the same book the reader was told about)
    pub = {"cagr": 0.1149, "sharpe": 1.132, "maxdd": -0.1056}
    assert identity_ok({"cagr": 0.11494, "sharpe": 1.1318, "maxdd": -0.10562}, pub)
    assert not identity_ok({"cagr": 0.1150, "sharpe": 1.132, "maxdd": -0.1056}, pub)
    assert not identity_ok({"cagr": 0.1149, "sharpe": 1.1330, "maxdd": -0.1056}, pub)
    print("selftest 9/9 PASS")
    return 0


def main():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    print("bond-free universe", len(cols), "flips repaired", n_flip, flush=True)

    sc = E.build_score(close[cols], amt[cols], feats)

    # --- identity leg on the published window (same cutoff, same universe) ---------
    published = load_published(E.PATHS.results_dir)
    cut = pd.Timestamp(published["as_of"])
    m_idx = close.index <= cut
    id_ser, _ = R.open_to_open_equity(close.loc[m_idx, cols], openp.loc[m_idx, cols],
                                      amt.loc[m_idx, cols], sc.loc[m_idx],
                                      REBAL, N_HOLD, COST, vol_target=VT)
    id_stats = A.stats2(id_ser, "identity_" + PUBLISHED_LABEL)
    dev = identity_deviation(id_stats, published["numbers"])
    ok = identity_ok(id_stats, published["numbers"])
    print("identity on published window", published["as_of"],
          "measured", {k: id_stats[k] for k in ("cagr", "sharpe", "maxdd")},
          "dev", dev, "ok", ok, flush=True)
    if not ok:
        print("REFUSED: the cap-free rule no longer reproduces %s on its own window"
              % PUBLISHED_LABEL, dev, flush=True)
        return 3

    arms = [
        ("plain", {}),
        ("cap_comm_1", {"commodity": 1}),
        ("cap_comm_2", {"commodity": 2}),
        ("cap_comm_1_conv_1", {"commodity": 1, "convertible": 1}),
    ]
    runs = []
    base_ser = None
    for label, caps in arms:
        diag = []
        m, ser = run_arm(close[cols], openp[cols], amt[cols], sc, cls, caps, label, diag)
        m["sleeve"] = sleeve_share(diag, cls)
        runs.append(m)
        if base_ser is None:
            base_ser = ser
        print(label, {k: m[k] for k in ("cagr", "sharpe", "maxdd", "turnover")}, flush=True)

    # identity leg: the cap-free arm must be the published book, not merely close to it
    base = runs[0]

    # delta table vs the plain arm, per horizon
    deltas = []
    for r in runs[1:]:
        d = {"arm": r.get("label", ""), "caps": r["caps"]}
        for k in ("cagr", "sharpe", "maxdd", "cagr_oos", "sharpe_oos", "maxdd_oos"):
            d["d_" + k] = round(r[k] - base[k], 4) if (r.get(k) is not None and base.get(k) is not None) else None
        d["d_turnover"] = round(r["turnover"] - base["turnover"], 3)
        deltas.append(d)

    out = {
        "schema": "etf-book-sleeve-cap/v1",
        "as_of": str(close.index[-1].date()),
        "params": {"n_hold": N_HOLD, "rebal": REBAL, "cost": COST, "vol_target": VT},
        "universe": len(cols), "flips_repaired": n_flip,
        "published_arm": published, "identity_deviation": dev,
        "identity_ok": ok, "identity_stats": {k: id_stats.get(k) for k in ("cagr", "sharpe", "maxdd")},
        "runs": runs, "deltas": deltas,
    }
    p = os.path.join(E.PATHS.results_dir, "etf_book_sleeve_cap.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p, flush=True)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main())