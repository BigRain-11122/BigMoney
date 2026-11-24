# -*- coding: utf-8 -*-
"""r2066 closeout: heartbeat + round_no only.  Nothing else is touched."""
from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
STATE = os.path.join(ROOT, "state-bm-c.json")

TASK = ("r2066 一纸两读：permission 面印出的许可底（min 路径）与判词实际用的门槛"
        "（any 路径）差 63.4 倍——票面加仓空间 5,000 元 vs 317,083 元")
VERDICT = ("CONTENTION（rc=3）只落新增文件面：headroom 两读面 selftest 19/19 + check OK + "
           "负控 7/7（其中一条负控抓出本面检查器自己的措辞会骗链重建）")


def _ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / 2**30, 1)
    except Exception:
        return None


def _behind():
    try:
        out = subprocess.run(["git", "rev-list", "--left-right", "--count",
                              "origin/main...HEAD"], cwd=ROOT, capture_output=True,
                             text=True, timeout=60).stdout.split()
        return int(out[1]) if len(out) == 2 else None
    except Exception:
        return None


def main():
    now = _dt.datetime.now().astimezone().replace(microsecond=0)
    ts = now.isoformat()

    with open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    before_keys = len(hb)
    hb.update({
        "last_seen": ts,
        "ts": ts,
        "clock_read": ts,
        "heartbeat_epoch_utc": int(now.timestamp()),
        "current_task": TASK,
        "verdict": VERDICT,
        "idle_rounds": 0,
        "agenda_starved": False,
    })
    ram = _ram_gb()
    if ram is not None:
        hb["ram_free_gb"] = ram
    b = _behind()
    if b is not None:
        hb["local_behind_commits"] = b
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
    assert "T" in hb["clock_read"], "clock_read must be T-separated (R262)"
    with open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    old = st.get("round_no")
    st["round_no"] = int(old) + 1 if old is not None else 1
    st_keys = len(st)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # re-read both to prove what landed
    with open(HB, encoding="utf-8") as f:
        hb2 = json.load(f)
    with open(STATE, encoding="utf-8") as f:
        st2 = json.load(f)
    print(json.dumps({
        "hb_keys_before": before_keys, "hb_keys_after": len(hb2),
        "epoch_is_int": isinstance(hb2.get("heartbeat_epoch_utc"), int),
        "clock_read": hb2.get("clock_read"),
        "ram_free_gb": hb2.get("ram_free_gb"),
        "local_behind_commits": hb2.get("local_behind_commits"),
        "round_no": st2.get("round_no"), "state_keys": st_keys,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
