# -*- coding: utf-8 -*-
# _r930bmb_closeout.py -- r930 bm-b closeout writes: state.json (884->930 reconcile),
# heartbeat fleet/machines/bm-b.json (order ack O-20261014-0925 + r930 faces),
# round report line append. EOL-aware dump recipe (r289/r483-4, crlf no-tail host).
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
NOW = datetime.datetime.now()
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M:%S")


def load_rewrite(path, mutate):
    with open(path, "rb") as f:
        raw = f.read().decode("utf-8")
    obj = json.loads(raw)
    mutate(obj)
    probe = json.dumps(obj, ensure_ascii=False, indent=1).replace("\n", "\r\n")
    if json.loads(probe) != obj:
        raise SystemExit("self-encode parse gate failed: %s" % path)
    with open(path, "wb") as f:
        f.write(probe.encode("utf-8"))
    # post-write re-read
    with open(path, "rb") as f:
        json.loads(f.read().decode("utf-8"))
    print("written: %s" % path)


def mut_state(s):
    s["round_no"] = 930
    s["did"] = (
        "r930: W19 SCREEN supply enrollment MAIN PRODUCT: 8x TRIAL-LABOR-"
        "W19-SCREEN-SHARD-0..7 landed runnable_pool shared+lane (447->455 "
        "entries each, +288/+0 pure-add surgical diff, W18-SCREEN pattern "
        "verbatim; id/shard-key mirror runner literal trial_labor_w19.py "
        "L1255-1256; lane pinned bm-b per r429 machine-local checkpoint law "
        "-- prereg sec.9 'any healthy engine' superseded by checkpoint "
        "locality, W17 enrollment precedent disclosed in entry note; gates "
        "in-script per r859 two-leg intent with shape deviation disclosed: "
        "house string workers_plan vs submit --workers int, W17/W18 both "
        "hand-enrolled: runner_exists + prereg_frozen + data_deps_present + "
        "dup-id + inbox_guard fetch CLEAR); IGNITION KEY = this round's "
        "commit+push (r694-i one-tick claim gate reads origin), autofill "
        "claims at next tick. S0: stash/ff/pop clean (origin +3: bm-a r978 "
        "estate-absorb + bm-c r990 x2; token_usage.json pop conflict "
        "resolved stash-side live-wins + stash dropped post-resolution per "
        "r642). S0.5: orders diff = 1 unacked CEO order O-20261014-0925-bm-b "
        "(fleet-idle accountability, received via sibling bm-b session 09:25) "
        "-> acked this round (bm-b receipt face pre-filed by issuer; bm-b "
        "duty = O-0951/O-0030 load law standing; committee case + bm-c "
        "fill-window = addressee lanes); D-19 dual-delta zero (decisions "
        "86187eff / orders 348eaf34, consumed fresh probe bm-a r978 shared "
        "evidence results/_r686bmb_d19_check.json). S1 smoke 49/49. Round-"
        "zero orphan probe py_faces=11 orphans=0. SatEngine alive rc0 idle "
        "queue 0. W19 runner status face: grammar/cells/prep_state PRESENT "
        "+ A9 + G-TIMING PASS (screen absent = enrollment target confirmed). "
        "S6 quick legs: dualrun ZERO-DRIFT 455 entries streak 11 + "
        "compute_audit supply_floor REFILLED (ready 8 >= floor 3, "
        "starvation_candidate false; FLAG ignition_sla = ready-awaiting-push "
        "transient, self-heals next autofill tick post-push) + pywm "
        "insufficient_history legal + token delta 0 + attrition scan CLEAN. "
        "Inbox MSG-20261014-0855-bmc-w237-finalize = bm-a engine-lane "
        "(R31 zero-touch, left for addressee). idle_trigger --worked -> "
        "idle_rounds 0. STATE FACE RECONCILE: logs/iteration-loop/state.json "
        "was stale at 884 since 2026-10-11 15:10 (sessions r885-r929 wrote "
        "round-report lines + commits; state file unmaintained) -> this "
        "write realigns to 930 per report-ledger sequence."
    )
    s["verdict"] = (
        "green: W19 screen supply 8/8 enrolled dual-file + parse gates + "
        "id asserts ALL PASS; smoke 49/49; dualrun ZERO-DRIFT streak 11; "
        "attrition CLEAN; orders O-0925 acked (210 cumulative); orphan "
        "faces 0; flags = ignition_sla push-key transient + GPU "
        "PSU-deferred standing (MODE=pause, O-0925 sec3-3)"
    )
    s["next"] = (
        "r931: (a) verify autofill claims + burns W19-SCREEN-SHARD-0..7 "
        "(checkpoints results/trial_labor_w19/checkpoint/"
        "screen_shard_Nof8.jsonl machine-local; ~69 cells/shard stride "
        "i%8 of 546; W18 pace ~96min for 8 shards) -> screen-finalize "
        "(survival line + G-face battery + ledger append, reads local "
        "CKPT_DIR) -> judge-prep -> JUDGE pool entry + burn -> "
        "judge-finalize + w19_paired_deltas.json; 48h CEO report clock "
        "starts at judge landing; (b) S6 full chain at 10-14 15:30 data "
        "window; (c) standing: O-0925 committee enforcement case (bm-a "
        "lane), GPU PSU-swap MODE=pause, unity POC editor window, "
        "bili-reply CEO cookie+aid, MF panel bm-a lane crash-blocked"
    )
    s["current_task"] = ("r931: W19 screen burn watch -> screen-finalize "
                        "-> judge-prep/JUDGE enrollment")
    s["last_round_ts"] = NOW_ISO
    s["updated_at"] = NOW_ISO
    s["last_seen"] = NOW_ISO
    s["ts"] = NOW_ISO


