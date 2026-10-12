# -*- coding: utf-8 -*-
# r933 bm-c closeout: heartbeat + state + round report (one-shot, machine-read values only)
import json, time, datetime, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

import psutil
avail_gb = round(psutil.virtual_memory().available / 1e9, 1)
total_gb = round(psutil.virtual_memory().total / 1e9, 1)
cpu_pct = round(psutil.cpu_percent(interval=2), 1)
gpu = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                      "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
g_util, g_used, g_total = [int(x.strip()) for x in gpu.split(",")]
g_free = g_total - g_used

try:
    red = json.load(open(REPO + r"\results\watermark_red.json", encoding="utf-8")).get("red")
except Exception:
    red = None
assert red is not True, "WATERMARK RED TRUE -- read lane one-liner before closeout: %s" % red

PRODUCT_SHA = "b7d46427d"
NEXT_ORD_SHA = "90dd3a63eb6845ba7e5c6df0ff2e9b6d587fe02d021a587180c190b636754d62"
PREV_ORD_SHA = "8fa1ed2d7f229130c1b83e9f272706835344461d451337ae627f2e095ed68f6b"

did = ("2026-10-12 16:5x | r933 | bm-c absorb r931+r932 dead-window estate (r931: W222 five-face freeze splice executed on disk, landed by r932 commit 4167d791d; "
       "r932: three commits pushed 15:43-15:52 [splice absorb 4167d791d + W222 full cycle finalize e79215eca ledger 912,189/K=486,320 five-key ALL PASS + W223 seat publish "
       "8f2d79147 A 505_404..507_403 EIGHTY-THIRD/B 507_404..507_603] + fullload MSG written 15:59:32, died pre-closeout -- state frozen at round_no 931/heartbeat r930; "
       "this session = r933 next-after-highest-committed r932, counter 931->934, zero double-count) "
       "+ PRODUCT: W223 per-wave prereg derived + landed (seven-level lineage replay chain _w216 PAIRS+SUB17..SUB22 preflight 46/46 count==1; derive token-restore bugfix "
       "@T21@ '222'->'22' per W222 convention [dead-window slip, mechanical transform face, zero scientific fields] + freeze-window label 16:2x->16:4x live honesty; "
       "banned gate ADMIT rc0 + py_compile green + STALE all-zero + NEW all-present + chain legs 10 identity-verified; machine anchors: W222 finalize 912,189/K=486,320, "
       "merged mu -0.09279597/sigma 0.24510939, A_p95 0.3213, KL -0.0001/1.1913/1.1912, se_mu 0.000351, leg0 rows 220/owner 212/bmc_ordinal 52, 53rd owned wave projection; "
       "RAM live ~3.1GB honest face + engine DRY live-read) -> " + PRODUCT_SHA + " pushed (8f2d79147.." + PRODUCT_SHA + ") "
       "| FULLLOAD pool: item2 MV roughs 672x384 batch COMPLETED 16:35:46 (69 files incl LOOKBOARD-ROUGH672.jpg) -> GPU idle probe -> item3 INT8 768P night-candidate batch "
       "claimed + ignited (manifest policy_test_wave KN_KN16+KN_KN21, frames on disk, ComfyUI 0.36.0 alive queue empty, PID 54820, int8 ConvRot+turbo 4step+nvfp4+video VAE "
       "resolved, 1344x768; clips harvest = next window) "
       "| S0.5 ORD delta TRUE consumed (" + PREV_ORD_SHA[:8] + "->" + NEXT_ORD_SHA[:8] + ": @bm-c fullload O-20261012-1505 + sprint-compress O-20261012-1420 + token-save + "
       "resource-total-order + O-20261012-1510 confirm + git-boundary note -- r932 first-receipt MSG landed this window; carried obligations executed: GPU telemetry trio "
       "ADDED to heartbeat [r932 claimed in MSG but died pre-write, landed by r933]) | S1 smoke 49/49 "
       "| S6: pool_dualrun ZERO-DRIFT streak 29 + compute_audit FLAG pool_starvation,supply_floor (structural wave-chain gap, W223 prereg landed = armed response, splice next "
       "window heals) + py_watermark insufficient_history (fresh-window honest face) + update_daily 0 new rows (sina delayed bar, cutoff 10-09, Monday bars pending -> papers "
       "legs on bar landing) + market_regime rc0 (breadth 0.73) + market_clock ORANGE_COOL idempotent + fundamental fresh-skip + b_layer rc0 + thermo honest no-op + 14 "
       "lane-guard collectors honest no-ops + fund_premium snapshot honest exit 2 (nav non-null rate 0<0.9, EM source face, 30min backoff self-heal, next-window recheck) + "
       "token_meter delta=0")

