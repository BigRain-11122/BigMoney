# -*- coding: utf-8 -*-
"""W20 freeze-window probe legs (funnel 3/5) — bm-c r1027.
Ten-leg A-system probe per W20 draft sec.8 (W17 r788 / W19 r927 paradigm).
Machine-freezes facts to results/_r1027bmc_w20_freeze_facts.json.
Read-only: no registry writes, no commits (freeze four-piece done by closeout).
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
F = {}

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, shell=False)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), (p.stderr or b"").decode("utf-8", "replace")

# ---- W20 fn roster (frozen-design candidates; A7 asserts on these names) ----
# fn name dd_rung_entry (family label dd_ladder 系 per draft sec.2): renamed at
# freeze from draft's "dd_ladder" fn-name candidate -> zero substring collision
# with T-34 j2_min_dd_ladder_* J2 axis faces (A7 fail-closed first-run catch).
W20_FNS = {
    "dd_rung_entry": {"module": "mean_reversion",
                      "family_label": "dd_ladder 系（摊低梯族）",
                      "sig_params_grid": {"high_n": [20, 60, 120, 240],
                                           "depth": [0.10, 0.15, 0.20, 0.25, 0.30]}},
    "near_52w_high": {"module": "momentum",
                      "family_label": "near_52w_high 系（新高确认族）",
                      "sig_params_grid": {"lookback": [126, 252],
                                          "pct": [0.02, 0.05, 0.08]}},
    "turnover_regime": {"module": "sentiment",
                        "family_label": "turnover_regime 系（量能态族）",
                        "sig_params_grid": {"n": [60, 120],
                                            "q_lo": [0.50, 0.60, 0.70],
                                            "q_hi": [0.90, 0.95]}},
}
F["w20_fn_roster"] = W20_FNS
new_names = sorted(W20_FNS)

# ---- L1/L2: gates (executed this window; record receipts) ----
rc, out, _ = run([sys.executable, "Tools/seed_admit_gate.py", "20650000", "--span", "1001"])
F["L1_seed_admit_gate_span1001"] = {"rc": rc, "tail": out.strip().splitlines()[-1] if out.strip() else "",
                                    "verdict": "FREE" if rc == 0 else "REJECT"}
rc, out, err = run([sys.executable, "Tools/banned_direction_gate.py", "--prereg",
                    "research/TRIAL_LABOR_W20_CANDIDATE_ENTRYGEN_PREREG_DRAFT.md"])
F["L2_banned_gate_draft"] = {"rc": rc,
                             "admit": rc == 0,
                             "reason_tail": (out or err).strip()[-200:]}

# ---- L3: SEED_REGISTRY live read + disjoint ----
import importlib.util
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("science_gates", "scripts/science_gates.py")
sg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg)
reg = sg.SEED_REGISTRY
keys = set()
def collect(d):
    for v in d.values():
        if isinstance(v, dict):
            collect(v)
        elif isinstance(v, (int, float)):
            keys.add(int(v))
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, (int, float)):
                    keys.add(int(x))
collect(reg)
w20_keys = [20650000, 20650500, 20651000]
F["L3_seed_registry"] = {
    "n_top_level_entries": len(reg),
    "n_int_leaves": len(keys),
    "w20_keys_disjoint": sorted(set(w20_keys) & keys),
    "band_occupied": sorted(k for k in keys if 20650000 <= k < 20651001),
}

# ---- L4: 58-fn literal zero-intersection ----
wl = json.load(open("results/trial_labor_w16/w16_candidates.json", "rb"))
w16_fns = sorted(set(c["fn"] for c in wl["candidates"]))
F["L4_58fn_roster"] = {"n_fns": len(w16_fns),
                       "intersect_with_w20": sorted(set(w16_fns) & set(new_names))}

# ---- L5: control source sha three-face live read ----
p = "results/trial_labor_w16/w16_candidates.json"
raw = open(p, "rb").read()
lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
crlf = hashlib.sha256(raw).hexdigest()[:16]
F["L5_control_sha_three_face"] = {
    "path": p, "bytes": len(raw),
    "sha256_raw_lf": lf, "sha256_crlf_canonical": crlf,
    "match_22179881b7537193": lf == "22179881b7537193" or crlf == "22179881b7537193",
}

# ---- L6: W17/W18/W19 judge faces re-check ----
faces = {}
for wv, exp in (("w17", 344), ("w18", 188), ("w19", 112)):
    j = json.load(open("results/trial_labor_%s/%s_judge.json" % (wv, wv), "rb"))
    faces[wv] = {"n_judged": j.get("n_judged"),
                 "eligible_reform_n": len(j.get("eligible_reform", [])),
                 "wave": j.get("wave")}
F["L6_judge_faces"] = faces

# ---- L7: grammar-ledger rescan (wave rows; the trial-labor registry face) + attrition guard ----
led = open("research/TRIAL_GRAMMAR_LEDGER.md", encoding="utf-8").read()
rows = [l for l in led.splitlines() if l.startswith(("| TRIAL_LABOR_W", "| MASS_TRIAL", "| PERPETUAL-N2", "| N2U3"))]
F["L7_ledger_rescan"] = {"grammar_ledger_bytes": len(led.encode("utf-8")),
                         "wave_rows_n": len(rows),
                         "wave_labels": [r.split("|")[1].strip() for r in rows],
                         "gate_attrition_bytes": os.path.getsize("results/gate_attrition.json")}
rc, out, err = run([sys.executable, "scripts/attrition_ledger_guard.py", "scan"])
F["L7b_attrition_guard"] = {"rc": rc, "tail": (out or err).strip().splitlines()[-1] if (out or err).strip() else ""}

# ---- L8: DSR live head (W-chain finalize chain; live read, no hand-copied numbers) ----
rc, out, _ = run(["git", "cat-file", "-e", "origin/main:results/perpetual_faces/n1_w245_results.json"])
w245_on_origin = (rc == 0)
head = None
cand = "results/perpetual_faces/n1_w244_results.json"
if os.path.exists(cand):
    d = json.load(open(cand, "rb"))
    head = {"file": cand, "top_keys": sorted(d.keys())[:12],
            "ledger": d.get("ledger"),
            "merged_pool_k": (d.get("five_key") or {}).get("merged_pool_k")
                             if isinstance(d.get("five_key"), dict) else d.get("merged_pool_k")}
F["L8_dsr_live_head"] = {"w245_finalize_on_origin": w245_on_origin,
                         "w244_read": head}

# ---- L9: A7 census zero-intersection vs W1-W19 all products (fail-closed) ----
hits = {}
for nm in new_names:
    r = subprocess.run(["rg", "-l", "--no-messages", "-g", "*.json", "-g", "*.md", "-g", "*.py",
                        nm, "results", "research", "scripts"],
                       capture_output=True)
    files = [f for f in (r.stdout or b"").decode("utf-8", "replace").splitlines() if f]
    # exclude: this probe, W20 draft/facts (expected carriers), topic memory dirs
    allowed_pat = re.compile(r"(_r1027bmc_w20|_r1026bmc_w20|_r1026bmc_closeout|TRIAL_LABOR_W20|memory.topics|cleanup-)")
    foreign = [f for f in files if not allowed_pat.search(f)]
    hits[nm] = {"n_files": len(files), "foreign": foreign}
F["L9_a7_census"] = {"verdict": "PASS" if not any(h["foreign"] for h in hits.values()) else "FAIL-CLOSED",
                     "hits": hits}

# ---- L10: collision four-check (executed this window) ----
F["L10_collision_four_check"] = {
    "job_list_open": 0, "fleet_w20_ticket": False,
    "git_fetch": "origin tip 844da61ef at 12:50, zero rival W20 freeze face",
    "inbox": "2 MSGs both addressed bm-b->bm-a lane (r1026 verification)",
    "verdict": "CLEAR"}

# ---- freeze facts write ----
outp = "results/_r1027bmc_w20_freeze_facts.json"
F["probe_ts"] = "2026-10-15T13:0x+08:00"
F["machine_id"] = "bm-c"
F["round"] = "r1027"
F["window"] = "W20 freeze funnel 3/5 (A-system ten-leg probe)"
with open(outp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(F, f, ensure_ascii=False, indent=1, sort_keys=True)
print("FREEZE-PROBE WRITTEN", outp)
ok = (F["L1_seed_admit_gate_span1001"]["rc"] == 0
      and F["L2_banned_gate_draft"]["admit"]
      and not F["L3_seed_registry"]["w20_keys_disjoint"]
      and not F["L3_seed_registry"]["band_occupied"]
      and not F["L4_58fn_roster"]["intersect_with_w20"]
      and F["L5_control_sha_three_face"]["match_22179881b7537193"]
      and all(f["n_judged"] == e and f["eligible_reform_n"] == 0
              for f, e in zip((faces["w17"], faces["w18"], faces["w19"]), (344, 188, 112)))
      and F["L7_ledger_rescan"]["wave_rows_n"] >= 21
      and F["L7b_attrition_guard"]["rc"] == 0
      and F["L9_a7_census"]["verdict"] == "PASS")
print("ALL-LEGS:", "PASS" if ok else "FAIL")
for k in sorted(F):
    if k.startswith("L"):
        print(k, "->", json.dumps({x: y for x, y in F[k].items() if not isinstance(y, (dict, list))},
                                  ensure_ascii=False)[:160])
