"""Which asset class carries the beta the sizing rule divides by?

The executed book is sized as `k = beta_target / beta_hat` with beta_target 0.20
(r1256) and beta_hat 0.434543 measured on the book in force. The ticket it publishes
holds five names: four `crossborder` and one `equity`. The graded card's vocabulary is
equity / commodity / convertible -- `crossborder` has no counterpart there, so the beta
the rule divides by is partly a measurement of names the gate never prices.

This face answers exactly one question and publishes one number per name and per class:
how much of beta_hat 0.434543 does each name carry, and how much does each asset class
carry? Then it re-runs the SAME rule (same score, same 20-bar grid, same next-open fill,
same 8bp) on the graded universe alone, so the size quoted for 2026-11-11 can name the
class it is betting on.

Two different quantities are kept apart on purpose (a name that says "beta" for both
would let a reader substitute one for the other):

  * `published_path_beta`   -- what the rule actually divided by: the expanding OLS
                               slope of the realised book path (composition drifts
                               every 20 bars). Reproduced here as an identity leg.
  * `static_composition_beta` -- sum_i w_i * beta_i with TODAY's ticket weights held
                               over the whole window. This is the ONLY quantity that
                               decomposes additively per name, and it is not the path
                               beta; the gap between them is composition drift and is
                               printed rather than hidden.

A name whose history starts after the window begins is UNREADABLE, never zero (a censored
observation is not a measurement of no exposure). Coverage of ticket weight is reported
next to every sum for the same reason.

Run:
  python scripts/etf_book_class_beta_split.py run       # ~3 min (two panel sims)
  python scripts/etf_book_class_beta_split.py --check   # 0.2s, published face only
  python scripts/etf_book_class_beta_split.py selftest  # offline
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TICKET_GLOB = "results/etf_book_order/TICKET-*.json"
PROV_PATH = "results/etf_book_live_size_provenance/SIZE-PROVENANCE.json"
OUT_PATH = "results/etf_book_class_beta_split.json"

GRADED = ("equity", "commodity", "convertible")
MIN_OBS = 60           # bars of overlap before a name-level beta is a measurement
BARS_PER_YEAR = 250.0
# same tolerance the sibling face uses: half a percentage point of capital is not a
# rounding difference in a size quoted for a trade.
SIZE_TOL = 0.005
IDENTITY_TOL = 1e-6


def _read_json(rel):
    with open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return json.load(f)


def _json_default(o):
    """numpy scalars are not JSON types; a face that cannot be written is not published."""
    import numpy as np
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError("not serialisable: %r" % (type(o),))


def latest_ticket():
    files = sorted(glob.glob(os.path.join(BASE, TICKET_GLOB)))
    if not files:
        return None, None
    with open(files[-1], encoding="utf-8") as f:
        return os.path.basename(files[-1]), json.load(f)


def published_face():
    """Everything derivable without loading the panel (`--check` path)."""
    name, tk = latest_ticket()
    if tk is None:
        return {"face": "etf_book_class_beta_split", "verdict": "NO_TICKET",
                "sentence": "no ticket face on disk; nothing to split"}
    order = tk["ticket"]["order"]
    prov = _read_json(PROV_PATH) if os.path.exists(os.path.join(BASE, PROV_PATH)) else {}
    census = {}
    for r in order:
        census[r.get("class")] = census.get(r.get("class"), 0) + 1
    outside = {c: n for c, n in census.items() if c not in GRADED}
    return {
        "face": "etf_book_class_beta_split",
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "ticket_file": name,
        "beta_target": tk.get("beta_target"),
        "k_now": tk.get("k_now"),
        "book_weight": tk["ticket"].get("book_weight"),
        "decision_bar": tk.get("book_decided_at"),
        "published_path_beta": prov.get("beta_hat"),
        "names": [{"symbol": r["symbol"], "class": r.get("class"),
                   "weight": r.get("weight")} for r in order],
        "class_census": census,
        "classes_outside_graded_universe": outside,
        "graded_universe": sorted(GRADED),
        "ticket_names_outside_graded_universe": sum(outside.values()),
        "panel_work": "not run (file-only face; use `run` for the split)",
    }


def _pair(r, rm):
    import pandas as pd
    p = pd.concat([r, rm], axis=1).dropna()
    return p


def name_stats(close, mkt, names, weights, classes, end_bar=None):
    """Per-name beta / vol contribution on ONE fixed window, with its identity legs.

    `beta_contribution` sums to the STATIC composition beta (today's weights held over
    the window). `vol_contribution` is the Euler split of the reconstructed book's
    volatility and sums exactly to it; when some names are unreadable both sums cover
    only `weight_covered` of the ticket and say so.
    """
    import numpy as np
    import pandas as pd

    idx = close.index if end_bar is None else close.index[close.index <= end_bar]
    px = close.loc[idx]
    if mkt not in px.columns:
        raise ValueError("market proxy %r missing from panel" % (mkt,))
    rm = px[mkt].pct_change()

    rows = []
    for sym, w in zip(names, weights):
        w = float(w)
        row = {"symbol": sym, "class": classes.get(sym, "unknown"), "weight": w,
               "overlap_bars": 0, "beta": None, "sigma_ann": None,
               "beta_contribution": None, "vol_contribution": None, "unreadable": None}
        if sym not in px.columns:
            row["unreadable"] = "not on the panel"
            rows.append(row)
            continue
        pair = _pair(px[sym].pct_change(), rm)
        row["overlap_bars"] = int(len(pair))
        if len(pair) < MIN_OBS:
            row["unreadable"] = "fewer than %d overlapping bars (%d)" % (MIN_OBS, len(pair))
            rows.append(row)
            continue
        var = float(pair.iloc[:, 1].var())
        if not np.isfinite(var) or var <= 0:
            row["unreadable"] = "market variance is zero on this window"
            rows.append(row)
            continue
        row["beta"] = float(pair.iloc[:, 0].cov(pair.iloc[:, 1]) / var)
        row["sigma_ann"] = float(pair.iloc[:, 0].std()) * np.sqrt(BARS_PER_YEAR)
        row["beta_contribution"] = w * row["beta"]
        rows.append(row)

    readable = [r for r in rows if r["beta"] is not None]
    covered = float(sum(r["weight"] for r in readable))
    book_ret = None
    sigma_book = None
    vol_sum = None
    book_bars = 0
    window_first = None
    window_last = None
    window_limited_by = None
    if readable:
        # complete cases only: every contribution must be measured on the SAME bars as the
        # book volatility it is split from, otherwise the Euler identity is only approximately
        # true and the leg that checks it becomes a comfort blanket instead of a test.
        frame = pd.DataFrame({r["symbol"]: px[r["symbol"]].pct_change() for r in readable})
        frame["__mkt__"] = rm
        frame = frame.dropna()
        book_bars = int(len(frame))
        if book_bars:
            window_first = str(frame.index[0].date())
            window_last = str(frame.index[-1].date())
            firsts = {}
            for r in readable:
                v = px[r["symbol"]].pct_change().dropna()
                firsts[r["symbol"]] = v.index[0] if len(v) else None
            if firsts:
                # the name that sets the common window: without it the window would be longer.
                # Disclosing it is the difference between "measured on 306 bars" and a reader
                # assuming 5,258.
                window_limited_by = max(firsts, key=lambda s: firsts[s])
        wvec = pd.Series({r["symbol"]: r["weight"] for r in readable}, dtype=float)
        book_ret = frame[list(wvec.index)].mul(wvec, axis=1).sum(axis=1)
        # Euler split in RETURN units: w_i * cov(r_i, book) / sigma(book) sums to
        # sigma(book) itself. Dividing by the variance would give fractions summing to
        # 1 -- a share, not a contribution, and the two are not interchangeable.
        sigma_d = float(book_ret.std())
        sigma_book = sigma_d * np.sqrt(BARS_PER_YEAR)
        if sigma_d > 0:
            for r in readable:
                rr = frame[r["symbol"]]
                r["vol_contribution"] = float(r["weight"] *
                                              rr.cov(book_ret) / sigma_d
                                              * np.sqrt(BARS_PER_YEAR))
    # identity: the Euler split must rebuild the book volatility it was computed from.
    vol_total = None if not readable else float(sum(r["vol_contribution"] or 0.0 for r in readable))
    beta_static = None if not readable else float(sum(r["beta_contribution"] for r in readable))
    # The same names fully invested. The ticket weights sum to the book weight (0.46), so
    # `beta_static` is the beta of a 46%-invested mix and is NOT comparable with an
    # un-levered path beta -- dividing by the covered weight puts both on one denominator.
    beta_static_norm = None
    if readable and covered > 0:
        beta_static_norm = float(sum(r["beta_contribution"] for r in readable) / covered)

    by_class = {}
    for r in rows:
        c = r["class"]
        b = by_class.setdefault(c, {"names": 0, "readable_names": 0, "weight": 0.0,
                                    "beta_contribution": 0.0, "vol_contribution": 0.0})
        b["names"] += 1
        b["weight"] += r["weight"]
        if r["beta_contribution"] is not None:
            b["readable_names"] += 1
            b["beta_contribution"] += r["beta_contribution"]
        if r["vol_contribution"] is not None:
            b["vol_contribution"] += r["vol_contribution"]
    for c, b in by_class.items():
        b["weight"] = round(b["weight"], 6)
        b["beta_contribution"] = round(b["beta_contribution"], 6)
        b["vol_contribution"] = round(b["vol_contribution"], 6)

    return {
        "rows": rows,
        "by_class": dict(sorted(by_class.items())),
        "static_composition_beta": None if beta_static is None else round(beta_static, 6),
        "static_composition_beta_normalized": (
            None if beta_static_norm is None else round(beta_static_norm, 6)),
        "static_beta_denominator": "ticket weights sum to book_weight; normalized = divided "
                                   "by covered weight",
        "book_sigma_ann": None if sigma_book is None else round(sigma_book, 6),
        "vol_contribution_total": None if vol_total is None else round(vol_total, 6),
        "weight_covered": round(covered, 6),
        "weight_uncovered": round(1.0 - covered, 6),
        "unreadable_names": [r["symbol"] for r in rows if r["beta"] is None],
        "window_bars": int(len(idx)),
        "window_span": {"first": window_first, "last": window_last},
        "window_limited_by": window_limited_by,
        "book_bars_complete_case": book_bars,
    }


def verdict(published_k, graded_k, published_beta, graded_beta, tol=SIZE_TOL):
    """One sentence about the money: does dropping the ungraded names move the size?"""
    if None in (published_k, graded_k, published_beta, graded_beta):
        return {"verdict": "UNREADABLE",
                "sentence": "one side could not be measured; an unread rule is not evidence "
                            "that the sizes agree",
                "gap_pp": None, "size_same": None}
    gap = float(graded_k) - float(published_k)
    # inclusive boundary, with room for float subtraction (0.465-0.46 != 0.005 exactly)
    same = abs(gap) <= tol + 1e-12
    return {
        "verdict": "SAME_SIZE_AFTER_DROPPING_UNGRADED" if same else "SIZE_MOVES",
        "sentence": None,
        "graded_k": round(float(graded_k), 6),
        "published_k": round(float(published_k), 6),
        "gap_pp": round(100.0 * gap, 2),
        "graded_beta": round(float(graded_beta), 6),
        "published_beta": round(float(published_beta), 6),
        "size_same": same,
        "tol_pp": round(100.0 * tol, 2),
    }


def run():
    import numpy as np
    import pandas as pd

    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from scripts import etf_composite_pf as F
    from scripts import etf_phase_beta_target as BT
    from scripts import etf_book_order as BO
    from scripts import etf_equity_alpha as AE
    from scripts.etf_asset_class import classify

    face = published_face()
    if face.get("verdict") == "NO_TICKET":
        return face

    print("panel: loading", flush=True)
    close, openp, amt, feats = F.build_panel()
    if BO.REPAIR_PANEL:
        close, openp, n_flip = AE.repair_flips(close, openp)
        print("panel: repaired %d flip prints" % n_flip, flush=True)
    classes = pd.Series(classify(list(close.columns)))
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        return dict(face, verdict="MECHANISM_FAULT", sentence="no market proxy on the panel")

    dec_bar = pd.Timestamp(face["decision_bar"]) if face.get("decision_bar") else close.index[-1]
    names = [r["symbol"] for r in face["names"]]
    weights = [float(r["weight"]) for r in face["names"]]

    # ---- decomposition of the book in force
    print("split: %d ticket names over bars <= %s" % (len(names), str(dec_bar.date())), flush=True)
    split = name_stats(close, mkt_col, names, weights, classes, end_bar=dec_bar)

    # ---- published path beta, reproduced (identity leg #1)
    cols_a = [c for c in close.columns if classes[c] in _keep_classes()]
    score_a = F.build_score(close[cols_a], amt[cols_a], feats)
    print("arm published: %d symbols, next-open engine" % len(cols_a), flush=True)
    ser_a, _to_a, _gap_a = F.run_next_open(close[cols_a], openp[cols_a], amt[cols_a], feats,
                                          BO.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score_a)
    mkt = close[mkt_col]
    idx = ser_a.index.intersection(mkt.index)
    sched = BO.k_schedule(BT.rets(ser_a.reindex(idx)), BT.rets(mkt.reindex(idx)), BO.DEFAULT_BETA)
    if not sched:
        return dict(face, verdict="MECHANISM_FAULT", sentence="beta schedule empty")
    _k_pub, k_pub, beta_pub = sched[-1]

    # ---- the same rule on the graded universe alone (identity leg #2: same engine)
    cols_b = [c for c in close.columns if classes[c] in GRADED]
    score_b = F.build_score(close[cols_b], amt[cols_b], feats)
    print("arm graded: %d symbols, next-open engine" % len(cols_b), flush=True)
    ser_b, _to_b, _gap_b = F.run_next_open(close[cols_b], openp[cols_b], amt[cols_b], feats,
                                          BO.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score_b)
    idx_b = ser_b.index.intersection(mkt.index)
    sched_b = BO.k_schedule(BT.rets(ser_b.reindex(idx_b)), BT.rets(mkt.reindex(idx_b)),
                            BO.DEFAULT_BETA)
    if not sched_b:
        return dict(face, verdict="MECHANISM_FAULT", sentence="graded beta schedule empty")
    _k_g, k_graded, beta_graded = sched_b[-1]

    row_b = score_b.loc[dec_bar].dropna() if dec_bar in score_b.index else None
    names_graded = list(row_b.nlargest(F.N_HOLD).index) if row_b is not None else []

    # The split's common window is set by the youngest name in the ticket and can be far
    # shorter than the path's expanding window. Measure the path beta on that SAME window
    # too, so the composition gap is not silently a window-length gap.
    span = split.get("window_span") or {}
    path_same_window = None
    if span.get("first") and span.get("last"):
        rp_all = BT.rets(ser_a.reindex(idx))
        rm_all = BT.rets(mkt.reindex(idx))
        mask = ((rp_all.index >= pd.Timestamp(span["first"]))
                & (rp_all.index <= pd.Timestamp(span["last"])))
        rp_w, rm_w = rp_all[mask], rm_all[mask]
        var_w = float(rm_w.var()) if len(rm_w) else 0.0
        if var_w > 0 and len(rp_w) >= MIN_OBS:
            path_same_window = {"beta": round(float(rp_w.cov(rm_w)) / var_w, 6),
                                "bars": int(len(rp_w)),
                                "span": [span["first"], span["last"]],
                                "published_path_beta_full_window": round(float(beta_pub), 6)}

    published_beta = face.get("published_path_beta")
    published_k = face.get("k_now")
    # numpy bools are not JSON-serialisable; every leg is coerced at the boundary so the
    # face can be written, not just computed (r-type: a result that cannot be saved
    # silently stays unpublished).
    def _b(x):
        return None if x is None else bool(x)

    legs = {
        "published_beta_matches_face": _b(
            None if published_beta is None
            else abs(float(beta_pub) - float(published_beta)) <= 1e-4),
        "published_k_matches_ticket": _b(
            None if published_k is None else abs(float(k_pub) - float(published_k)) <= 1e-6),
        "vol_split_rebuilds_book_sigma": _b(
            None if split["book_sigma_ann"] is None or split["vol_contribution_total"] is None
            else abs(split["vol_contribution_total"] - split["book_sigma_ann"]) <= 1e-5),
        "class_sums_match_name_sums": _b(_class_sums_match(split)),
        "ticket_names_read_back": _b([r["symbol"] for r in split["rows"]] == names),
    }
    broken = [k for k, v in legs.items() if v is False]

    v = verdict(published_k, k_graded, published_beta, beta_graded)
    shares = {}
    tot = split["static_composition_beta"]
    if tot:
        for c, b in split["by_class"].items():
            shares[c] = round(100.0 * b["beta_contribution"] / tot, 2)

    out = dict(face)
    out.update({
        "panel_work": "run",
        "market_proxy": mkt_col,
        "published_path_beta": None if published_beta is None else round(float(published_beta), 6),
        "reproduced_path_beta": round(float(beta_pub), 6),
        "k_published": round(float(published_k), 6) if published_k is not None else None,
        "k_reproduced": round(float(k_pub), 6),
        "graded_arm": {
            "classes": sorted(GRADED),
            "universe_symbols": len(cols_b),
            "path_beta": round(float(beta_graded), 6),
            "k": round(float(k_graded), 6),
            "decision_bar": str(sched_b[-1][0].date()) if hasattr(sched_b[-1][0], "date")
                            else str(sched_b[-1][0]),
            "names_on_ticket_bar": names_graded,
            "names_classes": {s: str(classes.get(s, "unknown")) for s in names_graded},
        },
        "split": split,
        "static_composition_beta": split["static_composition_beta"],
        "static_composition_beta_normalized": split["static_composition_beta_normalized"],
        "book_sigma_ann": split["book_sigma_ann"],
        "class_share_of_static_beta_pct": shares,
        "path_beta_same_window": path_same_window,
        "beta_gap_normalized_pp": (
            None if path_same_window is None
            or split["static_composition_beta_normalized"] is None
            else round(100.0 * (path_same_window["beta"]
                                - split["static_composition_beta_normalized"]), 2)),
        "beta_gap_sized_vs_path_pp_UNIT_MISMATCH": (
            None if path_same_window is None or split["static_composition_beta"] is None
            else round(100.0 * (path_same_window["beta"] - split["static_composition_beta"]), 2)),
        "unit_note": ("the sized mix (%.1f%% invested) and an un-levered path (100%%) are on different "
                      "denominators; only beta_gap_normalized_pp compares like with like"
                      % (100.0 * (split["weight_covered"] or 0.0))),
        "beta_gap_vs_published_path_pp_FULL_WINDOW_MISMATCH": (
            None if published_beta is None or split["static_composition_beta_normalized"] is None
            else round(100.0 * (float(published_beta)
                                - split["static_composition_beta_normalized"]), 2)),
        "verdict": v["verdict"],
        "comparison": v,
        "identity_legs": legs,
        "identity_broken": broken,
        "sentence": _sentence(v, shares, split, face),
    })
    return out


def _keep_classes():
    from scripts import etf_variants_null_rolling as V
    return V.KEEP


def _class_sums_match(split):
    bs = split["by_class"]
    b_sum = sum(b["beta_contribution"] for b in bs.values())
    v_sum = sum(b["vol_contribution"] for b in bs.values())
    b_tot = split["static_composition_beta"] or 0.0
    v_tot = split["vol_contribution_total"] or 0.0
    return abs(b_sum - b_tot) <= 1e-5 and abs(v_sum - v_tot) <= 1e-5


def _sentence(v, shares, split, face):
    outside = face.get("classes_outside_graded_universe") or {}
    if v["verdict"] == "UNREADABLE":
        return v["sentence"]
    share_txt = ", ".join("%s %.1f%%" % (c, s) for c, s in sorted(shares.items(), key=lambda x: -x[1]))
    head = ("The book in force carries %.3f of static beta (%.3f on the same names fully "
            "invested), split by class as %s; dropping the %d name(s) the graded card never "
            "prices moves the size from %.6f to %.6f (%+.2fpp)."
            % (split["static_composition_beta"] or 0.0,
               split["static_composition_beta_normalized"] or 0.0, share_txt,
               sum(outside.values()), v["published_k"], v["graded_k"], v["gap_pp"]))
    tail = ("The size does not name a class it bets on, and the class it is betting on is not "
            "one the gate graded." if v["verdict"] == "SIZE_MOVES"
            else "The size survives the universe change; the class split is still what the "
                 "label should say.")
    return head + " " + tail


# --------------------------------------------------------------------------- selftest
def selftest():
    import numpy as np
    import pandas as pd

    ok = 0
    total = 0

    def leg(cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL:", label)

    rng = np.random.default_rng(7)
    n = 320
    idx = pd.bdate_range("2022-01-03", periods=n)
    rm = pd.Series(rng.normal(0.0004, 0.011, n), index=idx)
    r1 = 1.20 * rm + pd.Series(rng.normal(0, 0.002, n), index=idx)
    r2 = 0.40 * rm + pd.Series(rng.normal(0, 0.002, n), index=idx)
    px = pd.DataFrame({
        "MKT": 100 * (1 + rm).cumprod(),
        "AAA": 100 * (1 + r1).cumprod(),
        "BBB": 100 * (1 + r2).cumprod(),
        "NEW": np.nan,
    }, index=idx)
    # NEW lists only for the last 20 bars (censored history, not zero exposure)
    late = 100 * (1 + 0.9 * rm).cumprod()
    px.loc[idx[-20]:, "NEW"] = late.iloc[-20:]
    classes = pd.Series({"AAA": "crossborder", "BBB": "equity", "NEW": "crossborder"})

    s = name_stats(px, "MKT", ["AAA", "BBB", "NEW"], [0.4, 0.4, 0.2], classes)
    rows = {r["symbol"]: r for r in s["rows"]}
    leg(abs(rows["AAA"]["beta"] - 1.20) < 0.06, "AAA beta near 1.20 (got %r)" % rows["AAA"]["beta"])
    leg(abs(rows["BBB"]["beta"] - 0.40) < 0.06, "BBB beta near 0.40")
    leg(rows["NEW"]["beta"] is None, "censored history is UNREADABLE, not zero")
    leg("NEW" in s["unreadable_names"], "unreadable name listed")
    leg(abs(s["weight_covered"] - 0.8) < 1e-9, "coverage reports the unread weight")
    leg(abs(s["weight_uncovered"] - 0.2) < 1e-9, "uncovered weight reported")
    leg(s["static_composition_beta"] is not None
        and abs(s["static_composition_beta"]
                - (0.4 * rows["AAA"]["beta"] + 0.4 * rows["BBB"]["beta"])) < 1e-6,
        "static beta = sum of per-name contributions")
    leg(s["book_sigma_ann"] is not None
        and abs(s["vol_contribution_total"] - s["book_sigma_ann"]) < 1e-9,
        "Euler vol split rebuilds book sigma")
    leg(_class_sums_match(s), "class sums match name sums")
    leg(s["window_limited_by"] == "AAA" or s["window_limited_by"] == "BBB",
        "the common window names the name that sets it (got %r)" % s["window_limited_by"])
    leg(s["window_span"]["first"] is not None and s["window_span"]["last"] is not None,
        "the measurement window is printed, not implied")
    leg(s["book_bars_complete_case"] < s["window_bars"],
        "a late-listing name shortens the complete-case window and the shorter count is shown")
    leg(s["static_composition_beta_normalized"] is not None
        and abs(s["static_composition_beta_normalized"]
                - s["static_composition_beta"] / s["weight_covered"]) < 1e-6,
        "normalized beta is the sized beta over the covered weight (one denominator change)")
    leg(abs(s["by_class"]["crossborder"]["weight"] - 0.6) < 1e-9,
        "crossborder class weight includes the unreadable name")
    leg(s["by_class"]["crossborder"]["readable_names"] == 1,
        "readable count per class is not the name count")

    # a readable panel with a single name: weight_covered 1.0 and no uncovered twin
    s1 = name_stats(px[["MKT", "BBB"]], "MKT", ["BBB"], [1.0], classes)
    leg(abs(s1["weight_covered"] - 1.0) < 1e-9 and abs(s1["weight_uncovered"]) < 1e-9,
        "full coverage reported as 1.0/0.0")
    leg(s1["static_composition_beta_normalized"] is not None
        and abs(s1["static_composition_beta_normalized"] - s1["static_composition_beta"]) < 1e-9,
        "full coverage: normalized and sized beta coincide")

    # the two windows must be measured on their own bars
    s2 = name_stats(px, "MKT", ["AAA"], [1.0], classes, end_bar=idx[150])
    leg(s2["window_bars"] == 151, "end_bar truncates the window (got %d)" % s2["window_bars"])

    # verdict classes
    leg(verdict(0.46, 0.462, 0.43, 0.44)["verdict"] == "SAME_SIZE_AFTER_DROPPING_UNGRADED",
        "same size within tolerance")
    leg(verdict(0.46, 0.60, 0.43, 0.33)["verdict"] == "SIZE_MOVES", "size moves beyond tolerance")
    leg(verdict(0.46, None, 0.43, 0.44)["verdict"] == "UNREADABLE",
        "unread side is UNREADABLE not agreement")
    mov = verdict(0.46, 0.30, 0.43, 0.67)
    leg(abs(mov["gap_pp"] - (-16.0)) < 1e-6, "gap is graded minus published in pp")
    leg(mov["graded_k"] == 0.30 and mov["published_k"] == 0.46, "both sizes printed")

    # tolerance boundary is inclusive (a size exactly on the line is not a move)
    leg(verdict(0.46, 0.465, 0.43, 0.43)["size_same"] is True, "tolerance is inclusive")

    # name->class mapping survives a class the graded vocabulary does not know
    v = verdict(0.46, 0.40, 0.43, 0.50)
    sent = _sentence(v, {"crossborder": 62.5, "equity": 37.5}, s, 
                     {"classes_outside_graded_universe": {"crossborder": 2}})
    leg("62.5" in sent and "crossborder" in sent, "sentence names the class share")
    leg("not\none the gate graded" not in sent, "no newline injected into the sentence")

    # published_face degrades honestly with no ticket
    leg(published_face()["face"] == "etf_book_class_beta_split", "published face names itself")

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "--check":
        print(json.dumps(published_face(), ensure_ascii=False, indent=1))
        return 0
    t0 = None
    import time
    t0 = time.time()
    out = run()
    out["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    out["elapsed_sec"] = round(time.time() - t0, 1)
    path = os.path.join(BASE, OUT_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=_json_default)
    print(json.dumps({k: out.get(k) for k in
                      ("evidence_cutoff", "verdict", "comparison", "identity_broken",
                       "static_composition_beta", "published_path_beta",
                       "class_share_of_static_beta_pct", "sentence")},
                     ensure_ascii=False, indent=1))
    return 0 if not out.get("identity_broken") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))