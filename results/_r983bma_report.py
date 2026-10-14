# -*- coding: utf-8 -*-
"""r983 bm-a: append round report line (per-machine file)."""
import datetime

now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
row = (
    f"| {now} | r983 | bm-a takeover of dead r983-era session (died 11:18 post-orders-scan pre-closeout; "
    "orphan probe 0/38 faces) + **W238 PREREG FROZEN+DELIVERED** (research/PERPETUAL_N1_W238_PREREG.md 27558B, "
    "47 SUB pairs from frozen W237 template d311a5439, derive_v2 r982-count-fixes (5 assert counts: "
    "538_204..538_403 x3->x2 / PERPETUAL_N1_W238 x1->x2 / 98th x2->x4 / 122nd x1->x2 / 945,189 x2->x3) "
    "re-derived full fail-closed assert PASS + receipt facts ledger 945,189 / K 519,320 / bands "
    "A 538404..540403 B 540404..540603; ignition key = this push -> W238 splice next round) + S0.5 dual-delta "
    "(ORD bde2e581->db08b85b consumed via fresh group-tree read: 10-14 tail rows all MV/BigStream/bm-c/bm-b "
    "software-copyright, zero BigMoney directives; DEC 86187eff unchanged; d19 --advance read-back OK) + "
    "smoke 49/49 + satengine ALIVE rc0 queue0 + state heal 979->983 (r861-family 4th: r980-982 estates landed "
    "but state never advanced, honest) + S6 41-leg chain detached pid 44360 (r980bmc runner clone per reuse-law) "
    "+ estate absorb (r982 assert_check + d19/daemon rolling faces) + stray root artifact quarantined | "
    "evidence: receipt _w238bma_prereg_derive_receipt.json + orders tail _r983bma_orders_tail.txt + "
    "state-bm-a.json round 983 | next: W238 five-face freeze splice (clone _w236bma_freeze_edits.py pattern) "
    "-> self-burn 12/12 -> finalize; window <=48h |"
)
with open("fleet/round_reports-bm-a.md", "a", encoding="utf-8", newline="") as fh:
    fh.write("\n" + row + "\n")
print("report row appended, len", len(row))
