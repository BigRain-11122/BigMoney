"""r634 bm-b closing bookkeeping: state.json, heartbeat, round report line.

Single-writer faces only (bm-b owns state.json / machines/bm-b.json /
logs/iteration-loop/round_reports.md per S5 routing).
R170/R178 law: heartbeat_epoch_utc must be JSON int via int(time.time()).
R262 law: clock_read ISO 8601 with T separator + UTC offset.
"""
import json
import time
from datetime import datetime, timezone, timedelta

import psutil  # type: ignore

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

NOTE = (
    "r634: watch/maintenance round during FUND trio NULLS burn window. "
    "S0 fetch 0-behind (K: invisible this session -> r631 temp sparse-clone recipe, D-19 decisions hash MATCH 4167b784 zero-consume); "
    "S0.5 orders 151/151 double-scan zero-unacked; S1 smoke 47/47; S3 engine alive rc0 idle; "
    "boards: job_list empty, fleet tasks all claimed, W14 park upheld (D-20260930-41 banned face, CEO unfreeze face), "
    "moneyflow IC advisory parked (panel source-blocked since 09-25, bm-a collector lane); "
    "town.html org_chart-v2 alignment queued small task verified ALREADY COMPLETE (11/11 dept buildings per r292/r383, anti-dup no-rebuild); "
    "trio burns healthy V376/Q260/D149 (+8/+10/+11 since r633, zero-dup-k, appends <3min old, daemons PID 34396/57116/30208 alive); "
    "fuse containment pins verified protective (bm-a off-caliber + double-burn keep-blocks, r631 law no-touch); "
    "S6 37 legs 37/37 rc0; S7 registers 4/4 + attrition CLEAN; "
    "10-06 finalize pre-window zero-blocker held (G-SEG monthly-freq chop<50 structural face awaiting GM ruling per bm-a r633 E21; judgment lines zero-touch)"
)

# 1) state.json
state = json.load(open(r"state.json", encoding="utf-8"))
state["round_no"] = 634
state["note"] = NOTE
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at", "last_seen"):
    state[k] = ts
state["round_no_label"] = "round 634 (bm-b)"
json.dump(state, open(r"state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 2) heartbeat fleet/machines/bm-b.json
vm = psutil.virtual_memory()
hb = json.load(open(r"fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["round_no"] = 634
hb["round_no_label"] = "round 634 (bm-b)"
hb["current_task"] = (
    "FUND trio NULLS burn watch (V376/Q260/D149 of 2000 progressing) + 10-06 finalize pre-window zero-blocker watch"
)
hb["verdict"] = (
    "GREEN (smoke 47/47; S6 37/37 rc0; trio burns healthy zero-dup-k appends fresh; "
    "engine alive rc0; W14 park + moneyflow IC = legitimate parked faces; "
    f"RAM {vm.available / 1e9:.2f}GB)"
)
hb["ts"] = ts
hb["updated"] = ts
hb["updated_at"] = ts
hb["cpu_util_pct"] = psutil.cpu_percent(interval=1)
hb["free_ram_gb"] = round(vm.available / 1e9, 2)
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["ram_free_gb"] = hb["free_ram_gb"]
hb["ram_avail_gb"] = hb["free_ram_gb"]
json.dump(hb, open(r"fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify epoch int law + clock T-separator law
chk = json.load(open(r"fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must use T separator (R262)"
print("state+heartbeat written; epoch=", chk["heartbeat_epoch_utc"], "clock=", chk["clock_read"])

# 3) round report line
REPORT = (
    f"{ts} | R634 bm-b (dept:工程:S0零消费+NULLS监护+S6全绿+board实况定谳) | "
    "watermark verdict: GREEN (red=false; lane healthy; next_pick=claimed moneyflow IC advisory, panel source-blocked=bm-a collector lane合法park) | "
    "当前活: FUND 三族 NULLS 烧录在飞 V376/Q260/D149 of 2000（+8/+10/+11 since r633, zero-dup-k, 追加 mtime<3min, 三 daemon 全活 04:38/07:26/11:54 起） | "
    "最近实物: S6 37腿 rc0 再生 faces @20:5x——docs/live_usage/LIVE-2026-10-03.md+docs/daily_report/REPORT-20261003.md+dashboard_status 刷新 + r634 探针组（town 对齐=11/11 部门楼已完备勿重建；W14=合规 park 维持；fuse 钉=防护性全对零碰） | "
    "下个里程碑: 10-06 finalize 前置窗零阻塞维持（V ETA 10-05/06、Q 10-06/07、D 10-08/09；G-SEG 月频族 chop 14<50 结构性面候 GM 裁决= bm-a r633 E21 呈报在案，判线零触碰；VALUE cmd_finalize 崩溃面 r626d/r629 已修复 3/3 pre-flight 绿）| "
    "did: S0 fetch 0 behind（K: 本会话不可见→r631 sparse clone 直读 origin blob 方法复用）+D-19 MATCH 4167b784 零消费; S0.5 orders 151/151 双扫零未回执; S1 smoke 47/47; S3 引擎 rc0 idle; 板查 job_list 空+tasks 全 claimed+inbox 空+pool done362/waiting1(W14)/ready3(NULLS 镜像面); S6 37/37 rc0; S7 注册器 4/4（loop pin=2 no-op/watchdog/pre-commit+pre-push 双爪 LF 一致）+attrition CLEAN+二扫 NONE | "
    "验证: smoke 47/47; S6 37/37 rc0; trio zero-dup-k 追加新鲜; orders 双扫 0 未回执; 引擎 rc0 活 | 本地未达 origin commit 数=0（commit 后 push+fetch+ls-tree 自证）"
)
with open(r"logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(REPORT + "\n")
print("round report appended")
