# -*- coding: utf-8 -*-
# r926 bm-b closeout: state.json + round_reports.md + heartbeat atomic update
import json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

DID = ("r926 dead-session-takeover closeout: (1) S0 deep surgery: adopted r925 estate (37 files/0 deletions, watchdog-killed 07:27 pre-closeout) "
       "+ stacked rebase x2 (3+6 UU daemon live faces take-theirs live-wins + r815 drift-normalize loop recipe) "
       "+ pre-push claw race window resolved WITHOUT --no-verify (bm-a W238 seat 3e551d846 landed between my fetch/push -> re-rebase onto it -> claw passed clean) "
       "+ delivery 3e551d846..923caac39 = r925 product JUDGED-2026-10-09.json (first judged N2U3 channel-1 evidence, lawful-zero, k=32 n_registered=0) UNSTRANDED on origin. "
       "(2) S0.5 orders 0 unacked (209/209); D-19 dual-delta zero (decisions b137f331/orders 348eaf34). (3) S1 smoke 49/49. (4) round-zero orphan probe py_faces=17 orphans=0. "
       "(5) SatEngine alive rc0. (6) S6 quick legs: dualrun ZERO-DRIFT streak 8 + compute_audit FLAG pool_starvation/supply_floor (W19=the refill, prereq complete in-repo) "
       "+ pywm py_low_board_clear LEGAL + token delta 0 + attrition 4 CLEAN. (7) idle --worked -> idle_rounds=0. "
       "(8) W19 frozen-prereg authoring NOT completed this round (S0 surgery consumed half the 25min watchdog window) -- honest non-completion; "
       "r927 one-round job with all pieces in hand: draft sec.0-8 committed + freeze-probe 8/8 committed + next-pointer precise")

NEXT = ("r927: (a) W19 FREEZE funnel 3/5 = author research/TRIAL_LABOR_W19_PREREG.md full template from draft sec.0-8 "
        "+ freeze-probe facts 8/8 (results/_r925bmb_w19_freeze_probe.json: L1 timing-isolation census zero rows W1-W18, L2 apply_timing anchor, "
        "L3 entry-source sha CRLF-canonical 22179881b7537193, L4 W17/W18 consumption canons, L5 seeds full-band 20640000 span=1001 FREE, L6 BAN-04 ADMIT, L7 collision CLEAR) "
        "+ SEED_REGISTRY trio 20640000/20640500/20641000 same-commit (registry lives in seed_admit_gate tooling) + wave ticket T-2026-10-14-<seq>-P1 (last=T-2026-10-09-178, pick next free seq) "
        "+ F-04 MSG same-round + freeze gates rc0 re-run (banned_direction_gate --prereg + seed_admit_gate span=1001 + queue_head_collision_probe) = funnel 3/5 completion; "
        "(b) runner build funnel 4/5 (clone trial_labor_w18.py + _entry_load CRLF recipe verbatim + G-face determinism battery as-burned==W17 control==W18 xgate 43/173); "
        "(c) S6 full chain at 10-14 15:30 window (r925 ran 06:18-07:04 32/32 rc0, pre-15:30 legs all no-op this morning); "
        "(d) standing: GPU PSU-swap MODE=pause (i2v 27/53 held), unity POC editor window, Speech-02/Music3 gates, bili-reply CEO cookie+aid, MF panel bm-a lane crash-blocked")

VERDICT = ("GREEN: r925 estate unstranded and delivered on origin (JUDGED-2026-10-09 first judged N2U3 evidence = CEO-visible product) + all probes green; "
           "flags = supply_floor/pool_starvation (W19 freeze+burn = the refill, funnel 3/5 prereq complete in-repo) + GPU PSU-deferred (MODE=pause) "
           "+ W19 freeze authoring honestly not completed this round -> r927 precise continuation")

# --- state.json ---
sp = ROOT + r"\state.json"
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round"] = 926
st["round_no"] = 927
st["round_no_label"] = "r926"
st["did"] = DID
st["next"] = NEXT
st["verdict"] = VERDICT
st["last_action"] = "r926: r925 estate delivered on origin (JUDGED-2026-10-09 unstranded) + S0 double-rebase surgery + claws race resolved clean"
st["last_action_at"] = ts
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["last_seen"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["current_task"] = "r927: W19 FREEZE funnel 3/5 (one-round job, all prereqs in hand) + runner build start"
st["task"] = st["current_task"]
st["latest_artifact"] = "results/alphagen_rl_p1/JUDGED-2026-10-09.json (delivered on origin via 923caac39) + results/_r925bmb_w19_freeze_probe.json (8/8 PASS)"
st["next_milestone"] = "W19 frozen prereg + ignition (supply refill of starved pool, ready 0<floor 3); S6 full chain 10-14 15:30"
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_face_note"] = "r926 probe 07:33: py_faces=17 orphans=0 killed=[]"
st["now_active"] = "SatEngine ticking idle (queue 0); GPU idle MODE=pause PSU-deferred; backfill_ext_slots detached pythonw running (data lane, legal); W19 freeze = r927 one-round job"
st["sync"] = {
    "last_push_ts": ts,
    "note": "r926: closeout commit+push follows this write; delivery self-proof via fetch+rev-list",
}
st["note"] = "r926: fourth dead-session-takeover link in r923-r926 chain; each link landed verifiable product (r923 repair, r925 JUDGED delivery, r926 estate unstranding on origin)"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# --- round_reports.md (bm-b lane file per S5) ---
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
line = (f"{ts} | r926 | bm-b | {DID} | 证据: push 3e551d846..923caac39 + closeout push follows + smoke 49/49 + dualrun streak8 + "
        f"attrition CLEAN + orphan_face=0 | 下轮: W19 FREEZE funnel 3/5 one-round job (draft sec.0-8 + probe 8/8 + seeds trio + ticket + F-04 + gates rc0)\n")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# --- heartbeat fleet/machines/bm-b.json ---
hp = ROOT + r"\fleet\machines\bm-b.json"
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["round"] = 926
hb["round_no"] = 927
hb["round_no_label"] = "r926"
hb["clock_read"] = ts
hb["ts"] = ts
hb["last_seen"] = ts
hb["last_round_at"] = ts
hb["last_action"] = st["last_action"]
hb["last_action_at"] = ts
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["next"] = NEXT
hb["did"] = DID
hb["verdict"] = VERDICT
hb["heartbeat_epoch_utc"] = epoch
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["green_idle"] = False
hb["orphan_face"] = 0
hb["orphan_face_note"] = st["orphan_face_note"]
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["now_active"] = st["now_active"]
hb["sync"] = st["sync"]
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# self-proof: epoch is int
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
print("CLOSEOUT-OK", ts, "epoch", epoch, "type", type(hb["heartbeat_epoch_utc"]).__name__)
