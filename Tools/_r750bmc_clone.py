# -*- coding: utf-8 -*-
"""r750 bm-c clone gate: create _r750bmc_{s05,s6,qa_ignite}.py from r749
originals via double-mode replacement (_r749bmc_ prefix mode + bare 749 mode),
assert stale749=0 across the trio (r736 clone law), py-compile each clone,
receipt -> results/_r750bmc_clone_receipt.json. Pattern credit: r736/r740/r742/
r743/r745/r746/r748/r749 canonical clone chain."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TRIO = ["s05", "s6", "qa_ignite"]
receipt = {"round": 750, "mode": "double-replacement", "files": {}}

for name in TRIO:
    src = os.path.join(ROOT, "Tools", "_r749bmc_%s.py" % name)
    dst = os.path.join(ROOT, "Tools", "_r750bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r749bmc_", "_r750bmc_")
    txt3 = txt2.replace("749", "750")
    stale = txt3.count("749")
    receipt["files"][name] = {"src": os.path.basename(src), "dst": os.path.basename(dst),
                              "bytes_in": len(txt.encode("utf-8")),
                              "bytes_out": len(txt3.encode("utf-8")),
                              "stale749": stale}
    assert stale == 0, "stale 749 token in %s clone" % name
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt3)
    py_compile.compile(dst, doraise=True)
    receipt["files"][name]["compile"] = "OK"

out = os.path.join(ROOT, "results", "_r750bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1)
print(json.dumps(receipt, indent=1))
