# -*- coding: utf-8 -*-
# r985 bm-a closeout: heartbeat + state + round report line update
import io, json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
R = "985"

hb_path = "fleet/machines/bm-a.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))

ack = hb.get("orders_ack", [])
if "O-20261014-0925-bm-b.md" not in ack:
    ack.append("O-20261014-0925-bm-b.md")

cur = ("r985: W238 own-wave full-cycle closeout LANDED (six-gate PRE-FINALIZE 13th consecutive ALL PASS -> "
       "finalize one-pass 945,735+2,200=947,935 EXACT -> five-key ALL PASS -> sec78 backfill; "
       "W239 waits-upstream DISARMED; MSG-1255 sent; ORD delta consumed zero BigMoney directives)")
did = ("r985: S0 0-behind + orphan probe 0/34 + D19 dual-delta (ORD 83454e8f consumed: 10-14 rows all "
       "MV/BigStream/software-copyright/CEO-PROXY lanes zero BigMoney directives; DEC unchanged) + "
       "O-0925 ack ledger repair (receipt was r979 in-order file, orders_ack row added) + S1 smoke 49/49 + "
       "six-gate receipt _w238bma_sixgate_prereg.json (splice integrity sha16 clean-equal x2 + banned ADMIT + "
       "pf 9/9 + n1 selftest + 12/12 shards + seed_admit FREE-verbatim/BLOCKED-fresh positive) + finalize "
       "one-pass + fivekey receipt + sec78 machine backfill + idle --worked")

hb.update({
 "last_seen": now_iso, "ts": now_iso, "updated": now_iso, "updated_at": now_iso,
 "clock_read": now_iso, "last_run": now_iso, "last_round_closed": now_iso, "last_round_ts": now_iso,
 "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
 "heartbeat_epoch_utc_type_int": True,
 "round": 985, "round_no": 985, "last_round": 985, "loop_round": 985,
 "current": cur, "now_active": cur, "current_task": cur,
 "did": did, "last_action": "r985 W238 finalize closeout",
 "task": cur,
 "last_artifact": "results/perpetual_faces/n1_w238_results.json (finalize product, 12:5x)",
 "latest_artifact": "results/perpetual_faces/n1_w238_results.json (finalize product, 12:5x)",
 "recent_artifact": "results/perpetual_faces/n1_w238_results.json (finalize product, 12:5x)",
 "verdict": ("green (red=false lane=healthy; satengine ALIVE queue0 idle post-W238-finalize; "
             "W238 finalize LANDED ledger 947,935/K 521,520 five-key ALL PASS; "
             "W239 seat=bm-c waits-upstream disarmed; supply chain: W239 freeze next + W240 seat pending)"),
 "next": ("r986: supply chain -- W240 seat probe (post-W238 universe, seed-decoupled double-hop face) + "
          "bars 15:30 full S6 chain + any CEO-PROXY fleet orders"),
 "next_milestone": ("W238 chain complete (LANDED this round); W239 bm-c freeze expected <=48h; "
                    "month-boundary first exam 10-31; C-20261014-01 10-16 revisit"),
 "idle_rounds": 0, "agenda_starved": False,
 "orders_ack": ack,
 "last_orders_seen": ("r985: ORD 83454e8f consumed (delta db08b85b->83454e8f tail = 10-14 12:1x-12:3x rows: "
                      "CEO-PROXY席 O-20261014-1210 + 科学巡视 O-20261014-1235 + bm-a 35B coder O-20261014-1230 "
                      "deploy-closed + @bm-c probe order + bm-b B站 lane + @bm-c software rows -- zero BigMoney "
                      "directives; watermark advanced 83454e8f); DEC d77f5fa1 UNCHANGED"),
 "last_orders_sha": "83454e8f01ddf8019bd30d2bb57bd4a742b55bc6",
 "last_orders_at": now_iso, "last_orders_read_at": now_iso,
 "last_decisions_seen": "r985: DEC d77f5fa1 UNCHANGED (raw-blob sha256 == watermark pin, zero re-consume)",
 "last_decisions_read_at": now_iso,
 "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
})
io.open(hb_path, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (smoke F7)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO (smoke F7)"
print("HEARTBEAT-OK r985 epoch", chk["heartbeat_epoch_utc"])

# ---- state-bm-a.json ----
st_path = "state-bm-a.json"
st = json.load(io.open(st_path, encoding="utf-8"))
st.update({
 "round": 985, "round_no": 985, "last_round": 985,
 "loop_round": 985,
 "last_round_at": now_iso, "updated": now_iso, "updated_at": now_iso, "ts": now_iso,
 "clock_read": now_iso, "last_run": now_iso, "last_round_closed": now_iso, "last_round_ts": now_iso,
 "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
 "heartbeat_epoch_utc_type_int": True,
 "current": cur, "now_active": cur, "current_task": cur, "did": did,
 "last_action": "r985 W238 finalize closeout",
 "last_artifact": "results/perpetual_faces/n1_w238_results.json (finalize product, 12:5x)",
 "latest_artifact": "results/perpetual_faces/n1_w238_results.json (finalize product, 12:5x)",
 "recent_artifact": "results/perpetual_faces/n1_w238_results.json (finalize product, 12:5x)",
 "task": cur,
 "verdict": ("green (red=false lane=healthy; engine ALIVE idle queue0 post-W238-finalize; W238 finalize LANDED "
             "947,935/K 521,520 five-key ALL PASS this round; W239 waits-upstream disarmed; "
             "S6 r984 chain products absorbed this commit)"),
 "verify": ("green (six-gate receipt ALL PASS + finalize identity 945,735+2,200=947,935 EXACT + "
            "five-key ALL PASS + sec78 placeholders=0 + smoke 49/49 + D19 advance read-back OK "
            "+ idle --worked 0)"),
 "next": ("r986: W240 seat probe (post-W238 universe) + bars 15:30 S6 full chain + CEO-PROXY fleet orders scan"),
 "next_milestone": ("W238 chain complete (LANDED this round); W239 bm-c freeze <=48h; month exam 10-31; "
                    "C-20261014-01 revisit 10-16"),
 "idle_rounds": 0, "agenda_starved": False,
 "orphan_face": 0, "orphan_faces": 0,
 "last_orders_seen": hb["last_orders_seen"],
 "last_orders_sha": "83454e8f01ddf8019bd30d2bb57bd4a742b55bc6",
 "last_orders_at": now_iso, "last_orders_read_at": now_iso,
 "last_decisions_seen": hb["last_decisions_seen"],
 "last_decisions_read_at": now_iso,
})
dg = st.get("d19_watermark_guard")
if isinstance(dg, dict):
    dg["round_ref"] = 985
    dg["ts"] = now_iso
io.open(st_path, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))
chk2 = json.load(io.open(st_path, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
print("STATE-OK r985")
