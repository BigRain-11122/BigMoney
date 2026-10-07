# -*- coding: utf-8 -*-
"""r741 bm-c clone gate: create _r741bmc_{s05,s6,qa_ignite}.py from r740
originals via double-mode replacement (_r740bmc_ prefix mode + bare 740 mode),
assert stale740=0 across the trio (r736 clone law), py-compile each clone,
receipt -> results/_r741bmc_clone_receipt.json. Pattern credit: r736/r740
canonical clone chain."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TRIO = ["s05", "s6", "qa_ignite"]
receipt = {"round": 741, "mode": "double-replacement", "files": {}}

for name in TRIO:
    src = os.path.join(ROOT, "Tools", "_r740bmc_%s.py" % name)
    dst = os.path.join(ROOT, "Tools", "_r741bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r740bmc_", "_r741bmc_")
    txt3 = txt2.replace("740", "741")
    stale = txt3.count("740")
    receipt["files"][name] = {"src": os.path.basename(src), "dst": os.path.basename(dst),
                              "bytes_in": len(txt.encode("utf-8")),
                              "bytes_out": len(txt3.encode("utf-8")),
                              "stale740": stale}
    assert stale == 0, "stale 740 token in %s clone" % name
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt3)
    py_compile.compile(dst, doraise=True)
    receipt["files"][name]["compile"] = "OK"

out = os.path.join(ROOT, "results", "_r741bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1)
print(json.dumps(receipt, indent=1))
