# -*- coding: utf-8 -*-
"""r767 bm-c clone gate: create _r767bmc_{s05,s6,qa_ignite}.py from r766
originals via double-mode replacement (_r766bmc_ prefix mode + bare 766
mode), re-point Pattern-credit lines to the immediate predecessor
(_r766bmc_* originals, per canonical clone chain), assert stale766=0 across
the trio with credit/law-family exclusions (r736 clone law), py-compile
each clone, receipt -> results/_r767bmc_clone_receipt.json. Pattern credit:
Tools/_r764bmc_boot.py (double-replacement creator) + Tools/
_r766bmc_clone_gate.py (stale-scan receipt shape)."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TRIO = ["s05", "s6", "qa_ignite"]
PREV = "766"
EXCLUDE_MARKS = ("_r766bmc_", "Pattern credit", "law family", "credit:")
receipt = {"round": 767, "mode": "double-replacement + credit re-point",
           "prev_scan": PREV, "files": {}, "stale_total": 0}

for name in TRIO:
    src = os.path.join(ROOT, "Tools", "_r766bmc_%s.py" % name)
    dst = os.path.join(ROOT, "Tools", "_r767bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r766bmc_", "_r767bmc_")
    txt3 = txt2.replace("766", "767")
    # credit lines: point at the immediate predecessor (r766 originals)
    txt4 = txt3.replace("_r765bmc_", "_r766bmc_")
    stale = []
    for i, line in enumerate(txt4.splitlines(), 1):
        if PREV in line:
            if any(m in line for m in EXCLUDE_MARKS):
                continue
            stale.append({"line": i, "text": line.strip()[:120]})
    entry = {"src": os.path.basename(src), "dst": os.path.basename(dst),
             "bytes_in": len(txt.encode("utf-8")),
             "bytes_out": len(txt4.encode("utf-8")),
             "stale_hits": stale}
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt4)
    try:
        py_compile.compile(dst, doraise=True)
        entry["compile"] = "OK"
    except Exception as e:
        entry["compile"] = "FAIL: %s" % e
        receipt["stale_total"] += 100  # compile fail = gate fail
    receipt["files"][name] = entry
    receipt["stale_total"] += len(stale)

receipt["verdict"] = "PASS" if receipt["stale_total"] == 0 else "FAIL"
out = os.path.join(ROOT, "results", "_r767bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, indent=1, ensure_ascii=False)
print(json.dumps(receipt, indent=1, ensure_ascii=False))
raise SystemExit(0 if receipt["verdict"] == "PASS" else 1)
