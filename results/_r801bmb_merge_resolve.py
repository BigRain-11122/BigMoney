# r801 bm-b resolver: 8 UU merge absorb (origin newer 11:06-11:11 > ours 10:53-11:11).
# Per-window empirical direction (r773 law), probed:
#   - 5 snapshot faces: THEIRS ts-newer-wins (all origin sides newer)
#   - fleet/orders/O-20261007-0935-bm-c.md: THEIRS whole-blob (version of record; bm-c r670
#     acknowledged the r803 receipt + JSON evidence verified at origin; our r800 duplicate
#     receipt preserved in git history + round reports, zero unique info)
#   - compute_audit/regime_state: THEIRS state + history/transitions/triggers ROW UNION (zero-loss)
import subprocess, json, hashlib

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    assert h, f"stage {stage} missing for {path}"
    return subprocess.run(["git", "cat-file", "blob", h],
                          capture_output=True).stdout.decode("utf-8", "replace")

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

receipt = {"round": "r801", "faces": {}}

THEIRS = ["fleet/orders/O-20261007-0935-bm-c.md",
          "results/_attrition_guard_scan.json",
          "results/lhb_update_status.json",
          "results/scorecard_v1.json",
          "results/strategy_scorecard.json",
          "results/update_status.json"]
for p in THEIRS:
    b = blob(3, p)
    write(p, b)
    receipt["faces"][p] = {"recipe": "THEIRS ts-newer-wins / version-of-record",
                           "sha16": hashlib.sha256(b.encode()).hexdigest()[:16]}

for p, keys in [("results/compute_audit.json", ["history"]),
                ("results/regime_state.json", ["history", "transitions", "triggers"])]:
    jt = json.loads(blob(3, p))
    jo = json.loads(blob(2, p))
    for k in keys:
        vo, vt = jo.get(k) or [], jt.get(k) or []
        seen, un = set(), []
        for row in vo + vt:
            sig = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if sig not in seen:
                seen.add(sig)
                un.append(row)
        receipt["faces"][f"{p}::{k}"] = {"ours_rows": len(vo), "theirs_rows": len(vt), "union_rows": len(un)}
        jt[k] = un
    out = json.dumps(jt, ensure_ascii=False, indent=1) + "\n"
    write(p, out)
    receipt["faces"][p] = {"recipe": "THEIRS state + row-union zero-loss",
                           "sha16": hashlib.sha256(out.encode()).hexdigest()[:16]}

with open("results/_r801bmb_merge_resolve.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolver done: THEIRS x%d + union x2" % len(THEIRS))
for k in receipt["faces"]:
    if "::" in k:
        print(k, receipt["faces"][k])
