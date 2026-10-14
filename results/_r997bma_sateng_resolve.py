"""r997 rebase pick-3 resolve: satengine faces.
- history_bm-a.jsonl: line-level union of BASE(:2) + MINE(:3), dict-only gate,
  dedupe by full-line bytes, epoch-order stable (r570 law).
- face/state snapshots: take BASE (fresher 19:56:05 tick).
"""
import subprocess, json

GIT = r"C:\Program Files\Git\cmd\git.exe"

def show(stage, path):
    r = subprocess.run([GIT, "show", ":%s:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, (stage, path, r.returncode)
    return r.stdout.decode("utf-8", "replace")

def write_wt(path, text_bytes):
    with open(path, "wb") as f:
        f.write(text_bytes)

# ---- 1) jsonl union ----
P = "results/saturation_engine/history_bm-a.jsonl"
base_lines = show("2", P).splitlines()
mine_lines = show("3", P).splitlines()
seen, union, rejects = set(), [], []
for src in (base_lines, mine_lines):
    for ln in src:
        s = ln.strip()
        if not s:
            continue
        if s in seen:
            continue
        try:
            d = json.loads(s)
            if not isinstance(d, dict):
                rejects.append(("nondict", s[:60])); continue
        except Exception:
            rejects.append(("unparseable", s[:60])); continue
        seen.add(s)
        union.append((d.get("epoch", 0), s))
union.sort(key=lambda x: x[0])
final_lines = [s for _, s in union]
out = ("\r\n".join(final_lines) + "\r\n").encode("utf-8")
write_wt(P, out)
print("jsonl union: base=%d mine=%d union=%d rejects=%d" % (len(base_lines), len(mine_lines), len(final_lines), len(rejects)))
assert len(rejects) == 0, rejects
# assert both sides' unique tails present
blob = out.decode("utf-8")
for probe in ("19:54:06", "19:56:05"):
    assert probe in blob, "union lost tail " + probe
print("both tails present ok")

# ---- 2) snapshots take base (fresher) ----
for p in ("results/saturation_engine/face_bm-a.json", "results/saturation_engine/state_bm-a.json"):
    b = show("2", p).encode("utf-8")
    write_wt(p, b)
    jb = json.loads(b.decode("utf-8"))
    print("snapshot take-base:", p, "ts=", jb.get("ts") or jb.get("last_tick", {}).get("ts"))
