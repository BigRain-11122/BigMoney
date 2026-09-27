# -*- coding: utf-8 -*-
"""r391 bm-a close-out: state file, heartbeat, round report line (one-shot)."""
import json, time, datetime

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
TS_LOOSE = NOW.strftime("%Y-%m-%dT%H:%M") + "x"
HM = NOW.strftime("%H:%M")

did = (
    "R391: TRIAL_LABOR_W3 prereg 起草+冻结（T-2026-09-28-97 认领即开跑同轮=TRIAL_LABOR_LAW §1 常设线默认动作"
    "〔触发实况三条件：板空 0 open+池饿 0 bm-a 可吃〔8 非 done 全 bm-b 车道或物理/RAM 门后〕+零在飞判决批"
    "〔W1/MASS/W2 三判决批全池 waiting〕〕；新语法面=政体入场门 GATE∈{none,bull, bear} 六元组 R/X/S/T/STOP/GATE"
    " 10,752 组合/模板〔先验=REFINE-BENCH 首炉第一杠杆+MASS stage-1 复现 36.7% vs 9.0%·trial-labor W1/W2 谱系未开面〕"
    "→ 第四语法 sha 待序列化（≠W1 a2fa15f4b06b3c40≠MASS 96269ebe766c3fc2≠W2 1dd3d95792395cec）+"
    "seeds 20287500/20288000/20288500 band 扫描零命中同 commit 登记 R250 一步律+排除律六源"
    "〔+w2_screen 存活 404+MASS screen 存活 166 generate 时点实读消费·judged 三源 declare 不可得零行如实〕+"
    "W2-C census 族面禁碰 anti-dup〔W2 §9.1 独占 declare〕+judged 供给 generate 时点重declare 窗〔W2 同门先例〕"
    "〕commit 28fcb7b2 pushed origin + F-04 MSG-20260928-0755-bma-all 发出 + "
    "S0.5 99/99 双扫零未回执〔README.md 非令件〕+decisions 零涉本仓新行〔D-06 r390 已回执〕+"
    "S0 stash-rebase 拉齐 bm-c r145〔fund_premium 周一首拍 de-risk+V2-P1 fuse 通道解锁 post-census〕"
)
verify = (
    "smoke 25/25 + prereg 冻结四件定向 add（未 -A·watchdog autofill_state 未吞）+science_gates import 实证"
    "〔registry 三键 20287500/20288000/20288500 读回 ok〕+S6 全链 rc=0 盘前 no-op 家族零掩盖"
    "〔audit v2.3 CLEAN py 0.0% flags=[] load_state pool-supply-gap+wm probe py_low_board_clear legal-idle "
    "n=2 span 21.3min avg 0.1%+daily 0 新行 cutoff 09-24+regime ORANGE shadow breadth 0.77+scorecard 6/28/7+"
    "clock CALL-0924 ORANGE_COOL sleeves=4 activated=0+lhb <30min+heat pre-15:30+futures/repo/options/sinamf/ths "
    "cutoff-covered 零网络+MF rank pass spawn 诚实+astock/revosc/alloc/fp 车道护栏 no-op+AH refresh spawn 诚实+"
    "fundamental 10.1h fresh-skip+b_layer mask 5222 all_pass+live.paper 6/6 anchor OK〔enforce→shadow 日期门 "
    "2026-10-01 诚实降级〕+t35v PASS zero-pending+t24p 22/22 drift=0+t24m 0/22 NOT-ELIGIBLE 诚实+"
    "aggr/grid/sysv1 idempotent+t35exp 09-24+daily_report faces=4+build_status+token delta=0〕+"
    "schtasks 4/4〔IterationLoop Running pin=8 ok/LoopWatchdog Ready 08:00/claw installed〕+orders scan-2 零"
)
nxt = (
    "T-97 W3 runner build（scripts/trial_labor_w3.py=import-face 复用 w1/w2/mass 机械+GATE effective-signal "
    "置零叠加层〔MSG-0440 E1 映射先例·engine/exit_rules.py 零触碰〕+selftest hermetic 含 gate 因果腿/NaN 窗 "
    "gate-closed/gate=none=W2 语义基线 parity〕→grammar 序列化+TRIAL_GRAMMAR_LEDGER wave-3 行→"
    "TRIAL-LABOR-W3-GENERATE 池条目〔RAM 门 r354 三采样〕；W2B census finalize watch ETA ~10:30→"
    "W2-C §9.2 当值机起草窗+judge 链 flip（bm-b 车道）；T-91 s3 09:15 auto-fire watch〔IntradayMarks 09:25 "
    "armed·今日首 marks 15:30 后链〕；三判决批 48h CEO 呈报钟 09-29 22:45（bm-b）；council C-01 窗 09-29 12:00"
)

# ---- state file ----
with open("state-bm-a.json", encoding="utf-8") as f:
    s = json.load(f)
