# -*- coding: utf-8 -*-
"""R239 T-77 conflict resolver: three-blob read via subprocess bytes (r209 law -- no PS redirect),
bm-b claim 09:42:01 precedes mine (yield per fleet/README s4); take bm-b claim side, fold yield note.
Writes resolved file + validation. Exit 2 on any anomaly (fail-closed)."""
import json
import subprocess
import sys

PATH = "fleet/tasks/T-2026-09-26-77-P1.json"


def blob(stage):
    out = subprocess.run(["git", "show", f":{stage}:{PATH}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"blob read fail stage {stage}: {out.stderr[:200]}")
    return json.loads(out.stdout.decode("utf-8"))


base, ours, theirs = blob(1), blob(2), blob(3)
# in a rebase: stage2 'ours' = the side we rebase ONTO (origin/main = bm-b), stage3 'theirs' = MY replayed commit
bmb, mine = ours, theirs
print("bm-b side claimed_at:", bmb.get("claimed_at"), "| status:", bmb.get("status"))
print("mine   side claimed_at:", mine.get("claimed_at"), "| status:", mine.get("status"))
assert "bm-b" in str(bmb.get("claimed_by", "")), "side identification failed"
assert "bm-a" in str(mine.get("claimed_by", "")), "side identification failed (mine)"
# yield: bm-b claimed first (09:42:01 < 09:47) and already delivered -> take bm-b side wholesale
resolved = dict(bmb)
resolved["yield_note_r239"] = ("bm-a R239 claimed T-77 at 09:47 without seeing bm-b's 09:42:01 claim commit "
                               "(landed after bm-a's 09:39 pull); per fleet/README s4 commit-time yield bm-a "
                               "concedes -- bm-b delivery (routing+fuse+L2 ledger+GPU code face) is canonical; "
                               "bm-a keeps only complementary T-75 synergy (token line in daily_report.py) and "
                               "takes the GPU-FACTOR-LANE-PROOF pool flip (bm-a-box GPU) as continuation.")
for k in list(resolved.keys()):
    if k.startswith("progress_r239") and "bm-a" in str(resolved[k]) and "slice-1" in str(resolved[k]):
        del resolved[k]  # drop my redundant slice note; bm-b's own progress field stays
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(resolved, f, ensure_ascii=False, indent=1)
    f.write("\n")
# validate roundtrip + key fields
chk = json.load(open(PATH, encoding="utf-8"))
assert "bm-b" in str(chk["claimed_by"]), "claim must be bm-b after yield"
assert chk.get("yield_note_r239"), "yield note missing"
print("resolved: bm-b claim kept; yield note written; my progress_r239 dropped")