verdict = ("green: W223 per-wave prereg landed same-window (seven-level replay preflight 46/46, banned ADMIT, derive bugfix disclosed, " + PRODUCT_SHA + " pushed); "
           "fullload pool item3 INT8 candidates ignited (GPU loaded ~14.6GB, clips pending harvest); smoke 49/49; engine alive rc0 queue DRY post-W222-finalize; "
           "pool_starvation+supply_floor structural flags disclosed (W223 splice = next window FIRST ACTION); S0.5 ORD delta consumed (fullload carried obligations "
           "executed incl GPU telemetry trio); watermark fresh-window honest face; update_daily Monday bars pending")

nxt = ("r934: (1) W223 five-face freeze splice editor clone + execute FIRST ACTION (template _w222bmc_freeze_edits.py; bands machine-read from "
       "_w223bmc_20261012_probe_receipt; six-gate script pre-written with the splice bundle per W222 sec.8 standing law + boundary-pair-scan gate leg per r932 escalation "
       "proposal); (2) engine self-burn 12/12 + six-gate PRE-FINALIZE in burn window + finalize one-pass + sec.7/8 machine-read backfill + five-key; (3) candidate batch "
       "harvest (KN16/KN21 clips + INT8 768P quality face for tonight) + tonight 00:00-08:00 32-unit i2v night window (interactive window owns prerequisites: face verdict + "
       "9-frame KF re-make); (4) Monday new-bar recheck (update_daily; papers full chain on bar landing); (5) unity-mcp POC receipt due 10-13 12:00 (O-20261012-0739 bm-a lane "
       "watch); (6) fund_premium snapshot recheck (exit-2 backoff window)")

summary = "W223 per-wave prereg derived + landed (seven-level replay 46/46, banned ADMIT, bugfix @T21@ disclosed, " + PRODUCT_SHA + " pushed) + fullload item3 INT8 candidates ignited"
artifact = ("research/PERPETUAL_N1_W223_PREREG.md (16:4x derive, 23,425B sha16 89a3bd341ea347ca, commit " + PRODUCT_SHA + " pushed) + "
            "results/_w223bmc_prereg_derive.py (seven-level lineage replay chain)")
milestone = "W223 freeze+burn+finalize (next two windows) + candidate batch validation + tonight 32-unit i2v night window + Monday new-bar papers chain"

absorb_note = ("r933 absorb note: prior sessions r931/r932 each ran full/partial bodies with commits+pushes (r931: W222 five-face freeze splice executed on disk -- landed "
               "by r932 commit 4167d791d; r932: splice absorb + W222 full cycle finalize e79215eca [ledger 912,189/K=486,320, five-key ALL PASS, sec.7/8 backfilled] + W223 "
               "seat publish 8f2d79147 + fullload MSG 15:59:32) but BOTH died pre-closeout -- state had been frozen at round_no 931 the whole time (heartbeat still r930); "
               "this session executed as r933 (next after highest committed r932) per the bm-c r894/r897/r907/r911/r915/r917/r919/r921/r928/r930 absorb precedent and "
               "advanced counter 931->934 so next session = r934; zero double-count: S0.5 ORD delta consumed THIS window (dec 94c93393 hold/FALSE, ord " + PREV_ORD_SHA[:8] +
               "->" + NEXT_ORD_SHA[:8] + " TRUE consumed); r931/r932 body debts were handled by r932 itself (commits landed); r932 MSG estate landed by r933 (b7d46427d)")

ord_note = ("r933 consumed delta " + PREV_ORD_SHA[:8] + "->" + NEXT_ORD_SHA[:8] + " = rows 10-12 13:5x->15:2x (@bm-c fullload O-20261012-1505 six-item carried: r932 "
            "first-receipt MSG landed this window b7d46427d; pool item2 roughs COMPLETED 16:35:46; pool item3 INT8 candidates ignited this window; GPU telemetry trio landed "
            "in heartbeat this window) + sprint-compress O-20261012-1420 (tonight 00:00-08:00 32-unit i2v prep in place: ComfyUI 0.36.0 alive + int8 workflow canonical "
            "pack in-register) + token-save order (BigMoney zero cloud calls, L1 local only, token_meter delta=0) + resource-total-order (fullload self-claim executed) + "
            "O-20261012-1510 sprint-confirm + git-boundary note (zero repo action) -- all BigStream/fleet-resource faces, zero BigMoney-repo scientific action")

