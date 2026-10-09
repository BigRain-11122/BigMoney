# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
n1 = open(ROOT + r"\scripts\perpetual_faces_n1.py", encoding="utf-8",
          errors="replace", newline="").read()
n1n = n1.replace("\r\n", "\n")


def chunk(text, start, end):
    i = text.find(start)
    j = text.find(end, i)
    return text[i:j + len(end)]


S = '    202: {"batch": "PERPETUAL-N1-W202",'
E = '"engine_owner": "bm-a"},'
mine = chunk(n1n, S, E)
probe = open(ROOT + r"\results\_r935bma_probe_frag_cfg202.txt",
             encoding="utf-8", newline="").read()
print("mine len", len(mine), "probe len", len(probe))
n = min(len(mine), len(probe))
for k in range(n):
    if mine[k] != probe[k]:
        print("first diff at", k)
        print("mine :", repr(mine[max(0, k - 60):k + 60]))
        print("probe:", repr(probe[max(0, k - 60):k + 60]))
        break
else:
    print("prefix equal; tail mine :", repr(mine[len(probe):][:100]))
    print("prefix equal; tail probe:", repr(probe[len(mine):][:100]))
