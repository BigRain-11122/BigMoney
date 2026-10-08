# r757 bm-c cloner bootstrap: derive _r757bmc_clone.py from _r756bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 755 and
# 756 tokens): 756->757 FIRST, then 755->756. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r756bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r757bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("756", "757")
txt = txt.replace("755", "756")
assert txt.count("757") >= 4 and txt.count("_r757bmc_") >= 3
assert 'stale756' in txt and 'stale 756 token' in txt
assert '"round": 757' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
