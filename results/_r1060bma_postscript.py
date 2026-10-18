# -*- coding: utf-8 -*-
# r1060 bm-a postscript: push_verified/sync state faces + report postscript line
import json
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now_iso = datetime.now(CST).isoformat(timespec="seconds")

pv = {
    "ts": now_iso,
    "origin_tip": "6be15f319e",
    "ahead_behind": "0/0",
    "note": ("r1060 push delivered first-try (no race this window, origin static since S0 pull); "
             "fetch+ls-tree 6/6 origin-eligible artifacts verified "
             "(state-bm-a.json / round_reports-bm-a.md / fleet/machines/bm-a.json / _r1060bma_s6chain.ps1 / "
             "results/_r1060bma_closeout.py / research/HANDOVER.md); local-unpushed=0; "
             "W270 seat publish stays with bm-c r1094 (not yet on origin at this window's close)")
}

sp = "state-bm-a.json"
with open(sp, "r", encoding="utf-8") as f:
    st = json.load(f)
st["push_verified"] = pv
st["sync"] = dict(pv)
st["updated"] = now_iso
st["updated_at"] = now_iso
st["ts"] = now_iso
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

hp = "fleet/machines/bm-a.json"
with open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["push_verified"] = dict(pv)
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["ts"] = now_iso
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

rp = "round_reports-bm-a.md"
line = (now_iso + " | r1060 postscript | 送达自证：6be15f319e 送达 origin（首推即中·本窗零竞速=origin 自 S0 pull 后静止）"
        "·fetch+ls-tree 6/6 关键件在位（state/round_reports/heartbeat/s6chain/closeout/HANDOVER）"
        "·ahead/behind 0/0·本地未达 origin commit 数=0 | ls-tree 6/6 | "
        "下轮指针不变（r1061：W270 席位守望+MF 周一裁决 <=10-19+委员会 §六 裁决表 <=10-20 12:00+E20 GM/委员会保留面+S4U carried）\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

with open(rp, "r", encoding="utf-8") as f:
    tail = f.read()[-400:]
assert "r1060 postscript" in tail, "postscript append failed"
print("POSTSCRIPT_OK", now_iso)
