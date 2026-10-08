# -*- coding: utf-8 -*-
"""r753 bm-c resolver boot: derive _r753bmc_rebase_resolve.py from the r750
canonical resolver. All '750' tokens in the source are SELF-references
(docstring header, receipt path, round field) -- law refs (r738/r711/r756/
r678/r742/r658) contain no '750' substring, so a single bare replace is safe.
Bare-number single-replacement (no generation overlap in this source)."""
import io

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r750bmc_rebase_resolve.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r753bmc_rebase_resolve.py"
txt = io.open(SRC, encoding="utf-8").read()
n_before = txt.count("750")
txt = txt.replace("750", "753")
assert txt.count("753") >= 4 and txt.count("_r753bmc_") >= 2
assert txt.count("750") == 0, "stale 750 token in resolver clone"
assert '"round": 753' in txt
io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
print("resolver clone ok bytes=%d src_750_tokens=%d" % (len(txt.encode("utf-8")), n_before))
