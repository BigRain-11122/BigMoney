# -*- coding: utf-8 -*-
"""r763 bm-c push-race merge-kit clone: create _r763bmc_{merge_resolve,
merge_finish}.py from r747 originals via double-mode replacement
(_r747bmc_ prefix mode + bare 747 mode), assert stale747=0 across the pair
(r736 clone law), py-compile each clone. r747 law: future race windows clone
the two-piece closer verbatim. Receipt -> results/_r763bmc_merge_clone.json."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PAIR = ["merge_resolve", "merge_finish"]
receipt = {"round": 763, "mode": "double-replacement", "files": {}}

for name in PAIR:
    src = os.path.join(ROOT, "Tools", "_r747bmc_%s.py" % name)
    dst = os.path.join(ROOT, "Tools", "_r763bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r747bmc_", "_r763bmc_")
    txt3 = txt2.replace("747", "763")
    stale = txt3.count("747")
    receipt["files"][name] = {"src": os.path.basename(src), "dst": os.path.basename(dst),
                              "bytes_in": len(txt.encode("utf-8")),
                              "bytes_out": len(txt3.encode("utf-8")),
                              "stale747": stale}
    assert stale == 0, "stale 747 token in %s clone" % name
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt3)
    py_compile.compile(dst, doraise=True)
    receipt["files"][name]["compile"] = "OK"

out = os.path.join(ROOT, "results", "_r763bmc_merge_clone.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1)
print(json.dumps(receipt, indent=1))
