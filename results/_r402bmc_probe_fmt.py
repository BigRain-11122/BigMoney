# -*- coding: utf-8 -*-
import json
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\tasks\T-2026-10-02-147-P1.json"
orig = open(p, "rb").read()
print("first 80:", orig[:80])
print("last 80:", orig[-80:])
print("endswith newline:", orig.endswith(b"\n"), "CRLF count:",
      orig.count(b"\r\n"), "LF count:", orig.count(b"\n"))
j = json.loads(orig.decode("utf-8"))
rt = (json.dumps(j, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
print("rt len", len(rt), "orig len", len(orig), "equal:", rt == orig)
if rt != orig:
    for i in range(min(len(rt), len(orig))):
        if rt[i] != orig[i]:
            print("first diff at", i)
            print("orig:", orig[max(0,i-40):i+40])
            print("rt  :", rt[max(0,i-40):i+40])
            break
    else:
        print("prefix equal, tail differs")
        print("orig tail:", orig[-60:])
        print("rt tail  :", rt[-60:])
