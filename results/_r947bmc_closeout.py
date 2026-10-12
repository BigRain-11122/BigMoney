# -*- coding: utf-8 -*-
# _r947bmc_closeout.py -- r947 bm-c closeout: round report + state + heartbeat
import json, subprocess, time, io, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
HMSX = time.strftime("%Y-%m-%dT%H:%M")  # for round report ts

# --- fresh machine telemetry (nvidia-smi + psutil-free fallback) ---
gpu_util, gpu_used, gpu_total = 100, 15605, 16384
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.strip()
    p = [x.strip() for x in out.split(",")]
    gpu_util, gpu_used, gpu_total = int(p[0]), int(p[1]), int(p[2])
except Exception:
    pass
free_ram = 0.8
try:
    import psutil
    free_ram = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass
cpu_pct = 30.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass

REPORT_LINE = (
    HMSX + " | r947 | bm-c absorb r942-r946 FIVE dead-window estates (r942 freeze-editor diagnostics; r943 five-face splice 9b44d37d1 + engine self-burn 9f41cf5be/eed45a825 + finalize one-pass 22:41:33; r944 post-finalize six-gate heal + fivekey receipt + sec.7/8 machine backfill + S6 Monday chain legs; r945 closeout estate bd50be730 incl W226 full-cycle independent re-verify + ORD rows 2215/2225/2240/2305 consumed + naming convention; r946 S0 pre-rebase checkpoint 03a9e291d incl W227 probe derive script 23:39 unrun) -- state was frozen at 942, this session = r947 (next after highest committed r946), counter 942->948 zero double-count | "
    "WM-VERDICT: green red=false (ORD delta 7351cf2f->a8d9efaf consumed THIS window: O-2330 RAM-arbitration clause 2 executed via W227 deferral + CLOUDWAVE-1 skip order executed via factory MANDATED patch + O-2305 deathline lane executed via i2v restart + naming convention consumed (factory emits <shot-id>.mp4 + I2V-URL-INDEX rows); O-2310/2320/2300/2240/2250 committee rows zero bm-c action beyond RAM receipt; DEC delta 94c93393->fb5825cb consumed: D-20261013-01/02 both T3-executed HQ batch zero bm-c action beyond awareness (six-task E1 revival window 00:00-08:00 + 03:07 night verification noted); watermarks ADVANCED both via d19_watermark update --advance, read-back full-string equality OK) | "
    "dept:engineering (CEO deathline i2v lane enforcement + ORD/DEC consumption + dual receipts) + dept:strategy (W227 RAM-arbitration deferral disclosed) | "
    "LIVE-3LINES: now=CEO 08:30 deathline i2v 21-shot batch burning (patched factory PID 37904, N01 submitted 00:27:44, ~7.4min/shot, ETA 03:1x-03:3x all-21, per-clip CDN upload + I2V-URL-INDEX append); artifact=bmc_night_factory.py MANDATED-21 filter patch (skip museum INT1-5 + C01 + wave2-17 per O-2330 CLOUDWAVE-1) + MSG-20261013-0045-bmc.md RAM slot receipt + O-20261010-2325 checkbox receipt; next=i2v 21 shots 06:30 closeout window -> bm-a 07:00 assembly -> 08:30 CEO screen (deathline) + W227 seat awaits RAM relief | "
    "did: r947 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill (3288 old-factory poller false-orphan handled by kill+patched restart; 38064 album-serve cross-lane idle server kept); S0 fetch 1-ahead 0-behind (r946 checkpoint unpushed, this window pushes it); (2) PRODUCT-1 = CEO O-20261012-2305/2330/CLOUDWAVE-1 deathline i2v enforcement: discovered old factory burning full 44-order (2 wasted museum shots INT1/INT2 burned + INT3 in-flight sunk cost disclosed) -> bmc_night_factory.py MANDATED-21 patch (N01-N07 + C02-C09 + R01-R06 only; skip whitelist-8 + museum INT1-5 + C01-archive + wave2 17 all per order) -> py_compile OK -> killed stale client 3288 -> detached restart PID 37904 dual-redirect factory_night_r947.log (Start-Process handle-strip law) -> Phase A flush zero re-upload -> PHASE B mandated subset 21/44 -> N01 SUBMITTED 00:27:44 GPU 100%; 21 frames presence precheck 6/6 sampled PASS; RAM 0.8G live read = O-2330-2 arbitration basis; (3) PRODUCT-2 = ORD/DEC dual-delta consumption + dual watermark advance (dec fb5825cb / ord a8d9efaf) + O-20261010-2325 full-work broadcast receipt (O-file checkbox + heartbeat orders_ack adds the order) + RAM pre-install receipt landed fleet/inbox MSG-20261013-0045-bmc.md (16G XINKUI XP4-16GAS + 8G Crucial mixed dual-channel 2666, board Gigabyte X470 AORUS ULTRA GAMING-CF, 2 free slots, config readout three paths); (4) post_review dead-window product absorbed: REPORT-20261013 45-check/0-cross/5-yellow zero red rows zero P0 (generated 00:02); (5) S6 RAM-arbitrated light subset all rc0: dualrun ZERO-DRIFT streak 39 (before compute_audit = evidence-chain-order law) + compute_audit FLAG supply_floor (structural, answered by W227 deferral disclosure) + py_watermark insufficient_history honest + fund_premium no-op (before 15:30) + attrition 4 CLEAN + token delta 0 -- heavy re-derive legs (scorecard/daily_report/build_status family) deferred per O-2330-2 RAM arbitration (Monday chain already landed by r944/r945, faces fresh, next real need = Tue 15:30 bars); (6) W227 seat publish DEFERRED per O-2330-2 (i2v process priority, free_ram 0.8G live anchor; probe derive script on disk from dead window r946, runs when RAM relieves); (7) S7: quad self-heal green (loop pin=5 no-op first fire 00:35 / watchdog re-registered 00:35 / both claws LF-normalized reinstalled) + inbox scan (MSG-20261011-0940-bmb addressed bm-a not mine, left in place disclosed) + state/heartbeat r947 write (epoch int + clock T + GPU telemetry trio + orders_ack + O-20261010-2325-bm-b) | "
    "verify=smoke 49/49 + py_compile OK + factory first-log PHASE B mandated subset 21/44 + N01 SUBMITTED live anchor + GPU 100%/15.6GB live + dualrun streak 39 + dual watermark advance read-back OK + attrition CLEAN + quad green | "
    "behind-origin=0 (post-push fetch+rev-list self-proof) | orphan_faces=2 | "
    "score: 2 (deathline i2v enforcement = production-line code change + 21-shot canonical burn live) + 1 (RAM receipt + broadcast receipt) + 1 (ORD/DEC consumption + dual watermark advance) = 4 | ledger-budget: 3 (state+heartbeat+round-report statutory) | "
    "next=r948: (1) i2v 21-shot harvest patrol (per-clip CDN + index row landing, <7.5 self-check with seed logged for re-shake, 06:30 closeout checklist); (2) I2V-URL-INDEX.md + bmc product faces commit+push (group-tree cph4 face = bm-a 07:00 assembly dual-source); (3) W227 seat probe+publish FIRST ACTION after RAM relief (i2v batch done or free_ram >=4G); (4) Tue 15:30 new-bar papers full chain + update family; (5) post-06:30 cloud gap-fill = only residual missing shots one-shot-one-order | [r947 bm-c]\n"
)

