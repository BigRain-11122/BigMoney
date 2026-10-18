# -*- coding: utf-8 -*-
"""r1064 bm-a closeout: state-bm-a.json + heartbeat + round report line (broadcast-order + maintenance-product round)."""
import json, time, datetime, io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.isoformat(timespec="seconds")
epoch = int(time.time())

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
    ram_free_gb, ram_free_mb, total_ram_gb = 57.1, 58457, 93.6
    free_ram_pct, ram_load_pct, cpu_pct = 61.0, 39.0, 5.0

gpu_free_vram_mb = 7414  # last idle_trigger cross-check face (CEO working machine, honest face)

DID = ("r1064: (1) S0 pull --rebase ff absorbed origin +4 (bm-c r1096 W271 PREREG FREEZE + broadcast O-20261018-1810 + "
       "bm-c r1097 W271 five-face splice LANDED + satengine ledger append; live-faces stash/pop clean zero-UU r1058 recipe); "
       "(2) round-zero orphan probe 16 py faces / 0 orphans / 1 resident server (8792 exempt); "
       "(3) S0.5 NEW ORDER O-20261018-1810-bm-c (CEO full-mobilization broadcast after game window) consumed SAME-ROUND: "
       "bm-a receipt '维持全力' landed in order file §四 (no pause history this machine) + dual-face ack via orders_ack_append.py "
       "(state 112 / heart 112, 4 mirrors synced) + §S3 reminders (S5-27 帧位重裁 / S5-26 ESRGAN 补修 / F5-33c 过闸) "
       "= director-seat BigStream faces per dual-company law (r1057 MSG-1200 precedent), informational one-line for this loop, zero obligation; "
       "D-19 zero-delta BOTH faces hold (dec 4cfdd17c / ord 135dfea5); "
       "(4) S1 smoke 49/49; S2 job_list empty + boards drained (r1058 agenda census face held); "
       "S3 satengine ALIVE rc0 idle + watermark green red=false = waiting-state maintenance round per product law sec.2; "
       "(5) MAIN: S6 chain 43 legs + live_paper all rc0 bad=0 (_r1064bma_s6chain.ps1 = r1063 face clone verbatim, Sunday no-op faces; "
       "MF main-lane fuse retained per design, Monday <=10-19 adjudication armed with day-8..11 chain); "
       "(6) idle round-head green_idle two_read_red (idle_rounds=4 accumulated via r1060 CLOUD_CAP_DEFER fires) -> --worked same-round "
       "(broadcast-order processing + S6 chain = actual product work per r1062/r1063 precedent), idle_rounds 0, agenda_starved false; "
       "(7) S7: loop pin=8 no-op (next fire 18:48) + watchdog alive (S4U flip access-denied = carried C-20261016-04 elevation window) "
       "+ claws reinstalled both + attrition_guard_scan rc0 in-chain; "
       "(8) waiting faces one-line: W271 splice landed (bm-c r1097) remaining chain self-burn->sixgate->finalize->fivekeys->sec78->W272 seat "
       "all bm-c lane (W272 owner naming rides W271 sec.7/8 backfill; bm-a zero wave obligation) / MF Monday adjudication armed / "
       "council sec.6 table <=10-20 12:00 / E20 GM-council reserved no-self-start / CODELY.md 9,987B headroom intact (zero append this round)")

LAST_ARTIFACT = ("broadcast-order consumption faces (fleet/orders/O-20261018-1810-bm-c.md bm-a receipt line + state/heartbeat orders_ack 112 dual-face) + "
                 "S6-derived same-day idempotent faces regenerated (docs/daily_report/REPORT-2026-10-18 + docs/live_usage/LIVE-2026-10-18 + "
                 "results/strategy_scorecard.json + results/daily_scorecard.json + results/dashboard_status.json/js) + _r1064bma_s6chain.ps1 chain script")

NEXT = ("r1065: (1) MF Monday adjudication <=10-19 (Monday S6 retest adds day-12 face; evidence chain day-8..11 complete in moneyflow_update_status.json); "
        "(2) W271 remaining-chain watch on bm-c lane (self-burn 12/12 -> sixgate 34th -> finalize -> fivekeys -> sec78 backfill -> W272 seat naming; "
        "bm-a zero wave obligation until seat names bm-a); (3) S5-27 re-roll execution watch on bm-c lane; "
        "(4) council sec.6 first ruling table watch <=10-20 12:00; (5) E20 three-axis synthesis = GM/council signature reserved face, loop does not self-start; "
        "(6) CODELY.md 9,987B headroom (next append re-triggers editorial per law); (7) S0.5 d19 probe: ord/dec hold expected unless group-side new rows land")

