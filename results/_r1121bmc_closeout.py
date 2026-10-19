# -*- coding: utf-8 -*-
# r1121 bm-c closeout: heartbeat + state faces + round-report row. (fleet README S5/S7 law)
import io, json, time, subprocess, datetime, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")          # T-separated with offset
epoch = int(time.time())

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout or "").strip()

ram_free = 0.0
try:
    import psutil
    ram_free = round(psutil.virtual_memory().available / 1024 ** 3, 2)
except Exception:
    pass
try:
    nv = sh(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"])
    parts = [x.strip() for x in nv.split(",")]
    gpu_face = "nvidia-smi %s%%·%s MiB used / %s MiB" % (parts[0], parts[1], parts[2])
except Exception:
    gpu_face = "nvidia-smi unreadable"
cpu_pct = 0.0
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=1)
except Exception:
    pass

DID = ("r1121-continuation (absorb of dead r1121 S0.5 window): (1) NATS 机队总线 @bm-c 派单三步全 PASS "
       "[bootstrap 钉版 v2.15.1/v0.5.0 — github 直连挂死愈合 via gh-proxy 镜像律+幂等复验 NATS-BIN OK; "
       "register FluxGroup-NatsHB every:1m NodeId=bm-c 隐藏链 S4U 拒=裁决面候提权; deploy=ignite fire OK 16:48:58 result=0; "
       "BUS OK role=node; netdiag 全文; KV state.bm-c rev71; fleet-live-status 三机行全绿 (bm-a 19s/bm-b 10s/bm-c 29s·bm-d 在装预期缺失); "
       "回执 MSG-1653-bmc-natsbus.md CAS 上链组树 e0409120 + 坑律两条 (node 须 -Server 指中枢/bootstrap 无超时挂死)]; "
       "(2) S0.5 ORD 12 行判收 (死窗 5: 角色生命线/冲刺总动员/商业化模拟态/全司推广/BigLife census + 本窗 5: 模式扫描/外部审查定谳/"
       "MV 教学令/导演全量学习/艺术MV令 + 尾扫 2: 质量灵魂律/MV 调研收口 — 全部零 bm-c 机械义务·外部审查行 BM repo-slim=REPO-SLIM leg-7 在册已认领 "
       "·意义门四闸在册强化) 水位两段推进 ac5501f1->d85679de->9769861f 双面同步·DEC 95879dd9 hold; "
       "(3) 16:26 每日产出汇报令 BigMoney 行提前落 (DAILY-OUTPUT-REPORT.md CAS 50babcd — 对外 0 件如实+NATS 节点+W278 周期闭环+PREP 锚件); "
       "(4) W279 PREP 增量: T0 针脚楼层实测收据 results/_w279bmc_needle_floors.json (10:3x=5/09:5x=2/下波面全零/n1_w278=4/W279p_=2/629_101=3/freezer x1); "
       "(5) S6 light 10/10 rc0 (update_daily 0 rows cutoff 10-16 honest sina-lag~20:4x·dualrun streak 51·token delta=258·fund_premium no-op·REPORT-2026-10-19 faces=5); "
       "(6) smoke 49/49 + attrition 4 CLEAN + quad green (loop pin=5 no-op·watchdog S4U=裁决面·claws x2) + orphan 0")

VERDICT = ("green r1121 CEO-ticket window: NATS 总线 bm-c 节点上线在役 (三机行全绿·KV rev71·回执上链 e0409120) + "
           "W279 prereg derive 顺延 r1122 FIRST ACTION per r1096 honest-split (CEO 派单优先序合法占用窗口·锚件全机冻: "
           "prep facts + T0 99001d3d + needle floors)")

