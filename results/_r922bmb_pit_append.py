# -*- coding: utf-8 -*-
"""r922 bm-b pit-machine.md direct-write append (r666/r889/r903/r908/r911
precedent: CODELY.md main file 30,534B leaves 186B < entry size, so the
new pit law lands verbatim in the machine-domain pit file). Zero-loss
assertion: entry bytes counted, sha16 stamped, receipt written."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "research", "pit-machine.md")
RECEIPT = os.path.join(ROOT, "results", "_r922bmb_pit_append.json")

ENTRY = (
    "- [2026-10-14 03:0x r922 bm-b] **孤儿探针三面律对 ProcessPool 监督者假阳性"
    "（parent-dead+cpu-stalled 双面成立但 worker 满载=活车道）**：N2U3 leg-3 烧录"
    "（PID 8556，autofill 分离 launch 01:06）在飞时 orphan_face_probe 报 orphans=1"
    "——主进程三面全中（父死=分离 spawn 合法态·无隐藏宿主·CPU 0 delta=ProcessPool "
    "监督者只等 workers），但其 8 个 spawn_main worker（parent_pid=8556）各烧 "
    "~100% CPU=真负载在子不在父；若 --kill 轮按报告击杀=毁 3.3h 训练批（checkpoint "
    "断点续跑虽在，烧录面白烧+judged 链延后）。判死律补：face3(cpu-stalled) 命中的"
    "\u201c孤儿\u201d动手前必查子进程面——ParentProcessId=<pid> 有活子且子群 CPU "
    "delta 载荷>0=监督者假阳性禁杀；真孤儿=无活子或子群同停滞。How to apply：探针"
    "报告 orphan_details 命中时先查子进程载荷再定生死；分离 spawn 的长批"
    "（multicore O-20260930-2355 律族）监督者恒为此形态。\n"
    "- 对账行 r922 bm-b: direct-write entry per r666/r889/r903/r908/r911 precedent "
    "(CODELY.md 主件 30,534B 余量 186B 红线·机器/探针/进程卫生域归位 pit-machine.md); "
    "entry bytes={BYTES} sha16={SHA16} verbatim-in-file (zero-loss asserted); "
    "receipt=results/_r922bmb_pit_append.json\n"
)

pre = open(TARGET, encoding="utf-8").read()
pre_size = os.path.getsize(TARGET)
entry_bytes = ENTRY.encode("utf-8")
sha16 = hashlib.sha256(entry_bytes).hexdigest()[:16]
filled = ENTRY.replace("{BYTES}", str(len(entry_bytes))).replace(
    "{SHA16}", sha16)
final_bytes = filled.encode("utf-8")
with open(TARGET, "a", encoding="utf-8", newline="") as f:
    f.write(filled)
post = open(TARGET, encoding="utf-8").read()
receipt = {
    "round": "r922 bm-b",
    "law": "direct-write exception (main full: 30,534B + entry > 30,720B cap)",
    "target": "research/pit-machine.md",
    "entry_bytes": len(entry_bytes),
    "entry_sha16": sha16,
    "verbatim_in_file": filled in post,
    "pre_size_b": pre_size,
    "post_size_b": os.path.getsize(TARGET),
    "main_codely_size_b": os.path.getsize(os.path.join(ROOT, "CODELY.md")),
    "zero_loss_assert": post == pre + filled,
    "ts": "2026-10-14T03:02:00+08:00",
}
with open(RECEIPT, "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps(receipt, ensure_ascii=False))
assert receipt["verbatim_in_file"] and receipt["zero_loss_assert"]
assert receipt["post_size_b"] <= 30720
