# r749 bm-c cloner bootstrap: derive _r749bmc_clone.py from _r748bmc_clone.py
# Order-sensitive bare-number double-replacement (source contains BOTH 747 and
# 748 tokens): 748->749 FIRST, then 747->748. Prefixes ride the bare replace.
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r748bmc_clone.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r749bmc_clone.py"
txt = io.open(SRC, encoding="utf-8").read()
txt = txt.replace("748", "749")
txt = txt.replace("747", "748")
assert txt.count("749") >= 4 and txt.count("_r749bmc_") >= 3
assert 'stale748' in txt and 'stale 748 token' in txt
assert '"round": 749' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
for line in txt.splitlines():
    if "src = os.path" in line or "dst = os.path" in line or 'out = os.path.join' in line:
        print(line.strip())
print("bootstrap ok bytes=%d" % len(txt.encode("utf-8")))