NEXT = ("r1122 FIRST ACTIONS: (1) W279 prereg derive = P0 first action: builder one-generation roll "
        "_r1116bmc_build_w278_derive.py -> _r1122bmc_build_w279_derive.py (E63 canon law; ALL span OLD sides "
        "verified line-level against results/_w278bmc_prereg_derive.py ACTUAL text per r1116 heal(i) law; "
        "anchors = prep facts machine-frozen results/_w279bmc_prep_facts.json + T0 needle floors "
        "results/_w279bmc_needle_floors.json [10:3x=5/09:5x=2 正楼层·W278 周期戳 13:5x/15:1x/15:0x 零楼层·freezer "
        "unlag W279->W280·W280p 投影 631_101..633_100/631_301..631_500·席位收据 bands A 629101..631100 / B 631101..631300 "
        "leg0 rows=276 owner=268 bmc=97 ordinal=269·fin anchors ledger 1,035,935/K 609,520/K-lift -0.0002·seed FREE x2]; "
        "stamp roll 10:3x->15:1x (W278 finalize 0a92fcc28f 15:13:26)·engine stamps r1116->r1122·r1113->r1116 era) -> "
        "derive _w279bmc_prereg_derive.py -> research/PERPETUAL_N1_W279_PREREG.md ALL GATES PASS -> banned ADMIT -> "
        "freeze commit + push; (2) 10-19 bar sina-lag ~20:4x -> papers chain full re-arm; (3) NATS 心跳任务常设在役 "
        "(FluxGroup-NatsHB every:1m·S4U 候提权转换); (4) next 5x HANDOVER duty = bm-c r1125; (5) 明日 22:0x DAILY-OUTPUT-REPORT 行滚动")

