# -*- coding: utf-8 -*-
# r1070 bm-a closeout: state + heartbeat + round report + HANDOVER 5x (four faces, one pass)
import json, os, datetime, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
TS = now.isoformat(timespec="seconds")            # 2026-10-19T02:XX:XX+08:00 (T-sep law)
EPOCH = int(now.timestamp())

def wjson(path, d):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def rjson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---- resource faces ----
import psutil
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 1024**3, 1)
ram_free_pct = round(vm.available / vm.total * 100, 1)
gpu_free = None
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20).stdout.strip()
    gpu_free = int(o.splitlines()[0])
except Exception:
    gpu_free = -1

DID = ("r1070: (1) S0 pull window: behind=9 -> untracked estate face (results/post_review/REPORT-20261019.md "
       "dead-window derive) blocked merge -> hash-diff vs origin blob (differ) -> quarantined "
       "results/_quarantine/REPORT-20261019.local-r1070.md + removed (lossless: same-day idempotent regen face, "
       "origin committed face takes over) -> pull rc0 absorbed bm-c r1098..r1103 batch (W272 five-face complete "
       "one-window r1100 + W273 seat 92nd own wave r1101 + W273 PREREG FREEZE 839441a547 + W274 derive PREP "
       "3a01530c70 = bm-c lane chain, bm-a zero wave obligation); autostash pop 2 UU resolved per law "
       "(watermark_red.json newer-wins local 01:51:03 vs origin 01:23:03 r1028 family; post_review.jsonl union "
       "12095+12095->12145 zero-loss asserted r419/r1061); stash dropped; marker scan rc0; (2) round-zero orphan "
       "probe 0/21 py faces 1 resident server exempt; idle trigger round-head green_idle=false (RAM 32.5pct) "
       "two_read_red=false idle_rounds=0; (3) S0.5 orders_ack dual-face scan CLEAN 105/114/0; D-19 dec+ord BOTH "
       "advanced (dec 78658731->8706acd8 = 10-19 00:00 batch D-01..D-04 all dispatched/executed elsewhere, zero "
       "bm-a-loop obligation; ord 6bfe7815->e695556b = 23:46 CEO quanmian-kaigong resume-trigger row executed via "
       "bm-a interactive window, loop visibility-consume; read-back full-string equality, mirrors synced 8); "
       "(4) S1 smoke 49/49; S3 satengine alive rc0 queue0 verdict idle; (5) CANON KIT ADOPT CLOSED (O-2236 "
       "sec.3.1 <=1-round window): group-origin probe hit idle-guard-kit/bmc_idleguard.py + work-bank schema -> "
       "Tools/bma_idleguard.pyw v2 canon-adopted (canon claim logic + bank schema + PRODUCER exposure + atomic "
       "writes + queue-busy parity; bm-a deltas documented: GPU busy face nvidia-smi util+compute-apps "
       "immune-by-construction to C2059 self-match; SatEngine revive register_satengine_task+tick recipe; JSONL "
       "sentinel log; spawn-fail revert-to-pending) + live-fire rc0 (busy face util 22pct busy-clear-mark; 17 "
       "scheduled fires 23:05-01:55 all rc-clean; two-hop caught 01:35 false-idle blip; SatEngine alive all "
       "fires) + bm-a-gpu-bank.json CAS surgical delivered to group origin (0b90342673, _law verbatim + empty "
       "jobs = producer-pending honest face, blob equality asserted, zero tree touch per r1054 "
       "group-activity-window law); O-2236 receipt addendum appended; MSG-20261019-0102 kit-landed consumed -> "
       "processed; (6) A1 G3 FALSE-GREEN FIX LANDED (plan sec.III A1, deadline <=10-21 met early): "
       "scripts/saturation_engine.py + _claimable_crossface pure helper (structural wait != ignitable work; "
       "SLI-RECONCILE precedent 2026-10-15) wired pre-ignite-loop on full materialized queue; "
       "last_tick/face/status carry claimable_n/struct_wait_n/struct_wait_idle dual read; selftest 12 legs PASS "
       "incl. false-green counterexample (all-door-blocked queue reads struct_wait_idle NOT loaded, door name "
       "carried) + positive control (door-open reads fully claimable); live tick rc0 (queue0 honest idle, "
       "crossface 0/0/False) + status dual-read live; (7) S6 chain 43 legs all rc0 bad=0 (r1069 face verbatim "
       "clone _r1070bma_s6chain.ps1, log results/_r1070bma_s6chain_rc.log); MF day-13 retest INSIDE chain = "
       "MONDAY ADJUDICATION CLOSED: fresh spawn first-pull mode -> 3x RemoteDisconnected conn-fuse stop, "
       "checkpoint intact (done 2152), panel cutoff 2026-10-13 complete=false -> ADJUDICATED PERSISTENT "
       "(day-8..13 six-day consecutive same-signature chain, both lanes) -> panel stays parked+frozen, "
       "self-heal stays armed (fast-fail zero-rows zero-waste), moneyflow IC batch (watermark next_pick) stays "
       "gated on panel completion, sina_mf parallel-source redundancy in-service; face moves "
       "waiting->standing-blocked disclosure; (8) W274 seat @ALL consumed informational (owner=bm-c 93rd own "
       "wave candidate, prereg derive = bm-c next-window FIRST ACTION); slots MSGs (bmc/bmb) left in inbox for "
       "hardware seat (r1037 precedent); (9) S7 quartet idempotent + attrition rc0 (in-chain) + HANDOVER 5x "
       "r1070 row (r1065 stamp absence OVERDUE-DISCLOSED per r1050 precedent)")

