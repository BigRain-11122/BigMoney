# -*- coding: utf-8 -*-
# r976 W234 derive assembly: splice the emitted SUB block into the tpl.
import py_compile, sys
sys.stdout.reconfigure(encoding="utf-8")
TPL = r"results\_w234bmc_prereg_derive_tpl.py"
SUB = r"results\_w234bmc_sub_block.py"
OUT = r"results\_w234bmc_prereg_derive.py"
tpl = open(TPL, encoding="utf-8").read()
sub = open(SUB, encoding="utf-8").read()
assert tpl.count("@@SUB_BLOCK@@") == 1, "SUB marker not unique in tpl"
assert sub.startswith("SUB = {") and sub.rstrip().endswith("}"), "sub block shape drift"
py_compile.compile(SUB, doraise=True)  # emitted block compiles standalone
out = tpl.replace("@@SUB_BLOCK@@", sub.rstrip("\n"))
assert "@@SUB_BLOCK@@" not in out and out.count("SUB = {") == 1
open(OUT, "w", encoding="utf-8", newline="").write(out)
py_compile.compile(OUT, doraise=True)
print("derive assembled:", OUT, "bytes:", len(out.encode("utf-8")), "| py_compile PASS")
