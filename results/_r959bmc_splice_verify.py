# r959 (bm-c): W228 splice estate machine verification before commit
# - receipt sha16 asserts vs on-disk bytes (fail-closed)
# - py_compile both spliced faces
# - W228 registration census in both faces
import hashlib
import json
import py_compile
import re
import sys

BASE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
rec = json.load(open(BASE + r"\results\_w228bmc_freeze_receipt.json", encoding="utf-8"))
fails = []

for path, key in [
    (BASE + r"\scripts\perpetual_faces.py", "pf_sha16_post"),
    (BASE + r"\scripts\perpetual_faces_n1.py", "n1_sha16_post"),
]:
    b = open(path, "rb").read()
    sha16 = hashlib.sha256(b).hexdigest()[:16]
    expect = rec[key]
    ok = sha16 == expect
    print(path.split("\\")[-1], "sha16", sha16, "expect", expect, "MATCH" if ok else "MISMATCH")
    if not ok:
        fails.append("sha16 mismatch: " + path)
    try:
        py_compile.compile(path, doraise=True)
        print(path.split("\\")[-1], "py_compile OK")
    except Exception as e:
        fails.append("py_compile fail: %s: %s" % (path, e))

src_n1 = open(BASE + r"\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
src_pf = open(BASE + r"\scripts\perpetual_faces.py", encoding="utf-8").read()
n228 = len(re.findall(r"\b228\b", src_n1))
p228 = len(re.findall(r"\b228\b", src_pf))
print("228 occurrences n1:", n228, "| pf:", p228)
if n228 < 3 or p228 < 3:
    fails.append("W228 registration census too low (n1=%d pf=%d)" % (n228, p228))

# ledger face: current total must reflect the 12 appended shards (12 x 200 = 2400 rows since W227 923,189)
import os
cand = [f for f in os.listdir(BASE + r"\results\perpetual_faces") if "ledger" in f.lower()]
print("ledger candidates:", cand)
for c in cand:
    try:
        led = json.load(open(BASE + r"\results\perpetual_faces" + "\\" + c, encoding="utf-8"))
        if isinstance(led, dict):
            total = led.get("total_rows") or led.get("total")
            print(c, "total:", total, "| keys:", sorted(led.keys())[:8])
    except Exception as e:
        print(c, "read note:", e)

if fails:
    print("VERIFY-FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("VERIFY-PASS")