CURRENT = ("r1070: product round -- O-2236 canon adopt CLOSED (guard v2 canon-adopted + live-fire + "
           "bm-a-gpu-bank.json CAS-delivered to group origin 0b90342673) + A1 G3 false-green fix LANDED "
           "(saturation_engine claimable crossface, selftest 12 legs, live dual-read) + MF Monday adjudication "
           "CLOSED (blockade persistent day-13, standing disclosure) + S6 43 legs rc0 + D-19 dual advance")
TASK = "r1070: canon-adopt + A1 G3 fix + MF adjudication product round"
ARTIFACT = ("Tools/bma_idleguard.pyw v2 (canon-adopted, live-fire rc0) + scripts/saturation_engine.py "
            "(A1 claimable crossface, selftest 12 legs PASS) + cph4/fleet/work-bank/bm-a-gpu-bank.json "
            "(group origin 0b90342673 CAS, blob equality) + results/_r1070bma_s6chain_rc.log 43 rc0")
NEXT = ("r1071: (1) A2 G4 PnL-attribution daily report leg (plan sec.III A2, <=10-23; daily_report "
        "attribution section + selftest leg); (2) canon kit local-tree materialization rides fleet sync (bank "
        "file on origin; guard reads local tree, absent=empty equivalent face); (3) W274 chain watch on bm-c "
        "lane (zero bm-a obligation until a seat names bm-a); (4) BmaIdleGuard v2 scheduled fires observation "
        "continues; (5) council sec.6 first ruling table watch <=10-20 12:00; (6) E20 three-axis synthesis = "
        "GM/council signature reserved face; (7) construction-plan committee report <=10-25 (A3 G1+G2 "
        "runtime-side enforcement next batch <=10-24); (8) month-boundary first exam 10-31; (9) next 5x = "
        "bm-a r1075")
NEXTEM = ("A2 G4 PnL-attribution daily face <=10-23; construction-plan committee report <=10-25; MF blockade "
          "standing (self-heal armed, IC batch gated on panel completion)")
VERDICT = ("GREEN: r1070 product round all green -- canon adopt CLOSED same-round (guard v2 + live-fire + bank "
           "CAS 0b90342673 + receipt addendum) + A1 G3 false-green fix landed EARLY (deadline 10-21, selftest "
           "12 legs + live dual-read) + MF Monday adjudication CLOSED (persistent, standing-blocked "
           "disclosure) + S6 43 rc0 + D-19 dual advance + smoke 49/49 + board CLEAN 105/114/0 + orphan 0/21; "
           "product score = 2-point candidate x2 (runnable infra: canon guard v2 + engine crossface); honest "
           "faces = CODELY budget 9903B near-line (pit row deferred to state notes), r1065 5x stamp absence "
           "OVERDUE-DISCLOSED, dual S4U flips still carried C-20261016-04")
VERIFY = ("results/_r1070bma_s6chain_rc.log 43 rc-lines all rc0 bad=0 + A1 selftest PASS (12 legs incl. "
          "false-green counterexample + positive control) + A1 live tick/status dual-read (claimable_n/"
          "struct_wait_n/struct_wait_idle live faces) + guard v2 live-fire log (~/.codely-cli/sentinel/"
          "bma-idleguard.log, bma-idleguard-v2-canon busy-clear-mark rc0) + group CAS receipt "
          "(_r1070bma_group_bank_cas.py: push ok 0b90342673 blob_equality ok attempts 1) + D-19 advance "
          "read-back full-string equality (dec 8706acd8 / ord e695556b, mirrors synced 8) + orders_ack_scan "
          "CLEAN 105/114/0 + smoke 49/49 + orphan probe 0/21 + MF refresh log day-13 face (3x "
          "RemoteDisconnected fuse-stop)")
