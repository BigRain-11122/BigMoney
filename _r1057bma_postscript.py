# -*- coding: utf-8 -*-
"""r1057 bm-a postscript: push_verified/sync faces + postscript report line."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

STATE = "state-bm-a.json"
HEART = "fleet/machines/bm-a.json"
REPORT = "round_reports-bm-a.md"

now_dt = datetime.now(timezone(timedelta(hours=8)))
now = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
TIP = "6b956f2498"

SYNC = {
    "ts": now,
    "origin_tip": TIP,
    "ahead_behind": "0/0",
    "note": ("r1057 push race-resolved: origin advanced mid-window (bm-c r1091 W268 five-face splice 8bc7ac759e + "
             "2 satengine ledger appends) -> rebase clean zero-UU -> delivered 6b956f2498; fetch+ls-tree 11/11 "
             "origin-eligible artifacts verified (12th = results/_r1057bma_s6chain_rc.log blanket-*.log gitignored "
             "local evidence per r1054 face); local-unpushed=0; W269 stays GATED on W268 finalize (bm-c next)"),
}

POSTSCRIPT = (now + " | r1057 postscript | 送达自证：push 首拒（origin 窗内前移=bm-c r1091 W268 五面 splice 8bc7ac759e"
              "+2 satengine ledger append）→rebase 干净零 UU→6b956f2498 送达 origin·fetch+ls-tree 11/11 可达件全在位"
              "（第 12 件 rc.log=gitignored 本地证据面 r1054 先例）·本地未达 origin commit 数=0·"
              "W268 splice 落地=席链推进 W269 门槛收窄至 finalize（bm-c 下窗）守门维持 | ls-tree 11/11 | "
              "下轮指针不变（r1058：W269 观察+MF 周一裁决+委员会表+E19 消费面）")


def main():
    for path in (STATE, HEART):
        with io.open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        obj["sync"] = SYNC
        obj["push_verified"] = SYNC
        obj["heartbeat_epoch_utc"] = epoch if path == HEART else obj.get("heartbeat_epoch_utc", epoch)
        obj["heartbeat_epoch_utc_type_int"] = True
        obj["last_seen"] = now
        obj["ts"] = now
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
    with io.open(REPORT, "r", encoding="utf-8") as f:
        text = f.read()
    if not text.endswith("\n"):
        text += "\n"
    text += POSTSCRIPT + "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    hb = json.load(io.open(HEART, encoding="utf-8"))
    assert isinstance(hb["heartbeat_epoch_utc"], int)
    print("POSTSCRIPT-OK tip=%s epoch=%d" % (TIP, epoch))


if __name__ == "__main__":
    main()
