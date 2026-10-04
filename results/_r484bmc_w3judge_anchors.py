"""r484 bm-c W3-judge freeze anchors: w3 candidates sha16 + survivor count +
ledger head + seed-band occupancy scan (R250 one-step law evidence)."""
import hashlib
import json
import os
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r484bmc_w3judge_anchors_out.txt")
lines = []

cpath = os.path.join(REPO, "results", "mass_trial", "w3_candidates.json")
sha = hashlib.sha256(open(cpath, "rb").read()).hexdigest()[:16]
lines.append(f"w3_candidates_sha16={sha}")

spath = os.path.join(REPO, "results", "mass_trial", "w3_screen_summary.json")
summ = json.load(open(spath, encoding="utf-8"))
surv = summ.get("survivor_ids", [])
lines.append(f"w3_survivors={len(surv)}")
lines.append(f"w3_screen_complete={summ.get('complete')}")
tl = summ.get("trials_ledger", {})
lines.append(f"w3_screen_ledger batch_trials={tl.get('batch_trials')} total={tl.get('total')}")

sys.path.insert(0, REPO)
os.chdir(REPO)
import scripts.science_gates as sg  # noqa: E402
head = sg.ledger_head()
lines.append(f"ledger_head total={head['total']}")

# SEED_REGISTRY band occupancy in the candidate gap 20285600..20285999
occ = {k: v for k, v in sg.SEED_REGISTRY.items()
       if isinstance(v, int) and 20285500 <= v <= 20286500}
lines.append(f"registry_occupancy_20285500_20286500={sorted(occ.items(), key=lambda x: x[1])}")
hit = {k: v for k, v in sg.SEED_REGISTRY.items()
       if isinstance(v, int) and 20285600 <= v <= 20285999}
lines.append(f"candidate_band_20285600_20285999_hits={hit}")

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))
print("PROBE_DONE")
