"""The pool is empty because every book the desk has judged fails its own calendar.

r1464 onward the supply face has printed AGENDA_DEBT with one cause: four candidates,
zero that pass. r1418 pointed the calendar gate at the book the desk actually holds
(nobond_vt08_adopted) and got CONDITIONAL on exactly one check, Y4_top2_share, at
71.08% against a 70% line. r1449 then showed the rung is not a rounding artefact:
narrower windows and narrower universes move the number by -4.76pp and -2.81pp, so a
gate-legal rung may simply not exist on that path.

This file asks the question nobody has asked: the 8% vol target is the ONLY knob
between the ADMITing bond-free book (68.98% top2) and the refused one (71.08%). The
target is not fixed by law -- 8% was a choice. So sweep the rung itself: no target,
8%, 10%, 12%, 15%, 20%, 25%, and for each one re-run the published engine (imported,
never re-implemented) and re-issue a verdict through candidate_year_gate.admission_block
(the frozen lines are imported, so this file cannot drift the gate).

Two things this face refuses to do:

* It does not relax the gate to make a book pass. The lines in candidate_year_gate.py
  are imported as they stand; if no rung passes, the answer is NO_RUNG_PASSES and the
  supply line's debt is a science debt, not a missing round.
* It does not call a passing rung "better". A rung that clears Y4 by shrinking the
  book is a smaller book; the receipt prints CAGR, drawdown and realised vol beside the
  verdict so the trade is visible instead of implied.

Usage:
    python scripts/etf_book_vt_ladder.py run [--quick]
    python scripts/etf_book_vt_ladder.py check
    python scripts/etf_book_vt_ladder.py selftest
"""
import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_vt_ladder")
OUT = os.path.join(OUT_DIR, "VT-LADDER.json")
BARS_PER_WINDOW = 60
CELL = {"rebalance_days": 20, "top_n": 5, "cost": 0.0010}
BARS_PER_YEAR = 244.0

# The rung is the only knob: same panel, same score, same rebalance, same cost.
RUNGS = [("none", None), ("vt08", 0.08), ("vt10", 0.10), ("vt12", 0.12),
         ("vt15", 0.15), ("vt20", 0.20), ("vt25", 0.25)]
QUICK_RUNGS = [("none", None), ("vt08", 0.08), ("vt12", 0.12)]


