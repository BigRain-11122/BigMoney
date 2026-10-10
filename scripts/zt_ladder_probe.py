#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E10 zt ladder relay playstyle structure probe (P3 explore head, r952 bm-a).

Data face: data/zt_pool/ four-panel forward archive (zt/zbgc/dtgc/strong,
O-20261001-2103, FIRST_DATE 2026-10-08 forward-accumulation law).

Probe faces (descriptive only, zero judgment, zero criteria):
  F1 per-day structure: four-face counts, ladder histogram (lianban), ladder top,
     seal-fund median, intra-day blown counts, high-board (>=2) sector concentration
  F2 day-over-day transition: promoted / blown_next / gone / reboard, promotion
     rate by ladder level (k -> k+1 survival face)
  F3 four-face linkage: strong-pool x zt overlap per day (relay continuation candidates)
  F4 era-context: P6 thermo (results/regime_thermo/thermo_daily.csv, 31y daily
     max_height/n_lianban4p) era-band medians vs forward-panel ladder top --
     era-stratified supply reference per O-20260928-1522 domestic-playstyle law
     (thermo cutoff 2026-09-22 P-5C frozen; forward panel 10-08+ -> zero overlap,
     reference-only, not a same-day join).

Honest disclosure: forward panel has few days (>=1); transition windows =
consecutive-day pairs count; all faces carry the day-count denominator.
Exit: 0 normal / 2 mechanism failure. Selftest hermetic pure-function legs.
"""
import argparse
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "zt_pool")
THERMO = os.path.join(ROOT, "results", "regime_thermo", "thermo_daily.csv")
OUT = os.path.join(ROOT, "results", "shortline", "zt_ladder_probe.json")

ERA_BANDS = [(1996, 2005), (2006, 2015), (2016, 2020), (2021, 2026)]


def _grp(df, day):
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=df.columns if df is not None else [])
    return df[df["日期"] == day]


def _codes(df):
    if df is None or len(df) == 0:
        return set()
    return set(df["代码"].astype(str))


def build_perday_faces(zt, zbgc, dtgc, strong, day):
    """F1+F3: single-day structure faces. All pure, no I/O."""
    ztd = _grp(zt, day)
    ladder = {}
    if len(ztd) and "连板数" in ztd.columns:
        vc = ztd["连板数"].value_counts()
        ladder = {str(int(k)): int(v) for k, v in vc.items()}
    top = int(ztd["连板数"].max()) if len(ztd) and "连板数" in ztd.columns else 0
    top_codes = []
    if len(ztd) and "连板数" in ztd.columns:
        tdf = ztd[ztd["连板数"] == top]
        top_codes = [
            {"代码": str(r["代码"]), "名称": str(r.get("名称", "")), "连板数": top}
            for _, r in tdf.iterrows()
        ][:8]
    fund = None
    if len(ztd) and "封板资金" in ztd.columns:
        s = pd.to_numeric(ztd["封板资金"], errors="coerce").dropna()
        fund = float(s.median()) if len(s) else None
    blown = None
    if len(ztd) and "炸板次数" in ztd.columns:
        s = pd.to_numeric(ztd["炸板次数"], errors="coerce").dropna()
        blown = {"mean": float(s.mean()) if len(s) else None,
                 "n_zero_blow": int((s == 0).sum()), "n_rows": int(len(s))}
    sector = {}
    if len(ztd) and "连板数" in ztd.columns and "所属行业" in ztd.columns:
        hb = ztd[ztd["连板数"] >= 2]
        vc = hb["所属行业"].value_counts()
        sector = {str(k): int(v) for k, v in vc.head(5).items()}
        sector["_n_highboard_rows"] = int(len(hb))
    zt_codes = _codes(ztd)
    strong_codes = _codes(_grp(strong, day))
    return {
        "day": day,
        "n_zt": int(len(ztd)),
        "n_zbgc": int(len(_grp(zbgc, day))),
        "n_dtgc": int(len(_grp(dtgc, day))),
        "n_strong": int(len(_grp(strong, day))),
        "ladder_histogram": ladder,
        "ladder_top": top,
        "ladder_top_codes": top_codes,
        "seal_fund_median": fund,
        "intraday_blow": blown,
        "highboard_sector_top5": sector,
        "strong_x_zt_overlap": int(len(zt_codes & strong_codes)),
    }


def build_transition(zt, zbgc, strong, day1, day2):
    """F2: one consecutive-day transition window. k->k+1 promotion face."""
    d1 = _grp(zt, day1)
    d2 = _grp(zt, day2)
    b2 = _grp(zbgc, day2)
    s2 = _grp(strong, day2)
    zt2 = _codes(d2)
    zbgc2 = _codes(b2)
    strong2 = _codes(s2)
    res = {"window": [day1, day2],
           "n_zt_d1": int(len(d1)),
           "promoted": [], "blown_next": [], "gone": [], "recount_anomaly": [],
           "promotion_by_level": {},
           "reboard_zbgc_to_zt": int(len(_codes(_grp(zbgc, day1)) & zt2))}
    level = {}
    for _, r in d1.iterrows():
        code, k = str(r["代码"]), int(r["连板数"])
        if code in zt2:
            row2 = d2[d2["代码"].astype(str) == code].iloc[0]
            k2 = int(row2["连板数"])
            if k2 == k + 1:
                res["promoted"].append({"代码": code, "名称": str(r.get("名称", "")), "k": k, "k2": k2})
                level.setdefault(k, [0, 0])
                level[k][0] += 1
            else:
                res["recount_anomaly"].append({"代码": code, "k": k, "k2": k2})
        elif code in zbgc2:
            res["blown_next"].append({"代码": code, "k": k})
        else:
            g = {"代码": code, "k": k, "in_strong_next": code in strong2}
            res["gone"].append(g)
        level.setdefault(k, [0, 0])
        level[k][1] += 1
    res["promotion_by_level"] = {
        str(k): {"n_at_k": v[1], "n_promoted": v[0],
                 "rate": (v[0] / v[1]) if v[1] else None}
        for k, v in sorted(level.items())}
    for key in ("promoted", "blown_next", "gone", "recount_anomaly"):
        res["n_" + key] = len(res[key])
    return res


def build_era_faces(thermo_df, panel_days, panel_tops):
    """F4: era-band medians from P6 thermo vs forward-panel ladder tops."""
    if thermo_df is None or len(thermo_df) == 0:
        return {"available": False, "note": "thermo_daily.csv absent/empty"}
    df = thermo_df.copy()
    df["year"] = df["date"].astype(str).str[:4].astype(int)
    bands = {}
    for lo, hi in ERA_BANDS:
        seg = df[(df["year"] >= lo) & (df["year"] <= hi)]
        if len(seg) == 0:
            continue
        bands["%d-%d" % (lo, hi)] = {
            "n_days": int(len(seg)),
            "max_height_median": float(seg["max_height"].median()),
            "n_lianban4p_median": float(seg["n_lianban4p"].median()),
            "n_lianban2_median": float(seg["n_lianban2"].median()),
        }
    recent = df.tail(250)
    return {
        "available": True,
        "thermo_cutoff": str(df["date"].iloc[-1]),
        "era_bands": bands,
        "recent_1y": {"max_height_median": float(recent["max_height"].median()),
                      "n_lianban4p_median": float(recent["n_lianban4p"].median())},
        "forward_panel_days": panel_days,
        "forward_panel_ladder_tops": panel_tops,
        "overlap_note": "thermo P-5C frozen cutoff precedes forward panel start; era reference only, zero same-day join",
    }


def build_evidence(panel_dir=PANEL, thermo_path=THERMO):
    zt = pd.read_parquet(os.path.join(panel_dir, "zt.parquet"))
    zbgc = pd.read_parquet(os.path.join(panel_dir, "zbgc.parquet"))
    dtgc = pd.read_parquet(os.path.join(panel_dir, "dtgc.parquet"))
    strong = pd.read_parquet(os.path.join(panel_dir, "strong.parquet"))
    with open(os.path.join(panel_dir, "collected_days.json"), encoding="utf-8") as f:
        cd = json.load(f)
    days = sorted(set(cd.get("zt", [])))
    if not days:
        raise RuntimeError("zero collected zt days in panel ledger")
    per_day = [build_perday_faces(zt, zbgc, dtgc, strong, d) for d in days]
    trans = [build_transition(zt, zbgc, strong, days[i], days[i + 1])
             for i in range(len(days) - 1)]
    thermo = None
    if os.path.exists(thermo_path):
        thermo = pd.read_csv(thermo_path)
    era = build_era_faces(thermo, days, [p["ladder_top"] for p in per_day])
    return {
        "probe": "zt_ladder_probe",
        "evidence_cutoff": days[-1],
        "panel_days": days,
        "n_days": len(days),
        "rows": {"zt": int(len(zt)), "zbgc": int(len(zbgc)),
                 "dtgc": int(len(dtgc)), "strong": int(len(strong))},
        "per_day": per_day,
        "transitions": trans,
        "era_context": era,
        "thin_disclosure": "forward panel n_days=%d; transition windows=%d; descriptive structure face only, no judgment/criteria (T-67 sec.2 freeze law: prereg needs >=12 months forward history)" % (len(days), len(trans)),
    }


def _synth_zt(rows):
    cols = ["日期", "代码", "名称", "涨跌幅", "封板资金", "炸板次数", "连板数", "所属行业"]
    return pd.DataFrame(rows, columns=cols)


def _synth_simple(cols, rows):
    return pd.DataFrame(rows, columns=cols)


def selftest():
    ok = 0

    def check(name, cond):
        nonlocal ok
        assert cond, "FAIL: " + name
        ok += 1

    # F1: histogram/top/sector
    zt = _synth_zt([
        ["2026-01-05", "000001", "A", 10.0, 100, 0, 1, "电池"],
        ["2026-01-05", "000002", "B", 10.0, 300, 1, 2, "电池"],
        ["2026-01-05", "000003", "C", 10.0, 200, 0, 3, "白酒"],
        ["2026-01-06", "000002", "B", 10.0, 400, 0, 3, "电池"],
        ["2026-01-06", "000003", "C", 9.9, 500, 2, 4, "白酒"],
        ["2026-01-06", "000004", "D", 10.0, 50, 0, 1, "白酒"],
    ])
    empty = pd.DataFrame(columns=zt.columns)
    f1 = build_perday_faces(zt, empty, empty, empty, "2026-01-05")
    check("f1_n_zt", f1["n_zt"] == 3)
    check("f1_hist", f1["ladder_histogram"] == {"1": 1, "2": 1, "3": 1})
    check("f1_top", f1["ladder_top"] == 3)
    check("f1_fund_median", abs(f1["seal_fund_median"] - 200.0) < 1e-9)
    check("f1_sector", f1["highboard_sector_top5"]["电池"] == 1
          and f1["highboard_sector_top5"]["_n_highboard_rows"] == 2)
    check("f1_blow", f1["intraday_blow"]["n_zero_blow"] == 2)
    # F2: promoted/blown/gone + level rates
    zbgc = _synth_simple(["日期", "代码"],
                          [["2026-01-05", "000004"], ["2026-01-06", "000001"]])
    strong = _synth_simple(["日期", "代码"], [["2026-01-06", "000009"]])
    t = build_transition(zt, zbgc, strong, "2026-01-05", "2026-01-06")
    check("t_promoted_n", t["n_promoted"] == 2)
    check("t_blown_n", t["n_blown_next"] == 1)
    check("t_gone_n", t["n_gone"] == 0)
    check("t_reboard", t["reboard_zbgc_to_zt"] == 1)
    check("t_rate_k1", t["promotion_by_level"]["1"]["rate"] == 0.0)
    check("t_rate_k2", abs(t["promotion_by_level"]["2"]["rate"] - 1.0) < 1e-9)
    check("t_rate_k3", abs(t["promotion_by_level"]["3"]["rate"] - 1.0) < 1e-9)
    # F4: era bands on synthetic thermo
    thermo = pd.DataFrame({
        "date": ["1998-01-02", "2010-05-06", "2018-03-04", "2024-07-08"] * 3,
        "max_height": [8, 5, 4, 6] * 3,
        "n_lianban4p": [30, 10, 5, 8] * 3,
        "n_lianban2": [60, 40, 30, 35] * 3,
    })
    era = build_era_faces(thermo, ["2026-01-05"], [3])
    check("era_avail", era["available"] is True)
    check("era_band_med", era["era_bands"]["1996-2005"]["max_height_median"] == 8.0)
    check("era_band_recent", era["era_bands"]["2021-2026"]["max_height_median"] == 6.0)
    # determinism: build_evidence face double-run on synthetic panel dir
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(td, exist_ok=True)
        for name, df in [("zt", zt), ("zbgc", zbgc), ("dtgc", empty), ("strong", strong)]:
            df.to_parquet(os.path.join(td, name + ".parquet"))
        with open(os.path.join(td, "collected_days.json"), "w", encoding="utf-8") as f:
            json.dump({"zt": ["2026-01-05", "2026-01-06"]}, f)
        ev1 = json.dumps(build_evidence(td, THERMO), sort_keys=True, default=str)
        ev2 = json.dumps(build_evidence(td, THERMO), sort_keys=True, default=str)
        check("determinism", ev1 == ev2)
        ev = json.loads(ev1)
        check("ev_cutoff", ev["evidence_cutoff"] == "2026-01-06")
        check("ev_windows", len(ev["transitions"]) == 1)
    return "selftest: %d/%d PASS" % (ok, ok)


def main():
    ap = argparse.ArgumentParser(description="E10 zt ladder structure probe")
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        print(selftest())
        return 0
    try:
        ev = build_evidence()
    except Exception as e:  # mechanism failure: honest report, no partial write
        print("PROBE FAIL: %r" % e)
        return 2
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1, default=str)
    print("probe OK: days=%s top=%s -> %s" % (
        ev["panel_days"], [p["ladder_top"] for p in ev["per_day"]], OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
