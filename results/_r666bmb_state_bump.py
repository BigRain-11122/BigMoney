# -*- coding: utf-8 -*-
# r666 bm-b state.json round increment (r645: programmatic json.dump + json.loads self-verify)
import json, io, datetime

p = "state.json"
d = json.load(io.open(p, encoding="utf-8"))
d["round_no"] = 666
d["last_round_at"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["round_no_label"] = ("bm-b round 666 (golden-week watch; trio V717/Q552/D405 of 2000 @~28/hr; "
                       "S6 all-green; bm-a recovered faces auto-returned)")
d["last_decisions_read_at"] = d["last_round_at"]
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
# self-verify
chk = json.loads(io.open(p, encoding="utf-8").read())
assert chk["round_no"] == 666 and isinstance(chk["round_no"], int), "round_no verify failed"
print("state.json round_no ->", chk["round_no"], "verify OK")
