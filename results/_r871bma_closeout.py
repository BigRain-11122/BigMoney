# -*- coding: utf-8 -*-
"""r871 bm-a closeout: state round_no, round-report row, heartbeat refresh.
Multi-writer shared files -> fresh in-file read-modify-write (r806 law)."""
import json
import time
import datetime

import psutil

NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S") + NOW.strftime("%z")[:3] + ":" \
    + NOW.strftime("%z")[3:]
EPOCH = int(time.time())

# --- state round_no 871 -> 872 -------------------------------------------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = int(st.get("round_no", 871)) + 1
json.dump(st, open(sp, "w", encoding="utf-8", newline=""), indent=1,
          ensure_ascii=False)
assert st["round_no"] == 872, st["round_no"]

# --- round report row ------------------------------------------------------
ROW = (
    TS + " | r871 bm-a (dept:研究-REGIME-5验证+牛市供给) | WM-VERDICT: 绿 "
    "(red=false lane=healthy; py_low_board_clear 板清合法闲; supply_gap 旗"
    "持续=W184 链在制应答面) | 当前活=T-177 slice-2 REGIME5-VALIDATION-P1 "
    "烧批落地+leg-2 供给扫描开动; 最近实物=results/regime5_validation/"
    "REGIME5-VALIDATION-2026-09-30.json (08:45, 1,010 cells, 账头 808,918+"
    "1,010=809,928) + scripts/regime5_validation.py (selftest 16/16) + "
    "research/REGIME5_BULL_SUPPLY_SCAN.md (leg-2 种子件); 下个里程碑=T-177 "
    "leg-2 F1(ETF动量轮动)×CTA_P1 相关性探针+预注册起草 (窗≤48h·10-10 前)"
    " + W184 链供池烧录 | did: S0-1 孤儿面=0 (10 py faces 只读报告); S0 净树"
    "先收 live faces 再 rebase (bm-b r746 同窗 5 commit·快进 push); S0.5 "
    "orders 全量差集 51/51 acked (双扫); S1 smoke 49/49; S2 板空+水位绿+"
    "idle 未达档 (VRAM 5.28<6GB); S3 验证批主门=BULL/BEAR 方向性三面判负"
    "诚实照报 (BULL d+9.94bp n=59 p=0.92 CI 跨 0 t=0.36; BEAR d-0.25bp≈0 "
    "p=0.99——深熊 t+1 反弹吞噬漂移·raw +0.72bp 同判=非防抖伪影; 结构信号"
    "在: CHOP -1.87bp p=0.0060 显著/GRIND +18.3bp) · N_CONF*=1 argmin L 旗标"
    "→bm-c 矩阵修订窗 · Leg C net(N*)=+7,180bp PASS (|d| 路由值读法·符号直"
    "和=分区恒等零退化读法已拒并 audit 披露) · 锚面 6/6 EXACT D2 锁盒 · 种子"
    "94_100 spawn(1001) 零顺爬 · E47 方法论捕获+TREASURE 行+attrition 行 · "
    "修订窗律=多视界 t+5/t+20 另批预注册 (零阈值改动零重跑); S6 36/36 rc0 "
    "(dualrun streak 51 零漂移; 采集器盘前合法 no-op; moneyflow rank pass+"
    "AH 面分离 spawn; scorecard 38.6s/战报/CEO 页/总控面板再生; token 今日 "
    "0); S7 quartet 幂等 (loop pin8 no-op/watchdog 重装/双爪 LF 归一装) +"
    " attrition CLEAN + state r872 + 心跳 epoch-int 自证; not-at-origin=0"
    " | 下轮指针: ①T-177 leg-2 F1×CTA_P1 相关性探针 ②F1 预注册起草 (D6 同"
    "族门+出场轴显式门) ③W184 链 seat 烧录消费 ④10-08 15:30 后新 bar 窗 "
    "live.paper+纸盘族腿+CTA_P1 试用期首读数\n"
)
rp = "logs/iteration-loop/round_reports-bm-a.md"
src = open(rp, encoding="utf-8").read()
if not src.endswith("\n"):
    src += "\n"
open(rp, "w", encoding="utf-8", newline="").write(src + ROW)

# --- heartbeat -------------------------------------------------------------
vm = psutil.virtual_memory()
free_gb = round(vm.available / 1024 ** 3, 1)
free_mb = int(vm.available / 1024 ** 2)
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["clock_read"] = TS
h["ts"] = TS
h["last_seen"] = TS
h["cpu_pct"] = cpu_pct
h["cpu_util_pct"] = cpu_pct
h["cpu_load_pct"] = cpu_pct
h["free_ram_gb"] = free_gb
h["ram_free_gb"] = free_gb
h["idle_ram_gb"] = free_gb
h["idle_ram_mb"] = free_mb
h["heartbeat_epoch_utc"] = EPOCH
h["last_heartbeat_epoch_utc"] = EPOCH
h["verdict"] = ("green (T-177 slice-2 REGIME5-VALIDATION-P1 burned same-"
                "round: main gate BULL/BEAR directional three-face FAIL "
                "honest, structural signals exist CHOP/GRIND; N_CONF*=1 "
                "flag to bm-c matrix amendment window; Leg C net PASS; "
                "watermark red=false lane healthy; py_low_board_clear "
                "legal idle; supply_gap flag = W184 chain in-motion)")
h["current_task"] = ("T-2026-10-08-177 leg-2: bull-offense supply scan "
                     "(F1 ETF momentum rotation x CTA_P1 corr probe + "
                     "prereg draft, <=10-10)")
h["last_action"] = ("r871: REGIME5-VALIDATION-P1 burned 40.2s (1,010 cells, "
                    "ledger 809,928, anchor 6/6 EXACT, seed 94_100 "
                    "spawn(1001)); main gate directional FAIL honest "
                    "(BEAR t+1 bounce eats drift, raw same-verdict); "
                    "N_CONF*=1 flag; Leg C net +7,180bp PASS; E47 "
                    "methodology capture; leg-2 supply scan seed landed "
                    "(F1/F2/F3 with external citations)")
h["idle_rounds"] = 0
h["agenda_starved"] = False
json.dump(h, open(hp, "w", encoding="utf-8", newline=""), indent=1,
          ensure_ascii=False)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601"
print("closeout ok: state r%d, report row, heartbeat epoch=%d, ram_free=%sGB, cpu=%s%%"
      % (st["round_no"], chk["heartbeat_epoch_utc"], free_gb, cpu_pct))
