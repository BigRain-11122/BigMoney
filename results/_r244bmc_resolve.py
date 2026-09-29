# r244 bm-c rebase conflict resolver (r449 blob-union law):
# 1) compute_audit.json = {latest, history} union face -> ts-keyed union of
#    both histories + latest = newer ts; 2) _attrition_guard_scan.json =
#    snapshot evidence -> take newer ts (stale face loses, r241 newer-ts law).
import io, json, os, subprocess, sys

tmp = os.environ["TEMP"]
ours = json.load(io.open(os.path.join(tmp, "ca_ours.json"), encoding="utf-8"))
theirs = json.load(io.open(os.path.join(tmp, "ca_theirs.json"), encoding="utf-8"))

# --- compute_audit union ---
def hkey(e):
    return (e.get("ts"), e.get("machine"), e.get("audit_version"))

merged, seen = [], set()
for e in ours.get("history", []) + theirs.get("history", []):
    k = hkey(e)
    if k not in seen:
        seen.add(k)
        merged.append(e)
merged.sort(key=lambda e: e.get("ts") or "")
latest = ours["latest"] if (ours["latest"].get("ts", "") >= theirs["latest"].get("ts", "")) else theirs["latest"]
union = {"latest": latest, "history": merged}
io.open("results/compute_audit.json", "w", encoding="utf-8").write(
    json.dumps(union, ensure_ascii=False, indent=1))
print("compute_audit union: history", len(merged),
      "| latest ts", latest.get("ts"))

# --- attrition guard scan: newer ts wins ---
ag_ours = json.load(io.open(os.path.join(tmp, "ag_ours.json"), encoding="utf-8"))
ag_theirs = json.load(io.open(os.path.join(tmp, "ag_theirs.json"), encoding="utf-8"))
# refresh blobs at CURRENT rebase stage (stage 2/3 files may have changed
# since the first conflict window) -- re-extract via git for accuracy
def blob(side):
    r = subprocess.run(["git", "show", f":{side}:results/_attrition_guard_scan.json"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return json.loads(r.stdout)
a2, a3 = blob(2), blob(3)
pick = a2 if (a2.get("ts", "") >= a3.get("ts", "")) else a3
io.open("results/_attrition_guard_scan.json", "w", encoding="utf-8").write(
    json.dumps(pick, ensure_ascii=False, indent=1))
print("attrition scan: kept ts", pick.get("ts"),
      "| verdict", pick.get("verdict", pick.get("summary", "n/a")))

# parse-validate both outputs (r241 full JSON parse validation law)
for p in ("results/compute_audit.json", "results/_attrition_guard_scan.json"):
    json.load(io.open(p, encoding="utf-8"))
print("both faces parse OK")
