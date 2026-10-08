# -*- coding: utf-8 -*-
"""r786 bm-c W17 probe leg (L1 zero-burn) -- funnel leg 2/5 per draft sec.6.1
(research/TRIAL_LABOR_W17_CANDIDATE_EXITAXIS_PREREG_DRAFT.md, D-20261009-01
pool-replenish main line). Five read-only legs, ONE facts JSON, zero ledger
writes, zero prereg numbers pre-written into any frozen doc (placeholder law).

Legs:
 L1 ledger exit-axis zero-burn assert (draft sec.1 claim re-verified mechanically)
 L2 banned_direction_gate pre-run on the DRAFT (honest rc; freeze-window hard
    gate re-run is unchanged law -- this leg only pre-flights wording)
 L3 seed berth probe: ast-parse science_gates.SEED_REGISTRY (never hand-typed)
    + ledger number harvest + conservative 2000-wide occupancy disjointness
    + full text scan over code/doc surfaces for candidate literals
 L4 exit face enumeration: importlib READ-ONLY of engine/exit_rules.py (iron
    law: zero modification -- exit priority/T+1/cost model untouched)
 L5 entry-lib facts: w14_grammar.json sha/anchor facts + ledger sha16 match

rc contract: 0 = all legs green (facts carry the PROPOSED berth for the
freeze window); 1 = hard-gate violation (exit-axis burned in W lineage /
W16 trio absent from registry); 2 = mechanism issue (honest, do not mask).
House style: ASCII-only source (r786 s05/s6 drivers), GBK console entry
reconfigure (r236 law), CREATE_NO_WINDOW on the one subprocess call
(U060/2026-10-01 silence law)."""
import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")  # r236 GBK console entry law

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUT = os.path.join(ROOT, "results", "_r786bmc_w17_probe_facts.json")
LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
DRAFT = os.path.join(ROOT, "research",
                    "TRIAL_LABOR_W17_CANDIDATE_EXITAXIS_PREREG_DRAFT.md")
GATE = os.path.join(ROOT, "Tools", "banned_direction_gate.py")
GATES_PY = os.path.join(ROOT, "scripts", "science_gates.py")
EXIT_PY = os.path.join(ROOT, "engine", "exit_rules.py")
W14_GRAMMAR = os.path.join(ROOT, "results", "trial_labor_w14", "w14_grammar.json")
W14_JUDGE_STATE = os.path.join(ROOT, "results", "trial_labor_w14",
                               "judge_state.json")

EXIT_AXIS_TOKENS = ["tiered_tp", "hard_stop", "time_decay", "trailing",
                    "hold_to_end", "pattern_exit", "take_profit", "stop_loss"]
W_ROW_RE = re.compile(
    r"^\|\s*(MASS_TRIAL_W\d+|TRIAL_LABOR_W\d+|PERPETUAL-N2-W\d+|"
    r"PERPETUAL-N1-W\d+)\b")
# W16 family band [20593000, 20596000) verbatim from
# research/TRIAL_LABOR_W16_PREREG.md sec. seed-3-step-law (E10 band-domain).
W16_BAND = (20593000, 20596000)
# Candidate berths, gap=2000 above W16 band end first (W16's own gap=2000
# above theme_judge_p2 band-end precedent), then upward alternates.
CANDIDATE_TRIOS = [
    (20598000, 20598500, 20599000),
    (20600000, 20600500, 20601000),
    (20610000, 20610500, 20611000),
    (20620000, 20620500, 20621000),
]
SCAN_DIRS = ["research", "scripts", "Tools", "engine", "firm", "live",
             "config", "docs", "knowledge", "fleet"]
SCAN_EXTS = (".py", ".md", ".json", ".txt", ".ps1")
SELF_BASENAMES = {os.path.basename(__file__),
                  os.path.basename(OUT),
                  "TRIAL_LABOR_W17_CANDIDATE_EXITAXIS_PREREG_DRAFT.md"}
OCCUPANCY_WIDTH = 2000  # conservative per-base occupancy (W16 unc derived
# band stayed within base+500; 2000 is the family-band width precedent)


