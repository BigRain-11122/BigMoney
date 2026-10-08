# r758 bm-c cloner bootstrap: derive _r758bmc_clone.py from _r757bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 756 and
# 757 tokens): 757->758 FIRST, then 756->757. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r757bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r758bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("757", "758")
txt = txt.replace("756", "757")
assert txt.count("758") >= 4 and txt.count("_r758bmc_") >= 3
assert 'stale757' in txt and 'stale 757 token' in txt
assert '"round": 758' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
