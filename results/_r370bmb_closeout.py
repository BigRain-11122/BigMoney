# -*- coding: utf-8 -*-
"""r370 bm-b closeout writer: HANDOVER 5x line + round report line +
state.json + heartbeat (UTF-8 exact, zero PS redirect faces)."""
import json
import time
import datetime
import io
import psutil

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + \
    now.strftime("%z")[-2:]           # T-separated ISO 8601 with offset
epoch = int(time.time())
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 1e9, 2)
cpu_pct = psutil.cpu_percent(interval=1)

# ---- 1. HANDOVER r370 5x line (append at tail, round-335-bm-b precedent)
hand_line = (
    "- 开发队列增量窗（续接版）*round 370 bm-b（5x 核对本轮）*，2026-09-28 09:2x 核对；"
    "对账区间增量 bm-b r366-370（基线=round 100 bm-c 行；bm-c r145/r150 线已并入），"
    "统一链 297,428→301,180 实读（TRIAL_LAB_W3_SCREEN 批 3,752 入链=bm-a R394/395 "
    "burn+finalize face；本窗 bm-b 零批 finalize）。"
    "①r366=TRIAL_LABOR_W2 slice-5 intake 落地（D6 绑定门+TRIAL-<FAMILY>-<NN> 计数器+"
    "W1 cmd_intake registered-corr 死路 bug 双波修复）；r367-369=维护/冲突窗"
    "（r368 push-storm 23-UU 正典解+escape 分支 r369 S0 discharge 落地；r369 W3 screen "
    "slice-2 bm-c 单写者零异议 MSG-0852）；**r370（本轮）=W3 judge 三件套 LANDED**"
    "（F-04 认领 MSG-0905 commit 0b8e27c2 origin-first+bm-a MSG-0915 明确让路零异议；"
    "scripts/trial_labor_w3.py judge-prep/judge/judge-finalize 三段：双腿 P-5C 网格×"
    "base/x2 四曲线全携 GATE+初始止损 overlay（冻结合成序 signal→filter→timing→GATE→"
    "initial-stop）+双 nulls seed 20288500 [20288500,i]+G1'v2/DSR/家族 PBO/G2 共享库零手抄+"
    "gate_face_judgment 分段+gate_flip_days_legL §5.6 披露列；selftest 59→72/72 hermetic+"
    "subprocess 双跑 stdout/stderr 字节恒等 rc=0+judge-prep 诚实 rc=2；池条目 TRIAL-"
    "LABOR-W3-JUDGE waiting lane_owner=null 单分片；MSG-0908 六披露回执；S7 push 撞 "
    "bm-a screen-finalize 同窗→池整文件 UU→classify=r312 pool-entry-done-union→"
    "_r370bmb_resolve.py（screen done-absorb 取完成侧+judge waiting 保留+零丢失断言）→"
    "rebase continue→push LANDED c91e909f）。"
    "②观测（非本机车道）：bm-a R394-395=W3 screen 烧批 3,752/3,752（~4.6min autofill）+"
    "finalize 落地 survivors 513/3,552=14.4%（prereg §5 pred.2 带内）+null p95 0.5116"
    "（W1/W2 同带）+**GATE 分段生存率 bear 18.96%>none 13.36%>bull 11.17%=§5 pred.4 "
    "方向实证（MASS stage-1 先验跨刻度迁移成立）**；bm-c r150=W3-SCREEN claim-race yield "
    "close（bma 烧批道权威+bmc ghost void per r392）+stash-pop mirror storm 正典解。"
    "③窗口维护面：smoke 25/25 逐轮、orders 99/99 双扫零未回执、板 0 open、post_review "
    "尾零 NO、水位 py_low_with_work_cands 合法（census W2B 4-worker 结构性+四 judge 批候选"
    " RAM 门 r354）、census W2B i=2599/5620 ETA ~16:00、S6 33 legs rc=0（pre-15:30 no-op 族+"
    "bm-a/bm-c 车道守卫诚实 no-op）、CODELY 热层 <10KB。"
    "④指针：**census W2B finalize watch→RAM ≥4GB 三采样稳窗→W1-JUDGE/MASS-TRIAL x4/"
    "W2-JUDGE/W3-JUDGE 四判决批 flips（bm-b=flip executor，W1-JUDGE r357 defer 先例）→"
    "烧批→judge-finalize×4→W2/W3 intake slices**；09-28 周一开市窗=15:30 后新 bar 全链"
    "接力（update_daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow 勿手改〕→t35v→"
    "t24×2→aggr 20 账→grid 5 账首拍 marks→export→scorecard→daily_report）；10-01 月度三件套"
    "（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门生效；10-31 公决"
    "首检 all-HOLD+T-34 半年报 11-01；迁移 v2.2 armed 窗至 09-29 12:00；r375 下次 5x 核对。"
)
with io.open("research/HANDOVER.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(hand_line + "\n")

# ---- 2. round report line (append at tail)
rr = (
    f"{ts} | round 370 bm-b | dept:策略/研究/舰队 (W3 judge slice supply step) | "
    "WM-VERDICT: py_low_with_work_cands=合法 (probe 09:07: census W2B 4-worker 在燃结构性 "
    "py 27-40% + 板 0 open + bandit 0 open + 四 judge 批池候选全 RAM 门 r354 待 census "
    "finalize=合法供给面; red=false@08:20:23 lane healthy) | did: (1) S0-1 bm-b 锚定+S0 "
    "pull FF+S0.5 orders 99/99 双扫零差集+decisions.md 不存在零动作; (2) F-04 认领 W3 "
    "judge 切片 MSG-0905（commit 0b8e27c2 origin-first 抢占窗, bm-a MSG-0915 明确让路"
    "零异议+bm-c 沉默窗）; (3) **W3 judge 三件套建落** scripts/trial_labor_w3.py: "
    "judge-prep（screen-finalize 门+grammar 锚 cc59eab79db53436+t18 manifest+双腿 census "
    "==frozen+per-leg gate meta+passive 预计算+零存活 vacuous 短路）/ judge（分片烧 "
    "checkpoint 逐格 append+judge_state 门+双腿×base/x2 四曲线全携 gate+stop overlay+"
    "双 nulls seed 20288500 [20288500,i]+regime 分段+n_eff 样本充足律+descriptive+crisis/"
    "stop/gate-flip 披露列）/ judge-finalize（G1'v2+DSR n_trials=活链头跨波不重置+家族 "
    "PBO CSCV+G2+E[FP]+gate_face_judgment 分段+账本 TRIAL_LAB_W3_JUDGE+gate_flip_days_"
    "legL §5.6 面板级翻面计数列 gate=none→null）; selftest 59→**72/72 PASS** (+13 judge "
    "腿) + subprocess 双跑 stdout/stderr sha 恒等 rc=0 + judge-prep CLI 门诚实 rc=2 实证; "
    "池条目 TRIAL-LABOR-W3-JUDGE waiting lane_owner=null 单分片（_r370bmb_add_pool.py "
    "断言守卫）; MSG-0908 六披露回执; (4) S7 push 撞 bm-a screen-finalize 同窗→runnable_"
    "pool 整文件 UU→classify_conflicts=r312 pool-entry-done-union→_r370bmb_resolve.py"
    "（HEAD=screen done+result_ref 完成侧吸收+我方 judge waiting 保留+94 条零丢失断言+"
    "parse-verify）→rebase continue（core.editor=true 律）→push LANDED c91e909f; "
    "(5) W3 screen 判读面收讫（bm-a MSG-0915: survivors 513/3,552=14.4% 带内、null p95 "
    "0.5116、GATE 分段 bear 18.96%>none 13.36%>bull 11.17%=§5 pred.4 方向实证）; (6) S6 "
    "33 legs rc=0（水位 probe+compute_audit CLEAN+update_daily 0 新行 cutoff 09-24 中秋"
    "口径+regime ORANGE shadow+clock ORANGE_COOL+全 bm-a/bm-c 车道守卫诚实 no-op+fundamental"
    " fresh skip+b_layer 5222 全过 gates all_pass+live.paper/t35v/t24 无新 bar 条件腿"
    "跳过+aggr/alloc/grid 幂等 no-op+export/scorecard 守卫跳过+daily_report faces=4 token=1"
    "+token delta=0）; (7) 收件箱 4 消息判读归档（0844/0852/0858/0915）; (8) 5x HANDOVER "
    "r370 线+S7 schtasks 实勘+自愈链 | verify: smoke 25/25; census i=2599/5620 ETA ~16:00"
    "（08:46:34 checkpoint 7min 前）; judge 链物理依赖=①screen-finalize 已落 ✓ ②judge-prep"
    "（bm-b 宿主）③RAM≥4GB 三采样=后两门待 census 收尾窗 | next: census W2B finalize "
    "watch→RAM 稳窗→W1-JUDGE/MASS x4/W2-JUDGE/W3-JUDGE 四 flips（bm-b=flip executor）→"
    "烧批→finalize×4→W2/W3 intake slices; V2-P1 un-defer after W2B finalize+RAM（清 "
    "defer_note r378 律）; 周一 15:30 后新 bar 全链; 10-01 月度三件套+REGIME_GUARD v3 日期门; "
    "迁移窗 09-29 12:00"
)
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8",
             newline="\n") as fh:
    fh.write(rr + "\n")

