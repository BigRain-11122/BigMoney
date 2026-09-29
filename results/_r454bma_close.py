import json
import time
from datetime import datetime, timezone, timedelta

# --- heartbeat (bm-a only, types per R170/R178/R262 laws) ---
hb_path = "fleet/machines/bm-a.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
hb["current_task"] = ("r454 closed: dead-tick r453 S6 adoption (77 artifacts, r240 law) + "
                      "31-UU rebase storm resolved per canon (6 ALL_FACES mlv-union, x2 jsonl "
                      "line-union 1842 raw-decode OK, twins same-side, host faces local, 2 "
                      "manual take-new) + smoke 26/26 + attrition CLEAN; next = 5x HANDOVER "
                      "check + trial-labor board check")
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = 24
hb["gpu_idle_vram_gb"] = 0
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601 (R262)"
print("heartbeat ok epoch=", chk["heartbeat_epoch_utc"], chk["clock_read"])

# --- state (surgical round_no increment 454->455 + round fields) ---
st_path = "state-bm-a.json"
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 455
st["did"] = ("r454: dead-tick r453 S6 sweep adoption closeout (r240 adopt-verify-close law) -- "
             "02:38-slot tick landed S3 e959262a3 then died pre-S7 after full S6 chain (77 "
             "artifacts 02:41-42) + surgical round_no 453->454; forensics green (zero other "
             "bigmoney executors, all M-files in dead-tick window, autofill drift benign); "
             "adoption commit replayed onto bm-c r247/r248 window -> 31 UU + 1 UNKNOWN storm "
             "resolved per conflict-resolve canon: 6 ALL_FACES via merge_lane_views union, "
             "fundamental_b_layer_filter probe take-new (face name not in engine, fail-closed "
             "fallback), 4 host-guarded faces take-local (R31 authority), 12 snapshot probe "
             "take-new on staged blobs, twins same-side (daily_report x2 + live_usage x4), "
             "x2_watch_log line-union 1842 raw-decode verified (r443 acceptance), guard_scan "
             "manual adjudication take-new (files counts monotone, ts newer, S7 rescan "
             "supersedes); resolver results/_r454bma_resolve.py + probe2 committed")
st["verify"] = ("smoke 26/26; orders 122/122 both sweeps zero unacked; decisions 75 rows "
                "zero-new (tail=09-28 closed note); watermark red=false (next_pick=claimed "
                "moneyflow IC, lane event-attention-factors); attrition guard 4 ledgers CLEAN; "
                "reconcile 2-face drift (gate_attrition/crash_fuse) = observation-phase data "
                "recorded not fault; push 7f3f867db HEAD==origin; loop pin8 no-op, watchdog "
                "re-registered, pre-commit claw installed; heartbeat epoch int self-check")
st["next"] = ("r455: (1) 5x HANDOVER check due (round_no 455 multiple of 5); (2) TRIAL_LABOR "
              "board/pool check -> next wave face (W13 berth draft if queue clear / supply "
              "floor refill if ready<3) -- W12 runner-build belongs to bm-b, W5 runner-build "
              "to bm-c; (3) 10-01 month-first-round trio regen (idempotent) + REGIME_GUARD v3 "
              "date-gate hands-off; (4) S9C amend veto window to 10-07, implementation leg "
              "only after; (5) P0 hot-cold CODELY reorg owed (~10.5KB over 10KB hard line)")
st["current_task"] = "r454 closed; next = 5x HANDOVER check + trial-labor board check + W13 berth face if clear"
st["last_round_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
st["updated"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
json.dump(st, open(st_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state ok round_no=", st["round_no"])

# --- round report line (fleet/README sec.6 fixed fields) ---
rp_path = "round_reports-bm-a.md"
line = (f"{st['updated']} | r454 | dead-tick r453 S6 adoption (r240 law: 77 artifacts "
        "forensics-verified, adoption commit) + 31-UU rebase storm resolved per canon "
        "(6 ALL_FACES mlv-union + x2 line-union 1842 + twins same-side + host faces local + "
        "2 manual take-new; resolver _r454bma_resolve.py) | smoke 26/26, orders 122/122, "
        "attrition CLEAN, watermark green, push 7f3f867db HEAD==origin, reconcile 2-face "
        "drift observation-recorded | r455: 5x HANDOVER check + TRIAL_LABOR board check "
        "(W13 berth face), CODELY hot-cold reorg P0\n")
with open(rp_path, "a", encoding="utf-8") as f:
    f.write(line)
print("report line appended")
