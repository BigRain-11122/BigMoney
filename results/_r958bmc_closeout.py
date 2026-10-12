# -*- coding: utf-8 -*-
# r958 closeout: state + heartbeat + round report writes (JSON-safe python).
import json, time, datetime, sys
sys.stdout.reconfigure(encoding="utf-8")
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_short = now.replace("T", " ")[0:19]
epoch = int(time.time())

REPORT_LINE = ("| " + now + " | r958 | bm-c: W228 PREREG DERIVED+LANDED (product research/PERPETUAL_N1_W228_PREREG.md @ origin e6c8441aa, "
 "freeze-time face sha16 45c99338c49b0c1b 24,492B) -- TWELVE-level lineage replay (pairs216+SUB17..SUB27) preflight 46/46 replayed blocks "
 "count==1 in freeze-time W227 blob 0d0c63c6e; find sides machine-generated from committed _w227 SUB new-sides via results/_w228bmc_subgen.py "
 "m25-materialization zero-transcription + authored repls R28 (_w228bmc_r28_data.py) all runtime count-asserted; bands A 516_404..518_403 / "
 "B 518_404..518_603 per ADMIT receipt _w228bmc_20261013; S5 anchors machine-read n1_w227_results ledger 923,189/K=497,320/mu -0.09275553/"
 "sigma 0.24507723/A p95 0.3206/KL 1.1917 +0.0000/se_mu 0.000348; S5.5 W229+ projection A 518_404..520_403/B 518_604..518_803 EIGHTY-NINTH "
 "anticipated; STALE x73 zero NEW x49 present; freeze label r958 2026-10-13 7:4x; pitfall: ast.Dict.keys is a list attribute not method -- "
 "node.keys() TypeError silently fakes extract-fail (dbg probes committed) | S0.5 dual-delta FALSE both (dec fb5825cb/ord d559e530, unacked=0; "
 "S7 closeout double-scan same) | S1 smoke 49/49 | satengine rc0 ALIVE | S6 light: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG "
 "pool_starvation/supply_floor structural (answered by this prereg; splice+burn next) + wm py_low_board_clear legal | attrition 4 CLEAN "
 "(1 healed shrink) | S7 quad green (loop pin=5 no-op + watchdog re-armed + pre-commit/pre-push claws installed) + round-zero probe "
 "py_faces=8 orphans=2 zero-kill | splice editor clone map landed results/_w228bmc_freeze_clone_map.md (cut m225/estate 83/block 86 rows/"
 "legs w225+w226+w227) | counter 958->959 | W228 five-face freeze splice = next window FIRST ACTION |")

open(r"round_reports-bm-c.md", "a", encoding="utf-8").write(REPORT_LINE + "\n")

st = json.load(open(r"state-bm-c.json", encoding="utf-8"))
st["round_no"] = 959
st["last_round"] = 958
st["last_round_at"] = now
st["last_round_ts"] = epoch
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["clock_read"] = now
st["heartbeat_epoch_utc"] = epoch
st["last_seen"] = now_short
st["current_task"] = "r959 W228 freeze-splice editor derive+run (clone map results/_w228bmc_freeze_clone_map.md + committed _w227bmc_freeze_edits.py = full recipe) -> engine self-burn 12/12 -> PRE-FINALIZE six-gate -> finalize one-pass -> five-key + sec.7/8 backfill"
st["current_task_at"] = now
st["current_task_ts"] = now
st["did"] = ("r958 (W228 prereg derive window): (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; S0 fetch behind=0/ahead=0 "
 "(r957 push landed), round-start dirty=6 all own bm-c live faces (collected at closeout); (2) S0.5 dual-delta FALSE both (dec fb5825cb / ord "
 "d559e530 hold, unacked=0) + S7 closeout double-scan same; (3) S1 smoke 49/49; boards clear (jobs 0, fleet open=0); satengine rc0 ALIVE; "
 "wm red=false lane healthy (next_pick claimed moneyflow IC batch = bm-a lane); (4) PRODUCT = W228 PREREG derived+landed origin e6c8441aa "
 "(research/PERPETUAL_N1_W228_PREREG.md sha16 45c99338c49b0c1b; TWELVE-level replay preflight 46/46; finds machine-generated via "
 "_w228bmc_subgen m25 from committed _w227 SUB new-sides zero-transcription; bands A 516_404..518_403 / B 518_404..518_603; S5 anchors "
 "machine-read W227 ledger 923,189 / K 497,320 / mu -0.09275553 / sigma 0.24507723 / A p95 0.3206 / KL 1.1917 +0.0000 / se_mu 0.000348; "
 "S5.5 W229+ projection A 518_404..520_403 / B 518_604..518_803 EIGHTY-NINTH; STALE x73 zero NEW x49 present); (5) splice editor clone map "
 "landed results/_w228bmc_freeze_clone_map.md; (6) S6 light: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG pool_starvation/supply_floor "
 "structural (answered by prereg; splice+burn next) + wm py_low_board_clear legal; (7) S7 quad green + attrition 4 CLEAN (1 healed shrink); "
 "counter 958->959")
