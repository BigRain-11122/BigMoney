# r669 bm-b side verification: direct field compare on 3 sample UU faces (r661 double-form law)
import subprocess, json

def blob(rev, path):
    p = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    assert p.returncode == 0, p.stderr[:200]
    return p.stdout

out = {}
for path in ("results/lhb_update_status.json", "results/compute_audit.json", "docs/live_usage/LIVE-2026-10-04.json"):
    o = json.loads(blob("HEAD", path).decode("utf-8"))
    t = json.loads(blob("MERGE_HEAD", path).decode("utf-8"))
    keys = [k for k in ("ts", "updated", "generated", "generated_at", "verdict", "cutoff", "last_attempt") if k in o or k in t]
    out[path] = {
        "ours": {k: o.get(k) for k in keys},
        "theirs": {k: t.get(k) for k in keys},
        "ours_machine": o.get("machine"),
        "theirs_machine": t.get("machine"),
    }

with open(r"results\_r669bmb_side_verify.json", "wb") as f:
    f.write(json.dumps(out, ensure_ascii=True, indent=1).encode("ascii"))
print("VERIFY-WRITTEN")
