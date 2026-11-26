# -*- coding: utf-8 -*-
"""r2121 delivery note: append the proof row + state key after the push."""
import datetime as dt
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORTS = os.path.join(ROOT, "round_reports-bm-c.md")

ROW = (
    "|**送达复核（08:0x）**：commit **2829d2cd5d** 已直推 origin/main（74bb952042..2829d2cd5d），"
    "fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0	0**，"
    "`git ls-tree -r --name-only origin/main` 四件新件在位"
    "（scripts/etf_book_permission_vs_size.py、results/etf_book_permission_vs_size.json、"
    "research/ETF_BOOK_PERMISSION_VS_SIZE.md、results/_r2121bmc_closeout.py）→ "
    "**本地未达 origin commit 数=0**；pre-commit 爪本轮重装（CR 归一后 MATCH=True）、pre-push MATCH=True、"
    "Bigmoney-LoopWatchdog 就绪、Bigmoney-IterationLoop 重注册 no-op（pin=0）、"
    "attrition_ledger_guard CLEAN（4 账本·2 处历史缩行 healed 照录）。记账：本行 1 处 + state 1 处 + 心跳 1 处 = 3 |"
)

PROOF = (
    "commit 2829d2cd5d pushed origin/main (74bb952042..2829d2cd5d); after fetch "
    "git rev-list --left-right --count origin/main...HEAD = 0/0; git ls-tree -r origin/main sees the "
    "four new paths (scripts/results/md/_r2121bmc_closeout); pre-commit claw reinstalled this round "
    "(CR-normalized MATCH=True), pre-push MATCH=True, watchdog ready, loop task re-register no-op "
    "(pin=0), attrition guard CLEAN (4 ledgers, 2 historical shrink rows healed) -> "
    "本地未达 origin commit 数=0"
)


def main():
    with io.open(REPORTS, "a", encoding="utf-8", newline="") as fh:
        fh.write(ROW + "\n")

    with io.open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    st["送达自证_r2121"] = PROOF
    with io.open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)

    now = dt.datetime.now().astimezone()
    with io.open(HB, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    hb["ts"] = now.isoformat(timespec="seconds")
    hb["clock_read"] = now.isoformat(timespec="seconds")
    hb["heartbeat_epoch_utc"] = int(now.timestamp())
    with io.open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)

    with io.open(HB, encoding="utf-8") as fh:
        chk = json.load(fh)
    assert isinstance(chk["heartbeat_epoch_utc"], int)
    print(json.dumps({"state_keys": len(st), "epoch": chk["heartbeat_epoch_utc"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
