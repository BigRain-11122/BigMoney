# -*- coding: utf-8 -*-
# r978 probe2: exact bytes around A-hops-prior-B 94th instance in R34 data
import sys, io
out = io.StringIO()
src = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()
i = src.find("A-hops-prior-B")
while i != -1:
    out.write(repr(src[max(0, i - 30):i + 60]) + "\n")
    i = src.find("A-hops-prior-B", i + 1)
needle = "=\u00b7**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e5d\u5341\u56db\u4f8b\uff08E36 \u5361\uff09**"
out.write("needle repr: " + repr(needle) + "\n")
out.write("needle count: %d\n" % src.count(needle))
open(r"results\_r978bmc_rep_probe2.txt", "w", encoding="utf-8").write(out.getvalue())
print("written")
