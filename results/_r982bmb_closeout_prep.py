# r982 closeout prep: state + heartbeat + round report row (pre-surgery facts only)
import json, time, datetime, ctypes, subprocess

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# RAM free (ctypes stdlib)
class MSTAT(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
ms = MSTAT(); ms.dwLength = ctypes.sizeof(MSTAT)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
RAM_FREE_GB = round(ms.ullAvailPhys / 1024**3, 1)
try:
    VRAM_FREE_MB = int(float(subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                                             capture_output=True, timeout=25).stdout.decode().strip().splitlines()[0]))
except Exception:
    VRAM_FREE_MB = -1
print("RAM_FREE_GB=%s VRAM_FREE_MB=%s" % (RAM_FREE_GB, VRAM_FREE_MB))

# ---------- state.json ----------
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 982
st["round"] = 982
st["round_no_label"] = "r982"
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_action"] = "r982: i2v 53/53 COMPLETE + valve-out (XQ05 467s clean-context fix) + D-19 orders delta consumed + S6 39 legs green"
st["last_action_at"] = NOW
st["current_task"] = "r982: i2v completion verdict + valve-out + D-19 + S6 absorb + astock watch"
st["task"] = "r982: i2v completion verdict + valve-out + D-19 + S6 absorb + astock watch"
st["current"] = "r982: 53/53 verdict + valve-out + D-19 orders delta + S7 quad + astock march"
st["now_active"] = "r982: live faces = astock backfill worker 8380 (rebuild march 3986/5219); i2v line CLOSED (GPU back to keepwarm standing, qwen3.8:4b re-pinned)"
st["did"] = ("r982: (a) C-r981 receipt consumed: c108b6b611 ancestor of origin/main rc=0 (origin +2 = bm-a r1017 W246 freeze/GENERATOR faces, zero bm-b dispatch; fleet/orders+inbox sets unchanged) "
             "(b) D-19 dual-sha probe: decisions full sha256 UNCHANGED (ab3f0cc9f4cb9bbb...e0ba8fd identical to r980/r981); orders GENUINE DELTA sha1 3b1ca198bdd9...->1835852be5b3cfd23672d10660b47dafc3d921e4 "
             "= 1 new row (10-15 15:3x Qwen switchover v3 wrap-up, bm-a execution report of CEO approval; canon cph4/fleet/qwen38-rollout-20261015.md line 27 for bm-b = 'B-line 4b derived CPU-only in-place + llm_assist routed' = ALREADY COMPLIANT, zero bm-b action); watermarks updated dec ab3f0cc9 / ord 1835852b "
             "(c) S0.5 scan zero-new orders/zero-new inbound MSGs (origin fleet faces identical to r981 ack set) "
             "(d) PREDECESSOR-ABSORB: r982 first session (15:2x-15:47, watchdog-killed pre-closeout) work absorbed: XQ05 sole-item reignition 15:34 (runner 24696) OOM-errored at 184s (15:38, oomtrace x2) -> root-caused 5.5h server allocator fragmentation (60 renders, idle 3951/8192MiB held) -> clean CUDA restart 15:47 (server 16772 + runner 12988, timeout 4200->10800) "
             "(e) i2v 53/53 COMPLETION VERDICT + VALVE-OUT (round main product): XQ_XQ05 SAVED 15:55:24 (467s, 2,993,855B) on clean context - kin evidence KN28 1757s / XQ26 318s; ALBUM LANE DONE lane=bmb ok=53 fail=0; clips-animatic-480 53/53 mp4 all >=182,492B; valve-out executed: ComfyUI server tree-killed, keepwarm.pause REMOVED, MinigameOllamaServe re-triggered, qwen3.8:4b re-pinned resident (vram=3711319408, serve up) = pre-batch standing state restored per r916 law; completion receipt MSG-20261015-1608 written to fleet/inbox (rides this push, delivery law r959/r974) "
             "(f) S6 39 legs ALL GREEN (predecessor 15:36-15:41 chain absorbed, log _r982bmb_s6chain.log): pool_dualrun ZERO-DRIFT streak 37; compute_audit FLAG ignition_sla (TRIAL-LABOR-W20-SCREEN-SHARD-0..3 = bm-c RAM-park family, cross-machine honest flag, zero bm-b ignitable face); py_watermark insufficient_history (window n=1); update_daily 0 new rows at 15:37 checkpoint cutoff 10-14 (sina late bar, next-round chain picks up naturally); market_regime ORANGE day4 shadow; scorecard/paper_export/daily_scorecard/build_status stale-takeover derive by bm-b (bm-a heartbeat stale, O-2100 s2.4 STALE_MIN law); thermo+dualarm+minute_feed+b_layer+attrition all green; NEWBAR gate newbar=False -> paper legs no-op "
             "(g) smoke 49/49 PASS (h) saturation engine live-probed alive (rc=0, queue 0, verdict idle) "
             "(i) watermark GREEN (red=false, next_pick=claimed moneyflow IC, panel parked source-blocked standing) "
             "(j) orphan probe: py_faces=14, orphans=0 (i2v runner false-positive family cleared - runner actively burned then exited clean) "
             "(k) astock rebuild march: worker 8380 alive since 11:45, per_files 2996 (r981) -> 3541 (15:39) -> 3986 (16:1x), ~+15/min, ETA ~17:35, completion package next rounds "
             "(l) S8 green_idle=false (RAM 8.4% batch window; claimable_pool_lines=1; idle_rounds=0; no idle sin) "
             "(m) S7 quad: loop recipe pin=2 no-op; watchdog recipe S4U-via-XML-flip re-registered; pre-commit + pre-push claws both OK; schtasks both tasks LogonStatus=interactive/background (S4U) - zero LogonType regression this round "
             "(n) C-r982 own-face surgery push in closeout segment C (receipt = results/_r982bmb_push_receipt.json, consumed next round)")
