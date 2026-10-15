# -*- coding: utf-8 -*-
# r1045 debug probe: inspect T2 §5.4 region post-transform (why line_pre_w249 missing)
import io
src = io.open("results/_w250bmc_prereg_derive.py", encoding="utf-8").read()
src = src.split("# ---------------- post gates ----------------")[0]
src = src.replace('io.open(OUT, "w", encoding="utf-8", newline="").write(T2)', "pass")
g = {"__name__": "dbg", "__file__": "results/_w250bmc_prereg_derive.py"}
exec(src, g)
T2 = g["T2"]
i = T2.find("K-lift 线移动")
io.open("results/_w250bmc_dbg_t2_region.txt", "w", encoding="utf-8", newline="").write(
    "REGION:\n" + T2[i:i+700] + "\n\nCOUNTS:\n"
    + "line_pre_w249=%d\n" % T2.count("line_pre_w249")
    + "line_pre_w248=%d\n" % T2.count("line_pre_w248")
    + "line_pre_w250=%d\n" % T2.count("line_pre_w250")
    + "line_pre=%d\n" % T2.count("line_pre"))
print("probe written")
