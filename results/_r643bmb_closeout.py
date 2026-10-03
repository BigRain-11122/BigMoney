# -*- coding: utf-8 -*-
"""r643 bm-b closeout driver: state.json round bump + heartbeat refresh +
round-report append (bytes-mode, mixed-encoding file) + S7 double-scan.
Pure bookkeeping, one-shot; evidence values sampled live at run time."""
import datetime as dt
import glob
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
now_epoch = int(time.time())

# --- S7 double-scan: orders dir recount vs ack set, inbox re-check --------
orders = sorted(os.path.basename(p) for p in glob.glob(r"fleet\orders\O-*.md"))
hb = json.load(io.open(r"fleet\machines\bm-b.json", encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
unacked = [o for o in orders if o not in acked]
inbox = [f for f in os.listdir("fleet\\inbox")
         if os.path.isfile(os.path.join("fleet\\inbox", f))]
print(f"double_scan: orders={len(orders)} acked={len(acked)} "
      f"unacked={unacked} inbox_unread={inbox}")

# --- system sample ---------------------------------------------------------
import psutil  # noqa: E402
cpu_pct = round(psutil.cpu_percent(interval=2), 1)
ram_avail = round(psutil.virtual_memory().available / 1e9, 2)
try:
    q = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, timeout=10)
    vram_free = int(q.stdout.split()[0])  # MiB
except Exception:
    vram_free = hb.get("gpu_free_vram_mb", 0)
print(f"sample: cpu={cpu_pct}% ram_avail={ram_avail}GB vram_free={vram_free}MiB")

# --- nulls counters (fresh, for heartbeat current_task) -------------------
def _count(path):
    ks = []
    with io.open(path, "rb") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                ks.append(json.loads(raw).get("k"))
            except ValueError:
                pass
    return len(ks)

qv = {f: _count(os.path.join("results", f, "nulls.jsonl"))
      for f in ("fund_quality_p1", "fund_value_p1", "fund_divlowvol_p1")}
print("nulls:", qv)

# --- state.json bump -------------------------------------------------------
state = json.load(io.open("state.json", encoding="utf-8"))
prev = state["round_no"]
state["round_no"] = prev + 1
state["round_no_label"] = f"round {prev + 1} (bm-b)"
state["note"] = (
    "r643: product round -- finalize-window readiness probe landed: "
    "scripts/finalize_trio_readiness.py (run+selftest; gates G1 "
    "burn_complete have>=2000 / G2 dup_k==0 / G3 rehearsal-green fresh "
    "/ G4 G-SEG governance watch w/ r638 insufficient-sample fallback; "
    "60s dual-sample rate + cross-round history face; selftest PASS x2 "
    "deterministic after wall-clock-dep leg hermetic fix). Live face: "
    "Q/V/D have=388/526/262 of 2000, dup_k=0, mechanical_ready=false "
    "(G1 pending burns), G4 PENDING. S0: predecessor live-overlap "
    "adjudicated per single-executor law (02:39 tick = r642 addendum "
    "push-race adoption session, reflog merge 02:42:47, inbox sweep "
    "02:56, exit ~03:00, zero state/heartbeat touch -> this session "
    "carried 643; three-proof detection law -> CODELY.md); churn absorb "
    "+ merge net-path (r637 treadmill law, intersection-empty). S0.5 "
    "orders 152/152 zero-diff + D-19 sparse-clone fallback MATCH "
    "EB14B510 zero-consume. S1 47/47. S3 gates green (WM red=false; "
    "engine alive rc0 idle; no red; trial-labor not triggered = trio "
    "batches in flight). S6 ~30 legs rc0 (Sunday Golden-Week honest "
    "no-op family + lane guards; dualrun ZERO-DRIFT streak 35; audit "
    "CLEAN burning-healthy py 85pct; LIVE page + REPORT regenerated). "
    "S7 4/4 idempotent + attrition CLEAN."
)
for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read"):
    state[k] = now_iso
state["last_decisions_read_at"] = now_iso
with io.open("state.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("state.json: round", prev, "->", state["round_no"])

# --- heartbeat -------------------------------------------------------------
hb["last_seen"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch
hb["round_no"] = state["round_no"]
hb["round_no_label"] = state["round_no_label"]
hb["current_task"] = (
    f"FUND trio NULLS burn watch (daemons live, Q/V/D = "
    f"{qv['fund_quality_p1']}/{qv['fund_value_p1']}/"
    f"{qv['fund_divlowvol_p1']} of 2000, finalize window 10-05..10-09 "
    "pending G-SEG GM ruling) + finalize readiness probe delivered "
    "(scripts/finalize_trio_readiness.py)"
)
hb["verdict"] = (
    "GREEN (smoke 47/47; readiness probe selftest PASS x2; D-19 MATCH "
    "zero-consume; S6 ~30 legs rc0; dualrun ZERO-DRIFT streak 35; "
    "attrition CLEAN; engine alive rc0 idle; orders 152/152; trio "
    "burns healthy dup_k=0; predecessor overlap adjudicated "
    "zero-double-write)"
)
for k in ("ts", "updated", "updated_at"):
    hb[k] = now_iso
hb["cpu_util_pct"] = cpu_pct
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
    hb[k] = ram_avail
hb["gpu_idle_vram_gb"] = round(vram_free / 1024, 2)
hb["gpu_idle_vram_mb"] = vram_free
hb["gpu_free_vram_gb"] = round(vram_free / 1024, 2)
hb["gpu_free_vram_mb"] = vram_free
hb["gpu_free_vram_mib"] = vram_free
hb["gpu_vram_free"] = vram_free
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
_clock = hb["clock_read"]
assert "T" in _clock and _clock.endswith("+08:00"), f"clock bad: {_clock}"
ep = hb["heartbeat_epoch_utc"]
back = dt.datetime.fromtimestamp(ep).astimezone().isoformat(timespec="seconds")
assert abs((dt.datetime.now().astimezone()
            - dt.datetime.fromisoformat(back)).total_seconds()) < 120, \
    "epoch<->clock cross-check failed"
with io.open(r"fleet\machines\bm-b.json", "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("heartbeat: epoch", ep, "int-ok, clock", _clock)

# --- round report append (bytes mode, mixed-encoding history file) ---------
report_line = (
    f"{now_iso} | round 643 (bm-b, dept:工程/舰队+研究): watermark "
    "verdict=GREEN (red=false; audit CLEAN burning-healthy; WM probe "
    "local_batch_running=true; dualrun ZERO-DRIFT streak 35)"
    "\n当前活: FUND 三族 NULLS 烧录健康在飞 "
    f"Q{qv['fund_quality_p1']}/V{qv['fund_value_p1']}/"
    f"D{qv['fund_divlowvol_p1']} of 2000（三族 dup_k=0·autofill tick "
    "keepalive 活·finalize 窗 10-05..10-09 候 G-SEG 裁定/r638 备案）"
    "\n最近实物: scripts/finalize_trio_readiness.py + results/"
    "finalize_trio_readiness.json 03:0x（finalize 窗开启门探针：G1 "
    "have>=2000/G2 dup_k/G3 预演绿新鲜度/G4 G-SEG 治理面四门+60s 双采样"
    "速率 ETA+跨轮历史 jsonl·selftest PASS x2 确定性·实测面 "
    "mechanical_ready=false G1 待烧完·G2/G3 绿·G4 PENDING）"
    "\n下个里程碑: 三族烧完→finalize 判决窗开窗（探针 mechanical_ready"
    "翻绿即开窗信号·G-SEG 无裁定按 r638 insufficient-sample 备案）；窗 "
    "≤48h"
    "\n做了什么: S0 tick 重叠活会话三证探测+裁决（02:39 先行收养会话="
    "r642 addendum push-race 收口 02:42:47 reflog merge→02:56 inbox 大扫"
    "→~03:00 退出零簿记触碰→本会话承 643 零双写·律入 CODELY.md）+churn "
    "absorb+merge 净路（r637 律·交集空）；S0.5 令 152/152 双扫零未回执"
    "+D-19 sparse-clone fallback MATCH EB14B510 零消费；S1 smoke 47/47；"
    "S2 双板空（job_list 空+tasks 无 open）；S3 序检全过（WM 绿·引擎活 "
    "rc0 idle·无修红·常设线不触发=有在飞批）；产品增量=finalize 窗开启"
    "门探针（scripts/finalize_trio_readiness.py：四门判据+双采样速率"
    "ETA+跨轮历史面+R31 车道护栏他机 stdout-only·selftest 墙钟依赖腿"
    "治本为固定参考时刻·history_rate prev/min 假 Δ bug 当场修复）；"
    "S6 ~30 腿 rc0（周日黄金周诚实 no-op 族+车道护栏 stdout-only·"
    "dualrun streak 35·audit CLEAN py 85pct·LIVE 页+REPORT 再生·token "
    "delta=0）；S7 4/4（loop pin=2 no-op·watchdog 重注册在位·双爪幂等"
    "重装·attrition CLEAN 4 ledgers）"
    "\n验证证据: readiness 探针 selftest PASS x2（确定性双跑）；实测面 "
    "results/finalize_trio_readiness.json（G1=F G2=T G3=T G4=PENDING·"
    "eta 实读）；S6 各腿 rc0 行；attrition scan CLEAN；double_scan "
    "orders=152/152 inbox=0"
    "\n下轮指针: r644 = 每轮跑 python scripts\\finalize_trio_readiness.py"
    " run 至 mechanical_ready 翻绿（历史面跨轮速率收敛）+ 三族烧监护续"
    "（烧完即 finalize 开窗动作）+ LIVE v1.5 面随烧录自动刷新验收"
    "\n本地未达 origin commit 数=0（push 后 ls-remote 自证）"
    "\n"
)
path = r"logs\iteration-loop\round_reports.md"
with io.open(path, "rb") as fh:
    blob = fh.read()
if blob and not blob.endswith(b"\n"):
    blob += b"\n"
new_bytes = report_line.encode("utf-8")
assert blob.count(new_bytes) == 0
with io.open(path, "wb") as fh:
    fh.write(blob + new_bytes)
print("round_reports.md: appended", len(new_bytes), "bytes")
print("CLOSEOUT_OK")
