# r753 bm-c cloner bootstrap: derive _r753bmc_clone.py from _r752bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 751 and
# 752 tokens): 752->753 FIRST, then 751->752. Prefixes ride the bare replace.
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r752bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r753bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("752", "753")
txt = txt.replace("751", "752")
assert txt.count("753") >= 4 and txt.count("_r753bmc_") >= 3
assert 'stale752' in txt and 'stale 752 token' in txt
assert '"round": 753' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
