# -*- coding: utf-8 -*-
"""r743 bm-c clone gate: create _r743bmc_{s05,s6,qa_ignite}.py from r742
originals via double-mode replacement (_r742bmc_ prefix mode + bare 742 mode),
assert stale742=0 across the trio (r736 clone law), py-compile each clone,
receipt -> results/_r743bmc_clone_receipt.json. Pattern credit: r736/r740/r742
canonical clone chain."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TRIO = ["s05", "s6", "qa_ignite"]
receipt = {"round": 743, "mode": "double-replacement", "files": {}}

for name in TRIO:
    src = os.path.join(ROOT, "Tools", "_r742bmc_%s.py" % name)
    dst = os.path.join(ROOT, "Tools", "_r743bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r742bmc_", "_r743bmc_")
    txt3 = txt2.replace("742", "743")
    stale = txt3.count("742")
    receipt["files"][name] = {"src": os.path.basename(src), "dst": os.path.basename(dst),
                              "bytes_in": len(txt.encode("utf-8")),
                              "bytes_out": len(txt3.encode("utf-8")),
                              "stale742": stale}
    assert stale == 0, "stale 742 token in %s clone" % name
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt3)
    py_compile.compile(dst, doraise=True)
    receipt["files"][name]["compile"] = "OK"

out = os.path.join(ROOT, "results", "_r743bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1)
print(json.dumps(receipt, indent=1))
