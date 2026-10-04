"""r681 bm-b close: round report append (bytes-mode, idempotent marker gate),
state.json round_no 680->681 (json.dump + reload self-verify, r645 law),
heartbeat refresh (int epoch, T-format clock, three-line CEO visibility)."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

now = datetime.datetime.now().astimezone()
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
marker = "r681 (bm-b)".encode("utf-8")

line = (
    "2026-10-04T16:53:00+08:00 | r681 (bm-b) PRODUCT (dept:舰队值守+数据维护链): "
    "[watermark verdict: GREEN (red=false; D-19 MATCH 4E5BE321F9B7; orders 154/154 "
    "same-caliber set-diff zero unacked/zero extra; satengine alive rc0 hb 5s fresh "
    "queue=22 held by RAM-floor gate free 2.7-3.3GB<4.0GB machine discipline "
    "self-ignite; post_review REPORT-20261004 dist ✓45/✗0/🟡5 zero active red; "
    "audit CLEAN py 86% burning-healthy; dualrun ZERO-DRIFT streak 52)] | "
    "当前活: FUND trio NULLS 烧录在飞 V853/Q668/D507 of 2000 @16:47 (42.6/33.4/25.4pct, "
    "owner=bm-b keepalive 1.9min fresh, rates 24.3/20.5/18.0/h, ETA V 10-06T16 / "
    "Q 10-07T09 / D 10-08T03) + N1-W116 2/12 RAM-gated | "
    "最近实物: S6 38/38 rc0 streak 52 -- REPORT-2026-10-04 (daily_report 16:46) + "
    "LIVE-2026-10-04 (CEO page) + CALL-2026-09-30 market-clock cell=ORANGE_COOL + "
    "LHB 11-page fresh pull + smoke 48/48 | "
    "下轮指针: W116 RAM-gated 引擎自愈点火; FUND-VALUE finalize 候选窗 10-06T15+ "
    "(r668 池面双翻律, rehearsal ALL-GREEN); 下个里程碑=trio NULLS 判决批收口 "
    "10-06..10-08 (VALUE finalize 首窗 10-06T15+, 窗内48h) | "
    "本地未达 origin commit 数=0 (commit 后 push+fetch+ls-tree 自证)"
)

data = open(RR, "rb").read()
assert data.count(marker) == 0, "r681 marker already present (idempotence gate)"
with open(RR, "ab") as fh:
    fh.write(line.encode("utf-8") + b"\n")
data2 = open(RR, "rb").read()
assert data2.count(marker) == 1, "r681 marker count != 1 after append"

st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = 681
st["round_no_label"] = "round 681 (bm-b)"
with open(STATE, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
st2 = json.load(open(STATE, encoding="utf-8"))
assert st2["round_no"] == 681, "state round_no self-verify failed"

import psutil
vm = psutil.virtual_memory()
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = clock
hb["round_no"] = 681
hb["round_no_label"] = "round 681 (bm-b)"
hb["current_task"] = (
    "r681 close: S6 38/38 rc0 streak 52 (REPORT/LIVE-101004 refreshed); trio NULLS "
    "V853/Q668/D507 of 2000 burning healthy (ETA V 10-06T16/Q 10-07T09/D 10-08T03); "
    "N1-W116 2/12 RAM-gated self-ignite; next grain = FUND-VALUE finalize 候选窗 "
    "10-06T15+ (r668 池面双翻律, rehearsal ALL-GREEN)"
)
hb["verdict"] = "healthy burning"
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
hb["free_ram_gb"] = round(vm.available / 1024 ** 3, 2)
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["ram_free_gb"] = hb["free_ram_gb"]
hb["ram_avail_gb"] = hb["free_ram_gb"]
hb["total_ram_gb"] = round(vm.total / 1024 ** 3, 2)
hb["ram_gb"] = hb["total_ram_gb"]
try:
    import subprocess
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=15,
        creationflags=0x08000000)
    mib = int(r.stdout.strip().splitlines()[0])
    hb["gpu_idle_vram_gb"] = round(mib / 1024, 2)
    hb["gpu_idle_vram_mb"] = mib
    hb["gpu_free_vram_gb"] = hb["gpu_idle_vram_gb"]
    hb["gpu_free_vram_mb"] = mib
    hb["gpu_vram_free"] = mib
    hb["gpu_free_vram_mib"] = mib
except Exception:
    pass
with open(HB, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"], "clock must be T-separated"
print("CLOSE OK: rr=appended count==1, state=681, hb epoch=%d clock=%s ram=%.2fGB"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], hb2["free_ram_gb"]))