NOTES = ("r1070: (1) NEW pit: untracked working-tree estate blocks pull --rebase (autostash covers tracked "
         "only) -- resolve = git hash-object --no-filters vs git rev-parse origin/main:<path>: identical = "
         "lossless rm; differ = quarantine copy + rm; origin face takes over post-pull (today: "
         "REPORT-20261019.md quarantined results/_quarantine/, dead-window derive redundant vs committed "
         "origin face); (2) A1 crossface measured PRE-ignite-loop on FULL queue (loop pops struct-blocked "
         "heads into skips, post-loop depth would hide the struct-wait face); (3) utf-8 tail slicing must "
         "decode-then-slice not bytes[-N:] (mid-char break = unreadable file, self-fixed in _r1070bma_"
         "pull_faces.py); (4) CODELY budget 9903B near 10KB line: new pit row deferred to this notes face "
         "per hot-cold law")
ACKNOTE = ("r1070: fleet board CLEAN (105 orders / 114 acks, 0 unacked, 0 face divergence); zero NEW fleet "
           "orders this window (canon-adopt receipt rides O-20261018-2236 addendum line); D-19 group deltas "
           "consumed via advance (10-19 00:00 decisions batch D-01..D-04 = other-seat executions; 23:46 CEO "
           "resume row = bm-a interactive-window executed, visibility-consume); inbox: kit-landed + w274-seat "
           "consumed -> processed; slots MSGs (bmc/bmb) left for hardware seat")

# ---- state-bm-a.json (full canonical repair incl. r1069 partial-write heal) ----
sp = os.path.join(ROOT, "state-bm-a.json")
st = rjson(sp)
prev_epoch = st.get("heartbeat_epoch_utc", EPOCH)
for k, v in [("round_no", 1071), ("round", 1070), ("loop_round", 1070),
             ("last_round", "r1070"), ("last_round_label", "r1070"), ("round_no_label", "r1070"),
             ("current", CURRENT), ("current_task", TASK), ("task", TASK), ("did", DID),
             ("last_action", DID), ("now_active", "bm-a loop r1070 closeout (canon-adopt + A1 G3 fix + MF adjudication product round)"),
             ("next", NEXT), ("next_milestone", NEXTEM), ("verdict", VERDICT), ("verify", VERIFY),
             ("last_artifact", ARTIFACT), ("recent_artifact", ARTIFACT), ("latest_artifact", ARTIFACT),
             ("notes_r1070", NOTES), ("orders_ack_note", ACKNOTE),
             ("orphan_face", 0), ("orphan_faces", 0), ("orphan_killed", 0),
             ("heartbeat_epoch_utc", EPOCH), ("heartbeat_epoch_utc_type_int", True),
             ("last_heartbeat_epoch_utc", prev_epoch),
             ("clock_read", TS), ("ts", TS), ("updated", TS), ("updated_at", TS),
             ("last_round_at", TS), ("last_round_closed", TS), ("last_round_ts", TS),
             ("last_run", TS), ("last_seen", TS), ("last_action_at", TS),
             ("last_orders_at", TS), ("last_decisions_at", TS),
             ("last_orders_read_at", TS), ("last_decisions_read_at", TS),
             ("cpu_pct", cpu), ("cpu_load_pct", cpu), ("cpu_total_pct", cpu), ("cpu_util_pct", cpu),
             ("free_ram_gb", ram_free_gb), ("ram_free_gb", ram_free_gb), ("idle_ram_gb", ram_free_gb),
             ("ram_free_pct", ram_free_pct), ("free_ram_pct", ram_free_pct),
             ("ram_load_pct", round(100 - ram_free_pct, 1)),
             ("gpu_free_vram_mb", gpu_free)]:
    st[k] = v
wjson(sp, st)

