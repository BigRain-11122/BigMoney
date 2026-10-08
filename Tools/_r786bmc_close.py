# -*- coding: utf-8 -*-
"""r786 bm-c S7-close refresh: round-report delivery tail line + heartbeat/
state sync face post-push refresh (O-20261009-0024 sec1-4, bm-b r807 naming
alignment) + head_sha roll to delivered tip. Runs AFTER push verified
ahead=0/behind=0. ASCII source; epoch python int (R170/R178)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())


def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip()


_, HEAD = git("rev-parse", "HEAD")
_, AHEAD = git("rev-list", "--count", "origin/main..HEAD")
_, BEHIND = git("rev-list", "--count", "HEAD..origin/main")
assert AHEAD == "0" and BEHIND == "0", "sync not closed: %s/%s" % (AHEAD, BEHIND)

TAIL = (u"{ts} | r786 S7-close | push 送达自证：main commit 7836eecc8 + "
        u"merge 5cfed3336（12-UU 收口=CODELY append-only union〔r784 多候选坑"
        u"行+r807 bm-b 账本分叉律行双保·零丢失〕+10 派生面 take-new-by-ts"
        u"〔全 ours 01:00:1x > theirs 00:59:5x·r505 墙钟新侧律〕+x2_watch_log "
        u"ts-union〔r758 律·receipt results/_r786bmc_resolve.json〕）双波已在 "
        u"origin·fetch 后 ahead=0/behind=0（O-20261009-0024 sec1-1 同步闭环"
        u"达成）·head={head}").format(ts=TS, head=HEAD[:9])

with open(REPORT, "a", encoding="utf-8") as fh:
    fh.write(u"\n" + TAIL + u"\n")

SYNC = {"ahead": int(AHEAD), "behind": int(BEHIND), "last_push_ts": TS,
        "note": u"O-20261009-0024 sec1-4 sync face; post-push refresh "
                u"in-round (delivery self-verified ahead=0/behind=0 "
                u"via fetch+rev-list)"}
for path in (os.path.join(ROOT, "fleet", "machines", "bm-c.json"),
             os.path.join(ROOT, "state-bm-c.json")):
    with open(path, encoding="utf-8") as fh:
        obj = json.load(fh)
    obj["sync"] = SYNC
    obj["head_sha"] = HEAD
    obj["heartbeat_epoch_utc"] = EPOCH
    obj["last_pulled_at"] = TS
    obj["updated"] = TS
    obj["updated_at"] = TS
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    assert isinstance(obj["heartbeat_epoch_utc"], int)

print("close refresh ok: tail appended; sync ahead=%s behind=%s head=%s"
      % (AHEAD, BEHIND, HEAD[:9]))
