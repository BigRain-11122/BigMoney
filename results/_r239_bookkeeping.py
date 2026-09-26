# -*- coding: utf-8 -*-
"""r239 S7 bookkeeping: state.json, round report line, heartbeat, DECISIONS
append (D-04), CODELY.md memory line. All file-based python (r230 GBK law)."""
import io
import json
import os
import time
from datetime import datetime

NOW = datetime.now()
TS = NOW.strftime("%Y-%m-%d %H:%M")
ISO = NOW.isoformat(timespec="seconds")

# ---------------------------------------------------------------- state.json
sp = "logs/iteration-loop/state.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 239
st["did"] = ("r239: T-74+T-75 CEO-immediate takeover claim-and-start same round (bm-a heartbeat stale "
             "09:23:45>20min, plate full T-76+T-70) -- T-75 FULL: daily_report.py 4-face battle report "
             "(run/force/selftest, selftest PASS, 55 accounts) + firm/DECISIONS.md canon D-01..04 + first "
             "report REPORT-20260926.md (force disclosed) + S6 chain wiring + scorecard pointer; T-74 "
             "s0+s1: MARKET_CLOCK_COMBO.md canonical tree + s2 prereg frozen (Arm-A regime-only, heat "
             "composite unfrozen gate >=60td) + CALL-20260926.md market call (ORANGE ladder 50%)")
st["verdict"] = "GREEN"
st["next"] = ("T-74 s2 runner->selftest->pool submit + SW name-audit + fund-event guard; T-75 Monday 15:45 "
              "first auto-fire verify; watchdog red-face flip confirm; GPU-FACTOR-LANE-PROOF waits bm-a "
              "flip; 09-28 Monday new-bar full chain; 10-01 monthly three-suite + v3 date gate")
st["last_round_ts"] = ISO
st["last_result"] = "exit 0 all S6 legs (weekend no-op legal; no new bar -> paper chain legal skip; smoke 25/25 x2)"
st["current_task"] = "T-75 done + T-74 s0/s1 delivered (s2 next slice); T-74/T-75 takeover closed same round"
st["last_tick"] = NOW.strftime("%H:%M")
st["updated_at"] = ISO
st["last_seen"] = TS
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json -> round 239")

# ------------------------------------------------------------ round report line
RR = "2026-09-26 {ts} | r239 bm-b (dept:总经办·工程·组合与资金部·T-74/T-75 CEO 即时接管) | WM-VERDICT: 轮首红 runnable-work-idle-low-cpu@10:00:21（点名面=两张 open CEO 即时票 T-74/T-75 滞留 3 周期无人认领）→ 本轮正解=接管闭环：bm-a 心跳 09:23:45 停滞>20min+在制盘满+板无认领 → bm-b 按 O-1730 即时律认领双票 commit 2fab3637 开工同轮；轮中 probe 10:07 py_low_board_clear=合法白名单（板全闭环+bandit 0+池 bm-b 道 0 ready；GPU-FACTOR-LANE-PROOF waiting bm-a 翻面=物理依赖注记）；watchdog 下 tick 自动翻红面 | did: S0 stash-pull-pop FF 零冲突；S0.5 双扫 78/78 全对账零未回执+decisions.md 缺位零动作；S1 smoke 25/25；T-75 全交付（daily_report.py 四面战报 selftest PASS+55 账户族（_summary schema-foreign 剔除 r157 律）+DECISIONS.md 正典 4 条+首份战报 force 通道披露+S6 链 byte 精准插腿 LF 保真+scorecard 指针行+run 守卫 no-op 验证+smoke 零回归）；T-74 s0+s1（正典六层树+s2 预注册冻结：Arm-A 纯 v3 四格、热度复合未冻结裁定≥60td 观察门、N_eff=8、G1'v2/G2v2 共享库、诚实窗口板块面 2020 起+政体面深史；CALL-20260926.md：ORANGE 阶梯 50% 防守 sleeve+Top-3 倾斜 512800/159985/513100+基金事件畸变守卫旗 512480/159995 r60=-62% 级）；S6 链全绿（compute_audit FLAG pool_starvation=池空注记、六车道 no-op 诚实、b_layer 5222 码全门过、无新 bar paper 链合法跳） | 证据: smoke 25/25×2、daily_report selftest PASS×3、run no-op、force 首报 55 账户、schtasks 双任务在位（Loop 运行中/Watchdog 10:30 就绪）、commit 2fab3637 双票锁 | 下轮: T-74 s2 runner+池提交+SW 核名+基金事件守卫腿；T-75 周一 15:45 首自动 fire；watchdog 红面翻绿确认；09-28 周一新 bar 全链；10-01 月度三件套+v3 日期门\n"
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(RR.format(ts=NOW.strftime("%H:%M")))
print("round_reports.md appended")

