import os, re
d = os.path.join(os.environ["TEMP"], "r531_surgical")
pf = open(os.path.join(d, "merged_scripts__perpetual_faces.py"), encoding="utf-8").read()
lines = pf.split("\n")
# find the N1_BANDS wave-row region: print keys with their a-bands in file order
rows = re.findall(r"^\s+(\d+): \{\"a\": \((\d+), (\d+)\), \"b_exit\": \((\d+), (\d+)\)", pf, re.M)
for r in rows[-5:]:
    print("band row:", r)
print("order ints:", [int(r[0]) for r in rows])
# check W18 then W19 comment blocks present exactly once
print("W18 comment blocks:", pf.count("# W18 (r530 bm-a, prereg-time extension"))
print("W19 comment blocks:", pf.count("W19 re-band") + pf.count("# W19 ("))
import ast
ast.parse(pf)
print("AST OK pf")
cn = open(os.path.join(d, "merged_research__PERPETUAL_FACES.md"), encoding="utf-8").read()
i18 = cn.find("N1 \u6ce218")
i19 = cn.find("N1 \u6ce219")
i_r529 = cn.find("N3-R1 \u00d7 N1-W13")
print("canon: r529 at", i_r529, "W18 at", i18, "W19 at", i19)
print("canon rows count:", cn.count("- N1 \u6ce2"), "wave rows")
