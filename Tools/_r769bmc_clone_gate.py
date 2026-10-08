# -*- coding: utf-8 -*-
"""r769 bm-c clone gate: create _r769bmc_{s05,s6,qa_ignite}.py via
double-mode replacement + credit re-point. Sources: s05 from _r767bmc_s05.py
(r768 generation absent in the triple-crash continuation window -- 2-gen jump
disclosed here), s6/qa_ignite from _r768bmc_*.py (immediate predecessors).
qa_ignite docstring collision-probe line re-stamped with the r769 probe fact
(qa/smoke-r769.md NOT on origin/main at 17:5x -> no collision, first
registration; counter stays at case #6). Stale scan with credit/law-family
exclusions (r736 clone law), py-compile each clone, receipt ->
results/_r769bmc_clone_receipt.json.
Pattern credit: Tools/_r767bmc_clone_gate.py (canonical clone gate shape)."""
import json
import os
import py_compile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
JOBS = [
    {"name": "s05", "src_gen": "767", "prev": "767",
     "credit_from": "_r766bmc_", "credit_to": "_r767bmc_"},
    {"name": "s6", "src_gen": "768", "prev": "768",
     "credit_from": "_r767bmc_", "credit_to": "_r768bmc_"},
    {"name": "qa_ignite", "src_gen": "768", "prev": "768",
     "credit_from": "_r767bmc_", "credit_to": "_r768bmc_"},
]
EXCLUDE_MARKS = ("_r767bmc_", "_r768bmc_", "Pattern credit", "law family",
                 "credit:", "Pre-ignite collision probe")
NEW_PROBE = ("Pre-ignite collision probe result: qa/smoke-r769.md NOT on "
             "origin/main (r769 probe 17:5x) -> no collision, first "
             "registration by bm-c; collision case counter stays #6 "
             "(r761/r764/r766/r767/r768 canon unchanged).")
receipt = {"round": 769, "mode": "double-replacement + credit re-point",
           "files": {}, "stale_total": 0}

for job in JOBS:
    name, g = job["name"], job["src_gen"]
    src = os.path.join(ROOT, "Tools", "_r%sbmc_%s.py" % (g, name))
    dst = os.path.join(ROOT, "Tools", "_r769bmc_%s.py" % name)
    txt = open(src, encoding="utf-8").read()
    txt2 = txt.replace("_r%sbmc_" % g, "_r769bmc_")
    txt3 = txt2.replace(g, "769")
    txt4 = txt3.replace(job["credit_from"], job["credit_to"])
    if name == "s05":
        # 2-generation jump disclosure (r768 s05 absent, crash window)
        txt4 = txt4.replace(
            '"""r769 bm-c S0.5 facts probe',
            '"""r769 bm-c S0.5 facts probe (2-gen jump, source=_r767bmc_ '
            'immediate-but-one: intermediate generation absent in '
            'triple-crash continuation window, disclosed r769)', 1)
    if name == "qa_ignite":
        lines = txt4.splitlines(True)
        for i, ln in enumerate(lines):
            if "Pre-ignite collision probe result:" in ln:
                lines[i] = NEW_PROBE + "\n"
        txt4 = "".join(lines)
    stale = []
    for i, line in enumerate(txt4.splitlines(), 1):
        if g in line:
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
        receipt["stale_total"] += 100
    receipt["files"][name] = entry
    receipt["stale_total"] += len(stale)

receipt["verdict"] = "PASS" if receipt["stale_total"] == 0 else "FAIL"
out = os.path.join(ROOT, "results", "_r769bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, indent=1, ensure_ascii=False)
print(json.dumps(receipt, indent=1, ensure_ascii=False))
raise SystemExit(0 if receipt["verdict"] == "PASS" else 1)
