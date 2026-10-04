# -*- coding: utf-8 -*-
"""r687 bm-a addendum: report addendum line (marker gate) + orders S7 rescan
(same-form set-diff)."""
import json, os, io

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PATH = REPO + r"\round_reports-bm-a.md"
MARK = "r687 (bm-a) addendum"
txt = io.open(PATH, encoding="utf-8").read()
assert txt.count(MARK) == 0, "addendum already present"

line = (
    "2026-10-04T17:1x+08:00 | r687 (bm-a) addendum | close-window merge "
    "origin r485 wave DELIVERED 64a508e30 (bm-c W3 judge enrollment: prep "
    "PASS 777 cells = 785 survivors - 8 collapse; 21 regen faces ours-newer "
    "per-face ts probe r484-inverted precedent; pool + w3_judge_state "
    "theirs-canonical) | SAME-ROUND claim-and-start honored per O-1730: "
    "autofill tick claimed w3-judge-2of4 owner=bm-a (commit 03f7ac259 "
    "self-pushed) + burn LAUNCHED pid 26224 detached multiproc (verified "
    "alive via CIM full-scan second form r661; launch ts 17:15:02, "
    "fullburn_window=true) | shard allocation: 0=bm-c, 1=bm-b, 2=bm-a "
    "burning; shard-3 left to capacity-ledger/daemons (no force-claim per "
    "CEO 10% CPU margin law) | verdict面 777 cells dual-nulls B=2000/P=2000 "
    "per cell, seed 20285600 canonical | 记分 unchanged 2 | 本地未达 origin "
    "commit 数: 0 (claim commit tick-self-pushed, DELIVERED)"
)
with io.open(PATH, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + line + "\n")
txt2 = io.open(PATH, encoding="utf-8").read()
assert txt2.count(MARK) == 1

# orders S7 rescan
odir = os.path.join(REPO, "fleet", "orders")
files = sorted(f for f in os.listdir(odir)
               if f.startswith("O-") and f.endswith(".md"))
hb = json.load(io.open(os.path.join(REPO, "fleet", "machines", "bm-a.json"),
                       encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
unacked = [f for f in files if f not in ack]
with io.open(REPO + r"\results\_r687bma_orders_rescan.json", "w",
             encoding="utf-8") as f:
    json.dump({"files_total": len(files), "unacked": unacked,
               "ack_total": len(ack)}, f, ensure_ascii=False, indent=1)
print("addendum OK; orders rescan: %d files, %d unacked" % (len(files),
                                                            len(unacked)))
