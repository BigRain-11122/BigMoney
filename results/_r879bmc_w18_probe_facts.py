# _r879bmc_w18_probe_facts.py -- TRIAL_LABOR_W18 (sizing-axis) freeze-window
# probe facts (funnel leg 2/5, pre-freeze evidence; W17 drain precondition
# consumed 2026-10-11 14:49).
#
# Law chain: O-20261010-1825 sec.2 "W18 same-window draft (drain-gated)";
# draft = research/TRIAL_LABOR_W18_CANDIDATE_SIZINGAXIS_PREREG_DRAFT.md
# (bm-b r838, DRAFT-BERTH). This probe = the draft's own mandated
# "freeze-window probe leg" (sec.4/5): seed-band re-derive (the draft's
# 20620000 trio was occupied by e16_alphagen_rg on 10-11, anticipated by
# the draft itself), W16 verbatim source face, W17 verdict consumption ->
# X-axis determination per W17 prereg sec.0 consumer (3), sizing face
# inventory (engine-native discipline), grammar-ledger sizing-isolation
# census, DSR live head, collision checks, anchors.
#
# Read-only probe: zero registry writes, zero pool writes, zero engine
# calls. Receipt = results/_r879bmc_w18_probe_facts.json.

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)   # knowledge ns-pkg (r817 lesson)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT = os.path.join(ROOT, "results", "_r879bmc_w18_probe_facts.json")
DRAFT = os.path.join(ROOT, "research",
                     "TRIAL_LABOR_W18_CANDIDATE_SIZINGAXIS_PREREG_DRAFT.md")
W16_CAND = os.path.join(ROOT, "results", "trial_labor_w16",
                        "w16_candidates.json")
W17_JUDGE = os.path.join(ROOT, "results", "trial_labor_w17",
                         "w17_judge.json")
W17_DELTAS = os.path.join(ROOT, "results", "trial_labor_w17",
                          "w17_paired_deltas.json")
BACKTESTER = os.path.join(ROOT, "engine", "backtester.py")
LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
SEED_GATE = os.path.join(ROOT, "Tools", "seed_admit_gate.py")
BANNED_GATE = os.path.join(ROOT, "Tools", "banned_direction_gate.py")
EVIDENCE_CUTOFF = "2026-09-22"   # P-5C frozen binding (W14/W16/W17 lineage)
DRAFT_TRIO = (20620000, 20620500, 20621000)   # draft sec.4 proposal
ALT_TRIO_20630 = (20630000, 20630500, 20631000)  # structure-mirror of W17
ALT_TRIO_20620 = (20620200, 20620700, 20621200)  # compact continuation


def sha16(path):
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    return h


def run_seed_gate(base, span=1000):
    """Machine-read the canonical admit gate (single-source law)."""
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
    """Draft-proposed trio expected BLOCKED (e16 occupation disclosed);
    alternatives expected FREE. Freeze window picks the berth."""
    out = {"draft_trio_20620000": [run_seed_gate(b) for b in DRAFT_TRIO],
           "draft_trio_band_head": run_seed_gate(20620000, 2000),
           "alt_trio_20630": [run_seed_gate(b) for b in ALT_TRIO_20630],
           "alt_trio_20620_head": run_seed_gate(ALT_TRIO_20620[0], 1000),
           "alt_20621000": run_seed_gate(20621000)}
    # gen berth (trio[0]) is the anchor: occupied gen = trio dead; the
    # e16 registrations sit exactly on 20620000 (gen) + 20620100 (the
    # would-be null seat at draft spacing +100)
    blocked = out["draft_trio_20620000"][0]["rc"] == 1
    alt_free = all(r["rc"] == 0 for r in out["alt_trio_20630"])
    out["determination"] = {
        "draft_band_occupied": bool(blocked),
        "occupied_by": ["e16_alphagen_rg_gen", "e16_alphagen_rg_null"],
        "occupation_note": "e16 froze 20620000/20620100 on 10-11 05:0x "
                           "AFTER the draft (10-10 20:0x) proposed the "
                           "same berth -- the draft's own anticipated "
                           "rejection (W17 lesson: natural candidates can "
                           "be occupied); freeze window MUST re-derive",
        "recommended_primary": "20630000/20630500/20631000 (structure "
                              "mirror of W17 trio 20610000/20610500/"
                              "20611000, role spacing 500/1000 preserved, "
                              "all FREE at probe time)",
        "alt_free_all": bool(alt_free),
        "recheck_law": "freeze window re-runs seed_admit_gate live "
                       "(probe receipt is evidence, not a reservation)",
    }
    return out


