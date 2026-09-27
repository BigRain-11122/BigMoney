# -*- coding: utf-8 -*-
"""R307 bm-a: T-91 claim-and-start (CEO immediate-law O-1730; order O-20260926-2340 caught by S7 double-scan)."""
import json, io, datetime

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")

# F-04 MSG first (declaration before claim commit)
msg = {
    "id": "MSG-20260927-0908-bm-a-t91-claim",
    "from": "bm-a",
    "to": "ALL",
    "ts": ts,
    "type": "F-04-claim-declaration",
    "subject": "T-91 claim-and-start (live paper exercise lane, O-20260926-2340)",
    "body": ("bm-a OS loop R307 S7 double-scan caught O-2026-09-26-2340 (overnight CEO order, GM "
             "convergence revision landed 09:03) + T-91 open/unclaimed. Per O-1730 immediate-law "
             "claim-and-start same round: bm-a claims T-91 (s1 live harness + s2 REV-OSC paper account; "
             "s3 auto-fires Monday 09:15; s4 report wiring). Anti-dup honored: T-90=bm-b chain E2E, "
             "T-89=bm-b market-stage stats, REV-OSC judged batch=already ran overnight no re-judge. "
             "Claim commit follows this MSG seconds-level."),
}
with io.open(r"fleet\inbox\MSG-20260927-0908-bm-a-t91-claim.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(msg, fh, ensure_ascii=False, indent=1)

P = r"fleet\tasks\T-2026-09-27-91-P1.json"
d = json.load(open(P, encoding="utf-8"))
assert d["status"] == "open", d["status"]  # fail-closed on dual-claim collision
d["status"] = "claimed"
d["claimed_by"] = ("bm-a (OS iteration loop R307 S7 double-scan catch, claim-and-start same round per "
                   "O-20260924-1730 immediate-law; F-04 MSG-20260927-0908 first; s1 live harness + s2 REV-OSC "
                   "paper account start now; s3 auto-fires 2026-09-28 09:15)")
d["claimed_at"] = ts
d["progress_r307_bma"] = ("r307 claim-and-start: order O-2026-09-26-2340 read + lane-separation acknowledged "
                          "(T-90/T-89 stay bm-b; REV-OSC judged batch not re-judged) + SYSTEM_V1_PREREG.md "
                          "five-layer spec + O-2045 paper machinery reuse faces being read this round; "
                          "s1 harness build starts now (weekend-legal per ticket note)")
with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
d2 = json.load(open(P, encoding="utf-8"))
assert d2["status"] == "claimed" and "bm-a" in d2["claimed_by"]
print("T-91 claimed by bm-a at", ts)