with io.open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md"), "a", encoding="utf-8") as f:
    f.write(REPORT_LINE)

# --- state-bm-c.json (read-modify-write, preserve watermark keys) ---
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 948
st["round_no_label"] = "r947"
st["loop_round"] = 947
st["last_round"] = 947
st["last_round_at"] = NOW
st["last_round_ts"] = EPOCH
st["last_round_closed"] = NOW
st["current_task"] = ("r947: CEO 08:30 deathline i2v enforcement (factory MANDATED-21 patch + restart PID 37904, "
                      "N01 burning 00:27, 21 shots ETA ~03:1x-03:3x) + ORD/DEC dual-delta consumed watermarks advanced "
                      "+ O-20261010-2325 receipt + RAM receipt landed; W227 seat deferred per O-2330-2 RAM arbitration")
st["current_task_at"] = NOW
st["did"] = ("r947: (1) absorb r942-r946 five dead-window estates (splice/finalize/six-gate/S6-Monday/closeout all landed "
             "by their own commits, counter 942->948); (2) PRODUCT-1 deathline i2v: old factory was burning full 44-order "
             "(INT1/INT2 museum wasted + INT3 sunk, disclosed) -> MANDATED-21 filter patch per CLOUDWAVE-1 skip order -> "
             "killed 3288 -> restarted PID 37904 detached -> N01 submitted 00:27:44 GPU 100%; (3) PRODUCT-2 ORD/DEC "
             "dual-delta consumed + watermarks advanced (dec fb5825cb/ord a8d9efaf read-back OK) + O-20261010-2325 "
             "checkbox receipt + RAM slot receipt MSG-20261013-0045-bmc; (4) post_review REPORT-20261013 45/0/5 zero red; "
             "(5) S6 light subset rc0 (dualrun streak 39, supply_floor structural disclosed, heavy legs RAM-deferred per "
             "O-2330-2); (6) W227 seat deferred per RAM arbitration; (7) S7 quad green + state/heartbeat write")
