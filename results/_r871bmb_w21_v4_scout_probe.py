"""r871 bm-b scout probe: N2-W21 supply-face adjudication + T-101 v4
22-gate library consumption-face scouting.

Read-only facts probe (zero burn, zero ledger, zero panel writes).
Questions answered (advisory scout face, r870 next_milestone window <=10-13):
  Q1: Is a same-family N2-W21 alphagen beam wave lawful? (family closure check)
  Q2: What consumption faces are OPEN for the v4 candidate library
      (22 gates = A158 17 RECHECK-CONFIRM + MP1 5 RECHECK-CONFIRM) given the
      A9-A13 usage-line closures?
  Q3: What pre-draft gates does the A1/C1 dual-thermometer composite arm face
      (sentiment-family double-negative archive + BAN-05) require?
Outputs: results/_r871bmb_w21_v4_scout.json
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

FACTS = {}


def _read(path):
    with io.open(os.path.join(ROOT, path), encoding="utf-8", errors="strict") as fh:
        return fh.read()


def _marker(text, needle, label):
    return {"check": label, "needle": needle, "present": needle in text}


# ---- Q1: W21 same-family wave lawfulness -------------------------------------
w20 = _read("research/PERPETUAL_N2_W20_PREREG.md")
FACTS["q1_w20_closure"] = {
    "rp2_leverage_2of2": _marker(w20, "RP2 \u6760\u6746\u590d\u73b0=TRUE", "W20 RP2=2/2 replication-true"),
    "rp2_upgrade_citable": _marker(w20, "\u5347\u7ea7\u4e3a\u53ef\u5f15\u7528", "leverage claim upgraded citable"),
    "same_family_reopen_ban": _marker(
        w20,
        "\u6362\u76ae\u91cd\u8dd1",
        "same-family rerun ban clause (z-axis/holding/threshold variants)",
    ),
    "reopen_channel": _marker(
        w20,
        "\u65b0\u6570\u636e\u6e90+\u4f8b\u5916\u4e09\u95ee",
        "restart channel = new data source + exception three questions",
    ),
}

# ---- v4 library roster facts --------------------------------------------------
import science_gates as sg  # noqa: E402

try:
    import t101_v4_a158_fv as fv  # noqa: E402

    gates17 = sorted(fv.GATES17)
except Exception as ex:  # pragma: no cover - hard fail face
    gates17 = []
    FACTS["q2_gates17_import_error"] = repr(ex)

recheck = json.loads(_read("results/gate_recheck_mp1.json"))
vc = recheck.get("verdict_counts") or {}
mp1_confirm = sorted(recheck.get("library_entries") or [])
FACTS["q2_mp1_recheck_crosscheck"] = {
    "verdict_counts": vc,
    "recheck_confirm_count": vc.get("RECHECK-CONFIRM"),
    "library_entries_size": len(mp1_confirm),
    "counts_match": vc.get("RECHECK-CONFIRM") == len(mp1_confirm),
}

union = sorted(set(gates17) | set(mp1_confirm))
overlap = sorted(set(gates17) & set(mp1_confirm))
FACTS["q2_v4_library_roster"] = {
    "a158_confirm_17": gates17,
    "mp1_confirm": mp1_confirm,
    "union_size": len(union),
    "overlap_size": len(overlap),
    "overlap": overlap,
    "expected_union": 22,
    "roster_matches_expected": len(union) == 22 and len(overlap) == 0,
}

# ---- Q2: usage-line closure map (text markers in the arm table) ---------------
bench = _read("research/DECISION_CHAIN_BENCHMARKS.md")
FACTS["q2_usage_line_closures"] = {
    "a9_gate_timing_closed": _marker(bench, "FV 0/9", "A9 single-gate timing line closed"),
    "a10_combo_timing_closed": _marker(bench, "FV 0/16", "A10 regime-combo timing closed"),
    "a11_selector_closed": _marker(bench, "FV 0/24", "A11 cross-sectional selector closed"),
    "a12_conditioning_closed": _marker(bench, "FV 0/12", "A12 conditioning sleeve closed"),
    "a13_predictor_positive": _marker(bench, "FV 2/12 PASS", "A13 predictor face positive info discovery"),
    "a13_downstream_bmb_lane": _marker(
        bench,
        "A1/C1 \u53cc\u6e29\u5ea6\u8ba1\u590d\u5408\u81c2\u6307\u540d\u8f93\u5165\u7279\u5f81",
        "A13 downstream: f_c2 -> A1/C1 composite named input feature (bm-b lane)",
    ),
    "a2_remaining_lane_a1": _marker(
        _read("research/T-101-V4-A2-CORRSOURCE_PREREG.md"),
        "v4 \u4f9b\u7ed9\u7ebf\u552f\u4e00\u5269\u4f59\u8f66\u9053=A1 C1 \u53cc\u6e29\u5ea6\u8ba1\u81c2",
        "A2 closeout: only remaining v4 supply lane = A1/C1 composite (bm-b)",
    ),
}

# ---- Q3: A1/C1 composite arm pre-draft gates ----------------------------------
lt = _read("research/LHB_THERMO_IC_P1.md")
to = _read("research/THERMO-OVERLAY-P1.md")
FACTS["q3_a1_composite_predraft_gates"] = {
    "lhb_thermo_family_closure": _marker(
        lt, "\u65cf\u7ea7\u95ed\u5408", "LHB thermo family-level closure statement"
    ),
    "thermo_overlay_negative": _marker(
        to, "0/6", "THERMO-OVERLAY-P1 0/6 negative verdict"
    ),
    "closed_families_registry_keys": sorted(sg.CLOSED_FAMILIES.keys()),
    "sentiment_family_in_registry": any(
        k in ("sentiment", "thermo", "lhb") for k in sg.CLOSED_FAMILIES
    ),
    "adjudication": (
        "A1/C1 composite arm drafting requires: (a) BAN-05 new_data exception "
        "adjudication vs retail-quant-conclusions-v2#3 (THERMO-OVERLAY-P1 "
        "precedent), (b) sentiment-family double-negative archive adjudication "
        "(LHB_THERMO_IC_P1 sec.8 + THERMO-OVERLAY-P1 sec.8: new data source + "
        "exception three questions before any sentiment/temperature-typed claim)"
    ),
}

# ---- verdict block ------------------------------------------------------------
FACTS["scout_verdict"] = {
    "q1_w21_same_family_wave": "BANNED - alphagen beam family closed RP2=2/2 "
    "(W20 sec.8); same-family z/holding/threshold variants = rerun ban; "
    "restart needs new data source + exception three questions",
    "q1_never_dry_pivot": "supply line pivots to consumption chain: v4 "
    "22-gate library consumption face (T-101 lineage) = the next burnable "
    "batch family; pool feeding resumes via prereg->freeze->pool-submit chain",
    "q2_open_consumption_faces": [
        "A13-style predictor extension on the v4 22-gate library "
        "(f_c2v4 = 22-gate mask mean, f_mp1 = 5-gate mean; RAW/RESID "
        "rank-IC vs fwd20; A13 machinery clone law r836; feeds the A1/C1 "
        "composite input roster per A13 sec.8 downstream pointer)",
    ],
    "q2_closed_consumption_faces": [
        "single-gate / combo timing usage (A9 0/9 + A10 0/16)",
        "cross-sectional selector usage (A11 0/24)",
        "vol/risk conditioning usage (A12 0/12)",
    ],
    "q3_a1_composite_arm": "gated: BAN-05 + sentiment-family adjudication "
    "required pre-draft; NOT drafted this window",
    "advisory_only": True,
    "zero_burn": True,
}

out_path = os.path.join(ROOT, "results", "_r871bmb_w21_v4_scout.json")
with io.open(out_path, "w", encoding="utf-8") as fh:
    json.dump(FACTS, fh, ensure_ascii=False, indent=1, sort_keys=True)
print(json.dumps(FACTS["scout_verdict"], ensure_ascii=False, indent=1))
print("roster ok:", FACTS["q2_v4_library_roster"]["roster_matches_expected"],
      "| mp1_confirm:", FACTS["q2_v4_library_roster"]["mp1_confirm"])
