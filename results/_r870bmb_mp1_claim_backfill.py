# -*- coding: utf-8 -*-
"""r870 bm-b N2-MP1 claim backfill (r942 four-piece remedy leg-1): the
completed burn (daemon claims 07:38:02/07:42:02, 1724/1724, finalize rc0
r868) lacks a worker claim-close artifact (MP1 runner = A158-era clone,
predates the O-20260930-2355 claim law) so the launcher harvest-flip never
landed and the crash-confirmer fed the fuse (refusals=2, 08:14/08:16).
Backfill the claim with full provenance; the daemon's next tick
_harvest_done_flips lands shard+entry done (r942 leg-2, THERMO live
precedent). Pool single-writer law respected (claim file only, no
runnable_pool.json write)."""
import io
import json
import os
import time

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
ENTRY = "N2-MP1"
SHARD = "n2-mp1-run-0of1"
MID = "bm-b"
d = os.path.join(ROOT, "results", "pool_claims", ENTRY)
os.makedirs(d, exist_ok=True)
fp = os.path.join(d, "%s.%s.json" % (SHARD, MID))
if os.path.exists(fp):
    print("[backfill] claim already present:", fp)
    raise SystemExit(0)

# provenance legs (r942: autofill launch record + results JSON completeness)
af = json.loads(io.open(os.path.join(ROOT, "results", "autofill_state.bm-b.json"),
                        encoding="utf-8").read())
launches = [e for e in af.get("launches", []) if e.get("entry") == ENTRY]
assert launches, "no autofill launch records for N2-MP1"
res = json.loads(io.open(os.path.join(ROOT, "results", "mp1_tsgate_p1.json"),
                         encoding="utf-8").read())
vc = res["verdict_counts"]
n_processed = res["audit"]["insts_with_stats"] + len(res["audit"].get("skipped", {}))
assert sum(vc.values()) == 178 and n_processed == 1724, \
    "results completeness verification failed (processed=%d)" % n_processed

now = time.strftime("%Y-%m-%d %H:%M:%S")
claim = {
    "machine_id": MID,
    "state": "closed",
    "pid": launches[-1].get("pid"),
    "heartbeat": now,
    "outcome": "ok",
    "exit_code": 0,
    "started": launches[0]["ts"],
    "closed_at": now,
    "result_ref": ("checkpoint shard_0of1.jsonl 1724/1724 complete + "
                   "results/mp1_tsgate_p1.json finalized (r868 bm-b: "
                   "PASS=%d PARTIAL=%d FAIL=%d N/A=%d) + research/MP1_TSGATE.md; "
                   "provenance=autofill launches %s (pid %s) + %s (pid %s); "
                   "r942 four-piece remedy leg-1 claim-backfill (MP1 runner "
                   "predates O-20260930-2355 claim law, completed burn "
                   "misread by fuse refusals=2; harvest flip=daemon next tick)"
                   % (vc["PASS"], vc["PARTIAL"], vc["FAIL"], vc["N/A"],
                      launches[0]["ts"], launches[0].get("pid"),
                      launches[-1]["ts"], launches[-1].get("pid"))),
}
io.open(fp, "w", encoding="utf-8", newline="").write(
    json.dumps(claim, ensure_ascii=False, indent=1))
print("[backfill] claim written:", fp)
