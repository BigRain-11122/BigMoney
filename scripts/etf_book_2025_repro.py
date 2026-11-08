"""Was 2025 a year the book had, or one bet the book happened to hold?

r1421/r1426/r1435 left three published sentences that all point at 2025 and none of which
says whether 2025 can be RE-READ:

  * results/etf_book_year_attribution.json -- 2025 contributes +43.0pp net, of which
    +18.56pp is the commodity sleeve and +17.65pp the equity sleeve; the top three names
    are 518800 / 518600 / 518660 (+5.71 / +4.74 / +4.58 log points), all gold ETFs.
  * results/etf_book_half_year_provenance.json -- for the three refused books, HALF of the
    seven-year net comes from 2025, the newest FULL year (the last row is partial).
  * r1419/r1429 -- the same book reads a different top-2 share on each decision phase.

So the desk holds a headline whose single largest year is also the newest full year and
also a gold year. Three separate questions follow, and this face answers exactly those:

  (1) PHASE      does 2025 survive a one-week shift of the decision grid, or is 43pp the
                 reading of one coin-toss phase (r1419 family)?
  (2) COST       does 2025 survive 3x the modelled toll (30bp/side)?
  (3) BETA       was the association gold beta rather than selection? The book's 2025
                 commodity sleeve is measured against an equal-weight buy-and-hold of the
                 SAME commodity names over the SAME bars -- the gap is timing/selection,
                 the baseline is what holding the sleeve passively would have paid.

Zero prereg, zero judged face, zero network, zero engine edit, zero production change. The
walk is etf_book_year_attribution.walk imported (never retyped); the engine identity leg
is the same one that file pins. Every number below is derived; nothing is typed in.

  python scripts/etf_book_2025_repro.py run
  python scripts/etf_book_2025_repro.py --selftest
  python scripts/etf_book_2025_repro.py --check
"""
import json
import os
import statistics
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
import etf_book_year_attribution as Y  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_2025_repro.json")
YEAR = "2025"
# The five weekly starts are exactly one 20-bar rebalance block, the same phase set the
# year gate was adjudicated over (candidate_year_gate_phases.PHASE_STARTS).
PHASE_STARTS = ("2020-01-01", "2020-01-08", "2020-01-15", "2020-01-22", "2020-01-29")
COST_MULTIPLES = (1.0, 2.0, 3.0)
COST = 0.0010
VOL_TARGET = 0.08
# Frozen before reading: the verdict words must be decidable without seeing the numbers.
RULE = {
    "spread_pp_max": 15.0,
    "cost3x_floor_pp": 0.0,
    "words": {
        "REPRODUCES": "2025 is positive on every phase, the phase spread is inside "
                      "spread_pp_max, and 3x toll still leaves it positive",
        "PHASE_FRAGILE": "the phases disagree in sign, or the spread is wider than "
                         "spread_pp_max -- 2025 belongs to a grid, not to the book",
        "COST_FRAGILE": "2025 turns non-positive at 3x toll -- the year is a cost artifact",
        "NOT_REPRODUCIBLE": "2025 is non-positive on the median phase",
    },
    "beta_words": {
        "SELECTION_ADDS": "the book collected MORE than simply holding the same names "
                          "over the same bars -- the sleeve's timing/selection paid",
        "BETA_EXPLAINS": "the passive equal-weight sleeve paid at least what the book "
                         "collected -- nothing in this sleeve needs a selection story",
        "BOOK_LAGS_SLEEVE": "the book collected a negative amount in a sleeve that the "
                            "passive holding priced above zero",
    },
}


# ---------------------------------------------------------------- readings

