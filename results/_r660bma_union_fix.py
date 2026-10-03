r"""r660 cross-machine union fix for 2 shared faces post-UU-resolution.

compute_audit.json: {latest, history[]} -> union histories dedup-by-ts sorted, cap 201, latest=max ts.
token_usage.json: machines{} -> per-machine own-side wins (bm-a entry from ours, bm-b from theirs),
generated=max. Byte-safe json IO, strict load self-check after write.
"""
import json
import subprocess

CAP = 201


def show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout


# --- compute_audit.json union (sides: HEAD=ours-pre-merge, origin/main=theirs) ---
ours = json.loads(show("HEAD", "results/compute_audit.json").decode("utf-8"))
theirs = json.loads(show("origin/main", "results/compute_audit.json").decode("utf-8"))
rows = {}
for r in ours["history"] + theirs["history"]:
    rows[r["ts"]] = r
hist = sorted(rows.values(), key=lambda r: r["ts"])[-CAP:]
merged = {"latest": hist[-1], "history": hist}
with open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
print("compute_audit union rows:", len(hist), "latest:", hist[-1]["ts"])
lost = [r["ts"] for r in ours["history"] if r["ts"] not in rows]  # always empty, sanity
print("ours rows preserved:", sum(1 for r in hist if r["ts"] in {x['ts'] for x in ours['history']}))

# --- token_usage.json per-machine union ---
tu_ours = json.loads(show("HEAD", "results/token_usage.json").decode("utf-8"))
tu_theirs = json.loads(show("origin/main", "results/token_usage.json").decode("utf-8"))
tu = dict(tu_theirs)
machines = dict(tu_ours.get("machines", {}))
machines.update(tu_theirs.get("machines", {}))
# own-side authority: bm-a entry from ours (if ours has it), bm-b entry from theirs
if "bm-a" in tu_ours.get("machines", {}):
    machines["bm-a"] = tu_ours["machines"]["bm-a"]
if "bm-b" in tu_theirs.get("machines", {}):
    machines["bm-b"] = tu_theirs["machines"]["bm-b"]
tu["machines"] = machines
tu["generated"] = max(tu_ours.get("generated", ""), tu_theirs.get("generated", ""))
with open("results/token_usage.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(tu, f, ensure_ascii=False, indent=1)
print("token_usage machines keys:", list(machines), "generated:", tu["generated"])

# strict self-check (r645 state.json law)
for p in ("results/compute_audit.json", "results/token_usage.json"):
    json.load(open(p, encoding="utf-8"))
    print("self-check OK:", p)
