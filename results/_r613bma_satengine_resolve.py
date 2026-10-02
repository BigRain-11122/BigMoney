# r613 bm-a: resolve autostash-apply conflicts on saturation_engine daemon files
# :2: = HEAD side (satengine tick 07:26:04, newer) ; :3: = autostash side (07:00:04, older)
# snapshot faces (state/face) take-:2: newer; history jsonl = line-level union zero-loss
import json
import subprocess

P_SNAP = ["results/saturation_engine/state_bm-a.json", "results/saturation_engine/face_bm-a.json"]
P_HIST = "results/saturation_engine/history_bm-a.jsonl"


def stage_bytes(stage: int, path: str) -> bytes:
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    assert r.returncode == 0, (path, stage, r.stderr[:200])
    return r.stdout


for p in P_SNAP:
    ours, theirs = stage_bytes(2, p), stage_bytes(3, p)
    jo, jt = json.loads(ours), json.loads(theirs)

    def deep_ts(o, best=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v.startswith("2026-") and (k.lower().startswith("ts") or k.lower().startswith("updated") or k.lower().startswith("last")) and len(v) >= 19:
                    best = max(best, v)
                best = deep_ts(v, best)
        elif isinstance(o, list):
            for it in o:
                best = deep_ts(it, best)
        return best

    to, tt = deep_ts(jo), deep_ts(jt)
    assert to >= tt, f"{p}: HEAD side not newer ({to} vs {tt}) - manual adjudication needed"
    with open(p, "wb") as f:
        f.write(ours)
    json.loads(open(p, "rb").read())
    print(f"[snap] {p}: HEAD {to} >= stash {tt} -> took :2: ({len(ours)}B)")

ours, theirs, base = stage_bytes(2, P_HIST), stage_bytes(3, P_HIST), stage_bytes(1, P_HIST)
lo = [l for l in ours.split(b"\n") if l.strip()]
lt = [l for l in theirs.split(b"\n") if l.strip()]
lb = [l for l in base.split(b"\n") if l.strip()]
seen, merged = set(), []
for line in lo + lt:  # HEAD rows first (newer ticks), then any stash-unique rows
    if line not in seen:
        seen.add(line)
        merged.append(line)
lost = [l for l in set(lo) | set(lt) if l not in set(merged)]
assert not lost, "union lost rows"
nl = b"\r\n" if ours.split(b"\n")[0].endswith(b"\r") else b"\n"
out = nl.join(merged) + nl
with open(P_HIST, "wb") as f:
    f.write(out)
cnt = len(merged)
print(f"[hist] {P_HIST}: |HEAD|={len(lo)} |stash|={len(lt)} |base|={len(lb)} -> union {cnt} rows (zero-loss)")
print("AUTOSTASH RESOLVE DONE rc=0")
