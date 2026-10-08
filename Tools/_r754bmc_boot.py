# r754 bm-c cloner bootstrap: derive _r754bmc_clone.py from _r753bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 752 and
# 753 tokens): 753->754 FIRST, then 752->753. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r753bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r754bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("753", "754")
txt = txt.replace("752", "753")
assert txt.count("754") >= 4 and txt.count("_r754bmc_") >= 3
assert 'stale753' in txt and 'stale 753 token' in txt
assert '"round": 754' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
