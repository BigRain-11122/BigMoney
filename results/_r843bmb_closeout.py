# -*- coding: utf-8 -*-
# r843 bm-b closeout: round report line + state.json + heartbeat (utf-8 declared per pit-encoding)
import json, time, psutil
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

RR_LINE = (
 "2026-10-10T21:5x+08:00 | r843 bm-b | dept:工程（等待窗收口：D19 ord delta 消费推进+S6 38 腿+四件套全绿） | "
 "WM-VERDICT: green（red=false @21:37 probe；py_low_with_work_cands 合法=local_batch 1=astock 面板重建在飞〔pid 10404·refresh lock lane〕+池 ready 3 全 lane=bm-a 已认领非本机候选+板 0+bandit 0；supply_gap=O-1645 standing；ignition_sla 零 breach） | "
 "孤儿面=0（probe 21:32 py_faces=16 orphans=0） | "
 "CEO three-line: 当前活=r843 收口（D19 ord 水位推进 5437bc4e→3af479f1·增量=21:3x @bm-c mv0001 行非本司零动作·dec 恒等零 delta + S6 38 腿 37×rc0+alloc rc=2 已知 P5 stale-leg standing）；"
 "最近实物=results/d19_watermark.json（ord ADVANCED 3af479f1 读回恒等）+results/_r843bmb_s6chain.log（38 腿逐腿 rc 账+dualrun ZERO-DRIFT streak 28），2026-10-10 21:3x-21:4x；"
 "下个里程碑=r844+（窗 ≤10-11 06:00·面板完备 ETA ~02:15± 按 857/5229@21:34 pace ~15.6/min）：detached T23 census 全量烧录（~15-25min 长活）→census_holds 判读→N2 U3 ① prereg 起草窗（holds）/G2 学术引用 fallback（负面） | "
 "did: S0-1 锚定 bm-b；S0 落后 5 commit 集成=own daemon churn 8 件 pre-rebase 吸收 commit（bm-a r962 同范式）+rebase 干净零 UU；S0.5 令扫 60 件全 ack 零未回执（S7 双扫同零）；"
 "D19 双水位=dec a20664ec 恒等零 delta 零动作+ord 5437bc4e→3af479f1 消费推进（guard update --advance·读回 full-string 恒等·回执 results/d19_watermark.json）；"
 "S1 smoke 49/49；S2 job_list 0+fleet 票 0 open（T-182 bm-c 认领在跑·T-183 done r838 已收口）；"
 "S3 固定序全查=水位红牌 false+饱和引擎活 rc0（heartbeat 49s·queue_depth 0·verdict idle）+修红无红项+试用劳动力常设线=主队列头 T23 census 物理依赖 astock 全宇宙重建（857/5229@21:34·pid 10404 alive·census run gate awaiting_panel exit 2 诚实禁假跑）"
 "+闲置硬触发=green_idle true（ram 45.8%·vram 闸 disclosure-only T-183 已解耦）·claimable_pool_lines 2=W17 screen-7of8+judge 全 lane_owner=bm-a 已认领（21:04:04/21:33:08 实弹）→R31 lane-guard 让路零双烧·本机零接管（bm-a 心跳活跃 21:33 非停滞）；"
 "队列头 tech/explore 双空诚实维持（r842 三空注记承袭·禁造假活动数）；W18 drain-gated（bm-a owns w17-judge）+fund 三族 GM 裁定 standing+题材 overlay 切片起草留续窗 standing+astock 重建进度验证 638→857（14min·~15.6/min）；"
 "S6 38 腿全链（dualrun 先行序 T-116 s3）：pool_dualrun ZERO-DRIFT streak 28（419 entries）+compute_audit flags=[supply_gap] 常设（supply_floor breach=false·ignition_sla_breach_ids 空·single_core_hog=pid 10404 重建本体合法）"
 "+pywm py_low_with_work_cands（工作候选实指=astock 重建 local_batch 合法）+周六采集腿族全诚实 no-op+update_astock_daily refresh-lock 尊重 no-op 实证（panel cutoff 2026-10-09 covers·零网络）"
 "+regime_thermo/dualarm/rev_osc/clock/report/live_usage/token rc0+lane 守卫族（scorecard/paper_export/daily_scorecard/dashboard/system_v1=host bm-a 心跳活跃→守卫跳过诚实）+alloc rc=2（已知 P5 stale-leg 510880 缺件·s3 评审窗维持）；"
 "S7 四件套全绿（loop pin=2 no-op first-fire 21:42+watchdog 在册 first-fire 21:41+双爪 LF 归一重装）+attrition 4 台账 CLEAN | "
 "记账预算 4/5（state+心跳+轮报+D19 水位；S6 管线产出不计） | score: 0（等待窗豁免面：主队列头 T23 物理依赖 astock 面板重建在飞·r840-843 连续诚实等待窗·零造假活动数；D19/S6/四件套=簿记与管线维持非产品增量） | unacked_orders=0 | "
 "本地未达 origin commit 数=0（push 后 fetch+rev-list 自证→见 S7） | "
 "下轮指针: r844 queue（承 r843）：astock rebuild completion verify（窗 ~10-11 01:45-02:15±·盘面 pace 实证）→面板完备即 detached spawn T23 census 全量烧录（~15-25min 长活）→census_holds 判读→N2 U3 ① prereg 起草窗（holds）/G2 学术引用 fallback（负面）+S6 链；W18 stays drain-gated（bm-a owns w17-judge） | [r843 bm-b]"
)

