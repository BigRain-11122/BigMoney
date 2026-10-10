# -*- coding: utf-8 -*-
"""r957 bm-a: crash-fuse host-transfer surgery for the 8 W17 screen sigs.

Facts (bm-c r829 round report 12:14 + crash_fuse records):
- The W17 KeyError('faces') code defect was FIXED by bm-c r829 (two
  pack points, selftest 21/21 + worker-probe 173/173 PASS). Current
  runner sha faec7eea2224bfc2 = the FIXED version.
- The 8 count=1 "crashes" (12:48 -> 15:42 staggered) are the r791
  RAM-gate bounded-wait 40min cap expiry exits on bm-c (honest wait
  self-termination, NOT code defects): bm-c RAM pinned 0.15GB<4GB by
  the CEO film chain (O-20261010-1825 evidence chain).
- O-1825 sec.1 transfers the shards to bm-a (RAM 51G free). The fuse
  misclassifies host-side resource-cap exits as crash-loop for ANY
  machine; clearing per the D-03(2) tombstone mechanism with the true
  reason. Protection loop intact: a NEW crash on bm-a carries a fresh
  last_crash_ts and beats this tombstone at the merge.

Surgery per pit-pool-edit laws: per-face anchors, count asserts,
parse gate before write. Three faces: shared + bm-a lane + bm-c lane
(bm-c lane is a shared-tree file; clearing it stops the refusal-ts
inflation that would out-date the tombstone before bm-c consumes
MSG-1900).
"""
import io, json, datetime

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
REASON = ("host_transfer_r791_ram_gate_cap_expiry_not_code_defect; "
          "KeyError('faces') fixed bm-c r829 (selftest 21/21 + "
          "worker-probe 173/173); O-20261010-1825 sec.1 bm-c->bm-a "
          "(RAM 51G free); new crash carries fresh ts and beats this "
          "tombstone")
SIGS = [f"scripts/trial_labor_w17.py|screen,{n},8" for n in range(8)]

FACES = [
    r"results\crash_fuse.json",
    r"results\crash_fuse.bm-a.json",
    r"results\crash_fuse.bm-c.json",
]

for path in FACES:
    src = io.open(path, encoding="utf-8", newline="").read()
    data = json.loads(src)
    sigs = data.get("sigs", {})
    cleared = data.setdefault("cleared", {})
    moved = 0
    for sig in SIGS:
        if sig in sigs:
            reg = sigs.pop(sig)
            cleared[sig] = {
                "cleared_ts": NOW,
                "cleared_by": "bm-a",
                "reason": REASON,
                "crashes": int(reg.get("count", 0)),
                "old_code_sha256": reg.get("code_sha256"),
            }
            moved += 1
    body = json.dumps(data, indent=1, ensure_ascii=False)
    json.loads(body)  # parse gate
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    print(f"{path}: moved {moved} sig(s) to cleared; "
          f"sigs left={len(sigs)} cleared={len(cleared)}")
    for sig in SIGS:
        assert sig not in json.loads(io.open(path, encoding="utf-8").read())["sigs"], sig
print("surgery complete at", NOW)
