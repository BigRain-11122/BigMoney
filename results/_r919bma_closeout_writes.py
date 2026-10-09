# r919 bm-a closeout state write (single-file fresh read-modify-write per multi-writer law)
import json, datetime, time, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
SP = os.path.join(REPO, "state-bm-a.json")

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

with open(SP, "rb") as f:
    s = json.loads(f.read().decode("utf-8-sig"))

did = ("r919: S0 dead-session estate takeover (r899 precedent: process census sole BigMoney loop + 2 unpushed commits "
       "+ zero closeout): dead r919 session had landed W199 prereg BUILD + five-face FREEZE locally "
       "(d372c9c1e) + churn absorb (b52663b8a); estate absorb commit 447f86fb1 (daemon churn + n1_w199 "
       "materialized 12 shards per p2cal tracked convention) + r832 writer-pause window (4 writer schtasks "
       "disabled, re-enabled after): zero-overlap rebase onto origin ccb2f0949 (11 incoming all bm-c "
       "autofill/absorb, zero file overlap) -> push b8a9a9112 self-verified 0/0 + S0.5 orders scan unacked=0 "
       "(scanner .md-suffix bug fixed: full-name compare 55/55) + DEC bd94a27b/ORD b38eaaf8 python-raw "
       "UNCHANGED zero action + S1 smoke 49/49 + watermark red=false + engine ALIVE idle (W199 self-burn "
       "ignition pending next engine tick, task re-enabled) + S6 38-leg evening chain driver launched "
       "background PID 70404 (r916 bloodline rolled one gen, options-skip per O-20261009-1105)")

s.update({
    "round_no": 919, "round": 919, "loop_round": 919,
    "last_round": 918, "last_round_at": "2026-10-09T15:15:06+08:00",
    "last_round_closed": "2026-10-09T15:15:06+08:00",
    "last_round_ts": "2026-10-09T15:15:06+08:00",
    "did": did,
    "last_action": "r919 closeout: dead-session estate absorbed + W199 freeze delivered to origin; S6 evening chain in flight",
    "last_artifact": ("r919 products: research/PERPETUAL_N1_W199_PREREG.md 21,511B (W199 five-face freeze: bands "
                      "A 452_604..454_603 staircase FIFTY-NINTH hops=1 + B 454_604..454_803 W141 reserved-walk) + "
                      "results/p2cal_ext/n1_w199/ 12 shards + results/_r919bma_s6_driver.py (38-leg evening chain) + "
                      "results/_r919bma_s05scan.py; all pushed b8a9a9112"),
    "now_active": "r919 closing: estate takeover landed (W199 freeze on origin) + S6 evening chain running (new-bar 10-09)",
    "current": "r919 closing: estate takeover landed (W199 freeze on origin) + S6 evening chain running (new-bar 10-09)",
    "current_task": ("r920: S6 evening chain receipt verify (bad_legs) + W199 engine ignition verify + "
                     "PARKING-P1 burn due 10-14 12:00 (O-20261009-1105); W200 seat chain window opens (seat law <=24h)"),
    "task": ("r920: S6 evening chain receipt verify (bad_legs) + W199 engine ignition verify + "
             "PARKING-P1 burn due 10-14 12:00 (O-20261009-1105); W200 seat chain window opens (seat law <=24h)"),
    "next": ("r920: S6 evening chain receipt verify (bad_legs) + W199 engine ignition verify + "
             "PARKING-P1 burn due 10-14 12:00 (O-20261009-1105); W200 seat chain window opens (seat law <=24h)"),
    "next_milestone": ("r920: S6 evening chain receipt verify + W199 engine ignition verify; PARKING-P1 burn due 10-14 "
                       "12:00 (O-20261009-1105)"),
    "verify": ("green (r919: estate takeover zero-loss rebase push 0/0; smoke 49/49; watermark green; engine ALIVE; "
               "S6 38-leg evening chain in flight)"),
    "verdict": ("green (r919: estate takeover zero-loss rebase push 0/0; smoke 49/49; watermark green; engine ALIVE; "
                "S6 38-leg evening chain in flight)"),
    "ts": now_iso, "updated": now_iso, "last_seen": now_iso, "last_run": now_iso, "clock_read": now_iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
    "idle_rounds": 0, "agenda_starved": False, "orphan_faces": 0,
    "last_decisions_at": now_iso,
    "last_decisions_seen": "r919 S0.5 scan: DEC bd94a27b UNCHANGED vs r918 consumption -- zero delta; zero action",
    "last_decisions_ts": now_iso,
    "last_orders_at": now_iso,
    "last_orders_seen": "r919 S0.5 scan: ORD b38eaaf8 UNCHANGED vs r918 consumption -- zero delta; unacked=0; zero action",
    "last_orders_ts": now_iso,
})
s["push_verified"] = {"ts": now_iso, "origin_tip": "b8a9a9112", "ahead_behind": "0/0",
                      "note": "r919 estate takeover rebase push self-verified post-push fetch+rev-list; closeout commit follows"}
s["sync"] = s["push_verified"]

with open(SP, "w", encoding="utf-8", newline="") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

chk = json.loads(open(SP, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("state written: round_no=", chk["round_no"], "epoch=", chk["heartbeat_epoch_utc"], "type int OK")
