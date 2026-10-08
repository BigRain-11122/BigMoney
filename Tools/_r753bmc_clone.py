# -*- coding: utf-8 -*-
"""r753 bm-c clone gate: create _r753bmc_{s05,s6,qa_ignite}.py from r752
originals via double-mode replacement (_r752bmc_ prefix mode + bare 752 mode),
assert stale752=0 across the trio (r736 clone law), py-compile each clone,
receipt -> results/_r753bmc_clone_receipt.json. Pattern credit: r736/r740/r742/
r743/r745/r746/r748/r749/r752 canonical clone chain."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TRIO = ["s05", "s6", "qa_ignite"]
receipt = {"round": 753, "mode": "double-replacement", "files": {}}

for name in TRIO:
    src = os.path.join(ROOT, "Tools", "_r752bmc_%s.py" % name)
    dst = os.path.join(ROOT, "Tools", "_r753bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r752bmc_", "_r753bmc_")
    txt3 = txt2.replace("752", "753")
    stale = txt3.count("752")
    receipt["files"][name] = {"src": os.path.basename(src), "dst": os.path.basename(dst),
                              "bytes_in": len(txt.encode("utf-8")),
                              "bytes_out": len(txt3.encode("utf-8")),
                              "stale752": stale}
    assert stale == 0, "stale 752 token in %s clone" % name
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt3)
    py_compile.compile(dst, doraise=True)
    receipt["files"][name]["compile"] = "OK"

out = os.path.join(ROOT, "results", "_r753bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1)
print(json.dumps(receipt, indent=1))