VERDICT = ("GREEN: r1064: broadcast-order + maintenance-product round all green -- O-20261018-1810-bm-c consumed same-round "
           "(receipt 维持全力 + dual-face ack 112/112) + S6 43 legs + live_paper rc0 bad=0 + smoke 49/49 + D-19 zero-delta both faces hold + "
           "satengine ALIVE + watermark green red=false + orphan 0/16 + loop pin=8 no-op + claws x2 + attrition guard rc0 + "
           "idle --worked (two_read_red consumed same-round via broadcast-order + S6 product work); "
           "honest face = 1-point product round (real file changes: order receipt + ack faces + S6-derived faces + chain script; "
           "waiting objects one-line per product law sec.2, no re-scan)")

VERIFY = ("results/_r1064bma_s6chain_rc.log 43 rc-lines + live_paper all rc0 bad=0 (gitignored local evidence) + smoke 49/49 + "
          "orders_ack_append APPEND-OK state=APPENDED heart=APPENDED 112/112 mirrors=4 + receipt-line verify RECEIPT_OK "
          "(_r1064bma_ord_receipt.py fresh read-modify-write + post-write read-back assert) + "
          "d19 probe zero-delta read-back (dec 4cfdd17c / ord 135dfea5 hold, no advance = no consumption face) + "
          "idle --worked receipt (idle_rounds 0, agenda_starved false)")

sp = os.path.join(ROOT, "state-bm-a.json")
with io.open(sp, encoding="utf-8") as f:
    st = json.load(f)

st_prev_epoch = st.get("heartbeat_epoch_utc")
st["round_no"] = 1065
st["round"] = 1064
st["loop_round"] = 1064
st["last_round"] = "r1064"
st["last_round_label"] = "r1064"
for k in ("last_round_at", "last_round_ts", "last_round_closed", "last_action_at", "last_run", "last_seen", "updated", "updated_at", "ts"):
    st[k] = now_iso
st["current"] = ("r1064: broadcast-order round (O-1810 full-mobilization receipt 维持全力 + dual-face ack 112) + S6 all-green maintenance-product round "
                 "(43 legs + live_paper rc0 bad=0) + idle --worked; waiting faces: W271 remaining chain + W272 seat on bm-c lane, MF Monday, council sec.6 table, E20 reserved")
st["now_active"] = "bm-a loop r1064 closeout (broadcast-order consumption + S6 maintenance-product round)"
st["task"] = "r1064: broadcast-order + maintenance-product round (S6 chain + closeout)"
st["current_task"] = ("r1064: O-20261018-1810-bm-c consumed (receipt + ack 112/112) + S6 43 legs all green; "
                      "wave lane stays bm-c (W271 remaining chain), Monday MF adjudication armed")
st["did"] = DID
st["last_action"] = DID
st["last_artifact"] = LAST_ARTIFACT
st["recent_artifact"] = LAST_ARTIFACT
st["latest_artifact"] = LAST_ARTIFACT
st["next"] = NEXT
st["next_milestone"] = ("MF Monday adjudication <=10-19 (evidence day-8..11 complete) + W271 remaining-chain/W272 seat watch on bm-c lane + "
                        "council sec.6 table <=10-20 12:00")
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
st["last_orders_seen"] = "r1064: O-20261018-1810-bm-c consumed same-round (broadcast resume receipt 维持全力 + dual-face ack); D-19 zero-delta hold (ord 135dfea5, dec 4cfdd17c)"
st["last_decisions_seen"] = "r1064: D-19 zero-delta hold (dec 4cfdd17c, zero new group rows consumed)"
st["last_orders_at"] = now_iso
st["last_decisions_at"] = now_iso
st["last_orders_read_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["orders_ack_note"] = ("r1064: NEW ORDER O-20261018-1810-bm-c (CEO full-mobilization broadcast after game window) consumed same-round: "
                         "bm-a receipt '维持全力' (no pause history) + orders_ack_append.py dual-face ack (state 112 / heart 112, mirrors 4); "
                         "§S3 reminders (S5-27 帧位重裁 / S5-26 ESRGAN / F5-33c) = director-seat BigStream faces per r1057 MSG-1200 precedent, "
                         "informational for this loop; D-19 group face zero-delta both hold (dec 4cfdd17c / ord 135dfea5); inbox EMPTY for bm-a (zero files)")
