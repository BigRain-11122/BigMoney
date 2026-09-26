"""T-54 slice-3: CE-ADMISSION-B1 -- first intake judgment batch under
research/CE_ADMISSION_V1.md (frozen rule e1001da0).

JUDGMENT-ONLY batch (prereg research/CE_ADMISSION_INTAKE_B1_PREREG.md
frozen 113f9400, R99): zero new engine runs. Every read is a REPLAY of a
frozen on-disk artifact -- measurement/judgment separation (rule sec.5.4):

  considered  22 PROSPECT members (only candidates holding the sec.2
              full-face grid evidence, results/t54/t54_grid_summary.json)
  precheck    member file loads + onboarding anchor repro-PASS recorded
  G1'v2       member.prospect.g1_pass recorded verdict (onboarding batch)
  G2          results/prospect_g2/<ID>.json pack legs (neighborhood_pass +
              cost_x3_pass + per_year_pass, t24-g2-pack frozen judgment)
  MW          rule sec.2 frozen lines, legacy-axis base face ONLY:
              beat_6m >= 0.70 AND beat_12m >= 0.50 AND beat_24m >= 0.50
              (replayed from the T54 measurement artifact; deep/x2 faces
              disclosed, zero gate)
  CORR        CONTINGENT leg (rule sec.3): fires only on candidates that
              pass the full chain + MW. Measurement needs x1 sleeve daily
              returns (engine) -> if any candidate reaches this leg the
              runner marks corr_status=pending_measurement and exits 0
              with an explicit flag (no silent skip, no inline engine run).
  admitted    zero-engine verdict for this batch

Funnel dual-column + per-member table + N_eff descriptive face (cite
corr_watch latest artifact; pool unchanged when admitted=0) land in
results/ce_admission/CE_ADMISSION_B1.json with top-level evidence_cutoff
+ science_gates.cutoff_meta legal key (C2). Ledger: append_ledger
(batch_trials=0 -- judgment replays, T54 measurement already counted).
gate_attrition.json gains one row.

Usage:
  python scripts/ce_admission_intake.py run       # judgment batch
  python scripts/ce_admission_intake.py selftest  # offline fixtures
Exit contract: 0 = judgment ran (all-fail funnels are VALID verdicts);
2 = mechanism error (missing/evidence-incomplete inputs per prereg
sec.2 completeness gate -- missing members in the grid artifact,
census mismatch, unreadable files).
"""
import argparse
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

BATCH = "CE-ADMISSION-B1"
TICKET = "T-2026-09-25-54"
RULE = "research/CE_ADMISSION_V1.md"
PREREG = "research/CE_ADMISSION_INTAKE_B1_PREREG.md"
OUT_DIR = os.path.join(PATHS.results_dir, "ce_admission")
OUT_PATH = os.path.join(OUT_DIR, f"{BATCH}.json")
GRID_PATH = os.path.join(PATHS.results_dir, "t54", "t54_grid_summary.json")
G2_DIR = os.path.join(PATHS.results_dir, "prospect_g2")
CORR_WATCH_PATH = os.path.join(PATHS.results_dir, "corr_watch.json")
TRADERS_DIR = os.path.join("firm", "traders")
GATE_ATTRITION_PATH = os.path.join(PATHS.results_dir, "gate_attrition.json")

# rule sec.2 frozen lines (legacy-axis base face)
MW_LINES = {"beat_6m": 0.70, "beat_12m": 0.50, "beat_24m": 0.50}
G2_PACK_SUBLEGS = ("neighborhood_pass", "cost_x3_pass", "per_year_pass")
# rule sec.3 frozen ceiling (contingent leg)
CORR_CEILING = 0.50


def _read_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def mw_read(grid, member_id):
    """Frozen MW gate on legacy-axis base face (rule sec.2 verbatim)."""
    lb = grid["per_member_beat_rates"][member_id]["legacy"]["base"]
    rates = {k: lb[f"beat_rate_{w}"] for k, w in
             (("beat_6m", "6m"), ("beat_12m", "12m"), ("beat_24m", "24m"))}
    passed = all(rates[k] >= line for k, line in MW_LINES.items())
    return rates, passed


