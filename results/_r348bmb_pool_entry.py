# r348 bm-b S3: add TRIAL-LABOR-W1-SCREEN pool entry in status=waiting with
# explicit RAM flip-gate (autofill has NO RAM gate -- r348 probe; free RAM
# 2.0GB < 4GB dual-company discipline; W2-A census burn holding ~15.5GB
# no-kill). W2B waiting precedent r346 (pool zero-write avoids tick race).
# Byte-careful write: mirror original line endings + indent=1 (r339 law family).
import io
import json

path = "results/runnable_pool.json"
raw = io.open(path, "rb").read()
crlf = raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n")
d = json.loads(raw.decode("utf-8"))

assert not any(e.get("id") == "TRIAL-LABOR-W1-SCREEN" for e in d["entries"]), \
    "entry already present (idempotent abort)"

entry = {
    "id": "TRIAL-LABOR-W1-SCREEN",
    "ticket_ref": "T-2026-09-24-94 s2 screen slice (CEO O-20260927-2245 1000-wave trial + O-2026-09-27-2255 line-B; ticket science face claimed bm-b r346, s1 prereg FROZEN fe0fa81c r347 + sec.9.3 amendment f92993e5; batch execution face open per shard law, ticket lock only holds science face)",
    "prereg_ref": "research/TRIAL_LABOR_W1_PREREG.md FROZEN R99 (registered-six anchors + 71 school fns x REFINE_BENCH 448-axis x uniform 500/family; T-84s3 sha256 dedup; K=200 dual-null p95 freeze-line; G1'v2/G2 funnel cumulative-N DSR; seeds 20283500/20284000/20284500 registered R250) + research/TRIAL_GRAMMAR_LEDGER.md append-only (same-grammar-rerun ban sec.4); TRIAL intake face: zero judgment claims pre-funnel",
    "runner": "scripts/trial_labor_w1.py",
    "runner_args": ["screen", "--shard", "0", "--shards", "1"],
    "lane_owner": None,
    "priority": 1,
    "status": "waiting",
    "entered_at": "2026-09-28 00:11:00",
    "data_gates": "in-runner fail-closed: prep gates already PASS 6/6 (G-PANEL/G-CENSUS census==P-5C FROZEN grid leg-L 1253 via p5c import / G-ANCHOR registered-six live.paper replay faithful / G-EXCLUDE armed); cells = 658 distinct candidates + K=200 dual nulls; per-shard jsonl checkpoint cross-kill resume; runner-internal RAM guard armed (r348-A build); selftest 19/19 re-verified r348 second session",
    "shards": [
        {
            "key": "screen-0of1",
            "status": "waiting",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/trial_labor_w1/checkpoint/screen_shard_0of1.jsonl (row-level done-set resume)",
            "note": "single shard; measured 1.2s/cell x 858 cells / 12 workers ~ 2min BelowNormal light batch; B7b consumer keys contract verified in selftest"
        }
    ],
    "workers_plan": {
        "workers": "worker_cap() pool (12 observed; W2-A burn parallel 12+4=16 exactly-saturated BelowNormal)",
        "priority": "BelowNormal",
        "note": "FLIP GATE waiting->ready: ONLY when machine free RAM >= 4GB (dual-company discipline; r348 probe: autofill.py has NO RAM gate so waiting status is the ONLY protection; W2-A census burn holds ~15.5GB no-kill, free RAM 2.0GB at entry time). Expected unlock: W2-A finalize harvest (pool CENSUS-FUS-S2-W2A done-flip window) frees worker RSS. Flip executor: any round post-unlock, one-line status edit, honest note in round report"
    },
    "note": "r348 queue: waiting not ready per W2B precedent r346 (pool zero-write avoids tick claim race under RAM squeeze); autofill tick 10-min cadence would grab ready entry immediately -- DO NOT flip under <4GB"
}
d["entries"].append(entry)

s = json.dumps(d, ensure_ascii=False, indent=1)
if crlf:
    s = s.replace("\n", "\r\n")
with io.open(path, "wb") as f:
    f.write(s.encode("utf-8"))
    if s.endswith(("\n", "\r\n")) and not raw.endswith(b"\n"):
        pass
back = json.load(io.open(path, encoding="utf-8"))
assert back["entries"][-1]["id"] == "TRIAL-LABOR-W1-SCREEN"
assert back["entries"][-1]["status"] == "waiting"
print("pool entry added: TRIAL-LABOR-W1-SCREEN status=waiting | entries:",
      len(back["entries"]), "| crlf mirror:", crlf)