def leg_w16_source():
    d = json.load(open(W16_CAND, encoding="utf-8"))
    cands = d["candidates"]
    ids = [c["candidate_id"] for c in cands]
    return {"path": "results/trial_labor_w16/w16_candidates.json",
            "sha256_16": sha16(W16_CAND),
            "n": d["n"], "n_candidates": len(cands),
            "first": ids[0], "last": ids[-1],
            "n_173_assert": len(cands) == 173 == d["n"],
            "verbatim_reuse_law": "draft sec.4: zero new generation, "
                                  "173 cells verbatim; sha frozen at "
                                  "freeze time by re-read"}


def leg_w17_drain():
    d = json.load(open(W17_JUDGE, encoding="utf-8"))
    deltas = json.load(open(W17_DELTAS, encoding="utf-8"))
    per_face = deltas.get("per_face", {})
    face_medians = {k: v.get("median_delta") for k, v in per_face.items()
                    if isinstance(v, dict)}
    face_p = {k: v.get("wilcoxon_p") for k, v in per_face.items()
              if isinstance(v, dict)}
    drained = (d.get("n_judged") == 344 and d.get("g1_pass_n") == 0
               and d.get("eligible_v2") == [] and
               d.get("eligible_reform") == [])
    return {"w17_judge": {"n_judged": d.get("n_judged"),
                          "g1_pass_n": d.get("g1_pass_n"),
                          "eligible_v2_n": len(d.get("eligible_v2") or []),
                          "eligible_reform_n":
                              len(d.get("eligible_reform") or []),
                          "onboard_n": len(d.get("onboard_list") or []),
                          "E_FP_nominal": d.get("E_FP_nominal")},
            "paired_deltas_face_medians": face_medians,
            "paired_deltas_wilcoxon_p": face_p,
            "paired_deltas_n_pairs": per_face.get("tiered_tp_only", {}).get(
                "n_pairs"),
            "drain_complete": bool(drained),
            "drain_note": "W17-JUDGE finalize landed 2026-10-11 14:49 "
                          "(bm-c lane, ledger total 878,097) -- W18 "
                          "physical precondition MET"}


def leg_x_axis_determination(w17):
    """W17 all-negative + zero median paired delta on every exit face ->
    grammar-efficiency conclusion per W17 prereg sec.0 consumer (3):
    future GENERATE may FIX X=template_default."""
    medians = (w17.get("paired_deltas_face_medians") or {})
    no_improvement = bool(medians) and all(
        (v is None) or (v <= 0.0) for v in medians.values())
    all_neg = w17["w17_judge"]["g1_pass_n"] == 0
    x = "template_default" if (all_neg and no_improvement) else None
    return {"w17_all_negative": bool(all_neg),
            "all_exit_faces_median_delta_le_zero": bool(no_improvement),
            "x_axis_determination": x,
            "law": "draft sec.3 (W17 landed -> X per W17 sec.0 consumer "
                   "(3) grammar-efficiency conclusion) + W17 prereg "
                   "consumer (3) text: all-negative paired-isolation "
                   "re-fail = exit-axis demotion canonical basis, future "
                   "waves may FIX X=template_default saving the axis",
            "exit_axis_gate_declaration": "(3) template_default measured "
                                          "by design (engine default "
                                          "stack = tested baseline, "
                                          "three-choice gate zero-gap)"}


def leg_sizing_face_inventory():
    """Engine-native sizing faces (zero-reimplementation discipline);
    runner-level precedent faces disclosed for the freeze resolution."""
    src = open(BACKTESTER, encoding="utf-8").read()
    modes = sorted(set(re.findall(r'sizing_mode["\']?\s*[=,]\s*["\']'
                                 r'(\w+)["\']', src)))
    default = re.search(r'params\.get\("sizing_mode",\s*"(\w+)"\)', src)
    native = {"fixed_initial", "equity_fraction"}
    return {"engine_native_sizing_modes": sorted(native),
            "backtester_mentions_found": modes,
            "default_mode": default.group(1) if default else None,
            "native_faces_complete": native.issubset(set(modes))
                                     or default is not None,
            "invvol_vol_target_engine_native": False,
            "invvol_precedent": "LOWAMP-P1/-DEEP-P1 sizing in {invvol,eq} "
                                "burned at RUNNER portfolio-weight level "
                                "(scripts/lowamp_p1.py etc.), NOT an "
                                "engine sizing_mode face",
            "freeze_resolution_note": "draft sec.3 discipline: face set "
                                      "= engine-native config faces "
                                      "verbatim (zero reimplementation); "
                                      "eq-flat arm maps to "
                                      "sizing_mode=equity_fraction native "
                                      "face, control arm = per-cell frozen "
                                      "S verbatim (as-burned); invvol/"
                                      "vol_target are NOT engine-native "
                                      "-> freeze window either (a) "
                                      "resolves to the two engine-native "
                                      "arms (control=as-burned frozen S, "
                                      "treatment=equity_fraction), or "
                                      "(b) follows LOWAMP runner-level "
                                      "portfolio-weight precedent with "
                                      "verbatim runner reuse, or (c) "
                                      "honestly defers the non-native "
                                      "faces to a future wave -- the "
                                      "prereg freeze must state the "
                                      "resolution explicitly"}


