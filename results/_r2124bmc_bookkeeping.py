"""r2124 bm-c bookkeeping: state round_no, round keys, heartbeat fields.

Kept as a file (not an inline -c) so the numbers written are auditable later.
"""
import io
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

ROUND = 2124
CUR = ("r2124: publish the year-line reachability face a killed window left on disk, "
       "and put the zt panel's 日期 column back on the collector's ISO caliber "
       "(r2123's amendment had rewritten all 1,897 rows flat, which made the CEO risk "
       "tape print one day as two)")

NEW = {
    "本轮_r2124": (
        "r2124 PRODUCT (watermark red=false/lane=healthy, contention rc0 CLEAN single "
        "host, orphan faces 0): (1) finished and shipped the year-line reachability face "
        "an interrupted window left uncommitted -- 12 frozen cells (4 widths x 3 rebals), "
        "only N3_R10_10bp clears all four year measures (top-2 67.97% vs line 70.00%, "
        "CAGR 11.15%) but its one-day capacity 0.14e8 sits under the 0.20e8 floor; the "
        "5-name book has the capacity and misses by 0.54pp; R10<R20<R40 in every width "
        "=> the line is reachable in TIME, not in width. selftest 12/12, check CHECK OK, "
        "chain legs year_line_reach_write + year_line_reach 2/2 rc0. (2) r2123's "
        "LATE_COMPLETION_SUPERSET amendment was right about the rows and wrong about the "
        "stamp: it rewrote the whole zt panel's 日期 column from 2026-11-23 to 20261123 "
        "while the collector (update_zt_pool L162/169/292), the other three panels and the "
        "day ledger all stay ISO -- so the CEO risk tape printed '四面板截止日不一致 "
        "zt=20261123' for a day when all four agreed, and append-dedupe stopped matching. "
        "Repaired with a guard that refuses unless row count, per-day counts and the "
        "amended day's 146 rows all survive (first version refused itself on a key-space "
        "bug; fixed to compare in ISO keys). Collector then advanced for real: all four "
        "panels now 2026-11-25 (zt 51 / zbgc 30 / dtgc 43 / strong 80). Readers "
        "regenerated: ceo_live_usage aligned True + selftest ALL PASS, daily_report §九 "
        "'四面同为 2026-11-25'. That closes 3 of the 11 reds the killed window read."),
    "竞争_r2124": (
        "rc=0 CLEAN (results/_repo_write_contention.bm-c.json: fewer than two codely hosts "
        "alive; this host pid=21372 from 09:40:04). Scheduler faces (saturation engine, "
        "watermark, arbiter, cpu_fill) kept writing their own small state files; no second "
        "coding host."),
    "通过_r2124": (
        "orders 118 files (117 orders + README) / heartbeat orders_ack 331 -> the only "
        "unacked are the pre-2026-10-26 lane broadcasts (r2066 precedent, not re-acked "
        "one by one); fleet group origin/main:docs/decisions.md raw bytes 250,586B sha256 "
        "79e3083b85c130b8... == own watermark -> zero new decisions, zero action; "
        "fleet/inbox empty; orphan_face_probe py_faces=4 orphans=0 resident_servers=1; "
        "attrition_ledger_guard CLEAN (4 ledgers, 3 historical shrink rows healed); "
        "Bigmoney-IterationLoop and Bigmoney-LoopWatchdog both present (loop running at "
        "the time of the query); saturation engine status rc0 alive (last_verdict=idle); "
        "idle_trigger green_idle=true but this round produced faces -> --worked cleared "
        "idle_rounds."),
    "smoke_r2124": (
        "full suite not closed in-window: detached pythonw -m smoke_test -> "
        "logs/smoke_r2124b.log (pid 21236, started 09:5x), still running at round end, so "
        "no total is claimed. The interrupted window's run read 770/781 PASS 11 FAIL "
        "(logs/smoke_r2124.log); this round closed 3 of those 11 (CEO one-pager risk-tape "
        "date/cash leg, 'the CEO page carries today's market risk tape', and the daily "
        "report §九 parity face they read). 8 carried reds untouched and named in the QA."),
    "记账_r2124": "轮报告 1 处 + QA 1 件 + state 1 处 + 心跳 1 处 = 4",
}


def main():
    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = ROUND
    st.update(NEW)
    with io.open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

    with io.open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    now = datetime.now().astimezone()
    iso = now.isoformat(timespec="seconds")
    hb.update({
        "last_seen": iso,
        "ts": iso,
        "clock_read": iso,
        "heartbeat_epoch_utc": int(time.time()),
        "current_task": CUR,
        "round_no": ROUND,
        "verdict": "healthy",
        "idle_rounds": 0,
        "agenda_starved": False,
    })
    with io.open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)

    with io.open(HB, encoding="utf-8") as f:
        chk = json.load(f)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"], "clock_read must be ISO with T"
    print("state round_no=%d keys=%d" % (st["round_no"], len(st)))
    print("heartbeat %s epoch=%s(%s) verdict=%s"
          % (chk["clock_read"], chk["heartbeat_epoch_utc"],
             type(chk["heartbeat_epoch_utc"]).__name__, chk["verdict"]))


if __name__ == "__main__":
    main()
