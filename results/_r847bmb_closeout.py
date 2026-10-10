# r847 bm-b closeout: heartbeat + state update (ASCII-only)
import json, time, datetime, psutil, subprocess

root = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / (1024**3), 1)
cores = psutil.cpu_count(logical=True)
gpu_free_mb = 0
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=15)
    gpu_free_mb = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    gpu_free_mb = 0

verdict = ("GREEN: r847 stewardship wait-window round (smoke 49/49; D19 ord ADVANCED 3af479f1->24e6066e same-round consumed, "
           "dec a20664ec zero-delta; fleet orders 65/65 ack zero unacked; attrition CLEAN; board/job/queues empty; "
           "pool W17-JUDGE ready lane_owner=bm-a -> yielded per R31; SatEngine alive rc0; idle cleared via --worked "
           "(S6 41-leg product chain + astock stewardship); audit flags supply_gap/supply_floor = W18 drain-gated by design "
           "awaiting bm-a W17-JUDGE drain; py_low_with_work_cands legal = astock rebuild in-flight network-bound fetch; "
           "T23 census physical dependency continues, disk 2553/5217 accelerating, ETA improved ~00:00-01:00 vs 02:10 prior)")
did = ("r847: stewardship round: S0 absorb 11 daemon face files (8+3 satengine race re-absorb) + pull --rebase up-to-date; "
       "S0.5 fleet orders 65/65 zero unacked; D19 dual watermark probe: dec zero-delta + ord ADVANCED 3af479f1->24e6066e "
       "(2 new group rows consumed: mv0001 KF dispatch -> countermand, both non-quant + W17 shard yied-to-bm-a/bm note acked); "
       "smoke 49/49; S3 fixed order green (wm red=false next_pick claimed; SatEngine rc0 alive queue 0); S6 41 legs 40 rc0 + "
       "alloc rc=2 known P5 510880 TRANSFER-pending honest; astock rebuild lock alive disk 2553/5217 pace accelerating "
       "(1814@22:5x -> 2221@23:1x -> 2553@23:18); claim faces lawfully yielded (W17-JUDGE bm-a lane R31; board/job empty; "
       "backlog row-4 MiniGame anti-dup stands); S7 four-piece self-heal (loop pin=2 no-op, watchdog registered, both claws "
       "LF-normalized) + attrition guard CLEAN + idle --worked cleared")

# heartbeat
hp = root + r"\fleet\machines\bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "round": 847, "round_no": 847,
    "now_active": "r847 closeout: stewardship wait-window round (S6 41 legs 40 rc0 + alloc rc=2 known 510880 pending; astock rebuild 2553/5217 accelerating; D19 ord watermark advanced 24e6066e)",
    "current_task": "r848 queue: astock rebuild completion verify (improved ETA ~00:00-01:00) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)",
    "task": "r848 queue: astock rebuild completion verify (improved ETA ~00:00-01:00) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)",
    "next": "r848 queue: astock rebuild completion verify (improved ETA ~00:00-01:00) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg drafting window if holds / G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)",
    "latest_artifact": "r847: results/_r847bmb_s6chain.log (41 legs: 40 rc0 + alloc rc=2 known P5 510880 TRANSFER-pending) + thermo/dualarm/market_clock/rev_osc/minute_feed faces refreshed + docs/daily_report/REPORT-2026-10-10.md + docs/live_usage/LIVE-2026-10-10.md, 2026-10-10 23:1x",
    "next_milestone": "astock panel complete (~00:00-01:00 improved ETA) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) -> N2 U3(1) prereg draft window",
    "verdict": verdict,
    "last_action": did,
    "did": did,
    "last_round_at": now, "last_seen": now, "updated": now, "ts": now,
    "clock_read": now, "updated_at": now,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": cores,
    "free_ram_gb": ram_free_gb,
    "gpu_free_vram_mb": gpu_free_mb,
    "gpu_free_vram_gb": round(gpu_free_mb / 1024, 2),
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_faces": 0,
    "orphan_face_note": "r847 orphan probe 23:1x py_faces=15 orphans=0",
    "sync": {"last_push_ts": now, "note": "r847 closeout; post-push fetch self-proof behind=0 pending S7 verify"},
})
json.dump(h, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=True)

# state.json (bm-b uses shared state.json per fleet README s6)
sp = root + r"\state.json"
s = json.load(open(sp, encoding="utf-8"))
s.update({
    "machine_id": "bm-b",
    "round_no": 847,
    "round": 847,
    "round_no_label": "r848",
    "note": did,
    "last_round_at": now, "ts": now, "updated": now, "last_seen": now,
    "clock_read": now,
    "did": did,
    "verdict": verdict,
    "last_action": did,
    "now_active": "r847 closeout: stewardship wait-window round (astock 2553/5217 accelerating, S6 41 legs done, claim faces yielded)",
    "current_task": "r848 queue: astock completion verify -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W18 drain-gated (bm-a owns w17-judge)",
    "task": "r848 queue: astock completion verify -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W18 drain-gated (bm-a owns w17-judge)",
    "next": "r848 queue: astock completion verify -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W18 drain-gated (bm-a owns w17-judge)",
    "latest_artifact": "r847: results/_r847bmb_s6chain.log (41 legs: 40 rc0 + alloc rc=2 known P5 510880 TRANSFER-pending) + docs/daily_report/REPORT-2026-10-10.md + docs/live_usage/LIVE-2026-10-10.md refreshed, 2026-10-10 23:1x",
    "next_milestone": "astock panel complete (~00:00-01:00 improved ETA) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) -> N2 U3(1) prereg draft window",
    "last_orders_sha": "24e6066ef2f1a472df20d2c34ee22575e2751ade",
    "last_orders_at": now,
    "last_orders_read_at": now,
    "last_orders_sha_note": "r847: ord ADVANCED 3af479f1->24e6066e via scripts/d19_watermark.py update --advance --receipt results/d19_watermark.json (r537 SHA-1 40-hex raw-blob PIN; delta consumed same round; read-back full-string equality OK); dec a20664ec zero-delta",
    "last_round_ts": now,
    "updated_at": now,
})
json.dump(s, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
print("heartbeat+state updated; epoch=%d int=%s; clock_read=%s; ram_free=%.1fGB gpu_free=%dMB cores=%d" % (epoch, isinstance(epoch, int), now, ram_free_gb, gpu_free_mb, cores))