# ------------------------------------------------------------------ heartbeat
hp = "fleet/machines/bm-b.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = ISO
hb["current_task"] = ("r239 done: T-74+T-75 CEO-immediate takeover (bm-a stale>20min) -- T-75 FULL delivery "
                      "(daily_report 4-face battle report live + DECISIONS canon D-01..04 + S6 wiring + first "
                      "report same-day disclosed); T-74 s0 tree-frozen + s1 market call delivered, s2 batch next")
hb["round_no"] = 239
hb["verdict"] = ("py_low_board_clear = legal idle whitelist post-takeover (board fully claimed/delivered this "
                 "round; bandit 0; pool 0 ready bm-b lanes; GPU-FACTOR-LANE-PROOF waits bm-a flip = physical dep; "
                 "round-start red lane runnable-work-idle-low-cpu RESOLVED by same-round claim-and-deliver, "
                 "watchdog flips red face next tick")
import psutil  # noqa: present per prior heartbeats
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
hb["total_ram_gb"] = round(psutil.virtual_memory().total / 1e9, 1)
hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
mem = psutil.virtual_memory()
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["idle_ram_mb"] = int(mem.available / 1e6)
gpu_mb = 0
try:
    for ln in os.popen("nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits").read().splitlines():
        gpu_mb = max(gpu_mb, int(ln.strip()))
except Exception:
    pass
hb["gpu_free_vram_gb"] = round(gpu_mb / 1024, 1)
hb["gpu_free_vram_mb"] = gpu_mb
hb["gpu_idle_vram_mb"] = gpu_mb
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat bm-b written, epoch int verified:", chk["heartbeat_epoch_utc"])

# ------------------------------------------------------------ DECISIONS D-04
dp = "firm/DECISIONS.md"
line = ("- [D-20260926-04] T-74 热度复合规则暂缓冻结（≥60 交易日并发史观察门后才准冻结数值），运转臂=Arm-A 纯 v3 四态 "
        "— why: 人气榜仅 3 份快照+LHB 镜像面+moneyflow 首拉在飞=阈值零实证基础，禁编数（实战出真知元律） — "
        "evidence: research/MARKET_CLOCK_COMBO.md §2/§3 + docs/market_call/CALL-20260926.md\n")
with io.open(dp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("DECISIONS D-04 appended")

# ------------------------------------------------------------- CODELY memory
cp = "CODELY.md"
mem_line = ("- [2026-09-26 10:2x] 坑律/数据面（bm-b r239·T-74 s1 板块动量板·L2 信号面数据形状）：**ETF 价格面动量读数受基金份额折算/拆分事件畸变——512480/159995 r60=−62% 级非市场真跌（core48 板块谱 40 面实勘）**；动量/轮动面消费前必须加基金事件守卫腿（折算跳变检测），核名清单禁臆测（代码面呈现，s2 prep 首步核名）；连带律：CEO 即时票接管三征判读=心跳停滞>20min+他机末 commit 停滞+板无认领（commit --all 查 T-75 无交付件=ticket 创建 commit ≠ 工作交付 commit，禁混读）。指针=research/MARKET_CLOCK_COMBO.md §2+docs/market_call/CALL-20260926.md 诚实边界+commit 2fab3637\n")
with io.open(cp, "a", encoding="utf-8", newline="") as f:
    f.write(mem_line)
print("CODELY.md memory line appended")
