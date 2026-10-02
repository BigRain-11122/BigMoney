# -*- coding: utf-8 -*-
import subprocess
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
blob = subprocess.check_output(
    ["git", "-C", ROOT, "show", "HEAD:CODELY.md"])
wt = open(ROOT + r"\CODELY.md", "rb").read()
print("blob", len(blob), "B; wt", len(wt), "B")
print("blob CRLF:", blob.count(b"\r\n"), "LF:", blob.count(b"\n"))
print("wt   CRLF:", wt.count(b"\r\n"), "LF:", wt.count(b"\n"))
print("equal:", blob == wt)
if blob != wt:
    n = min(len(blob), len(wt))
    for i in range(n):
        if blob[i] != wt[i]:
            print("first diff at", i)
            print("blob:", blob[max(0, i - 30):i + 30])
            print("wt  :", wt[max(0, i - 30):i + 30])
            break
    else:
        print("common prefix identical; lengths differ")
# also pit-pool
blob2 = subprocess.check_output(
    ["git", "-C", ROOT, "show", "HEAD:research/pit-pool.md"])
wt2 = open(ROOT + r"\research\pit-pool.md", "rb").read()
print("pitpool blob", len(blob2), "CRLF", blob2.count(b"\r\n"),
      "LF", blob2.count(b"\n"), "| wt", len(wt2), "CRLF",
      wt2.count(b"\r\n"), "LF", wt2.count(b"\n"))
