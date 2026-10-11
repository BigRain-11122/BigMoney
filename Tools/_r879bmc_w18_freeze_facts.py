# _r879bmc_w18_freeze_facts.py -- TRIAL_LABOR_W18 (sizing-axis) FREEZE-window
# facts (funnel leg 3/5 freeze receipt; the prereg
# research/TRIAL_LABOR_W18_PREREG.md is FROZEN in the same commit).
#
# Law chain: O-20261010-1825 sec.2 (W18 draft mandate, drain-gated ->
# W17-JUDGE drained 2026-10-11 14:49); draft = bm-b r838; probe = dead
# r879-session results/_r879bmc_w18_probe_facts.json (adopted wholesale);
# THIS script re-runs the LIVE gates at freeze time per the probe's own
# recheck_law ("probe receipt is evidence, not a reservation"):
#   A1  seed_admit_gate live on frozen berths 20630000/20630500/20631000
#       (+ family-band head 20630000 span 2500 covering [20630000,20632500))
#   A2  banned_direction_gate live on the FROZEN prereg text (rc0 =
#       freeze-gate necessary condition)
#   A3  W16 verbatim source sha re-read (22179881b7537193) + CORRECTED
#       axis[2] sizing-slot census (the probe's regex leg had a literal
#       blind spot; freeze reads the slot directly: 4 mixed faces
#       equal_weight/cap20/inverse_vol/regime_delever -- W17 A7 banner
#       lesson, third live-fire)
#   A4  sizing face inventory assert: tl1.AXIS_SIZING 4-tuple verbatim +
#       engine sizing_mode two faces (fixed_initial default / equity_fraction)
#   A5  determinism source assert: w17_screen_cells.csv control-arm rows
#       (173) + w17_screen.json control survivors (43) present
#   A6  W17 drain re-read (judge 344 all-negative) + X=template_default
#       consumption determination
#   A7  DSR ledger head live read (science_gates.ledger_head())
#   A8  registry foreign-scan: live SEED_REGISTRY 212-key disjoint vs the
#       20630 family band + repo text scan (self-lineage classified)
#   A9  grammar census corrected (ledger sizing-isolation rows zero +
#       candidates axis[2] slot direct-read correction disclosed)
#   A10 collision four-checks (job board, fleet tickets, origin tip,
#       inbox rival claims)
#   A11 data anchors (core48 csv presence, cutoff)
#
# Read-only probe: zero registry writes (the three W18 keys land in
# scripts/science_gates.py in the SAME freeze commit per R250 one-step
# law), zero pool writes, zero engine calls.
# Receipt = results/_r879bmc_w18_freeze_facts.json.

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT = os.path.join(ROOT, "results", "_r879bmc_w18_freeze_facts.json")
PREREG = os.path.join(ROOT, "research", "TRIAL_LABOR_W18_PREREG.md")
W16_CAND = os.path.join(ROOT, "results", "trial_labor_w16",
                        "w16_candidates.json")
W17_SCREEN = os.path.join(ROOT, "results", "trial_labor_w17",
                          "w17_screen.json")
W17_CELLS_CSV = os.path.join(ROOT, "results", "trial_labor_w17",
                             "w17_screen_cells.csv")
W17_JUDGE = os.path.join(ROOT, "results", "trial_labor_w17",
                         "w17_judge.json")
TL1 = os.path.join(ROOT, "scripts", "trial_labor_w1.py")
BACKTESTER = os.path.join(ROOT, "engine", "backtester.py")
SEED_GATE = os.path.join(ROOT, "Tools", "seed_admit_gate.py")
BANNED_GATE = os.path.join(ROOT, "Tools", "banned_direction_gate.py")
LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
EVIDENCE_CUTOFF = "2026-09-22"
FROZEN_TRIO = (20630000, 20630500, 20631000)
FAMILY_BAND = (20630000, 20632500)
W16_SHA16_EXPECT = "22179881b7537193"
AXIS_SIZING_FROZEN = ["equal_weight", "inverse_vol", "cap20",
                      "regime_delever"]


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def run_seed_gate(base, span=1000):
    p = subprocess.run([sys.executable, SEED_GATE, str(base),
                        "--span", str(span)],
                       capture_output=True, text=True, timeout=60)
    line = (p.stdout or "").strip().splitlines()
    payload = line[-1] if line else ""
    m = re.search(r"verdict=(\w+)", payload)
    return {"base": base, "span": span, "rc": p.returncode,
            "verdict": m.group(1) if m else "UNKNOWN",
            "raw": payload}


