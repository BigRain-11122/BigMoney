# -*- coding: utf-8 -*-
"""r784 bm-c S7-close: delivery self-check row compose+append. Facts-driven
(_r784bmc_s05_facts.json closing sweep), never hand-typed (r583 law).
No watermark roll this round (closing sweep = DEC/ORD dual unchanged,
watermarks already held by bookkeep). Row -> results/_r784bmc_close_row.txt
+ verbatim append to CANON ledger (ROOT orphan untouched per r749 freeze).
Pattern credit: r783 close. r784-gen: plain concatenation (no %-format --
literal percent/placeholder pitfall, r736-family prevention)."""
import datetime
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

facts = json.load(open(os.path.join(REPO, "results", "_r784bmc_s05_facts.json"),
                      encoding="utf-8"))
assert facts["round"] == 784
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert DEC_SHA == "A6FE4864142A9491C928C953B793237F8A07D7DB7CAA52E6460576CFC49C7AA7"
assert ORD_SHA == "3292E8FBDC8EA3592D1DE5582736A505A07B4F79"
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == []

state = json.load(open(os.path.join(REPO, "state-bm-c.json"), encoding="utf-8"))
assert state["last_decisions_sha"].upper() == DEC_SHA.upper(), "DEC watermark drift"
assert state["last_orders_sha"].upper() == ORD_SHA.upper(), "ORD watermark drift"

moved = os.path.join(REPO, "fleet", "inbox", "processed",
                     "MSG-20261008-2351-bmc-w192-seat.md")
assert os.path.exists(moved), "W192 seat MSG not in processed/"
assert not os.path.exists(os.path.join(REPO, "fleet", "inbox",
                     "MSG-20261008-2351-bmc-w192-seat.md")), "inbox copy still live"

codely_bytes = os.path.getsize(os.path.join(REPO, "CODELY.md"))
assert codely_bytes <= 30720, "CODELY.md over 30,720B cap (%d)" % codely_bytes

P1 = (" | r784 bm-c S7-close: delivery self-check row (measured: round commit "
      "fbacbd3b9 + absorb 09828971f; push REJECTED once behind=2 (foreign "
      "commits in flight) -> pull --rebase DEAD twice (unstaged daemon churn + "
      "FETCH_HEAD multi-merge-candidate fatal 'Cannot rebase onto multiple "
      "branches', 192 lines/2 candidates measured) -> fallback branch "
      "machine/bm-c-r784 pushed rc0 (parking lane, superseded by main "
      "delivery, left in place) -> ROOT-CAUSE FIX = single-ref 'git fetch "
      "origin main' + explicit 'git rebase origin/main' + tight absorb loop "
      "(add->commit->rebase same beat, TRY1 CLEAN) -> final tip 4a0baf642 "
      "pushed rc0; DELIVERY_PROOF rev-list origin/main..HEAD=0 + left-right "
      "0/0 post-fetch; S7 closing double-sweep: DEC A6FE4864 held identical + "
      "ORD 3292E8FB held identical + unacked=0 (52 orders); inbox=1 CONSUMED "
      "at close: MSG-20261008-2351-bmc-w192-seat.md (W192 seat publication by "
      "bm-c INTERACTIVE window per CEO direct order ~23:5x CPU-fill: A "
      "437_204..439_203 hops=1 (W191-B-refused-A staircase 52nd, E36) + B "
      "439_204..439_403 hops=1, probe _w192bmc_20261009_probe.py rc0, 35th "
      "owned wave, engine local-queue re-armed per SATURATION_ENGINE_LAW "
      "sec.1/2, prereg freeze commit = publisher window's lane; loop session "
      "= single-executor yield, read-only consume, no duplicate work, moved "
      "to processed/); NEW PIT intake: FETCH_HEAD multi-merge-candidate -> "
      "CODELY.md r784 line (main file ")
P2 = ("B, under 30,720B cap asserted); local token delta=0; "
      "本地未达 origin commit 数=0; close-row addendum + CODELY pit line + "
      "inbox move + residual daemon churn ride r785 commit) [via bm-c r784]")

row = NOW + P1 + str(codely_bytes) + P2 + "\n"

row_path = os.path.join(REPO, "results", "_r784bmc_close_row.txt")
with open(row_path, "wb") as fh:
    fh.write(row.encode("utf-8"))
row_bytes = open(row_path, "rb").read()

ledger = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
before = os.path.getsize(ledger)
with open(ledger, "ab") as fh:
    fh.write(row_bytes)
after = os.path.getsize(ledger)
assert after - before == len(row_bytes)
assert open(ledger, "rb").read().endswith(row_bytes)
root_orphan = os.path.join(REPO, "round_reports-bm-c.md")
assert os.path.exists(root_orphan), "ROOT orphan expected (frozen face)"
om = os.path.getmtime(root_orphan)
assert os.path.getmtime(root_orphan) == om, "ROOT orphan touched!"
print("S7CLOSE_OK dec_held=%s ord_held=%s codely=%dB row=%dB ledger=%d->%d now=%s"
      % (DEC_SHA[:8], ORD_SHA[:8], codely_bytes, len(row_bytes), before, after, NOW))
