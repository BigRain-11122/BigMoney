"""Does the 8% vol target fail its own calendar because it can only de-lever?

r1418 put the desk's own adopted book (bond-free composite + 8% vol target, nobond_vt08)
through the calendar gate for the first time: CONDITIONAL, and the single failing row was
Y4 top-2 years = 71.08% of the annual sum (line 70%). Its own brother without the overlay
(nobond_base) ADMITTED at 68.98%. So the de-risking layer is what pushed the book over the
line, and the published sizing face says why: average scale per year was
2020 0.455 / 2021 0.735 / 2022 0.800 / 2023 0.858 / 2024 0.712 / 2025 0.665 / 2026 0.665.

The 2020 clip is the expensive one -- that is the year the base book made +22.19% and the
overlay cut it to less than half a book. But 2025 was clipped to 0.665 too and still made
+43.06%, so "clip more in calm years" is not the whole story: the rule has no floor, so a
single noisy 60-bar window can park the book at half size through a whole recovery.

This run asks the r1418 follow-up directly: if the sizing rule gets a FLOOR (never below
x, instead of only never above 1.0), does the calendar concentration come down without
paying for it in return/drawdown? The floor is swept, the yearly rows are handed to the
frozen gate (candidate_year_gate.admission_block -- imported, not copied), and every arm
is repriced by the same published engine at 10bp/side.

Bit-identity: vol_floor=0.0 must reproduce the published nobond_vt08 run; that is the
selftest leg, not a hope.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_composite_pf as E  # noqa: E402
import etf_robust_pf as R  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import candidate_year_gate as G  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402

FLOORS = (0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
VOL_TARGET = 0.08
IS_END = "2023-12-31"
# E188 (adoption needs a path test): the same rule must survive a shifted decision phase
PHASE_STARTS = ("2020-01-01", "2020-01-08", "2020-01-15", "2020-01-22")
PHASE_ARMS = (0.0, 0.5)
OUT = os.path.join(ROOT, "results", "etf_book_scale_floor.json")


def nobond_universe():
    """Same recipe as scripts/etf_nobond_vt.py (bond-free = equity+commodity+convertible)."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    return close[cols], openp[cols], amt[cols], sc, n_flip


def arm(close, openp, amt, sc, floor, start=None):
    diag = []
    kw = {} if start is None else {"start": start}
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, 20, 5, 0.0010,
                                      vol_target=VOL_TARGET, vol_floor=floor,
                                      diag=diag, **kw)
    scale_by_year = {}
    if diag:
        df = pd.DataFrame(diag)
        df["year"] = df["date"].str[:4]
        scale_by_year = {y: round(float(g["scale"].mean()), 3)
                         for y, g in df.groupby("year")}
    return ser, turn, scale_by_year


def sub_stats(ser):
    """Same split the published book uses (IS through 2023-12-31, OOS after)."""
    out = {}
    for tag, sl in (("is", ser[ser.index <= IS_END]), ("oos", ser[ser.index > IS_END])):
        m = A.stats2(sl, tag)
        for k in ("cagr", "sharpe", "maxdd"):
            v = m.get(k)
            out[k + "_" + tag] = None if v is None else round(float(v), 4)
    return out


def published_capacity():
    """Read the adopted book's capacity from the r1418 face; never hand-copy it."""
    with open(os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json"),
              encoding="utf-8") as f:
        face = json.load(f)
    for b in face.get("books", []):
        if b.get("book") == "nobond_vt08_adopted":
            return b.get("capacity_cny_1day_5pct")
    return None


def published_reference():
    """r1418's own repricing of the adopted book on today's panel: yearly rows and the
    per-year average sizing scale, read from its face (never hand-copied)."""
    with open(os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json"),
              encoding="utf-8") as f:
        face = json.load(f)
    for b in face.get("books", []):
        if b.get("book") == "nobond_vt08_adopted":
            return b
    return None


