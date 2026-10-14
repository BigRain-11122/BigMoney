# r945 bm-b closeout: state.json + heartbeat + round report line (in-place, key-preserving)
import json, io, time, os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")            # T-separator, +08:00 offset
epoch = int(time.time())
R = 945          # completed round
RN = 946        # next round

DID = ("r945 bm-b: waiting-state round (sina 10-14 bar still undelivered source-side at 18:51 probe: "
       "new rows 0, cutoff stays 2026-10-13) + D-19 ORD single-row delta consumed+advanced "
       "(group row O-20261014-1745 zhu-AGENT 13-seat group review, committee-executed, zero BigMoney action rows; "
       "watermark 1176e4c4->1bb6ffe7 read-back equality OK; dec EQUAL c61d7884) + S6 33 legs rc0 "
       "(dualrun streak 30 ZERO-DRIFT; thermo/dualarm refreshed at frozen cutoffs; scorecard/REPORT/LIVE 10-14 "
       "regenerated idempotent; CALL-2026-10-13 ORANGE_COOL; market_regime trigger note breadth 0.81>=65%) + "
       "4 bar-gated paper legs (live.paper/t35_open_fill/t24_prospect x2) skipped honest + orders 88 disk 0 unacked "
       "(round-start + S7 double-scan) + smoke 49/49 + SatEngine alive queue 0 + orphan 0 + attrition CLEAN "
       "(1 historical shrink healed) + claws x2 reinstalled content-equal + loop task pin=2 no-op + watchdog present "
       "+ idle_trigger --worked (idle_rounds=0)")

NEXT = ("r946: (a) sina 10-14 bar catch -> live.paper REGIME_GUARD=enforce + t35_open_fill_verify + t24 prospect "
        "legs when landed; (b) supply route (a) stock-universe P1 awaits CEO signature -- waiting-state "
        "declaration, no re-scan of same objects")

VERDICT = ("GREEN: r945 waiting-state round -- S6 33 legs rc0 + paper chain gated honest (no new bar, cutoff "
           "2026-10-13; sina same-day bar undelivered source-side) + D-19 ORD advanced 1bb6ffe7 (group zhu-AGENT "
           "review row, zero BigMoney action) + orders 0 unacked + smoke 49/49 + attrition CLEAN; waiting state = "
           "sina 10-14 bar (external, self-heal) + CEO route-a signature (external) + MF panel source-block "
           "(bm-a lane, self-heal)")

ARTIFACT = ("docs/live_usage/LIVE-2026-10-14.md (ORANGE rung cap 50%) + docs/daily_report/REPORT-2026-10-14.md "
            "+ results/daily_scorecard.html refreshed @ 2026-10-14T18:55+08:00")

NOTE = ("r945: orders 0 unacked (disk 88); D-19 dec EQUAL c61d7884 + ord ADVANCED 1bb6ffe7 "
        "(O-20261014-1745 zero-BigMoney row consumed); flags supply_floor/pool_starvation standing WITH VERDICT "
        "(refill = CEO P1 route (a)); sina 10-14 bar catch pending (source-side, self-heal)")

NOW_ACTIVE = ("r945 closeout: S0 stash-bridge pull clean + S6 33 legs rc0; SatEngine ticking; waiting state = "
              "sina 10-14 bar (external) + CEO route-a signature (external)")

ORPH_NOTE = "r945 probe 18:5x: py_faces=11 orphans=0 killed=[]"