# ---- heartbeat fleet/machines/bm-a.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = rjson(hp)
prev_epoch_h = hb.get("heartbeat_epoch_utc", EPOCH)
for k, v in [("round_no", 1071), ("round", 1070), ("loop_round", 1070),
             ("last_round", "r1070"), ("last_round_label", "r1070"), ("round_no_label", "r1070"),
             ("current", CURRENT), ("current_task", TASK), ("task", TASK), ("did", DID),
             ("last_action", DID), ("now_active", "bm-a loop r1070 closeout"),
             ("next", NEXT), ("next_milestone", NEXTEM), ("verdict", VERDICT), ("verify", VERIFY),
             ("last_artifact", ARTIFACT), ("recent_artifact", ARTIFACT), ("latest_artifact", ARTIFACT),
             ("orders_ack_note", ACKNOTE),
             ("orphan_face", 0), ("orphan_faces", 0), ("orphan_killed", 0),
             ("heartbeat_epoch_utc", EPOCH), ("heartbeat_epoch_utc_type_int", True),
             ("last_heartbeat_epoch_utc", prev_epoch_h),
             ("clock_read", TS), ("ts", TS), ("updated", TS), ("updated_at", TS),
             ("last_round_at", TS), ("last_round_closed", TS), ("last_round_ts", TS),
             ("last_run", TS), ("last_seen", TS),
             ("cpu_pct", cpu), ("cpu_load_pct", cpu), ("cpu_total_pct", cpu), ("cpu_util_pct", cpu),
             ("free_ram_gb", ram_free_gb), ("ram_free_gb", ram_free_gb), ("idle_ram_gb", ram_free_gb),
             ("ram_free_pct", ram_free_pct), ("free_ram_pct", ram_free_pct),
             ("ram_load_pct", round(100 - ram_free_pct, 1)),
             ("gpu_free_vram_mb", gpu_free), ("health", "green")]:
    hb[k] = v
wjson(hp, hb)

# int-type assertion (R170/R178 law)
assert isinstance(rjson(hp)["heartbeat_epoch_utc"], int)
assert isinstance(rjson(sp)["heartbeat_epoch_utc"], int)

# ---- round report line ----
RL = (TS + " | r1070 | 产品轮（水位绿 red=false healthy）：当前活=O-2236 canon adopt 闭环+A1 G3 假绿修正落地"
      "（排期件 ≤10-21 提前达成）+MF 周一裁决定谳；最近实物=Tools/bma_idleguard.pyw v2（canon-adopted·实弹 rc0）"
      "+scripts/saturation_engine.py A1 claimable 交叉面（selftest 12 腿 PASS·live 双面读数）"
      "+cph4/fleet/work-bank/bm-a-gpu-bank.json（集团 origin 0b90342673 CAS·blob 恒等）；下个里程碑="
      "A2 G4 盈亏归因日账面 ≤10-23+建设案委员会呈报 ≤10-25 | did: S0 9-commit absorb（untracked estate 隔离处置"
      "+2 UU 收口 watermark newer-wins/post_review union 12145 零丢失）·D-19 dec/ord 双 advance 8706acd8/e695556b"
      "（10-19 00:00 决策批全他司执行+23:46 全面开工行=他窗 executed 可见性消费）·smoke 49/49·canon kit 探针命中"
      "→adopt 三件闭环（guard v2+银行 CAS+回执补遗）·守卫 17 火观察收口·S6 43 腿全 rc0 bad=0·MF day-13=封锁持续裁定"
      "（六连日同签名·面板冻结 10-13+自愈常开+sina_mf 平行源冗余·候裁决→常设封锁披露）·W274 席=bm-c 93rd own wave "
      "informational·HANDOVER 5x（r1065 缺戳披露）| verify: _r1070bma_s6chain_rc.log 43 rc0+A1 selftest 12 legs"
      "+guard v2 live-fire+group CAS receipt 0b90342673 blob_equality+D-19 read-back 恒等 mirrors 8+ack scan "
      "CLEAN 105/114/0+orphan 0/21 | 本地未达 origin commit 数=0（主提交推送后验·postscript 收口章）")
rp = os.path.join(ROOT, "round_reports-bm-a.md")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(RL + "\n")