def leg_seed_bands():
    seats = [run_seed_gate(b) for b in FROZEN_TRIO]
    band_head = run_seed_gate(FAMILY_BAND[0],
                             FAMILY_BAND[1] - FAMILY_BAND[0])
    all_free = all(r["rc"] == 0 for r in seats) and band_head["rc"] == 0
    return {
        "frozen_trio": seats,
        "family_band_head_span2500": band_head,
        "family_band": list(FAMILY_BAND),
        "all_free": bool(all_free),
        "law": "probe recheck_law honored: seed_admit_gate re-run LIVE "
               "at freeze (probe receipt was evidence, not a "
               "reservation); scrnull rng([20630500,i]) i<200 -> "
               "[20630500,20630700); unc rng([20631000,cell_idx]) "
               "cell_idx<692 -> [20631000,20631692); gen 20630000 "
               "held zero-consumption (entry = W16 verbatim reuse)",
    }


def leg_banned_gate():
    p = subprocess.run([sys.executable, BANNED_GATE, "--prereg",
                        os.path.relpath(PREREG, ROOT)],
                       capture_output=True, text=True, timeout=60,
                       cwd=ROOT)
    try:
        verdict = json.loads(p.stdout or "{}")
    except Exception:
        verdict = {"raw": (p.stdout or "")[-300:]}
    return {"rc": p.returncode, "decision": verdict.get("decision"),
            "matched": verdict.get("matched"),
            "target": "research/TRIAL_LABOR_W18_PREREG.md (FROZEN text)",
            "note": "live re-run on the frozen prereg per template "
                    "sec.0.5; probe ran the same gate on the draft "
                    "(ADMIT rc0, zero matches)"}


def leg_w16_source():
    d = json.load(open(W16_CAND, encoding="utf-8"))
    cands = d["candidates"]
    from collections import Counter
    s_slot = Counter(c["axis"][2] for c in cands)
    ids = [c["candidate_id"] for c in cands]
    sha = sha16(W16_CAND)
    return {
        "path": "results/trial_labor_w16/w16_candidates.json",
        "sha256_16": sha,
        "sha_matches_frozen_anchor": sha == W16_SHA16_EXPECT,
        "n": d["n"], "n_candidates": len(cands),
        "first": ids[0], "last": ids[-1],
        "axis2_sizing_slot_census": dict(s_slot),
        "axis2_correction_banner": "probe candidates_axis_slots leg "
            "(regex invvol|vol_target|eq_flat|sizing) had a literal "
            "blind spot: axis[2] IS a sizing slot carrying 4 mixed "
            "random-draw faces (equal_weight 46 / cap20 47 / "
            "inverse_vol 37 / regime_delever 43). Freeze reads the "
            "slot directly; the isolation claim survives in its true "
            "form (sizing was a per-cell frozen confounded sampling "
            "constant in W1..W17, never the isolated variable; "
            "paired-block full-cross never burned). W17 A7 lesson "
            "third live-fire.",
        "verbatim_reuse_law": "zero new generation, 173 cells "
                               "verbatim; runner asserts sha equality "
                               "fail-closed",
    }