def yearly_returns(ser: pd.Series) -> dict:
    """Calendar-year returns on the book's own definition (last/first within the
    year), plus the 60-bar window count the gate uses as its cohort analogue."""
    ser = ser.dropna().astype(float)
    out = {}
    for year, blk in ser.groupby(ser.index.year):
        ret = float(blk.iloc[-1]) / float(blk.iloc[0]) - 1.0
        out[str(year)] = {"net_pct": ret * 100.0,
                          "cohorts": int(len(blk) // BARS_PER_WINDOW),
                          "bars": int(len(blk))}
    return out


def realised_vol(ser: pd.Series) -> float | None:
    """Annualised vol of the book's own daily returns -- the number the target is
    supposed to hit. Reported, never used as a pass condition."""
    r = ser.dropna().astype(float).pct_change().dropna()
    if len(r) < 30:
        return None
    return float(r.std() * np.sqrt(BARS_PER_YEAR))


def sizing_by_year(diag: list, ser: pd.Series) -> dict:
    """Average position scale the target applied per calendar year (1.0 = fully
    invested). Derived from the engine's own diag rows, never from a formula here."""
    if not diag:
        return {}
    by_year: dict = {}
    for row in diag:
        y = str(pd.Timestamp(row["date"]).year)
        by_year.setdefault(y, []).append(float(row["scale"]))
    return {y: round(float(np.mean(v)), 4) for y, v in sorted(by_year.items())}


def rung_row(label: str, vt: float | None, ser: pd.Series, turn: float,
             diag: list) -> dict:
    years = yearly_returns(ser)
    cagr = A.stats2(ser, label).get("cagr")
    blk = G.admission_block(years, None, None, cagr)
    return {
        "rung": label,
        "vol_target": vt,
        "cagr_pct": cagr,
        "sharpe": A.stats2(ser, label).get("sharpe"),
        "maxdd_pct": A.stats2(ser, label).get("maxdd"),
        "vol_realised_pct": (None if realised_vol(ser) is None
                             else round(realised_vol(ser) * 100.0, 3)),
        "turnover_per_side": round(float(turn), 3),
        "verdict": blk["verdict"],
        "checks": blk["checks"],
        "year_metrics": blk["year_metrics"],
        "years": blk["years"],
        "partial_years": blk["partial_years"],
        "sizing_scale_by_year": sizing_by_year(diag, ser),
    }


def verdict_phrase(rows: list) -> dict:
    """Read the ladder's answer off its own rows; never hand-written."""
    if not rows:
        return {"answer": "UNKNOWN", "detail": "no rung was priced -- nothing to read"}
    passed = [r for r in rows if r["verdict"] == "ADMIT"]
    if passed:
        first = passed[0]
        return {"answer": "LADDER_HAS_RUNG",
                "detail": ("%s clears every frozen check (top2 %.4f <= %.2f)"
                           % (first["rung"], first["year_metrics"]["top2_share"],
                              G.TOP2_SHARE_MAX)),
                "rung": first["rung"]}
    best = min(rows, key=lambda r: (r["year_metrics"]["top2_share"] is None,
                                    r["year_metrics"]["top2_share"] or 9.9))
    fail = [k for k, v in best["checks"].items() if v is False]
    return {"answer": "NO_RUNG_PASSES",
            "detail": ("best rung %s still fails %s (top2 %.4f vs %.2f)"
                       % (best["rung"], ",".join(fail) or "?",
                          best["year_metrics"]["top2_share"] or float("nan"),
                          G.TOP2_SHARE_MAX)),
            "best_rung": best["rung"]}


def _sha16(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def build_runs(rungs=None) -> tuple[list, dict]:
    rungs = rungs or RUNGS
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    rows = []
    for label, vt in rungs:
        diag: list = []
        ser, turn = R.open_to_open_equity(
            close[cols], openp[cols], amt[cols], sc,
            CELL["rebalance_days"], CELL["top_n"], CELL["cost"],
            vol_target=vt, diag=diag if vt is not None else None)
        rows.append(rung_row(label, vt, ser, turn, diag))
        print("%-5s vt=%s cagr=%s maxdd=%s vol=%s verdict=%s"
              % (label, vt, rows[-1]["cagr_pct"], rows[-1]["maxdd_pct"],
                 rows[-1]["vol_realised_pct"], rows[-1]["verdict"]), flush=True)
    meta = {"bars": int(len(close)), "first": str(close.index[0].date()),
            "last": str(close.index[-1].date()),
            "flips_repaired": int(n_flip), "bond_free_universe": len(cols),
            "cell": dict(CELL)}
    return rows, meta


def run(rungs=None) -> dict:
    t0 = time.time()
    rows, meta = build_runs(rungs)
    out = {
        "face": "etf_book_vt_ladder",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": meta["last"],
        "cell": "N5_R20_10bp",
        "question": ("the 8% vol target is the only knob between the ADMITing "
                     "bond-free book and the refused one -- does any rung clear "
                     "the same frozen calendar gate"),
        "gate_rules": {
            "source": "scripts/candidate_year_gate.py (imported, not copied)",
            "top2_share_max": G.TOP2_SHARE_MAX,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "positive_years_share_min": G.POSITIVE_YEARS_SHARE,
        },
        "data": meta,
        "rungs": rows,
        "answer": verdict_phrase(rows),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


def load() -> dict | None:
    if not os.path.exists(OUT):
        return None
    with io.open(OUT, encoding="utf-8") as f:
        return json.load(f)


def check() -> int:
    """Re-derive every decision from the published face itself."""
    d = load()
    if d is None:
        print("MISSING %s" % OUT)
        return 1
    errs = []
    rows = d.get("rungs") or []
    if not rows:
        errs.append("face publishes no rungs")
    for r in rows:
        yrs = {str(v["year"]): {"net_pct": v["net_pct"], "cohorts": v["cohorts"]}
               for v in (r.get("years") or [])}
        again = G.admission_block(yrs, None, None, r.get("cagr_pct"))
        if again["verdict"] != r["verdict"]:
            errs.append("%s verdict re-derives: %s != %s"
                        % (r["rung"], again["verdict"], r["verdict"]))
        m = again["year_metrics"]
        if m["top2_share"] is not None and abs(m["top2_share"]
                                               - r["year_metrics"]["top2_share"]) > 1e-9:
            errs.append("%s top2_share re-derives" % r["rung"])
        if r["checks"]["Y4_top2_share"] != (m["top2_share"] <= G.TOP2_SHARE_MAX):
            errs.append("%s Y4 flag disagrees with its own top2_share" % r["rung"])
        for y, s in (r.get("sizing_scale_by_year") or {}).items():
            if not (0.0 <= s <= 1.0 + 1e-9):
                errs.append("%s scale %s=%s outside [0,1]" % (r["rung"], y, s))
        if r["vol_realised_pct"] is not None and r["vol_target"] is not None:
            # a target far below what the engine actually delivered is worth naming,
            # but it is a reading, not a failure
            pass
    answer = verdict_phrase(rows)
    if answer["answer"] != d["answer"]["answer"]:
        errs.append("answer re-derives: %s != %s"
                    % (answer["answer"], d["answer"]["answer"]))
    passed = [r["rung"] for r in rows if r["verdict"] == "ADMIT"]
    if bool(passed) != (d["answer"]["answer"] == "LADDER_HAS_RUNG"):
        errs.append("answer word disagrees with the rung list")
    if errs:
        print("CHECK_FAIL")
        for e in errs:
            print("  -", e)
        return 1
    print("CHECK_OK rungs=%d answer=%s" % (len(rows), d["answer"]["answer"]))
    return 0


def _synth_ser(year_nets: dict, bars_per_year: int = 244) -> pd.Series:
    """A level series whose calendar-year returns are exactly year_nets (in pp)."""
    idx, vals = [], []
    lv = 1.0
    for y in sorted(year_nets):
        start = lv
        for i in range(bars_per_year):
            if i == 0:
                vals.append(lv)
            else:
                lv = start * (1.0 + year_nets[y] / 100.0) ** (i / (bars_per_year - 1.0))
                vals.append(lv)
            idx.append(pd.Timestamp("%s-01-02" % y) + pd.Timedelta(days=i))
        lv = vals[-1]
    return pd.Series(vals, index=pd.DatetimeIndex(idx))


def selftest() -> int:
    ok = tot = 0
    errs = []

    def chk(cond, msg):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            errs.append(msg)

    # L1 yearly_returns reproduces the calendar definition on a synthetic curve
    nets = {"2020": 5.0, "2021": -3.0, "2022": 8.0}
    ser = _synth_ser(nets)
    yr = yearly_returns(ser)
    chk(len(yr) == 3, "three calendar years from the synthetic curve")
    chk(all(abs(yr[y]["net_pct"] - nets[y]) < 1e-6 for y in nets),
        "each year's return equals the one it was built from")
    chk(all(yr[y]["cohorts"] == 244 // BARS_PER_WINDOW for y in nets),
        "window count is floor(bars/60)")

    # L2 a ladder carried by two years is refused by the imported gate
    carried = {"2020": 1.0, "2021": 2.0, "2022": 2.0, "2023": 3.0, "2024": 25.0}
    blk = G.admission_block({str(y): {"net_pct": v, "cohorts": 4}
                             for y, v in carried.items()}, None, None, 0.08)
    chk(blk["checks"]["Y4_top2_share"] is False and blk["verdict"] != "ADMIT",
        "carried-by-two-years ladder fails Y4 -> %s" % blk["verdict"])

    # L3 an even ladder clears it (so a NO_RUNG_PASSES answer means the books, not the gate)
    even = {str(y): 8.0 for y in range(2020, 2026)}
    blk2 = G.admission_block({str(y): {"net_pct": v, "cohorts": 4}
                              for y, v in even.items()}, None, None, 0.08)
    chk(blk2["verdict"] == "ADMIT", "an even ladder still passes -> %s" % blk2["verdict"])

    # L4 the answer word is read off the rows, both directions
    def fake(rung, top2, verdict="REFUSE", checks=None):
        return {"rung": rung, "verdict": verdict,
                "checks": checks or {"Y4_top2_share": False},
                "year_metrics": {"top2_share": top2}}
    a1 = verdict_phrase([fake("a", 0.72), fake("b", 0.69, "ADMIT",
                                              {"Y4_top2_share": True})])
    chk(a1["answer"] == "LADDER_HAS_RUNG" and a1["rung"] == "b",
        "a passing rung is reported with its name")
    a2 = verdict_phrase([fake("a", 0.72), fake("b", 0.71)])
    chk(a2["answer"] == "NO_RUNG_PASSES" and a2["best_rung"] == "b",
        "no rung passing reports the closest one, not a relaxation")
    a3 = verdict_phrase([])
    chk(a3["answer"] == "UNKNOWN",
        "an empty ladder is UNKNOWN, never a silent 'nothing passes'")

    # L5 realised vol is a reading, and a degenerate curve cannot fake one
    flat = pd.Series([1.0] * 50, index=pd.bdate_range("2024-01-01", periods=50))
    chk(realised_vol(flat) == 0.0, "a flat curve has zero realised vol")
    chk(realised_vol(pd.Series([1.0] * 5, index=pd.bdate_range("2024-01-01", periods=5)))
        is None, "too few bars is None, not 0")

    # L6 sizing_by_year averages the engine's own diag rows per calendar year
    diag = [{"date": "2024-01-03", "scale": 0.5}, {"date": "2024-06-03", "scale": 1.0},
            {"date": "2025-01-03", "scale": 0.25}]
    s = sizing_by_year(diag, ser)
    chk(abs(s["2024"] - 0.75) < 1e-12 and abs(s["2025"] - 0.25) < 1e-12,
        "sizing averages within the year, not across")
    chk(sizing_by_year([], ser) == {}, "no diag rows means no sizing claim")

    # L7 the gate's lines are imported, not re-declared here
    chk(G.TOP2_SHARE_MAX == 0.70 and G.WORST_YEAR_FLOOR_PP == -15.0,
        "gate lines come from the frozen module")

    print("selftest %d/%d" % (ok, tot))
    for e in errs:
        print("  FAIL:", e)
    return 0 if not errs else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "check", "selftest"])
    ap.add_argument("--quick", action="store_true", help="price 3 rungs instead of 7")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    out = run(QUICK_RUNGS if a.quick else RUNGS)
    print(json.dumps({"answer": out["answer"],
                      "rungs": {r["rung"]: [r["verdict"], r["cagr_pct"],
                                            r["maxdd_pct"], r["vol_realised_pct"]]
                                for r in out["rungs"]},
                      "elapsed_sec": out["elapsed_sec"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())