st["verdict"] = ("green: W228 PREREG LANDED (origin e6c8441aa; TWELVE-level replay preflight 46/46; bands A 516_404..518_403 / B "
 "518_404..518_603; STALE zero / NEW all-present; S5 anchors machine-read W227 ledger 923,189 / K 497,320) + smoke 49/49 + dualrun streak 51 "
 "+ wm py_low_board_clear legal + S7 quad green + attrition CLEAN; audit FLAG pool_starvation/supply_floor structural answered by this "
 "prereg (chain continues splice -> burn -> six-gate -> finalize)")
st["next"] = ("r959: (1) W228 freeze-splice editor derive+run FIRST ACTION (results/_w228bmc_freeze_clone_map.md structural pairs: cut m225 / "
 "estate 83 / par_full 85 / legs w225+w226+w227 / block 86 rows; clone of committed _w227bmc_freeze_edits.py) -> engine mtime-watch "
 "self-burn 12/12 -> PRE-FINALIZE six-gate (W217-debt standing law) -> finalize one-pass -> five-key + sec.7/8 machine-read backfill; "
 "(2) Tue 15:30 new-bar window: papers full chain + update family; (3) W229 seat publish after W228 finalize per seat-first law; "
 "(4) W229+ projection A 518_404..520_403 / B 518_604..518_803 re-derive mandate inherited (A-hops-prior-B EIGHTY-NINTH instance anticipated)")
st["next_pointer"] = st["next"]
st["last_round_summary"] = ("r958: W228 prereg derived+landed (origin e6c8441aa, freeze-time face sha16 45c99338c49b0c1b, TWELVE-level "
 "replay preflight 46/46) + splice clone map + S6 light streak 51 + S7 quad green; counter 958->959")
st["last_round_closed"] = now
st["last_action"] = "r958 closeout (W228 prereg derive+land + S6 light + S7 quad)"
st["last_action_at"] = now
st["latest_artifact"] = "research/PERPETUAL_N1_W228_PREREG.md (origin e6c8441aa) + results/_w228bmc_freeze_clone_map.md"
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("W228 freeze splice + engine self-burn 12/12 + PRE-FINALIZE six-gate + finalize (next window first action per clone "
 "map); Tue 15:30 new-bar papers full chain")
st["prod_lanes"] = ("GPU=MV i2v lane idle-warm (queue 0/0, ComfyUI resident; director re-shakes + assembly ride bm-a lane); CPU=N1 W227 FULL "
 "CYCLE LANDED (923,189 / K 497,320) + W228 SEATED + PREREG LANDED (origin e6c8441aa; freeze splice = next window first action per chain law)")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["activity_now"] = ("2026-10-13 07:5x | r958 | bm-c: W228 prereg derived+landed origin e6c8441aa (TWELVE-level replay, preflight 46/46, "
 "STALE zero) + splice clone map landed; counter 958->959")
st["now_active"] = st["activity_now"]
st["sync"] = {"origin_tip": "e6c8441aa (W228 prereg landed; r958 closeout rides this window)",
              "ts": now, "ahead_behind": "0/0 post-push", "note": "r958: W228 prereg + clone map + S6 light + S7 closeout; state/heartbeat this round"}
st["r958_closeout_note"] = ("r958: clean continuation window (state round_no was 958 at open; executed as r958 per counter, advanced 958->959 so "
 "next session = r959); zero double-count: S0.5 dual-delta FALSE both windows (dec fb5825cb / ord d559e530 current, zero consumption owed); "
 "product = W228 prereg derive (machine-generated finds from committed lineage SUB new-sides, zero transcription) landed origin e6c8441aa + "
 "splice editor clone map (results/_w228bmc_freeze_clone_map.md) for the next-window splice; pitfall found+fixed same-window: "
 "ast.Dict.keys is a list attribute, node.keys() raises TypeError which the extract try/except silently converts to a fake extract-fail "
 "(dbg probes results/_w228bmc_dbg17*.py committed as evidence)")
json.dump(st, open(r"state-bm-c.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

hb = json.load(open(r"fleet\machines\bm-c.json", encoding="utf-8"))
hb["last_seen"] = now_short
hb["ts"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["activity_now"] = st["activity_now"]
hb["now_active"] = st["activity_now"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["verdict"] = "green: W228 prereg landed origin e6c8441aa + smoke 49/49 + S6 light streak 51 + S7 quad green"
hb["last_round"] = "r958"
hb["round_no"] = 959
json.dump(hb, open(r"fleet\machines\bm-c.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

chk = json.load(open(r"fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601 (R262 law)"
print("closeout writes OK:", now, "| epoch int:", chk["heartbeat_epoch_utc"], "| state round_no:", st["round_no"])
