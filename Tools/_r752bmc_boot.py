# r752 bm-c cloner bootstrap: derive _r752bmc_clone.py from _r751bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 750 and
# 751 tokens): 751->752 FIRST, then 750->751. Prefixes ride the bare replace.
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r751bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r752bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("751", "752")
txt = txt.replace("750", "751")
assert txt.count("752") >= 4 and txt.count("_r752bmc_") >= 3
assert 'stale751' in txt and 'stale 751 token' in txt
assert '"round": 752' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
