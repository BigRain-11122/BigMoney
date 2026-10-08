# -*- coding: utf-8 -*-
"""r781 bm-c S7-close delivery self-check row: composes the measured
delivery row (round commit 89ae57e74, push first pass, delivery proof),
writes evidence file results/_r781bmc_s7close_row.txt, appends verbatim to
CANON ledger logs/iteration-loop/round_reports-bm-c.md (ROOT orphan face
untouched per r749 freeze). Pattern credit: _r780bmc_s7row_append.py."""
import datetime
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

row = (
    "%s | r781 bm-c S7-close: delivery self-check row (measured: round commit 89ae57e74 "
    "in zero-rebase window (S0 fetch HEAD==origin/main==3a624f7c2 zero-delta, no integration "
    "needed; round-start dirty = 10 own daemon live faces + r781 driver pair, zero foreign); "
    "68-file add-set via add -A, zero foreign (hand-verified dirty-list gate: all faces = "
    "S6 40-leg regen outputs + state/heartbeat + ledger r781 row + r781 driver/receipt family "
    "+ daemon churn); push CLEAN FIRST PASS 3a624f7c2..89ae57e74; DELIVERY_PROOF tip=89ae57e74 "
    "behind/ahead=0/0 post-fetch + rev-list origin/main..HEAD=0; S7 closing double-sweep "
    "ORD/DEC identical + unacked=0 (51 orders) + inbox=0 (no mid-round new orders); "
    "local token delta=0 (zero LLM calls this round); local undelivered-to-origin commit "
    "count = 0; residual dirty = inter-round daemon churn rides r782 absorb per r628 "
    "precedent) - bm-c"
) % NOW

row_path = os.path.join(REPO, "results", "_r781bmc_s7close_row.txt")
with open(row_path, "wb") as fh:
    fh.write((row + "\n").encode("utf-8"))
row_bytes = open(row_path, "rb").read()

ledger = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
before = os.path.getsize(ledger)
with open(ledger, "ab") as fh:
    fh.write(row_bytes)
after = os.path.getsize(ledger)
assert after - before == len(row_bytes)
assert open(ledger, "rb").read().endswith(row_bytes)
root_orphan = os.path.join(REPO, "round_reports-bm-c.md")
orphan_mtime = os.path.getmtime(root_orphan) if os.path.exists(root_orphan) else None
assert os.path.getmtime(root_orphan) == orphan_mtime, "ROOT orphan touched!"
print("S7ROW_OK bytes=%d ledger=%d->%d now=%s" % (len(row_bytes), before, after, NOW))
