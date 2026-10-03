import json
import datetime

# state: round_no 646 -> 648 (r647 adoption note in round report)
d = json.load(open("state-bm-a.json", encoding="utf-8"))
d["round_no"] = 648
d["last_round_at"] = "2026-10-03T23:58:30+08:00"
d["last_round_ts"] = "2026-10-03T23:58:30+08:00"
json.dump(d, open("state-bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("state round_no ->", d["round_no"])

# heartbeat: bm-a own file only; epoch must be JSON int + clock T-separated
now = datetime.datetime.now().astimezone()
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
h["last_seen"] = now.isoformat(timespec="seconds")
h["round_no"] = 648
h["current_task"] = ("r648 closed: G2_SLOT_MON_P2 sec.9 freeze window "
                     "(prereg FROZEN + seed 20570000 + probe 6/6 PASS + "
                     "gate ADMIT + T-2026-10-03-164-P1 claimed); next slice "
                     "= runner build + burn + verdict finalize")
h["heartbeat_epoch_utc"] = int(__import__("time").time())
h["clock_read"] = now.isoformat(timespec="seconds")
json.dump(h, open("fleet/machines/bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# self-verify: epoch int + clock T-sep (R170/R178/R262 law)
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"][:19], "clock not T-separated"
print("heartbeat verified: epoch int =", chk["heartbeat_epoch_utc"],
      "| clock =", chk["clock_read"])
