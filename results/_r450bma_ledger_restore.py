"""r450 bm-a lane-ledger stale-blob restore (r446 union/blob law).

r450 session's A13 incident repair used a stale blob for
results/gate_attrition.bm-a.json -> worktree lost the 4 storm-restored
entries (A10/A11/A12/A13, restored at r449 e8e179214). Guard scan
rc=1 ACTIVE LOSS "work missing 4 rows present in HEAD".

Net path: HEAD blob取证 -> verify worktree has ZERO unique keys ->
byte-identical restore (worktree == HEAD -> file leaves dirty set).
"""
import json
import subprocess
import sys

PATH = "results/gate_attrition.bm-a.json"


def blob(rev):
    raw = subprocess.run(["git", "show", f"{rev}:{PATH}"],
                         capture_output=True, check=True).stdout
    return raw, json.loads(raw.decode("utf-8"))


def keys(j):
    return {(e.get("batch"), e.get("ts")) for e in j.get("entries", [])}


head_raw, head_j = blob("HEAD")
with open(PATH, encoding="utf-8") as fh:
    work_j = json.load(fh)

hk, wk = keys(head_j), keys(work_j)
missing = hk - wk
unique = wk - hk
print(f"head_entries={len(hk)} work_entries={len(wk)} "
      f"missing={sorted(missing)} worktree_unique={sorted(unique)}")

if unique:
    print("REFUSE: worktree has unique keys -- manual union required")
    sys.exit(2)

with open(PATH, "wb") as fh:
    fh.write(head_raw)
print("RESTORED byte-identical to HEAD blob")
