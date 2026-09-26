"""_r250bma_rot_probe.py -- CN-DIV-LOWVOL-ROT-P1 prereg S2 probe (frozen reference artifact).

Deterministic, zero-network, zero-judgment (data-completeness facts only; R99
law: no strategy/judgment runs before prereg freeze). Writes
results/div_lowvol_rot_probe.json which the prereg S2 freezes by reference.

Faces:
  1. per-leg corpus rows / first-last bar (data/daily/sh{510880,512890}.csv)
  2. joint date-set alignment + joint window bar count (family window face)
  3. evidence_cutoff = min(last bars) -> forward lockbox value
  4. ADV capacity face: per-year median ADV20 = median(volume*close) CNY
     (family root-cause carry: 512890 2020-2022 thin ADV documented in
      DIV_LOWVOL_P1 S8; volume*close~=amount per family probe verification)
  5. data completeness gate values (legs==2, cutoff, joint_bars threshold)
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "div_lowvol_rot_probe.json")
LEGS = {"510880": "sh510880.csv", "512890": "sh512890.csv"}


def load(code: str, fname: str) -> pd.DataFrame:
    p = os.path.join(ROOT, "data", "daily", fname)
    if not os.path.exists(p):
        raise SystemExit(f"probe: leg corpus missing: {p}")
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def main() -> int:
    legs = {}
    for code, fname in LEGS.items():
        df = load(code, fname)
        legs[code] = df

    facts = {"legs": {}}
    for code, df in legs.items():
        facts["legs"][code] = {
            "rows": int(len(df)),
            "first_bar": str(df["date"].iloc[0].date()),
            "last_bar": str(df["date"].iloc[-1].date()),
        }

    d1 = set(legs["510880"]["date"])
    d2 = set(legs["512890"]["date"])
    joint_dates = sorted(d1 & d2)
    cutoff = min(legs[c]["date"].iloc[-1] for c in LEGS)

    # alignment face is scoped to the JOINT window (510880 pre-2019 solo bars
    # are outside it by construction; global set equality is the wrong gate).
    # Mismatch days = corpus gap on one leg while the other traded; the batch
    # timeline is the INTERSECTION (both legs markable every timeline day) and
    # the mismatch set is frozen here for the runner's date-drift assertion.
    j0 = joint_dates[0]
    d1_in = {x for x in d1 if x >= j0}
    mismatch_days = sorted((d1_in | d2) - (d1_in & d2))
    facts["date_alignment"] = {
        "global_sets_identical": bool(d1 == d2),
        "only_in_510880_global": int(len(d1 - d2)),
        "mismatch_days_within_joint_window": [str(x.date()) for x in mismatch_days],
        "joint_bars": int(len(joint_dates)),
        "joint_first": str(joint_dates[0].date()) if joint_dates else None,
        "joint_last": str(joint_dates[-1].date()) if joint_dates else None,
        "timeline_convention": "intersection timeline; both legs markable/tradeable every batch day",
    }
    facts["evidence_cutoff"] = str(cutoff.date())

    # ADV capacity face: per-year median of trailing-20d mean turnover (CNY).
    adv = {}
    for code, df in legs.items():
        df = df.copy()
        df["amount_cny"] = df["volume"] * df["close"]
        df["year"] = df["date"].dt.year
        df["adv20"] = df["amount_cny"].rolling(20).mean()
        per_year = df.groupby("year")["adv20"].median()
        adv[code] = {str(int(y)): round(float(v), 0) for y, v in per_year.items() if v == v}
    facts["adv20_median_cny_per_year"] = adv

    # thin-window carry: 2020-2022 both-leg ADV medians (family root-cause face)
    thin = {}
    for code, years in adv.items():
        thin[code] = {y: years.get(y) for y in ("2020", "2021", "2022")}
    facts["thin_adv_window_carry"] = thin

    gate = {
        "legs_count": len(LEGS) == 2,
        "cutoff_is_2026_09_22": facts["evidence_cutoff"] == "2026-09-22",
        "joint_bars_ge_1800": facts["date_alignment"]["joint_bars"] >= 1800,
        "mismatch_days_frozen_disclosed": facts["date_alignment"]["mismatch_days_within_joint_window"] == ["2021-10-22"],
    }
    facts["completeness_gate_precheck"] = gate
    facts["probe_note"] = (
        "deterministic data-completeness probe for prereg S2 freeze-by-reference; "
        "zero strategy/judgment computation; ADV=volume*close per DIV_LOWVOL_P1 "
        "probe verification (volume unit face); new bars after 2026-09-22 are "
        "lockbox-excluded (corpus twins end at cutoff; core48 no-prefix panel has "
        "09-23/09-24 bars but 510880/512890 have no no-prefix twins)"
    )

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False, indent=1))
    ok = all(gate.values())
    print("GATE:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
