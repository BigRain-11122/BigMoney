# _r881bmc_closeout.py -- S7 closeout: state + heartbeat + round report
# atomic writes (r881; r880 label belongs to the killed session per its
# commit f705f1ccc, so round_no skips to 881 to avoid identity collision).
import json
import datetime
import time
import re

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
NOW_H = NOW.strftime("%Y-%m-%d %H:%M:%S")

DID = (
    "r881 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=0 "
    "(read-only); killed r880 estate NOT re-inherited (bm-b r888 already "
    "healed: 510880 ext_slots recipe-c + MSG-1658/1720 processed) -- verified "
    "then built on top; S0 dirty-tree ff surgery: 38 tracked-dirty faces, "
    "19-entry incoming-intersection via backup/checkout/ff/union (treasure "
    "guard rc3 on token_usage ledger -> extract-aside + face-identical "
    "no-merge proof; pool_core_samples union +2 dead-session rows; sync_face "
    "settle 26B absorbed delta untouched) -> HEAD ff 296593d80 + own "
    "delivery f8bbab59e (push range self-proof, behind=0); (2) S0.5 orders "
    "delta=0 (70/70 acked), group decisions/orders watermarks byte-match "
    "(zero action); (3) S1 smoke 49/49 (bm-b 510880 fix verified green "
    "fleet-wide); satengine rc0 alive; job_list 0; queue heads not probed "
    "(standing product line active); (4) PRODUCT: T-184 ticket JSON heal "
    "(single orphan <<<<<<< HEAD conflict marker from r888 rebase union, "
    "byte-surgery + json valid 18 keys, board machine-readability restored) "
    "+ W18 pool enforcement edit (GENERATE session-flip done: products "
    "landed f705f1ccc 16:57:43, cmd_generate no-claim W17 family design, "
    "flip stops no-claim re-fire loop; SCREEN-SHARD-1..7 lane_owner bm-c -> "
    "ANY per W17 handover precedent: bm-c free RAM 0.8-1.5GB << 4GB r354 "
    "gate, CEO game session 4.6GB + MV chain = legal yield, shard-0 worker "
    "parked r379/r491; SHARD-0 lane KEPT bm-c = machine-local checkpoint "
    "cross-machine double-burn bar; bm-b target alive ram 6.2G 17:11 "
    "heartbeat; data_deps all git-tracked = data-locality gate passes; "
    "double-file law content-level edit, dualarm ZERO-DRIFT streak 2 "
    "post-edit) + MSG-20261011-1735-bmc handover dispatch to bm-b; (5) "
    "watermark RED pool-batch-runnable-idle-low-cpu consumed SAME-ROUND by "
    "the lane relay (7 shards ignition_sla candidates now claimable by "
    "healthy machine); py_watermark insufficient_history (post-restart "
    "window, disclosed); compute_audit FLAG:ignition_sla pre-relay baseline; "
    "(6) S6 chain 37 legs rc0 (dualrun ZERO-DRIFT streak 2 / scorecard "
    "142.6s full derive / daily_report faces=5 / ceo_live twin) + 4 "
    "new-bar-gated legs skipped honest (Sunday: Friday bar 2026-10-09 "
    "already processed) + monthly legs not month-first; scorecard/t35_export/"
    "daily_scorecard host-guard ABSENCE vs protocol text disclosed (r378 "
    "family text drift, HQ-FEEDBACK candidate, no lane violation this round "
    "-- deterministic idempotent faces); (7) S7: loop pin=5 no-op, watchdog "
    "MISSING -> re-registered 17:38 (real self-heal catch), both claws "
    "installed, attrition 4 CLEAN, idle --worked (idle_rounds=0); inbox: "
    "MSG-1658/1720 addressed bm-b (bm-b r888 processed, left for recipient "
    "move), MSG-0940 addressed bm-a (not mine), MSG-1735 mine outbound."
)

CURRENT_TASK = (
    "当前活: W18 screen 让渡落地+shard-0 本机 RAM 窗等待（CEO 游戏会话占 "
    "RAM·合法让路）| 最近实物: W18 pool enforcement edit + T-184 票 JSON 修复"
    "（f8bbab59e·2026-10-11T17:35+08:00）| 下个里程碑: bm-b 接烧 shards 1-7 + "
    "screen-finalize 并面 → JUDGE → CEO 48h 报时钟（judge 落地起算）"
)

# -- state-bm-c.json
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
prev = st.get("round_no", 879)
assert prev == 879, "unexpected prev round_no %s" % prev
st["round_no"] = 881
st["round_no_label"] = "r881"
st["last_round"] = 881
st["did"] = DID
st["current_task"] = CURRENT_TASK
st["current_task_at"] = NOW_ISO
st["clock_read"] = NOW_ISO
st["ts"] = NOW_ISO
st["updated"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["last_seen"] = NOW_ISO
st["last_seen_at"] = NOW_ISO
st["last_round_at"] = NOW_ISO
st["last_round_ts"] = NOW_ISO
st["note"] = (
    "r881 closed: W18 lane relay (shards 1-7 ANY, generate done-flip, "
    "shard-0 bm-c kept) + T-184 JSON heal + killed-r880 estate built-on; "
    "round_no skips 880 (dead-session label per f705f1ccc)."
)
st["last_decisions_read_at"] = "2026-10-11T17:26:00+08:00"
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# -- heartbeat fleet/machines/bm-c.json
hp = "fleet/machines/bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = NOW_ISO
h["ts"] = NOW_ISO
h["clock_read"] = NOW_ISO
h["current_task"] = CURRENT_TASK
h["current_task_at"] = NOW_ISO
h["heartbeat_epoch_utc"] = int(time.time())
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["note"] = ("r881: W18 lane relay delivered; shard-0 parked-waiting RAM "
             "window (legal yield); S6 37 legs rc0.")
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)

# verify epoch int + clock T-separator (R170/R178/R262 law)
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], "clock sep"

# -- round report line
rp = "round_reports-bm-c.md"
line = (
    "%s | r881 | S0 dirty-tree ff surgery (38 dirty/19 intersection, pool "
    "union +2, token ledger extract-aside proof) + smoke 49/49 + PRODUCT: "
    "T-184 ticket JSON heal (orphan conflict marker) + W18 pool enforcement "
    "(GENERATE done-flip + SHARDS-1..7 lane ANY RAM-gate relay W17 "
    "precedent, SHARD-0 bm-c double-burn bar, MSG-1735 to bm-b) + watermark "
    "RED consumed same-round + S6 37 legs rc0 + S7 watchdog missing->rebuilt "
    "| evidence: f8bbab59e push self-proof behind=0, dualrun ZERO-DRIFT "
    "streak 2, attrition CLEAN, smoke 49/49 | next: bm-b shard pickup "
    "verify + screen-finalize consolidation + judge chain (48h CEO clock)\n"
    % NOW_ISO
)
with open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)
print("closeout writes OK: state r881, heartbeat epoch int, report line")
