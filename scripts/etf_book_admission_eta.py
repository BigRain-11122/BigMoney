#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The floor has been red for 35 rounds. Nothing said when it could go green.

r1418..r1427 built a yearly admission gate, made it able to say "cannot tell", and then
showed that the number Y4 actually uses (net_top2_share) cannot adjudicate three of its
own four arms -- so the only row refusing the adopted book was a ruler that could not
judge itself.  r1427 re-read every refusal through the two calibers r1426 marked
trusted (effective_years, years_for_half): all three phase books REFUSAL_SURVIVES.

That closed the "is it the ruler?" question but left the supply floor red with no
horizon.  A red that says "the book is front-loaded" is an observation; a red that says
"front-loaded, binding ruler = years_for_half, clears after N more years at the book's
own median iff no phase needs more" is a dated expectation somebody can act on.

WHAT THIS FILE DOES (no new pricing, no new judgement lines)
------------------------------------------------------------
1. Reprices the three phase-books through the published engine and checks each phase 0
   against r1427's published numbers (identity leg -- if it drifts, rc3, no file).
2. Publishes the RULER MATRIX: for every candidate, the verdict word of each caliber the
   r1426 receipt trusts, today.  A ruler swap is only a lever if some trusted ruler
   says PASS where Y4 says FAIL; the matrix prints that answer instead of assuming it.
3. Publishes the ETA: append n years at a stated rate (the candidate's own median, and
   as a sensitivity its worst full year and zero), recompute the four Y checks and both
   trusted calibers, and report the SMALLEST n that clears -- taken over every phase, so
   the number is phase-robust rather than a one-grid promise.