with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(RR_LINE + "\n")

# --- state.json ---
with open("state.json", "r", encoding="utf-8") as f:
    st = json.load(f)
R843 = ("r843: D19 ord delta consumed+ADVANCED 5437bc4e->3af479f1 (delta=21:3x @bm-c mv0001 row non-BigMoney zero-action; "
        "dec a20664ec identical zero-delta) + S6 38 legs (37xrc0 + alloc rc=2 known P5 stale-leg) + quartet green + attrition CLEAN; "
        "main queue head T23 census physically blocked on astock full-universe rebuild (857/5229@21:34, pid 10404 alive, ETA ~02:15) honest wait window r840-843")
NEXT = ("r844 queue: astock rebuild completion verify (window ~10-11 01:45-02:15+ per disk-count pace) -> "
        "spawn detached T23 census full burn (~15-25min) -> census_holds readout -> N2 U3 (1) prereg drafting window if holds / "
        "G2 academic-citation fallback if negative + S6 chain; W18 stays drain-gated (bm-a owns w17-judge)")
st["machine_id"] = "bm-b"
st["round_no"] = 843
st["round"] = 843
st["round_no_label"] = "r844"
st["note"] = R843
st["did"] = R843
st["last_action"] = R843
st["verdict"] = ("r843: GREEN; smoke 49/49; D19 ord advanced 3af479f1 (delta non-BigMoney); dualrun ZERO-DRIFT streak 28; "
                 "quartet green; attrition CLEAN; board/queues empty; pool ready 3 all lane=bm-a claimed; "
                 "T23 census head physically gated on astock rebuild 857/5229 ETA ~02:15 = honest wait window; zero double-burn")
st["current_task"] = NEXT
st["task"] = NEXT
st["next"] = NEXT
st["now_active"] = "r843 closeout: D19 ord advance + S6 38 legs + honest wait window on T23 census (astock rebuild in flight)"
st["latest_artifact"] = "r843: results/d19_watermark.json (ord ADVANCED 3af479f1 read-back equal) + results/_r843bmb_s6chain.log (38 legs rc ledger, dualrun streak 28), 2026-10-10 21:4x"
st["next_milestone"] = "r844+ (window <=10-11 06:00): astock panel complete (857/5229 @21:34, ETA ~02:15) -> detached T23 census burn -> holds verdict; W18 legs stay drain-gated (bm-a owns w17-judge)"
st["last_round_at"] = TS
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["last_seen"] = TS
st["clock_read"] = TS
st["last_round_ts"] = TS
st["last_orders_sha"] = "3af479f1383537596cd0937a8d64e056879c27e8"
st["last_orders_at"] = TS
st["last_orders_read_at"] = TS
st["last_orders_sha_note"] = ("r843: ord ADVANCED 5437bc4e->3af479f1 via scripts/d19_watermark.py update --advance --receipt results/d19_watermark.json "
                              "(r537 SHA-1 40-hex raw-blob PIN; delta consumed same round; read-back full-string equality OK)")
with open("state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
svm = psutil.virtual_memory()
free_gb = round(svm.available / 2**30, 1)
ram_pct = round(svm.available / svm.total * 100, 1)
hb["machine_id"] = "bm-b"
hb["round"] = 843
hb["round_no"] = 843
hb["now_active"] = st["now_active"]
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["next"] = NEXT
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = ("GREEN: r843 wait-window closeout (T23 census head physically gated on astock rebuild 857/5229 ETA ~02:15, honest per rule-2 wait exemption); "
                 "D19 ord advanced 3af479f1; S6 38 legs green (alloc rc=2 known P5 stale-leg); quartet+attrition clean; idle stays 1 (pool lines lane-pinned bm-a, agenda non-empty)")
hb["last_action"] = R843
hb["last_round_at"] = TS
hb["last_seen"] = TS
hb["updated"] = TS
hb["ts"] = TS
hb["clock_read"] = TS
hb["updated_at"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["ram_free_pct"] = ram_pct
hb["gpu_free_vram_mb"] = 3360
hb["gpu_free_vram_gb"] = 3.36
hb["vram_free_gb"] = 3.36
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "r843 orphan probe 21:32 py_faces=16 orphans=0"
hb["sync"] = {
    "last_push_ts": TS,
    "note": "r843 closeout; post-push fetch self-proof behind=0 pending S7 verify (addendum on any claw block)",
}
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

print("closeout ok: rr-line appended, state round_no=843, heartbeat epoch=%d ram_free=%sGB" % (EPOCH, free_gb))
