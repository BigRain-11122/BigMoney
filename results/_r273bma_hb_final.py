# r273 bm-a final heartbeat: orders_ack mechanical regeneration 84->85 (O-20260926-2229 processed),
# current_task/verdict reflect T-84 claim + s1 physical hold. Byte-face: no-BOM/CRLF/indent=1/no-trail-NL.
# r74/r33 laws: ack regenerated from directory, string form, full filenames incl .md (r220 law).

import json, time, datetime, glob, os

p = "fleet/machines/bm-a.json"
h = json.load(open(p, encoding="utf-8-sig"))
tokens = sorted(os.path.basename(x) for x in glob.glob("fleet/orders/O-*.md"))
h["orders_ack"] = " ".join(tokens)
now = datetime.datetime.now()
h["last_seen"] = now.strftime("%Y-%m-%d %H:%M")
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = now.astimezone().isoformat()
h["current_task"] = ("T-84 v6.0 convergence s1 lane (claimed r273 per O-2229 immediate law): "
                     "reachability probe delivered, code audit physically held -- no D: drive on box, "
                     "resume on re-mount/TRANSFER/lane-handover; s2-s4 unaffected")
out = json.dumps(h, ensure_ascii=False, indent=1)
open(p, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
back = json.load(open(p, encoding="utf-8-sig"))
assert isinstance(back["heartbeat_epoch_utc"], int)
assert "T" in back["clock_read"]
assert back["orders_ack"].split() == tokens and len(tokens) == 85
print("heartbeat final: 85 ack tokens, epoch int", back["heartbeat_epoch_utc"])
