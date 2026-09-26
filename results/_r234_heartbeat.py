# -*- coding: utf-8 -*-
"""R234 bm-a S7: heartbeat update (epoch as JSON int per R170/R178 law, self-verify after write)."""
import json
import time

path = "fleet/machines/bm-a.json"
hb = json.load(open(path, encoding="utf-8-sig"))
epoch = int(time.time())
hb["machine_id"] = "bm-a"
hb["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["current_task"] = ("r234 done: T-72 s2 pull supervised healthy (4927/5228 @08:12, zero failures, "
                      "QC 6/6, ETA ~08:26); acceptance RUN at pull-completion round (~R235-236)")
hb["round_no"] = 234
hb["heartbeat_epoch_utc"] = epoch          # JSON int per F7/R170/R178
hb["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["verdict"] = "GREEN"
# orders_ack unchanged (74/74 zero-diff verified twice this round)
with open(path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# post-write self-verification
chk = json.load(open(path, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat written; epoch int ok:", chk["heartbeat_epoch_utc"], chk["clock_read"])
