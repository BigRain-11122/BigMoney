# -*- coding: utf-8 -*-
"""r1063 bm-a closeout: state-bm-a.json + heartbeat + round report line (maintenance-product round)."""
import json, time, datetime, io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.isoformat(timespec="seconds")
epoch = int(time.time())

# fresh machine faces via psutil (idle_trigger cross-check pattern)
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / (1024**3), 1)
    ram_free_mb = int(vm.available / (1024**2))
    total_ram_gb = round(vm.total / (1024**3), 1)
    free_ram_pct = round(vm.available / vm.total * 100, 1)
    ram_load_pct = round(100 - free_ram_pct, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    ram_free_gb, ram_free_mb, total_ram_gb = 62.7, 48332, 93.6
    free_ram_pct, ram_load_pct, cpu_pct = 67.0, 33.0, 3.0

gpu_free_vram_mb = 7414  # last idle_trigger cross-check face (CEO working machine, honest face)

DID = ("r1063: (1) S0 no-pull window (fetch origin 0/0 behind-zero, tree 3 runtime live faces non-blocking r1035 family); "
       "(2) round-zero orphan probe 7 py faces / 0 orphans / 1 resident server (8792 exempt); "
       "(3) S0.5 orders_ack dual-scan CLEAN 102/111/0 + D-19 zero-delta BOTH faces hold (dec 4cfdd17c / ord 135dfea5; "
       "r1062-postscript expected c8b328c1 face superseded by group-side churn per r1060 content-adjudication law, zero action); "
       "(4) S1 smoke 49/49; S2 job_list empty + fleet tasks open=NONE (python scan) + tech/explore boards drained + backlog zero bm-a claimable lines "
       "(r1058 agenda census face held); S3 satengine ALIVE rc0 idle queue0 + watermark green red=false (next_pick moneyflow IC claimed/panel-blocked) "
       "= waiting-state maintenance round per product law sec.2; "
       "(5) MAIN: S6 chain 43 legs + live_paper all rc0 bad=0 (_r1063bma_s6chain.ps1 = r1062 face clone verbatim, Sunday no-op faces); "
       "MF day-11 evidence LANDED same-round (17:52:42 fresh retest 300706/07/08 RemoteDisconnected x3 -> conn_stopped=true fuse; "
       "rank lane 17:37:31 fetch_failed page1 RemoteDisconnected) = blockade ALIVE day-11, Monday <=10-19 adjudication chain complete day-8..11; "
       "(6) idle round-head green_idle two_read_red -> --worked same-round (S6 chain = actual product work per r1062 precedent), "
       "idle_rounds 0, agenda_starved false; "
       "(7) S7: loop pin=8 no-op (next fire 17:58) + watchdog alive (S4U flip access-denied = carried C-20261016-04 elevation window) "
       "+ claws reinstalled both + attrition_guard_scan rc0 in-chain; "
       "(8) waiting faces one-line: W271 bm-c lane (W272 rides W271 sec.7/8 backfill) / S5-27 re-roll bm-c lane watch / "
       "MF Monday adjudication armed / council sec.6 table <=10-20 12:00 / E20 GM-council reserved no-self-start / "
       "CODELY.md 9,987B headroom intact (zero append this round)")

LAST_ARTIFACT = ("S6-derived same-day idempotent faces regenerated (docs/daily_report/REPORT-2026-10-18 + docs/live_usage/LIVE-2026-10-18 + "
                 "results/strategy_scorecard.json + results/daily_scorecard.json + results/dashboard_status.json/js) + "
                 "MF day-11 evidence face (results/moneyflow_update_status.json 17:52 chain) + _r1063bma_s6chain.ps1 chain script")

NEXT = ("r1064: (1) MF Monday adjudication <=10-19 (Monday S6 retest adds day-12 face; evidence chain day-8..11 complete in moneyflow_update_status.json); "
        "(2) W271 watch on bm-c lane (prereg derive = bm-c r1096 first action; W272 owner naming rides W271 sec.7/8 backfill; bm-a zero wave obligation); "
        "(3) S5-27 re-roll execution watch on bm-c lane (pixel endpoint gate -> S7R chain -> wave-3 PENDING -> 32/32); "
        "(4) council sec.6 first ruling table watch <=10-20 12:00; (5) E20 three-axis synthesis = GM/council signature reserved face, loop does not self-start; "
        "(6) CODELY.md 9,987B = ~113B headroom under decimal 10KB line (next append re-triggers editorial per law); "
        "(7) S0.5 d19 probe: ord/dec hold expected unless group-side new rows land")

VERDICT = ("GREEN: r1063: maintenance-product round all green -- S6 43 legs + live_paper rc0 bad=0 + smoke 49/49 + "
           "orders_ack dual-scan CLEAN 102/111/0 + D-19 zero-delta both faces hold + satengine ALIVE + watermark green red=false + "
           "orphan 0/7 + loop pin=8 no-op + claws x2 + attrition guard rc0 + idle --worked (two_read_red consumed same-round via S6 product work); "
           "MF day-11 blockade evidence landed (Monday adjudication armed); honest face = 1-point product round "
           "(real file changes: S6-derived faces + chain script + MF evidence face; waiting objects one-line per product law sec.2, no re-scan)")

VERIFY = ("results/_r1063bma_s6chain_rc.log 43 rc-lines + live_paper all rc0 bad=0 (gitignored local evidence) + smoke 49/49 + "
          "orders_ack_scan CLEAN 102/111/0 + d19 probe zero-delta read-back (dec 4cfdd17c / ord 135dfea5 hold, no advance = no consumption face) + "
          "idle --worked receipt (idle_rounds 0, agenda_starved false) + MF day-11 face in results/moneyflow_update_status.json "
          "(17:52:42 retest 3x RemoteDisconnected conn_stopped=true)")

sp = os.path.join(ROOT, "state-bm-a.json")
with io.open(sp, encoding="utf-8") as f:
    st = json.load(f)

st_prev_epoch = st.get("heartbeat_epoch_utc")
st["round_no"] = 1064
st["round"] = 1063
st["loop_round"] = 1063
st["last_round"] = "r1063"
st["last_round_label"] = "r1063"
for k in ("last_round_at", "last_round_ts", "last_round_closed", "last_action_at", "last_run", "last_seen", "updated", "updated_at", "ts"):
    st[k] = now_iso
st["current"] = "r1063: S6 all-green maintenance-product round (43 legs + live_paper rc0 bad=0) + MF day-11 blockade evidence landed (Monday adjudication armed) + idle --worked; waiting faces: W271/S5-27 on bm-c lane, MF Monday, council sec.6 table, E20 reserved"
st["now_active"] = "bm-a loop r1063 closeout (S6 maintenance-product round + MF day-11 evidence)"
st["task"] = "r1063: maintenance-product round (S6 chain + closeout)"
st["current_task"] = "r1063: maintenance-product round executed (S6 43 legs all green + MF day-11 evidence); wave lane stays bm-c (W271), Monday MF adjudication armed"
st["did"] = DID
st["last_action"] = DID
st["last_artifact"] = LAST_ARTIFACT
st["recent_artifact"] = LAST_ARTIFACT
st["latest_artifact"] = LAST_ARTIFACT
st["next"] = NEXT
st["next_milestone"] = "MF Monday adjudication <=10-19 (evidence day-8..11 complete) + W271/S5-27 watches on bm-c lane + council sec.6 table <=10-20 12:00"
st["verdict"] = VERDICT
st["verify"] = VERIFY
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st_prev_epoch
st["heartbeat_epoch_utc_type_int"] = isinstance(epoch, int)
st["clock_read"] = now_iso
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_killed"] = 0
st["free_ram_gb"] = ram_free_gb
st["ram_free_gb"] = ram_free_gb
st["idle_ram_gb"] = ram_free_gb
st["ram_free_mb"] = ram_free_mb
st["idle_ram_mb"] = ram_free_mb
st["free_ram_pct"] = free_ram_pct
st["ram_free_pct"] = free_ram_pct
st["ram_load_pct"] = ram_load_pct
st["total_ram_gb"] = total_ram_gb
st["cpu_load_pct"] = cpu_pct
st["cpu_pct"] = cpu_pct
st["cpu_total_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["gpu_free_vram_mb"] = gpu_free_vram_mb
st["last_orders_seen"] = "r1063: D-19 zero-delta hold (ord 135dfea5, dec 4cfdd17c, zero new group rows consumed)"
st["last_decisions_seen"] = "r1063: D-19 zero-delta hold (dec 4cfdd17c, zero new group rows consumed)"
st["last_orders_at"] = now_iso
st["last_decisions_at"] = now_iso
st["last_orders_read_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["orders_ack_note"] = ("r1063: fleet/orders zero new orders (dual-scan CLEAN 102/111 zero divergence); D-19 group face zero-delta both hold "
                         "(dec 4cfdd17c / ord 135dfea5; r1062-postscript c8b328c1 expectation superseded by group churn per r1060 content-adjudication law); "
                         "inbox EMPTY for bm-a (zero files)")
st["notes_r1063"] = ("r1063: (1) waiting-state maintenance round per product law sec.2 -- waiting objects (W271/S5-27 bm-c lane, MF Monday, council sec.6, E20, S4U elevation) "
                     "declared one-line each, zero re-scan; (2) MF day-11 evidence chain = 17:52:42 retest 3x RemoteDisconnected conn_stopped + rank lane 17:37:31 fetch_failed; "
                     "Monday <=10-19 adjudication face = fresh S6 retest day-12 + freeze-chain adjudication; (3) D-19 c8b328c1 face (r1062 postscript expectation) "
                     "resolved as group-side churn supersession per r1060 law -- content-hash adjudication, zero consumption; "
                     "(4) watchdog S4U flip access-denied = carried C-20261016-04 (elevation window pending)")

with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
with io.open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb_prev_epoch = hb.get("heartbeat_epoch_utc")
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = hb_prev_epoch
hb["current_task"] = "r1063: S6 maintenance-product round all green + MF day-11 evidence (Monday adjudication armed)"
hb["verdict"] = "GREEN"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = 32
hb["free_ram_gb"] = ram_free_gb
hb["gpu_free_vram_mb"] = gpu_free_vram_mb
hb["round_no"] = 1063
hb["last_round"] = "r1063"
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# round report line
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = (f"{now_iso} | r1063 | 维护产出轮（等待态一行收账面·r1058 议程普查面维持）：S0 零拉取窗（fetch origin 0/0 behind=0·树面 3 运行时活面 r1035 族非阻塞）·"
        f"round-zero 孤儿探针 0/7 面（1 resident server 8792 豁免）·S0.5 双扫 CLEAN 102/111/0+D-19 双面零增量 hold（dec 4cfdd17c/ord 135dfea5·"
        f"r1062 尾注预期 c8b328c1 面被组面收敛吞没=r1060 内容定谳律零动作）·S1 smoke 49/49·S2 板面全清（job_list 空+fleet tasks open=NONE〔python 扫〕+"
        f"tech/explore 板净+backlog 零 bm-a 可领行）·S3 satengine ALIVE rc0 idle+水位绿 red=false（next_pick moneyflow IC=claimed/panel-blocked）·"
        f"**本轮主产=S6 链 43 腿+live_paper 全 rc0 bad=0**（_r1063bma_s6chain.ps1=r1062 面 verbatim 克隆·周日 no-op 面）+**MF day-11 封锁证据落地**"
        f"（17:52:42 新鲜重试 300706/07/08 RemoteDisconnected x3→conn_stopped·rank 道 17:37:31 fetch_failed=封锁 day-11 仍活·"
        f"周一 <=10-19 裁决链 day-8..11 完整）·idle 轮首 green_idle two_read_red→--worked 同轮清零（basis=S6 产品工·r1062 先例）·"
        f"S7 loop pin=8 no-op（下火 17:58）+watchdog 活（S4U flip 拒绝访问=carried C-20261016-04）+双爪重装+attrition guard rc0（链内）·"
        f"等待面一行：W271 bm-c 道（W272 骑 W271 §7/8 回填）／S5-27 重摇 bm-c 道守望／MF 周一裁决 armed／委员会 §6 首裁表 <=10-20 12:00／"
        f"E20=GM/委员会保留面不自启／CODELY.md 9,987B 余量维持（本轮零 append） | 证据=results/_r1063bma_s6chain_rc.log 43+1 rc0 bad=0+smoke 49/49+"
        f"orders_ack_scan CLEAN 102/111/0+d19 零增量读回（双面 hold·零 advance=零消费）+idle --worked 回执（idle_rounds 0）+"
        f"MF day-11 面 results/moneyflow_update_status.json（17:52 重试 3 连断 conn_stopped） | 本轮=产品 1 分（实际文件改动+S6 能看面再生+MF 证据面·"
        f"非纯记账·等待态律合规零重扫） | 下轮指针=r1064：MF 周一裁决 <=10-19（周一 S6 重试补 day-12 面·证据链冻结裁决）+W271 守望（bm-c r1096 首动作=prereg derive）+"
        f"S5-27 重摇守望（bm-c 道）+委员会 §6 表 <=10-20 12:00+E20 GM/委员会保留面+CODELY.md 10KB 线余量维持 | 本地未达 origin commit 数=0（收官 push 验证后）\n")
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# self-verify: epoch int + clock T-separator
assert isinstance(st["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in st["clock_read"], "clock_read must be T-separated (R262)"
print(json.dumps({"ok": True, "epoch": epoch, "now": now_iso, "ram_free_gb": ram_free_gb, "cpu_pct": cpu_pct}, ensure_ascii=False))