def year_row(ser, buckets, cls, year=YEAR):
    """One calendar year from the same definition etf_book_year_attribution publishes."""
    log_curve = np.log(ser.astype(float))
    blocks = list(log_curve.groupby(log_curve.index.year))
    out = None
    for i, (y, blk) in enumerate(blocks):
        if str(y) != year:
            continue
        start_level = 0.0 if i == 0 else float(log_curve[log_curve.index.year < y].iloc[-1])
        rows = {k[1]: v for k, v in buckets.items() if k[0] == str(y)}
        end_level = float(blk.iloc[-1])
        sleeves = {}
        for name, pts in rows.items():
            if name == "toll":
                continue
            c = cls.get(name)
            if c is None:
                continue
            sleeves[c] = sleeves.get(c, 0.0) + pts
        top = sorted(((n, v) for n, v in rows.items() if n != "toll"),
                     key=lambda kv: -abs(kv[1]))[:5]
        # the published face (etf_book_year_attribution) counts LOG POINTS x 100, so a
        # sleeve of 18.56 means +18.56 log-points-percent; the identity leg is the unit
        # check, because mixing raw log units with pp silently rescales every sleeve by 100
        out = {
            "year": str(y),
            "log_pp": round((end_level - start_level) * 100.0, 4),
            "net_pct": round((float(np.exp(end_level - start_level)) - 1.0) * 100.0, 4),
            "sleeves": {k: round(v * 100.0, 4) for k, v in sorted(sleeves.items())},
            "toll_pp": round(rows.get("toll", 0.0) * 100.0, 4),
            "top_names": [{"name": n, "log_pp": round(v, 4),
                           "class": cls.get(n),
                           "share_of_year": round(v / (end_level - start_level), 4)
                           if end_level != start_level else None}
                          for n, v in top],
        }
    return out


def passive_sleeve(openp, names, year=YEAR):
    """Equal-weight buy-and-hold of `names` over the same calendar year, open to open.

    Uses the same price column and the same boundary rule as the year row (entering bar
    at the previous year's last level, exit at the year's last bar), so the two numbers
    are comparable without a second convention.
    """
    op = openp.reindex(columns=[n for n in names if n in openp.columns])
    if op.shape[1] == 0:
        return None
    sub = op.loc[(op.index.year >= int(year) - 1) & (op.index.year <= int(year))]
    if sub.shape[0] < 3:
        return None
    first_prev = op.loc[op.index.year < int(year)]
    begin = first_prev.iloc[-1] if first_prev.shape[0] else sub.iloc[0]
    end = op.loc[(op.index.year == int(year))].iloc[-1]
    rets = []
    for c in op.columns:
        a, b = begin.get(c), end.get(c)
        if a is not None and b is not None and np.isfinite(a) and np.isfinite(b) and a > 0:
            rets.append(float(np.log(b / a)))
    if not rets:
        return None
    return {"names": list(op.columns), "per_name_log_pp": round(float(np.mean(rets)) * 100, 4),
            "log_pp": round(float(np.mean(rets)) * 100, 4),
            "net_pct": round((float(np.exp(np.mean(rets))) - 1.0) * 100, 4),
            "n_names": len(rets)}


def verdict_of(rows, cost_rows):
    """Three-word state from the frozen RULE; nothing here looks at BETA."""
    nets = [r["net_pct"] for r in rows if r.get("net_pct") is not None]
    if not nets:
        return {"state": "NOT_REPRODUCIBLE", "reason": "no phase published a 2025 row"}
    med = float(statistics.median(nets))
    spread = max(nets) - min(nets)
    signs = {n > 0 for n in nets}
    base = {"median_net_pct": round(med, 4), "spread_pp": round(spread, 4),
            "min_net_pct": round(min(nets), 4), "max_net_pct": round(max(nets), 4),
            "phases": len(nets)}
    if med <= 0:
        return dict(base, state="NOT_REPRODUCIBLE", reason=RULE["words"]["NOT_REPRODUCIBLE"])
    if len(signs) > 1 or spread > RULE["spread_pp_max"]:
        return dict(base, state="PHASE_FRAGILE", reason=RULE["words"]["PHASE_FRAGILE"])
    c3 = [r["net_pct"] for r in cost_rows if r.get("multiple") == 3.0]
    if c3 and min(c3) <= RULE["cost3x_floor_pp"]:
        return dict(base, state="COST_FRAGILE", reason=RULE["words"]["COST_FRAGILE"],
                    at_3x_net_pct=round(min(c3), 4))
    return dict(base, state="REPRODUCES", reason=RULE["words"]["REPRODUCES"],
                at_3x_net_pct=round(min(c3), 4) if c3 else None)