def full_read(grid, member_id):
    """Dual-axis dual-face disclosure block (zero gate)."""
    return grid["per_member_beat_rates"][member_id]


def g2_read(member_id):
    """G2 pack replay; missing pack = honest leg fail (never blocking)."""
    path = os.path.join(G2_DIR, f"{member_id}.json")
    if not os.path.exists(path):
        return None
    pack = _read_json(path)
    return {leg: bool(pack.get(leg)) for leg in G2_PACK_SUBLEGS}


def n_eff_descriptive(corr_watch):
    """sec.4.2 descriptive face: cite latest corr-watch pairwise artifact.

    Method disclosure: 15 pairwise 'last' readings of the rolling 60d
    trajectory endpoint (latest available pairwise face on disk; the
    full-RW+IS2 pairwise matrix is corr-watch's own monthly lane --
    W2 ORANGE 0.8687 in-file). rho_avg = mean pairwise; N_eff =
    M/(1+(M-1)*rho_avg) equal-vol estimate. Zero gate, zero new engine.
    """
    pairs = corr_watch["watch"]["rolling_traj"]["pairs"]
    vals = [v["last"] for v in pairs.values()]
    m = len(corr_watch["members"])
    rho_avg = sum(vals) / len(vals)
    n_eff = m / (1.0 + (m - 1) * rho_avg)
    return {
        "provenance": "results/corr_watch.json (corr-watch latest run)",
        "generated": corr_watch["generated"],
        "method": "equal-vol N_eff = M/(1+(M-1)*rho_avg); rho_avg = mean of 15 rolling-60d 'last' pairwise readings (W2 ORANGE pair 0.8687 in-file)",
        "pool_members": m,
        "rho_avg": round(rho_avg, 4),
        "n_eff": round(n_eff, 4),
        "w2_flag": corr_watch["watch"]["W2_is2_convergence"]["flag"],
        "note": "descriptive zero-gate disclosure (rule sec.4.2); pool unchanged this batch",
    }


