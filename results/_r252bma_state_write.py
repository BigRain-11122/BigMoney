# -*- coding: utf-8 -*-
"""R252 bm-a: state round_no + heartbeat update (byte-mirror, int epoch law)."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
stamp = now.strftime("%Y-%m-%d %H:%M")
clock_read = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---- state-bm-a.json ----
P = "state-bm-a.json"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
bom = raw[:3] == b"\xef\xbb\xbf"
d = json.loads(raw.decode("utf-8-sig"))
d["round_no"] = 252
d["did"] = ("R252: autofill fuse-starvation fix (skip-loop+S16e, 26/26) unblocked ROT "
            "launch 14:50:27; CN-DIV-LOWVOL-ROT-P1 landed 14:50:53 -> harvest gate PASS "
            "-> pool done + prereg s7/s8 + attrition row 44 -> verdict NEGATIVE 0/4 "
            "G1'v2 (best W252_bare 0.7371 < 0.9527); P0 ledger chain break found+repaired "
            "(5 products key-canonicalized, head 185798->186192 true, 6 runner sites "
            "fixed, judgment faces byte-untouched, science_gates 35/35 + smoke 25/25); "
            "post_review rows registered, reviewer 19 YES/0 NO")
d["verdict"] = "GREEN"
d["next"] = ("T-73 s3 remaining models (CORE-SAT satellite supply absent; REGIME-POLICY "
             "s2 research-first; GRID-SLEEVE combo prereg open); T80 anchor adjudication "
             "with bm-b (fused, refusal counter visible, no re-burn); 09-28 new-bar chain; "
             "10-01 month trio + v3 date gate; T-70 10-09")
d["ts"] = stamp
d["last_round_ts"] = d.get("updated_at") or stamp
d["updated_at"] = stamp
d["current_task"] = ("R252 done: autofill anti-starvation fix + ROT batch harvested "
                     "(negative, 0/4) + ledger chain repair head->186192 + 2 post_review "
                     "rows YES; next = s3 remaining models + T80 bm-b adjudication")
out = json.dumps(d, ensure_ascii=False, indent=1)
data = out.encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as fh:
    fh.write(data)

# ---- fleet/machines/bm-a.json (own file only) ----
M = "fleet/machines/bm-a.json"
raw = open(M, "rb").read()
crlf = b"\r\n" in raw
bom = raw[:3] == b"\xef\xbb\xbf"
m = json.loads(raw.decode("utf-8-sig"))
m["last_seen"] = stamp
m["current_task"] = d["current_task"]
m["task"] = d["current_task"]
m["verdict"] = "alive"
m["heartbeat_epoch_utc"] = epoch
m["clock_read"] = clock_read
m["round_no"] = 252
out = json.dumps(m, ensure_ascii=False, indent=1)
data = out.encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(M, "wb") as fh:
    fh.write(data)

# int-type self-check (R170/R178 law)
chk = json.loads(open(M, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("state round_no=252; heartbeat epoch:", chk["heartbeat_epoch_utc"],
      "int-type OK; clock:", clock_read)
