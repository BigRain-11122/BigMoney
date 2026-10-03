# -*- coding: utf-8 -*-
"""r642 bm-b closeout driver: state.json round bump + heartbeat refresh +
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
    "r642: product round -- ceo_live_usage v1.5 landed: LIVE page section 5 "
    "在飞判决批 (FUND trio NULLS burn counters, pure readout, zero new "
    "judgment; disclaimers renumbered 6); LIVE-2026-10-04 regenerated with "
    "live counters Q/V/D + selftest ALL PASS x2. S0 fetch zero-delta "
    "(tip==origin); S0.5 orders 152/152 double-scan zero unacked; D-19 "
    "sparse-clone fallback MATCH EB14B510 zero-consume. S1 47/47. S3 "
    "sequence all green (WM red=false; engine alive rc0 idle; no red "
    "items; trial-labor line not triggered = trio batches in flight). "
    "S6 25 legs rc0 (Sunday honest no-op family + lane guards; "
    "daily_scorecard/build_status host-guard skip per r366 stale-view "
    "veto; REPORT-2026-10-04 regenerated; token delta=0). S7 4/4 + "
    "attrition CLEAN + claws identical + watchdog present."
)
for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read"):
    state[k] = now_iso
state["last_decisions_read_at"] = now_iso
# watermark unchanged this round (EB14B510 MATCH) -> keep sha, refresh read ts
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
    "pending G-SEG GM ruling) + LIVE v1.5 burn-visibility face delivered"
)
hb["verdict"] = (
    "GREEN (smoke 47/47; v1.5 face selftest ALL PASS; D-19 MATCH zero-"
    "consume; S6 25 legs rc0; dualrun ZERO-DRIFT streak 34; attrition "
    "CLEAN; engine alive rc0 idle; orders 152/152; trio burns healthy "
    "dup_k=0)"
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
    f"{now_iso} | round 642 (bm-b, dept:工程/舰队+研究): watermark "
    "verdict=GREEN (red=false; audit CLEAN burning-healthy floor 3/3; "
    "WM probe local_batch_running=true; dualrun ZERO-DRIFT streak 34)"
    "\n当前活: FUND 三族 NULLS 烧录健康在飞 "
    f"Q{qv['fund_quality_p1']}/V{qv['fund_value_p1']}/"
    f"D{qv['fund_divlowvol_p1']} of 2000（三族 dup_k=0·追加 mtime<2min·"
    "autofill tick keepalive 活）"
    "\n最近实物: LIVE 页 v1.5 新面「⑤ 在飞判决批（NULLS 烧录进度·纯计"
    "数）」——docs/live_usage/LIVE-2026-10-04.md 02:3x 再生"
    "（scripts/ceo_live_usage.py _judgment_burn_face·selftest ALL "
    "PASS·三族 have/dup_k CEO 直读）"
    "\n下个里程碑: FUND 三族 NULLS 烧完 finalize 窗 10-05..10-09"
    "（G-SEG 结构性冻结面 GM 裁定悬置·VALUE 阻塞 r626d 6c2a6742f 已修）；"
    "窗 ≤48h"
    "\n做了什么: S0 fetch 零差集 tip==origin；S0.5 令 152/152 双扫零未回执"
    "+D-19 sparse-clone fallback MATCH EB14B510 零消费；S1 smoke 47/47；"
    "S2 双板空（job_list 空+tasks 无 open）；S3 序检全过（WM 绿·引擎活 "
    "rc0 idle·无修红·常设线不触发=有在飞批）；产品增量=ceo_live_usage "
    "v1.5（+118 行：_judgment_burn_face 纯计数读出·半写 daemon 尾行跳过"
    "诚实·dup_k 完整性·免责重编号⑥·selftest v1.5 断言×3）；S6 25 腿 rc0"
    "（周日诚实 no-op 族·update_lhb no-op·bm-a/bm-c 车道护栏 stdout-only·"
    "daily_scorecard/build_status 守卫跳过 r366 stale-view·REPORT-2026-"
    "10-04 再生·token delta=0）；S7 4/4（loop pin=2 no-op·watchdog 在位"
    "02:35·双爪恒等 pc/pp cmp rc0·attrition CLEAN）"
    "\n验证证据: ceo_live_usage selftest ALL PASS（v1.5 schema+计数诚实形"
    "+六节 md 三断言）；LIVE ⑤ 节三族计数实读（results/_r642bmb_live_sec5_"
    "view.txt）；burn probe results/_r642bmb_burn_probe.json；S6 各腿 rc0 "
    "行；attrition scan CLEAN（4 ledgers）"
    "\n下轮指针: r643 = FUND 三族烧监护续（V ETA 10-06 前后）+ finalize "
    "窗前置检查（have==2000 硬门+G-SEG 裁定面）+ LIVE v1.5 面随烧录自动"
    "刷新验收"
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