def leg1_ledger(text):
    rows = [ln for ln in text.splitlines() if ln.startswith("|")]
    w_rows = [ln for ln in rows if W_ROW_RE.match(ln)]
    hits = []
    for ln in w_rows:
        wave = W_ROW_RE.match(ln).group(1)
        for tok in EXIT_AXIS_TOKENS:
            if tok in ln:
                hits.append({"wave": wave, "token": tok})
    lowamp_rows = [ln for ln in rows if ln.startswith("| LOWAMP")]
    return {"rows_total": len(rows), "w_rows": len(w_rows),
            "exit_axis_hits_in_w_lineage": hits,
            "lowamp_family_rows_disclosed": len(lowamp_rows),
            "verdict": "ZERO_EXIT_AXIS_BURN" if not hits else "VIOLATION"}


def leg2_gate():
    p = subprocess.run([sys.executable, GATE, "--prereg", DRAFT],
                       capture_output=True, creationflags=CNW, cwd=ROOT)
    out = (p.stdout + p.stderr).decode("utf-8", "replace").strip()
    return {"rc": p.returncode, "tail": out[-400:],
            "verdict": "ADMIT" if p.returncode == 0 else "REJECT_PREFREEZE",
            "note": "pre-flight on DRAFT; freeze-window hard gate re-run is "
                    "unchanged law (draft sec.6.2)"}