THE ASSUMPTION IS PRINTED, NOT IMPLIED: this is arithmetic continuation ("if the next
years come in at this book's median"), not a forecast.  A zero year does not help Y4 at
all -- that is a leg, because it is the intuition most readers arrive with.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import candidate_year_gate as G  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_robust_pf as R  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_admission_eta.json")
PHASE_GATE = os.path.join(ROOT, "results", "etf_book_phase_gate.json")
CALIBER_RECEIPT = os.path.join(ROOT, "results", "etf_book_year_caliber.json")
CANDIDATES = os.path.join(ROOT, "results", "admission", "CANDIDATES.json")

PHASE_STARTS = ("2020-01-01", "2020-01-08", "2020-01-15", "2020-01-22", "2020-01-29")
ARMS = (
    ("nobond_vt08_adopted", 0.08, 0.0),
    ("nobond_base", None, 0.0),
    ("nobond_vt08_floor_050", 0.08, 0.5),
)
MAX_APPEND = 15          # a horizon longer than this is reported as "not within horizon"
RATES = ("median", "worst_full", "zero")


def caliber_module():
    import etf_book_year_caliber as Kmod
    return Kmod


def trusted_names():
    try:
        with open(CALIBER_RECEIPT, encoding="utf-8") as f:
            face = json.load(f)
        return [c["caliber"] for c in face["decision"]["calibers"] if c.get("trusted")]
    except Exception:
        return []


def year_rows(series):
    yrs = Y.yearly_returns(series)
    return yrs


def rate_of(yrs: dict, kind: str) -> float:
    """The continuation rate.  'median' = this book's own median annual net (%), the
    middle of what it has actually done; 'worst_full' = its worst complete year."""
    vals = [v["net_pct"] for v in yrs.values() if v.get("net_pct") is not None]
    full = [v["net_pct"] for v in yrs.values()
            if v.get("net_pct") is not None and (v.get("cohorts") or 0) >= 4]
    if kind == "zero":
        return 0.0
    if kind == "median":
        return float(statistics.median(vals)) if vals else 0.0
    if kind == "worst_full":
        return float(min(full)) if full else (float(min(vals)) if vals else 0.0)
    raise ValueError(kind)


def append(yrs: dict, n: int, rate: float) -> dict:
    out = {str(k): dict(v) for k, v in yrs.items()}
    for i in range(n):
        out["app%02d" % (i + 1)] = {"net_pct": float(rate), "cohorts": 4}
    return out


def year_pass(yrs: dict, capacity: float | None) -> dict:
    rows = G._year_rows(yrs)
    y = G.year_checks(rows, capacity)
    four = ("Y1_positive_years_share", "Y2_median_positive",
            "Y3_worst_year", "Y4_top2_share")
    return {"metrics": y["metrics"], "checks": y["checks"],
            "all_four_pass": all(y["checks"][k] for k in four),
            "failing": [k for k in four if not y["checks"][k]]}


def clear_eta(yrs: dict, capacity: float | None, caliber: str | None,
              rate: float, horizon: int = MAX_APPEND) -> dict:
    """Smallest n in [0, horizon] that clears the Y-gate (caliber=None) or the named
    caliber; None = not within horizon.  Evaluated at every n, so a non-monotone
    ruler (years_for_half can rise and fall as years accrue) is reported, not assumed."""
    K = caliber_module()
    trace = []
    first = None
    for n in range(0, horizon + 1):
        y = append(yrs, n, rate)
        yp = year_pass(y, capacity)
        cals = K.calibers(list(y.values()))
        if caliber is None:
            ok = yp["all_four_pass"]
            value = yp["metrics"]["top2_share"]
        else:
            ok = K.adjudicate_caliber(caliber, [{"start": "app%02d" % n,
                                                "calibers": cals,
                                                "years": len(y)}])["state"] == "PASS"
            value = cals.get(caliber)
        trace.append({"n": n, "ok": bool(ok), "value": value,
                      "top2_share": yp["metrics"]["top2_share"]})
        if ok and first is None:
            first = n
    non_monotone = False
    seen_ok = False
    for t in trace:
        if t["ok"]:
            seen_ok = True
        elif seen_ok:
            non_monotone = True
            break
    # publish a compact trace: the first six steps (where the reader's intuition lives)
    # plus the step that actually clears.  A 15-step trace on 135 rulers is 460KB a round
    # for evidence nobody reads past the answer.
    keep = set(range(0, min(horizon, 5) + 1))
    if first is not None:
        keep.add(first)
    return {"caliber": caliber, "rate_kind": None, "rate_pct": round(rate, 4),
            "eta_years": first, "within_horizon": first is not None,
            "non_monotone": non_monotone,
            "trace": [t for t in trace if t["n"] in keep]}


def ruler_matrix(yrs: dict, trusted: list) -> dict:
    """Every caliber's own verdict on TODAY's book (single phase)."""
    K = caliber_module()
    cells = [{"start": "today", "calibers": K.calibers(list(yrs.values())),
              "years": len(yrs)}]
    out = {}
    for c in K.CALIBERS:
        adj = K.adjudicate_caliber(c, cells)
        out[c] = {"state": adj["state"], "value": cells[0]["calibers"].get(c),
                  "trusted": c in trusted}
    return out


def arm_series(close, openp, amt, sc, vol_target, vol_floor, start):
    return R.open_to_open_equity(close, openp, amt, sc, 20, 5, 0.0010,
                                 vol_target=vol_target, vol_floor=vol_floor, start=start)


def identity_check(phase_face: dict) -> dict:
    """Phase 0 of the adopted arm must reproduce r1427's published top-2 share."""
    if not phase_face:
        return {"ok": False, "reason": "no published phase gate face"}
    pub = {}
    for b in phase_face.get("books", []):
        rows = b.get("phase_rows") or []
        if rows:
            pub[b["book"]] = rows[0].get("top2_share")
    return {"published_phase0": pub}


def run() -> int:
    t0 = time.time()
    trusted = trusted_names()
    phase_face = {}
    if os.path.exists(PHASE_GATE):
        with open(PHASE_GATE, encoding="utf-8") as f:
            phase_face = json.load(f)
    pub0 = {}
    for b in phase_face.get("books", []):
        rows = b.get("phase_rows") or []
        if rows:
            pub0[b["book"]] = rows[0].get("top2_share")

    close, openp, amt, sc, n_flip = S.nobond_universe()
    cap = S.published_capacity()

    books = []
    worst_gap = 0.0
    for label, vt, floor in ARMS:
        per_phase = []
        for start in PHASE_STARTS:
            ser, _turn = arm_series(close, openp, amt, sc, vt, floor, start)
            yrs = year_rows(ser)
            yp = year_pass(yrs, cap)
            rates = {k: rate_of(yrs, k) for k in RATES}
            etas = {}
            for kind in RATES:
                for cal in (None,) + tuple(trusted):
                    c = clear_eta(yrs, cap, cal, rates[kind])
                    c["rate_kind"] = kind
                    etas["%s|%s" % (kind, cal or "Y-GATE")] = c
            per_phase.append({
                "start": start,
                "years": {str(k): round(v["net_pct"], 4) for k, v in sorted(yrs.items())},
                "metrics": yp["metrics"], "checks": yp["checks"],
                "all_four_pass": yp["all_four_pass"], "failing": yp["failing"],
                "rates_pct": {k: round(v, 4) for k, v in rates.items()},
                "ruler_matrix": ruler_matrix(yrs, trusted),
                "etas": etas,
            })
            # identity is phase-0 only: the published face names which start each row is
            if start == PHASE_STARTS[0] and label in pub0 and pub0[label] is not None:
                got = yp["metrics"]["top2_share"]
                if got is not None:
                    worst_gap = max(worst_gap, abs(got - pub0[label]))

        # phase-robust ETA = the largest n any phase needs (a promise only counts if
        # it holds on every grid start, not on the median one)
        agg = {}
        for key in per_phase[0]["etas"]:
            vals = [p["etas"][key]["eta_years"] for p in per_phase]
            within = all(v is not None for v in vals)
            agg[key] = {
                "eta_years_worst_phase": max(vals) if within else None,
                "within_horizon": within,
                "per_phase": vals,
                "non_monotone_any_phase": any(p["etas"][key]["non_monotone"]
                                              for p in per_phase),
                "rate_kind": per_phase[0]["etas"][key]["rate_kind"],
                "caliber": per_phase[0]["etas"][key]["caliber"],
            }
        books.append({"book": label, "vol_target": vt, "vol_floor": floor,
                      "phases": per_phase, "phase_robust_eta": agg,
                      "today_failing": sorted({k for p in per_phase for k in p["failing"]})})
        print("%-24s today failing=%s  eta(Y-GATE|median, worst phase)=%s"
              % (label, ",".join(books[-1]["today_failing"]) or "none",
                 agg["median|Y-GATE"]["eta_years_worst_phase"]), flush=True)
        for cal in trusted:
            k = "median|%s" % cal
            if k in agg:
                print("%-24s   %-18s eta=%s" % (label, cal,
                                                agg[k]["eta_years_worst_phase"]), flush=True)

    # single-phase published candidates (smallcap / breadth) ride the same arithmetic
    singles = []
    if os.path.exists(CANDIDATES):
        with open(CANDIDATES, encoding="utf-8") as f:
            cand = json.load(f)
        for c in cand.get("candidates", []):
            yrs = {"y%s" % r["year"]: {"net_pct": r["net_pct"], "cohorts": r["cohorts"]}
                   for r in c.get("years", []) if r.get("net_pct") is not None}
            if len(yrs) < 2:
                continue
            yp = year_pass(yrs, c.get("capacity_cny_1day_5pct"))
            rates = {k: rate_of(yrs, k) for k in RATES}
            etas = {}
            for kind in RATES:
                for cal in (None,) + tuple(trusted):
                    e = clear_eta(yrs, c.get("capacity_cny_1day_5pct"), cal, rates[kind])
                    e["rate_kind"] = kind
                    etas["%s|%s" % (kind, cal or "Y-GATE")] = e
            singles.append({"candidate": c["candidate"], "arm": c["arm"],
                            "verdict_today": c.get("verdict"),
                            "all_four_pass": yp["all_four_pass"], "failing": yp["failing"],
                            "metrics": yp["metrics"], "rates_pct": {k: round(v, 4)
                                                                   for k, v in rates.items()},
                            "ruler_matrix": ruler_matrix(yrs, trusted),
                            "eta_years": {k: v["eta_years"] for k, v in etas.items()},
                            "non_monotone": {k: v["non_monotone"] for k, v in etas.items()}})
            print("%-24s %-8s today %-12s eta(Y-GATE|median)=%s"
                  % (c["candidate"], c["arm"], c.get("verdict"),
                     etas["median|Y-GATE"]["eta_years"]), flush=True)

    out = {
        "face": "etf_book_admission_eta",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": ("the yearly gate refuses every candidate it has been given; is the "
                     "lever the ruler, the book, or time -- and if time, how much?"),
        "assumption": ("arithmetic continuation: the next years come in at a stated rate "
                       "(median / worst_full / zero). Not a forecast, and no price is "
                       "re-derived -- this file appends years to a published table."),
        "rates": list(RATES), "max_append_years": MAX_APPEND,
        "gate_lines_imported": {
            "positive_years_share": G.POSITIVE_YEARS_SHARE,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "top2_share_max": G.TOP2_SHARE_MAX,
            "capacity_floor_cny": G.CAPACITY_FLOOR_CNY,
        },
        "trusted_calibers": trusted,
        "data": {"universe": int(len(close.columns)), "bars": int(len(close.index)),
                 "flips_repaired": n_flip, "capacity_cny_1day_5pct": cap,
                 "phase_starts": list(PHASE_STARTS)},
        "identity": {"published_phase0_top2": pub0,
                     "max_abs_gap_vs_published": round(worst_gap, 6),
                     "tolerance": 1e-6, "ok": worst_gap <= 1e-6},
        "books": books,
        "single_phase_candidates": singles,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if not out["identity"]["ok"]:
        print("rc3 identity drift max|d|=%r vs published phase-0 -- refusing to publish"
              % worst_gap, flush=True)
        return 3
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("saved", OUT, flush=True)
    return 0


def selftest() -> int:
    errs = []

    def chk(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg, flush=True)
        if not ok:
            errs.append(msg)

    cap = 5e7
    # L1 a two-year headline needs exactly one median year to clear Y4 arithmetically
    two = {"2020": {"net_pct": 43.0, "cohorts": 4}, "2021": {"net_pct": 14.6, "cohorts": 4},
           "2022": {"net_pct": 5.6, "cohorts": 4}, "2023": {"net_pct": 5.5, "cohorts": 4},
           "2024": {"net_pct": 5.7, "cohorts": 4}, "2025": {"net_pct": 5.6, "cohorts": 4},
           "2026": {"net_pct": 1.9, "cohorts": 3}}
    e1 = clear_eta(two, cap, None, rate_of(two, "median"))
    chk(e1["eta_years"] == 1,
        "L1 Y4 clears after %r median year (median %r)" % (e1["eta_years"],
                                                           round(rate_of(two, "median"), 3)))

    # L2 a zero continuation cannot help Y4 at all: the numerator and denominator both
    # stand still, so the share is exactly unchanged
    e2 = clear_eta(two, cap, None, 0.0)
    chk(e2["eta_years"] is None,
        "L2 appending zero-return years never clears Y4 (%r)" % (e2["eta_years"],))
    chk(abs(e2["trace"][0]["top2_share"] - e2["trace"][3]["top2_share"]) < 1e-12,
        "L2b the share is unchanged by zero years (%.6f)" % e2["trace"][3]["top2_share"])

    # L3 years_for_half is NOT monotone in time: one spike year alone is more than half
    # the calendar, and the count can rise and then fall as flat years accrue
    spiky = {"2020": {"net_pct": 60.0, "cohorts": 4}, "2021": {"net_pct": 8.0, "cohorts": 4},
             "2022": {"net_pct": 8.0, "cohorts": 4}, "2023": {"net_pct": 8.0, "cohorts": 4}}
    K = caliber_module()
    vals = [(n, K.calibers(list(append(spiky, n, 8.0).values()))["years_for_half"])
            for n in range(0, 8)]
    seen = {v for _n, v in vals}
    chk(len(seen) > 1,
        "L3 years_for_half moves as flat years accrue: %s" % vals)
    e3 = clear_eta(spiky, cap, "years_for_half", 8.0)
    chk(e3["non_monotone"] or e3["eta_years"] is not None,
        "L3b a non-monotone ruler reports either an eta or the non-monotone flag (%r/%r)"
        % (e3["eta_years"], e3["non_monotone"]))

    # L4 the ETA is the worst phase, never the friendliest one
    gap_a = clear_eta(two, cap, None, 20.0)
    gap_b = clear_eta(two, cap, None, 5.0)
    worst = max([gap_a["eta_years"] or 99, gap_b["eta_years"] or 99])
    chk(worst == (gap_b["eta_years"] or 99),
        "L4 a faster continuation clears no later than a slow one (%r vs %r)"
        % (gap_a["eta_years"], gap_b["eta_years"]))

    # L5 an all-negative book publishes None, never 0 (a share that cannot exist)
    neg = {"2020": {"net_pct": -5.0, "cohorts": 4}, "2021": {"net_pct": -3.0, "cohorts": 4},
           "2022": {"net_pct": -1.0, "cohorts": 4}}
    yp = year_pass(neg, cap)
    chk(yp["metrics"]["top2_share"] is None,
        "L5 a non-positive annual sum publishes None (%r)" % (yp["metrics"]["top2_share"],))
    chk(not yp["all_four_pass"], "L5b a losing book does not pass the gate")
    e5 = clear_eta(neg, cap, None, rate_of(neg, "median"))
    chk(e5["eta_years"] is None,
        "L5c a losing book never clears by adding losing years (%r)" % (e5["eta_years"],))

    # L6 the rate selector cannot silently fall back to a number nobody declared
    chk(abs(rate_of(two, "zero")) == 0.0, "L6 zero rate is exactly zero")
    one = {"2026": {"net_pct": 4.0, "cohorts": 4}}
    chk(rate_of(one, "worst_full") == 4.0,
        "L6b worst_full falls back to the only published year (%r)"
        % rate_of(one, "worst_full"))

    # L7 identity: whatever the live face says, its tolerance and comparison must agree
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            face = json.load(f)
        ident = face.get("identity") or {}
        chk(ident.get("ok") is True,
            "L7 the published face carries a passing identity block (%r)"
            % ident.get("max_abs_gap_vs_published"))
        chk(face.get("trusted_calibers") is not None,
            "L7b the face declares its trusted set (%r)" % (face.get("trusted_calibers"),))
        books = face.get("books") or []
        chk(all("phase_robust_eta" in b and b["phase_robust_eta"] for b in books),
            "L7c every book publishes a phase-robust ETA block")
        chk(all(len(b.get("phases") or []) == len(PHASE_STARTS) for b in books),
            "L7d every book carries all %d phases" % len(PHASE_STARTS))
    else:
        chk(True, "L7 skipped: no published face yet (first run)")

    print("selftest %d/%d" % (7 + 7 - len(errs), 14), flush=True)
    return 0 if not errs else 1


def check() -> int:
    """Read-only form for the chain: the published face must still pass identity."""
    if not os.path.exists(OUT):
        print("no published face -- run first")
        return 2
    with open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    ident = face.get("identity") or {}
    ok = ident.get("ok") is True
    print("eta check: identity_ok=%r max|d|=%r books=%d"
          % (ok, ident.get("max_abs_gap_vs_published"), len(face.get("books") or [])))
    return 0 if ok else 3


def main(argv) -> int:
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    if mode == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))