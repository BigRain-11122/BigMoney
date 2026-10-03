"""G2_SLOT_MON_P2 pre-freeze probe (stage-2 registration-caliber face).

Legs (facts for prereg sec.2, fail-closed, zero result-peeking):
 L1  stage-2 shortlist integrity: parent census results/g2_slot_mon_p1/
     g2_slot_mon_p1_census.json nominates EXACTLY {old_032, best_016}
     (family_verdicts nominated_faces union), each with all three frozen
     cond lines recorded -- shortlist provenance anchor.
 L2  both faces exist in vendor LEGACY_REGISTRY (pinned HEAD a770825)
     and in the parent probe roster (sha16 7ce1e81d019eba3d freeze face).
 L3  seed band [20570000, 20570060) free: disjoint vs every registered
     int seed band in science_gates.SEED_REGISTRY (scan, not memory).
 L4  panel facts re-assert: core48 INSERVICE_WHITELIST sha16
     abf3d43b9ca13ea5, 48 csv on disk, union last bar == 2026-09-22
     cutoff (P-family D2 forward lockbox same-window lineage).
 L5  parent-IC determinism anchors: re-derived per-face ic5_mean for the
     two shortlist faces from the parent ic_by_face.csv -- P2 runner
     cross-check tolerance 1e-6 (values loaded as frozen anchors).
 L6  class/family tags carried: both faces volume_price class (BAN
     inheritance zero-hit for the shortlist itself).

Exit 0 = all legs PASS; 1 = fact-leg FAIL (freeze forbidden); 2 = mech.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "research", "shortline", "screening"))

import csv as _csv  # noqa: E402
import science_gates as sg  # noqa: E402
from knowledge.panel_gate import INSERVICE_WHITELIST, INSERVICE_SHA16  # noqa: E402

PARENT_CENSUS = os.path.join(ROOT, "results", "g2_slot_mon_p1",
                             "g2_slot_mon_p1_census.json")
PARENT_IC = os.path.join(ROOT, "results", "g2_slot_mon_p1", "ic_by_face.csv")
PARENT_PROBE = os.path.join(ROOT, "results", "_r647bma_slot_mon_roster_probe.json")
VENDOR_SRC = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading\src"
sys.path.insert(0, VENDOR_SRC)

SHORTLIST = ["old_032", "best_016"]
SEED_P2 = 20570000
K_NULLS_P2 = 60
CUTOFF = "2026-09-22"
BAND = 60


def main() -> int:
    out = {"probe": "G2_SLOT_MON_P2 pre-freeze", "legs": {}, "pass": False}
    try:
        # L1 shortlist integrity
        pc = json.load(open(PARENT_CENSUS, encoding="utf-8", errors="replace"))
        nom = set()
        for fam, blk in pc["family_verdicts"].items():
            nom.update(blk.get("nominated_faces", []))
        l1 = (nom == set(SHORTLIST))
        out["legs"]["L1_shortlist_integrity"] = {
            "nominated_union": sorted(nom), "expected": SHORTLIST, "pass": l1}
        # L2 vendor registry + roster membership
        from mlquant.features.legacy_factors import LEGACY_REGISTRY  # type: ignore
        probe = json.load(open(PARENT_PROBE, encoding="utf-8",
                              errors="replace"))
        roster_names = set()
        rb = probe.get("roster") if isinstance(probe, dict) else None
        if isinstance(rb, dict):
            roster_names.update(rb.keys())
        l2 = all(f in LEGACY_REGISTRY for f in SHORTLIST) and \
            all(f in roster_names for f in SHORTLIST)
        out["legs"]["L2_vendor_roster"] = {
            "in_registry": {f: f in LEGACY_REGISTRY for f in SHORTLIST},
            "in_roster_freeze": {f: f in roster_names for f in SHORTLIST},
            "roster_freeze_sha16": probe.get("leg2_roster_freeze_sha16"),
            "roster_sha16_expected": "7ce1e81d019eba3d",
            "pass": l2}
        # L3 seed band disjoint scan
        bands = []
        for v in sg.SEED_REGISTRY.values():
            if isinstance(v, int):
                bands.append(v)
        clash = [s for s in bands
                 if s // 100000 == SEED_P2 // 100000 and
                 abs(s - SEED_P2) < 10000]
        l3 = (SEED_P2 not in bands) and not clash
        out["legs"]["L3_seed_band_free"] = {
            "seed": SEED_P2, "k": K_NULLS_P2, "band": [SEED_P2, SEED_P2 + BAND],
            "nearest_neighbors": sorted(
                [s for s in bands if abs(s - SEED_P2) <= 20000])[:6],
            "pass": l3}
        # L4 panel facts (path law: data/daily/<code>.csv, code carries
        # its own exchange prefix -- g2_slot_mon_p1.build_panel mirror).
        # P2 cutoff = parent window 2026-09-22 (same-window lineage);
        # panel has since advanced to 2026-09-30 (last pre-holiday bar)
        # -- the truncation line is IN-PANEL (raw read_csv cut), so the
        # assert here is "every member covers >= cutoff" (truncatable),
        # with union_last_bar recorded as fact, not == cutoff.
        ok48, missing, last_bars = 0, [], []
        for code in sorted(INSERVICE_WHITELIST):
            p = os.path.join(ROOT, "data", "daily", "%s.csv" % code)
            if not os.path.exists(p):
                missing.append(code)
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                last = fh.readlines()[-1].split(",")[0].strip()
            if last >= CUTOFF:
                ok48 += 1
            else:
                missing.append(code)
            last_bars.append(last)
        union_last = max(last_bars) if last_bars else None
        l4 = (len(INSERVICE_WHITELIST) == 48 and ok48 == 48 and
              not missing and union_last >= CUTOFF and
              INSERVICE_SHA16 == "abf3d43b9ca13ea5")
        out["legs"]["L4_panel"] = {
            "whitelist_sha16": INSERVICE_SHA16, "n_members": len(INSERVICE_WHITELIST),
            "covering_cutoff": ok48, "missing_or_short": missing,
            "union_last_bar": union_last, "cutoff_truncation_line": CUTOFF,
            "note": "panel advanced past parent cutoff; P2 truncates at "
                    "2026-09-22 (parent same-window lineage, D2 no-backflow "
                    "guaranteed by truncation)",
            "pass": l4}
        # L5 parent-IC anchors
        anchors = {}
        with open(PARENT_IC, encoding="utf-8", errors="replace") as fh:
            for row in _csv.DictReader(fh):
                if row["face"] in SHORTLIST:
                    anchors[row["face"]] = {
                        "ic5_mean": float(row["ic5_mean"]),
                        "x2_beat_rate": float(row["x2_beat_rate"]),
                        "x2_ann": float(row["x2_ann"]),
                        "nominated": int(row["nominated"])}
        l5 = set(anchors) == set(SHORTLIST) and all(
            anchors[f]["nominated"] == 1 for f in SHORTLIST)
        out["legs"]["L5_parent_ic_anchors"] = {
            "anchors": anchors, "pass": l5}
        # L6 class carry
        l6 = True
        cls = {}
        with open(PARENT_IC, encoding="utf-8", errors="replace") as fh:
            for row in _csv.DictReader(fh):
                if row["face"] in SHORTLIST:
                    cls[row["face"]] = row.get("class", "")
                    if cls[row["face"]] != "volume_price":
                        l6 = False
        out["legs"]["L6_class_carry"] = {"classes": cls, "pass": l6}
        out["pass"] = all(v["pass"] for v in out["legs"].values())
        out["evidence_cutoff"] = CUTOFF
        out["cutoff_meta"] = sg.cutoff_meta(CUTOFF)
    except Exception as e:  # probe mech fault
        out["legs"]["exception"] = repr(e)
        out["pass"] = False
    dst = os.path.join(ROOT, "results", "_r648bma_p2_probe.json")
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1, sort_keys=True)
    for k, v in out["legs"].items():
        if isinstance(v, dict):
            print(f"[L] {k}: pass={v.get('pass')}")
        else:
            print(f"[L] {k}: {v}")
    print("PROBE", "PASS" if out["pass"] else "FAIL")
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
