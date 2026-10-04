"""r675 pick2 absorption check -- verify pick 2 (4d3d635d4 satengine absorb) content
is fully contained in current HEAD (newer daemon snapshots), then skip is legal (r630 law)."""
import json, subprocess

def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

PICK2 = "4d3d635d4"
faces = ["results/saturation_engine/face_bm-a.json",
         "results/saturation_engine/history_bm-a.jsonl",
         "results/saturation_engine/state_bm-a.json"]
verdicts = []
for f in faces:
    pick2 = show(PICK2, f)
    head = show("HEAD", f)
    if pick2 is None or head is None:
        verdicts.append(f"{f}: MISSING SIDE"); continue
    if f.endswith(".jsonl"):
        # append-only history: HEAD lines must be a superset (row-level canon containment r656)
        p_rows = {ln for ln in pick2.decode("utf-8", "replace").split("\n") if ln.strip()}
        h_rows = {ln for ln in head.decode("utf-8", "replace").split("\n") if ln.strip()}
        missing = p_rows - h_rows
        verdicts.append(f"{f}: jsonl containment {'OK' if not missing else 'LOSS ' + str(len(missing))}")
    else:
        same = pick2 == head
        # json faces: daemon live-wins -- compare epoch/ts freshness
        try:
            pj, hj = json.loads(pick2), json.loads(head)
            pk, hk = pj.get("epoch", pj.get("ts", "")), hj.get("epoch", hj.get("ts", ""))
            verdicts.append(f"{f}: pick2_epoch={pk} head_epoch={hk} head_newer={hk >= pk} identical={same}")
        except Exception as e:
            verdicts.append(f"{f}: parse {e} identical={same}")

out = "\n".join(verdicts)
open("results/_r675bma_pick2_absorb.txt", "w", encoding="utf-8").write(out)
print(out)
