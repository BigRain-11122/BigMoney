# r759 bm-c cloner bootstrap: derive _r759bmc_clone.py from _r758bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 757 and
# 758 tokens): 758->759 FIRST, then 757->758. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r758bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r759bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("758", "759")
txt = txt.replace("757", "758")
assert txt.count("759") >= 4 and txt.count("_r759bmc_") >= 3
assert 'stale758' in txt and 'stale 758 token' in txt
assert '"round": 759' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
