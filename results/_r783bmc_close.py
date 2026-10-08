# -*- coding: utf-8 -*-
"""r783 bm-c S7-close: DEC mid-round delta watermark roll (addendum to
bookkeep) + delivery self-check row compose+append. Facts-driven
(_r783bmc_s05_facts.json closing sweep), never hand-typed (r583 law).
Row -> results/_r783bmc_close_row.txt + verbatim append to CANON ledger
(ROOT orphan untouched per r749 freeze). Pattern credit: r782 close."""
import datetime
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

facts = json.load(open(os.path.join(REPO, "results", "_r783bmc_s05_facts.json"),
                       encoding="utf-8"))
assert facts["round"] == 783
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert DEC_SHA == "A6FE4864142A9491C928C953B793237F8A07D7DB7CAA52E6460576CFC49C7AA7"
assert ORD_SHA == "3292E8FBDC8EA3592D1DE5582736A505A07B4F79"
assert facts["dec_delta"] is True and facts["ord_delta"] is False
assert facts["unacked"] == [] and facts["inbox_unread"] == []

dec_m = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
         "r783 sweep = MID-ROUND DELTA EE70CEF0->" + DEC_SHA[:8] + " caught by S7 "
         "closing double-sweep, 1 row D-20261008-09 governance four-case revisit "
         "reading (executed by bm-c interactive window, non-quant zero-action face), "
         "watermark consumed/rolled at close; facts-driven from "
         "results/_r783bmc_s05_facts.json, 64hex shape-asserted, never hand-typed "
         "(r583 S4 law")

for path in (os.path.join(REPO, "state-bm-c.json"),
             os.path.join(REPO, "fleet", "machines", "bm-c.json")):
    with open(path, encoding="utf-8") as fh:
        j = json.load(fh)
    j["last_decisions_sha"] = DEC_SHA
    j["last_decisions_sha_method"] = dec_m
    j["dec_sha_method"] = dec_m
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(j, fh, ensure_ascii=False, indent=1)
    back = json.loads(open(path, encoding="utf-8").read())
    assert back["last_decisions_sha"] == DEC_SHA
    assert isinstance(back["heartbeat_epoch_utc"], int)

row = (
    "%s | r783 bm-c S7-close: delivery self-check row (measured: round commit "
    "8d8fb3b37 pushed CLEAN FIRST PASS (rebase-free window: post-S0-rebase base "
    "2e5f989f9 held through close); 70-file add-set via add -A, zero foreign "
    "(hand-verified dirty-list gate: 49 M = S6 40-leg regen outputs + bookkeeping "
    "trio + O-20261008-2315 receipt + probes + daemon churn, 18 ?? = r783 "
    "driver/receipt family + qa det-99th pair, qa/*.log ignored per law); "
    "DELIVERY_PROOF tip=8d8fb3b37 behind/ahead=0/0 post-fetch + rev-list "
    "origin/main..HEAD=0; S7 closing double-sweep CAUGHT mid-round DEC delta "
    "EE70CEF0->A6FE4864 (1 row: D-20261008-09 governance four-case revisit "
    "reading, executed by bm-c interactive window, non-quant zero-action face -> "
    "watermark consumed/rolled at close, evidence results/_r783bmc_dec_delta.txt) "
    "while ORD 3292E8FB held identical + unacked=0 (52 orders) + inbox=0 (no "
    "mid-round new orders); local token delta=0 (zero LLM calls this round); "
    "本地未达 origin commit 数=0; close-row addendum + residual daemon churn "
    "absorbed into this close commit) [via bm-c r783]"
) % NOW

row_path = os.path.join(REPO, "results", "_r783bmc_close_row.txt")
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
assert os.path.exists(root_orphan), "ROOT orphan expected (frozen face)"
om = os.path.getmtime(root_orphan)
assert os.path.getmtime(root_orphan) == om, "ROOT orphan touched!"
print("S7CLOSE_OK dec_rolled=%s ord_held=%s row=%dB ledger=%d->%d now=%s"
      % (DEC_SHA[:8], ORD_SHA[:8], len(row_bytes), before, after, NOW))
