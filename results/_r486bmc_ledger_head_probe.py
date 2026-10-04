"""r486 bm-c ledger-head composition probe (one-shot, disclosure):
print sg.ledger_head() full dict + the last few ledger blocks with their
source files, to honestly disclose the N_eff basis used by w3 judge
finalize (live head law: never hand-copy constants; r685 quarantine-skip
fix must be active). ASCII output only."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates as sg  # noqa: E402

head = sg.ledger_head()
print("ledger_head:", json.dumps(head, ensure_ascii=False)[:600])

# last blocks: science_gates ledger is distributed across product jsons;
# use the internal scanner if exposed, else glob the trials ledger file(s)
for attr in ("ledger_blocks", "ledger_scan", "active_voids"):
    if hasattr(sg, attr):
        v = getattr(sg, attr)
        if callable(v):
            try:
                r = v()
                print(attr, "():", json.dumps(r, ensure_ascii=False)[:800])
            except Exception as e:
                print(attr, "() raised:", e)
        else:
            print(attr, "=", json.dumps(v, ensure_ascii=False)[:800])

# direct: results/trials_ledger*.json tail if exists
import glob
for p in glob.glob(os.path.join(ROOT, "results", "*ledger*.json")):
    try:
        d = json.load(open(p, encoding="utf-8"))
        print("---", os.path.basename(p), "keys:", list(d)[:10] if isinstance(d, dict) else type(d))
        if isinstance(d, dict) and "blocks" in d:
            for b in d["blocks"][-5:]:
                print("  block:", json.dumps(b, ensure_ascii=False)[:220])
        elif isinstance(d, dict) and "total" in d:
            print("  total:", d.get("total"), "prev:", d.get("prev_total"),
                  "batch:", d.get("batch"), "file:", d.get("file_name"))
    except Exception as e:
        print("---", p, "read fail:", e)
