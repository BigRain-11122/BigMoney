import json
import subprocess

for st in (2, 3):
    r = subprocess.run(["git", "show", f":{st}:results/compute_audit.json"],
                       capture_output=True)
    d = json.loads(r.stdout.decode("utf-8-sig"))
    latest = d.get("latest", {})
    print(f":{st}: audit latest.ts={latest.get('ts')!r} "
          f"hist_len={len(d.get('history', []))}")
for st in (2, 3):
    r = subprocess.run(["git", "show",
                        f":{st}:results/autofill_state.json"],
                       capture_output=True)
    d = json.loads(r.stdout.decode("utf-8-sig"))
    lt = d.get("last_tick", {})
    print(f":{st}: autofill last_tick ts={lt.get('ts')!r} "
          f"machine={lt.get('machine')!r}")
