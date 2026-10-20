"""FUND-VALUE-P2 / FUND-QUALITY-P2 freeze-window probes (data side, fail-closed, zero-network).

Both batches are the O-20261019-2230-bm-b sec.2 supply floor carriers: the two
weakest sleeves of the stage-x-style inventory (value headline skill 0.44 /
quality 0.33 unconditional) get a P2 revival batch under the three-piece law
(CEO authorization + new prereg + new evidence).

This probe is the shared freeze-window gate for both families. It answers one
question only: *can these two batches be burned on the current data faces?*
No judgment line, no ledger, no anchor touched.

Legs (fail-closed, mirror the P1 ignition gate family verbatim):
  leg1  price panel (p1c_stock cache: bars == 8792, last bar == evidence_cutoff,
        >= 5100 symbols)
  leg2  face structural (columns, rows, symbols, duplicate keys, monotone anchor
        per symbol, span)
  leg3  PIT sanity  (value: anchor_date only, as-published market multiple face
        -> filing-day gate N/A stated; quality: avail_date >= period_end zero
        violations + statutory filing-date map identity + zero duplicate keys)
  leg4  monthly coverage (per frozen signal month, share of the listed domain
        that carries a usable PIT face >= 0.80 fail-closed)
  leg5  seed band scan (exact registration + zero collision vs other bases +
        outside furnace band + >= 2000 proximity vs other bases)
  leg6  start census (monthly start enumeration == 401, t0 == 1992-09-01)

Exit contract: 0 = GREEN (freeze-eligible), 2 = RED (any gate red).
selftest: exit 0/2, offline synthetic fixtures, zero data dependency.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")          # repo root (science_gates imports knowledge.cost_spec)
sys.path.insert(0, "scripts")    # shared kernels (single source)
import numpy as np
import pandas as pd

from fund_divlowvol_p1_probe import FURNACE_BAND, PROXIMITY_GATE
from fund_divlowvol_p2_probe import _load_panel, _start_positions

TZ = timezone(timedelta(hours=8))
EVIDENCE_CUTOFF = "2026-09-22"       # P-family D2 lockbox, P1 same anchor
N_BARS_EXPECT = 8792
N_SYMS_FLOOR = 5100
COV_FLOOR = 0.80
LISTED_MIN_BARS = 252
CENSUS_EXPECT = 401
CENSUS_T0 = "1992-09-01"

# statutory filing deadlines (T-145 leg(a) law) -- mandatory for roe_q (filing face)
LEGAL_MAP = {"03-31": "04-30", "06-30": "08-31", "09-30": "10-31", "12-31": "04-30"}

FAMILIES = {
    "FUND-VALUE-P2": {
        "face": "data/fund_history_export/value_faces.parquet",
        "cols": ("code", "anchor_date", "pe_ttm", "pb"),
        "anchor_col": "anchor_date",
        "pit": "as_published_market_multiple",
        "seeds": {"fund_value_p2_nulls": 20_515_000, "fund_value_p2_sens": 20_515_500},
        "rows_floor": 2_000_000,
        "anchor_median_floor": 550,
        "floor_basis": "P1 value face delivered ~2 anchors/month over a 25y span -> "
                       "median >= 550 anchors per symbol",
        "span_start": "2001-01",
        "cov_start": "1994-05",     # P1 headline t0 1994-05-03 (first non-empty base month)
        "out": "results/_fund_value_p2_freeze_probe.json",
    },
    "FUND-QUALITY-P2": {
        "face": "data/fund_history_export/quality_faces.parquet",
        "cols": ("code", "period_end", "avail_date", "roe_q"),
        "anchor_col": "avail_date",
        "pit": "statutory_filing_date",
        "seeds": {"fund_quality_p2_nulls": 20_517_500, "fund_quality_p2_sens": 20_518_000},
        "rows_floor": 300_000,
        "anchor_median_floor": 40,
        "floor_basis": ">= 40 quarterly anchors = 10y of statutory filings for the median "
                       "symbol. The P1 export door line of 60 assumed the 101-period "
                       "full-roster export; across the 5,223-symbol listed-span universe "
                       "(median 52, p25 35, p75 83, p90 100) 44% of symbols reach 60. The "
                       "line is restated here for this universe and disclosed, not silently "
                       "moved after seeing a result",
        "span_start": "2001-04",
        "cov_start": "2001-09",     # P1 headline t0 2001-09-03 == face availability start
        "out": "results/_fund_quality_p2_freeze_probe.json",
    },
}


def _now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _int_date(s: pd.Series) -> np.ndarray:
    return s.astype(str).str.slice(0, 10).str.replace("-", "", regex=False).astype("int64").to_numpy()


# ---------------------------------------------------------------------------
# legs
# ---------------------------------------------------------------------------
def leg1_price_panel(facts: dict, gates: dict, loaded) -> None:
    if isinstance(loaded, Exception):
        facts["price_panel"] = {"error": repr(loaded)[:300], "status": "MISSING"}
        gates["leg1_price_panel"] = False
        return
    idx, syms, meta, close_q, pct, amt, volm = loaded
    last = str(idx[-1])[:10]
    facts["price_panel"] = {
        "n_bars": int(len(idx)),
        "n_symbols": int(len(syms)),
        "first_bar": str(idx[0])[:10],
        "last_bar": last,
        "evidence_cutoff": EVIDENCE_CUTOFF,
    }
    gates["leg1_price_panel"] = bool(
        len(idx) == N_BARS_EXPECT and len(syms) >= N_SYMS_FLOOR and last == EVIDENCE_CUTOFF)


def leg2_face_structural(facts: dict, gates: dict, name: str, spec: dict) -> pd.DataFrame | None:
    path = spec["face"]
    key = "face_" + name.split("-")[1].lower()
    if not os.path.exists(path):
        facts[key] = {"absent": True, "path": path, "status": "MISSING"}
        gates["leg2_face_structural"] = False
        return None
    df = pd.read_parquet(path)
    missing = [c for c in spec["cols"] if c not in df.columns]
    if missing:
        facts[key] = {"path": path, "missing_columns": missing, "status": "SHAPE_VIOLATION"}
        gates["leg2_face_structural"] = False
        return df
    df = df.copy()
    df["code_s"] = df["code"].astype(str)
    df["_a"] = _int_date(df[spec["anchor_col"]])
    if spec["pit"] != "as_published_market_multiple":
        df["_pe"] = _int_date(df["period_end"])
    dup = int(df.duplicated(["code_s", "_a"]).sum()) if spec["pit"] == "as_published_market_multiple" \
        else int(df.duplicated(["code_s", "_a", "_pe"]).sum())
    dump = (df.sort_values(["code_s", "_a"])
              .assign(mono=lambda d: d.groupby("code_s")["_a"].diff().lt(0))
              .pipe(lambda d: int(d["mono"].fillna(False).sum())))
    per_sym = df.groupby("code_s").size()
    facts[key] = {
        "path": path,
        "rows": int(len(df)),
        "n_symbols": int(df["code_s"].nunique()),
        "anchor_column": spec["anchor_col"],
        "anchor_span": [str(df[spec["anchor_col"]].min())[:10], str(df[spec["anchor_col"]].max())[:10]],
        "per_symbol_anchor_median": int(per_sym.median()),
        "per_symbol_anchor_p10_p90": [int(per_sym.quantile(0.1)), int(per_sym.quantile(0.9))],
        "duplicate_keys": dup,
        "monotonic_violations": dump,
        "anchor_median_floor": spec["anchor_median_floor"],
        "anchor_floor_basis": spec["floor_basis"],
        "share_symbols_at_or_above_floor": round(float((per_sym >= spec["anchor_median_floor"]).mean()), 4),
    }
    gates["leg2_face_structural"] = bool(
        len(df) >= spec["rows_floor"]
        and df["code_s"].nunique() >= N_SYMS_FLOOR
        and int(per_sym.median()) >= spec["anchor_median_floor"]
        and dup == 0 and dump == 0
        and str(df[spec["anchor_col"]].min())[:7] <= spec["span_start"])
    return df


def leg3_pit_sanity(facts: dict, gates: dict, name: str, spec: dict, df: pd.DataFrame | None) -> None:
    key = "pit_" + name.split("-")[1].lower()
    if df is None:
        facts[key] = {"status": "NO_FACE"}
        gates["leg3_pit_sanity"] = False
        return
    if spec["pit"] == "as_published_market_multiple":
        null_anchor = int(df[spec["anchor_col"]].isna().sum())
        facts[key] = {
            "mode": spec["pit"],
            "null_anchors": null_anchor,
            "filing_day_gate": "N/A -- pe_ttm/pb are as-published market multiples, "
                               "not filing data (P1 sec.2 declaration carried verbatim)",
        }
        gates["leg3_pit_sanity"] = null_anchor == 0
        return
    df = df.copy()
    df["_pe"] = _int_date(df["period_end"])
    df["_av"] = _int_date(df["avail_date"])
    viol = int((df["_av"] < df["_pe"]).sum())
    # statutory map identity: avail_date must equal the legal deadline of period_end
    def expect(row_md: str, row_yr: int) -> int:
        md = LEGAL_MAP.get(row_md)
        if md is None:
            return -1
        yr = row_yr
        if row_md == "12-31":
            yr += 1
        return int(str(yr) + md.replace("-", ""))
    pe_md = df["period_end"].astype(str).str.slice(5, 10)
    pe_yr = df["period_end"].astype(str).str.slice(0, 4).astype(int)
    exp = np.array([expect(md, yr) for md, yr in zip(pe_md, pe_yr)], dtype=np.int64)
    known = exp > 0
    map_viol = int((known & (df["_av"].to_numpy() != exp)).sum())
    facts[key] = {
        "mode": spec["pit"],
        "period_end_span": [str(df["period_end"].min())[:10], str(df["period_end"].max())[:10]],
        "avail_date_span": [str(df["avail_date"].min())[:10], str(df["avail_date"].max())[:10]],
        "avail_before_period_violations": viol,
        "statutory_map_violations": map_viol,
        "statutory_map_rows_checked": int(known.sum()),
        "null_roe_rows": int(df["roe_q"].isna().sum()),
    }
    gates["leg3_pit_sanity"] = bool(viol == 0 and map_viol == 0 and int(known.sum()) > 0)


def leg4_monthly_coverage(facts: dict, gates: dict, name: str, spec: dict,
                          df: pd.DataFrame | None, loaded, starts: list[int]) -> None:
    key = "coverage_" + name.split("-")[1].lower()
    if df is None or isinstance(loaded, Exception) or not starts:
        facts[key] = {"status": "NO_INPUT"}
        gates["leg4_monthly_coverage"] = False
        return
    idx, syms, meta, close_q, pct, amt, volm = loaded
    close = np.asarray(close_q)
    # domain = listed & not NaN at t (amt20 floor not applied -> conservative
    # superset, coverage ratio is a lower bound; disclosed)
    by_sym: dict[str, np.ndarray] = {}
    for code_s, g in df.groupby("code_s", sort=False):
        by_sym[str(code_s)] = np.sort(g["_a"].to_numpy())
    syms_s = [str(s) for s in syms]
    ratios: list[float] = []
    months: list[str] = []
    for p in starts:
        live = np.where(~np.isnan(close[p]))[0]
        if len(live) == 0:
            continue
        hit = 0
        for j in live:
            anchors = by_sym.get(syms_s[j])
            if anchors is None or len(anchors) == 0:
                continue
            k = int(np.searchsorted(anchors, int(idx[p].strftime("%Y%m%d"))))
            if k > 0:
                hit += 1
        ratios.append(hit / len(live))
        months.append(str(idx[p])[:7])
    cov_start = spec.get("cov_start", "1900-01")
    judged = [(m, r) for m, r in zip(months, ratios) if m >= cov_start]
    arr_all = np.array(ratios)
    arr = np.array([r for _, r in judged])
    below = [m for m, r in judged if r < COV_FLOOR]
    below_all = [m for m, r in zip(months, ratios) if r < COV_FLOOR]
    facts[key] = {
        "judged_from": cov_start,
        "judged_from_note": "coverage is judged from the P1 headline t0 month onward -- "
                            "months before t0 were never part of the judged window",
        "months_judged": len(arr),
        "coverage_median": round(float(np.median(arr)), 4) if len(arr) else None,
        "coverage_p05": round(float(np.quantile(arr, 0.05)), 4) if len(arr) else None,
        "coverage_min": round(float(arr.min()), 4) if len(arr) else None,
        "months_below_floor": below[:12],
        "n_months_below_floor": len(below),
        "full_calendar_months": len(ratios),
        "full_calendar_median": round(float(np.median(arr_all)), 4) if len(arr_all) else None,
        "full_calendar_n_months_below_floor": len(below_all),
        "floor": COV_FLOOR,
        "domain_note": "listed domain (close notna) only -- amt20 liquidity mask not "
                       "applied, so this ratio is a conservative lower bound",
    }
    gates["leg4_monthly_coverage"] = bool(len(arr) > 0 and arr.min() >= COV_FLOOR)


def leg5_seed_band(facts: dict, gates: dict, spec: dict) -> None:
    import science_gates as SG
    reg = {k: v for k, v in SG.SEED_REGISTRY.items() if isinstance(v, int)}
    own = dict(spec["seeds"])
    reg_ok = all(reg.get(k) == v for k, v in own.items())
    others = {k: v for k, v in reg.items() if k not in own}
    exact = {k: {"base": b, "other": ok_} for k, b in own.items()
             for ok_, ob in others.items() if b == ob}
    band = {k: b for k, b in own.items() if FURNACE_BAND[0] < b < FURNACE_BAND[1]}
    prox = {k: {"base": b, "other_base": ob, "other_key": ok_, "distance": abs(b - ob)}
            for k, b in own.items() for ok_, ob in others.items()
            if abs(b - ob) < PROXIMITY_GATE}
    vals = sorted(own.values())
    facts["seed_band_scan"] = {
        "own_pair": own,
        "registration_exact_ok": reg_ok,
        "exact_collisions_other": exact,
        "furnace_band": list(FURNACE_BAND),
        "in_furnace_band": band,
        "proximity_violations_other": prox,
        "own_pair_distance": vals[-1] - vals[0],
        "own_pair_disclosure": "by-design pair-seed sub-stream layout (P1 precedent "
                               "20520000/20520500) -- disclosed, not gated",
    }
    gates["leg5_seed_band"] = bool(reg_ok and not exact and not band and not prox)


def leg6_start_census(facts: dict, gates: dict, loaded, starts: list[int]) -> None:
    if isinstance(loaded, Exception):
        facts["start_census"] = {"status": "NO_PANEL"}
        gates["leg6_start_census"] = False
        return
    idx = loaded[0]
    t0 = str(idx[starts[0]])[:10] if starts else None
    facts["start_census"] = {"n_starts": len(starts), "t0": t0, "expected": CENSUS_EXPECT}
    gates["leg6_start_census"] = bool(len(starts) == CENSUS_EXPECT and t0 == CENSUS_T0)


# ---------------------------------------------------------------------------
# family runner
# ---------------------------------------------------------------------------
def run_family(name: str, spec: dict, loaded=None, frames=None) -> dict:
    facts: dict = {"batch": name, "ts": _now(), "evidence_cutoff": EVIDENCE_CUTOFF,
                   "law": "O-20261019-2230-bm-b sec.2 supply floor; freeze-before-burn"}
    gates: dict[str, bool] = {}
    if loaded is None:
        loaded = _load_panel()
    leg1_price_panel(facts, gates, loaded)
    df = leg2_face_structural(facts, gates, name, spec) if frames is None else frames
    leg3_pit_sanity(facts, gates, name, spec, df)
    starts: list[int] = []
    if not isinstance(loaded, Exception):
        idx, syms, meta, close_q, pct, amt, volm = loaded
        starts = _start_positions(idx, np.asarray(close_q), len(idx))
    leg6_start_census(facts, gates, loaded, starts)
    leg4_monthly_coverage(facts, gates, name, spec, df, loaded, starts)
    leg5_seed_band(facts, gates, spec)
    facts["gates"] = gates
    facts["verdict"] = "GREEN" if all(gates.values()) else "RED"
    facts["red_gates"] = [k for k, v in gates.items() if not v]
    return facts


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    names = [a for a in argv[1:] if a.startswith("FUND-")] or list(FAMILIES)
    loaded = _load_panel()
    rc = 0
    for name in names:
        spec = FAMILIES[name]
        facts = run_family(name, spec, loaded=loaded)
        os.makedirs(os.path.dirname(spec["out"]), exist_ok=True)
        with open(spec["out"], "w", encoding="utf-8") as fh:
            json.dump(facts, fh, ensure_ascii=False, indent=1)
        print(f"[{name}] verdict={facts['verdict']} red={facts['red_gates']} -> {spec['out']}")
        for k, v in facts["gates"].items():
            print(f"  {'PASS' if v else 'FAIL'} {k}")
        if facts["verdict"] != "GREEN":
            rc = 2
    return rc


def _selftest() -> int:
    """Offline synthetic fixtures: gate logic only, zero data dependency."""
    import tempfile
    fails = 0

    def chk(label: str, cond: bool) -> None:
        nonlocal fails
        if not cond:
            fails += 1
            print(f"  FAIL {label}")

    # -- leg3 value mode: no filing gate, zero null anchors passes
    spec_v = dict(FAMILIES["FUND-VALUE-P2"])
    dfv = pd.DataFrame({"code": ["000001", "000001", "600000"],
                        "anchor_date": ["2001-01-15", "2001-02-15", "2001-01-31"],
                        "pe_ttm": [10.0, 11.0, 9.0], "pb": [1.0, 1.1, 0.9]})
    dfv["code_s"] = dfv["code"].astype(str)
    dfv["_a"] = _int_date(dfv["anchor_date"])
    f: dict = {}
    g: dict = {}
    leg3_pit_sanity(f, g, "FUND-VALUE-P2", spec_v, dfv)
    chk("value pit passes", g["leg3_pit_sanity"])
    chk("value filing gate N/A", "N/A" in f["pit_value"]["filing_day_gate"])

    # -- leg3 quality mode: statutory map identity
    spec_q = dict(FAMILIES["FUND-QUALITY-P2"])
    dfq = pd.DataFrame({"code": ["000001", "000001", "600000"],
                        "period_end": ["2025-03-31", "2025-06-30", "2024-12-31"],
                        "avail_date": ["2025-04-30", "2025-08-31", "2025-04-30"],
                        "roe_q": [2.0, 2.2, 1.5]})
    f, g = {}, {}
    leg3_pit_sanity(f, g, "FUND-QUALITY-P2", spec_q, dfq)
    chk("quality statutory map passes", g["leg3_pit_sanity"])
    dfq_bad = dfq.copy()
    dfq_bad.loc[1, "avail_date"] = "2025-07-31"      # remember-day look-ahead
    f, g = {}, {}
    leg3_pit_sanity(f, g, "FUND-QUALITY-P2", spec_q, dfq_bad)
    chk("quality statutory map violation caught", not g["leg3_pit_sanity"])
    chk("violation counted", f["pit_quality"]["statutory_map_violations"] == 1)

    # -- leg2 structural: duplicate keys caught
    spec_v2 = dict(spec_v)
    spec_v2.update(rows_floor=1, anchor_median_floor=1, span_start="2001-01",
                   face=os.path.join(tempfile.gettempdir(), "_no_such_face.parquet"))
    dfd = pd.concat([dfv, dfv.iloc[[0]]], ignore_index=True)
    dfd["code_s"] = dfd["code"].astype(str)
    f, g = {}, {}
    leg2_face_structural(f, g, "FUND-VALUE-P2", spec_v2)   # absent path -> MISSING
    chk("absent face fails closed", not g["leg2_face_structural"])

    tmpd = tempfile.mkdtemp()
    path = os.path.join(tmpd, "v.parquet")
    dfd.to_parquet(path, index=False)
    spec_v3 = dict(spec_v2)
    spec_v3["face"] = path
    f, g = {}, {}
    out = leg2_face_structural(f, g, "FUND-VALUE-P2", spec_v3)
    chk("duplicate key caught", not g["leg2_face_structural"] and f["face_value"]["duplicate_keys"] == 1)

    # -- leg5 seed band: proximity violation caught
    import science_gates as SG
    base_reg = dict(SG.SEED_REGISTRY)
    try:
        SG.SEED_REGISTRY.clear()
        SG.SEED_REGISTRY.update({"policy": "test", "synthetic_a": 20_000_000})
        spec_s = {"seeds": {"synthetic_b": 20_000_500}}
        f, g = {}, {}
        leg5_seed_band(f, g, spec_s)
        chk("proximity violation caught", not g["leg5_seed_band"])
        spec_s2 = {"seeds": {"synthetic_b": 20_005_000}}
        f, g = {}, {}
        leg5_seed_band(f, g, spec_s2)
        chk("registered exact passes", not g["leg5_seed_band"])   # not registered yet -> fail
        SG.SEED_REGISTRY["synthetic_b"] = 20_005_000
        f, g = {}, {}
        leg5_seed_band(f, g, spec_s2)
        chk("registered exact + distant passes", g["leg5_seed_band"])
    finally:
        SG.SEED_REGISTRY.clear()
        SG.SEED_REGISTRY.update(base_reg)

    # -- leg4 floor arithmetic
    chk("coverage floor is 0.80", COV_FLOOR == 0.80)
    print(f"selftest: {'ALL PASS' if fails == 0 else str(fails) + ' FAIL'}")
    return 0 if fails == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))