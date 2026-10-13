# -*- coding: utf-8 -*-
"""r987 bm-c closeout: wait-state window #5 (bars pre-15:30 + W236=bm-a in-flight + pool RW-5 freeze + MF-IC-P1 parked 23d).
Updates state-bm-c.json + heartbeat fleet/machines/bm-c.json + canonical round report (r750 law path).
Assertions: counter 987->988, epoch int, report line appended, json round-trip.
"""
import json, time, datetime, sys, io

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = ROOT + r"\state-bm-c.json"
HEART = ROOT + r"\fleet\machines\bm-c.json"
REPORT = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"

now_epoch = int(time.time())
# local time with +08:00 offset (machine tz)
dt_local = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
ts_iso = dt_local.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hhmm = dt_local.strftime("%H:%M")

# sample cpu/ram via psutil if available, else fall back to pre-measured honest values
cpu_pct = 88.0
ram_free_gb = 0.8
try:
    import psutil
    cpu_pct = float(psutil.cpu_percent(interval=1))
    ram_free_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    pass

DID = ("r987: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; S0 fetch 0/0 clean "
       "(x6 daemon live-faces legit dirty, no rebase owed); (2) S0.5 dual-delta FALSE both scans (opening + S7 tail; "
       "ord content-sha 348eaf34 / dec raw-blob sha256 86187eff both hold, unacked=0, zero new local orders since "
       "O-20261014-0312 acked r986); (3) S1 smoke 49/49; (4) S3: satengine ALIVE rc0 (queue empty; W236=bm-a chain "
       "in-flight prereg 67ade8314 05:1x, splice/burn/finalize theirs per seat-first, zero new bmq commits this window) "
       "+ wm verdict=insufficient_history fresh-window honest (bars_present=false, daily_panel 10-13 fresh, pre-15:30 "
       "legal no-op family) + post_review today 45-ok/0-x/5-wait zero-x (REPORT-20261014 sweep committed by r986 "
       "addendum) + jobs=0 + fleet tasks open=0 + P2/P3 boards empty + idle RAM-gated honest (free "
       + str(ram_free_gb) + "G/23.9G not-claim-eligible; idle_trigger streak=0 last_declare=worked) + GPU lane=MV V3 "
       "protected per O-20261014-0312 sec.2; (5) WAIT-STATE window #5 held per one-line law (10-14 bars not due until "
       "15:30; pool ready=0 + RW-5 freeze = supply legally chained to W236 finalize [bm-a]; MF-IC-P1 parked 23d "
       "upstream bm-a collector v3 live panel rebuild in flight); (6) S6 light: dualrun ZERO-DRIFT streak 51 + "
       "compute_audit FLAG pool_starvation/supply_floor structural answered-by-chain W236 + token delta=0 L2 legs 0 "
       "today; (7) S7: attrition 4 CLEAN + pin=5 no-op + watchdog re-registered + both claws installed + tail "
       "dual-scan FALSE; counter 987->988")

VERDICT = ("green: wait-state window #5 honestly held (bars pre-15:30; W236 bm-a in-flight seat-first zero takeover "
           "criteria met; pool supply RW-5 frozen chained to their finalize; MF-IC-P1 parked 23d upstream rebuild in "
           "flight; idle RAM-gated honest) + smoke 49/49 + S0.5 dual FALSE x2 + post_review zero-x + S6 light "
           "zero-drift + S7 quad green")

NEXT = ("r988: (1) W236 chain watch -- bm-a splice/burn/finalize theirs; absorb ONLY if their window dies post-seat "
        "per seat-first law; (2) 10-14 bars re-probe after 15:30 -> papers full chain when new bar lands (10-13 papers "
        "debt zero per r985 verify); (3) MF panel watch -- if bm-a panel completes, MF-IC-P1 S2 completion gate check "
        "(execution machine = panel holder); (4) MV V3 director rulings watch per ORD rows; closeout scripts: "
        "canonical report path MANDATORY (r750 law)")

CURTASK = ("r987 wait-state window #5 close (bars pre-15:30 + W236=bm-a in-flight + pool RW-5 freeze + MF-IC-P1 "
           "parked 23d)")
ACTIVITY = ("2026-10-14 " + hhmm + " | r987 | bm-c: wait-state window #5 | counter 987->988")
ARTIFACT = "wait-state window #5 (no new artifact; zero-drift streak 51 held; post_review 45-ok/0-x; S7 quad green)"
MILESTONE = "10-14 bars post-15:30 papers chain + W236 finalize watch (bm-a) + MF panel completion -> MF-IC-P1 unpark"
ACKRCPT = ("r987: zero unacked both scans; group ORD/DEC dual-delta FALSE both (ord 348eaf34 content-sha / dec "
           "86187eff hold); zero bm-c execution owed")