st["verdict"] = ("GREEN-production-win: i2v 53/53 COMPLETE (XQ05 467s clean-context fix, clips verified, valve-out done, MSG-1608 receipt); "
                 "astock rebuild 3986/5219 marching; D-19 orders delta consumed (1 row, zero bm-b action); S6 39 legs green; S7 quad green zero regression")
st["next"] = ("r983: 1) C-r982 receipt consume 2) astock refresh completion watch -> data churn completion package push (per_files ETA ~17:35) "
              "3) D-19 dual-sha re-probe 4) S7 quad (LogonType spot-check = regression watch face) 5) S8 gate "
              "6) update_daily 10-15 bar pickup check (15:37 sina late-bar face, newbar-gated legs follow) 7) r982 addendum row lands with r983 push face")
st["next_milestone"] = "astock rebuild completion package ~17:35-18:00 today (window <=48h); i2v line CLOSED (53/53 delivered)"
st["last_artifact"] = "results/_r982bmb_push_receipt.json (next-round consume)"
st["latest_artifact"] = "results/_r982bmb_push_receipt.json (next-round consume)"
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_face_note"] = "r982 probe: 14 py faces, 0 orphans (i2v runner false-positive family cleared - runner actively burned XQ05 then exited clean; zero flags)"
st["note"] = ("r982: predecessor-absorb round (first r982 session watchdog-killed pre-closeout at ~15:47, detached batch workers survived legal, this session consumed+closed); "
              "i2v completion MSG-1608 IN PUSH PAYLOAD (delivery law r959/r974); docs faces (daily_report/live_usage) written local NOT pushed (anti-regression vs bm-a fresh-host derive window); "
              "data churn (data/daily + astock per-files) held local pending refresh completion package; results scratch views local per r975 precedent")
# D-19 probe faces (orders watermark MOVED - genuine delta consumed)
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_at"] = NOW
st["last_orders_read_at"] = NOW
st["last_decisions_probe_at"] = NOW
st["last_orders_probe_at"] = NOW
st["decisions_delta_pending"] = False
st["orders_delta_pending"] = False
st["d19_probe_due"] = False
st["d19_probe_due_note"] = "r982 round-start probe consumed (decisions full-sha unchanged ab3f0cc9; orders GENUINE delta 3b1ca198->1835852b = 1 row Qwen v3 wrap-up, bm-b already compliant per canon line 27, zero action); next probe = r983 round-start cadence"
st["last_decisions_sha"] = "ab3f0cc9"
st["last_orders_sha"] = "1835852b"
st["last_decisions_sha_probe"] = "ab3f0cc9f4cb9bbb1f23c5e5a98bd5bed540a272b0b111bb481120ea7e0ba8fd"
st["last_orders_sha_probe"] = "1835852be5b3cfd23672d10660b47dafc3d921e4"
st["last_orders_sha_probe_note"] = "r982: GENUINE delta - orders blob sha1 changed 3b1ca198bdd9...->1835852be5b3... (direct hashlib.sha1 over fresh git-show dump); delta = 1 row (10-15 15:3x Qwen switchover v3 wrap-up via bm-a, group commit c0d35d0); consumed zero-action"
st["last_decisions_sha_method"] = "r982: origin blob sha256 via git show (group fetch in-probe); unchanged vs r980/r981 probes"
st["last_orders_sha_note"] = "r982: genuine delta consumed - orders sha1 1835852be5b3cfd23672d10660b47dafc3d921e4 (new watermark); delta row = bm-a Qwen v3 report, zero bm-b leg"
# sat engine
st["sat_engine"] = {"status": "alive (live-probed rc=0 this round: queue 0, verdict idle)", "checked_at": NOW}
# sync block
st["sync"]["r981_main_push"]["consumed_at"] = NOW
st["sync"]["behind_origin_main"] = 0
st["sync"]["r982_main_push"] = {
    "status": "PENDING_AT_HASH_TIME",
    "consumed_at": "pending r983",
    "behind_origin_main": 0,
    "note": "C-r982 payload = own faces (state/heartbeat/round report + completion MSG-1608 + XQ05 reignition/restart/oomtrace evidence + s6chain work files + d19 probe + orphan probe + smoke log + astock status + attrition scan + market_clock/thermo/dualarm/minute_feed diff faces); base = origin tip fresh at surgery; docs faces intentionally excluded (anti-regression); receipt = results/_r982bmb_push_receipt.json",
}
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json updated")

