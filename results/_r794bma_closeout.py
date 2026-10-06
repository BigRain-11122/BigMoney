# -*- coding: utf-8 -*-
"""r794 bm-a takeover closeout: state + round report update."""
import io
import json
import time
from datetime import datetime, timezone, timedelta

tz = timedelta(hours=8)
now = datetime.now(timezone(tz)).isoformat(timespec="seconds")

# --- state-bm-a.json (fresh read-modify-write, machine-own file) ---
p = "state-bm-a.json"
d = json.loads(io.open(p, encoding="utf-8").read())
d["round_no"] = 794
d["last_round"] = 794
d["last_round_at"] = now
d["last_round_ts"] = now
d["last_action"] = ("r794 (takeover of timeout-killed 21:08 session, scratch-archaeology per r639 law): "
                    "W165 deriv v2 generator repaired (single root cause = P1 trailing-comma "
                    "lookahead (?![\\d,]) killed tuple first-elements/list-comma forms -> mixed-era "
                    "tuples + 764,012 residue; fixed to (?!(?:\\d|,\\d)) keeping long-form protection) "
                    "+ false-positive residue checks made context-precise (bare 764,012 = legit BACK "
                    "vmap entry + stale-list face, pinned) + 2 missing P4 rules added ([-1]==164/len==162 "
                    "composite, N1_BANDS 162 rows). ALL FOUR W165 tools derived + AST PASS + "
                    "independent audit PASS (results/_r794bma_w165_audit.py: era-consistent tuples "
                    "W163/W164/W165/W166p, anchors green). Freeze chain NOT started this round "
                    "(25min budget: half-done canonical freeze = r639 hazard; deliberate stop).")
d["current_task"] = ("W165 freeze node fire next round: run results/_r794bma_w165_face_probe.py -> "
                     "_r794bma_w165_freeze_edits.py -> _r794bma_w165_prereg_build.py -> "
                     "_r794bma_w165_freeze_verify.py -> seat MSG -> 12-shard burn (engine queue) -> "
                     "finalize --wave 165; plus deferred S6 chain")
d["next"] = ("W165 freeze chain execution (tools ready+audited): face_probe -> freeze_edits -> "
             "prereg_build -> freeze_verify -> seat registration MSG-2026-10-06-205x -> burn 12 "
             "shards -> finalize --wave 165. Do NOT re-derive (v2 generator + 4 tools committed).")
d["heartbeat_epoch_utc"] = int(time.time())
d["last_heartbeat_epoch_utc"] = d.get("heartbeat_epoch_utc", 0)
d["clock_read"] = now
d["ts"] = now
d["updated"] = now
d["last_seen"] = now
d["verify"] = ("deriv v2: ALL FOUR TOOLS DERIVED + AST PASS; independent audit PASS "
               "(_r794bma_w165_audit.py, era deltas 1999/199/2000/200 all legit forms); "
               "smoke 48/48; engine alive idle; decisions/orders watermarks already consumed "
               "by dead r794 session (pre-kill, in-file)")
d["latest_artifact"] = ("results/_r794bma_w165_{face_probe,prereg_build,freeze_edits,freeze_verify}.py "
                        "(derived+audited) @2026-10-06T21:5x")
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
chk = json.loads(io.open(p, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("state-bm-a.json updated, epoch int OK:", chk["heartbeat_epoch_utc"])

# --- round report line (append) ---
rp = "fleet/round_reports-bm-a.md"
line = (f"{now} | r794 | bm-a takeover of timeout-killed r794 session (21:08->21:33): scratch "
        f"archaeology per r639 law; W165 deriv v2 root-caused+fixed (P1 trailing-comma lookahead "
        f"(?![\\d,]) -> (?!(?:\\d|,\\d)); residue checks made context-precise; +2 P4 rules); ALL FOUR "
        f"W165 tools derived + AST PASS + independent audit PASS (_r794bma_w165_audit.py); freeze "
        f"chain deliberately NOT started (budget; half-done canonical freeze = r639 hazard) | "
        f"evidence: deriver stdout 'ALL FOUR TOOLS DERIVED + AST PASS', audit 'AUDIT PASS', "
        f"smoke 48/48 pre-work | next: fire W165 freeze chain (face_probe->freeze_edits->"
        f"prereg_build->freeze_verify->seat->burn->finalize) + deferred S6 | 本地未达 origin commit 数=0 "
        f"(push attempted at closeout)\n")
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report appended")