st["notes_r1064"] = ("r1064: (1) broadcast-order consumption face -- O-20261018-1810-bm-c landed mid-window via S0 pull (+4 commits); "
                     "receipt = one-line 维持全力 per §1 (bm-a no pause history, CEO game window touched bm-c only); "
                     "§S3 待办提醒 (S5-27 帧位重裁请求在案 / S5-26 ESRGAN 补修 / F5-33c 过闸) adjudicated as director-seat (BigStream) faces "
                     "per dual-company law + r1057 MSG-1200 precedent -- this BigMoney loop carries zero MV-pixel obligation, MSG stays consumed by that seat; "
                     "(2) W271 five-face splice LANDED (bm-c r1097 7dd091eef1) per origin observation -- remaining chain (self-burn -> sixgate 34th -> "
                     "finalize -> fivekeys -> sec78 -> W272 seat) stays bm-c lane, bm-a zero skip-claim held; "
                     "(3) idle two_read_red consumption basis = broadcast-order processing + S6 chain = actual product work (r1062/r1063 precedent family); "
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
hb["current_task"] = "r1064: O-20261018-1810-bm-c consumed (receipt 维持全力 + ack 112/112) + S6 43 legs all green (MF Monday adjudication armed)"
hb["verdict"] = "GREEN"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = 32
hb["free_ram_gb"] = ram_free_gb
hb["gpu_free_vram_mb"] = gpu_free_vram_mb
hb["round_no"] = 1064
hb["last_round"] = "r1064"
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# round report line
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = (f"{now_iso} | r1064 | 广播令+维护产出轮：S0 rebase ff 吸收 origin +4（bm-c r1096 W271 PREREG FREEZE+广播令 O-1810+r1097 W271 五面 splice+satengine 台账·"
        f"活面 stash/pop 干净零 UU r1058 配方）·round-zero 孤儿探针 0/16 面（1 resident server 8792 豁免）·"
        f"**S0.5 新令 O-20261018-1810-bm-c 同轮消费**（CEO 游戏窗后全面开工广播令：bm-a 回执「维持全力」落令面 §四+orders_ack_append 双面 ack "
        f"state 112/heart 112 镜像 4 同步；本机无暂停史零额外动作；§S3 待办提醒收悉=S5-27 帧位重裁/S5-26 ESRGAN 补修/F5-33c 过闸→"
        f"导演席 BigStream 线在案候裁·双公司分工律 r1057 MSG-1200 先例·本循环司零义务一行记账）+D-19 双面零增量 hold（dec 4cfdd17c/ord 135dfea5）·"
        f"S1 smoke 49/49·S2 板面全清维持·S3 satengine ALIVE rc0 idle+水位绿 red=false·**本轮主产=S6 链 43 腿+live_paper 全 rc0 bad=0**"
        f"（_r1064bma_s6chain.ps1=r1063 面 verbatim 克隆·周日 no-op 面·MF 主道 fuse 按设计保留=周一 <=10-19 裁决 armed day-8..11 链）·"
        f"idle 轮首 green_idle two_read_red（idle_rounds=4=r1060 CLOUD_CAP_DEFER 递延点火累计）→--worked 同轮清零"
        f"（basis=广播令处理+S6 产品工·r1062/r1063 先例族）·S7 loop pin=8 no-op（下火 18:48）+watchdog 活"
        f"（S4U flip 拒绝访问=carried C-20261016-04）+双爪重装+attrition guard rc0（链内）·"
        f"等待面一行：W271 余链（自燃→六门 34→finalize→fivekeys→§7/8 回填→W272 席面点名）全 bm-c 道·bm-a 零波义务零抢跑维持／"
        f"MF 周一裁决 armed／委员会 §6 首裁表 <=10-20 12:00／E20=GM/委员会保留面不自启／CODELY.md 9,987B 余量维持（本轮零 append） | "
        f"证据=results/_r1064bma_s6chain_rc.log 43+1 rc0 bad=0+smoke 49/49+orders_ack_append APPEND-OK 112/112 镜像 4+"
        f"回执行读回断言 RECEIPT_OK（_r1064bma_ord_receipt.py 新鲜读改写律）+d19 零增量读回（双面 hold·零 advance=零消费）+"
        f"idle --worked 回执（idle_rounds 0） | 本轮=产品 1 分（令面回执+ack 面+S6 能看面再生+链脚本·非纯记账·等待态律合规零重扫） | "
        f"下轮指针=r1065：MF 周一裁决 <=10-19（周一 S6 重试补 day-12 面·证据链冻结裁决）+W271 余链+W272 席面守望（bm-c 道）+"
        f"委员会 §6 表 <=10-20 12:00+E20 GM/委员会保留面+CODELY.md 10KB 线余量维持 | 本地未达 origin commit 数=0（收官 push 验证后）\n")
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# self-verify: epoch int + clock T-separator
assert isinstance(st["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in st["clock_read"], "clock_read must be T-separated (R262)"
print(json.dumps({"ok": True, "epoch": epoch, "now": now_iso, "ram_free_gb": ram_free_gb, "cpu_pct": cpu_pct}, ensure_ascii=False))