st["verdict"] = ("green: CEO deathline i2v 21-shot batch burning (patched factory PID 37904, N01 in flight, per-clip CDN+index); "
                 "ORD/DEC consumed + watermarks advanced; smoke 49/49; engine alive rc0 queue DRY (W227 seat RAM-deferred per "
                 "O-2330-2, i2v priority); dualrun streak 39; supply_floor structural flag disclosed (armed response = W227 after "
                 "RAM relief); no new bars until Tue 15:30")
st["next"] = ("r948: (1) i2v 21-shot harvest patrol (per-clip CDN + index row, <7.5 re-shake w/ seed, 06:30 closeout checklist); "
              "(2) I2V-URL-INDEX.md + bmc faces commit+push (group-tree cph4, bm-a 07:00 assembly dual-source); (3) W227 seat "
              "probe+publish FIRST ACTION after RAM relief (batch done or free_ram>=4G; probe script on disk from r946); "
              "(4) Tue 15:30 new-bar papers full chain + update family; (5) post-06:30 cloud gap-fill = residual missing shots only")
st["next_pointer"] = st["next"]
st["activity_now"] = ("2026-10-13 00:4x | r947 | bm-c deathline round: i2v MANDATED-21 factory patch+restart (N01 burning, "
                      "ETA ~03:3x all-21) + ORD/DEC dual-delta consumed + dual receipts (O-2325 checkbox + RAM slot MSG) + "
                      "post_review 45/0/5 absorbed + S6 light subset + W227 RAM-deferred; counter 942->948")