ACK_NOTE = (
    "r930 bm-b ack: CEO fleet-idle accountability order received via "
    "sibling bm-b session 09:25 (receipt face pre-filed by issuer per "
    "sec-4); bm-b duties = sec3-3 standing (O-0951 power law + O-0030 "
    "CPU full-use law in force; GPU i2v 27/53 parked pending CEO/PSU "
    "ruling), W19 screen burn chain enrolled this round = the current "
    "bm-b CPU compute face; committee enforcement case + bm-c CPU "
    "fill-window = addressee lanes (bm-a/bm-c per order sec3-1/3-2)"
)


def mut_heartbeat(h):
    h["round"] = 930
    h["round_no"] = 930
    h["round_no_label"] = "r930"
    h["heartbeat_epoch_utc"] = int(time.time())
    h["clock_read"] = NOW_ISO
    h["ts"] = NOW_ISO
    h["updated"] = NOW_ISO
    h["updated_at"] = NOW_ISO
    h["last_seen"] = NOW_ISO
    h["last_round_at"] = NOW_ISO
    h["last_action_at"] = NOW_ISO
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["green_idle"] = False
    if "O-20261014-0925-bm-b.md" not in h["orders_ack"]:
        h["orders_ack"].append("O-20261014-0925-bm-b.md")
    h["orders_ack_count"] = len(h["orders_ack"])
    if "orders_ack_notes" not in h:
        h["orders_ack_notes"] = {}
    h["orders_ack_notes"]["O-20261014-0925-bm-b.md"] = ACK_NOTE
    h["orphan_face"] = 0
    h["orphan_faces"] = 0
    h["orphan_face_note"] = ("r930 round-zero probe 09:19: py_faces=11 "
                             "orphans=0 killed=[]")
    h["last_action"] = ("r930: W19 SCREEN supply enrollment 8/8 dual-file "
                        "(TRIAL-LABOR-W19-SCREEN-SHARD-0..7, gates green, "
                        "ignition key = closeout push) + CEO order "
                        "O-0925 acked")
    h["last_action_at"] = NOW_ISO
    h["current_task"] = ("r931: W19 screen burn watch (autofill claims "
                         "post-push) -> screen-finalize -> judge-prep -> "
                         "JUDGE enrollment")
    h["task"] = h["current_task"]
    h["did"] = (
        "r930 bm-b: W19 SCREEN supply enrollment MAIN PRODUCT: 8 pool "
        "entries TRIAL-LABOR-W19-SCREEN-SHARD-0..7 landed shared+lane "
        "(447->455, +288/+0 surgical, W18 pattern, runner-mirrored "
        "id/keys, lane pinned bm-b per r429 checkpoint law, inbox_guard "
        "CLEAR, parse gates ALL PASS); ignition = closeout push (r694-i "
        "one-tick claim gate). S0 stash/ff/pop clean (+3 origin, "
        "token_usage conflict stash-side live-wins); S0.5 orders: CEO "
        "O-20261014-0925-bm-b fleet-idle accountability acked (bm-b "
        "duty = load law standing; committee/bm-c faces = addressee "
        "lanes); D-19 dual-delta zero. S1 smoke 49/49; orphan probe 0; "
        "SatEngine alive rc0. S6: dualrun ZERO-DRIFT 455 streak 11; "
        "compute_audit supply_floor 8>=3 REFILLED + FLAG ignition_sla "
        "(push-key transient); pywm insufficient_history legal; token "
        "delta 0; attrition CLEAN. Inbox W237-finalize = bm-a lane "
        "(R31 zero-touch). state.json 884->930 reconcile (stale since "
        "10-11, report-ledger is the live sequence)."
    )
    h["verdict"] = (
        "GREEN: W19 screen supply 8/8 enrolled = trial-labor standing "
        "line execution (pool floor refilled 8>=3); all probes green "
        "(smoke 49/49, dualrun streak 11, attrition CLEAN, D-19 "
        "zero-delta, orders 0 unacked post-ack); flags = ignition_sla "
        "push-key transient (self-heals next tick) + GPU PSU-deferred "
        "standing (MODE=pause per O-0925 sec3-3)"
    )
    h["latest_artifact"] = (
        "results/runnable_pool.json TRIAL-LABOR-W19-SCREEN-SHARD-0..7 "
        "entries (09:28, shared+lane) + results/"
        "_r930bmb_w19_screen_enroll.json receipt"
    )
    h["now_active"] = (
        "autofill next tick claims W19-SCREEN-SHARD-0..7 post-push "
        "(~69 cells/shard CPU burn); SatEngine ticking idle; GPU idle "
        "MODE=pause PSU-deferred (O-0925 sec3-3)"
    )
    h["next"] = (
        "r931: (a) W19 screen burn watch -> screen-finalize -> "
        "judge-prep -> JUDGE enrollment+burn -> judge-finalize + "
        "w19_paired_deltas (48h CEO clock at judge landing); (b) S6 "
        "full chain 15:30 data window; (c) standing: O-0925 committee "
        "case (bm-a), GPU PSU-swap, unity POC, bili-reply CEO cookie, "
        "MF panel bm-a lane"
    )
    h["next_milestone"] = (
        "W19 SCREEN burns done + screen-finalize <= 2026-10-14 12:00; "
        "JUDGE <=48h (2026-10-16); S6 full chain 10-14 15:30"
    )
    h["note"] = (
        "r930: supply enrollment round (funnel screen-phase ignition); "
        "O-0925 CEO order acked same round; state face reconciled "
        "884->930 (stale-state disclosure in did)"
    )
    h["sync"] = {
        "last_push_ts": NOW_ISO,
        "note": ("r930: closeout commit+push follows this write; pool "
                 "enrollment = ignition key (r694-i one-tick claim "
                 "gate reads origin); delivery self-proof fetch+"
                 "rev-list follows push"),
    }


