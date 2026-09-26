# r251 bm-a resolver part-2: manual verdicts for the 2 UNKNOWN files
# (dashboard pair anchored by ITS OWN meta.generated_at -- part-1 had
# wrongly anchored the js twin on the daily-report pair's ts; recomputed
# here whole bytes for BOTH js+json twins from the same side) +
# compute_audit.json = history zero-loss union + take-new latest.ts.
import json
import subprocess

def blob(side, path):
    return subprocess.run(["git", "show", f":{side}:{path}"],
                          capture_output=True).stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

# ---- dashboard pair by meta.generated_at
j2 = jload(blob(2, "results/dashboard_status.json"))
j3 = jload(blob(3, "results/dashboard_status.json"))
g2 = j2.get("meta", {}).get("generated_at")
g3 = j3.get("meta", {}).get("generated_at")
side = 3 if (g3 or "") >= (g2 or "") else 2
assert g2 and g3, "generated_at must exist on both sides (no None-tie)"
open("results/dashboard_status.json", "wb").write(
    blob(side, "results/dashboard_status.json"))
open("results/dashboard_status.js", "wb").write(
    blob(side, "results/dashboard_status.js"))
chk = open("results/dashboard_status.js", "rb").read()
assert b"window.DASH_DATA" in chk, "js wrapper must survive"
json.loads(open("results/dashboard_status.json", encoding="utf-8-sig").read())
print("dashboard pair take-:%d by meta.generated_at %s vs %s" % (side, g2, g3))

# ---- compute_audit: history union + latest take-new by ts
d2, d3 = jload(blob(2, "results/compute_audit.json")), \
         jload(blob(3, "results/compute_audit.json"))
seen, hist = set(), []
for row in d2.get("history", []) + d3.get("history", []):
    sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if sig not in seen:
        seen.add(sig)
        hist.append(row)
hist.sort(key=lambda r: r.get("ts", ""))
t2 = (d2.get("latest") or {}).get("ts")
t3 = (d3.get("latest") or {}).get("ts")
latest = d3["latest"] if (t3 or "") >= (t2 or "") else d2["latest"]
out = {**d3, "latest": latest, "history": hist}
data = json.dumps(out, ensure_ascii=False, indent=1)
json.loads(data)
open("results/compute_audit.json", "w", encoding="utf-8",
     newline="\n").write(data + "\n")
print("compute_audit: history union %d+%d -> %d (ts-asc), latest take-"
      "by ts %s vs %s" % (len(d2.get("history", [])),
                          len(d3.get("history", [])), len(hist), t2, t3))
