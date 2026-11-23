"""r2009 supplement: put the three CEO-facing lines on the heartbeat (rule 5) -- what is
running, what landed, what is next within 48h -- and mirror them on the state face.
"""
import datetime
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
FIELDS = os.path.join(ROOT, "results", "_r2009bmc_heartbeat_fields2.json")

now = datetime.datetime.now().astimezone().replace(microsecond=0)
iso = now.isoformat()
epoch = int(time.time())

ARTIFACT = os.path.join(ROOT, "research", "ETF_BOOK_NOBOND_TICKET.md")
MILESTONE = ("(a) wire this face to the S6 chain + two smoke legs once the contention window "
             "closes (<=48h); (b) read it against etf_book_capacity_at_size so 13-15% of NAV per "
             "name is judged placeable or not (<=48h)")

with open(STATE, encoding="utf-8") as f:
    st = json.load(f)
st["last_artifact"] = "research/ETF_BOOK_NOBOND_TICKET.md + results/etf_book_nobond_ticket.json + scripts/etf_book_nobond_ticket.py"
st["last_artifact_at"] = iso
st["next_milestone"] = MILESTONE
st["failed_this_round"] = ("nothing failed; two self-inflicted reds were caught by this round's own "
                           "check before publishing (weights+cash summed to 0.999999 at 6dp, and the "
                           "printed scale differed from the scale used to size the cash slot)")
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

fields = {
    "last_seen": iso,
    "ts": iso,
    "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "last_artifact": os.path.basename(ARTIFACT),
    "last_artifact_at": iso,
    "next_milestone": MILESTONE,
    "activity_now": st["activity_now"],
    "agenda_starved": False,
    "idle_rounds": 0,
}
with open(FIELDS, "w", encoding="utf-8") as f:
    json.dump(fields, f, ensure_ascii=False, indent=1)

hb = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "heartbeat_write.py"),
                     "apply", "--fields", FIELDS], capture_output=True, text=True)
print("heartbeat rc", hb.returncode)
print((hb.stdout or "").strip()[:500])
print("state round_no", st.get("round_no"), "artifact", st["last_artifact"][:60])
