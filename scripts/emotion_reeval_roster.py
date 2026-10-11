#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E15 roster probe - emotion-family reform-line reeval input face (catalog #18).

Purpose (E15 leg-1, r875 bm-b):
  Extract the frozen mass-trial near-miss dossier (results/mass_trial/report_card.json,
  evidence_cutoff 2026-09-22, report-only aggregation of frozen wave judge files)
  verbatim into a roster face for the planned FDR4D reform-line re-adjudication batch
  (REGISTRATION_REFORM_FDR4D_PREREG sec.9-6 five-step chain; W14/W16 = live precedent).

Laws honored:
  - Zero judgment, zero thresholds invented here: descriptive roster only.
    Batch membership m for BH FDR is decided by the frozen prereg (next leg), not here.
  - L1 deterministic, zero network, read-only inputs, append-safe output.
  - "report_card honesty" preserved verbatim: family recurrence is a direction
    clue, not a promotion (catalog #18 consumes it as the reopen-channel input).

Usage:
  python scripts/emotion_reeval_roster.py run       # emit results/emotion_reeval/e15_roster.json
  python scripts/emotion_reeval_roster.py selftest # hermetic offline self-check
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_CARD = os.path.join(ROOT, "results", "mass_trial", "report_card.json")
OUT_DIR = os.path.join(ROOT, "results", "emotion_reeval")
OUT_PATH = os.path.join(OUT_DIR, "e15_roster.json")

# Metric keys carried per member (verbatim from the frozen dossier).
METRIC_KEYS = (
    "candidate_id", "family", "dsr", "family_pbo", "g1_margin",
    "g1_sharpe_full", "g1_skill_line", "g2_dsr_ok", "g2_pbo_ok",
    "g2_eligible", "n_eff_start_windows", "oos_ret_legL",
    "oos_sharpe_legL", "signflip_p", "bootstrap_ci_lower",
)

# Direction-clue family named by EXTERNAL_IDEAS_CATALOG_R1 row #18
# (sentiment.turnover_surge recurrence x2; E6 emotion family PBO 0.1857).
DIRECTION_FAMILY = "sentiment.turnover_surge"


def build_roster(report_card):
    """Deterministic roster face from the frozen report card. Pure function."""
    if not isinstance(report_card, dict):
        raise ValueError("report_card must be a dict")
    passers = report_card.get("passers") or []
    members = []
    for p in passers:
        if not isinstance(p, dict):
            continue
        rec = {}
        for k in METRIC_KEYS:
            if k in p:
                rec[k] = p[k]
        if "candidate_id" not in rec or "family" not in rec:
            raise ValueError("dossier member missing candidate_id/family")
        members.append(rec)
    members.sort(key=lambda r: (r["family"], str(r["candidate_id"])))
    fam_count = {}
    for m in members:
        fam_count[m["family"]] = fam_count.get(m["family"], 0) + 1
    families = []
    for fam, cnt in sorted(fam_count.items()):
        best = max((m for m in members if m["family"] == fam),
                   key=lambda m: m.get("oos_sharpe_legL") or -9.0)
        families.append({
            "family": fam,
            "n_members": cnt,
            "recurrence_ge2": cnt >= 2,
            "direction_clue": fam == DIRECTION_FAMILY,
            "best_member": best["candidate_id"],
            "best_oos_sharpe_legL": best.get("oos_sharpe_legL"),
            "min_family_pbo": min((m.get("family_pbo") for m in members
                                   if m["family"] == fam
                                   and m.get("family_pbo") is not None),
                                  default=None),
        })
    return {
        "batch": "E15_EMOTION_REEVAL_ROSTER",
        "source_report_card": "results/mass_trial/report_card.json",
        "source_evidence_cutoff": report_card.get("evidence_cutoff"),
        "source_honesty": report_card.get("honesty"),
        "n_members": len(members),
        "members": members,
        "families": families,
        "direction_family": DIRECTION_FAMILY,
        "notes": [
            "Descriptive roster only: zero judgment, zero thresholds; batch",
            "membership m and BH-FDR gate decided by the frozen prereg (E15 leg-2).",
            "Reform gates to be imported from science_gates (g2_reform_fdr4d,",
            "REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS, REFORM_TOPN_PER_WAVE) -",
            "no hand-copied judgment lines (r271 single-canon law).",
        ],
        "generated_by": "scripts/emotion_reeval_roster.py",
    }


def run():
    with open(REPORT_CARD, "r", encoding="utf-8", errors="replace") as f:
        report_card = json.load(f)
    roster = build_roster(report_card)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("roster written:", OUT_PATH)
    print("members:", roster["n_members"],
          "families:", len(roster["families"]))
    for fam in roster["families"]:
        flag = " <== direction clue" if fam["direction_clue"] else ""
        print("  %-28s n=%d pbo_min=%s%s" % (
            fam["family"], fam["n_members"], fam["min_family_pbo"], flag))
    return 0


def selftest():
    fixture = {
        "evidence_cutoff": "2026-09-22",
        "honesty": "fixture honesty line",
        "passers": [
            {"candidate_id": "W3-23027", "family": DIRECTION_FAMILY,
             "dsr": 0.4903, "family_pbo": 0.1857, "oos_sharpe_legL": 1.4377,
             "signflip_p": 0.0, "g2_dsr_ok": False, "g2_eligible": False},
            {"candidate_id": "W2-23057", "family": DIRECTION_FAMILY,
             "dsr": 0.5288, "family_pbo": 0.2286, "oos_sharpe_legL": 1.9327,
             "signflip_p": 0.001},
            {"candidate_id": "W3-27009", "family": "seasonal.trend_by_season",
             "dsr": 0.2429, "family_pbo": 0.2714, "oos_sharpe_legL": 0.5},
        ],
    }
    r = build_roster(fixture)
    checks = []
    checks.append(("member count", r["n_members"] == 3))
    checks.append(("sorted by family",
                   [m["candidate_id"] for m in r["members"]] ==
                   ["W3-27009", "W2-23057", "W3-23027"]))
    fam_map = {f["family"]: f for f in r["families"]}
    checks.append(("recurrence flag",
                   fam_map[DIRECTION_FAMILY]["recurrence_ge2"] is True))
    checks.append(("direction clue flag",
                   fam_map[DIRECTION_FAMILY]["direction_clue"] is True))
    checks.append(("best member by sharpe",
                   fam_map[DIRECTION_FAMILY]["best_member"] == "W2-23057"))
    checks.append(("min pbo",
                   fam_map[DIRECTION_FAMILY]["min_family_pbo"] == 0.1857))
    checks.append(("evidence cutoff carried",
                   r["source_evidence_cutoff"] == "2026-09-22"))
    checks.append(("verbatim honesty carried",
                   r["source_honesty"] == "fixture honesty line"))
    ok = True
    for name, cond in checks:
        print("[selftest]", name, "PASS" if cond else "FAIL")
        ok = ok and cond
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "run":
        return run()
    if mode == "selftest":
        return selftest()
    print("usage: emotion_reeval_roster.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