def beta_reading(book_commodity_pp, passive):
    if passive is None or book_commodity_pp is None or passive["log_pp"] <= 0:
        return {"state": "UNREADABLE",
                "reason": "passive sleeve flat or unpriced; no beta question to answer"}
    share = book_commodity_pp / passive["log_pp"]
    if book_commodity_pp < 0:
        state = "BOOK_LAGS_SLEEVE"
    elif book_commodity_pp > passive["log_pp"]:
        state = "SELECTION_ADDS"
    else:
        state = "BETA_EXPLAINS"
    return {"state": state, "reason": RULE["beta_words"][state],
            "book_commodity_log_pp": round(book_commodity_pp, 4),
            "passive_log_pp": passive["log_pp"],
            "share_of_passive": round(share, 4)}


# ---------------------------------------------------------------- run

def _universe():
    close, openp, amt, feats = E.build_panel()
    close, openp, _n = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls_all = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls_all[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    return close[cols], openp[cols], amt[cols], sc, {c: cls_all[c] for c in cols}


def run():
    t0 = time.time()
    close, openp, amt, sc, cls = _universe()

    phases, cost_rows, identity = [], [], None
    for start in PHASE_STARTS:
        ser, buckets, _by = Y.walk(close, openp, amt, sc, cls, cost=COST,
                                   vol_target=VOL_TARGET, start=start)
        row = year_row(ser, buckets, cls)
        if identity is None:
            ref, _turn = R.open_to_open_equity(close, openp, amt, sc, 20, 5, COST,
                                              vol_target=VOL_TARGET, start=start)
            gap = float(np.max(np.abs(ser.to_numpy()
                                      - ref.reindex(ser.index).to_numpy())))
            identity = {"phase": start, "max_abs_gap_vs_engine": gap}
        phases.append({"start": start, "row": row})
        print("  phase %-12s 2025 net %8.3f%%  commodity %7.2fpp  toll %6.2fpp  top %s"
              % (start, row["net_pct"] if row else float("nan"),
                 (row or {}).get("sleeves", {}).get("commodity", 0.0),
                 (row or {}).get("toll_pp", 0.0),
                 ((row or {}).get("top_names") or [{}])[0].get("name")), flush=True)

    for mult in COST_MULTIPLES:
        ser, buckets, _by = Y.walk(close, openp, amt, sc, cls, cost=COST * mult,
                                   vol_target=VOL_TARGET, start=PHASE_STARTS[0])
        row = year_row(ser, buckets, cls)
        cost_rows.append({"multiple": mult, "cost_per_side": COST * mult,
                          "net_pct": row["net_pct"] if row else None,
                          "toll_pp": row["toll_pp"] if row else None,
                          "commodity_pp": (row or {}).get("sleeves", {}).get("commodity")})

    # which names the 2025 commodity sleeve collected, and what holding them passively paid
    med_row = None
    for p in phases:
        if p["start"] == PHASE_STARTS[0]:
            med_row = p["row"]
    commodity_names = sorted(c for c, k in cls.items() if k == "commodity")
    top_commodity = [t["name"] for t in (med_row or {}).get("top_names", [])
                     if t.get("class") == "commodity"]
    passive_all = passive_sleeve(openp, commodity_names)
    passive_top = passive_sleeve(openp, top_commodity) if top_commodity else None
    book_commodity = ((med_row or {}).get("sleeves", {}) or {}).get("commodity")

    verdict = verdict_of([p["row"] for p in phases], cost_rows)
    beta = beta_reading(book_commodity, passive_all)

    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": "is the book's 2025 a readable year or a single-phase, cost-edged, "
                    "gold-beta year?",
        "rule": {"kind": "exploratory", "prereg": None, "verdict": None, "ledger": None,
                 "why": "decomposes and re-prices an already-published year; it admits "
                        "nothing and refuses nothing",
                 "frozen": RULE, "frozen_before_read": True},
        "config": {"year": YEAR, "rebal": 20, "n_hold": 5, "cost_per_side": COST,
                   "vol_target": VOL_TARGET, "phase_set": list(PHASE_STARTS),
                   "cost_multiples": list(COST_MULTIPLES),
                   "walk": "etf_book_year_attribution.walk (imported)"},
        "identity": identity,
        "phases": phases,
        "cost_ladder": cost_rows,
        "verdict": verdict,
        "sleeve_beta": {
            "reading": beta,
            "commodity_names_in_panel": len(commodity_names),
            "top_commodity_names": top_commodity,
            "passive_all_commodity": passive_all,
            "passive_top_names": passive_top,
        },
        "reading_note": "net_pct is a calendar-year return from the previous year's last "
                        "level to this year's last bar (etf_book_year_attribution's own "
                        "definition). passive_* is equal-weight buy-and-hold of the same "
                        "names over the same boundary. A bet and a book print the same "
                        "headline until they are separated like this.",
        "elapsed_sec": round(time.time() - t0, 2),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("verdict: %s (%s)" % (verdict["state"], verdict["reason"]))
    print("beta: %s (book %s pp vs passive %s pp)"
          % (beta["state"], beta.get("book_commodity_log_pp"),
             (passive_all or {}).get("log_pp")))
    print("wrote", OUT)
    return 0


# ---------------------------------------------------------------- selftest

def _fixture(n_bars=520, n_names=6, seed=11):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-01", periods=n_bars)
    drift = rng.normal(0.0004, 0.0006, n_names)
    rets = rng.normal(0, 0.008, (n_bars, n_names)) + drift
    close = pd.DataFrame(100 * np.exp(np.cumsum(rets, axis=0)), index=idx,
                         columns=["A%d" % i for i in range(n_names)])
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(5e9, index=idx, columns=close.columns)
    cls = {c: ("commodity" if i == 0 else "equity") for i, c in enumerate(close.columns)}
    sc = close.pct_change(20).fillna(0.0)
    return close, openp, amt, sc, cls


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    close, openp, amt, sc, cls = _fixture()
    ser, buckets, _by = Y.walk(close, openp, amt, sc, cls, cost=COST,
                               vol_target=None, start="2024-01-01")
    row = year_row(ser, buckets, cls, year="2024")
    leg("a year row is published for a fixture year", row is not None and "net_pct" in row)
    parts = sum(row["sleeves"].values()) + row["toll_pp"]
    leg("sleeves + toll add up to the year's log return", abs(parts - row["log_pp"]) < 1e-6,
        "%.9f vs %.9f" % (parts, row["log_pp"]))

    # phase reproducibility on a deterministic fixture: same book, same numbers
    s1, b1, _ = Y.walk(close, openp, amt, sc, cls, cost=COST, vol_target=None,
                       start="2024-01-01")
    s2, b2, _ = Y.walk(close, openp, amt, sc, cls, cost=COST, vol_target=None,
                       start="2024-01-01")
    leg("the walk is deterministic (rerun equals run)",
        float(np.max(np.abs(s1.to_numpy() - s2.to_numpy()))) == 0.0)

    # cost monotonicity: a heavier toll cannot pay more
    rows = []
    for mult in (1.0, 2.0, 3.0):
        s, b, _ = Y.walk(close, openp, amt, sc, cls, cost=COST * mult, vol_target=None,
                         start="2024-01-01")
        rows.append(year_row(s, b, cls, year="2024")["net_pct"])
    leg("cost ladder is monotone non-increasing", rows[0] >= rows[1] >= rows[2],
        str(rows))

    # verdict words are reachable
    v = verdict_of([{"net_pct": 5.0}, {"net_pct": 6.0}, {"net_pct": 7.0}],
                   [{"multiple": 3.0, "net_pct": 2.0}])
    leg("a clean phase set reads REPRODUCES", v["state"] == "REPRODUCES", v["state"])
    v = verdict_of([{"net_pct": 5.0}, {"net_pct": -6.0}, {"net_pct": 7.0}],
                   [{"multiple": 3.0, "net_pct": 2.0}])
    leg("a sign-changing phase set reads PHASE_FRAGILE", v["state"] == "PHASE_FRAGILE",
        v["state"])
    v = verdict_of([{"net_pct": 5.0}, {"net_pct": 6.0}, {"net_pct": 7.0}],
                   [{"multiple": 3.0, "net_pct": -0.5}])
    leg("a year that dies at 3x toll reads COST_FRAGILE", v["state"] == "COST_FRAGILE",
        v["state"])
    v = verdict_of([{"net_pct": -1.0}, {"net_pct": -2.0}], [])
    leg("a negative median reads NOT_REPRODUCIBLE", v["state"] == "NOT_REPRODUCIBLE",
        v["state"])

    # passive sleeve is a plain equal-weight log return over one boundary
    op = pd.DataFrame({"X": [10.0, 12.0, 15.0], "Y": [10.0, 10.0, 10.0]},
                      index=pd.to_datetime(["2024-12-31", "2025-06-30", "2025-12-31"]))
    p = passive_sleeve(op, ["X", "Y"], year="2025")
    want = float(np.mean([np.log(15.0 / 10.0), np.log(10.0 / 10.0)])) * 100
    leg("passive sleeve averages the per-name log return",
        abs(p["log_pp"] - round(want, 4)) < 1e-9, "%.6f vs %.6f" % (p["log_pp"], want))

    # beta words
    leg("a book that only matches the sleeve reads BETA_EXPLAINS",
        beta_reading(10.0, {"log_pp": 18.0})["state"] == "BETA_EXPLAINS")
    leg("a book that beats the sleeve reads SELECTION_ADDS",
        beta_reading(20.0, {"log_pp": 18.0})["state"] == "SELECTION_ADDS")
    leg("a book that trails the sleeve reads BOOK_LAGS_SLEEVE",
        beta_reading(-2.0, {"log_pp": 18.0})["state"] == "BOOK_LAGS_SLEEVE")
    leg("a flat sleeve leaves the beta question unreadable",
        beta_reading(5.0, {"log_pp": 0.0})["state"] == "UNREADABLE")

    errs = [n for n, ok, _ in legs if not ok]
    for n, ok, d in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", n, ("  | " + d) if d else ""))
    print("selftest %d/%d" % (len(legs) - len(errs), len(legs)))
    return 0 if not errs else 1


# ---------------------------------------------------------------- check

def check():
    """Re-derive the published verdict and beta state from the receipt's own rows."""
    if not os.path.exists(OUT):
        print("check: receipt absent; nothing to check")
        return 2
    with open(OUT, encoding="utf-8") as fh:
        doc = json.load(fh)
    probs = []
    rows = [p["row"] for p in doc.get("phases", [])]
    want = verdict_of(rows, doc.get("cost_ladder") or [])
    got = doc.get("verdict") or {}
    for k in ("state", "median_net_pct", "spread_pp", "min_net_pct", "max_net_pct"):
        if want.get(k) != got.get(k):
            probs.append("verdict.%s published %r re-derived %r" % (k, got.get(k), want.get(k)))
    sb = doc.get("sleeve_beta") or {}
    med = next((p["row"] for p in doc.get("phases", [])
                if p["start"] == doc["config"]["phase_set"][0]), None)
    book_pp = ((med or {}).get("sleeves") or {}).get("commodity")
    want_beta = beta_reading(book_pp, sb.get("passive_all_commodity"))
    for k in ("state", "share_of_passive"):
        if want_beta.get(k) != (sb.get("reading") or {}).get(k):
            probs.append("sleeve_beta.%s published %r re-derived %r"
                         % (k, (sb.get("reading") or {}).get(k), want_beta.get(k)))
    if probs:
        for p in probs:
            print("CHECK-FAIL", p)
        return 3
    print("check OK: verdict %s, beta %s" % (got.get("state"), want_beta.get("state")))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd in ("--selftest", "selftest"):
        return selftest()
    if cmd in ("--check", "check"):
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))