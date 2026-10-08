# r755 bm-c cloner bootstrap: derive _r755bmc_clone.py from _r754bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 753 and
# 754 tokens): 754->755 FIRST, then 753->754. Prefixes ride the bare replace.
# HAND-WRITTEN fresh per boot self-clone pit law (r753 -> pit-lineage.md).
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r754bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r755bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("754", "755")
txt = txt.replace("753", "754")
assert txt.count("755") >= 4 and txt.count("_r755bmc_") >= 3
assert 'stale754' in txt and 'stale 754 token' in txt
assert '"round": 755' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
