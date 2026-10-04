import json, hashlib, re, sys, os
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
sys.path.insert(0, repo)
sys.path.insert(1, repo + r"\scripts")
import science_gates as sg

# 1. seed registry around the 2028xxxx band
hits = {}
for name, val0 in sorted(sg.SEED_REGISTRY.items(), key=lambda kv: str(kv[1])):
    try:
        val = int(val0)
    except Exception:
        continue
    if 20280000 <= val <= 20290000:
        hits[name] = val
print("SEED_REGISTRY 2028xxxx band:")
for k, v in hits.items():
    print(f"  {k} = {v}")

# 2. w3 candidates sha16
with open(repo + r"\results\mass_trial\w3_candidates.json", "rb") as f:
    cand_bytes = f.read()
sha16 = hashlib.sha256(cand_bytes).hexdigest()[:16]
print("w3_candidates.json sha16:", sha16, "bytes:", len(cand_bytes))

# 3. w3 screen summary
with open(repo + r"\results\mass_trial\w3_screen_summary.json", "rb") as f:
    summ = json.loads(f.read().decode('utf-8'))
surv = summ.get("survivor_ids") or summ.get("survivors")
print("w3 screen summary keys:", sorted(summ.keys()))
n_surv = len(surv) if surv is not None else None
print("survivors:", n_surv)
print("evidence_cutoff:", summ.get("evidence_cutoff"))
print("trials_ledger:", summ.get("trials_ledger"))

# 4. ledger head
head = sg.ledger_head()
print("ledger head total:", head if not isinstance(head, dict) else json.dumps(head)[:300])

# 5. grep for 20285 band usage across scripts (collision scan for candidate seed)
import subprocess
r = subprocess.run(["git", "-C", repo, "grep", "-n", "-E", "2028[57][0-9]{3}", "--", "scripts", "research"], capture_output=True)
out = r.stdout.decode('utf-8', 'replace')
lines = out.splitlines()
print("git grep 20285xxxx hits:", len(lines))
for ln in lines[:40]:
    print("  ", ln[:150])
