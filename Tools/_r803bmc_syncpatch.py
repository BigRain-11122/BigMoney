# -*- coding: utf-8 -*-
"""r803 bm-c closeout sync patch: heartbeat head_sha + delivery-verified
sync note (post-push face). Pattern credit: r802 closeout sync patch canon."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now_iso = datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00")

hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
hb["head_sha"] = "7cbc89dc8"
hb["last_pulled_at"] = now_iso
hb["sync"] = {
    "ahead": 0,
    "behind": 0,
    "last_push_ts": now_iso,
    "note": ("r803 post-push delivery self-verified ahead=0/behind=0 via fetch+rev-list "
             "(push 7cbc89dc8 clean, pre-push claw passed, no escape needed); round chain: "
             "S0 absorb c88ba9d1e -> pull --rebase clean zero-UU -> S6 40/40 (24th green) -> "
             "closeout -> round commit 7cbc89dc8 -> push -> sync patch"),
}
hb_path.write_text(json.dumps(hb, ensure_ascii=False, indent=1), encoding="utf-8")
hb2 = json.loads(hb_path.read_text(encoding="utf-8"))
assert hb2["head_sha"] == "7cbc89dc8" and hb2["sync"]["ahead"] == 0
print("sync patch OK: head_sha=7cbc89dc8 ts=%s" % now_iso)