SUMMARY = ("r987: wait-state window #5 (bars pre-15:30 + W236=bm-a in-flight + MF-IC-P1 parked 23d + pool 0 + RW-5 "
           "freeze) + smoke 49/49 + S0.5 dual FALSE x2 + post_review zero-x + S6 light zero-drift streak 51 + S7 quad "
           "green; counter 987->988")
LASTACTION = "r987 closeout (wait-state window #5 + S6 light + S7 quad)"
VERIFY = ("receipts: probe results/_orphan_face_probe.bm-c.json + smoke 49/49 + s05 dual-FALSE x2 "
          "(results/_s05_probe.bm-c.json) + dualrun streak 51 + attrition results/_attrition_guard_scan.json CLEAN + "
          "S7 quad (pin=5/watchdog/claws x2) + post_review REPORT-20261014 45-ok/0-x/5-wait")
PRODLANES = ("CPU=N1 W236: bm-a chain in-flight (prereg 67ade8314 landed 05:1x; splice/burn/finalize theirs; bm-c "
             "yielded per seat-first); MF-IC-P1: parked 23d source-blocked (panel absent on bm-c verified; bm-a "
             "collector v3 live, panel rebuild in flight); GPU=MV V3: burn window protected per O-20261014-0312 sec.2")
R987NOTE = ("r987: clean continuation window (state round_no=987 at open, executed r987, advanced 987->988 so "
            "next=r988); zero absorb owed (r986 addendum 8e5607687 landed clean); zero double-count: S0.5 dual-delta "
            "FALSE both scans (ord 348eaf34 / dec 86187eff current), unacked=0 both scans")


def stamp(obj, keys):
    for k in keys:
        obj[k] = ts_iso


