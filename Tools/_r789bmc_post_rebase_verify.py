# -*- coding: utf-8 -*-
import subprocess, json

def show(path):
    return subprocess.run(["git", "show", "HEAD:" + path], capture_output=True).stdout

src = show("scripts/perpetual_faces_n1.py").decode("utf-8", errors="replace")
print("W193 cfg in HEAD n1:", '193: {"batch": "PERPETUAL-N1-W193"' in src)
print("W193 mat face in HEAD n1:", "W193 materializer face" in src)
print("w137 both in HEAD n1:", "w137_adjudicated = {94_100, 94_200}" in src)

j = json.loads(show("results/perpetual_faces/n1_w192_results.json"))
print("W192 products in HEAD:", j["science_gates"]["ledger"]["total"] == 836745)

pj = json.loads(show("results/runnable_pool.json"))
ents = pj["entries"] if isinstance(pj, dict) and "entries" in pj else pj
if isinstance(ents, dict):
    ents = list(ents.values())
w17 = [e for e in ents if "W17" in str(e.get("id", ""))]
print("pool W17 entries in HEAD:", len(w17), "statuses:", sorted(set(e.get("status") for e in w17)))

# post-rebase n1 selftest gate (merged tree: bm-a W193 face + bm-c W192 products)
r = subprocess.run(["python", "scripts/perpetual_faces_n1.py", "selftest"],
                   capture_output=True, cwd=None)
tail = (r.stdout or b"").decode("utf-8", errors="replace").strip().splitlines()[-1:]
print("n1 selftest post-rebase rc:", r.returncode, "|", (tail[0] if tail else "")[:120])
