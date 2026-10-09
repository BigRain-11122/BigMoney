# r943 bm-a closeout: round report line + state-bm-a.json + heartbeat (fresh read-modify-write per 10-06 law)
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
R = "943"

REPORT_LINE = (
    NOW + " | r" + R + " | bm-a | dept:工程 (S0 rebase storm canon-resolve + THERMO pool stale-ready heal P0 + S6 39 legs) | "
    "S0: origin+7 (bm-b r817/closeout + bm-c autofill keepalive) vs local+4 (r942 estate) -- 13 UU faces "
    "classifier 13/0 UNKNOWN: 7 ALL_FACES via merge_lane_views resolve (compute_audit 203-row union / regime_state "
    "3-ledger union / update_status+lhb+futures max-cutoff / token_usage replay-side) + 6 docs twins via "
    "_r943bma_resolve.py (fundamental_b_layer_filter snapshot ts-probe 05:21:52 replay-side; REPORT/LIVE twins "
    "same-side byte-copy twin-coupling r329) + 3 SatEngine live-wins daemon faces checkout --ours (newer absorbed "
    "side, churn-commit replay conflict) + rebase-continue daemon-race add -A same-window r813 law + 6-face "
    "reconcile ZERO-DRIFT + push f0d133a18 landed | "
    "P0 WM red=true 05:42:03 (pool-batch-runnable-idle-low-cpu, THERMO-OVERLAY-P1-BURN stale-ready: r942 closeout "
    "flipped lane mirror ONLY, shared runnable_pool.json flip missed = inverse-r688 case) -> two-layer done-flip "
    "surgery _r943bma_flip.py (claim-file evidence closed-ok 05:02:41 pid5476; entry+shard->done; result_ref+done_at "
    "backdated to actual completion) -> re-probe 05:48:03 red=false lane healthy pool_ready=[] -- root cause fixed "
    "in-round, closed loop verified | "
    "S1 smoke 49/49; S6 39 legs rc0 (no new bar Saturday, panel tail 2026-10-09); attrition guard CLEAN (4 files, "
    "historical shrinks healed); post_review zero live fail-verdicts (5 marks all inside honest-negative prose); "
    "quartet DEC b87a92b1 / ORD 0ddb01d9 python-raw MATCH both scans zero re-consume; inbox zero unread; "
    "schtask quartet loop-pin8 no-op + watchdog re-registered 05:54 + both claws installed | "
    "lane survey: W17 screen = bm-c lane-pinned (machine-local CKPT_DIR finalize face; shards 0-4 owner=bm-c "
    "keepalive 05:37, 5/6/7 open-but-lane-pinned = NOT cross-machine claimable) -- zero claim this round correct; "
    "W204 seat=bm-c locked (MSG-20261010-0022-bmc), derive prereq W203 first-burn DONE (n1_w203_results.json "
    "finalize in place) -- owner bm-c to arm; PARKING-P1 burn watch due 10-14 12:00 watchdog in-cadence | "
    "next: r944 watch window (PARKING-P1 / W17 funnel / W204 arm by bm-c) + HANDOVER next 5x = r945"
)

# 1) round report append (fresh read, verify last line is r942)
with open("round_reports-bm-a.md", "rb") as f:
    rep = f.read().decode("utf-8")
lines = rep.rstrip("\n").split("\n")
assert "r942" in lines[-1], "report tail is not r942: " + lines[-1][:80]
rep_out = rep.rstrip("\n") + "\n" + REPORT_LINE + "\n"
with open("round_reports-bm-a.md", "wb") as f:
    f.write(rep_out.encode("utf-8"))
print("[closeout] report line r943 appended, tail ok")

# 2) state file update (fresh read)
with open("state-bm-a.json", "rb") as f:
    st = json.loads(f.read().decode("utf-8"))
st["round_no"] = 943
st["round"] = 943
st["loop_round"] = 943
st["round_no_label"] = "r943"
st["last_round"] = 942
st["ts"] = NOW
st["clock_read"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_run"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_round_closed"] = NOW
st["last_heartbeat_epoch_utc"] = EPOCH
st["heartbeat_epoch_utc"] = EPOCH
did = ("r943: S0 rebase storm canon-resolved (13 UU classifier + 7 merge_lane_views + twin-coupling 6 + 3 daemon "
       "live-wins + reconcile ZERO-DRIFT, push f0d133a18) + P0 THERMO-OVERLAY-P1-BURN stale-ready heal (two-layer "
       "done-flip, WM red->healthy 05:48 re-probe, inverse-r688 root cause) + S6 39 legs rc0 + smoke 49/49 + "
       "attrition CLEAN + quartet GREEN")