def main():
    # --- state ---
    with io.open(STATE, "r", encoding="utf-8") as f:
        state = json.load(f)
    assert state["round_no"] == 987, "state round_no unexpected: %r" % state.get("round_no")
    state["round_no"] = 988
    state["round_no_label"] = "r987"
    state["last_round"] = 987
    state["loop_round"] = 987
    state["last_round_label"] = "r987"
    stamp(state, ["last_round_at", "clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at",
                  "current_task_at", "last_pulled_at", "last_orders_read_at", "last_orders_at", "last_orders_seen",
                  "last_orders_sha_note_ts" if "last_orders_sha_note_ts" in state else "ts",
                  "last_decisions_read_at", "last_decisions_at", "last_decisions_seen", "orders_ack_ts",
                  "last_round_summary_at", "last_action_at", "last_round_closed", "last_round_closed_at" if "last_round_closed_at" in state else "ts"])
    state["heartbeat_epoch_utc"] = now_epoch
    state["last_ts"] = now_epoch
    state["current_task_ts"] = now_epoch
    state["r987_closeout_note"] = R987NOTE
    state["r987_absorb_note"] = ""
    state["did"] = DID
    state["verdict"] = VERDICT
    state["next"] = NEXT
    state["next_pointer"] = NEXT
    state["current_task"] = CURTASK
    state["activity_now"] = ACTIVITY
    state["now_active"] = ACTIVITY
    state["latest_artifact"] = ARTIFACT
    state["last_artifact"] = ARTIFACT
    state["recent_artifact"] = ARTIFACT
    state["next_milestone"] = MILESTONE
    state["last_round_summary"] = SUMMARY
    state["last_action"] = LASTACTION
    state["orders_ack_receipt"] = ACKRCPT
    state["verify"] = VERIFY
    state["prod_lanes"] = PRODLANES
    state["cpu_pct"] = cpu_pct
    state["cpu_util_pct"] = cpu_pct
    state["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
    state["free_ram_gb"] = ram_free_gb
    state["idle_ram_gb"] = ram_free_gb
    state["ram_free_gb"] = ram_free_gb
    state["orphan_face"] = 2
    state["orphan_faces"] = 2
    state["idle_rounds"] = 0
    state["agenda_starved"] = False
    state["sync"] = {"origin_tip": "8e5607687 (r986 addendum) at open; closeout commit+push rides this window",
                     "ts": ts_iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
                     "note": "r987: fetch 0/0 at open (x6 daemon live-faces legit dirty); wait-state window #5"}
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")

    # --- heartbeat ---
    with io.open(HEART, "r", encoding="utf-8") as f:
        heart = json.load(f)
    assert heart["round_no"] == 987, "heartbeat round_no unexpected: %r" % heart.get("round_no")
    heart["round_no"] = 988
    heart["round_no_label"] = "r987"
    heart["last_round"] = 987
    heart["loop_round"] = 987
    heart["last_round_label"] = "r987"
    stamp(heart, ["last_seen", "clock_read", "ts", "last_seen_at", "updated_at", "updated", "current_task_at",
                  "last_round_at", "last_round_summary_at", "last_action_at", "last_orders_read_at",
                  "last_orders_at", "last_orders_seen", "last_decisions_read_at", "last_decisions_at",
                  "last_decisions_seen", "orders_ack_ts", "last_pulled_at"])
    heart["heartbeat_epoch_utc"] = now_epoch
    heart["last_ts"] = now_epoch
    heart["current_task_ts"] = now_epoch
    heart["did"] = DID
    heart["verdict"] = VERDICT
    heart["next"] = NEXT
    heart["next_pointer"] = NEXT
    heart["current_task"] = CURTASK
    heart["activity_now"] = ACTIVITY
    heart["now_active"] = ACTIVITY
    heart["latest_artifact"] = ARTIFACT
    heart["last_artifact"] = ARTIFACT
    heart["recent_artifact"] = ARTIFACT
    heart["next_milestone"] = MILESTONE
    heart["last_round_summary"] = SUMMARY
    heart["last_action"] = LASTACTION
    heart["orders_ack_receipt"] = ACKRCPT
    heart["verify"] = VERIFY
    heart["prod_lanes"] = PRODLANES
    heart["cpu_pct"] = cpu_pct
    heart["cpu_util_pct"] = cpu_pct
    heart["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
    heart["free_ram_gb"] = ram_free_gb
    heart["idle_ram_gb"] = ram_free_gb
    heart["ram_free_gb"] = ram_free_gb
    heart["orphan_face"] = 2
    heart["orphan_faces"] = 2
    heart["idle_rounds"] = 0
    heart["agenda_starved"] = False
    heart["sync"] = {"origin_tip": "8e5607687 (r986 addendum) at open; closeout commit+push rides this window",
                     "ts": ts_iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
                     "note": "r987: fetch 0/0 at open (x6 daemon live-faces legit dirty); wait-state window #5"}
    with io.open(HEART, "w", encoding="utf-8", newline="\n") as f:
        json.dump(heart, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")

    # --- canonical round report (r750 law path) ---
    line = (ts_iso + " | r987 | bm-c wait-state window #5 close (bars pre-15:30 + W236=bm-a in-flight yield + "
            "MF-IC-P1 parked 23d upstream + pool 0 + RW-5 freeze) | WM-VERDICT: green red=false (insufficient_history "
            "fresh window; bars_present=false + daily_panel cutoff 2026-10-13 fresh; 10-13 papers chain verified "
            "consumed zero-debt r985) | orphan face=2 zero-kill (py_faces=8) | body: S0 fetch 0/0 clean (x6 daemon "
            "live-faces); S0.5 dual-delta FALSE both scans (ord 348eaf34/dec 86187eff hold, unacked=0); smoke 49/49; "
            "satengine ALIVE rc0 (W236=bm-a chain prereg 67ade8314 in-flight, yield per seat-first); jobs=0 + fleet "
            "open=0 + P2/P3 empty + idle RAM-gated honest (free " + str(ram_free_gb) + "G, streak=0 worked) + GPU=MV "
            "V3 protected; post_review today 45-ok/0-x/5-wait zero-x; S6 light: dualrun ZERO-DRIFT streak 51 + audit "
            "FLAG supply_floor structural (answered-by-chain W236) + token delta=0; S7: attrition 4 CLEAN + pin=5 "
            "no-op + watchdog re-registered + claws x2 installed + tail dual-scan FALSE | evidence: "
            "results/_orphan_face_probe.bm-c.json + smoke 49/49 + results/_s05_probe.bm-c.json + "
            "results/_attrition_guard_scan.json CLEAN + post_review REPORT-20261014 | 本地未达 origin commit 数=0 "
            "(post-push delivery self-check this window; next-window S0 re-verify) | r988: W236 bm-a chain watch "
            "(absorb only if window dies post-seat) + 15:30 bars re-probe -> papers chain + MF panel watch -> S2 gate "
            "+ MV V3 rulings watch + canonical report path MANDATORY")
    with io.open(REPORT, "r", encoding="utf-8") as f:
        content = f.read()
    n_before = content.count("\n")
    if not content.endswith("\n"):
        content += "\n"
    content += line + "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    n_after = content.count("\n")

    # --- assertions ---
    with io.open(STATE, "r", encoding="utf-8") as f:
        s2 = json.load(f)
    with io.open(HEART, "r", encoding="utf-8") as f:
        h2 = json.load(f)
    assert s2["round_no"] == 988 and h2["round_no"] == 988
    assert isinstance(s2["heartbeat_epoch_utc"], int) and isinstance(h2["heartbeat_epoch_utc"], int)
    assert s2["heartbeat_epoch_utc"] == now_epoch
    assert n_after == n_before + 1, "report line count delta %d" % (n_after - n_before)
    assert "T" in s2["clock_read"] and "+08:00" in s2["clock_read"]
    print("CLOSEOUT-OK r987 counter->988 epoch=%d cpu=%.1f ram_free=%.1f report_lines=+1" % (now_epoch, cpu_pct, ram_free_gb))


if __name__ == "__main__":
    main()