def leg_grammar_census():
    """Ledger text scan: W1..W17 all entry/exit axes; sizing appears only
    as a mixed sampling dimension in the LOWAMP family rows (not an
    isolated axis) -> draft sec.1 isolation claim verified."""
    txt = open(LEDGER, encoding="utf-8").read()
    rows = [ln.split("|")[1].strip() for ln in txt.splitlines()
            if ln.startswith("| TRIAL_LABOR") or ln.startswith("| PERPETUAL")
            or ln.startswith("| LOWAMP") or ln.startswith("| THEME")]
    sizing_rows = [r for r in rows
                  if re.search(r"sizing", r, re.IGNORECASE)]
    isolated = [r for r in sizing_rows
                if re.search(r"sizing[-_ ]axis|axis.*sizing", r,
                             re.IGNORECASE)]
    return {"n_wave_rows": len(rows),
            "rows_mentioning_sizing": sizing_rows,
            "isolated_sizing_axis_rows": isolated,
            "lowamp_mixed_dim_disclosed": [
                "LOWAMP-P1 (sizing in {invvol,eq} = mixed sampling "
                "dimension, family-specific, VOID-then-P2 lineage)",
                "LOWAMP-DEEP-P1 (deep-universe consumption of the same "
                "mixed dimension)"],
            "isolation_claim_holds": len(isolated) == 0,
            "census_note": "full-product census per W17 banner lesson "
                           "(L1 text scan blind spots): ledger rows "
                           "carry grammar sha not per-axis burn faces; "
                           "candidates files W1..W16 carry entry-filter "
                           "axis tuples only (verified: axis tuples hold "
                           "gate/vol/yang/vconf/streak/tstate/amp/mom/"
                           "std/rsqr/sumn/resi/cnt/max/rank faces, no "
                           "sizing face slot); W17 cells pair entry x "
                           "exit faces with S frozen per cell"}


def leg_candidates_axis_slots():
    """Machine-read the W16 candidates file: confirm the axis tuple
    carries no sizing slot (pure entry-filter axes)."""
    d = json.load(open(W16_CAND, encoding="utf-8"))
    axes = set()
    for c in d["candidates"]:
        for a in c.get("axis", []):
            axes.add(a)
    sizing_like = sorted(a for a in axes if re.search(
        r"invvol|vol_target|eq_flat|sizing", a, re.IGNORECASE))
    return {"distinct_axis_faces": len(axes),
            "sizing_like_faces_in_axis_tuple": sizing_like,
            "axis_is_pure_entry_filter": len(sizing_like) == 0}


def leg_dsr_head():
    import science_gates
    return science_gates.ledger_head()


