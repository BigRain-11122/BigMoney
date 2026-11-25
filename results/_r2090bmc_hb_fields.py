# r2090 bm-c heartbeat patch. GPU keys already written by Tools/gpu_face.py apply
# (r1909: one probe for all 33 aliases). This only touches the narrative/clock
# fields, and proves a byte-identical round-trip before writing (indent=1 + CRLF,
# no trailing newline -- the r2043 trap).
import json
import os
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

raw = open(HB, "rb").read()
d = json.loads(raw.decode("utf-8"))
# heartbeat_write (Tools/gpu_face.py -> Tools/heartbeat_write.py) is the canonical
# writer for this face and emits indent=1 + LF + trailing newline. Match it rather
# than the CRLF working-tree shape, or the diff becomes a whole-file rewrite.
assert (json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode(
    "utf-8") == raw, "heartbeat round-trip not byte-identical"

now = datetime.now().astimezone().replace(microsecond=0).isoformat()
d["round_no"] = 2090
d["last_seen"] = now
d["ts"] = now
d["clock_read"] = now
d["heartbeat_epoch_utc"] = int(time.time())
d["work"] = ("r2090 · 8 臂烧回同一世界（ONE_WORLD·任务自 DISABLE）+ 把「红名单」做成常设件："
             "smoke_red_recheck --check（selftest 23/23）+ 两条链腿 + 一次真全量冒烟 767 腿 749 PASS / 18 FAIL")
d["current_task"] = "r2090 臂族 ONE_WORLD 收口 + 红名单自动重问接线"
d["task"] = d["current_task"]
d["verdict"] = "lane healthy: arms on one world; 18 red legs (14 inline, 1 real)"

out = (json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
tmp = HB + ".tmp"
with open(tmp, "wb") as fh:
    fh.write(out)
os.replace(tmp, HB)

# post-write assertions
back = json.loads(open(HB, "rb").read().decode("utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
assert "T" in back["clock_read"], "clock_read must use T (F7)"
assert back["round_no"] == 2090
print("heartbeat ok epoch=%s round=%s" % (back["heartbeat_epoch_utc"], back["round_no"]))
