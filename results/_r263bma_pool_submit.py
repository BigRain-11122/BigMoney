# -*- coding: utf-8 -*-
"""R263 bm-a -- pool submit: CN-CORE-DDCTL-P1 (T-73 s3 slice-6).

Appends ONE ready entry to results/runnable_pool.json mirroring the
family entry schema (CN-CORE-SATELLITE-P1 precedent). Byte faces
probed and mirrored: no BOM / LF / indent=1 / trailing newline /
ensure_ascii=False (producer parity, R255 five-face law). Exit 0.
"""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

raw = open(POOL, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw \
    and raw.endswith(b"\n"), "pool byte faces drifted (probe mismatch)"
d = json.loads(raw.decode("utf-8"))

assert not any(e.get("id") == "CN-CORE-DDCTL-P1"
               for e in d["entries"]), "entry already present"

entry = {
    "id": "CN-CORE-DDCTL-P1",
    "ticket_ref": "T-2026-09-26-73 s3 slice-6 (doctrine residual: "
                  "R261 frozen s8 pointer 2; CEO O-20260926-0926; bm-a "
                  "lane; F-04 claim MSG-20260926-1815)",
    "prereg_ref": "research/CN_CORE_DDCTL_PREREG.md (frozen R263 commit "
                  "precedes ANY run; probe results/core_ddctl_probe.json "
                  "frozen same commit; seed cn_core_ddctl_p1=20261130 "
                  "registered AT freeze one-step R250 law; runner "
                  "committed post-freeze selftest 13/13 zero runs)",
    "runner": "scripts/cn_core_ddctl_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "data_gates": "in-runner fail-closed exit 2: family panel gates "
                  "(T==3333 2013-01-04..2026-09-22 + first==2013-01-04 + "
                  "cutoff==2026-09-22 D2 lockbox + event set == frozen 3 + "
                  "CORE 510880 zero events + first_active==2013-07-17) + "
                  "dd-axis probe identity (DD10 6on/5off/34-of-51 "
                  "first-on 2013-07-17; DD20 4on/4off/10-of-51 first-on "
                  "2014-01-21; drift = exit 2) + SEED_REGISTRY assert "
                  "(cn_core_ddctl_p1=20261130) + R240 zero-rebalance-eval "
                  "refusal + census gate before finalize; selftest 13-leg "
                  "battery ALL PASS pre-burn",
    "shards": [
        {
            "key": "coreddctl-0of1",
            "status": "ready",
            "owner": None,
            "owner_since": None,
            "checkpoint": "no mid-batch npz ckpt (single pass <5min); "
                          "landed marker = results/cn_core_ddctl/"
                          "p1_results.json with ledger block; idempotent "
                          "fast path exit 0 after finalize "
                          "(CN_CORE_DDCTL_P1_REFINALIZE=1 = only redo); "
                          "harvest = pool flip done by next round per "
                          "r244 law (批不自翻)"
        }
    ],
    "workers_plan": {
        "workers": 1,
        "note": "single finalize dependency chain (4 cells x3 faces + "
                "100 nulls + 3 baselines = 115 units, est <2min single "
                "worker; queue-fill sim O(T) per unit, family 21.8s at "
                "64 units)"
    },
    "note": "N=104 on the D1 bill (4 judged cells + 100 two-arm nulls); "
            "prereg s0/s6; family machinery reuse (CS panel + DRV "
            "engine + SRP guards + science_gates shared criteria); "
            "verdict face = x2 V2 cost always-on",
    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
}
d["entries"].append(entry)
d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

out = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(out)
os.replace(tmp, POOL)
print("pool entry appended: CN-CORE-DDCTL-P1 ready; entries="
      f"{len(d['entries'])}")
