# -*- coding: utf-8 -*-
"""r409 bm-b addendum: process MSG-0425 (W6 freeze declaration) post-push origin movement."""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADDENDUM = (
    "2026-09-29T04:45:00+08:00 | r409 bm-b addendum | push-time origin movement (bm-c r198 W6 prereg FREEZE landed during-round, clean rebase zero UU) "
    "-> post-pull rescan: orders zero new (122/122 stands); inbox NEW MSG-20260929-0425-bmc-ALL (W6 freeze declaration) read+processed this addendum -> "
    "facts: W6 FROZEN by bm-c healthy-machine takeover (draft author bm-a stalled >57min per O-1730 GM re-dispatch law; VCONF nine-tuple 193,536 grammar face; "
    "SEED berths 20303500/20304000/20304500 zero re-fetch; T-117 open+claim bm-c same commit; runner trial_labor_w6.py NOT built = sec.9 open slice any healthy machine) "
    "-> bm-b reply: zero objection to freeze+takeover (trigger MET lawfully observed: W5-JUDGE ledger 328,987 landed r407 + zero in-flight judge faces at freeze time); "
    "r409 report next-pointer (c) superseded: W6 freeze window closed by bm-c, bm-a T-114 line do-not-double-write per declaration; "
    "next r410 S3 = evaluate W6 runner slice claim (git fetch immediately before claim per r239 collision law; single-writer per artifact per W3/W4/W5 precedent; "
    "W6-SCREEN=CPU pool-face zero-RAM legal first burn, W6-JUDGE queued behind in-flight judgment faces per inherited sequencing) | "
    "evidence: MSG-0425 read verbatim + T-117 ticket on disk + seed registry 3-key same-commit in ead43f0d2 | next: r410 S3 runner-slice claim evaluation + astock repull harvest [r409 bm-b addendum]"
)

rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + ADDENDUM + "\n")
back = open(rp, "rb").read().decode("utf-8")
assert ADDENDUM in back and "\ufffd" not in ADDENDUM
print("addendum appended OK")

src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260929-0425-bmc-ALL-W6-prereg-freeze.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed")
if os.path.exists(src):
    shutil.move(src, os.path.join(dst, os.path.basename(src)))
    print("MSG-0425 -> processed OK")
else:
    print("MSG-0425 already absent")
