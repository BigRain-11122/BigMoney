# -*- coding: utf-8 -*-
"""R307 bm-a: state flip 306->307 + heartbeat update (epoch int, clock ISO with offset)."""
import json, io, datetime, time

now = datetime.datetime.now().astimezone()
ts = now.isoformat()
epoch = int(time.time())

# --- state-bm-a.json flip ---
P = r"state-bm-a.json"
d = json.load(open(P, encoding="utf-8"))
assert d["round_no"] == 306, d["round_no"]
d["round_no"] = 307
d["did"] = ("R307: T-73 ticket CLOSED (all s1/s2/s3+s4 faces landed: 16-school survey + slices A-E + five CN models "
            "ALL NEGATIVE -- matrix 19 cells + GRID-SLEEVE via T-78 0 survivors; zero CN-* paper accounts honest; "
            "s4 month-boundary zero-intake cross-check pointer -> 10-01 monthly face) + board/bandit exhaustion "
            "verified honest (supply line = next external wave, cadences met) + S6 30/30 rc=0")
d["verdict"] = "py_low_board_clear LEGAL-idle (0 open tickets incl T-73 closed, bandit 0 open candidates date-gated, pool ready=0, no local batch; supply cadences met: daily digest R289 + wave-10 09-26)"
d["next"] = ("R308: 09-28 Monday new-bar full-chain relay (daily -> live.paper REGIME_GUARD v3 -> t35v -> t24x2 -> "
             "aggr -> export -> scorecard) + next external harvest wave per O-1721 when due; watch moneyflow rank-pass "
             "self-heal (EM conn-level blocked 53/5222 since 09-25) + ah_panel refresh (EM mapping blocked); "
             "sina_mf depth 101d -> 150d IC-gate ~2026-11 pointer; 10-01 month-boundary trio + T-73 s4 zero-intake cross-check")
d["ts"] = ts
d["last_round_ts"] = ts
d["updated_at"] = ts
d["current_task"] = "R308 next: Monday new-bar relay + supply watch"
with io.open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
d2 = json.load(open(P, encoding="utf-8"))
assert d2["round_no"] == 307

# --- heartbeat fleet/machines/bm-a.json (own file only) ---
H = r"fleet\machines\bm-a.json"
h = json.load(open(H, encoding="utf-8"))
h["last_seen"] = ts
h["clock_read"] = ts
h["heartbeat_epoch_utc"] = epoch
assert isinstance(h["heartbeat_epoch_utc"], int)
h["current_task"] = "R307 done: T-73 closed (five CN models all-negative verdict consolidation ticket); board clear"
h["verdict"] = "py_low_board_clear legal idle"
h["round_no"] = 307
h["task"] = "R308: Monday new-bar relay + O-1721 supply watch"
with io.open(H, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
h2 = json.load(open(H, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "F7: epoch must be JSON int"
assert "T" in h2["clock_read"] and ("+08:00" in h2["clock_read"]), "F7: clock ISO must carry T + UTC offset"
print("state 307 + heartbeat ok; epoch=", epoch, "clock=", ts)