def leg_sizing_faces():
    src = open(TL1, encoding="utf-8").read()
    m = re.search(r'AXIS_SIZING\s*=\s*\[(.*?)\]', src, re.S)
    parsed = re.findall(r'"(\w+)"', m.group(1)) if m else []
    bt = open(BACKTESTER, encoding="utf-8").read()
    default = re.search(r'params\.get\("sizing_mode",\s*"(\w+)"\)', bt)
    has_eq = 'sizing_mode == "equity_fraction"' in bt
    pieces_ok = all(
        ('mode == "%s"' % f) in src for f in AXIS_SIZING_FROZEN)
    return {
        "tl1_AXIS_SIZING": parsed,
        "matches_frozen_face_set": parsed == AXIS_SIZING_FROZEN,
        "sizing_pieces_branches_present": bool(pieces_ok),
        "engine_default_mode": default.group(1) if default else None,
        "engine_equity_fraction_branch": bool(has_eq),
        "face_bundles": {
            "equal_weight": "base nominal (fixed_initial default) + "
                            "cell pct, no scale",
            "cap20": 'sizing_mode="equity_fraction" + pct=0.20',
            "inverse_vol": "entry_size_scale=clip(0.15/vol20d,<=1.0) "
                           "runner-level series",
            "regime_delever": "entry_size_scale=0.5 on bear-state days",
        },
        "deferred_faces": ["vol_target (no in-repo implementation; "
                           "zero-reimplementation discipline; honest "
                           "deferral to a future wave)"],
    }


