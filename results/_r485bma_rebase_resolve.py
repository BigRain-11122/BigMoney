"""r485 bm-a rebase conflict resolver (canon recipes: compute_audit history
ts-key union per r158/r120 + take-new latest; token_usage/update_status =
take-new snapshot; CODELY = entry-level union per r327).
Reads :2:/:3: stage blobs, writes resolved worktree files. NO data invention.
"""
import json
import subprocess

def blob(stage, path):
    b = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True).stdout
    return b

# --- compute_audit.json: union history by ts, latest = newer side
p = "results/compute_audit.json"
d2 = json.loads(blob(2, p).decode("utf-8-sig"))
d3 = json.loads(blob(3, p).decode("utf-8-sig"))
merged = {}
for e in d2.get("history", []):
    merged[e.get("ts")] = e
for e in d3.get("history", []):
    merged.setdefault(e.get("ts"), e)
hist = sorted(merged.values(), key=lambda e: str(e.get("ts")))
latest = d3["latest"]  # 18:23:21 > 18:17:27 verified by probe
res = dict(d3)
res["history"] = hist
res["latest"] = latest
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print(f"compute_audit union: {len(d2['history'])}+{len(d3['history'])}"
      f"-> {len(hist)} entries, latest={latest.get('ts')}")

# --- token_usage.json / update_status.json: take :3 (mine, newer ts verified)
for p in ["results/token_usage.json", "results/update_status.json"]:
    with open(p, "wb") as fh:
        fh.write(blob(3, p))
    d = json.loads(open(p, "rb").read().decode("utf-8-sig"))
    key = [k for k in ("generated", "updated") if k in d]
    print(f"{p}: take :3 (mine) {key}={d[key[0]]}")

# --- CODELY.md: entry-level union (bm-b 2 lines + my 1 line, both kept)
p = "CODELY.md"
t2 = blob(2, p).decode("utf-8-sig").splitlines()
t3 = blob(3, p).decode("utf-8-sig").splitlines()
bmb = [l for l in t2 if l.startswith("- [2026-09-30 r47") and "bm-b" in l]
mine = [l for l in t3 if "r485 bm-a" in l and l.startswith("- [2026-09-30")]
assert len(bmb) == 2, f"bm-b lines: {len(bmb)}"
assert len(mine) == 1, f"my lines: {len(mine)}"
base = [l for l in t2 if l not in bmb]      # shared context from base side
# append bm-b's 2 + my 1 after the last content line (tail union)
out = base + [l for l in bmb] + [l for l in mine]
text = "\n".join(out) + "\n"
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)
print(f"CODELY union: base {len(t2)} lines + bmb {len(bmb)} + mine "
      f"{len(mine)} -> {len(out)}")
