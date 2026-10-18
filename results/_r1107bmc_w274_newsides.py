# -*- coding: utf-8 -*-
# r1107 diagnostic 3: list every needle whose NEW side contains W274 (chain will roll it to
# W275 -- legitimate only if the face is a current-gen W275 reference), and whose OLD side
# count in canon = 0 (suspect hallucinated faces). Also S8-span W274 old-face reality check.
import io, re
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
B = io.open(REPO + r"\results\_r1107bmc_build_w275_derive.py", encoding="utf-8", newline="").read()
C = io.open(REPO + r"\results\_w274bmc_prereg_derive.py", encoding="utf-8", newline="").read()
T0 = io.open(REPO + r"\results\_w275bmc_w274_frozen_face.txt", encoding="utf-8", newline="").read()
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
ns = {"ram_face": "~4.4GB", "gpu_face": "GPUSTUB"}
exec(B[i:j], ns)
print("== needles with NEW side containing W274 ==")
for old, new in ns["NEEDLES"]:
    if "W274" in new:
        print("  old=%r (canon count %d)" % (old[:90], C.count(old)))
        print("  new=%r" % new[:90])
        print("  T0' count of expected final face (new with W274->W275 swap): %d"
              % T0.count(new.replace("W274", "W275")[:60]))
print()
print("== S8 span heal pairs: old-face T0' counts (span = final text, must match T1' post-VMAP) ==")
for f in ["bm-c r1102 W273 §7 范式", "bm-c r1102 W274 §7 范式",
          "bm-c r1102 W273 §8 范式", "bm-c r1102 W274 §8 范式",
          "W273 finalize one-pass bm-c r1102", "estate chain r1102 W273 同窗全周期"]:
    print("  %-46r T0'=%d canon=%d" % (f, T0.count(f), C.count(f)))
