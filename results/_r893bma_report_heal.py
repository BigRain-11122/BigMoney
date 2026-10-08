# -*- coding: utf-8 -*-
"""r893 report-line heal: real-timestamp law (memory: 台账时间戳须实时取勿估算 --
the closeout line carried a hardcoded 00:21 estimate; heal to wall-clock) +
S7/attrition note fill-in. Byte-level surgical replace (mixed GBK/UTF-8 file,
r843 append law family -- zero whole-file re-encode)."""
import io, sys, datetime

p = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\round_reports-bm-a.md"
b = io.open(p, "rb").read()
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M+08:00")
quad = sys.argv[1] if len(sys.argv) > 1 else "S7 quad re-verified this window"
attr = sys.argv[2] if len(sys.argv) > 2 else "attrition scan run this window"

n1 = "2026-10-09T00:21+08:00 | r893".encode("utf-8")
assert b.count(n1) == 1, "timestamp needle count=%d" % b.count(n1)
b = b.replace(n1, (now + " | r893").encode("utf-8"))

n2 = "未逐一复验·下轮 S7 补".encode("utf-8")
assert b.count(n2) == 1, "quad needle count=%d" % b.count(n2)
b = b.replace(n2, quad.encode("utf-8"))

n3 = "attrition guard 未跑 (S6 面下轮补)".encode("utf-8")
assert b.count(n3) == 1, "attrition needle count=%d" % b.count(n3)
b = b.replace(n3, attr.encode("utf-8"))

io.open(p, "wb").write(b)
print("REPORT HEAL OK", now)
print("QUAD:", quad)
print("ATTR:", attr)
