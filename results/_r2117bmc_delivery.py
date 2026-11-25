# -*- coding: utf-8 -*-
"""r2117 delivery note: state key + one report row (send verification)."""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TEXT = ("commit **29999df1f3** pushed to origin/main (1ee5b2df57..29999df1f3); after fetch "
        "`git rev-list --left-right --count origin/main...HEAD` = **0/0**; "
        "`git ls-tree -r --name-only origin/main` sees the three new paths "
        "(scripts/minute_feed_first_reader.py, results/minute_feed_first_reader.json, "
        "research/MINUTE_FEED_FIRST_READER.md) plus Tools/s6_chain_bmc.py, the two bookkeeping "
        "faces and five closeout helpers -> 本地未达 origin commit 数=0")

raw = io.open("state-bm-c.json", "rb").read()
st = json.loads(raw.decode("utf-8"))
assert json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8") == raw, "state format drift"
st["送达自证_r2117"] = TEXT
io.open("state-bm-c.json", "wb").write(
    json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8"))

row = ("| 2026-11-26T05:12:00+08:00 | r2117-delivered | bm-c | 送达补记：" + TEXT + " |\n")
with io.open("logs/iteration-loop/round_reports-bm-c.md", "ab") as f:
    f.write(row.encode("utf-8"))
print("delivery note written")