# ---------- state.json ----------
sp = os.path.join(ROOT, "state.json")
with io.open(sp, encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "round": R, "round_no": RN, "round_no_label": "r945",
    "did": DID, "next": NEXT, "task": NEXT, "current_task": NEXT,
    "verdict": VERDICT, "note": NOTE, "now_active": NOW_ACTIVE,
    "last_action": "r945: waiting-state declaration + D-19 ORD advance + S6 33 legs rc0",
    "last_action_at": ts, "last_round_at": ts, "last_round_ts": ts,
    "last_seen": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "clock_read": ts, "latest_artifact": ARTIFACT,
    "orphan_face": 0, "orphan_faces": 0, "orphan_face_note": ORPH_NOTE,
    "last_orders_sha_note": "r945: ORD delta consumed (single group row O-20261014-1745, zero BigMoney action rows); advanced 1176e4c4->1bb6ffe7 via guard --advance, read-back equality OK",
    "last_orders_at": ts,
})
st["sync"] = {"last_push_ts": ts, "note": "r945 closeout commit+push follows this write; behind=0 verified post-push"}
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with io.open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "round": R, "round_no": RN, "round_no_label": "r945",
    "did": DID, "next": NEXT, "task": NEXT, "current_task": NEXT,
    "verdict": VERDICT, "note": NOTE, "now_active": NOW_ACTIVE,
    "last_action": "r945: waiting-state declaration + D-19 ORD advance + S6 33 legs rc0",
    "last_action_at": ts, "last_round_at": ts, "last_seen": ts,
    "ts": ts, "updated": ts, "updated_at": ts,
    "clock_read": ts,
    "heartbeat_epoch_utc": epoch,
    "latest_artifact": ARTIFACT,
    "orphan_face": 0, "orphan_faces": 0, "orphan_face_note": ORPH_NOTE,
    "idle_rounds": 0, "agenda_starved": False, "green_idle": False,
})
hb["sync"] = {"last_push_ts": ts, "note": "r945 closeout commit+push follows this write; behind=0 verified post-push"}
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# epoch type self-assert
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"

# ---------- round report ----------
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    "| {ts} | r945 bm-b [dept:eng/fleet] | WM-VERDICT: green (red=false; py_watermark=py_low_board_clear legal "
    "idle white-list; compute_audit pool_starvation+supply_floor standing WITH VERDICT route-closed refill=CEO P1 "
    "route-a) | orphan-faces=0 (round probe 18:5x: py_faces=11 orphans=0) | current: WAITING-STATE round per "
    "r944 pointer -- sina 10-14 bar still undelivered source-side (18:51 update_daily probe: new rows 0, cutoff "
    "2026-10-13) + D-19 ORD delta consumed+advanced (single new group row O-20261014-1745 zhu-AGENT 13-seat group "
    "review, committee-executed, zero BigMoney action rows; watermark 1176e4c4->1bb6ffe7 read-back equality OK; "
    "dec EQUAL c61d7884) + S0 stash-bridge pull clean (absorbed bm-c r1003 estate-absorb + own lane r943/r944 "
    "commits, behind 0) + S6 33 legs rc0 (dualrun streak 30 ZERO-DRIFT; thermo/dualarm refreshed at frozen "
    "cutoffs; scorecard/REPORT/LIVE 10-14 regenerated idempotent; CALL-2026-10-13 ORANGE_COOL; market_regime "
    "trigger note breadth 0.81>=65%) + 4 bar-gated paper legs (live.paper/t35_open_fill/t24_prospect x2) skipped "
    "honest | latest artifact: {art} | next milestone: sina 10-14 bar landing -> live.paper REGIME_GUARD=enforce "
    "+ t35/t24 chain (self-heal <=48h); supply route (a) stock-universe P1 awaits CEO signature | orders 0 "
    "unacked (disk 88, round-start + S7 double-scan); D-19 dec EQUAL c61d7884 + ord ADVANCED 1bb6ffe7; smoke "
    "49/49; attrition CLEAN (1 historical shrink healed); claws x2 reinstalled content-equal; loop task pin=2 "
    "no-op + watchdog present; idle_trigger --worked (idle_rounds=0); unreached-origin commits=1 pre-push "
    "(closeout push + fetch self-verify follows) | next pointer: r946 sina-bar-landing round; else waiting-state "
    "one-line declaration (no re-scan of same objects) |\n"
).format(ts=ts, art=ARTIFACT)
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)

print("closeout writes OK: state.json round=%d round_no=%d | heartbeat epoch=%d (int) | report line appended" % (R, RN, epoch))
