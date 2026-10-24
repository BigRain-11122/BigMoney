# -*- coding: utf-8 -*-
"""r1198 bm-c closeout bookkeeping: state counter/note, round report row, heartbeat.

All values are machine-read or measured in this window; no wall-clock guessing.
"""
import io
import json
import time
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ).isoformat(timespec="seconds")
epoch = int(time.time())

STATE = "state-bm-c.json"
st = json.load(io.open(STATE, encoding="utf-8"))
assert st.get("round_no") == 1197, "state counter drift: %r" % st.get("round_no")
st["round_no"] = 1198
st["round"] = 1198
st["last_round_report"] = "round_reports-bm-c.md tails (r1198 W310 seat+freeze+splice)"
st["round_no_label"] = "r1197 W309 closeout -> this window r1198 (W310 seat+freeze+splice) -> next r1199"
st["ts"] = now
st["last_decisions_check"] = now
st["recent_artifact"] = "results/p2cal_ext/n1_w310/"
st["verify"] = ("smoke 57/57 | W310 seat ADMIT (A 697_301..699_300 / B 699_301..699_500) | "
                "prereg freeze 442e881af8 | five-face splice d490186e9d (168 parity rows, pf 9/9 + n1 PASS) | "
                "attrition CLEAN | claws MATCH")
st["r1198_closeout_note"] = (
    "r1198: W310 opened end-to-end in ONE window (seat -> prereg freeze -> five-face splice -> engine "
    "ignition), the clean one-window shape that W309 did NOT have (r1196 opened, r1197 closed). "
    "PRODUCT: (1) W310 seat ADMIT via Tools/n1_seat_probe.py on the post-W309 299-owner universe "
    "(live walk, zero transcription): A-ext 697_301..699_300 (1 hop: arithmetic continuation "
    "697_101..699_100 refused at start by the registered W309 B band 697_101..697_300) / B-ext "
    "699_301..699_500 (1 hop own-A reservation cascade: naive 697_301..697_500 lands inside this "
    "wave's own A window), seed_admit_gate FREE on both bands, universe 299 owner rows (bm-a 130 / "
    "bm-b 41 / bm-c 128, ordinal 300); ordinals passed in explicitly per r1170 (63rd A-hop / 64th "
    "above-own-A). Seat MSG published BEFORE the freeze (r565) = "
    "fleet/inbox/MSG-20261024-1500-bmc-w310-seat.md, push 68a4a18b1f. (2) prereg derive "
    "results/_w310bmc_prereg_derive.py: canon-clone of the frozen W309 face b109a52460 (25,848B / 63 "
    "lines / sha16 fbba5b7d8166c35c) -> research/PERPETUAL_N1_W310_PREREG.md (25,913B / 63 lines / "
    "sha16 98a587b54a1fc058), 37 count-asserted keys (count table printed before any replacement, "
    "r1171) + 4 parked cumulative chains extended by one entry (se_mu narrowing / A-B 1-hop wave "
    "list / own-turn rotation / RAM freeze). Freeze commit 442e881af8; banned_direction_gate rc0 zero "
    "matches. (3) five-face splice via results/_w310bmc_gen_patch.py -> "
    "results/_w310bmc_freeze_edits.py: 168 parity rows (69 estate + 37 kept + 61 dropped-from-own + "
    "62 fresh), pf selftest 9/9 PASS, n1 selftest PASS (no traceback), registry row 310 registered "
    "with a=(697301,699300)/b_exit=(699301,699500), engine self-ignited on row landing (r535 mtime "
    "law; results/p2cal_ext/n1_w310/ shards appearing, 6/12 by report time). Splice commit "
    "d490186e9d. S0: HEAD==origin at open; S0.5 D-19 decisions digest UNCHANGED (dec 3cfdec0c0a664129 "
    "/ ord kept) => zero rows owed; unacked orders 0 (109 files / 234 acks) + 7 of our OWN stale seat "
    "MSGs archived to fleet/inbox/processed/. S1 smoke 57/57. round-zero orphan probe py_faces=5 "
    "orphans=0. S6 39-leg chain launched headless (pid 47880 -> results/_r1198bmc_s6_chain.out); by "
    "report time legs 1-5 green (dualrun/compute_audit/py_watermark/update_daily/market_regime) and "
    "the tail lands next window. S7 attrition 4 ledger files CLEAN (3 historical shrinks healed) / "
    "both claws MATCH / scheduled tasks NOT re-registered per the 2026-10-17 CEO cleanup order. "
    "PIT: (a) the wave-open lineage carries THREE hardcoded wave literals that the generic W-label "
    "bump cannot reach -- the pf row key in 'f\\'{ROW_I}309: {{\"a\":' and the batch-key literals "
    "'309: {\"batch\"' / '309: {{\"batch\"'. Missing the pf row key writes the NEW band at the PREVIOUS "
    "wave's registry key and silently drops the previous row (caught by the n1 selftest mirror assert "
    "WAVE_CONFIGS[309] vs N1_BANDS[309], then healed by git checkout + regenerating the editor with "
    "the extra key); always diff the generated editor against its parent and check every bare 3-digit "
    "wave literal, not just W-prefixed ones. (b) r1195->r1196->r1198 round-label remapping needs "
    "sentinels: a plain pairwise map rewrites the prior-wave window inside strings the post-fix step "
    "then owns; park them as pure-letter sentinels, then fix the finalize-window sentences explicitly "
    "(-- the W309 finalize window is r1197 and its estate chain is r1196/r1196/r1197)."
)

io.open(STATE, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1) + "\n")

ROW = ("| %s | r1198 | W310 opened end-to-end in one window: seat ADMIT (A 697_301..699_300 / B "
       "699_301..699_500; A 63rd consecutive A-hop, B 64th above-own-A; live-derived off the "
       "post-W309 299-owner universe; ordinals passed in explicitly per r1170) + prereg freeze "
       "(canon-clone of b109a52460, 37 count-asserted keys + 4 parked chains extended; "
       "banned_direction_gate rc0) + five-face splice (168 parity rows; pf 9/9 + n1 PASS; registry "
       "row 310 landed; engine self-ignited, 6/12 shards by report time). S0.5 D-19 digest unchanged "
       "=> zero rows owed; unacked orders 0 (109/234) and 7 own stale seat MSGs archived to "
       "processed; S1 smoke 57/57; orphan face=0; S6 39-leg chain launched headless (pid 47880, "
       "first 5 legs rc0, tail next window); S7 attrition CLEAN (3 historical shrinks healed) / both "
       "claws MATCH / scheduled tasks NOT re-registered per the 2026-10-17 CEO cleanup order. | "
       "next = r1199 W310 six-gate + finalize + fivekeys + sec7/8 | watermark verdict: GREEN (no red "
       "gate, next_pick claimed) | local-not-on-origin commits=0 (post-push self-proof) | registry "
       "zero-hit (no sweep action)\n")
with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(ROW)

hb_path = "fleet/machines/bm-c.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb["round"] = 1198
hb["round_no"] = 1198
hb["last_seen"] = now
hb["ts"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = "W310 seat+freeze+splice landed; engine self-burning 12 shards; S6 chain tail in flight"
hb["verdict"] = "GREEN"
hb["recent_artifact"] = "results/_w310bmc_freeze_receipt.json"
io.open(hb_path, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
print("state/heartbeat/report updated", now, epoch)
assert isinstance(json.load(io.open(hb_path, encoding="utf-8"))["heartbeat_epoch_utc"], int)