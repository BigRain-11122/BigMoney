import json, time, datetime, io

now = datetime.datetime.now()
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

ORD_NEW = "e2423fefcae0e9f9f0b54e9375dd11f4d51dd14c"
ORD_OLD = "58b9ee8823dafaa3807e35e33931474c48938c9f76475e39393a2b61b9004169"
DEC_CUR = "6910a9ed7d1a99044b607c6307d2e6f9e44b8e9f3dd0d7c301e5ea57cd5c2cb9"

# ---------- state-bm-c.json ----------
sp = "state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 1022
s["last_orders_sha"] = ORD_NEW
s["last_orders_at"] = ts_iso
s["last_orders_read_at"] = ts_iso
s["last_orders_sha_note"] = (
    "r1021: ORD delta " + ORD_OLD[:8] + "->" + ORD_NEW[:8] + " consumed (1 new row = 10-15 05:4x wave3 A-trial 29/29 + casting 16/16 receipt row -- bm-c r1016 own delivery receipt, downstream faces (@bm-a director board review -> A-batch 1344x768 + casting x3 + B-batch 12 unlock) are bm-a-side, zero new BigMoney execution owed this window); watermark self-advanced"
)
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no ->", s["round_no"])

# ---------- heartbeat fleet/machines/bm-c.json ----------
hp = "fleet/machines/bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["machine_id"] = "bm-c"
h["last_seen"] = ts_iso
h["clock_read"] = ts_iso
h["ts"] = ts_iso
h["heartbeat_epoch_utc"] = epoch
h["heartbeat_epoch_utc_type"] = "int (assert)"
h["round_no"] = 1021
h["last_round"] = "r1021"
h["last_round_at"] = ts_iso
h["prod_lanes"] = (
    "CPU=N1 W245 seat watch (W244=bm-a chain in-flight: freeze splice landed 07:11:10, burn/finalize theirs per seat-first law); "
    "GPU=ComfyUI resident idle (wave3 trial boards DELIVERED 05:43; A-batch fullres + casting promotion x3 + B-batch 12 frames gated on bm-a director review/face-lock)"
)
h["current_task"] = "r1021 watch window: W245 seat awaits W244 finalize (bm-a); MV V3 downstream awaits bm-a director review; bars 10-15 due 15:30"
h["current_task_at"] = ts_iso
h["activity_now"] = ts_iso + " | r1021 | bm-c: watch window + S6 37-leg chain all rc0 + S7 quad green | counter 1021->1022"
h["now_active"] = h["activity_now"]
h["latest_artifact"] = (
    "r1021: S6 chain 37/37 rc0 88.9s (dualrun streak 51 + compute_audit + wm red=false + REPORT/LIVE-2026-10-15 faces refreshed + "
    "market_clock ORANGE_COOL idempotent + collectors all lane-guard no-ops) + idle/attrition/queue-guard tri-green"
)
h["next_milestone"] = (
    "W245 seat same-window probe on W244 finalize landing (bm-a chain, ETA <=48h); bars 10-15 15:30 -> papers full chain; "
    "bm-a director wave3 review -> A-batch fullres + casting + B-batch unlock (GPU lane)"
)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["ram_note"] = "protect: i2v/ComfyUI 常驻+烧窗期·巡检令 O-20261014-0312 §2 紧态如实保留"
h["did"] = (
    "r1021: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill + fetch behind=0 (repo up-to-date); "
    "(2) S0.5 ORD delta TRUE consumed " + ORD_OLD[:8] + "->" + ORD_NEW[:8] + " (1 row = own r1016 receipt, zero action owed) + DEC hold " + DEC_CUR[:8] +
    " + local orders unacked=0 + inbox empty; "
    "(3) S1 smoke 49/49; "
    "(4) watch window honest: satengine ALIVE rc0 + W244 freeze landed 07:11 (bm-a burn/finalize in-flight, finalize NOT landed at close -> W245 seat awaits per seat-first) + "
    "jobs 0 + fleet tasks 0 open + P2/P3 heads all-done + backlog claimable=1 but RAM 3.7pct<40pct gate -> green_idle=false honest not-claim-eligible, idle_rounds stays 0 + "
    "MF panel source-blocked (bm-a lane 30-min self-heal, next_pick claimed IC batch parked on panel completion) + "
    "MV V3 GPU lane structurally upstream-gated (wave3 boards out for bm-a director review since 05:43); "
    "(5) S6 chain 37/37 rc0: dualrun ZERO-DRIFT streak 51 + compute_audit + wm red=false + update_daily pre-15:30 legal 0-rows + regime breadth 0.77 shadow recorded + "
    "market_clock CALL-2026-10-14 ORANGE_COOL idempotent + collectors all lane-guard no-ops (bm-a/bm-b lanes) + fund_premium pre-15:30 no-op (bm-c lane fires post-15:30) + "
    "fundamental 10.5h-fresh skip + b_layer mask regen rc0 + aggr/grid papers idempotent at cutoff 10-14 + REPORT-2026-10-15 + LIVE-2026-10-15 faces refreshed + token delta=0 + "
    "post_review today 150 rows 0-x; "
    "(6) S7: attrition 4 CLEAN + loop pin=5 no-op + watchdog re-registered idempotent + both claws installed + orphan face=2 zero-kill + "
    "qsg scan CLEAR (tech 5/explore 4 live rows 0 findings); counter 1021->1022"
)
h["verdict"] = (
    "green: r1021 watch window (W245 seat awaits bm-a W244 finalize -- freeze landed 07:11, burn/finalize in-flight; MV GPU lane awaits bm-a director review; "
    "bars 15:30; S6 37/37 + S7 quad green)"
)
h["verify"] = "receipts: smoke 49/49 + S6 chain 37/37 rc0 (driver results/_r1021bmc_s6_driver.py) + dualrun streak 51 + attrition 4 CLEAN + qsg CLEAR + S7 quad green + closeout push rides this window"
h["next"] = (
    "r1022: (1) W245 seat same-window probe when W244 finalize lands (facts from W244 finalize lineage SUB new-sides, R34-style; bm-c turn likely per rotation); "
    "(2) bars 10-15 due 15:30 -> update_daily gate -> papers full chain (live.paper REGIME_GUARD + t35 openfill + t24 x2 + aggr/alloc/grid/system_v1 + export + faces); "
    "(3) bm-a director wave3 review receipts -> A-batch fullres 1344x768 + casting 2-type x3 seeds + B-batch 12 frames unlock (GPU generation-visual lane); "
    "(4) pool/W19 supply resumes post-W244 finalize (RW-5 freeze lift); (5) MF panel completion watch -> IC reference batch (bm-a collector lane)"
)
h["next_pointer"] = h["next"]
h["last_decisions_sha"] = DEC_CUR
h["last_decisions_at"] = ts_iso
h["last_orders_sha"] = ORD_NEW
h["last_orders_at"] = ts_iso
h["last_round_summary"] = "r1021: watch window honest (W245 awaits bm-a W244 finalize; MV GPU lane awaits bm-a director review) + S6 37-leg all rc0 + ORD 1-row receipt consumed; counter 1021->1022"
h["last_artifact"] = h["latest_artifact"]
h["full_load_selfproof"] = {
    "占用一行": "GPU=ComfyUI 8188 resident idle (wave3 trial delivered; queue empty, next burn gated on bm-a director review) + CPU=N1 W245 seat watch (W244 burn/finalize=bm-a chain in-flight)",
    "当前活": "r1021 watch window + S6/S7 maintenance green (37/37 + quad)",
    "下一交付物": "r1022: W245 seat on W244 finalize landing; 15:30 bars -> papers full chain; MV GPU unlock on bm-a director receipts",
    "队列水位": "N1 engine 0 burning on bm-c (W244=bm-a wave) · MV V3 wave3 trial 29+16 delivered, A-batch/B-batch gated upstream · P2/P3 queues all-done · bars 15:30"
}
h["free_ram_gb"] = 0.9
h["ram_free_gb"] = 0.9
h["idle_ram_gb"] = 0.9
h["gpu_free_vram_mb"] = 14590
h["gpu_free_vram_mib"] = 14248
h["free_vram_mb"] = 14590
h["cpu_pct"] = 39.0
h["cpu_util_pct"] = 39.0
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("heartbeat written, epoch int =", epoch, "round_no =", h["round_no"])
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("epoch type assert PASS")

# ---------- round report append ----------
rp = "round_reports-bm-c.md"
line = (
    ts_iso + " | r1021 | bm-c watch window: ORD delta consumed 1 row (own r1016 receipt, zero action) + W245 seat awaits bm-a W244 finalize (freeze landed 07:11, finalize in-flight) + "
    "MV V3 GPU lane upstream-gated (bm-a director review) + S6 chain 37/37 rc0 88.9s (dualrun streak 51, REPORT/LIVE-10-15 refreshed, collectors lane-guard no-ops) + "
    "S7 quad green + idle honest false (RAM 3.7pct gate) | evidence: results/_r1021bmc_s6_driver.py + smoke 49/49 + attrition 4 CLEAN + qsg CLEAR | "
    "next: W245 seat on finalize landing; bars 15:30 papers; bm-a review unlock\n"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended")