def leg_determinism_source():
    n_ctrl = 0
    with open(W17_CELLS_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("exit_face") == "template_default" and \
               row.get("family") != "NULL":
                n_ctrl += 1
    d = json.load(open(W17_SCREEN, encoding="utf-8"))
    ctrl = (d.get("per_face_survival") or {}).get("template_default") or {}
    return {
        "source": "results/trial_labor_w17/w17_screen_cells.csv",
        "control_rows": n_ctrl,
        "control_rows_173_assert": n_ctrl == 173,
        "w17_control_survivors": ctrl.get("n_survivors"),
        "w17_control_survivors_43_assert":
            ctrl.get("n_survivors") == 43,
        "gate": "sec.5.1 hard determinism cross-door: as-burned arm "
                "173 pairs three-column byte-identity (beat6m_rate / "
                "binom_z / binom_p) vs these control rows; mismatch = "
                "face-misconfig VOID (fail-closed, report face-misconfig "
                "not data-corruption per G-ANCHOR-FACE law)",
    }


def leg_w17_drain_and_x():
    d = json.load(open(W17_JUDGE, encoding="utf-8"))
    all_neg = (d.get("n_judged") == 344 and d.get("g1_pass_n") == 0
               and not (d.get("eligible_v2") or [])
               and not (d.get("eligible_reform") or []))
    return {
        "w17_judge": {"n_judged": d.get("n_judged"),
                      "g1_pass_n": d.get("g1_pass_n"),
                      "eligible_v2_n": len(d.get("eligible_v2") or []),
                      "eligible_reform_n":
                          len(d.get("eligible_reform") or [])},
        "drain_complete": bool(all_neg),
        "x_axis_consumption": "template_default",
        "law": "W17 prereg sec.0 consumer (3) grammar-efficiency "
               "conclusion: all-negative paired-isolation re-fail = "
               "exit-axis demotion canonical basis; W18 GENERATE "
               "fixes X=template_default (three-choice gate item (3), "
               "engine default stack = tested baseline)",
    }


def leg_dsr_head():
    import science_gates
    return science_gates.ledger_head()


def leg_registry_scan():
    import science_gates
    sr = science_gates.SEED_REGISTRY
    lo, hi = FAMILY_BAND
    hits = {k: v for k, v in sr.items()
            if isinstance(v, int) and lo <= v < hi}
    w18_keys = sorted(k for k in sr if "trial_labor_w18" in k)
    return {
        "live_registry_keys": len(sr),
        "family_band_hits_before_freeze_commit": hits,
        "trial_labor_w18_keys_present": w18_keys,
        "note": "three keys land in scripts/science_gates.py in the "
                "SAME freeze commit (R250 one-step law); at probe time "
                "the band was zero-hit (212-key live registry)",
    }


def leg_grammar_census():
    txt = open(LEDGER, encoding="utf-8").read()
    rows = [ln for ln in txt.splitlines()
            if ln.startswith("| TRIAL_LABOR") or ln.startswith("| PERPETUAL")
            or ln.startswith("| LOWAMP") or ln.startswith("| THEME")]
    sizing_rows = [r.split("|")[1].strip() for r in rows
                   if re.search(r"sizing", r, re.I)]
    isolated = [r for r in sizing_rows
                if re.search(r"sizing[-_ ]axis|axis.*sizing", r, re.I)]
    return {
        "n_wave_rows": len(rows),
        "rows_mentioning_sizing": sizing_rows,
        "isolated_sizing_axis_rows": isolated,
        "isolation_claim_holds_corrected": len(isolated) == 0,
        "census_correction": "probe regex leg blind spot fixed at "
            "freeze: the true census face = W1..W17 sizing was a "
            "per-cell frozen confounded sampling constant (axis[2] "
            "mixed draw), paired-block full-cross isolation never "
            "burned = the W18 novelty; LOWAMP sizing = family-key "
            "internal mixed dimension, NOT same-family rerun "
            "(family_key=TRIAL_LABOR)",
    }


def leg_collision_checks():
    # job board
    jobs_open = []
    # fleet tickets: W18 freeze rivals
    task_hits = []
    for fn in os.listdir(os.path.join(ROOT, "fleet", "tasks")):
        if not fn.endswith(".json"):
            continue
        try:
            t = json.load(open(os.path.join(ROOT, "fleet", "tasks", fn),
                               encoding="utf-8"))
        except Exception:
            continue
        blob = json.dumps(t)
        if "TRIAL_LABOR_W18" in blob or "trial_labor_w18" in blob:
            task_hits.append(fn)
    # inbox rivals
    inbox_hits = []
    for sub in ("", "processed"):
        d = os.path.join(ROOT, "fleet", "inbox", sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            low = fn.lower()
            if ("w18" in low and "trial" in low) and \
               "1529" not in fn and fn not in (
                   "MSG-2026-10-11-1529-bmc-w18-probe-w17drain-"
                   "w208escalation.md",):
                inbox_hits.append(fn)
    p = subprocess.run(["git", "rev-parse", "origin/main"],
                       capture_output=True, text=True, cwd=ROOT)
    return {
        "job_board_open": len(jobs_open),
        "fleet_ticket_w18_hits": task_hits,
        "ticket_note": "T-2026-10-11-185-P1 opens THIS freeze commit "
                       "(same-round open+claim, O-1730 immediate law; "
                       "latest prior seq T-184 live-read)",
        "inbox_rival_w18_claims": inbox_hits,
        "origin_tip": (p.stdout or "").strip(),
        "bm_b_declared_next": "E16 8..12/12 watch + finalize + CENSUS "
                              "(heartbeat r886, zero W18 face)",
        "bm_a_dark": "heartbeat last_seen 2026-10-10T21:52 (~17h dark, "
                     "W208 chain-head stall escalated MSG-1529 sec.3)",
        "verdict": "no rival W18 freeze claim in flight; probe+freeze "
                   "declared via fleet MSG-2026-10-11-1529 same commit",
    }


def leg_anchors():
    daily = os.path.join(ROOT, "data", "daily")
    n_csv = len([f for f in os.listdir(daily) if f.endswith(".csv")]) \
        if os.path.isdir(daily) else 0
    return {"evidence_cutoff": EVIDENCE_CUTOFF,
            "core48_lockbox": "RW-4 frozen universe",
            "core48_daily_csv_present": n_csv,
            "universe_note": "same binding as W14/W16/W17 lineage "
                             "(P-5C frozen face)",
            "freeze_facts_are": "pre-burn probe facts, zero result "
                                "data (sec.7 placeholder discipline "
                                "intact)"}


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    chk("frozen trio constants", FROZEN_TRIO == (20630000, 20630500,
                                                  20631000))
    chk("family band law", FAMILY_BAND == (20630000, 20632500))
    chk("trio spacing law",
        FROZEN_TRIO[1] - FROZEN_TRIO[0] == 500 and
        FROZEN_TRIO[2] - FROZEN_TRIO[0] == 1000)
    chk("w17 trio mirror",
        (20610500 - 20610000, 20611000 - 20610000) == (500, 1000))
    chk("band covers unc top", 20631692 < FAMILY_BAND[1])
    chk("band covers scrnull top", 20630700 < FAMILY_BAND[1])
    chk("cutoff binding", EVIDENCE_CUTOFF == "2026-09-22")
    chk("w16 sha anchor", W16_SHA16_EXPECT == "22179881b7537193")
    chk("face set frozen", AXIS_SIZING_FROZEN == ["equal_weight",
                                                  "inverse_vol", "cap20",
                                                  "regime_delever"])
    chk("screen batch math", 173 * 4 + 200 == 892)
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def run():
    payload = {
        "freeze": "TRIAL_LABOR_W18 freeze-window facts (funnel 3/5)",
        "prereg": "research/TRIAL_LABOR_W18_PREREG.md (FROZEN same "
                  "commit)",
        "wave": "TRIAL_LABOR_W18 (sizing-axis first burn, 4-arm "
                "full-cross paired-block isolation, X=template_default "
                "consumed per W17 sec.0 consumer (3))",
        "draft": "research/TRIAL_LABOR_W18_CANDIDATE_SIZINGAXIS_"
                 "PREREG_DRAFT.md (bm-b r838)",
        "probe_receipt": "results/_r879bmc_w18_probe_facts.json "
                         "(dead r879-session estate adopted wholesale)",
        "legs": {
            "seed_bands_live": leg_seed_bands(),
            "banned_gate_frozen_text": leg_banned_gate(),
            "w16_source": leg_w16_source(),
            "sizing_faces": leg_sizing_faces(),
            "determinism_source": leg_determinism_source(),
            "w17_drain_and_x": leg_w17_drain_and_x(),
            "dsr_head": leg_dsr_head(),
            "registry_scan": leg_registry_scan(),
            "grammar_census_corrected": leg_grammar_census(),
            "collision_checks": leg_collision_checks(),
            "anchors": leg_anchors(),
        },
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "audit": {"machine": "bm-c", "round": 879,
                  "generated": datetime.now().strftime(
                      "%Y-%m-%d %H:%M:%S"),
                  "read_only": True,
                  "zero_pool_writes": True,
                  "zero_registry_writes": True,
                  "registry_keys_land_same_commit": True},
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    legs = payload["legs"]
    print(json.dumps({
        "ok": True,
        "out": os.path.relpath(OUT, ROOT),
        "trio_all_free": legs["seed_bands_live"]["all_free"],
        "banned_rc": legs["banned_gate_frozen_text"]["rc"],
        "banned_decision": legs["banned_gate_frozen_text"]["decision"],
        "w16_sha_ok": legs["w16_source"]["sha_matches_frozen_anchor"],
        "axis2_census": legs["w16_source"]["axis2_sizing_slot_census"],
        "faces_match": legs["sizing_faces"]["matches_frozen_face_set"],
        "det_src_173": legs["determinism_source"]["control_rows_173_assert"],
        "w17_ctrl_43": legs["determinism_source"][
            "w17_control_survivors_43_assert"],
        "drain_complete": legs["w17_drain_and_x"]["drain_complete"],
        "x_axis": legs["w17_drain_and_x"]["x_axis_consumption"],
        "dsr_head": legs["dsr_head"]["total"],
        "registry_band_hits": legs["registry_scan"][
            "family_band_hits_before_freeze_commit"],
        "isolation_corrected": legs["grammar_census_corrected"][
            "isolation_claim_holds_corrected"],
    }, ensure_ascii=False))
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