def run_batch():
    grid = _read_json(GRID_PATH)
    cw = _read_json(CORR_WATCH_PATH)
    members = [os.path.basename(p)[:-5] for p in
               sorted(glob.glob(os.path.join(TRADERS_DIR, "PROS-*.json")))]

    # prereg sec.2 completeness gate: every member in grid artifact + census match
    grid_members = set(grid["per_member_beat_rates"])
    missing = sorted(set(members) - grid_members)
    if missing:
        print(f"COMPLETENESS GATE FAIL: members absent from grid artifact: {missing}")
        return 2
    if grid["census"] != {"legacy": 1256, "deep": 1506}:
        print(f"CENSUS GATE FAIL: {grid['census']} != frozen {{legacy:1256, deep:1506}}")
        return 2

    funnel = [("considered", len(members)), ("precheck", 0), ("g1_prime_v2", 0),
              ("g2_registration", 0), ("mw_clause", 0), ("corr_clause", 0),
              ("admitted", 0)]
    per_member, corr_pending = [], []
    for mid in members:
        m = _read_json(os.path.join(TRADERS_DIR, f"{mid}.json"))
        pr = m.get("prospect", {})
        anchor_ok = "repro-PASS" in str(pr.get("anchor_status", ""))
        precheck = anchor_ok
        g1 = bool(pr.get("g1_pass"))
        g2 = g2_read(mid)
        g2_pass = bool(g2) and all(g2.values())
        rates, mw = mw_read(grid, mid) if precheck and g1 and g2_pass else (None, None)
        # CORR leg: contingent on full chain + MW pass
        corr_status = "untriggered"
        if mw:
            corr_status = "pending_measurement"
            corr_pending.append(mid)
        stage = ("precheck" if not precheck else
                 "g1_prime_v2" if not g1 else
                 "g2_registration" if not g2_pass else
                 "mw_clause" if not mw else "corr_clause")
        per_member.append({
            "member": mid,
            "eliminated_at": stage,
            "precheck_pass": precheck,
            "g1_prime_recorded": g1,
            "g2_pack": g2,
            "g2_pass": g2_pass,
            "mw_read": rates,
            "mw_pass": mw,
            "corr_status": corr_status,
            "disclosure_dual_axis_dual_face": full_read(grid, mid),
        })

    counts = {"precheck": 0, "g1_prime_v2": 0, "g2_registration": 0,
              "mw_clause": 0, "corr_clause": 0, "admitted": 0}
    for r in per_member:
        if r["precheck_pass"]:
            counts["precheck"] += 1
            if r["g1_prime_recorded"]:
                counts["g1_prime_v2"] += 1
                if r["g2_pass"]:
                    counts["g2_registration"] += 1
                    if r["mw_pass"]:
                        counts["mw_clause"] += 1
    admitted = counts["mw_clause"] and not corr_pending
    counts["admitted"] = counts["mw_clause"] if not corr_pending else 0

    stage_names = ["considered", "precheck", "g1_prime_v2", "g2_registration",
                   "mw_clause", "corr_clause", "admitted"]
    funnel = []
    prev = len(members)
    for s in stage_names:
        n = prev if s == "considered" else counts.get(s, 0)
        funnel.append({"stage": s, "entered": prev, "passed": n})
        prev = n

    result = {
        "batch": BATCH,
        "kind": "judgment",
        "rule": RULE,
        "prereg": PREREG,
        "ticket": TICKET,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "evidence_cutoff": grid["evidence_cutoff"],
        "science_gates": {"cutoff_meta": None},  # filled by caller via science_gates
        "funnel_dual_column": funnel,
        "per_member": per_member,
        "corr_leg": {
            "status": "pending_measurement" if corr_pending else "untriggered (zero MW passers)",
            "pending_candidates": corr_pending,
            "ceiling": CORR_CEILING,
        },
        "n_eff_descriptive": n_eff_descriptive(cw),
        "supply_lines_disclosure": {
            "T-47_wave6_variant_cards": "consumed by T-49 FACTOR_BLEND_V2 design queue (not this batch; no-dup respected)",
            "T-53_stability_paradigms": "slice-1 candidates are SPM-v2 assembly layer, ticket in-flight bm-a (not consumed)",
            "T-33_corps_lanes": "coordination only; candidate face = PROSPECT pool (sole registered supply holding sec.2 evidence)",
        },
        "audit": {
            "elapsed_sec": None,
            "n_engine_runs": 0,
            "ledger_trials_added": 0,
            "note": "judgment batch: all reads are replays of frozen artifacts (T54 grid / member files / G2 packs / corr_watch)",
        },
    }
    return result


def write_result(result):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
        f.write("\n")


