import sys
SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r373bmc_entry_map.txt"
raw = open(SRC, "rb").read()
text = raw.decode("utf-8")
lines = text.split("\r\n")
buf = ["total_bytes=%d total_lines=%d" % (len(raw), len(lines))]
for i, ln in enumerate(lines):
    if ln.startswith("- ") or ln.startswith("#"):
        buf.append("%4d %6dB %s" % (i, len(ln.encode("utf-8")) + 2, ln[:96].replace("\r", "")))
open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
print("map written: %d lines" % len(buf))