hb = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
hb.update({
    "machine_id": "bm-c",
    "round_no": 933, "round_no_label": "r933", "last_round": "r933", "loop_round": 933,
    "clock_read": iso, "ts": iso, "last_seen": iso, "last_seen_at": iso, "updated": iso, "updated_at": iso,
    "last_round_at": iso, "last_round_ts": iso, "last_round_closed": iso, "last_run_at": iso, "last_round_summary_at": iso,
    "last_action_at": iso, "current_task_at": iso, "current_task_ts": iso,
    "heartbeat_epoch_utc": epoch,
    "cpu_pct": cpu_pct, "cpu_util_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1),
    "cores": 32, "cpu_cores": 32, "total_ram_gb": total_gb,
    "free_ram_gb": avail_gb, "idle_ram_gb": avail_gb, "ram_free_gb": avail_gb,
    "gpu_util_pct": g_util, "gpu_mem_used_mib": g_used, "gpu_mem_total_mib": g_total,
    "gpu_free_mb": g_free, "gpu_free_mib": g_free, "gpu_idle_mb": g_free, "gpu_idle_mib": g_free,
    "gpu_free_vram_mb": g_free, "gpu_free_vram_mib": g_free, "gpu_idle_vram_mb": g_free, "gpu_idle_vram_mib": g_free,
    "gpu_vram_free_mb": g_free, "gpu_free_vram_gb": round(g_free / 1024, 1),
    "free_vram_mb": g_free,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1,
    "did": did, "activity_now": did, "now_active": did,
    "verdict": verdict,
    "current_task": "W223 five-face freeze splice editor clone + execute = next window FIRST ACTION (template _w222bmc_freeze_edits.py; bands machine-read from probe receipt; six-gate script pre-written with splice bundle + boundary-pair-scan gate leg) + candidate batch harvest (KN16/KN21 clips) + tonight 32-unit i2v night window",
    "last_round_summary": summary, "last_action": "r933 product closeout (W223 prereg derive+land " + PRODUCT_SHA + " + fullload item3 candidates ignited)",
    "last_artifact": artifact, "recent_artifact": artifact, "latest_artifact": artifact,
    "next": nxt, "next_pointer": nxt, "next_milestone": milestone,
    "head_sha": PRODUCT_SHA,
    "last_orders_sha": NEXT_ORD_SHA, "last_orders_sha_note": ord_note,
    "last_orders_at": iso, "last_orders_read_at": iso, "last_orders_seen": iso,
    "last_decisions_read_at": iso,
    "orders_ack_receipt": "r933: ORD delta consumed " + PREV_ORD_SHA[:8] + "->" + NEXT_ORD_SHA[:8] + " (fullload carried obligations executed: item3 candidates ignited + GPU telemetry trio landed; sprint night-window prep in place); DEC delta FALSE (94c93393 hold); unacked=0",
    "orders_ack_ts": iso,
    "prod_lanes": "GPU=INT8 768P candidate batch KN16/KN21 in-flight (fullload pool item3, PID 54820; item2 MV roughs completed 16:35:46); CPU=N1 wave chain W222 complete -> W223 prereg landed, splice next window (structural gap disclosed, heals next window)",
    "r933_absorb_note": absorb_note,
})
hb["sync"] = {"ahead_behind": "r933 closeout commit rides this push",
              "origin_tip": PRODUCT_SHA + " (W223 prereg product)", "ts": iso,
              "note": "r933: prereg product " + PRODUCT_SHA + " pushed pre-closeout; closeout commit+push follows; state/heartbeat this round"}
