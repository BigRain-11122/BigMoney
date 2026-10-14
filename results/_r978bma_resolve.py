"""r978 bm-a rebase conflict resolver — deterministic content-based side selection.

6 conflicts from replaying estate commit 33fffb0f8 onto origin/main:
- processed MSG 0715/0745: keep ORIGIN blobs (canonical fleet processing, content
  already verified byte/CRLF-equivalent to the deleted local copies)
- token_usage.json: take-newer by 'generated' (merge_lane_views face law)
- _attrition_guard_scan.json: take-newer by 'ts'
- queue_head_collision_probe.json: bm-a lane probe face (machine_id=bm-a wins)
- _r686bmb_d19_check.json: content-equivalent; keep local side (byte-diff allowed)
"""
import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(path_sha):
    r = subprocess.run([GIT, "cat-file", "blob", path_sha], capture_output=True)
    return r.stdout

def stage_blobs(path):
    r = subprocess.run([GIT, "ls-files", "-u", "--", path], capture_output=True, text=True)
    out = {}
    for line in r.stdout.strip().splitlines():
        parts = line.split("\t")
        meta, p = parts[0], parts[1]
        mode, sha, stage = meta.split()
        out[int(stage)] = sha
    return out

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

log = []

# --- 1+2: processed MSG files -> origin blob (stage 2), content-verified earlier
for p in [
    "fleet/inbox/processed/MSG-20261014-0715-bma-w236-finalize.md",
    "fleet/inbox/processed/MSG-20261014-0745-bma-w238-seat.md",
]:
    st = stage_blobs(p)
    want = st[2]  # origin-side blob (stages 1==2 confirmed for 0715; 0745 both exist)
    data = blob(want)
    open(p, "wb").write(data)
    subprocess.run([GIT, "add", "--", p], check=True)
    log.append(f"{p}: took stage2 origin blob {want[:10]} ({len(data)}B)")

# --- 3: token_usage.json -> take-newer by 'generated'
p = "results/token_usage.json"
st = stage_blobs(p)
cand = {}
for s, sha in st.items():
    try:
        d = jload(blob(sha))
        cand[s] = d.get("generated", "")
    except Exception as e:
        cand[s] = f"ERR:{e}"
pick_stage = max((s for s in cand if not str(cand[s]).startswith("ERR")), key=lambda s: cand[s])
open(p, "wb").write(blob(st[pick_stage]))
subprocess.run([GIT, "add", "--", p], check=True)
log.append(f"{p}: take-newer generated -> stage{pick_stage} {st[pick_stage][:10]} ({cand})")

# --- 4: _attrition_guard_scan.json -> take-newer by 'ts'
p = "results/_attrition_guard_scan.json"
st = stage_blobs(p)
cand = {}
for s, sha in st.items():
    try:
        d = jload(blob(sha))
        cand[s] = d.get("ts", "")
    except Exception as e:
        cand[s] = f"ERR:{e}"
pick_stage = max((s for s in cand if not str(cand[s]).startswith("ERR")), key=lambda s: cand[s])
open(p, "wb").write(blob(st[pick_stage]))
subprocess.run([GIT, "add", "--", p], check=True)
log.append(f"{p}: take-newer ts -> stage{pick_stage} {st[pick_stage][:10]} ({cand})")

# --- 5: queue_head_collision_probe.json -> bm-a lane face wins (machine_id=bm-a)
p = "results/queue_head_collision_probe.json"
st = stage_blobs(p)
pick_stage = None
for s, sha in st.items():
    try:
        d = jload(blob(sha))
        if d.get("machine_id") == "bm-a":
            pick_stage = s
            break
    except Exception:
        pass
if pick_stage is None:
    pick_stage = 3  # fallback: local side
open(p, "wb").write(blob(st[pick_stage]))
subprocess.run([GIT, "add", "--", p], check=True)
log.append(f"{p}: machine_id=bm-a -> stage{pick_stage} {st[pick_stage][:10]}")

# --- 6: _r686bmb_d19_check.json -> content-equivalent (both 86187eff/348eaf34 False/False);
#     keep the replayed (local estate) side = stage 3 when present
p = "results/_r686bmb_d19_check.json"
st = stage_blobs(p)
sides = {}
for s, sha in st.items():
    try:
        d = jload(blob(sha))
        sides[s] = (d.get("decisions_sha", "")[:12], d.get("orders_sha", "")[:12],
                    d.get("decisions_changed"), d.get("orders_changed"))
    except Exception as e:
        sides[s] = f"ERR:{e}"
pick_stage = 3 if 3 in st else max(st)
open(p, "wb").write(blob(st[pick_stage]))
subprocess.run([GIT, "add", "--", p], check=True)
log.append(f"{p}: content-equivalent, kept stage{pick_stage} {st[pick_stage][:10]} ({sides})")

for line in log:
    print(line)
print("RESOLVE-DONE rc0")