def registry_bases():
    with io.open(GATES_PY, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    bases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "SEED_REGISTRY":
                    val = ast.literal_eval(node.value)
                    for k, v in val.items():
                        if isinstance(v, int):
                            bases[str(k)] = v
    return bases


def leg3_seed(text, reg):
    known = set(reg.values())
    # harvest 5-8 digit numbers from ledger rows (gen/null/unc/seeds fields;
    # harmless extra integers like raw counts get distance-checked too)
    for m in re.finditer(r"=(\d{5,8})", text):
        known.add(int(m.group(1)))
    w16_trio_ok = all(b in known for b in (20593000, 20593500, 20594000))
    # conservative occupancy disjointness test
    def disjoint(c, n):
        return not (n <= c < n + OCCUPANCY_WIDTH) and not (c <= n < c + OCCUPANCY_WIDTH)
    scan_hit_files = []
    occ_rejects = []
    for trio in CANDIDATE_TRIOS:
        blockers = sorted({n for c in trio for n in known
                           if not disjoint(c, n)})
        occ_ok = not blockers
        in_w16_band = any(W16_BAND[0] <= c < W16_BAND[1] for c in trio)
        if not occ_ok or in_w16_band:
            occ_rejects.append({"trio": list(trio),
                                "in_w16_band": in_w16_band,
                                "occupancy_blockers": blockers[:8]})
            continue
        hits = text_scan(trio)
        if not hits:
            return {"proposed_trio": list(trio),
                    "occupancy_rejected_trios": occ_rejects,
                    "trios_rejected_before": len(scan_hit_files),
                    "w16_trio_in_registry": w16_trio_ok,
                    "w16_band": list(W16_BAND),
                    "known_bases_n": len(known),
                    "text_scan_surfaces": SCAN_DIRS,
                    "verdict": "CLEAN_BERTH_PROPOSED"}
        scan_hit_files.append({"trio": list(trio), "hits": hits[:5]})
    return {"proposed_trio": None, "rejected_trios": scan_hit_files,
            "occupancy_rejected_trios": occ_rejects,
            "w16_trio_in_registry": w16_trio_ok,
            "known_bases_n": len(known), "verdict": "NO_CLEAN_BERTH"}


def text_scan(trio):
    hits = []
    needles = [str(c) for c in trio]
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in filenames:
                if not fn.endswith(SCAN_EXTS):
                    continue
                if fn in SELF_BASENAMES:
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(fp) > 2_000_000:
                        continue
                    with io.open(fp, encoding="utf-8", errors="replace") as fh:
                        for i, ln in enumerate(fh, 1):
                            for nd in needles:
                                if nd in ln:
                                    hits.append({"file": os.path.relpath(fp, ROOT),
                                                 "line": i})
                except OSError:
                    continue
    for fn in os.listdir(ROOT):
        if fn.endswith((".py", ".md")) and fn not in SELF_BASENAMES:
            fp = os.path.join(ROOT, fn)
            try:
                with io.open(fp, encoding="utf-8", errors="replace") as fh:
                    for i, ln in enumerate(fh, 1):
                        for nd in needles:
                            if nd in ln:
                                hits.append({"file": fn, "line": i})
            except OSError:
                continue
    return hits


def leg4_exit_faces():
    import importlib.util
    spec = importlib.util.spec_from_file_location("w17_probe_exit_rules", EXIT_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # READ-ONLY import; zero modification (iron law)
    cfg = mod.ExitConfig()
    fields = {f: getattr(cfg, f) for f in cfg.__dataclass_fields__}
    doc = mod.__doc__ or ""
    priority = [ln.strip() for ln in doc.splitlines()
                if re.match(r"\s*P\d", ln)]
    draft = io.open(DRAFT, encoding="utf-8").read()
    m = re.search(r"treatment 臂=\*\*①策略自有出场\*\*：出场规则族 faces（候选 face 集：([^）]+)）", draft)
    cand_faces = []
    if m:
        cand_faces = [x.strip().split("〔")[0].strip()
                      for x in m.group(1).split("/") if x.strip()]
    return {"exit_config_defaults": fields,
            "engine_default_priority": priority,
            "draft_treatment_face_candidates": cand_faces,
            "control_arm": "template_default (engine default exit stack as "
                           "tested baseline, draft sec.3 arm-3)",
            "verdict": "ENUMERATED_READ_ONLY"}


def leg5_entry_lib():
    facts = {"w14_grammar_file": os.path.relpath(W14_GRAMMAR, ROOT)}
    with io.open(W14_GRAMMAR, "rb") as fh:
        blob = fh.read()
    facts["w14_grammar_sha256_16"] = hashlib.sha256(blob).hexdigest()[:16]
    j = json.loads(blob.decode("utf-8"))
    facts["w14_grammar_top_keys"] = sorted(j.keys())
    facts["w14_grammar_cutoff"] = j.get("amp_anchor", {}).get("cutoff") \
        if isinstance(j.get("amp_anchor"), dict) else None
    facts["w14_grammar_decidable_days"] = \
        j.get("amp_anchor", {}).get("decidable_days") \
        if isinstance(j.get("amp_anchor"), dict) else None
    with io.open(W14_JUDGE_STATE, encoding="utf-8") as fh:
        js = json.load(fh)
    facts["judge_state_grammar_sha"] = js.get("grammar_sha256")
    facts["n_survivors_w14"] = js.get("n_survivors")
    ledger = io.open(LEDGER, encoding="utf-8").read()
    m = re.search(r"\|\s*TRIAL_LABOR_W14\s*\|\s*([0-9a-f]{16})", ledger)
    facts["ledger_w14_sha16"] = m.group(1) if m else None
    m16 = re.search(r"\|\s*TRIAL_LABOR_W16\s*\|\s*([0-9a-f]{16})", ledger)
    facts["ledger_w16_sha16"] = m16.group(1) if m16 else None
    facts["sha_match_verdict"] = {
        "judge_state_vs_ledger": facts["judge_state_grammar_sha"] == facts["ledger_w14_sha16"],
        "grammar_file_vs_ledger": facts["w14_grammar_sha256_16"] == facts["ledger_w14_sha16"],
    }
    return facts


def main():
    text = io.open(LEDGER, encoding="utf-8").read()
    facts = {"round": 786, "machine": "bm-c", "wave": "TRIAL_LABOR_W17",
             "funnel_leg": "2/5 probe (draft sec.6.1)", "burn": "ZERO (L1)"}
    l1 = leg1_ledger(text)
    facts["L1_ledger_exit_axis"] = l1
    l2 = leg2_gate()
    facts["L2_banned_gate_preflight"] = l2
    reg = registry_bases()
    l3 = leg3_seed(text, reg)
    facts["L3_seed_berth"] = l3
    l4 = leg4_exit_faces()
    facts["L4_exit_faces"] = l4
    l5 = leg5_entry_lib()
    facts["L5_entry_lib"] = l5

    hard = (l1["verdict"] == "VIOLATION"
            or not l3.get("w16_trio_in_registry", False))
    mech = (l3["verdict"] == "NO_CLEAN_BERTH")
    facts["shape_assert"] = bool(
        isinstance(l1["w_rows"], int) and l1["w_rows"] >= 15
        and isinstance(l2["rc"], int) and "proposed_trio" in l3)
    facts["rc_map"] = {"hard_violation": hard, "mechanism_issue": mech}
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    print(json.dumps({k: facts[k] for k in
                     ("L1_ledger_exit_axis", "L2_banned_gate_preflight",
                      "L3_seed_berth", "L5_entry_lib")}, indent=1)[:2400])
    print("facts:", OUT)
    return 1 if hard else (2 if mech else 0)


if __name__ == "__main__":
    raise SystemExit(main())