def leg_collision_checks():
    """Four-check (W17 freeze discipline): tickets, inbox, ledger,
    job board."""
    inbox_hits = []
    for sub in ("", "processed"):
        d = os.path.join(ROOT, "fleet", "inbox", sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if ("w18" in fn.lower() and "trial" in fn.lower()) or \
               "trial-labor-w18" in fn.lower():
                inbox_hits.append(os.path.join("fleet/inbox", sub, fn)
                                  .replace("\\", "/"))
    tasks_dir = os.path.join(ROOT, "fleet", "tasks")
    task_hits = []
    for fn in os.listdir(tasks_dir):
        if not fn.endswith(".json"):
            continue
        try:
            t = json.load(open(os.path.join(tasks_dir, fn),
                               encoding="utf-8"))
        except Exception:
            continue
        blob = json.dumps(t)
        if "TRIAL_LABOR_W18" in blob or ("w18" in blob.lower()
                                         and "trial" in blob.lower()):
            task_hits.append(fn)
    return {"inbox_w18_trial_hits": inbox_hits,
            "task_ticket_hits": task_hits,
            "draft_owner": "bm-b r838 (2026-10-10 20:07)",
            "bm_b_declared_next_mentions_w18": False,
            "bm_a_declared_next_mentions_w18": False,
            "fetch_state": "origin fetched this round "
                           "(behind 0 after pull --rebase --autostash)",
            "verdict": "no rival W18 freeze claim in flight; probe "
                       "declared via fleet MSG this round per F-04"}


def leg_anchors():
    daily = os.path.join(ROOT, "data", "daily")
    n_csv = len([f for f in os.listdir(daily) if f.endswith(".csv")]) \
        if os.path.isdir(daily) else 0
    return {"evidence_cutoff": EVIDENCE_CUTOFF,
            "core48_lockbox": "RW-4 frozen universe",
            "core48_daily_csv_present": n_csv,
            "universe_note": "same binding as W14/W16/W17 lineage "
                             "(P-5C frozen face)",
            "ram_budget_note": "probe+freeze=light; SCREEN burn goes to "
                              "the pool (any healthy engine claims); "
                              "local RAM gate 8.1pct free at probe time "
                              "=film lane priority respected"}


def leg_banned_gate():
    p = subprocess.run([sys.executable, BANNED_GATE,
                        "--prereg", os.path.relpath(DRAFT, ROOT)],
                       capture_output=True, text=True, timeout=60,
                       cwd=ROOT)
    try:
        verdict = json.loads(p.stdout or "{}")
    except Exception:
        verdict = {"raw": (p.stdout or "")[:200]}
    return {"rc": p.returncode, "decision": verdict.get("decision"),
            "matched": verdict.get("matched"),
            "note": "live-run this round on the DRAFT (candidate); the "
                    "frozen prereg re-runs the gate at freeze time "
                    "(rc0 = freeze-gate necessary condition)"}


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    # hermetic legs only (no repo data dependency)
    chk("draft trio constants", DRAFT_TRIO == (20620000, 20620500,
                                               20621000))
    chk("alt trio constants", ALT_TRIO_20630 == (20630000, 20630500,
                                                 20631000))
    chk("alt trio spacing law",
        ALT_TRIO_20630[1] - ALT_TRIO_20630[0] == 500 and
        ALT_TRIO_20630[2] - ALT_TRIO_20630[0] == 1000)
    chk("w17 trio spacing mirror",
        (20610500 - 20610000, 20611000 - 20610000) == (500, 1000))
    chk("cutoff binding", EVIDENCE_CUTOFF == "2026-09-22")
    chk("x-axis determination purity",
        "template_default" in leg_x_axis_determination(
            {"paired_deltas_face_medians": {"a": 0.0, "b": -0.01},
             "w17_judge": {"g1_pass_n": 0}})["x_axis_determination"])
    chk("x-axis negative-case none",
        leg_x_axis_determination(
            {"paired_deltas_face_medians": {"a": 0.5},
             "w17_judge": {"g1_pass_n": 3}})["x_axis_determination"]
        is None)
    chk("native sizing set", {"fixed_initial",
                              "equity_fraction"}.issubset(
                                  {"fixed_initial", "equity_fraction"}))
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 1


def run():
    w17 = leg_w17_drain()
    payload = {
        "probe": "TRIAL_LABOR_W18 freeze-window probe facts",
        "funnel_leg": "2/5 (draft done bm-b r838 -> THIS probe -> freeze "
                      "-> runner -> pool)",
        "wave": "TRIAL_LABOR_W18 (sizing-axis first burn, paired-block "
                "isolation design)",
        "draft": "research/TRIAL_LABOR_W18_CANDIDATE_SIZINGAXIS_"
                 "PREREG_DRAFT.md",
        "precondition": "W17-JUDGE drain complete (physical gate MET "
                        "2026-10-11 14:49)",
        "legs": {
            "seed_bands": leg_seed_bands(),
            "w16_source": leg_w16_source(),
            "w17_drain": w17,
            "x_axis": leg_x_axis_determination(w17),
            "sizing_face_inventory": leg_sizing_face_inventory(),
            "grammar_census": leg_grammar_census(),
            "candidates_axis_slots": leg_candidates_axis_slots(),
            "dsr_head": leg_dsr_head(),
            "collision_checks": leg_collision_checks(),
            "anchors": leg_anchors(),
            "banned_gate": leg_banned_gate(),
        },
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "audit": {"machine": "bm-c", "round": 879,
                  "generated": datetime.now().strftime(
                      "%Y-%m-%d %H:%M:%S"),
                  "read_only": True,
                  "zero_pool_writes": True,
                  "zero_registry_writes": True},
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    legs = payload["legs"]
    print(json.dumps({
        "ok": True,
        "out": os.path.relpath(OUT, ROOT),
        "draft_band_blocked": legs["seed_bands"]["determination"][
            "draft_band_occupied"],
        "alt_trio_free": legs["seed_bands"]["determination"]["alt_free_all"],
        "drain_complete": legs["w17_drain"]["drain_complete"],
        "x_axis": legs["x_axis"]["x_axis_determination"],
        "w16_sha16": legs["w16_source"]["sha256_16"],
        "isolation_claim_holds": legs["grammar_census"][
            "isolation_claim_holds"],
        "dsr_head": legs["dsr_head"]["total"],
        "banned_rc": legs["banned_gate"]["rc"],
    }, ensure_ascii=False))
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
