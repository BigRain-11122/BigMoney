# -*- coding: utf-8 -*-
"""r808 bm-a closeout: state bump, heartbeat, RR line, decisions watermark, CODELY pit append.
Fresh read-modify-write per multi-writer law (r10-06); no replace-tool use on shared ledgers."""
import json, io, time, datetime, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%d %H:%M:%S")
ISO = NOW.astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
DEC_SHA = "635c3024a95e4487a08e55be9dad3a97e41c73726a9d82d955986d95ef6f6af6"

# 1) state-bm-a.json: round bump + watermark
s = json.load(open("state-bm-a.json", encoding="utf-8"))
s["round_no"] = 808
s["last_decisions_sha"] = DEC_SHA
io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(s, ensure_ascii=False, indent=2) + "\n")

# 2) heartbeat fleet/machines/bm-a.json
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = ISO
h["current_task"] = "r808 closeout: S0 double-rebase crash-recovery surgery + W168 prereg/r807 closeout landed origin"
h["cpu_cores"] = 32
h["ram_free_gb"] = 55.6
h["gpu_free_vram_gb"] = 5.8
h["verdict"] = "ok"
h["heartbeat_epoch_utc"] = EPOCH  # int, R170/R178 law
h["clock_read"] = ISO            # T-separated, R262 law
h["ts"] = ISO
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(h, ensure_ascii=False, indent=2) + "\n")
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (smoke F7)"

# 3) round report line
rr = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    f"\n| {TS} | r808 | S0 crash-recovery surgery: dead r807 session's stale rebase cured "
    f"(edit-state + sequencer false 'edit all merge conflicts' blocker bypassed via manual commit from "
    f"author-script+message; churn-absorb x3 live-daemon race; skipped 2 superseded picks) -> r807 closeout "
    f"(79f) + W168 prereg landed origin 65b062839..03838491a; 2nd rebase vs bm-b r794 takeover resolved "
    f"(25-face newer-wins origin 04:18-20 vs dead-session 04:04-06); S0.5 orders 0 unacked; dec 635c3024 "
    f"D-20261007-01/02/03 consumed zero BigMoney dispatch, D-20261002-06 criterion MET (CODELY 28,655B<=30,720B "
    f"ahead of 10-09 window); S1 smoke 48/48; S2 boards 0 open engine alive idle pool 3 live (2 FUND ready "
    f"owner=bm-b + W14 waiting); S6 38/38 rc0 103s dualrun streak 51; S7 4-piece green + attrition CLEAN x4 "
    f"| push 03838491a verify=ls-tree; chain outputs in results; smoke 48/48 | next: W168 burn ignition "
    f"check via pool/autofill + trial-labor standing line |\n"
)
with io.open(rr, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

print("closeout writes ok; round=808 epoch=", EPOCH)