# ---- HANDOVER 5x row ----
HR = ("> bm-a round 1070 五倍数核对｜" + TS + " 核对；增量窗覆盖 r1061-r1070 十轮·**5x 戳 r1065 未落="
      "OVERDUE-DISCLOSED**〔r1061-r1068 死窗遗产吸收+等待态维护轮+守卫部署窗连续消耗·单窗紧凑覆盖范式收口〕"
      "·零回改零伪造·逐轮权威=round_reports-bm-a.md 全量在册+state-bm-a.json notes 族）：增量窗主线="
      "**死窗遗产坑链收口+O-2236 canon adopt 闭环+A1 G3 假绿修正落地+MF 周一裁决收口+建设案开工**——"
      "①r1061 死窗 staged 遗产+孤儿 UU 组合提交吞面坑首例（numstat 复盘点破+pathspec 重提交正法+E72 卡+CODELY 行）"
      "+S5-27 像素判读=bm-c 判读受证（差分法一致性标准）；②r1062 CODELY.md 热冷整编主件（9,987B·verbatim=archive "
      "202610.md·prescan rc3 授权面）+W270 收官观察；③r1063-r1067 等待态维护轮链（W271/W272 bm-c lane 观察+MF "
      "day-11/12 证据链+O-1810 广播令消费+r1065 五枚 CLOUD_CAP_DEFER 非死窗判读+r1066 push 竞速 claw 正拦+pre-push "
      "爪 bmc 件保护实弹）；④r1068 O-2236/O-2144 P0 同轮执行（interim BmaIdleGuard 部署+任务 Ready+首跳 rc0+双面回执"
      "+MSG-2310 canon-kit 请求+S4U XML flip 拒绝访问=carried C-20261016-04）；⑤r1069 建设案产品轮"
      "（scripts/automation_line_audit.py 五要素审计面 selftest 8/8+research/AUTOMATION-LINE-PLAN-v1.md A1-A5 排期"
      "+D-19 双 advance·pipe-hash 污染坑抓获=python raw-bytes 正法）；⑥r1070 本窗=**canon adopt 闭环**"
      "（kit 集团 origin 命中→Tools/bma_idleguard.pyw v2 canon-adopted〔认领逻辑/银行 schema/PRODUCER 曝光/原子写"
      "/queue parity·bm-a 保留面=C2059 免疫 GPU 忙判+SatEngine 正典复活配方+JSONL 哨兵+spawn 失败回滚 pending〕"
      "+实弹 rc0+17 计划火观察〔忙判正确·两跳拦截假闲闪断〕+**bm-a-gpu-bank.json CAS 投递集团 origin 0b90342673**"
      "〔_law verbatim+空 jobs 诚实面·blob 恒等·零树触碰〕）+**A1 G3 假绿修正落地**（saturation_engine."
      "_claimable_crossface 纯函数=tick 前全队列双面读 queue_depth vs claimable_n·struct_wait_idle 判定·"
      "last_tick/face/status 三面携字段·selftest 12 腿含假绿反例+正控制·live tick/status 双面读数 rc0·排期 ≤10-21 "
      "提前达成）+**MF 周一裁决定谳**（day-13 复测 spawn→3x RemoteDisconnected fuse 停发=六连日同签名→封锁裁定持续态"
      "·面板冻结 10-13+自愈常开+IC 批候面板完成+sina_mf 平行源冗余·候裁决→常设封锁披露）+S6 43 rc0+D-19 dec/ord "
      "双 advance（10-19 00:00 决策批 D-01..04 全他司执行+23:46 全面开工行=他窗 executed 可见性消费）+新坑律入 state "
      "notes（untracked estate 拦 pull --rebase 处方正法）。维护面全窗：smoke 49/49 链·S6 43 rc0 链·attrition CLEAN 链"
      "·孤儿面 0 链·四件套幂等链（loop pin=8·watchdog S4U flip=carried C-20261016-04·双爪 MATCH）·idle_trigger 链。"
      "产品清单漂移（增量代表面非全列）：Tools/bma_idleguard.pyw v2+Tools/register_idleguard_task.ps1+scripts/"
      "saturation_engine.py A1 交叉面+scripts/automation_line_audit.py+research/AUTOMATION-LINE-PLAN-v1.md+组树 "
      "cph4/fleet/work-bank/bm-a-gpu-bank.json+results/_r10xxbma_* 工件族+CODELY.md 热冷整编面+archive 202610.md。"
      "指针：**A2 G4 盈亏归因日账面 ≤10-23（plan §三）→A3 G1+G2 运行侧执法 ≤10-24→A4 W 波循环正式化+呈报 ≤10-25"
      "→A5 首线验收 ≤10-31**；W274+ 链=bm-c lane（席位点名 bm-a 才动）；MF 封锁常设披露（自愈在役）；月界首考 10-31；"
      "下一 5x=bm-a r1075。[via bm-a r1070]")
hp2 = os.path.join(ROOT, "research", "HANDOVER.md")
with open(hp2, "a", encoding="utf-8", newline="\n") as f:
    f.write(HR + "\n")

print(json.dumps({"closeout": "r1070-ok", "ts": TS, "epoch_int": EPOCH,
                  "cpu": cpu, "ram_free_gb": ram_free_gb, "gpu_free_mb": gpu_free,
                  "state_round_no": 1071, "heartbeat_epoch_int": True}, ensure_ascii=False))
