# r454 bm-b closeout: state.json 453->454 + round report line + heartbeat (epoch int, T-clock)
import json, time, datetime

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# --- state.json (bm-b legacy face) ---
sp = "state.json"
d = json.load(open(sp, encoding="utf-8"))
d["round_no"] = 454
d["note"] = (
    "r454 CLOSED: S0 rebase-replay landed r453 escape to main (marks AA union 3-line zero-loss, push 82453589c..a08d0f353, "
    "REV-OSC SIG/BARS now on main for bm-a) + S6 38-leg chain ALL rc0 (driver1 legs1-7 then GBK-print crash at leg8 -> cont driver legs8-38; "
    "dualrun ZERO-DRIFT 45/3 @135 entries; watermark py_low_board_clear legal; update_daily 0-rows cutoff 09-29; regime breadth 0.83 trigger; "
    "market_clock CALL-0928 ORANGE_COOL; lhb 30min-guard no-op cutoff 09-28; foreign lanes 9x honest no-op; astock/etf panel fresh no-op; "
    "rev_osc idempotent; minute_feed throttle 13min<20min next-round catch; intraday marks tick appended 18 positions @09:58:25 (r454 product); "
    "fundamental fresh-skip 23.3h; b_layer_filter verdict; paper family bm-a-guarded skips; daily_report 5-faces; LIVE-202609-30 refreshed; token L1 0) "
    "+ orphan adoption: r453 session residual marks tick 09:55:01 adopted (file 5 lines all parse-verified, r462 law) "
    "-- NEXT r455: minute_feed 10:05 window + supply floor heal watch (W13 GENERATE bm-a sec12-15 + catalog flip), MF_IC_P1 parked EM source (bm-a collector), 15:30 post-close legs"
)
d["last_round_at"] = TS
d["last_round_ts"] = "r453"
d["ts"] = TS
d["updated"] = TS
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h["machine_id"] = "bm-b"
h["last_seen"] = TS
h["current_task"] = (
    "r454 CLOSED: r453 escape landed main via S0 rebase-replay (marks union zero-loss) + S6 38-leg all rc0 + "
    "intraday marks tick 09:58:25 (18 positions) + orphan 09:55:01 tick adopted; supply-floor heal watch W13 bm-a; MF_IC parked EM source"
)
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = TS
h["cpu_cores"] = 16
h["free_ram_gb"] = 5.6
h["gpu_free_vram_gb"] = 2.2
h["verdict"] = "healthy: chain all-green, board clear, legal idle build-window"
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# verify epoch int
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2.get("heartbeat_epoch_utc"), int), "epoch must be int"
assert "T" in h2.get("clock_read", ""), "clock_read must be T-separated ISO"
print("closeout written: state 453->454, heartbeat epoch", EPOCH, "int-verified, clock", TS)
