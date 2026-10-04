# -*- coding: utf-8 -*-
# r711 bm-b closeout: state round_no + heartbeat + round report line (r708 lineage, %s banned per r610)
import json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now_local = datetime.datetime.now().astimezone()
ts = now_local.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (bm-b legacy filename per fleet README S5)
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 711
st["note"] = ("r711: watch+integration round - S6 chain 34 legs rc0 (REPORT/LIVE-2026-10-05 regen 05:02, dualrun ZERO-DRIFT streak 8, "
              "compute_audit CLEAN, all collectors correct no-op @cutoff 09-30 golden week); D-06 re-verify PASS (20 pit-*.md all <=30KB, max 28,386B, 10-07 closeout target holds); "
              "merge bm-c r514 S6 same-family wave 17 UU canonical-resolved (13 ours-newer + 2 rolling-ledger union + token machines per-key max-union picked_theirs=2; "
              "resolver results/_r711bmb_merge_resolve.py); smoke 48/48; orders 154/154 double-scan zero unacked; D-19 decisions/orders dual hash MATCH 755428F8/E79E15F9; "
              "attrition CLEAN; quartet 4/4; trio NULLS V1152/Q924/D730 of 2000 @05:11 burning (ETA V 10-06T1x/Q 10-07T1x/D 10-08T0x); "
              "W15 judge-finalize bm-a seat in-flight PID 103532 ETA ~05:50 (watch only); RAM 4.01GB just crossed floor - engine queue self-ignite window.")
st["last_round_at"] = ts
st["ts"] = ts
st["updated"] = ts
st["last_seen"] = ts
st["round_no_label"] = "round 711 (bm-b)"
st["clock_read"] = ts
st["next"] = ("(a) trio V lane closeout 10-06T17 (then Q 10-07T1x, D 10-08T0x) -> FUND trio nulls finalize windows; "
              "(b) D-06 closeout report to group 10-07 12:00 (re-verify PASS this round, target holds); "
              "(c) W15 judge-finalize landing watch (bm-a seat, ETA ~05:50) -> s4 intake chain after; "
              "(d) 10-09 post-holiday data-chain check (first trading day after National Day).")
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
st2 = json.load(open(sp, encoding="utf-8-sig"))
assert st2["round_no"] == 711 and st2["clock_read"] == ts, "state roundtrip"

# --- heartbeat fleet/machines/bm-b.json
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["current_task"] = ("trio NULLS V/Q/D burning (daemon, ETA 10-06T1x/10-07T1x/10-08T0x); W15 judge-finalize bm-a seat in-flight; "
                       "r711 watch+integration round closed")
hb["verdict"] = ("GREEN: smoke 48/48, S6 34 legs rc0, orders 154/154 zero unacked, D-19 dual MATCH, attrition CLEAN, "
                 "RAM 4.01GB at floor edge (trio legal occupancy), pool 3 lanes ready-burning + queue self-ignite window")
json.dump(hb, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
hb2 = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb2["clock_read"] == hb2["last_seen"] == ts, "hb roundtrip"
print("STATE round=711 OK | HB epoch=%d int OK | clock=%s" % (epoch, ts))
