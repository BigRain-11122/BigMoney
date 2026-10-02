import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
needle = "        _set_wave(2)\n    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n"
print("count A3-style:", src.count(needle))
i = src.find(needle)
print(repr(src[i - 80 : i + 90]))
# W105 vacancy + W103 leg tail check
print("W105 mentions:", src.count("W105"))
print("W103 materializer face count:", src.count("W103 materializer face"))
