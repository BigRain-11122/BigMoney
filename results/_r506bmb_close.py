import json, time

# --- heartbeat (bm-b writes only its own file) ---
hb = {
    "machine_id": "bm-b",
    "root_path": "C:\\Fluxgroup",
    "role": "compute-node",
    "joined": "2026-09-23",
    "last_seen": "2026-10-01T14:10:00+08:00",
    "heartbeat_epoch_utc": int(time.time()),
    "clock_read": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "current_task": "r506: N1-W9 wave frozen per O-1332 sec.1.2 (supply auto-triggers when bm-a NULLS harvest lands); T-139 stage-A akshare furnace complete (3 families judged-negative); LOWAMP-P2 finalize gate watch (17/18 done, NULLS bm-a in-flight ETA ~14:15)",
    "cpu_cores": 16,
    "free_ram_gb": 5.4,
    "gpu_free_vram_gb": 2.2,
    "total_ram_gb": 0.0,
    "cpu_util_pct": 47.0,
    "round_no": 506,
    "verdict": "r506 products: O-1332 acked+executed on bm-b faces (N1-W9 wave frozen: law sec.4 row + prereg + WAVE_CONFIGS + N1_BANDS mirror + selftest leg 3f + W9 materializer face + ADMIT machine-gate receipt, both selftests green; supply auto-trigger wired, blocked only by live NULLS) + T-139 stage-A MOM finalize (n=16 robust=0, three-family furnace judged-negative, ledger 380320) + MSG to bm-a (t139-complete) + NULLS double-burn yielded per MSG-1345 kill-advice (r297, bm-a original owner in-flight wins, partial 300 rows kept for union) + S6 34 legs rc0 (reconcile ZERO-DRIFT streak 2/3, audit supply_floor wave-tail legal, LIVE/REPORT ORANGE cap50 regenerated)",
    "orders_ack": [
        "O-20261001-1332-bm-c.md"
    ],
}
# preserve the full historical ack set: read previous file's ack list
prev = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
acks = set(prev.get("orders_ack", []))
acks.update(hb["orders_ack"])
hb["orders_ack"] = sorted(acks)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
json.dump(hb, open("fleet/machines/bm-b.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("heartbeat written: epoch int =", hb["heartbeat_epoch_utc"],
      "| acks =", len(hb["orders_ack"]), "| last ack:",
      hb["orders_ack"][-1])

# --- state.json (bm-b ledger) ---
st = json.load(open("state.json", encoding="utf-8"))
st["machine_id"] = "bm-b"
st["round_no"] = 506
st["note"] = ("r506: O-1332 CEO compute-saturation order acked+executed on bm-b faces -- "
              "N1-W9 wave frozen (law sec.4 W9 row A 32_100..34_099 / B 28_500..28_699 "
              "arithmetic continuation, ADMIT machine-gate receipt, prereg+WAVE_CONFIGS+"
              "N1_BANDS+selftest leg 3f+W9 materializer face, banned-gate ADMIT, dual "
              "selftests green; supply auto-triggers on NULLS harvest live=0) + T-139 "
              "stage-A akshare furnace complete (REV 121/LOWAMP 144/MOM 16 all robust=0 "
              "judged-negative, ledger 380,320, MSG to bm-a) + NULLS double-burn yielded "
              "per MSG-1345 (r297, bm-a 1017/2000 wins, partial 300 rows union-ready) + "
              "S6 34 legs rc0 + smoke 47/47")
st["last_round_at"] = "2026-10-01T14:10:00+08:00"
st["last_round_ts"] = "2026-10-01T14:10:00+08:00"
st["ts"] = "2026-10-01T14:10:00+08:00"
st["updated"] = "2026-10-01T14:10:00+08:00"
st["updated_at"] = "2026-10-01T14:10:00+08:00"
json.dump(st, open("state.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("state round_no =", st["round_no"])
