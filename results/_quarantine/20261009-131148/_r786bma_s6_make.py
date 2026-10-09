# -*- coding: utf-8 -*-
src = open(r"results\_r783bma_s6_chain.py", encoding="utf-8").read()
src = src.replace("r783 bm-a; bloodline = r781 verbatim 38 legs;",
                  "r786 bm-a; bloodline = r783 verbatim 38 legs;")
src = src.replace("W160 freeze+ignition round",
                  "W161 finalize round (dead-r785 absorption)")
src = src.replace('"round": 783', '"round": 786')
src = src.replace("_r783bma_s6_facts.json", "_r786bma_s6_facts.json")
open(r"results\_r786bma_s6_chain.py", "w", encoding="utf-8", newline="").write(src)
print("written", len(src))