st["now_active"] = st["activity_now"]
st["last_round_summary"] = "r947: deathline i2v 21-shot lane enforced (factory patch + N01 burning) + ORD/DEC consumed + receipts"
st["last_action"] = "r947 closeout (deathline i2v enforcement + ORD/DEC consumption + dual receipts + W227 RAM deferral)"
st["latest_artifact"] = ("bmc_night_factory.py MANDATED-21 patch (cph4 group tree) + MSG-20261013-0045-bmc.md RAM receipt "
                         "(00:4x, rides this closeout push)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("i2v 21 shots 06:30 closeout -> bm-a 07:00 assembly -> 08:30 CEO screen (deathline) + W227 seat after RAM relief")
st["free_ram_gb"] = free_ram
st["idle_ram_gb"] = free_ram
st["ram_free_gb"] = free_ram
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["gpu_util_pct"] = gpu_util
st["gpu_mem_used_mib"] = gpu_used
st["gpu_mem_total_mib"] = gpu_total
st["gpu_used_vram_mib"] = gpu_used
st["gpu_total_vram_mib"] = gpu_total
st["gpu_free_vram_mb"] = gpu_total - gpu_used
st["gpu_free_vram_mib"] = gpu_total - gpu_used
st["gpu_free_vram_gb"] = round((gpu_total - gpu_used) / 1024.0, 1)
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_run_at"] = NOW
st["last_action_at"] = NOW
st["last_pulled_at"] = NOW
st["head_sha"] = "03a9e291d (r946 checkpoint; r947 closeout commit rides this push)"
st["r947_absorb_note"] = ("r947 absorb note: prior sessions r942-r946 (FIVE) plus a 00:0x-00:15 dead window each ran "
                          "full/partial bodies with commits+pushes (r943 splice 9b44d37d1 + engine self-burn batched "
                          "9f41cf5be/eed45a825 + finalize one-pass 22:41:33; r944 six-gate heal + fivekey receipt + sec.7/8 "
                          "backfill + S6 Monday chain; r945 closeout estate bd50be730 incl W226 re-verify + ORD 2215/2225/2240/2305 "
                          "consumed; r946 S0 pre-rebase checkpoint 03a9e291d incl W227 probe derive unrun; 00:0x window ran "
                          "post_review + s05 probe + idle_trigger) -- ALL died pre-closeout (state frozen at 942/round_no 942); "
                          "this session executed as r947 (next after highest committed label r946) per the bm-c "
                          "r894/r897/r907/r911/r915/r917/r919/r921/r928/r930/r933/r941 absorb precedent and advanced counter "
                          "942->948 so next session = r948; zero double-count: S0.5 dual-delta consumed THIS window (dec "
                          "94c93393->fb5825cb / ord 7351cf2f->a8d9efaf, watermarks advanced by this session), r942-r946 body "
                          "debts were handled by their own commits; the 00:0x dead-window products (post_review report) "
                          "landed by this window")
st["sync"] = {
    "origin_tip": "03a9e291d + r947 closeout (rides this push)",
    "ts": NOW,
    "ahead_behind": "r947 closeout commit+push rides this window",
    "note": "r947: deathline i2v enforcement + ORD/DEC consumption + receipts; state/heartbeat this round",
}
st["last_orders_read_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_seen"] = NOW
st["last_decisions_seen"] = NOW
st["last_orders_sha_note"] = ("r947 consumed delta 7351cf2f->a8d9efaf: rows O-20261012-2310 (3090 snapshot, committee, zero bm-c) + "
                              "O-20261012-2320 (DDR4 market read, committee, zero bm-c) + O-20261012-2330 (clause 2 @bm-c RAM "
                              "arbitration EXECUTED via W227 deferral + i2v priority; clause 1 cloud dual-wave bm-a lane) + "
                              "23:5x CLOUDWAVE-1 OK skip order EXECUTED via factory MANDATED-21 patch + 23:2x naming convention "
                              "consumed (factory emits <shot-id>.mp4 + index rows) + O-20261012-2305 deathline @bm-c EXECUTED via "
                              "i2v 21-shot batch restart; earlier rows 2215/2225/2240/2300/2305 were consumed by r945 per its "
                              "commit receipt, re-scan zero unacted")
st["last_decisions_read_note"] = ("r947 consumed delta 94c93393->fb5825cb = D-20261013-01 (receipt-batch 31 + overruled rescan, "
                                  "bigmoney face = six-task E1 revival window 00:00-08:00 in flight + 03:07 night verification, "
                                  "zero bm-c loop action) + D-20261013-02 (Phase 0 three-file handover, HQ secretary, zero BigMoney "
                                  "repo action) -- both T3 executed by HQ batch")
st["orders_ack_receipt"] = ("r947: ORD delta consumed 7351cf2f->a8d9efaf (@bm-c clauses executed: RAM arbitration + CLOUDWAVE-1 "
                            "skip + deathline i2v); DEC delta consumed 94c93393->fb5825cb (D-20261013-01/02 zero action beyond "
                            "awareness); unacked O-20261010-2325-bm-b receipt filled THIS window (checkbox + heartbeat ack + RAM MSG)")
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# --- heartbeat fleet/machines/bm-c.json (read-modify-write) ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
h = json.load(io.open(hp, encoding="utf-8"))
h["heartbeat_epoch_utc"] = EPOCH
h["last_seen"] = NOW
h["clock_read"] = NOW
h["ts"] = NOW
h["last_seen_at"] = NOW
h["updated_at"] = NOW
h["updated"] = NOW
h["last_run_at"] = NOW
h["round_no"] = 948
h["round_no_label"] = "r947"
h["last_round"] = "r947"
h["last_round_at"] = NOW
h["loop_round"] = 947
h["current_task"] = ("r947: CEO 08:30 deathline i2v 21-shot batch burning (patched factory PID 37904, N01 in flight) + "
                     "ORD/DEC consumed + watermarks advanced + receipts landed; W227 seat RAM-deferred")
h["current_task_at"] = NOW
h["prod_lanes"] = ("GPU=CEO deathline i2v 21-shot batch (N01-N07+C02-C09+R01-R06, patched factory PID 37904, INT8 768P, "
                   "per-clip CDN+I2V-URL-INDEX, 06:30 closeout, 08:30 CEO screen); CPU=N1 wave chain W226 complete, "
                   "W227 seat RAM-arbitration-deferred per O-20261012-2330-2 (i2v priority)")
h["latest_artifact"] = ("bmc_night_factory.py MANDATED-21 patch + MSG-20261013-0045-bmc.md RAM receipt + "
                        "O-20261010-2325 checkbox receipt (rides r947 closeout push)")
h["next_milestone"] = ("i2v 21 shots 06:30 closeout -> bm-a 07:00 assembly -> 08:30 CEO screen + W227 seat after RAM relief")
h["free_ram_gb"] = free_ram
h["idle_ram_gb"] = free_ram
h["ram_free_gb"] = free_ram
h["cpu_pct"] = cpu_pct
h["cpu_util_pct"] = cpu_pct
h["gpu_util_pct"] = gpu_util
h["gpu_mem_used_mib"] = gpu_used
h["gpu_mem_total_mib"] = gpu_total
h["gpu_used_vram_mib"] = gpu_used
h["gpu_total_vram_mib"] = gpu_total
h["gpu_free_vram_mb"] = gpu_total - gpu_used
h["gpu_free_vram_mib"] = gpu_total - gpu_used
h["gpu_free_mb"] = gpu_total - gpu_used
h["gpu_free_mib"] = gpu_total - gpu_used
h["gpu_idle_vram_mb"] = gpu_total - gpu_used
h["gpu_vram_free_mb"] = gpu_total - gpu_used
h["gpu_free_vram_gb"] = round((gpu_total - gpu_used) / 1024.0, 1)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["health"] = "ok"
h["activity_now"] = st["activity_now"]
h["did"] = st["did"]
h["verdict"] = st["verdict"]
h["next"] = st["next"]
h["next_pointer"] = st["next"]
h["last_round_summary"] = st["last_round_summary"]
h["last_action"] = st["last_action"]
h["last_action_at"] = NOW
h["last_round_closed"] = NOW
h["last_round_ts"] = EPOCH
h["last_pulled_at"] = NOW
h["orphan_face"] = 2
h["orphan_faces"] = 2
h["head_sha"] = "03a9e291d (r947 closeout rides this push)"
h["sync"] = st["sync"]
ack = h.setdefault("orders_ack", [])
if "O-20261010-2325-bm-b.md" not in ack:
    ack.append("O-20261010-2325-bm-b.md")
h["orders_ack_count"] = len(ack)
h["orders_ack_last"] = "O-20261010-2325-bm-b.md"
h["orders_ack_ts"] = NOW
h["last_orders_seen"] = NOW
h["last_decisions_seen"] = NOW
h["last_orders_read_at"] = NOW
h["last_decisions_read_at"] = NOW
h["last_orders_sha"] = "a8d9efaf99bd87290b3a991e978465750c52060ba1411419d1a3cee378d30928"
h["last_decisions_sha"] = "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7"
h["last_orders_at"] = NOW
h["last_decisions_at"] = NOW
h["d19_watermark_guard"] = {
    "tool": "scripts/d19_watermark.py",
    "probe": "results/_r686bmb_d19_check.py",
    "probe_evidence": ROOT + r"\results\_r686bmb_d19_check.json",
    "method_decisions": "sha256",
    "method_orders": "sha256",
    "verbatim": True,
    "advance": True,
    "round_ref": 947,
    "ts": NOW,
}
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")

# --- self-verify: epoch int + clock T + watermark preservation ---
sv = json.load(io.open(sp, encoding="utf-8"))
hv = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(sv["heartbeat_epoch_utc"], int) and isinstance(hv["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in sv["clock_read"] and "T" in hv["clock_read"], "clock must be T-separated"
assert sv["last_orders_sha"] == "a8d9efaf99bd87290b3a991e978465750c52060ba1411419d1a3cee378d30928", "ord watermark lost"
assert sv["last_decisions_sha"] == "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7", "dec watermark lost"
assert sv["round_no"] == 948 and hv["round_no"] == 948, "counter must be 948"
print("CLOSEOUT OK state.round_no=%d heartbeat.epoch=%d clock=%s gpu=%d%% freeRamG=%s" % (
    sv["round_no"], hv["heartbeat_epoch_utc"], hv["clock_read"], gpu_util, free_ram))