REPORT_LINE = (
    "| %s | r930 | bm-b [dept:research/strategy] | W19 SCREEN supply "
    "enrollment 8/8 MAIN PRODUCT: (1) S0 stash/ff/pop clean (origin +3 "
    "= bm-a r978 estate-absorb + bm-c r990 x2; token_usage.json pop "
    "conflict resolved stash-side live-wins + stash dropped "
    "post-resolution r642). (2) S0.5 orders: 1 unacked = CEO "
    "O-20261014-0925-bm-b fleet-idle accountability (received via "
    "sibling bm-b session 09:25) -> ACKED this round (receipt face "
    "pre-filed by issuer; bm-b duty = O-0951/O-0030 load law standing; "
    "committee enforcement case + bm-c fill-window = addressee lanes); "
    "D-19 dual-delta zero (decisions 86187eff/orders 348eaf34, fresh "
    "probe consumed results/_r686bmb_d19_check.json bm-a r978). (3) S1 "
    "smoke 49/49. (4) round-zero orphan probe py_faces=11 orphans=0. "
    "(5) SatEngine alive rc0 idle queue 0. (6) MAIN: 8x TRIAL-LABOR-"
    "W19-SCREEN-SHARD-0..7 enrolled into runnable_pool shared+lane "
    "double-file (447->455 entries each, +288/+0 pure-add surgical, "
    "W18-SCREEN pattern verbatim; id/shard-key mirror runner literal "
    "L1255-1256; lane pinned bm-b per r429 machine-local checkpoint "
    "law -- prereg sec.9 any-healthy-engine superseded by checkpoint "
    "locality, W17 enrollment precedent, disclosed in entry note; "
    "gates in-script: runner_exists + prereg_frozen + data_deps_present "
    "+ dup-id + inbox_guard fetch CLEAR; r859 two-leg intent honored "
    "with shape deviation disclosed: house string workers_plan vs "
    "submit --workers int, W17/W18 both hand-enrolled) -> IGNITION KEY "
    "= this push (r694-i one-tick claim gate), autofill claims next "
    "tick; W19 status face pre-enrollment: grammar/cells/prep_state "
    "PRESENT + A9 + G-TIMING PASS. (7) S6 quick legs: dualrun "
    "ZERO-DRIFT 455 entries streak 11 + compute_audit supply_floor "
    "REFILLED (ready 8>=floor 3, starvation_candidate false; FLAG "
    "ignition_sla = ready-awaiting-push transient self-heals next "
    "tick) + pywm insufficient_history legal + token delta 0 + "
    "attrition 4 CLEAN. (8) inbox MSG-20261014-0855-bmc-w237-finalize "
    "= bm-a engine-lane (R31 zero-touch, left for addressee). (9) S7: "
    "idle --worked idle_rounds=0; state.json 884->930 reconcile "
    "(stale since 10-11 15:10, report-ledger = live sequence, "
    "disclosed). | 当前活: W19 screen 8 分片池面点火推送收尾 | "
    "最近实物: results/runnable_pool.json SHARD-0..7 entries "
    "(09:28 shared+lane) + receipt results/_r930bmb_w19_screen_"
    "enroll.json | 下个里程碑: W19 screen burns done + "
    "screen-finalize <= 10-14 12:00, JUDGE <=48h (10-16), S6 full "
    "chain 15:30 | watermark: GREEN (red=false; next_pick claimed MF "
    "IC waits panel) | orphan-faces=0 (probe 09:19: py_faces=11 "
    "orphans=0) | orders: O-0925 acked (210 cumulative) | evidence: "
    "_r930bmb_w19_screen_enroll.py + receipt (gates + assertions) + "
    "git diff --numstat 288/0 x2 + dualrun streak 11 + compute_audit "
    "supply_floor 8>=3 + attrition CLEAN + smoke 49/49 | "
    "unacked_orders=0 | registry-zero-hit: no sweep/archive/delete "
    "actions this round | local-unreached-origin-commits: round-start "
    "3 (absorbed ff) -> closeout commit+push follows + self-proof | "
    "next-pointer r931: (a) W19 screen burn watch -> screen-finalize "
    "-> judge-prep -> JUDGE enrollment+burn -> judge-finalize + "
    "w19_paired_deltas (48h CEO clock at judge landing); (b) S6 full "
    "chain 15:30; (c) standing: O-0925 committee case (bm-a), GPU "
    "PSU-swap MODE=pause, unity POC, bili-reply CEO cookie, MF panel "
    "bm-a lane | [r930 bm-b]"
) % NOW_ISO


def append_report():
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    with open(p, "rb") as f:
        raw = f.read()
    eol = b"\r\n" if raw.count(b"\r\n") >= (raw.count(b"\n") - raw.count(b"\r\n")) else b"\n"
    if not raw.endswith(eol):
        raw = raw + eol
    with open(p, "wb") as f:
        f.write(raw + REPORT_LINE.encode("utf-8") + eol)
    print("report line appended (eol=%s)" % eol)


load_rewrite(os.path.join(ROOT, "logs", "iteration-loop", "state.json"), mut_state)
load_rewrite(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), mut_heartbeat)
append_report()
print("closeout writes done %s" % NOW_ISO)
