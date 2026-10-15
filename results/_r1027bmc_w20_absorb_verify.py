# -*- coding: utf-8 -*-
"""r1027 absorb-window machine-verify of dead-window W20 freeze-probe legs
(bm-c absorb law: estate machine-verified BEFORE landing). Read-only."""
import hashlib, json, re, subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import importlib.util
spec = importlib.util.spec_from_file_location("science_gates", "scripts/science_gates.py")
sg = importlib.util.module_from_spec(spec); spec.loader.exec_module(sg)

names = ["dd_rung_entry", "near_52w_high", "turnover_regime"]
R = {}

# 58-fn roster zero-intersection (W16 frozen roster)
wl = json.load(open("results/trial_labor_w16/w16_candidates.json", "rb"))
w16_fns = sorted(set(c["fn"] for c in wl["candidates"]))
R["l4_58fn_intersect"] = sorted(set(w16_fns) & set(names))
R["l4_n_fns"] = len(w16_fns)

# SEED_REGISTRY disjoint + band occupancy
keys = set()
def collect(d):
    for v in d.values():
        if isinstance(v, dict): collect(v)
        elif isinstance(v, (int, float)): keys.add(int(v))
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, (int, float)): keys.add(int(x))
collect(sg.SEED_REGISTRY)
R["l3_registry_leaves"] = len(keys)
R["l3_w20_keys_hit"] = sorted(set([20650000, 20650500, 20651000]) & keys)
R["l3_band_occupied"] = sorted(k for k in keys if 20650000 <= k < 20651001)

# control sha three-face
p = "results/trial_labor_w16/w16_candidates.json"
raw = open(p, "rb").read()
R["l5_sha_raw_lf"] = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
R["l5_sha_crlf"] = hashlib.sha256(raw).hexdigest()[:16]
R["l5_match_canonical"] = R["l5_sha_raw_lf"] == "22179881b7537193" or R["l5_sha_crlf"] == "22179881b7537193"
R["l5_bytes"] = len(raw)

# judge faces (W17/18/19) live re-read
for wv, exp in (("w17", 344), ("w18", 188), ("w19", 112)):
    j = json.load(open("results/trial_labor_%s/%s_judge.json" % (wv, wv), "rb"))
    R["l6_%s" % wv] = {"n_judged": j.get("n_judged"),
                       "eligible_reform_n": len(j.get("eligible_reform", [])),
                       "expect": exp}

# A7 census re-run (zero foreign carriers)
allowed = re.compile(r"(_r102[0-9]bmc_w20|_r1026bmc_closeout|_r1027bmc_w20_absorb|TRIAL_LABOR_W20|memory.topics|cleanup-)")
R["l9_hits"] = {}
for nm in names:
    r = subprocess.run(["rg", "-l", "--no-messages", "-g", "*.json", "-g", "*.md", "-g", "*.py",
                        nm, "results", "research", "scripts"], capture_output=True)
    files = [f for f in (r.stdout or b"").decode("utf-8", "replace").splitlines() if f]
    foreign = [f for f in files if not allowed.search(f)]
    R["l9_hits"][nm] = {"n_files": len(files), "foreign": foreign}
R["l9_verdict"] = "PASS" if not any(h["foreign"] for h in R["l9_hits"].values()) else "FAIL-CLOSED"

ok = (not R["l4_58fn_intersect"] and not R["l3_w20_keys_hit"] and not R["l3_band_occupied"]
      and R["l5_match_canonical"]
      and all(R["l6_%s" % w]["n_judged"] == e and R["l6_%s" % w]["eligible_reform_n"] == 0
              for w, e in (("w17", 344), ("w18", 188), ("w19", 112)))
      and R["l9_verdict"] == "PASS")
R["absorb_verdict"] = "PASS" if ok else "FAIL"
R["machine_id"] = "bm-c"; R["round"] = "r1027"
with open("results/_r1027bmc_w20_absorb_verify.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(R, f, ensure_ascii=False, indent=1, sort_keys=True)
print("ABSORB-VERIFY:", R["absorb_verdict"])
print("l4 intersect:", R["l4_58fn_intersect"], "| l3 hit:", R["l3_w20_keys_hit"],
      "band:", R["l3_band_occupied"], "| l5:", R["l5_sha_raw_lf"], R["l5_sha_crlf"],
      "| l9:", R["l9_verdict"])
