"""r688 bm-a S3: w3-judge-2of4 burn liveness (double-form) + pool ticket state."""
import json
import os
import subprocess

# Form 1 + Form 2: full CIM scan, match by CommandLine
ps = (
    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
    "| Select-Object ProcessId,CommandLine | ConvertTo-Json"
)
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command", ps], capture_output=True
).stdout.decode("gbk", "replace")
procs = json.loads(out) if out.strip()[:1] in "[{" else []
if isinstance(procs, dict):
    procs = [procs]
print("python procs:", len(procs))
matches = []
for p in procs:
    cl = p.get("CommandLine") or ""
    if "judge" in cl.lower() or "w3" in cl.lower() or "mass" in cl.lower():
        matches.append((p["ProcessId"], cl[:140]))
for m in matches:
    print("JUDGE-CANDIDATE:", m[0], m[1])
if not matches:
    print("NO judge-related python processes alive")

# pool ticket state for w3 judge shards
pool = json.load(open("results/runnable_pool.json", encoding="utf-8-sig"))
entries = pool.get("entries", [])
w3j = [e for e in entries if "W3-JUDGE" in str(e.get("key", "")) or "w3_judge" in json.dumps(e)]
for e in w3j:
    print(
        "POOL:", e.get("key"), "| status:", e.get("status"),
        "| owner:", e.get("owner"), "| since:", e.get("owner_since"),
    )

# claim file for our shard
claim_dir = r"results\pool_claims"
for d in sorted(os.listdir(claim_dir)):
    if "W3-JUDGE" in d:
        full = os.path.join(claim_dir, d)
        for f in os.listdir(full):
            fp = os.path.join(full, f)
            t = os.path.getmtime(fp)
            import datetime
            print("CLAIMFILE:", d, f, datetime.datetime.fromtimestamp(t).isoformat())

# w3_judge_state + shard output progress
for path in ["results/w3_judge_state.json", "results/mass_trial/w3_judge_shard_2of4.jsonl"]:
    if os.path.exists(path):
        if path.endswith(".jsonl"):
            n = sum(1 for _ in open(path, encoding="utf-8", errors="replace"))
            print("SHARD-OUTPUT:", path, "lines:", n)
        else:
            print("STATE:", json.load(open(path, encoding="utf-8-sig")))
    else:
        print("MISSING:", path)
