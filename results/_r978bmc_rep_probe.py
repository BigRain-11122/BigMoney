# -*- coding: utf-8 -*-
# r978 probe: why rep needle A-hops-prior-B 94th not found in R34 data
import re
src = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()
for m in re.finditer(r"A-hops-prior-B[^\n]{0,120}", src):
    print(repr(m.group(0)))
print("---")
# also check E36 卡 faces and 九十X例
for m in re.finditer(r"\u7b2c\u4e5d\u5341[\u56db\u4e94\u4e09][\u4f8b\u679a][^\n]{0,40}", src):
    print(repr(m.group(0)))
