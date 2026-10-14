# -*- coding: utf-8 -*-
import io, json, datetime, hashlib
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
sync = {"ahead_behind": "0/0", "origin_tip": "f597934fa", "ts": now,
        "note": "r985: W238 closeout push 50fa77623..f597934fa verified (range line + ls-tree x3 + behind-0); local-not-at-origin commit count=0"}
for p in ("state-bm-a.json", "fleet/machines/bm-a.json"):
    d = json.load(io.open(p, encoding="utf-8"))
    d["sync"] = sync
    d["push_verified"] = sync
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("SYNC-FACE-OK", now)
