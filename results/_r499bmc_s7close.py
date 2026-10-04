# -*- coding: utf-8 -*-
"""r499 bm-c S7 close: inbox move (white-listed rename) + CODELY.md pit append
(r679 marker gate) + closing orders re-scan (S0.5 double-scan law)."""
import json
import os
import re
import shutil
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# ---- 1. closing orders re-scan (same-shape set) ----
r = subprocess.run(["git", "ls-tree", "origin/main", "fleet/orders/"],
                   capture_output=True, cwd=ROOT, creationflags=CREATE_NO_WINDOW)
names = []
for ln in r.stdout.decode("utf-8", "replace").splitlines():
    m = re.match(r"\d+ \w+ ([0-9a-f]+)\t(fleet/orders/O-.*\.md)$", ln)
    if m:
        names.append(m.group(2).split("/")[-1])
ack = json.load(open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8")).get("orders_ack", [])
unacked = [n for n in names if n not in ack]
print("CLOSING-SCAN orders=%d unacked=%d" % (len(names), len(unacked)))
for n in unacked:
    print("UNACKED-NEW: " + n)

# ---- 2. inbox move (self-issued custody bulletin, read+confirmed, no action item) ----
src = ROOT + r"\fleet\inbox\MSG-2026-10-04-2130-bmc-ALL.md"
dst = ROOT + r"\fleet\inbox\processed\MSG-2026-10-04-2130-bmc-ALL.md"
if os.path.exists(src):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print("MSG MOVED -> processed (self-issued custody bulletin r497, consumed on read)")
else:
    print("MSG already moved or absent")

# ---- 3. CODELY.md pit append (r679 marker gate, one entry <=1.5KB) ----
cp = ROOT + r"\CODELY.md"
with open(cp, "rb") as fh:
    raw = fh.read()
entry = (
    "\n- [2026-10-04 22:0x r499 bm-c] PS 函数返回值管道污染坑（r499 s6-runner 血统复制实弹·零腿伤害零盘伤）："
    "r498 正典 Leg() 进度打印用 Write-Host（只打印不进管道），r499 复制时误改 Write-Output→函数一切输出进返回值管道"
    "→$rc 捕获成数组→「$rc -ne 0」数组比较恒真→fails 数组被 38 条 LEG 显示行污染（S6 DONE fails=[全串] 假象）；"
    "log 逐腿 rc=0 行独立正确=判据层无恙。正法=函数内非返回输出一律 Write-Host 禁 Write-Output（pit-ps 在册 "
    "[void] 吞输出流条目姊妹面）。How to apply：复制 runner/批驱动器血统时核进度打印形态；见 fails 数组含 "
    "LEG 字样即判本坑勿误报真 FAIL。\n"
)
marker = "PS 函数返回值管道污染坑（r499 s6-runner"
assert raw.decode("utf-8", "replace").count(marker) == 0, "CODELY entry already present"
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
body = entry.replace("\n", "\r\n" if eol == b"\r\n" else "\n").encode("utf-8")
with open(cp, "ab") as fh:
    fh.write(body)
# verify append landed exactly once
with open(cp, "rb") as fh:
    raw2 = fh.read()
assert raw2.decode("utf-8", "replace").count(marker) == 1, "append verify fail"
print("CODELY APPENDED (%d bytes) size=%d" % (len(body), len(raw2)))
print("S7CLOSE DONE")
