# r1026 bm-a commit2: sync/push_verified block readback update
import json, io, os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ts = datetime.now().astimezone().isoformat(timespec="seconds")
blk = {
    "ts": ts,
    "origin_tip": "6f902ac60",
    "ahead_behind": "0/0",
    "note": ("r1026: push range d0d0d04a4..6f902ac60 verified (range line + fetch + behind-0; local-not-at-origin=0, "
             "same-round readback; rebase 1-commit CLEAN onto bm-c r1060 pair zero conflicts)"),
}
for rel in ("state-bm-a.json", os.path.join("fleet", "machines", "bm-a.json")):
    fp = os.path.join(ROOT, rel)
    d = json.load(io.open(fp, encoding="utf-8"))
    d["sync"] = blk
    d["push_verified"] = blk
    tmp = fp + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, fp)
    print("WROTE %s" % rel)
