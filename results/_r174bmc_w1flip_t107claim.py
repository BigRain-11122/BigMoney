# -*- coding: utf-8 -*-
"""r174 bm-c one-off: (a) MASS-TRIAL-W1-JUDGE-SHARD-0..3 waiting->ready pool
flip (O-20260928-1614 sec.1/3 immediate face; r203 flip-is-round-work law);
(b) T-2026-09-28-107 claim (O-1730 claim-and-start same round).

Flip-gate evidence (frozen in the entry data_gates, verified this window):
  (a) CENSUS-FUS-S2-W2A done + CENSUS-FUS-S2-W2B done (2026-09-28 14:14:14,
      commit 918f04ce) + TRIAL-LABOR-W1-SCREEN done (01:24:41, r121 bm-c,
      w1_screen.json committed);
  (b) bm-c free-RAM 3-sample [8.51, 8.44, 8.47] GB >= 4GB across ~30s
      (r354 law, measured this window before this script ran).

Lane pin honesty (V2-P1 r118 proven-set precedent): the judge dual-leg D
panel = Money02/data/cache/t18_deep_panel (bm-b machine-local; bm-c carries
no Money02 face). A null lane would let a cache-less machine claim a shard,
exit-2 on the in-runner t18 gate, and wedge it under a fresh heartbeat
(takeover gate = min(heartbeat, claim-stamp) staleness, autofill S9 family).
Pinning bm-b is the honest physical-dep disclosure; parallelism realizes as
shard-internal worker pool + cross-shard cadence on the sole capable
machine, with the cross-machine upgrade gated on a deep-panel transfer
(future slice, TRANSFER face).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
TICKET = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-28-107-P0.json")
NOW = time.strftime("%Y-%m-%d %H:%M:%S")

W1_IDS = {f"MASS-TRIAL-W1-JUDGE-SHARD-{i}" for i in range(4)}

FLIP_NOTE = (
    "r174 bm-c flip waiting->ready (r203 any-machine law): frozen flip-gate "
    "conditions verified -- (a) CENSUS-FUS-S2-W2A done + W2B done (14:14:14, "
    "918f04ce) + TRIAL-LABOR-W1-SCREEN done (01:24:41 r121 bm-c); "
    "(b) bm-c free-RAM 3-sample [8.51,8.44,8.47]GB >=4GB across ~30s (r354). "
    "O-20260928-1614 sec.1/3 immediate face: W1 four shards must not stack. "
    "LANE PIN bm-b = physical-dep honesty per DECISION-CHAIN-V2-P1 r118 "
    "precedent: dual-leg D panel Money02/data/cache/t18_deep_panel is "
    "bm-b-local; null lane = cache-less machine exit-2 wedge under fresh "
    "heartbeat. Parallelism = shard-internal worker pool + cross-shard "
    "cadence on the sole capable machine; cross-machine upgrade gated on "
    "deep-panel transfer (future slice)."
)


def main():
    with open(POOL, encoding="utf-8-sig") as f:
        pool = json.load(f)
    flipped = []
    for e in pool.get("entries", []):
        if e.get("id") in W1_IDS:
            if e.get("status") != "waiting":
                print(f"REFUSE {e['id']}: status={e.get('status')} "
                      "(expected waiting -- zero double-flip)", file=sys.stderr)
                return 2
            e["status"] = "ready"
            e["lane_owner"] = "bm-b"
            e["armed_at"] = NOW
            e["flip_note"] = FLIP_NOTE
            for sh in e.get("shards", []):
                if sh.get("status") == "waiting":
                    sh["status"] = "ready"
            flipped.append(e["id"])
    if set(flipped) != W1_IDS:
        print(f"REFUSE: found only {flipped} of 4 target entries "
              "(pool drift -- re-read before retry)", file=sys.stderr)
        return 2
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)
    os.replace(tmp, POOL)

    with open(TICKET, encoding="utf-8-sig") as f:
        t = json.load(f)
    if t.get("status") != "open":
        print(f"REFUSE T-107 claim: status={t.get('status')} "
              "(r239 collision -- another window claimed first)", file=sys.stderr)
        return 2
    t["status"] = "claimed"
    t["claimed_by"] = ("bm-c (OS iteration loop, round 174; git fetch "
                       "immediately before claim per r239 collision law)")
    t["claimed_at"] = NOW
    t["progress_r174_bmc"] = (
        "slice-1 same-round start (O-1730): compute_audit v2.4 hardening "
        "(supply_gap never-CLEAN per O-1625 miss-face + starvation window "
        "30->15min per O-1614 sec.5 + supply_floor leg ready>=3 per sec.1 + "
        "ignition_sla leg 10min per sec.2) + daily_report utilization face "
        "per sec.6 + COMPUTE_AUDIT.md v2.4 charter. Slices 2+: fill-ladder "
        "generator (sec.1/4), autofill force-claim SLA enforcement (sec.2), "
        "utilization dashboard sync (sec.6). Immediate-face receipts this "
        "round: W1-JUDGE four-shard pool flip (this window, bm-b lane pin "
        "physical-dep disclosed) + V2-P1 ignition already claimed/burning "
        "bm-b (16:18:31 owner_since)."
    )
    tmp = TICKET + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(t, f, indent=1, ensure_ascii=False)
    os.replace(tmp, TICKET)

    print(json.dumps({
        "flipped": sorted(flipped), "armed_at": NOW,
        "ticket": t["id"], "ticket_status": t["status"],
        "claimed_by": "bm-c", "claimed_at": NOW,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
