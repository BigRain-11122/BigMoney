# r756 bm-c cloner bootstrap: derive _r756bmc_clone.py from _r755bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 754 and
# 755 tokens): 755->756 FIRST, then 754->755. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r755bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r756bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("755", "756")
txt = txt.replace("754", "755")
assert txt.count("756") >= 4 and txt.count("_r756bmc_") >= 3
assert 'stale755' in txt and 'stale 755 token' in txt
assert '"round": 756' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
