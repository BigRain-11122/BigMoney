# -*- coding: utf-8 -*-
"""r2022 closeout (bm-c): bump the machine's own state face, nothing else.

Under the round's contention window (repo_write_contention rc=3, a peer session in
the same tree) this touches only bm-c's own bookkeeping faces, never a shared code
or data face.  `round_no` goes to 2022, not 2021: the peer session in this tree is
mid-round on 2021 (results/_r2021bmc_* written at 03:10) and its number is not mine
to take.  The gap is recorded in `round_no_note` so a later round can see why the
sequence has a hole rather than infer a lost round.
"""
from __future__ import annotations

import io
import json
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")


def now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def main() -> int:
    with io.open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    prev = int(state.get("round_no") or 0)
    state["round_no_prev"] = prev
    state["round_no"] = 2022
    state["rounds_done"] = int(state.get("rounds_done") or 0) + 1
    state["activity"] = "product"
    state["activity_now_round"] = 2022
    state["activity_now"] = (
        "r2022: the veto book's 27.34% vol is 84.9% shortable CSI1000 beta (R^2 matches "
        "r2003's index fit almost exactly through the IM future), but hedging it only pays "
        "in sample -- 2024+ Sharpe 0.619 hedged vs 0.621 unhedged (HEDGE_PAYS_IN_SAMPLE_ONLY)")
    state["verdict"] = "HEDGE_PAYS_IN_SAMPLE_ONLY"
    state["round_no_note"] = (
        "2021 is the peer session's in-flight round in the same tree (results/_r2021bmc_*, "
        "written 2026-11-24T03:10); this round takes 2022 and leaves 2021 to it")
    state["last_round_ts"] = now()
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    print("state round_no %d -> %d (rounds_done %d)"
          % (prev, state["round_no"], state["rounds_done"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