# ---- 3. state.json (bm-b face: root state.json)
state = json.load(io.open("state.json", encoding="utf-8"))
state["machine_id"] = "bm-b"
state["round_no"] = 370
state["note"] = ("r370: W3 judge slice LANDED (MSG-0905 claim, bma yield zero-objection "
                 "MSG-0915; trio+pool waiting+selftest 72/72; pool UU r312 done-union "
                 "resolved, push c91e909f); census W2B burn watch; judge chain = "
                 "judge-prep + RAM window post-census")
with io.open("state.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---- 4. heartbeat fleet/machines/bm-b.json (own file only)
hb_path = "fleet/machines/bm-b.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch          # python int, JSON int (R170/R178 law)
hb["clock_read"] = ts                       # T-separated ISO 8601 (R262 law)
hb["current_task"] = (
    "r370: W3 judge slice LANDED (F-04 claim MSG-0905 -> trio judge-prep/judge/"
    "judge-finalize + pool TRIAL-LABOR-W3-JUDGE waiting; selftest 59->72/72 "
    "double-run byte-identical; six-disclosure MSG-0908; pool UU r312 done-union "
    "resolved vs bma screen-finalize same-window); next = census W2B finalize "
    "watch (i=2599/5620 ETA ~16:00) -> RAM stable >=4GB window -> W1-JUDGE/MASS x4/"
    "W2-JUDGE/W3-JUDGE flips (bm-b = flip executor, autofill-fed) -> judge burns -> "
    "finalize x4 -> W2/W3 intake slices; V2-P1 un-defer after W2B finalize+RAM "
    "(clear defer_note r378 law)"
)
hb["round_no"] = 370
hb["loop_round"] = 370
hb["round"] = 370
hb["cpu_cores"] = vm.total and 16
hb["free_ram_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["idle_ram_mb"] = int(ram_free_gb * 1024)
hb["free_ram_mb"] = int(ram_free_gb * 1024)
hb["cpu_util_pct"] = cpu_pct
hb["cpu_pct"] = cpu_pct
hb["verdict"] = (
    "healthy: smoke 25/25, S6 33 legs rc=0 (pre-15:30 no-op family + lane guards "
    "honest skip), W3 judge slice landed (selftest 72/72, pool waiting RAM-gated), "
    "census W2B in-flight 4-worker i=2599/5620 (py 27-40% structural), free RAM "
    f"{ram_free_gb}GB window (judge pool candidates RAM-gated lawful r354), W3 "
    "screen survivors 513 received (bma finalize), zero collision faces"
)
with io.open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print(f"[r370 closeout] ts={ts} epoch={epoch} ram_free={ram_free_gb}GB "
      f"cpu={cpu_pct}% | HANDOVER+roundreport+state+heartbeat written, "
      f"epoch int + clock T verified")