# ---- heartbeat ----
hb_path = ROOT + r"\fleet\machines\bm-c.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb.update({
    "last_seen": iso, "last_seen_at": iso, "ts": iso, "updated": iso, "updated_at": iso, "now_active": iso,
    "clock_read": iso, "heartbeat_epoch_utc": epoch,
    "ram_free_gb": ram_free, "idle_ram_gb": ram_free, "free_ram_gb": ram_free,
    "cpu_util_pct": cpu_pct, "cpu_pct": cpu_pct,
    "gpu_face": gpu_face,
    "current_task": "r1122 FIRST ACTION = W279 prereg derive (builder one-gen roll, anchors all frozen); NATS bus heartbeat standing",
    "current_task_at": iso, "current_task_ts": epoch,
    "did": DID, "verdict": VERDICT,
    "idle_rounds": 0, "agenda_starved": False,
    "last_action": "r1121-continuation closeout (NATS bus node live + ORD 12-row consumed + BigMoney daily-report row landed + W279 PREP needle-floors increment)",
    "last_action_at": iso,
    "last_artifact": ("cph4/fleet/inbox/MSG-1653-bmc-natsbus.md (group e0409120) + results/_r1121bmc_netdiag.txt + "
                      "results/_w279bmc_needle_floors.json + DAILY-OUTPUT-REPORT.md BigMoney row (group 50babcd)"),
    "last_artifact_at": iso, "recent_artifact": hb["last_artifact"],
    "prod_lanes": "CPU=W279 prereg derive next-window P0 (PREP complete); GPU=idle day; NATS bus node live (every:1m standing)",
    "ram_critical_face": "none (loop CPU-only, GPU idle day)",
})
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ck = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(ck["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in ck["clock_read"], "clock_read not T-separated"
print("heartbeat written; epoch int OK; clock T OK; ram_free=%.2f cpu=%.1f" % (ram_free, cpu_pct))
print("gpu:", gpu_face)

# ---- state ----
st_path = ROOT + r"\state-bm-c.json"
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 1122
st["round_no_label"] = "r1121-continuation closeout -> counter 1122"
st["last_round"] = "r1121"
st["last_round_at"] = iso
st["last_round_closed"] = iso
st["last_round_closed_at"] = iso
st["last_round_summary"] = ("green r1121-continuation: NATS 机队总线 bm-c 节点上线在役 (@bm-c 派单三步全 PASS·回执 MSG-1653 "
                            "组树 e0409120·KV rev71·三机行全绿) + ORD 12 行两段判收全零 bm-c 义务 (水位 9769861f 双面) + "
                            "BigMoney 日报行落 (50babcd) + W279 PREP 针脚楼层收据机冻 (derive=r1122 first action per "
                            "honest-split) + S6 10/10 + smoke 49/49 + attrition CLEAN + quad green")
st["last_round_summary_at"] = iso
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "W279 prereg derive (r1122 first action) -> freeze push -> splice editor chain; NATS bus standing"
st["activity_now"] = iso
st["now_active"] = iso
st["last_action"] = "r1121-continuation closeout"
st["last_action_at"] = iso
st["last_artifact"] = hb["last_artifact"]
st["latest_artifact"] = hb["last_artifact"]
st["last_artifact_at"] = iso
st["current_task"] = hb["current_task"]
st["current_task_at"] = iso
st["head_sha"] = "r1121 closeout (rides this window's commit)"
st["full_load_selfproof"] = {
    "占用一行": "CPU=W279 derive r1122 first action (PREP all frozen); GPU=idle day; NATS 心跳任务常设在役 (FluxGroup-NatsHB every:1m)",
    "最近实物": "cph4/fleet/inbox/MSG-1653-bmc-natsbus.md @ 组树 e0409120 (NATS 总线 bm-c 节点回执·三机行全绿) + results/_w279bmc_needle_floors.json (T0 针脚楼层实测) + DAILY-OUTPUT-REPORT.md BigMoney 行 @ 50babcd @ " + iso,
    "下个里程碑": "W279 prereg derive 冻结上链 = r1122 首动作 (窗 ≤30min); 10-19 bar ~20:4x papers chain re-arm; 明晚 22:0x 日报行滚动",
}
st["ram_free_gb"] = ram_free
st["sync"] = {"origin_tip": "r1121 closeout commit (rides this window)", "ts": iso}
st["r1121_closeout_note"] = ("r1121-continuation: (1) absorb of dead r1121 S0.5 window (ORD 5-row judgment + watermark "
    "ac5501f1, machine-verified before landing); (2) S0 fetch behind=2 bm-b r1026 chain absorbed via rebase-at-commit; "
    "(3) CEO-ticket NATS bus @bm-c dispatch executed same-round (three steps + receipt MSG-1653 CAS-landed group "
    "e0409120 + KV heartbeat rev71 + 3-machine live-status green + 2 pit rows [node needs -Server / bootstrap no-timeout]); "
    "(4) ORD 12 rows consumed in three probes (all zero bm-c obligation; watermark ac5501f1->d85679de->9769861f two-face "
    "advance read-back verified, DEC 95879dd9 hold); (5) 16:26 daily-report law BigMoney row landed early (CAS 50babcd); "
    "(6) W279 prereg derive DEFERRED to r1122 FIRST ACTION per r1096 honest-split law (CEO-ticket priority consumption "
    "of the window; anchors all machine-frozen: prep facts + T0 99001d3d3f337942 CR-norm-eq-verified + needle floors "
    "measured this window); (7) S6 light 10/10 rc0 (bars 10-19 sina-lag ~20:4x honest 0 rows cutoff 10-16); (8) smoke 49/49 "
    "+ attrition 4 CLEAN + quad green; counter 1121->1122")
json.dump(st, open(st_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written; round_no=1122")

# ---- round report row ----
rr_path = ROOT + r"\round_reports-bm-c.md"
row = ("%s | r1121-continuation | NATS 机队总线 @bm-c 派单三步全 PASS (bootstrap 钉版 gh-proxy 愈合+deploy-ignite "
       "16:48:58+BUS OK+KV rev71+netdiag 全文+回执 MSG-1653 组树 e0409120) + ORD 12 行两段判收全零义务 (水位 "
       "9769861f 双面·DEC hold) + BigMoney 日报行落 (50babcd·16:26 令提前执行) + W279 PREP 增量 T0 针脚楼层实测 "
       "(_w279bmc_needle_floors.json) + W279 derive 顺延 r1122 首动作 (honest-split·CEO 票合法占窗) | smoke 49/49 + "
       "S6 10/10 rc0 + attrition 4 CLEAN + quad green + d19 双面推进回读等 + CAS 两推 ls-remote 自证 (e0409120/50babcd) "
       "+ KV rev71 三机行全绿 | r1122 FIRST ACTION = W279 prereg derive (builder 一代滚动·锚件全机冻) -> 冻结上链 -> "
       "splice editor chain; papers chain 等 10-19 bar (~20:4x); NATS 心跳常设在役\n") % iso
with open(rr_path, "a", encoding="utf-8") as f:
    f.write(row)
print("round report row appended")
