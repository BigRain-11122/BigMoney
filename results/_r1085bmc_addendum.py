# -*- coding: utf-8 -*-
# r1085 addendum: S7 tail dual-scan caught DEC delta -> consumed same-window (receipt-column backfill on
# already-consumed D-20261016-06, zero new obligations) + watermark advance 1d4741e4 -> 0ad85a30.
# r991 addendum precedent (mid-round arrival consumed + disclosed, counter unchanged).

import datetime
import hashlib
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = r"K:\Fluxgroup\FluxGroup"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")

# recompute pinned-method sha (raw-blob bytes SHA-256)
r = subprocess.run(["git", "-C", G, "show", "origin/main:docs/decisions.md"],
                   capture_output=True, timeout=120)
dec_sha = hashlib.sha256(r.stdout).hexdigest()
assert dec_sha == "0ad85a305830dc2f43c8be7db1ccecf2ef2078a3b55224cf7aecca74db51340c", \
    "dec sha drifted since tail scan: %s" % dec_sha

state_path = os.path.join(ROOT, "state-bm-c.json")
state = json.load(io.open(state_path, encoding="utf-8"))
assert state["round_no"] == 1086, "counter drift: %r" % state["round_no"]
assert state["last_decisions_sha"] == "1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1"

state["last_decisions_sha"] = dec_sha
state["last_decisions_read_at"] = TS
state["last_decisions_seen"] = TS
state["last_decisions_at"] = TS
state["ts"] = TS
state["updated"] = TS
state["updated_at"] = TS
state["now_active"] = TS
state["r1085_closeout_note"] = state.get("r1085_closeout_note", "") + (
    " || ADDENDUM: S7 tail dual-scan caught DEC DELTA (1d4741e4->" + dec_sha[:16] +
    "...): group commit beda8d2 09:08:51 (bm-a CEO-PROXY R2.17 晨检双销) = receipt-column BACKFILL on the "
    "already-consumed D-20261016-06 row (三任务 pause 复开缺口复测: \\Bigmoney-Autofill/\\Bigmoney-ResidentDispatcher/"
    "\\HQ-OllamaOrphanWatch all-Disabled 10-16 12:01 实测记录) -- judged ZERO new bm-c obligation: historical audit "
    "face; current live state consistent with the 10-18 00:3x CEO selective-restore order (ResidentDispatcher alive "
    "PID 40972; Ollama 族 not-restored per O-20261017-0953 LLM retirement); ORD tail FALSE-hold unchanged "
    "(8f6162d9); watermark advanced same-window read-back verified"
)
state["orders_ack_receipt"] = state.get("orders_ack_receipt", "") + (
    " || r1085 addendum: DEC delta consumed same-window (beda8d2 receipt-backfill on consumed D-20261016-06, "
    "zero new obligation, watermark advanced 1d4741e4->" + dec_sha[:16] + ".)"
)
state["verify"] = state.get("verify", "") + (
    " || addendum: dec sha read-back full-equality " + dec_sha[:16] + ". via pinned raw-blob sha256 method"
)
io.open(state_path, "w", encoding="utf-8", newline="").write(
    json.dumps(state, ensure_ascii=False, indent=1) + "\n")

hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb["last_decisions_seen"] = TS
hb["ts"] = TS
io.open(hb_path, "w", encoding="utf-8", newline="").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

# readback
s2 = json.load(io.open(state_path, encoding="utf-8"))
assert s2["last_decisions_sha"] == dec_sha
print("addendum OK: dec watermark 1d4741e4 -> %s (read-back equal), ts=%s" % (dec_sha[:16], TS))
