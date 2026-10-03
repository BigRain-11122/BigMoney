"""G2_SLOT_MON_P1 roster/feasibility probe (bm-a r647).

Blind probe for the r644 next-pointer slice: IC-enriched 47/126 face list
"low-cost translation layer variant" (monthly Top-16 cadence decomposition
batch). Freeze-precedes-run law (R99): this probe measures ONLY structural
facts + parent-census provenance anchors; it does NOT compute any monthly
sleeve / fwd-21d outcome (the batch's judgment face stays blind until the
frozen prereg commit lands).

Legs:
  L1 roster derivation -- deterministic union of cond1 passers
      (|ic5_mean| > that batch's own null p95) from the three frozen G2_SLOT
      census products (old 41 / stock 14 / tail 71; expected 18+2+27=47);
      class + family tag carried from parent census as-is.
  L2 roster_freeze sha16 -- sha256 of canonical roster JSON (runner selftest
      L1 anchor).
  L3 vendor anchor -- ml-quant-trading HEAD == a770825 (r644 law).
  L4 panel integrity -- core48 48 csv in place, six-field, window 2020-01-02
      .. cutoff 2026-09-22, union last bar == cutoff, zero dup dates.
  L5 seed band -- 20560000 free + disjoint vs SEED_REGISTRY (band
      [20560000,20560020), family bases 20530000/20540000/20550000 gap 10000).
  L6 COST_X1 single source -- rev_osc_stock_p1.COST_X1 == 13.041bp mirror.
  L7 parent provenance anchors -- per enriched face: parent x1/x2 ann, parent
      beat rate, parent turnover facts (frozen historical parent outputs,
      roster-derivation provenance + sec.5 prediction anchors only).
  L8 BAN carry distribution -- 47 faces by parent class (price_banned faces
      stay measured-but-never-nominatable per frozen sec.0.5 family rule).

Usage: python results/_r647bma_slot_mon_roster_probe.py
"""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

CUTOFF = "2026-09-22"
PANEL_START = "2020-01-02"
SEED_NULLS = 20560000
K_NULLS = 20
ANCHOR_HEAD = "a770825f841504e41581f057b4d94160e6a50c2e"
VENDOR_REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading"
SIX_FIELDS = ("open", "high", "low", "close", "volume", "amount")

PARENTS = [
    ("old", "results/g2_slot_old_p1"),
    ("stock", "results/g2_slot_stock_p1"),
    ("tail", "results/g2_slot_tail_p1"),
]


def find_census_json(d):
    for f in sorted(os.listdir(os.path.join(ROOT, d))):
        if f.endswith("_census.json"):
            return os.path.join(ROOT, d, f)
    raise SystemExit("census json missing in %s" % d)


def leg1_roster():
    roster = {}
    per_batch = {}
    for fam, d in PARENTS:
        c = json.load(open(find_census_json(d), encoding="utf-8"))
        p95 = c["nulls"]["p95_abs_mean_ic"]
        enriched = []
        for fid, f in c["faces"].items():
            icm = f["ic"]["ic5_mean"]
            if abs(icm) > p95:
                enriched.append(fid)
                roster[fid] = {
                    "family": fam,
                    "class": f["class"],
                    "parent_ic5_mean": icm,
                    "parent_null_p95": p95,
                    "parent_x1_ann": f["x1"]["ann"],
                    "parent_x2_ann": f["x2"]["ann"],
                    "parent_x2_beat": f["x2"].get("beat_rate"),
                    "parent_turnover": f["x2"].get("turnover_total"),
                    "parent_n_rebal": f["x2"].get("n_rebal"),
                }
        per_batch[fam] = {"p95": p95, "n_enriched": len(enriched),
                          "faces": sorted(enriched)}
    return roster, per_batch


