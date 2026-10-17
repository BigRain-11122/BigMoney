import io

def ctx(path, needle):
    t = io.open(path, "r", encoding="utf-8", errors="replace").read()
    out = []
    i = t.find(needle)
    while i != -1:
        s = max(0, i - 90)
        e = min(len(t), i + len(needle) + 90)
        out.append(t[s:e])
        i = t.find(needle, i + 1)
    return out

for label, path in [
    ("TEMPLATE_W260", r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w261bmc_w260_frozen_face.txt"),
    ("DERIVED_W261", r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\PERPETUAL_N1_W261_PREREG.md"),
]:
    for needle in ["987,535"]:
        hits = ctx(path, needle)
        print("%s needle=%r hits=%d" % (label, needle, len(hits)))
        for k, h in enumerate(hits):
            print("  [%d] %s" % (k, h.encode("unicode_escape").decode("ascii")))
