# r976 rebase conflict resolve: compute_audit.json union history + newer-latest (r957 law)
import subprocess, json, sys

def stage(idx, path):
    r = subprocess.run(["git", "show", f":{idx}:{path}"], capture_output=True, cwd=r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney")
    return json.loads(r.stdout.decode("utf-8"))

PATH = "results/compute_audit.json"
ours = stage(2, PATH)      # origin side (bm-b absorbed estate, older)
theirs = stage(3, PATH)    # my absorb commit (bm-a chain 07:4x, newer)
print("ours ts:", ours.get("ts"), "| theirs ts:", theirs.get("ts"))
print("ours hist:", len(ours.get("history", [])), "| theirs hist:", len(theirs.get("history", [])))

out = dict(theirs)  # newer-latest top-level (my 07:4x chain face)
ha = ours.get("history", [])
hb = theirs.get("history", [])
seen = set()
merged = []
for e in ha + hb:
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        merged.append(e)
# stable order: keep insertion order (ours first then theirs-new) — history is append-only face
out["history"] = merged
print("merged hist:", len(merged))
with open(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("RESOLVED union history", len(merged), "top-level from", theirs.get("ts"))
