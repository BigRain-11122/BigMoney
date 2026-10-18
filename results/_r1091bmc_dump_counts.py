# -*- coding: utf-8 -*-
import json
r = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1091bmc_needle_preflight.json", encoding="utf-8"))
c = r["counts"]
for k in ['267: {"batch"', '266: {"batch"', '268: {"batch"', '267: {{"batch"',
          '268: {{"batch"', '267: {"a"', '266: {"a"', '267: {{"a"', '268: {{"a"',
          '265: {"batch"', '266: {{"a"', 'W211..W265 fifty-five legs',
          'own W248..W265\n# legs (18 rows)', 'W211..W266 legs (55)',
          'arith_a267/arith_b267 define+assert consistent']:
    print(repr(k) + " = " + str(c.get(k, "NOT-MEASURED")))
# EOL detection of canon
t = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w267bmc_freeze_edits.py", "rb").read().decode("utf-8")
crlf = t.count("\r\n"); lf = t.count("\n") - crlf
print("canon EOL: crlf=%d lf=%d" % (crlf, lf))
