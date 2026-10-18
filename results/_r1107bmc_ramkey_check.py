# -*- coding: utf-8 -*-
import io, re
t = io.open(r"results\_w274bmc_prereg_derive.py", encoding="utf-8").read()
key = '"' + "本窗 free RAM ~4.4GB" + '": 0'
print("floors-key form count:", t.count(key))
for m in re.finditer(r".{18}本窗 free RAM ~4\.4GB.{12}", t):
    print(repr(m.group(0)))