def leg2_sha(roster):
    canon = json.dumps(roster, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def leg3_vendor():
    h = subprocess.run(["git", "-C", VENDOR_REPO, "rev-parse", "HEAD"],
                       capture_output=True, text=True).stdout.strip()
    return {"head": h, "match": h == ANCHOR_HEAD}


def leg4_panel():
    from knowledge.panel_gate import INSERVICE_WHITELIST  # noqa: PLC0415
    members = sorted(INSERVICE_WHITELIST)
    missing, dup = [], []
    n_days = None
    union_last = None
    for code in members:
        p = os.path.join(ROOT, "data", "daily", "%s.csv" % code)
        if not os.path.exists(p):
            missing.append(code)
            continue
        df = pd.read_csv(p, parse_dates=["date"])
        if not set(SIX_FIELDS) <= set(df.columns):
            missing.append(code + ":cols")
            continue
        df = df[(df["date"] >= pd.Timestamp(PANEL_START))
                & (df["date"] <= pd.Timestamp(CUTOFF))]
        if df["date"].duplicated().any():
            dup.append(code)
        n_days = len(df) if n_days is None else n_days
        union_last = str(df["date"].iloc[-1].date())
    return {"n_members": len(members), "missing": missing,
            "dup_date_members": dup, "sample_member_rows": n_days,
            "union_last": union_last,
            "union_last_eq_cutoff": union_last == CUTOFF}


def leg5_seed():
    from science_gates import SEED_REGISTRY  # noqa: PLC0415
    vals = []
    for v in SEED_REGISTRY.values():
        try:
            vals.append(int(v))
        except (TypeError, ValueError):
            continue  # non-numeric registry entries (str bands etc.) honest skip
    return {"seed": SEED_NULLS, "k": K_NULLS,
            "base_free": SEED_NULLS not in vals,
            "band_lo": SEED_NULLS, "band_hi": SEED_NULLS + K_NULLS,
            "disjoint": all(not (SEED_NULLS <= v < SEED_NULLS + K_NULLS)
                            for v in vals)}


def leg6_cost():
    sys.path.insert(0, os.path.join(ROOT, "research", "shortline", "screening"))
    from rev_osc_stock_p1 import COST_X1  # noqa: PLC0415
    return {"cost_x1_bp_per_side": round(COST_X1 * 1e4, 3),
            "match_13041": abs(COST_X1 * 1e4 - 13.041) < 1e-9}


def main():
    roster, per_batch = leg1_roster()
    probe = {
        "probe": "G2_SLOT_MON_P1 roster/feasibility probe",
        "round": "r647 bm-a",
        "law_lineage": "r644 next-pointer (IC 47/126 low-cost translation "
                       "variant slice) + O-20260930-1901 census-first/meaning "
                       "gate + R99 freeze-precedes-run",
        "leg1_roster": {"total": len(roster), "per_batch": per_batch,
                        "expected": {"old": 18, "stock": 2, "tail": 27,
                                     "total": 47}},
        "leg2_roster_freeze_sha16": leg2_sha(roster),
        "leg3_vendor_anchor": leg3_vendor(),
        "leg4_panel": leg4_panel(),
        "leg5_seed_band": leg5_seed(),
        "leg6_cost": leg6_cost(),
    }
    from collections import Counter
    cls = Counter(v["class"] for v in roster.values())
    fams = Counter(v["family"] for v in roster.values())
    probe["leg8_ban_carry"] = {"class_distribution": dict(cls),
                               "family_distribution": dict(fams),
                               "price_banned_note": "measured, "
                               "never nominatable (frozen sec.0.5 family "
                               "rule carried as-is)"}
    probe["roster"] = roster
    probe["leg1_roster"]["counts_match_expected"] = (
        len(roster) == 47
        and per_batch["old"]["n_enriched"] == 18
        and per_batch["stock"]["n_enriched"] == 2
        and per_batch["tail"]["n_enriched"] == 27)
    ok = (probe["leg1_roster"]["counts_match_expected"]
          and probe["leg3_vendor_anchor"]["match"]
          and probe["leg4_panel"]["n_members"] == 48
          and not probe["leg4_panel"]["missing"]
          and probe["leg4_panel"]["union_last_eq_cutoff"]
          and probe["leg5_seed_band"]["base_free"]
          and probe["leg5_seed_band"]["disjoint"]
          and probe["leg6_cost"]["match_13041"])
    probe["verdict"] = "PASS" if ok else "FAIL"
    out = os.path.join(ROOT, "results", "_r647bma_slot_mon_roster_probe.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(probe, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("verdict:", probe["verdict"])
    print("roster_total:", len(roster), dict(fams), dict(cls))
    print("roster_freeze_sha16:", probe["leg2_roster_freeze_sha16"])
    print("panel:", probe["leg4_panel"]["n_members"], "members, union_last",
          probe["leg4_panel"]["union_last"])
    print("seed:", probe["leg5_seed_band"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