s["round_no"] = 391
s["did"] = did
s["verify"] = verify
s["next"] = nxt
s["last_round_at"] = TS_LOOSE
s["current_task"] = (
    "r391 closed: TRIAL_LABOR_W3 prereg frozen+pushed 28fcb7b2 (T-97 bm-a claim; GATE axis new grammar face "
    "10,752 combos; seeds registered R250; W2-C forbidden anti-dup); next = W3 runner build + grammar "
    "serialize -> GENERATE pool; W2B finalize ~10:30 watch -> W2-C drafting window + judge flips (bm-b)"
)
s["updated"] = TS
s["last_round_ts"] = TS
s["round"] = 391
s["loop_round"] = 391
s["ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
s["last_round"] = TS
with open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# ---- heartbeat ----
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    h = json.load(f)
h["last_seen"] = TS
h["current_task"] = s["current_task"]
h["round_no"] = 391
h["round"] = 391
h["loop_round"] = 391
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = TS
h["task"] = "round-closed"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# ---- heartbeat self-assert (F7 law) ----
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    h2 = json.load(f)
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"] and h2["clock_read"][13] == ":", "clock_read must be T-separated"

# ---- round report line ----
report_line = (
    "\n" + TS + " | R391 bm-a (dept:策略+研究·试用劳动力常设线 W3 供给波起草轮) | "
    "WM first-line verdict: green (red=false lane healthy; probe 07:47:38 py_low_board_clear legal-idle "
    "n=2 span 21.3min avg_py 0.1%: board 0 open / bandit 0 / pool 8 non-done 全 bm-b 车道或物理/RAM 门后"
    "〔W2B census bm-b 燃 ETA ~10:30+V2-P1 ready bm-b+MASS judge x4+W1-JUDGE+W2-JUDGE 全 waiting=bm-b "
    "declare/RAM 门 frozen sec.9.1 串行〕=零 bm-a 可吃·audit v2.3 07:47 CLEAN py 0.0% flags=[] load_state "
    "pool-supply-gap) | did: S0-1 锚定 bm-a + S0 stash-rebase 拉齐 68be0530〔bm-c r145：fund_premium 周一"
    "首拍 de-risk+V2-P1 fuse 通道解锁 post-census〕+untracked dup 备份件在位零触碰〔r385 留档〕+S0.5 orders "
    "99/99 scan-1 零未回执+decisions 零涉本仓新行+S1 smoke 25/25+S2 板空核验〔job_list 0+fleet 33 tickets "
    "全 claimed·T-96 bm-b 在制〕+S3 主闭环=**TRIAL_LABOR_W3 prereg 起草+冻结+pushed 28fcb7b2**〔T-2026-09-28-97 "
    "认领即开跑同轮=TRIAL_LABOR_LAW §1 常供律默认动作：触发实况=板空+池饿+零在飞判决批；新语法面=政体入场门 "
    "GATE∈{none,bull,bear} 六元组 10,752 组合/模板〔REFINE_BENCH_LAW §2 R 轴血统·先验=首炉第一杠杆+MASS "
    "stage-1 复现 36.7% vs 9.0% vs 5.5%·trial-labor W1/W2 谱系未开面→GATE×STOP×轴系交互=新增可检空间〕；"
    "seeds 20287500/20288000/20288500 rg+registry 双扫描零命中同 commit 登记 R250 一步律；排除律六源"
    "（w1_screen 149+w2_screen 404+MASS screen 166 generate 时点实读消费+judged 三源 declare 不可得零行"
    "如实+注册六员+34 判负原批）；GATE 机制=信号日 510300 close vs MA200〔§2 门序列 3,483 行 2012-05→cutoff "
    "实证〕T+1 因果·effective-signal 置零·MSG-0440 E1 映射先例·engine/exit_rules.py 零触碰；W2-C census "
    "族面禁碰 anti-dup〔W2 §9.1 已declare 独占〕；judged 供给 (d) 面 generate 时点重declare 窗=W2 同门先例；"
    "F-04 MSG-20260928-0755-bma-all 同窗发出〕+S6 全链 rc=0 盘前 no-op 家族零掩盖+S7 自愈 4/4"
    "〔Loop Running pin=8/Watchdog Ready 08:00/claw installed/orders scan-2 零〕 | verify: smoke 25/25+"
    "science_gates import 实证三键读回+S6 全腿 rc=0+live.paper 6/6 anchor OK〔enforce→shadow 日期门 "
    "10-01 诚实〕+schtasks 4/4+state round_no 391 readback | next: W3 runner build→grammar 序列化→"
    "GENERATE 池条目；W2B finalize ~10:30→W2-C §9.2 起草窗+judge 链 flip（bm-b）；T-91 s3 今日 09:15 "
    "auto-fire watch；48h 呈报钟 09-29 22:45；下轮 5x=bm-a r395\n"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(report_line)

print("r391 close-out OK:", TS)
print("epoch:", h2["heartbeat_epoch_utc"], "clock:", h2["clock_read"])
print("state round_no:", json.load(open("state-bm-a.json", encoding="utf-8"))["round_no"])
