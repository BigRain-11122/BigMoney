"""r827 bm-b resolver part 2: 4 bm-b-owned daemon faces (lane-sync replay conflicts).

Recipes: daemon live-tick snapshots -> take the fresher committed side by
internal ts (r826 'daemon live-wins' family; daemons re-tick post-rebase
anyway); history jsonl -> line-level union zero loss (r188).
"""
import json
import subprocess

def blob(stage, path):
    return subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                          capture_output=True).stdout.decode("utf-8", errors="replace")

def pick_ts(j):
    for k in ("ts", "updated", "tick_at", "updated_at", "now"):
        v = j.get(k)
        if isinstance(v, str):
            return v
    return ""

receipt = {}
for p in ["results/p1d_gates.json", "results/saturation_engine/face_bm-b.json",
          "results/saturation_engine/state_bm-b.json"]:
    jo, jm = json.loads(blob(2, p)), json.loads(blob(3, p))
    to, tm = pick_ts(jo), pick_ts(jm)
    chosen = jm if tm >= to else jo
    json.loads(json.dumps(chosen))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(chosen, f, ensure_ascii=False, indent=1)
    receipt[p] = {"recipe": "daemon-live-tick-take-new", "ts_o": to, "ts_m": tm,
                  "took": "mine" if chosen is jm else "commit1"}

p = "results/saturation_engine/history_bm-b.jsonl"
lo = [l for l in blob(2, p).strip().splitlines() if l.strip()]
lm = [l for l in blob(3, p).strip().splitlines() if l.strip()]
seen, union = set(), []
for l in lo + lm:
    key = l.strip()
    if key not in seen:
        seen.add(key)
        union.append(l)
# sort by embedded ts if every line carries one, else keep stable append order
try:
    union.sort(key=lambda l: json.loads(l).get("ts", ""))
except Exception:
    pass
assert len(union) >= max(len(lo), len(lm)), "jsonl union shrink"
for l in union:
    json.loads(l)
with open(p, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(union) + "\n")
receipt[p] = {"recipe": "jsonl-line-union", "o": len(lo), "m": len(lm), "union": len(union)}

import io
with io.open("results/_r827bmb_resolve_p2_receipt.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("p2 resolver done:", json.dumps(receipt, ensure_ascii=False)[:400])
