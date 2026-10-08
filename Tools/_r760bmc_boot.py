# r760 bm-c cloner bootstrap: derive _r760bmc_clone.py from _r759bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 758 and
# 759 tokens): 759->760 FIRST, then 758->759. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r759bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r760bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("759", "760")
txt = txt.replace("758", "759")
assert txt.count("760") >= 4 and txt.count("_r760bmc_") >= 3
assert 'stale759' in txt and 'stale 759 token' in txt
assert '"round": 760' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
