# r684 bm-b: attrition scan UU resolve (per-run snapshot take-new ts, r681
# precedent) + marker sanity + stage.
import io, json, subprocess

def side(rev):
    r = subprocess.run(["git", "show", "%s:results/_attrition_guard_scan.json"
                        % rev], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", "replace"))

ours = side("HEAD")
theirs = side("MERGE_HEAD")
ts_o = str(ours.get("ts") or ours.get("scanned_at") or "")
ts_t = str(theirs.get("ts") or theirs.get("scanned_at") or "")
print("ours ts:", ts_o, "| theirs ts:", ts_t)
pick = ours if (ts_o >= ts_t) else theirs
with io.open("results/_attrition_guard_scan.json", "w", encoding="utf-8",
             newline="") as f:
    f.write(json.dumps(pick, ensure_ascii=False, indent=1) + "\n")
json.loads(io.open("results/_attrition_guard_scan.json", encoding="utf-8").read())
r = subprocess.run(["git", "add", "results/_attrition_guard_scan.json"],
                   capture_output=True)
assert r.returncode == 0
print("resolved take-new:", "ours" if pick is ours else "theirs")
