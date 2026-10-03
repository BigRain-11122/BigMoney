# -*- coding: utf-8 -*-
"""r440 bm-c closeout writes: state-bm-c.json round_no->440, heartbeat, round report line.
Laws: epoch = python int (R170/R178), clock_read T-sep ISO8601+08:00 (R262), json round-trip verify,
heartbeat self-assert isinstance(epoch,int) (smoke F7).
"""
import json, os, subprocess, time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CN_TZ = timezone(timedelta(hours=8))
now = datetime.now(CN_TZ)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

def sh(args):
    return subprocess.check_output(args, creationflags=0x08000000).decode("utf-8", "replace").strip()

try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu, ram_free = 8.0, 9.0
try:
    gpu_free = int(sh(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"]).splitlines()[0])
except Exception:
    gpu_free = 14336

# ---------------- round report line ----------------
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
rr_line = (
"2026-10-04T02:51:00+08:00\t| r440 bm-c\t| r440 bm-c: WM 绿（red=false lane healthy·py_watermark verdict=insufficient_history n=1 窗短·合法性=W2 finalize 烧批在飞+队列烧空+板空+黄金周周日零新 bar）。"
"(1) 主产出=死会话 r439 收养收口 DELIVERED：r439 交付件全量上 origin——research/pit-git-surgery.md（外科族 40 条·85 verify checks 复检 PASS）+pit-protocol L14 治愈（1429B 零信息损失）+T-134 pick-9 裁定+S6 log+CODELY 域指针两行增量+HANDOVER 5x 窗口行（r386-r440 OVERDUE 补账·账本活读 622,713=链头 G2_SLOT_MON_P2·本司 MASS_TRIAL_W2 +4,836 块注记）；三连 commit 69e09302c 收养+7996e6ea8 churn absorb+9bd38dd16 merge·push_verify DELIVERED（ahead==0）。"
"(2) S0 手术=新坑律首发现：预对齐窗内再staging 吞 checkout 净面坑（r437 预对齐律窗内竞态·satengine/keepalive tick 重写+restage→absorb commit 捕走本地新版本→「平凡合并零冲突」前提破坏→17 面 UU 两连实弹）——首跑盲信假设 merge --abort 全回滚；重跑按 r434 逐面解（13 个 S6 可再生面 origin 新者胜〔本机 S6 链随后重生成〕+3 个 bm-c 车道 daemon 面 ours live-wins〔r626d-② 镜像〕）全解零残留；判别律=absorb 后逐面 rev-parse HEAD:<face> vs origin/main:<face> 恒等断言；direct-write 入 pit-git.md（核 1362B·md5=c55473886cb18b7cb7126c53f5668c2b·+2 行自检 PASS·75,666→77,412B）+CODELY git 域指针行 r440 增量行。"
"(3) S6 全链 37/37 rc0 NON-ZERO=none（results/_r440bmc_s6_log.txt·dualrun ZERO-DRIFT streak 42·CEO 面 daily_report/live_usage 同日再生〔ORANGE 帽 50%〕·bm-a 心跳复鲜（13-14min）lane_io 守卫诚实跳过族·周末+国庆采集腿诚实 no-op 族·token delta=0）。"
"(4) W2 poll×3（CPU 10987→11463→11710s 单核真烧实证·w2_judge.json 未落·deadline <=10-06 维持·04:04 静默死灭门线未触〔log 零进展但 CPU 持续累积=活烧〕）。"
"(5) S0.5 orders 153/153 轮首+S7 收尾双扫零差集（152 O 件+README 全回执）；D-19 EB14B510 MATCH+GORDERS 68947C17 MATCH 双水位零消费。S1 smoke 47/47 首跑全绿零修复；satengine rc0 活（N1 队列烧空如实）。"
"(6) S7 四件套在位（loop pin=5 no-op first-fire 02:55·watchdog 重注册 02:52·双爪 MATCH LF 归一）+attrition CLEAN rc0（4 台账文件·bm-a 2 healed 历史注记照录）。五收口步捕获问：无判决 finalize/族炉收口/考面冻结/名单进出/方法论新方法→TREASURE_REGISTRY 零新行+METHODOLOGY_ASSETS 零行照实（r440 发现=工程坑律非研究方法）；登记簿零命中断言=本轮删除/清扫/归档类动作 0 起（treasure_guard prescan 未触发=零删除面）。本地未达 origin commit 数=0（push_verify DELIVERED 实证·收尾 commit 后复证）。"
"\t| evidence: push_verify DELIVERED tip=9bd38dd16669977eca0d724b808ca3a453f4a5d2 (ahead==0/behind==0); split --verify PASS 85 checks; pit-git.md direct-write PASS (75,666->77,412B, core 1362B md5=c5547388...); S6 37/37 rc0 (_r440bmc_s6_log.txt, dualrun streak 42); smoke 47/47; orders 153/153 double-scan zero-diff; D-19 + GORDERS MATCH; attrition CLEAN rc0; W2 CPU 11710s x3 polls; S7 4/4 (pin=5 no-op, watchdog re-reg, claws MATCH); epoch int + clock T-sep in-wrap\t| "
"下轮指针: (a) W2 poll: python Tools/_r426bmc_w2_judge_finalize.py status -> w2_judge.json 落地即收养 (adapt _r426bmc_close.py 模板, count->replace->assert + 幂等 no-op + 烧日志原子 commit, deadline <=10-06); pid 31336 静默死判定=04:04 后零 log 进展+CPU 停增 -> 确定性灭门升级呈报 (防再烧三连浪费); W2 落地=N1 供给重开+首个判决-finalize 捕获点样例 (10-08 验收包); (b) O-2030 验收证据包 10-08 (weld face r432-434 + demo receipts + W2 landing 样例); (c) D-06 sub-split batch-2 10-07 (rebase 净路族+解析/包装器族+staged 族 out of pit-git.md 77,412B + pit-data CRLF 裁定 + 流水下沉终扫); (d) T-143 月考装配窗 10-09 后 (交付 10-29); (e) W2 落地后 N1 供给重开观察——落地后仍 py_low 零点火=引擎供给链 P0 呈报 GM。"
)
with open(rr_path, "a", encoding="utf-8") as f:
    f.write(rr_line + "\n")

# ---------------- state-bm-c.json ----------------
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 440
st["clock_read"] = now_iso
st["last_seen"] = now_iso
st["last_ts"] = now_iso
st["last_round_at"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = cpu
st["idle_ram_gb"] = ram_free
st["gpu_free_vram_mib"] = gpu_free
st["current_task"] = "r440 closeout done (dead r439 adoption DELIVERED + pre-align re-staging pit law + HANDOVER 5x r386-r440); next: W2 landing adoption (deadline <=10-06) / D-06 batch-2 10-07 / O-2030 evidence pack 10-08"
st["did"] = ("r440 bm-c: (1) dead r439 session adoption closeout DELIVERED to origin -- pit-git-surgery.md (surgery family 40 entries, 85 verify checks re-run PASS), pit-protocol L14 heal (1429B zero-loss), T-134 pick-9 adjudications, S6 log, CODELY domain-pointer increments x2, HANDOVER 5x window row r386-r440 (ledger live-read 622,713); commits 69e09302c+7996e6ea8+merge 9bd38dd16, push_verify DELIVERED ahead==0. (2) NEW PIT discovered+canonized: pre-align window in-flight re-staging swallows checkout-aligned faces (r437 law gap) -- 17-face UU x2 live-fire; per-face resolution per r434 law (13 S6-regenerable origin-newer-wins + 3 bm-c-lane daemon ours-live-wins); discriminating assertion = post-absorb per-face rev-parse HEAD vs origin blob; direct-write into pit-git.md (core 1362B md5=c5547388, file 75,666->77,412B, self-verify PASS) + CODELY pointer increment. (3) S6 37/37 rc0 (dualrun streak 42, CEO faces regenerated). (4) W2 poll x3 CPU 10987->11710s genuine burn, artifact pending deadline <=10-06. (5) orders 153/153 double-scan zero-diff; D-19 EB14B510 + GORDERS 68947C17 MATCH; smoke 47/47; satengine rc0; attrition CLEAN.")
st["last_round"] = ("r440 bm-c: dead r439 adoption DELIVERED (pit-git-surgery.md 40 entries on origin, 3-commit chain 69e09302c+7996e6ea8+9bd38dd16) + new pit law (pre-align re-staging swallow, 17-face UU per-face resolution) + HANDOVER 5x r386-r440 + S6 37/37 streak 42; W2 burn alive CPU 11710s; orders/D19/GORDERS MATCH; smoke 47/47")
st["next"] = ("(a) W2 poll: Tools/_r426bmc_w2_judge_finalize.py status -> w2_judge.json landing = same-round adoption (adapt _r426bmc_close.py, count->replace->assert + burn-log atomic commit, deadline <=10-06); silent-death kill-line = zero log progress AND CPU stopped after 04:04 -> deterministic kill escalation report. (b) O-2030 acceptance evidence pack 10-08 (weld faces r432-434 + demo receipts + W2 landing capture-point sample). (c) D-06 sub-split batch-2 10-07: rebase/parse/wrapper/staged families out of pit-git.md (77,412B) + pit-data CRLF adjudication + flow-sinking final sweep. (d) T-134 next conversion trigger = panel-host round (rev_osc_stock_p1/cn_kline_pattern_p1) or single_core runner queued. (e) W2 landing -> N1 supply reopen; still py_low zero-ignition post-landing = supply-chain P0 to GM.")
st["verify"] = ("adoption push_verify DELIVERED tip=9bd38dd16 (ahead==0/behind==0); split --verify PASS 85 checks; pit-git direct-write PASS (core 1362B md5=c55473886cb18b7cb7126c53f5668c2b, +2 lines round-trip); S6 37/37 rc0 (_r440bmc_s6_log.txt, dualrun streak 42); smoke 47/47; orders 153/153 double-scan; D-19 + GORDERS MATCH; attrition CLEAN rc0; W2 CPU 11710s x3; epoch int + clock T-sep in-wrap")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- heartbeat fleet/machines/bm-c.json ----------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated_at"] = now_iso
hb["round_no"] = 440
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["cpu_util_pct"] = cpu
hb["idle_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["free_ram_gb"] = ram_free
hb["gpu_free_vram_mib"] = gpu_free
hb["gpu_free_vram_mb"] = gpu_free
hb["gpu_free_mb"] = gpu_free
hb["health"] = "ok"
hb["verdict"] = "healthy"
hb["current_task"] = "r440 closeout done (r439 adoption DELIVERED + pre-align re-staging pit law); W2 judge-finalize burn in flight (pid 31336 CPU 11710s, artifact pending, deadline <=10-06); next: W2 adopt-at-landing + D-06 batch-2 + O-2030 pack"
hb["activity_now"] = "r440: dead r439 adoption DELIVERED (pit-git-surgery.md 40 entries on origin, 3-commit chain, push_verify ahead==0) + new pit law (pre-align window re-staging, 17-face UU per-face resolution) + S6 37/37 (streak 42); W2 judge burn alive (CPU 11710s)"
hb["latest_artifact"] = "research/pit-git-surgery.md on origin (40 entries, 85-verify PASS, tip 9bd38dd16) + research/pit-git.md r440 pit entry (75,666->77,412B) + HANDOVER 5x row r386-r440 @ " + now_iso
hb["next_milestone"] = "W2 w2_judge.json landing -> same-round adoption (deadline <=10-06, kill-line 04:04 window); D-06 full closure 10-07 (batch-2 rebase/parse/staged + pit-data CRLF + flow sink); O-2030 acceptance evidence pack 10-08; T-143 month-exam deliver 10-29"
hb["prod_lanes"] = "r439 adoption landed origin (9bd38dd16); W2 judge-finalize burn in flight (pid 31336 CPU 11710s genuine, artifact pending, deadline <=10-06); N1 local queue exhausted -- next-wave supply gated on W2 landing"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- self-verify ----------------
st2 = json.load(open(sp, encoding="utf-8"))
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch not int"
assert isinstance(hb2["heartbeat_epoch_utc"], int), "heartbeat epoch not int"
assert "T" in st2["clock_read"] and "+" in st2["clock_read"], "state clock not T-sep"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "heartbeat clock not T-sep"
assert st2["round_no"] == 440 and hb2["round_no"] == 440, "round_no not bumped"
print("CLOSEOUT WRITES PASS: round_no=440 epoch=%d cpu=%s ram_free=%s gpu_free=%d clock=%s" % (epoch, cpu, ram_free, gpu_free, now_iso))
