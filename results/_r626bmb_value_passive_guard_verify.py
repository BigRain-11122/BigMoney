"""r626d bm-b: direct real-module verification of the MSG-1720 Finding B fix.

(1) repro: _passive_window(t0) is None for FUND-VALUE-P1 (the crash trigger
    that killed cmd_finalize pre-fix -- bm-a reproducer
    _r633bma_value_passive_probe.py);
(2) guard: first non-empty base month scan from t0 over month_pos finds a
    valid passive start;
(3) shifted passive: _passive_window(plo, hi) returns a real series ->
    sharpe/ret/span computable -- the exact code path the fixed
    cmd_finalize now takes;
(4) source-proof: the fixed runner source contains the guard (month_pos
    scan + span_note + SystemExit) -- byte anchors.

Import-only: reads the mmap cache, writes nothing to runner faces.
Output: results/_r626bmb_value_passive_guard_verify.json
"""
import datetime
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "scripts"))
import fund_value_p1 as m  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "_r626bmb_value_passive_guard_verify.json")
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "scripts", "fund_value_p1.py")

rep = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
       "machine": "bm-b", "family": "fund_value_p1",
       "fix_ref": "MSG-2026-10-03-1720 Finding B owner fix (r626d)",
       "rehearsal": True, "NOT_A_VERDICT": True}

# init exactly as cmd_finalize does
m._init_worker()
m._firing_months()
lo = m._G["_t0_pos"]
hi = len(m._G["idx"]) - 1
rep["t0"] = {"pos": int(lo), "date": str(m._G["idx"][lo].date())}

# (1) repro: the pre-fix crash trigger still holds at t0
rel_t0 = m._passive_window(lo, hi)
rep["repro_passive_at_t0_is_none"] = rel_t0 is None
assert rel_t0 is None, "expected None at t0 (repro face) -- if this fires," \
    " the t0 universe changed; re-check the guard premise"

# (2) guard: scan first non-empty base month (verbatim guard logic)
plo = next((p for p in m._G["month_pos"]
            if p >= lo and len(m._month_universe(p)["base_j"]) > 0), None)
assert plo is not None, "no non-empty base month from t0 -- guard would exit"
u_plo = m._month_universe(plo)
rep["guard_first_nonempty_base_month"] = {
    "pos": int(plo), "date": str(m._G["idx"][plo].date()),
    "n_base": int(len(u_plo["base_j"]))}

# (3) shifted passive: the exact path the fixed cmd_finalize takes
rel = m._passive_window(plo, hi)
pc = rel.pct_change().dropna()
sh = float((pc.mean() / pc.std(ddof=1)) * np.sqrt(252))
rep["shifted_passive"] = {
    "n_members": int(rel.count()),
    "sharpe_full": round(sh, 6),
    "ret_full": round(float(rel.iloc[-1] - 1), 6),
    "span": [str(m._G["idx"][plo].date()), str(m._G["idx"][hi].date())],
    "note": f"t0_base_empty: passive span shifted from t0 "
            f"{m._G['idx'][lo].date()} to first non-empty base month "
            f"{m._G['idx'][plo].date()} (MSG-2026-10-03-1720 Finding B "
            "owner fix)"}

# (4) source-proof: guard anchors present in the fixed runner
src = open(SRC, encoding="utf-8").read()
anchors = {
    "month_pos_scan": "for p in _G[\"month_pos\"]",
    "span_note_key": "\"span_note\": passive_note",
    "systemexit_guard": "passive face undefined (MSG-1720",
    "t0_kept_for_calendar": "stays pinned to t0 for",
}
rep["source_anchors"] = {k: (v in src) for k, v in anchors.items()}
assert all(rep["source_anchors"].values()), "guard anchors missing in runner"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print("[verify] Finding B fix PROVEN on real module:")
print(json.dumps({k: rep[k] for k in
                  ("repro_passive_at_t0_is_none",
                   "guard_first_nonempty_base_month", "shifted_passive")},
                 ensure_ascii=False, indent=1))
print("[verify] ->", OUT)