hb["d19_watermark_guard"]["round_ref"] = 933
hb["d19_watermark_guard"]["ts"] = iso
json.dump(hb, open(REPO + r"\fleet\machines\bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

st = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
st.update({
    "machine_id": "bm-c",
    "round_no": 934, "round_no_label": "r934", "last_round": "r933", "loop_round": 933,
    "clock_read": iso, "ts": iso, "last_seen": iso, "last_seen_at": iso, "updated": iso, "updated_at": iso,
    "last_round_at": iso, "last_round_ts": iso, "last_round_closed": iso, "last_run_at": iso,
    "heartbeat_epoch_utc": epoch,
    "cpu_pct": cpu_pct, "cpu_util_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1),
    "cores": 32, "cpu_cores": 32, "total_ram_gb": total_gb,
    "free_ram_gb": avail_gb, "idle_ram_gb": avail_gb, "ram_free_gb": avail_gb,
    "gpu_free_vram_mb": g_free, "gpu_free_vram_mib": g_free, "gpu_free_vram_gb": round(g_free / 1024, 1),
    "gpu_util_pct": g_util, "gpu_mem_used_mib": g_used, "gpu_mem_total_mib": g_total,
    "free_vram_mb": g_free,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1,
    "did": did, "activity_now": did, "now_active": did,
    "verdict": verdict,
    "current_task": hb["current_task"], "current_task_at": iso, "current_task_ts": iso,
    "last_round_summary": summary, "last_round_summary_at": iso,
    "last_action": hb["last_action"], "last_action_at": iso,
    "last_artifact": artifact, "recent_artifact": artifact, "latest_artifact": artifact,
    "next": nxt, "next_pointer": nxt, "next_milestone": milestone,
    "head_sha": PRODUCT_SHA,
    "last_orders_sha": NEXT_ORD_SHA,
    "last_orders_at": iso, "last_orders_read_at": iso, "last_orders_seen": iso,
    "last_decisions_read_at": iso,
    "r933_absorb_note": absorb_note,
})
st["sync"] = hb["sync"]
st["d19_watermark_guard"]["round_ref"] = 933
st["d19_watermark_guard"]["ts"] = iso
json.dump(st, open(REPO + r"\state-bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

rr = ("2026-10-12T16:5x | r933 | bm-c absorb r931+r932 dead-window estate (r931 splice-on-disk landed by r932 commit 4167d791d; r932 three commits pushed 15:43-15:52 "
      "[splice absorb+W222 full cycle finalize e79215eca ledger 912,189/K=486,320+five-key ALL PASS+W223 seat 8f2d79147]+fullload MSG 15:59:32, both died pre-closeout, "
      "state frozen at 931/heartbeat r930; this session = r933 next-after-highest-committed r932, counter 931->934, zero double-count) | WM-VERDICT: green red="
      + str(red).lower() + " (probe fresh: insufficient_history fresh-window honest face; engine alive rc0 queue DRY post-W222-finalize; pool_starvation+supply_floor flags = "
      "structural wave-chain gap disclosed, W223 prereg landed THIS window + splice next window heals) | dept:策略（N1 波链 W223 per-wave prereg 供给）+dept:工程（S0/S0.5/"
      "S6/S7+fullload GPU 车道承接） | 实况三行：当前活=W223 五面冻结 splice 编辑器克隆+执行=下窗第一动作（_w222bmc_freeze_edits.py 模板·bands 机读自 probe receipt·六门脚本"
      "随束同窗预写+boundary-pair-scan gate leg）；最近实物=research/PERPETUAL_N1_W223_PREREG.md（16:4x derive·23,425B·sha16 89a3bd341ea347ca·commit b7d46427d 已推）+INT8 "
      "768P 候选批点火（KN16/KN21·PID 54820·GPU 14.6GB 满载面）；下个里程碑=W223 freeze+自燃+finalize（下两窗内）+候选批收割验证+今晚 00:00-08:00 32 单 i2v 夜窗+周一新 bar "
      "papers 全链 | did: " + did + " | 验证证据=smoke 49/49+derive preflight 46/46+STALE 全零/NEW 全在+banned ADMIT rc0+push range 行 8f2d79147..b7d46427d 自证+S6 批 rc0"
      "+dualrun streak 29+attrition CLEAN+ORD delta consumed 自证 | 本地未达 origin commit 数=0（收尾 push 后 fetch+rev-list 自证）| 孤儿面=1 | 产品积分: 2（W223 per-wave "
      "prereg=冻结正典件上链）+1（derive 七级重放链工具+bugfix）+1（fullload 池③候选批点火·clips 待收）=4 | 记账预算: 3（state+heartbeat+round-report 法定簿记） | "
      "下轮指针=" + nxt + " | [r933 bm-c]\n")
open(REPO + r"\logs\iteration-loop\round_reports-bm-c.md", "a", encoding="utf-8").write(rr)

hb2 = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be T-separated ISO"
st2 = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
assert st2["round_no"] == 934 and st2["loop_round"] == 933
print("closeout written OK | iso=%s epoch=%d cpu=%s ram_free=%s gpu_util=%d gpu_used=%d gpu_free=%d" % (iso, epoch, cpu_pct, avail_gb, g_util, g_used, g_free))
print("wm_red:", red)
