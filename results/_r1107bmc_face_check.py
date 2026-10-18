# -*- coding: utf-8 -*-
import io
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
T0 = io.open(REPO + r"\results\_w275bmc_w274_frozen_face.txt", encoding="utf-8", newline="").read()
C = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
faces = [
    "bm-c r1102 W273 §7 范式", "bm-c r1102 W274 §7 范式", "bm-c r1105 W274 §7 范式",
    "bm-c r1102 W273 §8 范式", "bm-c r1102 W274 §8 范式",
    "席位窗实跑", "finalize one-pass bm-c",
    "W273 finalize one-pass", "W274 finalize one-pass",
]
print("%-38s %8s %8s" % ("face", "T0'", "canon"))
for f in faces:
    print("%-38r %8d %8d" % (f, T0.count(f), C.count(f)))
import re
for m in re.finditer(r".{10}席位窗实跑.{40}", T0):
    print("T0':", repr(m.group(0)))
for m in re.finditer(r".{10}席位窗实跑.{40}", C):
    print("CAN:", repr(m.group(0)))
for m in re.finditer(r".{6}finalize one-pass bm-c.{30}", T0):
    print("T0':", repr(m.group(0)))
for m in re.finditer(r".{6}finalize one-pass bm-c.{30}", C):
    print("CAN:", repr(m.group(0)))
