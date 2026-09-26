"""r245 bm-b hermetic E2E verification for scripts/grid_paper.py (T-78 s5c).

Proves the FULL run() write path without touching the real lane:
  synthetic 5-code panel (one bar past the frozen evidence_cutoff) ->
  5 account state JSONs written -> idempotent no-op rerun -> fund-event
  freeze leg (idio jump on a live cell = terminal freeze, marks truncated,
  honest disclosure; other accounts unaffected). Real batch label file is
read (read-only, single truth source); data paths + paper dir + live.paper
universe face are monkeypatched to synthetic fixtures. Zero repo writes.
"""
import json
import os
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import numpy as np
import pandas as pd

import grid_paper as gp

ok_all = True


def ok(name, cond):
    global ok_all
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    ok_all &= bool(cond)


idx = pd.bdate_range("2025-06-02", periods=340)   # ~340 bars > band_win+2
# calendar tail must include 2026-09-23 (evidence day), 09-24 (cutoff), 09-25
tail = pd.bdate_range("2026-09-21", periods=5)
index = pd.DatetimeIndex(sorted(set(idx).union(set(tail))))
N = len(index)
rng = np.random.default_rng(245)

with tempfile.TemporaryDirectory() as td:
    data_dir = os.path.join(td, "daily")
    paper_dir = os.path.join(td, "grid_paper")
    os.makedirs(data_dir)
    frames = {}
    for code in gp.LIVE:
        base = 100.0 + np.cumsum(rng.normal(0, 0.4, N))
        close = pd.Series(base, index=index)
        openp = close.shift(1).fillna(100.0) * (
            1 + rng.normal(0, 0.001, N))
        if code == "510300":                     # fund-event freeze leg
            close.iloc[-1] = close.iloc[-2] * 0.85   # -15% idio jump 09-25
            openp.iloc[-1] = close.iloc[-2]
        df = pd.DataFrame({"date": index.strftime("%Y-%m-%d"),
                           "open": openp.values,
                           "close": close.values})
        df.to_csv(os.path.join(data_dir, f"{code}.csv"), index=False)
        frames[code] = df

    # stub the universe face (live.paper import inside run())
    import types
    uni = pd.Series(0.005, index=index)         # calm universe median |r1|
    stub_lp = types.ModuleType("live.paper")
    stub_lp.load_core = lambda: object()
    stub_lp.build_panels = lambda _x: {"close": pd.DataFrame(
        {c: frames[c]["close"].values for c in gp.LIVE}, index=index)}
    sys.modules["live.paper"] = stub_lp
    # (uni_med derives from the stub close panel: median |r1| ~ calm)

    gp.PATHS = SimpleNamespace(daily_dir=data_dir)
    gp.PAPER_DIR = paper_dir

    rc1 = gp.run()
    ok("run(): marks 5/5 written, exit 0", rc1 == 0
       and all(os.path.exists(gp._state_path(c)) for c in gp.LIVE))

    sts = {}
    for c in gp.LIVE:
        with open(gp._state_path(c), encoding="utf-8") as fh:
            sts[c] = json.load(fh)
    s_ok = all(
        st["schema"] == "grid_paper_v1"
        and st["account"] == f"GRID-{c}"
        and st["experimental"] is True
        and st["evidence_cutoff"] == "2026-09-24"
        and st["panel_cutoff"] == "2026-09-25"
        and st["batch_honest_labels"]["g1_prime_v2"]["pass"] is False
        and st["batch_honest_labels"]["promotion_candidate"] is False
        and st["risk_budget"]["position_cap"] == 1.0
        and st["audit"]["ledger_trials_added"] == 0
        and st["machinery"]["params"]["n_grids"] == 10
        for c, st in sts.items())
    ok("states: schema+labels+budget+audit faces intact (5/5)", s_ok)

    ok("marks: 4/5 accounts carry the 09-25 mark (paper-start boundary)",
       all(len(sts[c]["marks"]) == 1
           and sts[c]["marks"][0]["date"] == "2026-09-25"
           for c in gp.LIVE if c != "510300"))

    fz = sts["510300"]["forward_fund_event"]
    ok("freeze: 510300 fund event -> terminal frozen, marks truncated, "
       "equity back to initial",
       fz["frozen"] is True and fz["event_days"] == ["2026-09-25"]
       and sts["510300"]["marks"] == []
       and sts["510300"]["equity_cny"] == gp.INITIAL_CNY
       and sts["510300"]["marks_summary"]["bars"] == 0)

    mtimes = {c: os.path.getmtime(gp._state_path(c)) for c in gp.LIVE}
    rc2 = gp.run()
    ok("idempotency: rerun no-op exit 0, state bytes untouched",
       rc2 == 0 and all(
           os.path.getmtime(gp._state_path(c)) == mtimes[c]
           for c in gp.LIVE))

print("E2E " + ("ALL PASS" if ok_all else "FAILED"))
sys.exit(0 if ok_all else 2)
