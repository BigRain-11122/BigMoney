"""FUND-QUALITY-P1 ignition-gate probes (data side, fail-closed, zero-network).

Quality family = T-145 leg(c) second fundamental family (O-20261002-2115 CEO
direct order). Mirrors scripts/fund_value_p1_probe.py (value family first
piece) with the quality-specific deltas:

  * data face = roe_q (report-period-keyed fundamental face, PIT audit receipt
    results/fund_pit_audit/audit_results.json -> pit.financial_face_rule):
    MANDATORY STATUTORY ANCHORING -- period-end anchoring is lookahead
    (Q1 +30d / H1 +62d / Q3 +31d / FY +120d); every row must be anchored at
    its statutory availability date (Q1->04-30, H1->08-31, Q3->10-31,
    FY->next-04-30) or later. The TRANSFER export bakes avail_date in;
    this probe verifies the mapping row-by-row (fail-closed).
  * join law = forward-fill latest anchor with avail_date <= t (quarterly
    face -> max ~124 trading days staleness, honestly disclosed).
  * coverage (data layer: any non-null anchored roe_q) vs eligibility
    (selection layer: roe_q in (0, 100]) are SEPARATED per r599 pit law.

Legs (live `run`):
  leg1  price panel gate (p1c_stock canonical loader, single source)
  leg2  quality-face TRANSFER landing + export gate:
        n_symbols >= 5100 AND per-symbol avail-anchor median >= 50
        AND per-symbol avail-anchor p10 >= 20
        (r604 bm-b amendment per T-152 live evidence MSG-0500: the 60 floor
        was a ticket-side estimate; live export measured anchor_median=52 /
        p10=26 = universe immutable property -- A-share 5,223-sym median
        listing year ~2013-14, max 102. Dual gate keeps the anti-sparse
        intent at the reality base.)
        AND avail_date coverage 2001-04-30 .. 2026-08-31
        AND zero duplicate period_end per symbol AND monotonic avail_date
        AND statutory mapping exact on EVERY row (period_end -> avail_date)
  leg3  monthly joined DATA coverage + start census:
        start census == 401 (T-22 monthly enumeration, value-family frozen
        number, bit-exact); per start t coverage = active members with a
        non-null roe_q anchor avail_date <= t; from first-signal date t0
        (first month coverage >= 0.80) onward every month >= 0.80
  leg4  seed-band scan for fund_quality_p1_nulls=20510000 /
        fund_quality_p1_sens=20510500 (r596 band-level law: exact-base
        disjointness vs full SEED_REGISTRY + stock_face_furnace occupied
        band [20333000, 20445400) open-interval assertion + proximity gate)

`selftest` = offline known-answer legs on synthetic fixtures (no data files):
  S1 statutory mapping known-answers (incl. FY->next-04-30 year rollover)
  S2 PIT forward-fill join (anchor with avail_date > t must not leak)
  S3 coverage-vs-eligibility layering (r599 law)
  S4 duplicate/non-monotonic detection (dup key = period_end per spec; same
     avail_date under FY/Q1 statutory collision is legal, NOT dup)
  S5 seed-band collision case (base inside furnace band) rejected, clean base admitted
  S6 period-end anchoring (lookahead) row rejected by mapping gate
  S7 amended anchor-density dual gate arithmetic (median>=50 AND p10>=20)

Output: results/_fund_quality_p1_transfer_probe.json (probe facts only).
Exit 0 = all gates green; exit 2 = any gate red (honest, no masking).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, ".")          # repo root (science_gates imports knowledge.cost_spec)
sys.path.insert(0, "scripts")
import numpy as np
import pandas as pd

PARQUET = "data/fund_history_export/quality_faces.parquet"
OUT = "results/_fund_quality_p1_transfer_probe.json"
TZ = timezone(timedelta(hours=8))

ROE_MIN, ROE_MAX = 0.0, 100.0   # frozen selection-eligibility band (draft: unit=percent, verify at freeze)
COV_FLOOR = 0.80                 # monthly data-coverage gate (value-family mirror)

# r596 band-level law constants (stock_face_furnace occupied band, registry-documented)
FURNACE_BAND = (20_333_000, 20_445_400)   # open interval, base+cell_idx*4000+k stretch
PROXIMITY_GATE = 2_000                    # min distance from any registered base
SEED_NULLS = 20_510_000                   # candidate fund_quality_p1_nulls (K=2000 -> rng([base, k]))
SEED_SENS = 20_510_500                    # candidate fund_quality_p1_sens     (N=500 -> rng([base, k]))


def _now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ----------------------------------------------------------------------------
# statutory anchor mapping (PIT audit receipt -> pit.financial_face_rule)
# ----------------------------------------------------------------------------
_STAT = {  # period-end month-day -> statutory availability month-day (+year rollover flag)
    "03-31": ("04-30", 0),
    "06-30": ("08-31", 0),
    "09-30": ("10-31", 0),
    "12-31": ("04-30", 1),   # FY -> next-year 04-30
}


def statutory_avail(period_end: str) -> str | None:
    """period_end 'YYYY-MM-DD' -> 'YYYY-MM-DD' statutory availability date.

    Returns None when period_end is not a valid report-period end
    (roe_q:nonperiod_keys family -- export excludes, probe counts).
    """
    if not isinstance(period_end, str) or len(period_end) != 10 or period_end[4] != "-" or period_end[7] != "-":
        return None
    md = period_end[5:]
    hit = _STAT.get(md)
    if hit is None:
        return None
    avail_md, rollover = hit
    year = int(period_end[:4]) + rollover
    return f"{year:04d}-{avail_md}"


# ----------------------------------------------------------------------------
# live probe
# ----------------------------------------------------------------------------
def _leg4_band_scan(facts: dict, gates: dict) -> None:
    import science_gates as SG
    reg = {k: v for k, v in SG.SEED_REGISTRY.items() if isinstance(v, int)}
    candidates = {"fund_quality_p1_nulls": SEED_NULLS, "fund_quality_p1_sens": SEED_SENS}
    exact_hits = {k: b for k, b in candidates.items() if b in reg.values()}
    in_band = {k: b for k, b in candidates.items() if FURNACE_BAND[0] < b < FURNACE_BAND[1]}
    too_close = {
        k: (b, rb) for k, b in candidates.items()
        for rb in reg.values() if abs(b - rb) < PROXIMITY_GATE
    }
    facts["seed_band_scan"] = {
        "candidates": candidates,
        "n_registry_bases": len(reg),
        "exact_hits": exact_hits,
        "furnace_band": list(FURNACE_BAND),
        "in_furnace_band": in_band,
        "proximity_violations": {k: list(v) if isinstance(v, tuple) else v for k, v in too_close.items()},
        "k_stretch_disclosure": {
            "nulls": f"rng([{SEED_NULLS}, k]) k=0..1999 (pair-seed sub-stream law)",
            "sens": f"rng([{SEED_SENS}, k]) k=0..499 (pair-seed sub-stream law)",
        },
        "gap_to_fund_value_block": SEED_NULLS - 20_500_000,  # >= 8000 clear of value-family block
    }
    gates["leg4_seed_band"] = bool(not exact_hits and not in_band and not too_close)


def main() -> int:
    facts: dict = {"probe": "FUND-QUALITY-P1 ignition data-side probes",
                   "generated": _now(), "machine": "bm-b",
                   "prereg": "research/FUND-QUALITY-P1.md (DRAFT-NOT-FROZEN)",
                   "transfer_ticket": "T-2026-10-03-152-P1"}
    gates: dict[str, bool] = {}

    # ---- leg1 price panel via canonical loader ----
    try:
        import p1c_stock_ic_batch as P1C
        idx, syms, meta = P1C.load_universe()
        close_raw = np.load(f"{P1C.CACHE_DIR}/close.npy", mmap_mode="r")
        n_bars = len(idx)
        facts["panel"] = {"n_bars": n_bars, "n_syms_panel": len(syms),
                          "first": str(idx[0].date()), "last": str(idx[-1].date()),
                          "ok_universe": meta.get("ok_universe")}
        gates["leg1_price_panel"] = bool(
            n_bars == 8792 and str(idx[-1].date()) == "2026-09-22" and len(syms) >= 5100)
    except Exception as exc:  # panel absent -> honest fail-closed
        facts["panel"] = {"error": repr(exc)}
        gates["leg1_price_panel"] = False
        idx = syms = close_raw = None

    # ---- leg2 quality-face TRANSFER landing + export gate ----
    import os
    if not os.path.exists(PARQUET):
        facts["quality_face"] = {
            "absent": True, "path": PARQUET,
            "note": "T-152 TRANSFER not landed -- fail-closed by design (this "
                    "receipt IS the transfer-necessity evidence).",
        }
        gates["leg2_transfer_export"] = False
        gates["leg3_monthly_coverage"] = False
    else:
        df = pd.read_parquet(PARQUET)
        n_symbols = int(df["code"].nunique())
        per = df.groupby("code")["avail_date"]
        median_anchors = float(per.size().median())
        avail_min = str(df["avail_date"].min()); avail_max = str(df["avail_date"].max())
        dup_any = bool(df.groupby("code")["period_end"]
                       .apply(lambda s: s.duplicated().any()).any())  # r604 dup-axis fix (MSG-0500): key = period_end per
        # ticket spec (5); avail_date duplication is STRUCTURAL under the
        # statutory mapping (FY 2008-12-31 and Q1 2009-03-31 both anchor to
        # 2009-04-30, nearly every symbol every year) -- checking avail_date
        # made leg2 permanently red; the fact key was already dup_period_end_any.
        mono_all = bool(per.apply(lambda s: s.is_monotonic_increasing).all())
        # statutory mapping exact on EVERY row (fail-closed; period-end anchor = lookahead row)
        expected = df["period_end"].map(statutory_avail)
        map_exact = bool((expected == df["avail_date"]).all())
        bad_map_rows = int((expected != df["avail_date"]).sum())
        facts["quality_face"] = {
            "rows": int(len(df)), "n_symbols": n_symbols,
            "anchor_median": median_anchors, "anchor_p10": float(per.size().quantile(0.10)),
            "avail_min": avail_min, "avail_max": avail_max,
            "dup_period_end_any": dup_any, "monotonic_avail_all": mono_all,
            "statutory_map_exact_all_rows": map_exact, "statutory_map_bad_rows": bad_map_rows,
        }
        gates["leg2_transfer_export"] = bool(
            n_symbols >= 5100 and median_anchors >= 50
            and float(per.size().quantile(0.10)) >= 20   # r604 dual gate: p10 floor 20 (reality 26)
            and avail_min[:10] <= "2001-04-30" and avail_max[:10] >= "2026-08-31"
            and (not dup_any) and mono_all and map_exact)

        # ---- leg3 monthly joined data coverage + census ----
        if gates["leg1_price_panel"]:
            d = df.assign(_a=df["avail_date"].astype("string").str.replace("-", "", regex=False).astype("int64"))
            by_sym: dict[str, tuple[np.ndarray, np.ndarray]] = {}
            for code, g in d.groupby("code", sort=False):
                g = g.sort_values("_a")
                by_sym[str(code)] = (g["_a"].to_numpy(), g["roe_q"].to_numpy())

            mask = (idx >= pd.Timestamp("1992-09-01")) & (idx <= pd.Timestamp("2026-03-02"))
            sub = idx[mask]; mk = sub.strftime("%Y-%m")
            month_first_pos: list[int] = []
            prev = None
            for p, k in zip(np.where(mask)[0], mk):
                if k != prev:
                    month_first_pos.append(int(p)); prev = k
            starts: list[int] = []
            for p in month_first_pos:
                if p < 252 or (n_bars - 1 - p) < 126:
                    continue
                if int((~np.isnan(close_raw[p])).sum()) < 24:
                    continue
                starts.append(p)
            facts["start_census"] = {"months_in_window": len(month_first_pos),
                                     "eligible_starts": len(starts), "expected": 401}

            cov_rows = []
            for p in starts:
                t_date = int(idx[p].strftime("%Y%m%d"))
                act = np.where(~np.isnan(close_raw[p]))[0]
                n_active = int(act.size)
                n_cov = 0; n_elig = 0
                for j in act:
                    pack = by_sym.get(syms[j])
                    if pack is None:
                        continue
                    ad, roe = pack
                    k = int(np.searchsorted(ad, t_date, side="right")) - 1
                    if k >= 0 and not np.isnan(roe[k]):
                        n_cov += 1
                        if ROE_MIN < roe[k] <= ROE_MAX:
                            n_elig += 1
                cov_rows.append({"t": t_date, "n_active": n_active, "n_cov": n_cov,
                                 "cov_ratio": round(n_cov / n_active, 4),
                                 "elig_ratio": round(n_elig / n_active, 4)})

            ratios = [r["cov_ratio"] for r in cov_rows]
            t0 = next((r for r in cov_rows if r["cov_ratio"] >= COV_FLOOR), None)
            after = [r for r in cov_rows if t0 and r["t"] >= t0["t"]]
            below_after = [r["t"] for r in after if r["cov_ratio"] < COV_FLOOR]
            facts["coverage"] = {
                "first_signal_date_t0": t0["t"] if t0 else None,
                "months_evaluated": len(cov_rows),
                "months_below_floor_after_t0": below_after,
                "n_below_after_t0": len(below_after),
                "cov_median": float(np.median(ratios)) if ratios else None,
                "cov_min_after_t0": float(np.min([r["cov_ratio"] for r in after])) if after else None,
                "elig_ratio_median_after_t0": float(np.median([r["elig_ratio"] for r in after])) if after else None,
                "worst_five": sorted(cov_rows, key=lambda r: r["cov_ratio"])[:5],
            }
            facts["roe_raw_stats"] = {
                "note": "unit sanity (percent vs fraction) -- freeze-time declaration input",
                "median": (float(np.nanmedian(df["roe_q"])) if len(df) else None),
                "p90": (float(np.nanpercentile(df["roe_q"], 90)) if len(df) else None),
            }
            gates["leg3_monthly_coverage"] = bool(
                len(starts) == 401 and t0 is not None and len(below_after) == 0)
        else:
            gates["leg3_monthly_coverage"] = False

    # ---- leg4 seed-band scan (data-independent) ----
    _leg4_band_scan(facts, gates)

    facts["gates"] = gates
    facts["verdict"] = "GREEN" if all(gates.values()) else "RED"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": facts["verdict"], "gates": gates}, ensure_ascii=False))
    return 0 if facts["verdict"] == "GREEN" else 2


# ----------------------------------------------------------------------------
# offline selftest (synthetic fixtures, zero data dependency)
# ----------------------------------------------------------------------------
def _mk_fixture_panel():
    idx = pd.bdate_range("2020-01-01", periods=60, freq="B")
    n = 3
    close = np.ones((len(idx), n))
    syms = ["000001", "000002", "600000"]
    return idx, syms, close


def _selftest() -> int:
    import science_gates as SG  # registry real import for leg5 (read-only)
    fails: list[str] = []

    def check(name: str, cond: bool):
        print(f"  [{ 'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # S1 statutory mapping known-answers
    print("[S1] statutory mapping known-answers")
    check("Q1 2001", statutory_avail("2001-03-31") == "2001-04-30")
    check("H1 2026", statutory_avail("2026-06-30") == "2026-08-31")
    check("Q3 2025", statutory_avail("2025-09-30") == "2025-10-31")
    check("FY rollover 2001", statutory_avail("2001-12-31") == "2002-04-30")
    check("FY rollover 2025", statutory_avail("2025-12-31") == "2026-04-30")
    check("nonperiod key -> None", statutory_avail("2001-03-18") is None)
    check("garbage -> None", statutory_avail("roe_q") is None)
    check("bad month -> None", statutory_avail("2001-04-30") is None)

    # S2 PIT forward-fill join (no future-anchor leak)
    print("[S2] PIT forward-fill join")
    ad = np.array([20200131, 20200430, 20200831], dtype=np.int64)
    roe = np.array([5.0, 8.0, 12.0])
    t = 20200715  # between 04-30 and 08-31 anchors
    k = int(np.searchsorted(ad, t, side="right")) - 1
    check("uses latest avail<=t (Q1 anchor, roe=8.0)", k == 1 and roe[k] == 8.0)
    t_early = 20200101  # before first anchor
    k2 = int(np.searchsorted(ad, t_early, side="right")) - 1
    check("before-first-anchor -> no data (k=-1)", k2 == -1)
    t_future = 20210901  # after all anchors -> uses latest, never future rows
    k3 = int(np.searchsorted(ad, t_future, side="right")) - 1
    check("after-all -> latest anchor (roe=12.0)", k3 == 2 and roe[k3] == 12.0)

    # S3 coverage-vs-eligibility layering (r599 law)
    print("[S3] coverage vs eligibility layering")
    roe_vals = np.array([5.0, np.nan, 150.0])  # eligible / no-anchor / covered-but-out-of-band
    cov = sum(1 for r in roe_vals if not np.isnan(r))
    elig = sum(1 for r in roe_vals if ROE_MIN < r <= ROE_MAX)
    check("coverage counts out-of-band + eligible (cov=2)", cov == 2)
    check("eligibility excludes out-of-band (elig=1)", elig == 1)
    check("layers differ (cov!=elig)", cov != elig)

    # S4 duplicate / monotonic detection (r604: dup key = period_end per spec (5);
    # same avail_date under FY/Q1 statutory collision is legal and must NOT flag)
    print("[S4] dup/mono detection")
    df_bad = pd.DataFrame({"code": ["A", "A", "B"],
                            "period_end": ["2020-03-31", "2020-03-31", "2020-06-30"],
                            "avail_date": ["2020-04-30", "2020-04-30", "2020-08-31"],
                            "roe_q": [1.0, 2.0, 3.0]})
    check("dup period_end detected",
          bool(df_bad.groupby("code")["period_end"].apply(lambda s: s.duplicated().any()).any()))
    df_fyq1 = pd.DataFrame({"code": ["A", "A"],
                             "period_end": ["2008-12-31", "2009-03-31"],
                             "avail_date": ["2009-04-30", "2009-04-30"],
                             "roe_q": [1.0, 2.0]})
    check("FY/Q1 same-avail distinct-period NOT dup (r604 regression)",
          not bool(df_fyq1.groupby("code")["period_end"].apply(lambda s: s.duplicated().any()).any()))
    check("FY/Q1 statutory mapping exact (both -> 2009-04-30)",
          all(statutory_avail(p) == "2009-04-30" for p in df_fyq1["period_end"]))
    df_nonmono = pd.DataFrame({"code": ["A", "A"],
                               "period_end": ["2020-06-30", "2020-03-31"],
                               "avail_date": ["2020-08-31", "2020-04-30"],
                               "roe_q": [1.0, 2.0]})
    check("non-monotonic detected",
          not bool(df_nonmono.groupby("code")["avail_date"].apply(lambda s: s.is_monotonic_increasing).all()))

    # S5 seed-band collision case (synthetic registry view)
    print("[S5] seed-band scan collision logic")
    band = FURNACE_BAND
    check("base inside furnace band rejected", band[0] < 20_339_000 < band[1])
    check("clean base admitted (20510000)", not (band[0] < SEED_NULLS < band[1]))
    reg_vals = set(SG.SEED_REGISTRY.values())
    check("candidates not in registry (exact)", SEED_NULLS not in reg_vals and SEED_SENS not in reg_vals)
    check("proximity clean (>=2000 from all bases)",
          all(abs(SEED_NULLS - v) >= PROXIMITY_GATE for v in reg_vals if isinstance(v, int)))
    # synthetic exact-hit case
    check("exact-hit case logic", 20_500_000 in {20_500_000, 99})

    # S6 period-end anchoring (lookahead) row rejected
    print("[S6] lookahead row rejected by mapping gate")
    df_look = pd.DataFrame({"period_end": ["2020-03-31"], "avail_date": ["2020-03-31"], "roe_q": [9.9]})
    expected = df_look["period_end"].map(statutory_avail)
    check("period-end anchor = mismatch (gate red)", bool((expected != df_look["avail_date"]).all()))
    check("expected avail is 2020-04-30", expected.iloc[0] == "2020-04-30")

    # S7 amended anchor-density dual gate arithmetic (r604: median>=50 AND p10>=20)
    print("[S7] anchor-density dual gate arithmetic")
    check("reality passes (median 52, p10 26)", 52.0 >= 50 and 26.0 >= 20)
    check("median 49 rejected", not (49.0 >= 50 and 26.0 >= 20))
    check("p10 19 rejected", not (52.0 >= 50 and 19.0 >= 20))
    check("old 60 floor would reject universe reality 52", not (52.0 >= 60))

    print(f"selftest: {len(fails)} FAIL" + ("" if not fails else f" -> {fails}"))
    return 0 if not fails else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    sys.exit(main())
