# -*- coding: utf-8 -*-
"""r830 bm-b closeout: state.json + heartbeat + round report line (load-modify-save, no retyping)."""
import json, time, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
R = "r830"
verdict = ("r830: guard/maintenance round - S6 ~33 legs rc0 zero-fail (dualrun ZERO-DRIFT streak 15; thermo rebuild; dualarm "
           "DUALARM-2026-09-30 written; daily_report REPORT-2026-10-10; live_usage LIVE-2026-10-10); D19 orders watermark "
           "ADVANCED ord=180e3dee (new group rows consumed: bm-b FleetLink verified ALIVE v1.4 - adoption pending bm-a "
           "poke only, 10:3x nudge row stale; mv0001 30s bm-b=backup standby); queue heads T20/E9 both COLLISION_RISK -> "
           "yielded per T-18; pool ready 9 all lane_owner=bm-c (W17 screen+judge, not touched, cooperative note echoes "
           "bm-a MSG-0935); W18 window gated on W17-JUDGE drain (bm-c); compute_audit FLAG supply_gap+ignition_sla "
           "SHARD-5/6/7+JUDGE (lane=bm-c); py_watermark=py_low_board_clear legal idle; smoke 49/49; orders 60/60 "
           "zero unacked; attrition CLEAN (1 healed historical); orphans=0; Sat no-op day for all collectors")

# ---- state.json (bm-b uses root state.json per S5) ----
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 830
s["round"] = 830
s["round_no_label"] = R
for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read", "last_round_ts", "updated_at"):
    s[k] = now
s["note"] = verdict
s["did"] = verdict
s["verdict"] = verdict
s["now_active"] = "r830 closeout: heartbeat + commit/push"
s["current_task"] = ("r831: E9 yield-watch (T-18 probe first) + W18 drafting window once W17-JUDGE drains (bm-c lane) + "
                     "mv0001 30s backup-standby (bm-c overload trigger only) + Monday 2026-10-12 09:15 minute_feed gated run")
s["task"] = s["current_task"]
s["next"] = s["current_task"]
s["last_action"] = "r830: S6 ~33 legs rc0 + D19 orders watermark advanced (bm-b FleetLink alive v1.4, adoption pending bm-a poke)"
s["latest_artifact"] = ("r830: results/regime_gate_dualarm/DUALARM-2026-09-30.json (refreshed, index=BEAR emotion-armed) + "
                        "docs/live_usage/LIVE-2026-10-10.md + docs/daily_report/REPORT-2026-10-10.md, 2026-10-10 11:0x")
s["next_milestone"] = ("r831+: E9/T20 yield-watch + W18 draft window post W17-JUDGE drain (bm-c) + Monday 2026-10-12 09:15 "
                      "minute_feed next gated run (panel current, routine append)")
s["last_orders_sha"] = "180e3dee7a082df1ad61da6bad857b0ca389d198"
s["last_orders_read_at"] = now
s["d19_watermark_guard"]["round_ref"] = 830
s["d19_watermark_guard"]["ts"] = now
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json (orders_ack preserved by load-modify-save) ----
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h["round"] = 830
h["round_no"] = 830
h["last_seen"] = now
h["ts"] = now
h["clock_read"] = now
h["updated"] = now
h["updated_at"] = now
h["last_round_at"] = now
h["heartbeat_epoch_utc"] = epoch
assert isinstance(h["heartbeat_epoch_utc"], int)
h["now_active"] = "r830 closeout: heartbeat + commit/push"
h["current_task"] = s["current_task"]
h["task"] = s["current_task"]
h["next"] = s["current_task"]
h["verdict"] = ("r830: guard/maintenance round; watermark red=false; py_low_board_clear legal idle; queue heads T20/E9 "
                "yielded (COLLISION_RISK); smoke 49/49; orders 60/60 acked; D19 ord watermark ADVANCED 180e3dee; "
                "attrition CLEAN; orphans=0; FleetLink listener v1.4 ALIVE (adoption pending bm-a poke)")
h["last_action"] = "r829: minute_feed 2-day gap closed (+2380 rows, behind 2->0) + S6 ~40 legs rc0"
h["latest_artifact"] = s["latest_artifact"]
h["next_milestone"] = s["next_milestone"]
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_faces"] = 0
h["orphan_face_note"] = "probe 17 py faces 0 orphans (r830 rc0)"
h["ram_free_gb"] = 10.4
h["ram_free_pct"] = 43.0
h["gpu_free_vram_gb"] = 3.4
h["gpu_free_vram_mb"] = 3456
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ack_n = len(h["orders_ack"])
assert isinstance(ack_n, int) and ack_n >= 60, "orders_ack list must survive load-modify-save"

# ---- round report line (S5: bm-b uses logs/iteration-loop/round_reports.md) ----
line = (f"| {now} | {R} | bm-b guard/maint round: S6 ~33 legs rc0 zero-fail (dualrun streak15, thermo rebuild, "
        f"DUALARM-2026-09-30, REPORT/LIVE-2026-10-10); D19 ord watermark ADVANCED 180e3dee (group orders consumed: "
        f"bm-b FleetLink ALIVE v1.4 adoption-pending-bm-a-poke, 10:3x nudge=stale face; mv0001 30s bm-b=backup standby); "
        f"T20/E9 heads COLLISION_RISK yielded; pool ready 9 all lane=bm-c (W17, coop note echoes bm-a MSG-0935); "
        f"W18 window gated on W17-JUDGE drain; compute_audit FLAG supply_gap+ignition_sla SHARD-5/6/7+JUDGE (lane=bm-c); "
        f"py_watermark py_low_board_clear; smoke 49/49; orders 60/60 zero unacked; attrition CLEAN; orphans=0; "
        f"Sat=collector no-op day | evidence: results/_attrition_guard_scan.json, results/regime_gate_dualarm/DUALARM-2026-09-30.json, "
        f"listener http://localhost:8790/health v1.4 OK | next: r831 E9/W18 yield-watch + Mon 10-12 09:15 minute_feed gated run |\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)
print(f"CLOSEOUT OK {R}: state round_no=830, heartbeat epoch={epoch} (int), ack_count={ack_n}, report line appended at {now}")