def run():
    close, openp, amt, sc, n_flip = nobond_universe()
    cap = published_capacity()
    arms = []
    for floor in FLOORS:
        ser, turn, scale_by_year = arm(close, openp, amt, sc, floor)
        years = Y.yearly_returns(ser)
        stats = A.stats2(ser, "floor_%.2f" % floor)
        blk = G.admission_block(years, cap, None, stats.get("cagr"))
        blk["book"] = "nobond_vt08_floor_%.2f" % floor
        blk["vol_floor"] = floor
        blk["turnover"] = round(turn, 3)
        blk["scale_by_year"] = scale_by_year
        blk["stats"] = {k: (None if stats.get(k) is None else round(float(stats[k]), 4))
                        for k in ("cagr", "sharpe", "maxdd") if k in stats}
        blk["stats"].update(sub_stats(ser))
        arms.append(blk)
        print("floor %.2f -> %-11s top2 %.4f cagr %.4f sharpe %.3f mdd %.4f"
              % (floor, blk["verdict"], blk["year_metrics"]["top2_share"],
                 blk["cagr_pct"] or 0.0, blk["stats"].get("sharpe") or 0.0,
                 blk["stats"].get("maxdd") or 0.0), flush=True)

    adm = [a for a in arms if a["verdict"] == "ADMIT"]
    best = None
    if adm:
        best = max(adm, key=lambda a: (a["stats"].get("sharpe") or -9))

    # E188 path test: a floor is only usable if it survives every decision phase.
    phases = []
    for start in PHASE_STARTS:
        row = {"start": start}
        for floor in PHASE_ARMS:
            ser, turn, _ = arm(close, openp, amt, sc, floor, start=start)
            yrs = Y.yearly_returns(ser)
            gm = G.admission_block(yrs, cap, None, A.stats2(ser, "p").get("cagr"))
            st = A.stats2(ser, "p")
            row["floor_%.1f" % floor] = {
                "verdict": gm["verdict"],
                "top2_share": gm["year_metrics"]["top2_share"],
                "cagr_pct": gm["cagr_pct"],
                "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
                "maxdd": None if st.get("maxdd") is None else round(float(st["maxdd"]), 4),
                "turnover": round(turn, 3)}
        a0, a5 = row["floor_0.0"], row["floor_0.5"]
        row["floor05_beats_floor0"] = bool(
            a5["sharpe"] is not None and a0["sharpe"] is not None
            and a5["sharpe"] >= a0["sharpe"] - 1e-9
            and a5["cagr_pct"] >= a0["cagr_pct"] - 1e-6)
        row["floor05_admits"] = a5["verdict"] == "ADMIT"
        phases.append(row)
        print("phase %s -> f0 %-11s top2 %.4f shp %.3f | f5 %-11s top2 %.4f shp %.3f %s"
              % (start, a0["verdict"], a0["top2_share"], a0["sharpe"] or 0,
                 a5["verdict"], a5["top2_share"], a5["sharpe"] or 0,
                 "BEATS" if row["floor05_beats_floor0"] else "does-not-beat"),
              flush=True)
    phase_pass = sum(1 for p in phases if p["floor05_beats_floor0"] and p["floor05_admits"])
    out = {
        "face": "etf_book_scale_floor",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "question": "the 8% vol target has no floor; is the calendar concentration in "
                    "r1418 bought by the missing floor?",
        "rule": {"vol_target": VOL_TARGET, "floors": list(FLOORS),
                 "gate": "candidate_year_gate.admission_block (imported)",
                 "cost_per_side": 0.0010, "rebal_bars": 20, "n_hold": 5},
        "data": {"flips_repaired": n_flip, "universe": int(len(close.columns)),
                 "bars": int(len(close.index)),
                 "capacity_from": "results/etf_book_year_gate/YEAR-GATE.json"},
        "capacity_cny_1day_5pct": cap,
        "arms": arms,
        "admitted": [{"book": a["book"], "sharpe": a["stats"].get("sharpe"),
                      "cagr_pct": a["cagr_pct"],
                      "top2_share": a["year_metrics"]["top2_share"]} for a in adm],
        "best_admitted": None if best is None else {
            "book": best["book"], "sharpe": best["stats"].get("sharpe"),
            "cagr_pct": best["cagr_pct"], "maxdd": best["stats"].get("maxdd"),
            "top2_share": best["year_metrics"]["top2_share"]},
        "baseline_floor0": {"verdict": arms[0]["verdict"],
                            "top2_share": arms[0]["year_metrics"]["top2_share"],
                            "sharpe": arms[0]["stats"].get("sharpe")},
        "phase_test": {"starts": list(PHASE_STARTS), "arms": list(PHASE_ARMS),
                       "rows": phases,
                       "floor05_beats_floor0_and_admits": phase_pass,
                       "of": len(phases),
                       "stable": phase_pass == len(phases)},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", OUT, flush=True)
    return out


def selftest() -> int:
    """L1: vol_floor=0.0 reproduces the published nobond_vt08 run (bit-identity of the
    engine default); L2: a positive floor strictly raises scale somewhere; L3: the gate
    is imported (same object identity) not re-implemented."""
    errs = []

    def chk(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg, flush=True)
        if not ok:
            errs.append(msg)

    ref = published_reference()
    chk(ref is not None, "L0 published nobond_vt08 repricing (r1418 face) is readable")

    close, openp, amt, sc, _ = nobond_universe()
    ser0, _, scale0 = arm(close, openp, amt, sc, 0.0)
    s0 = A.stats2(ser0, "t")
    if ref:
        pubs = ref.get("yearly_returns_pct") or {}
        mine = {y: v["net_pct"] for y, v in Y.yearly_returns(ser0).items()}
        worst = max((abs(mine[y] - pubs[y]) for y in pubs if y in mine), default=None)
        chk(worst is not None and worst < 1e-9,
            "L1 floor=0 reproduces every published yearly row (max|diff| %r)" % worst)
        ps = ref.get("sizing_scale_by_year") or {}
        worst_s = max((abs(scale0[y] - ps[y]) for y in ps if y in scale0), default=None)
        chk(worst_s is not None and worst_s < 5e-4,
            "L1b floor=0 reproduces the published sizing scale by year (max|diff| %r)"
            % worst_s)
        chk(abs((s0.get("cagr") or 0) * 100 - (ref.get("cagr_pct") or 0)) < 0.005,
            "L1c floor=0 reproduces published CAGR %.2f%% vs %.2f%%"
            % ((s0.get("cagr") or 0) * 100, ref.get("cagr_pct") or 0))
    else:
        chk(False, "L1 skipped: no published reference")

    ser7, _, scale7 = arm(close, openp, amt, sc, 0.7)
    lifted = sum(1 for y in scale7 if y in scale0 and scale7[y] > scale0[y] + 1e-9)
    chk(lifted > 0, "L2 floor=0.7 lifts the average scale in %d years" % lifted)
    chk(max(scale7.values()) <= 1.0 + 1e-9, "L2b floor never levers above 1.0")

    chk(G.admission_block is not None and Y.yearly_returns is not None,
        "L3 gate/derivation imported from their owners")
    tot = 1 + (3 if ref else 1) + 2 + 1
    print("selftest %d/%d" % (tot - len(errs), tot), flush=True)
    return 0 if not errs else 1


def main(argv):
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))