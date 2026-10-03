# r630 bm-b closeout: state.json + heartbeat updates (python = CJK-safe, epoch int)
import json, time, datetime, subprocess

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
RAM_FREE_GB = 3.2
CPU_PCT = 36

NOTE = (
    "r630: S0 dead-rebase closeout + full origin integration: inherited mid-interactive-rebase "
    "from dead R629 session detected (detached HEAD + rebase-merge, 2 picks pending); r613 daemon-live-write "
    "continue false-refusal reproduced (staging fix insufficient) -> r501 route-1/3 net path (commit -C + quit "
    "+ update-ref + checkout main); 2 superseded picks skipped (content subsumed per reland law, pool faces NOT "
    "replayed); value-nulls conflict-marker surgical strip (k=336/337 restored byte-exact from r629c blob); "
    "daemon ~40s write treadmill -> isolated-worktree cherry-pick x4 (23 contested faces resolved origin-side: "
    "bm-a r637 hosted derives + surgical pool faces; bm-b own faces mine) -> push 917b88421 = origin/main, "
    "delivery self-proven; W2-JUDGE-SHARD-1 determinism CONFIRMED (local 18:53:44 complete 201/201, blob "
    "a44a55a81 == origin byte-identical; MSG-2005 state report to bm-a per their request; MSG-1902 delivered "
    "to origin); orders 151/151 zero-unacked; D-19 MATCH 4167b784; smoke 47/47; engine alive rc0 idle; "
    "S6 34 legs rc0 (dualrun streak 20 ZERO-DRIFT; REPORT/LIVE/dashboard three stale-takeover derives legal); "
    "S7 regs/claws/attrition CLEAN; HANDOVER bm-b r630 5x stamp filed (r625 missed = pit-79 disclosed); "
    "NULLS trio V351/Q239/D130 of 2000 in flight (RAM 3.2GB<4GB no new claims)"
)

# state.json (bm-b uses root state.json per S5)
with open("state.json", encoding="utf-8") as f:
    state = json.load(f)
state["round_no"] = 630
state["note"] = NOTE
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at", "last_seen"):
    state[k] = NOW
state["round_no_label"] = "round 630 (bm-b)"
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# heartbeat fleet/machines/bm-b.json
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 630
hb["round_no_label"] = "round 630 (bm-b)"
hb["current_task"] = "FUND trio NULLS burn watch (V351/Q239/D130 of 2000) + post-integration health watch"
hb["verdict"] = "GREEN (origin integrated 917b88421 delivery-proven; burns healthy; smoke 47/47; S6 rc0; SHARD-1 determinism confirmed)"
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = CPU_PCT
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
    hb[k] = RAM_FREE_GB
hb["ram_gb"] = 27.5
for k in ("ts", "updated", "updated_at"):
    hb[k] = NOW
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-proof: epoch must be JSON int, clock T-separated
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be ISO T-separated"
print("state round_no=%d epoch_type=%s clock=%s" % (
    state["round_no"], type(chk["heartbeat_epoch_utc"]).__name__, chk["clock_read"]))
