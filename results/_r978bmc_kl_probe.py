# -*- coding: utf-8 -*-
# r978 probe3: K-lift faces in R34 data vs r35gen needles
import io
out = io.StringIO()
r34 = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()
i = r34.find("K-lift")
while i != -1:
    out.write(repr(r34[max(0, i - 40):i + 30]) + "\n")
    i = r34.find("K-lift", i + 1)
gen = open(r"results\_r977bmc_r35gen.py", encoding="utf-8").read()
j = gen.find("K-lift")
while j != -1:
    out.write("GEN: " + repr(gen[max(0, j - 40):j + 30]) + "\n")
    j = gen.find("K-lift", j + 1)
open(r"results\_r978bmc_kl_probe.txt", "w", encoding="utf-8").write(out.getvalue())
print("written")
