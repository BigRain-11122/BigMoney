# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"research\PERPETUAL_N1_W212_PREREG.md", encoding="utf-8").read()
i = t.find("selftest W212 face")
phys = t[i:i+330]
mine = ("selftest W212 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1\uff09\u3002**\u672c\u4ef6\u4e0e results/_w212bmc_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w211bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W211 \u884c+W211 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W211 \u5757\u7269\u7406\u5b57\u8282\u3010\u7ed3\u6784\u5df2\u77e5\u3011\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r848/W209 \u5148\u4f8b freeze-prep \u540c\u5f0f")
n = min(len(phys), len(mine))
for k in range(n):
    if phys[k] != mine[k]:
        print(f"first divergence at {k}: phys={phys[k-12:k+12]!r} vs mine={mine[k-12:k+12]!r}")
        break
else:
    print(f"common prefix OK for {n} chars; phys len={len(phys)} mine len={len(mine)}")
    print("phys tail:", repr(phys[n-20:n+40]))
    print("mine tail:", repr(mine[n-20:n+40]))
