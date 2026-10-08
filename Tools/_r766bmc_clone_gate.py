"""r766 bm-c lineage clone gate: scan the r766 clone faces for stale
prior-round (765) references (pattern-credit paths / law-family citations
excluded as legal), py_compile each face, write receipt
results/_r766bmc_clone_receipt.json. r736 pit law: cloned tools must carry
their new round identity everywhere. Receipt face credit:
results/_r765bmc_clone_receipt.json (stale764=0 precedent)."""
import json
import os
import py_compile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["Tools/_r766bmc_s05.py", "Tools/_r766bmc_s6.py",
         "Tools/_r766bmc_qa_ignite.py"]
PREV = "765"
EXCLUDE_MARKS = ("_r765bmc_", "Pattern credit", "law family", "credit:")

receipt = {"round": 766, "prev_scan": PREV, "files": {}, "stale_total": 0}
for f in FILES:
    p = os.path.join(ROOT, f)
    txt = open(p, encoding="utf-8").read()
    hits = []
    for i, line in enumerate(txt.splitlines(), 1):
        if PREV in line:
            if any(m in line for m in EXCLUDE_MARKS):
                continue
            hits.append({"line": i, "text": line.strip()[:120]})
    entry = {"stale_hits": hits}
    try:
        py_compile.compile(p, doraise=True)
        entry["compile"] = "OK"
    except Exception as e:
        entry["compile"] = "FAIL: %s" % e
        receipt["stale_total"] += 100  # compile fail = gate fail
    receipt["files"][f] = entry
    receipt["stale_total"] += len(hits)

receipt["verdict"] = "PASS" if receipt["stale_total"] == 0 else "FAIL"
out = os.path.join(ROOT, "results", "_r766bmc_clone_receipt.json")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, indent=1, ensure_ascii=False)
print(json.dumps(receipt, indent=1, ensure_ascii=False))
raise SystemExit(0 if receipt["verdict"] == "PASS" else 1)
