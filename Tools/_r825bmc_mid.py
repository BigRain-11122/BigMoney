# -*- coding: utf-8 -*-
"""r825 bm-c mid-round: absorb dead-r824 round number into state (QA driver
reads state.round_no+1; dead r824 session never advanced state), claim
T-181 ticket, and probe psutil available RAM for QA-driver go/no-go."""
import datetime
import json
import os

import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# 1) state round_no 823 -> 824 (dead predecessor r824 absorb; this session = r825)
sp = os.path.join(ROOT, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8-sig"))
assert s.get("round_no") == 823, f"unexpected round_no {s.get('round_no')}"
s["round_no"] = 824
s["round_no_label"] = "r824 (dead-predecessor absorb marker; live session = r825)"
s["note"] = (TS + " | r824-dead-absorb: predecessor session (r824) died mid-round "
             "after 4+ commits (claim/churn/merge/daemon) without state/ledger "
             "close; this transient state bump lets the QA driver round-read "
             "(+1) label this live session's pack r825. Close script will set "
             "round_no=825 with full ledger.")
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(s, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state round_no -> 824 (absorb marker)")

# 2) claim T-181
tp = os.path.join(ROOT, "fleet", "tasks", "T-2026-10-10-181-P1.json")
t = json.load(open(tp, encoding="utf-8-sig"))
assert t.get("status") == "open", f"T-181 status {t.get('status')} (collision!)"
t["status"] = "claimed"
t["claimed_by"] = "bm-c"
t["claimed_at"] = TS
t["notes"] = (t.get("notes", "") + " | progress_r825_bmc: claimed as wm-red "
              "runnable-work remediation (only open ticket; claim+start same "
              "round). Deliverable this round = prereg DRAFT v0 "
              "(research/THERMO_OVERLAY_P1.md, DRAFT-NOT-FROZEN: BAN-05 "
              "exception face + alpha candidates + cutoff anchors + exit-axis "
              "declaration). Freeze gate + F-04 inbox MSG + runner = next "
              "rounds. RAM-guard: CEO-order training in flight (0.5GB free), "
              "draft is text-face only, zero burn this round.")
with open(tp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("T-181 claimed by bm-c @", TS)

# 3) psutil available RAM
av = psutil.virtual_memory().available / 1024 ** 3
print("psutil_available_gb", round(av, 2))
print("GO_QA_DRIVER" if av >= 1.5 else "NO_QA_DRIVER_RAM_GUARD")