# ---------- heartbeat ----------
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
h["last_seen"] = NOW
h["task"] = "r982: i2v 53/53 COMPLETE + valve-out + D-19 orders delta + S6 absorb + astock watch"
h["did"] = ("r982: (a) C-r981 receipt consumed (c108b6b61 ancestor rc=0; origin +2 = bm-a r1017, zero bm-b dispatch) (b) D-19: decisions unchanged ab3f0cc9; orders GENUINE delta 3b1ca198->1835852b "
            "= 1 row Qwen switchover v3 wrap-up (bm-a report; canon bm-b line = 4b-derived CPU-only in-place = already compliant, zero action) (c) S0.5 zero-new orders/MSGs "
            "(d) predecessor r982 session absorbed (XQ05 reignition OOM 15:38 -> clean restart 15:47) (e) i2v 53/53 COMPLETE: XQ05 saved 15:55:24 (467s clean-context, 2.99MB; OOM root-cause = 5.5h server "
            "allocator fragmentation; methodology: len=226 long clips burn on FRESH server context); ALBUM LANE DONE ok=53 fail=0; clips-animatic-480 53/53 all >=182KB; VALVE-OUT done: ComfyUI tree-killed, "
            "keepwarm.pause removed, qwen3.8:4b re-pinned resident (r916 law); MSG-1608 completion receipt to fleet/inbox "
            "(f) S6 39 legs green (predecessor chain absorbed; pool_dualrun streak 37; compute_audit ignition_sla flag = bm-c RAM-park family honest; update_daily 0 rows at 15:37 = sina late bar, next round picks up) "
            "(g) smoke 49/49 (h) sat engine alive (i) watermark GREEN (j) orphan face=0 (k) astock 3986/5219 ETA ~17:35 (l) S8 not green-idle no idle sin (m) S7 quad green zero LogonType regression (n) C-r982 surgery in segment C")
h["cpu_cores"] = 16
h["free_ram_gb"] = RAM_FREE_GB
h["gpu_free_vram_mb"] = VRAM_FREE_MB
h["verdict"] = ("GREEN-production-win: i2v 53/53 COMPLETE (valve-out done, MSG-1608 receipt); astock 3986/5219; D-19 orders delta consumed zero-action; "
                "S6 39 legs green; S7 quad green")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["ts"] = NOW
h["orders_ack"] = ("r982: D-19 orders GENUINE delta consumed - 1 row (3b1ca198->1835852b: 10-15 15:3x Qwen switchover v3 wrap-up report via bm-a of CEO 'agree execute everything' approval; "
                   "bm-b face per canon line 27 already compliant = zero action); decisions sha256 unchanged (ab3f0cc9); S0.5 scan zero-new orders/zero-new MSGs; own orders O-20261015-0025/0906/0915/0952 "
                   "+ own MSGs 0104/0825/0952 standing on origin + NEW MSG-20261015-1608 animatic-53/53 completion receipt rides r982 push | " + h.get("orders_ack", ""))
h["note"] = ("r982: i2v completion MSG-1608 IN PUSH PAYLOAD; docs faces written local NOT pushed (anti-regression bm-a derive window); data churn held local pending astock completion package; "
             "orphan face=0 (family cleared); results scratch views local per r975 precedent")
with open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# self-check: epoch must be int (R170/R178 law)
h2 = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat updated; epoch int verified:", h2["heartbeat_epoch_utc"])

