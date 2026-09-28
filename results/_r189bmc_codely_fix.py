import io, re, sys

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
src = io.open(P, encoding="utf-8").read()

pat = re.compile(
    r"<<<<<<< HEAD\n(.*?)\|\|\|\|\|\|\| parent of 794d7772[^\n]*\n=======\n(.*?)>>>>>>> 794d7772[^\n]*\n",
    re.DOTALL)
m = pat.search(src)
if not m:
    print("ABORT: conflict block not found")
    sys.exit(2)
origin_side, mine_side = m.group(1), m.group(2)
# union: origin's r400 bm-b entry first (earlier ts), then my r189 entry
union = origin_side + mine_side
src = src[:m.start()] + union + src[m.end():]
for marker in ("<<<<<<<", ">>>>>>>", "|||||||"):
    if marker in src:
        print("ABORT: residual marker", marker)
        sys.exit(2)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("CODELY.md union resolved: origin r400 bm-b entry + r189 bmc entry, "
      "zero residual markers, bytes =", len(src.encode("utf-8")))
