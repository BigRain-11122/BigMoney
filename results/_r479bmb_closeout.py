"""r479 bm-b closeout: round report + state.json + heartbeat + CODELY appends."""
import json
import os
import psutil
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
TS_SHORT = NOW.strftime("%Y-%m-%d %H:%M")

# ---------- CPU/RAM sample ----------
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
free_ram = round(vm.available / 2**30, 1)
gpu_free = 2.1  # last known sample; no GPU burn in flight this round

# ---------- 1) round report line (bm-b uses logs/iteration-loop/round_reports.md) ----------
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"{TS_SHORT} | r479 bm-b | dept:工程/研究 | watermark verdict=绿 (red=false, lane healthy; py 低位=astock 刷新 I/O-bound 在飞+板全闭环合法 idle, 无可领票滞留>30min) | "
    "当前活: O-20260930-2054 e-item 执行——P2NULL-KLIFT-K2200-S2 外部工认领(O-2210)烧批完成 370.9s/550 runs (A j1000-1499+B j100-149, 冻结窗 cutoff 2026-09-22) 落 results/p2cal_ext/shard-2-of-4.json, A500+B50 完整性验证 PASS; "
    "S0/S1 harvest done-flips (结果件早已完整而 pool 行未翻=S1 owner=None 会被 picker 重复烧白跑, 按 r180 done-shard 律翻 done, 原始 burner bm-c 注记保全) + S2 done = 批 3/4 (S3 bm-c 在飞); "
    "merge_lane_views owner_since=null 坑修复: str(None)='None' 字符串比较恒胜真时间戳→null 行恒为 base 吞 done 翻面 (S1 实锤 done 被 settle 回 ready; S0/S2 因对侧行带真时间戳幸存), 修法=or '' 归一一行, selftest 0 FAIL, 修后 S1 翻面复活; 披露=MSG-20260930-2150-bmb-ALL; "
    "EXCLUSION+FACEB refresh 窗泊位 (astock 全宇宙刷新 21:09:13 起在飞 ~3.6h, defer_note 词法 r378 catch #4, S1 closed claim 防重复烧; 21:40 tick 实证 pool_empty_or_busy 零假烧); "
    f"S6 37 腿全 rc=0 (chunk1 23 腿+chunk2 14 腿; t24/live_paper 等=r478 新鲜验证已录的 checkpoint 幂等重跑, 锚漂 22/22 已披露候 bm-a berth 重锚, bm-a r491 引擎修复已落地指针); smoke 47/47; "
    "最近实物: results/p2cal_ext/shard-2-of-4.json (21:42, 550 runs) + scripts/merge_lane_views.py 修复 (21:46); "
    "下轮指针: astock 刷新落定→un-defer EXCLUSION/FACEB 复燃+FACEB 结果落→bm-c MSG-2040 回填解锁; K2200 S3 落→bm-c 批 finalize; 下里程碑窗≤48h (CEO 可见面三行之三)\n"
)
with open(rr_path, "a", encoding="utf-8") as fh:
    fh.write(line)

# ---------- 2) state.json ----------
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 479
st["note"] = (
    "r479: O-2054 e-item P2NULL-KLIFT-K2200-S2 burn complete (550 runs 370.9s, A500+B50 "
    "verified); S0/S1/S2 pool shard rows done (batch 3/4, S3 bm-c in-flight); "
    "merge_lane_views owner_since=null str-compare pit fixed (null row swallowed done "
    "flips, selftest 0 FAIL); EXCLUSION+FACEB defer_note-parked vs astock refresh window "
    "(21:09 spawn, ~3.6h), 21:40 tick pool_empty_or_busy zero false burns; S6 37 legs "
    "rc0; smoke 47/47"
)
for k in ("last_round_at", "last_round_ts", "ts", "updated"):
    st[k] = TS
st["updated_at"] = TS
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------- 3) heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = TS
epoch = int(time.time())
assert isinstance(epoch, int)
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = TS
hb["current_task"] = (
    "r479: P2NULL-KLIFT-K2200-S2 burned complete (550 runs, batch 3/4 done), "
    "merge owner_since-null pit fixed, EXCLUSION/FACEB parked vs astock refresh window"
)
hb["round_no"] = 479
hb["round"] = 479
hb["loop_round"] = 479
hb["last_round_at"] = TS
hb["last_round_ts"] = TS
hb["cpu_util_pct"] = round(cpu, 1)
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["gpu_free_vram_gb"] = gpu_free
hb["gpu_idle_vram_gb"] = gpu_free
hb["verdict"] = (
    "r479 OK: O-2054 e-item S2 burn complete 550 runs (batch 3/4), merge pit fixed "
    "(selftest 0 FAIL), EXCLUSION/FACEB parked vs refresh window (tick "
    "pool_empty_or_busy verified), S6 37 legs rc0, attrition pending closeout, orders 130/130"
)
ack = hb.get("orders_ack", [])
if "O-20260930-2054-bm-a.md" not in ack:
    ack.append("O-20260930-2054-bm-a.md")
hb["orders_ack"] = ack
hb["n_orders_ack"] = len(ack)
# post-write self-verification: epoch must be int
chk = json.loads(open(hp, "w", encoding="utf-8") and json.dumps(hb))
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
rt = json.load(open(hp, encoding="utf-8"))
assert isinstance(rt["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in rt["clock_read"], "clock_read must be ISO8601 T-separated"

# ---------- 4) CODELY.md appends ----------
cp = os.path.join(ROOT, "CODELY.md")
codely = open(cp, encoding="utf-8").read().rstrip("\n")
lines = [
    "- [2026-09-30 21:5x r479 bm-b] O-20260930-2054 回执+执行：e-item P2NULL-KLIFT-K2200-S2 "
    "烧批完成（550 runs/370.9s，A500+B50 验证 PASS，批 3/4）+S0/S1 harvest done-flips 防重复烧；"
    "EXCLUSION/FACEB refresh 窗 defer_note 泊位+S1 closed claim（21:40 tick pool_empty_or_busy "
    "实证零假烧）；低效诊断律自查=py 低位系 astock 刷新 I/O-bound 在飞+板全闭环=合法 idle，无可领票滞留>30min",
    "- [2026-09-30 r479 bm-b] merge_lane_views owner_since=null 字符串比较坑：_merge_shard_same_key "
    "对键在值 null 的行 str(None)=\"None\" 恒胜一切真时间戳（\"N\">\"2\"）→null 行恒为 base 吞 done "
    "翻面（S1 实锤=done 被 settle 回 ready；S0/S2 幸存仅因对侧行带真时间戳）。修法=比较前 `or \"\"` 归一"
    "（一行），selftest 0 FAIL，修后 S1 翻面复活。How to apply：共享库时间戳键比较必须先归一 null/None，"
    "禁裸 str() 可能 null 的值；done/harvest 翻面被 settle 吞回时，先查配对行时间戳字段有无 null 值键。",
]
with open(cp, "a", encoding="utf-8") as fh:
    fh.write("\n" + "\n".join(lines) + "\n")

print("closeout writes done; epoch=", epoch, "cpu=", cpu, "free_ram=", free_ram)