# ---------- round report row (append-only, binary) ----------
row = ("%s | r982 | 前会话遗产同轮吸收（15:2x-15:47 上一执行体收口前被击杀·detached 批件合法存续·本席续跑收口）+**i2v 53/53 完工判定+阀出（本轮主产出）**："
       "XQ_XQ05 末单 467s 干净上下文一次过（15:55:24·2,993,855B）——三次败因链定谳：4200s 帽×2 timeout=OOM 爬行非挂死+15:38 CUDA OOM 实锤（res_multistep 前向+aimdo 清理崩·oomtrace 两件）"
       "=5.5h 龄服务端分配器碎片（60 渲染后 idle 3951/8192MiB 被占）→正法=干净 CUDA 重启（15:47·timeout 升 10800）→467s 过·旁证 KN28 1757s/XQ26 318s 皆新鲜上下文·**方法论=长单一律新鲜服务端起烧**→"
       "ALBUM LANE DONE ok=53 fail=0·clips-animatic-480 **53/53 mp4 全≥182,492B 零空壳**·阀出三件套=ComfyUI 树杀（VRAM 释放）+keepwarm.pause 移除（Test-Path False 实证）+MinigameOllamaServe 复触+"
       "qwen3.8:4b 复 pin 常驻（vram=3711319408·serve up·GPU 回停车基线+keepwarm 常设态·r916 律）+完工回执 MSG-20261015-1608 入 fleet/inbox 随本轮上链（送达律 r959/r974）+"
       "D-19 双 sha 消费（decisions 全 sha256 恒等 ab3f0cc9…e0ba8fd 零动作·orders **真增量** 3b1ca198→1835852b=对 fresh dump 直接 hashlib.sha1 复核=1 新行=10-15 15:3x Qwen 换代 v3 收口报"
       "（bm-a 执行面·CEO 'agree execute everything' 批复·canon 实读 bm-b 行=B站线 4b 派生 CPU-only 在位+llm_assist 走路由=已合规零 bm-b 腿）·水位更新 ord 1835852b）+C-r981 回执消费"
       "（c108b6b61 ancestor rc=0·origin +2=bm-a r1017 W246 面零 bm-b 派单）+S0.5 令扫零新令零新 MSG+S6 39 腿全绿（前会话 15:36-15:41 链实况吸收·pool_dualrun ZERO-DRIFT streak37·"
       "compute_audit 旗=ignition_sla=TRIAL-LABOR-W20-SCREEN-SHARD-0..3 bm-c RAM-park 族跨机如实面·py_watermark insufficient_history n=1·update_daily 15:37 时点 0 新行 cutoff 10-14=sina 迟 bar 下轮链自然接·"
       "scorecard/paper_export/daily_scorecard/build_status=stale-takeover derive per O-2100 s2.4（bm-a 心跳 stale）·market_regime ORANGE 第 4 天 shadow·thermo+dualarm+minute_feed+b_layer+attrition 全绿·"
       "NEWBAR gate newbar=False 纸面腿 no-op）+smoke 49/49+饱和引擎活实测（rc=0 queue0 idle）+水位 GREEN（red=false·next_pick=claimed moneyflow IC parked 面板常设）+孤儿面=0"
       "（14 py faces·批 runner 假阳族清零=活跃烧录后净退场）+astock 行军判定（worker 8380 活·per_files 2996→3541→3986/5219·~+15/min·ETA ~17:35·完工包候后窗）+"
       "S8 green_idle=false（RAM 8.4% 批窗·claimable_pool_lines=1·idle_rounds=0·双产线在飞无闲置罪）+S7 四件套绿（loop 配方 pin=2 no-op·watchdog 配方 S4U-via-XML-flip 重注·双爪 OK·"
       "schtasks 双任务登录状态=交互方式/后台方式 S4U 实证=零回归） | 实况三行：当前活=astock rebuild 行军 3986/5219（worker 8380）+i2v 线已收口（GPU 回 keepwarm 常设态）；"
       "最近实物=clips-animatic-480 53/53 mp4 完工交付（XQ_XQ05 15:55:24）+MSG-20261015-1608 完工回执+阀出三件套实证（pause 移除+复 pin 3.71GB+serve up）；"
       "下个里程碑=astock 完工包 ~17:35-18:00 今日（窗≤48h） | 记账预算: 4/5（state+report+心跳+push 回执） | 产品积分: 2（53/53 实物批完工+阀出实机动作+完工 MSG） | "
       "验证证据：clips-animatic-480 53 枚 ls+min size 182492B+log-bmb-r982b.out.txt 尾「ALBUM LANE DONE ok=53 fail=0」+results/_r982bmb_xq05_reignite.json+results/_r982bmb_xq05_restart.json+"
       "oomtrace 两件+pause Test-Path False+/api/ps qwen3.8:4b 复 pin 回执+results/_r982bmb_s6chain.log 尾 CHAIN_DONE+smoke 49/49+results/_r686bmb_d19_check.json+orders sha1 1835852b 直核+"
       "results/_orphan_face_probe.bm-b.json+sat engine rc=0+watermark_red.json red=false | 下轮指针：r983=C-r982 回执消费+astock 完工判定→数据 churn 完工包+D-19 再探+S7/S8+"
       "update_daily 10-15 bar 接收判定（15:37 sina 迟 bar 面）\n")
open(r"logs\iteration-loop\round_reports.md", "ab").write(row.encode("utf-8"))
print("round report row appended")
print("NOW =", NOW, "EPOCH =", EPOCH)
