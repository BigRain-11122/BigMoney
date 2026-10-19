# r1116 bm-c: parenthetical-landing probe (defect category 3 diagnosis, one-shot evidence)
# Replicates the builder's needle->W-chain->lowercase transform on SRC and reports the
# refuser-band parenthetical + prose + freezer landing faces BEFORE the heal passes.
import io
REPO = "."
B = io.open("results/_r1116bmc_build_w278_derive.py", encoding="utf-8", newline="").read()
SRC = io.open("results/_w277bmc_prereg_derive.py", encoding="utf-8", newline="").read()
i = B.index("NEEDLES = [")
j = B.index("needle_counts = {}", i)
ns = {"ram_face": "~8.5GB", "gpu_face": "PROBE", "ram_anchor": "~8.5G"}
exec(B[i:j] + "\n", ns)
NEEDLES = ns["NEEDLES"]
txt = SRC
for o, n in NEEDLES:
    txt = txt.replace(o, n)
P1 = "\x01W\x01"
txt2 = txt
for w in range(277, 261, -1):
    if w == 277:
        txt2 = txt2.replace("W277", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W278")
P2, P3 = "\x01N\x01", "\x01B\x01"
txt2 = txt2.replace("n1_w277", P2).replace("n1_w276", "n1_w277").replace("n1_w275", "n1_w276").replace(P2, "n1_w278")
txt2 = txt2.replace("_w277bmc", P3).replace("_w276bmc", "_w277bmc").replace("_w275bmc", "_w276bmc").replace(P3, "_w278bmc")
txt2 = txt2.replace("w276_frozen_face", "w277_frozen_face")
for face in ["refuser band 628_901..629_100〕", "refuser band 626_701..626_900〕", "refuser band 624_501..624_700〕",
             "注册 W277 B 带 626_701..626_900 落 naive A 窗内", "注册 W277 B 带 628_901..629_100 落 naive A 窗内",
             "W278 freezer 承接面强制注记", "W279 freezer 承接面强制注记"]:
    print("%d :: %s" % (txt2.count(face), face))
