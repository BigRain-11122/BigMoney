# -*- coding: utf-8 -*-
# r980 probe: locate the exact post-LAYER2 KL segment vs the generator needle, char-diff them.
import ast, sys
sys.stdout.reconfigure(encoding="utf-8")

# (1) replicate LAYER-2 on R34 text
t = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()
t = t.replace("PERPETUAL-N1-W234", "PERPETUAL-N1-W235")
t = t.replace("PERPETUAL_N1_W234", "PERPETUAL_N1_W235")
t = t.replace("n1_w234", "n1_w235")
t = t.replace("_w234bmc", "_w235bmc")
t = t.replace("W234", "@SELF@")
t = t.replace("line_pre_w233", "line_pre_w@WPRE@")
t = t.replace("n1_w233", "n1_w234")
t = t.replace("W233", "W234")
t = t.replace("@WPRE@", "w234")
t = t.replace("@SELF@", "W235")

i = t.find("K-lift")
seg = t[t.rfind('"', 0, i) + 1:]
seg = seg[: seg.find('"')]
print("POST-SHIFT SEG:", repr(seg))

# (2) extract needles from generator AST
src = open(r"results\_r977bmc_r35gen.py", encoding="utf-8").read()
tree = ast.parse(src)
needles = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "rep":
        a = node.args[0]
        if isinstance(a, ast.Constant):
            needles.append((node.lineno, a.value))
for ln, nd in needles:
    if "K-lift" in nd:
        print("GEN NEEDLE@L%d: %r" % (ln, nd))
        # char-diff
        for j, (c1, c2) in enumerate(zip(nd, seg)):
            if c1 != c2:
                print("first diff at", j, repr(nd[j-10:j+10]), "VS", repr(seg[j-10:j+10]))
                break
        else:
            print("common prefix equal; lens:", len(nd), len(seg))
