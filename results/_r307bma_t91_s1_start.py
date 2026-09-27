# -*- coding: utf-8 -*-
"""R307 bm-a: T-91 s1 STARTED face -- design decisions + precise continuation points
+ heartbeat orders_ack for O-2026-09-26-2340 (S7 double-scan catch receipt)."""
import json, io, datetime

ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# --- T-91 progress note (s1 started this round; build continues R308) ---
P = r"fleet\tasks\T-2026-09-27-91-P1.json"
d = json.load(open(P, encoding="utf-8"))
assert d["status"] == "claimed" and "bm-a" in d["claimed_by"]
d["progress_r307bma_s1_start"] = (
    "r307 s1 STARTED (claim-and-start same round; faces read + design decisions + data verified): "
    "(1) MACHINERY REUSE DECISION: live/paper.py registered-trader lane is G2-registration-bound "
    "(SIGNAL_BUILDERS must reproduce registered evidence) -- SYSTEM-V1 starts paper regardless of judged "
    "state (out-of-sample by construction) so it does NOT fit that lane; lawful O-2045 reuse face = "
    "machinery COMPONENTS (daily-panel marks accrual + T+1 open conservative proxy O-1132 + fill guard + "
    "cost x1) via an independent lane script scripts/system_v1_paper.py following AGGR/GRID observation-"
    "account precedent -- UNLIKE AGGR, s4 wires this into daily_scorecard + town GM-office rows (CEO face "
    "per spec). Independent lane results/system_v1_paper/ with sleeve-attribution columns. "
    "(2) L1 STATE SOURCE frozen: results/market_clock/call_latest.json (current ORANGE per CALL-2026-09-24; "
    "clock eight-grid keys the L2 routing table). "
    "(3) DATA FACE VERIFIED: astock daily panel complete=true n=5228 cutoff 2026-09-24 (data/astock_daily/per/"
    "<code>.csv qfq, bm-b lane overnight delivery) -> REV-OSC stock face starts DIRECTLY Monday (ETF-proxy "
    "interim face of prereg L3 NOT needed; upgrade path O-2330 sec.3 satisfied by delivery). "
    "(4) REV-OSC sleeve: reuse the frozen judged-batch runner logic (results/rev_osc/ overnight, no re-judge) "
    "as signal component import (no re-implementation); three-piece defaults per O-2335. "
    "R308 EXACT CONTINUATION: (a) read results/rev_osc runner + REFINE_BENCH-20260926-P1 + O-2335 three-piece "
    "param source; (b) build scripts/system_v1_paper.py skeleton: frozen L2 route table (ORANGE row: REV-OSC "
    "ON / trend suppressed-half / lowvol experimental-half / cash-leg full / cap 50%) + L4 ladder (single-name "
    "<=15%, weekly sleeve rebalance) + L5 exits (tp+8/re-stop-10 same-day-stop-priority/hold 7-10d) + hermetic "
    "selftest (zero-run); (c) Monday-09:15 auto-fire wiring decision (S6 conditional leg vs dedicated scheduled "
    "entry) with single-instance lock; (d) s2 REV-OSC standalone account inside same lane script; (e) s4 report "
    "wiring after harness green. Deadline face: functional before 2026-09-28 09:15 open."
)
with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# --- heartbeat orders_ack: append O-2026-09-26-2340-bm-a (new overnight order) ---
H = r"fleet\machines\bm-a.json"
h = json.load(open(H, encoding="utf-8"))
ack = h.get("orders_ack", "")
tok = "O-2026-09-26-2340-bm-a"
if tok not in ack.split():
    ack = (ack + " " + tok).strip()
h["orders_ack"] = ack
h["current_task"] = "R307 done + T-91 claimed/started (s1 design landed; harness build R308; Monday 09:15 start)"
h["task"] = "R308: T-91 s1 harness build (system_v1_paper.py skeleton + selftest + Monday auto-fire wiring)"
with io.open(H, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
h2 = json.load(open(H, encoding="utf-8"))
assert tok in h2["orders_ack"].split()
assert isinstance(h2["heartbeat_epoch_utc"], int)
print("T-91 s1-start note + heartbeat ack ok; acks now include", tok)