st["did"] = did
st["last_action"] = "r943 closeout: rebase storm resolved + pool stale-ready healed + S6 green"
art = ("results/_r943bma_flip.py (two-layer pool done-flip) + results/watermark_red.json red=false 05:48:03 "
       "(probe-verified heal) + results/_r943bma_s6_chain.json (39 legs rc0) + results/_r943bma_resolve.py "
       "(rebase storm resolver)")
st["last_artifact"] = art
st["latest_artifact"] = art
nxt = ("r944: watch window (PARKING-P1 burn due 10-14 12:00 watchdog in-cadence; W17 screen funnel bm-c lane; "
       "W204 arm by bm-c seat owner) + idle agenda scan; HANDOVER next 5x = r945")
st["next"] = nxt
st["now_active"] = nxt
st["current"] = nxt
st["task"] = nxt
st["current_task"] = nxt
st["next_milestone"] = "PARKING-P1 burn due 10-14 12:00; W204 arm pending bm-c; HANDOVER r945"
verd = ("green (r943: THERMO pool stale-ready healed two-layer flip WM red->healthy re-probe; rebase storm "
        "13-face canon-resolved zero-loss push f0d133a18; smoke 49/49; S6 39/39 rc0; attrition CLEAN; quartet GREEN)")
st["verdict"] = verd
st["verify"] = verd
st["last_orders_seen"] = "r943 double-scan zero new rows (ORD 0ddb01d9 unchanged, ack diff ZERO both scans)"
st["last_orders_at"] = "2026-10-10"
st["last_orders_ts"] = NOW
st["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH both scans r943; zero new BigMoney dispatch"
st["last_decisions_at"] = "2026-10-10"
st["last_decisions_ts"] = NOW
st["push_verified"] = {"ts": NOW, "origin_tip": "f0d133a18", "ahead_behind": "0/0",
                       "note": "r943 S0 rebase-storm push delivered (r942 estate via 13-face canon resolve); "
                               "post-push fetch+rev-list verified"}
st["sync"] = dict(st["push_verified"])
with open("state-bm-a.json", "wb") as f:
    f.write((json.dumps(st, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
# verify epoch int type (R170/R178 law)
st2 = json.loads(open("state-bm-a.json", "rb").read().decode("utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int) and isinstance(st2["last_heartbeat_epoch_utc"], int)
print("[closeout] state-bm-a.json updated, epoch int verified", EPOCH)

# 3) heartbeat (fresh read)
with open("fleet/machines/bm-a.json", "rb") as f:
    hb = json.loads(f.read().decode("utf-8"))
hb["round_no"] = 943
hb["round"] = 943
hb["loop_round"] = 943
hb["last_round"] = 942
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["last_seen"] = NOW
hb["last_run"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = True
hb["did"] = did
hb["last_action"] = "r943 closeout: rebase storm resolved + pool stale-ready healed + S6 green"
hb["last_artifact"] = art
hb["latest_artifact"] = art
hb["next"] = nxt
hb["now_active"] = nxt
hb["current"] = nxt
hb["current_task"] = nxt
hb["task"] = nxt
hb["next_milestone"] = "PARKING-P1 burn due 10-14 12:00; W204 arm pending bm-c; HANDOVER r945"
hb["verdict"] = verd
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_orders_seen"] = "r943 double-scan zero new rows (ORD 0ddb01d9 unchanged)"
hb["last_orders_at"] = "2026-10-10"
hb["last_orders_sha"] = "0ddb01d9aca7588382fb4341651f6d7548503070d4a12cf98c2774346d48276e"
hb["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH both scans r943"
hb["last_decisions_at"] = "2026-10-10"
hb["last_decisions_sha"] = "b87a92b1b445fd1dab4daa9250c9d52eb85e0ac122c7b870ce5f83e822c67374"
with open("fleet/machines/bm-a.json", "wb") as f:
    f.write((json.dumps(hb, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
hb2 = json.loads(open("fleet/machines/bm-a.json", "rb").read().decode("utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
print("[closeout] heartbeat updated, epoch int verified")
print("CLOSEOUT WRITES DONE")