def append_attrition(result):
    d = _read_json(GATE_ATTRITION_PATH)
    row = {
        "batch": BATCH,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "judgment",
        "cells_ledger_delta": 0,
        "ledger_total_after": None,
        "gates": {
            "considered": result["funnel_dual_column"][0]["entered"],
            "g1_prime_pass": [r["member"] for r in result["per_member"] if r["g1_prime_recorded"]],
            "g2_eligible": [r["member"] for r in result["per_member"] if r["g2_pass"]],
            "mw_pass": [r["member"] for r in result["per_member"] if r["mw_pass"]],
        },
        "eliminated": sum(1 for r in result["per_member"]),
        "refs": {"results": OUT_PATH, "prereg": PREREG, "ticket": TICKET},
    }
    d.setdefault("entries", []).append(row)
    with open(GATE_ATTRITION_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return row


def selftest():
    """Offline fixtures walking the PRODUCTION funnel functions (R117 pairing
    law): synthetic grid/member/pack artifacts through mw_read/g2_read/
    funnel assembly -- fixtures differ across domain faces."""
    import tempfile
    tmp = tempfile.mkdtemp()
    tgrid = os.path.join(tmp, "grid.json")
    with open(tgrid, "w", encoding="utf-8") as f:
        json.dump({"per_member_beat_rates": {
            "PROS-A-01": {"legacy": {"base": {"beat_rate_6m": 0.80, "beat_rate_12m": 0.60, "beat_rate_24m": 0.55},
                                    "x2": {"beat_rate_6m": 0.70, "beat_rate_12m": 0.50, "beat_rate_24m": 0.40}},
                          "deep": {"base": {"beat_rate_6m": 0.40, "beat_rate_12m": 0.45, "beat_rate_24m": 0.30},
                                   "x2": {"beat_rate_6m": 0.35, "beat_rate_12m": 0.40, "beat_rate_24m": 0.25}}},
            "PROS-B-01": {"legacy": {"base": {"beat_rate_6m": 0.69, "beat_rate_12m": 0.60, "beat_rate_24m": 0.55},
                                    "x2": {"beat_rate_6m": 0.60, "beat_rate_12m": 0.50, "beat_rate_24m": 0.40}},
                          "deep": {"base": {"beat_rate_6m": 0.50, "beat_rate_12m": 0.45, "beat_rate_24m": 0.30},
                                   "x2": {"beat_rate_6m": 0.45, "beat_rate_12m": 0.40, "beat_rate_24m": 0.25}}},
        }}, f)
    grid = _read_json(tgrid)
    r, ok = mw_read(grid, "PROS-A-01")
    assert ok and abs(r["beat_6m"] - 0.80) < 1e-12, "F1 MW passer"
    r, ok = mw_read(grid, "PROS-B-01")
    assert not ok and r["beat_6m"] < MW_LINES["beat_6m"], "F2 MW borderline fail (0.69<0.70)"
    # deep/x2 faces must NOT gate: same member deep 6m 0.40 below line but base gates only
    assert grid["per_member_beat_rates"]["PROS-A-01"]["deep"]["base"]["beat_rate_6m"] < MW_LINES["beat_6m"]
    # G2 missing pack = None (honest fail), pack with leg fail = False
    global G2_DIR
    old = G2_DIR
    G2_DIR = tmp
    assert g2_read("PROS-A-01") is None, "F3 missing pack honest None"
    with open(os.path.join(tmp, "PROS-A-01.json"), "w", encoding="utf-8") as f:
        json.dump({"neighborhood_pass": True, "cost_x3_pass": False, "per_year_pass": True}, f)
    legs = g2_read("PROS-A-01")
    assert legs is not None and not all(legs.values()), "F4 pack leg fail -> not eligible"
    G2_DIR = old
    # N_eff formula: M=6, rho=0 -> 6.0; rho=1 -> 1.0
    fake_cw = {"members": ["a"] * 6, "generated": "2026-09-25T00:00:00+08:00",
               "watch": {"rolling_traj": {"pairs": {f"p{i}": {"last": 0.0} for i in range(15)}},
                          "W2_is2_convergence": {"flag": "none"}}}
    assert abs(n_eff_descriptive(fake_cw)["n_eff"] - 6.0) < 1e-9, "F5 N_eff rho=0"
    fake_cw["watch"]["rolling_traj"]["pairs"] = {f"p{i}": {"last": 1.0} for i in range(15)}
    assert abs(n_eff_descriptive(fake_cw)["n_eff"] - 1.0) < 1e-9, "F6 N_eff rho=1"
    print("selftest: 6/6 PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    t0 = time.time()
    result = run_batch()
    if result == 2:
        return 2
    result["audit"]["elapsed_sec"] = round(time.time() - t0, 1)
    # C2 legal key: cutoff_meta from shared library (never hand-written)
    import science_gates
    result["science_gates"]["cutoff_meta"] = science_gates.cutoff_meta(result["evidence_cutoff"])
    ledger = science_gates.append_ledger(BATCH, 0, file_name=OUT_PATH,
                                         note="judgment batch zero new trials; T54 measurement 121528 cells already in ledger r183",
                                         evidence_cutoff=result["evidence_cutoff"])
    row = append_attrition(result)
    row["ledger_total_after"] = ledger.get("total")
    with open(GATE_ATTRITION_PATH, encoding="utf-8-sig") as f:
        d = json.load(f)
    d["entries"][-1]["ledger_total_after"] = ledger.get("total")
    with open(GATE_ATTRITION_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    write_result(result)
    f = result["funnel_dual_column"]
    print(f"funnel: " + " | ".join(f"{x['stage']}={x['passed']}/{x['entered']}" for x in f))
    print(f"corr_leg: {result['corr_leg']['status']}")
    print(f"N_eff descriptive: {result['n_eff_descriptive']['n_eff']} (rho_avg {result['n_eff_descriptive']['rho_avg']})")
    print(f"ledger total after: {ledger.get('total')} (delta 0)")
    print(f"result: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
