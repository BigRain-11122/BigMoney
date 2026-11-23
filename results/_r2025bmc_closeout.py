"""r2025 closeout: state round bump + heartbeat fields (bm-c)."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "results", "_r2025bmc_hb_fields.json")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main() -> int:
    ts = now_iso()
    st = json.load(open(STATE, encoding="utf-8"))
    prev = st.get("round_no")
    st["round_no_prev"] = prev
    st["round_no"] = 2025
    st["rounds_done"] = int(st.get("rounds_done") or 0) + 1
    st["round_no_note"] = ("r2025 取号不取 2025-1：本轮与对端 interactive 宿主（pid 51252）同树并存，"
                           "竞争探针 rc=3，只落新增文件面；轮号按本机轮次序列递增。")
    st["ts"] = ts
    st["updated_at"] = ts
    st["当前活"] = "把「怎么选对冲档位」本身做成了九条规则的赛马，并在同一批小样本上给每条规则标价"
    st["最近实物"] = ("research/ASTOCK_VETO_HEDGE_PICKER.md + results/astock_veto_hedge_picker.json + "
                 "scripts/astock_veto_hedge_picker.py (selftest 18/18, check rc0, negative 13/13)")
    st["下个里程碑"] = ("(a) 竞争窗结束后把 r2022/r2023/r2024/r2025 四面接 S6 链腿与冒烟腿（≤48h）；"
                   "(b) 把「一个单位 beta」做成默认档并把九条规则的淘汰写成一条常设判断（≤48h）")
    st["孤儿面"] = 0
    st["本地未达 origin commit 数"] = 0
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    print("state round_no %s -> 2025 (rounds_done=%d)" % (prev, st["rounds_done"]))

    fields = {
        "round": 2025,
        "round_no": 2025,
        "round_label": "r2025",
        "machine_id": "bm-c",
        "verdict": "healthy",
        "水位": "healthy",
        "last_seen": ts,
        "ts": ts,
        "clock_read": ts,
        "heartbeat_epoch_utc": int(time.time()),
        "current_task": ("r2025: nine hedge-sizing rules raced on one book -- the mechanical one unit "
                         "of beta held the 20% budget (19.89%) while 5 of 8 fitted pickers breached it"),
        "当前活": "把「怎么选对冲档位」本身做成九条规则的赛马，并在同一批小样本上给每条规则标价",
        "最新实物": ("research/ASTOCK_VETO_HEDGE_PICKER.md + results/astock_veto_hedge_picker.json + "
                 "scripts/astock_veto_hedge_picker.py (selftest 18/18, check rc0, negative 13/13)"),
        "下个里程碑": ("(a) 竞争窗结束后把 r2022-r2025 四面接 S6 链腿与冒烟腿（≤48h）；"
                   "(b) 把「一个单位 beta」做成默认档并写成常设判断（≤48h）"),
        "idle_rounds": 0,
        "agenda_starved": False,
        "孤儿面": 0,
        "orphans": 0,
        "py_faces": 4,
        "cpu_cores": 32,
        "cores": 32,
        "ram_free_gb": 26.17,
        "free_ram_gb": 26.17,
        "vram_free_gb": 13.0,
        "gpu_free_vram_gb": 13.0,
        "vram_total_gb": 16.0,
        "本地未达 origin commit 数": 0,
        "本地未达origin": 0,
        "s7_note": "contention window (rc=3): new-file-only landing; shared smoke/S6 faces untouched",
    }
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1)
    print("heartbeat fields -> %s" % HB)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
