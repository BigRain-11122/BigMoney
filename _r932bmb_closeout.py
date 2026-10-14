# -*- coding: utf-8 -*-
# r932 bm-b closeout: state.json + heartbeat + round report append.
# Salvage + integration round; judge-finalize disclosed in-flight.
import json, time, io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- state.json (bm-b face) ----
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 932
st["round_no_label"] = "r932"
st["clock_read"] = now_iso
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_seen"] = now_iso
st["current_task"] = ("r933: verify W19 judge-finalize landing (PID 17108 "
                      "in flight, do NOT relaunch) -> intake -> next wave")
st["did"] = ("r932 bm-b (salvage+integration, judge-finalize disclosed "
             "in-flight): S0 ff +4 origin (bm-a r983/984 absorbed) with 18 "
             "stale shared regen faces discarded pre-stash ts-newer-wins "
             "(r930 law) + marks-20261014.jsonl pop conflict resolved "
             "HEAD-identical with fsck-verified ZERO unique-loss (stash "
             "theirs 10/10 lines contained in HEAD 11) + prior dead "
             "instance salvage: scripts/trial_labor_w19.py zero-variance "
             "guard patch (25+/6-, judge-finalize DSR crash fix x2 "
             "forensics _r932bmb_jf.err) COMMITTED + detached "
             "judge-finalize PID 17108 (launched 12:33:28 by dead "
             "instance) alive 36+ CPU-min, products pending. S0.5: "
             "orders 0 unacked (88 files); D-19 dual-delta consumed "
             "(dec d77f5fa1 ord 83454e8f; new rows D-20261014-01..04 "
             "zero BigMoney dispatch -- bigmoney mentions informational "
             "re HQ-FEEDBACK staleness, face belongs to us; watermark "
             "ADVANCED). S1 smoke 49/49. SatEngine alive rc0 idle. S6 "
             "quick legs: dualrun ZERO-DRIFT streak 17 (456 entries) + "
             "compute_audit FLAG supply_floor (pool 0/3 behind W19 "
             "chain, structural, refill next wave) + pywm "
             "insufficient_history local_batch=1 (the finalize itself) + "
             "minute_feed +20 rows intraday + astock/etf/rev_osc no-op "
             "fresh + thermo DONE + dualarm written + token 0 + "
             "attrition CLEAN. PS pit hit: stash@{0} unquoted = "
             "hashtable mangle (pit-git CRT family, second hit today).")
st["last_action"] = ("r932: dead-instance salvage landed (patch committed) "
                     "+ S0 ff+4 + D-19 consumed/advanced + S6 legs green; "
                     "judge-finalize in flight")
st["last_action_at"] = now_iso
st["next"] = ("r933: (a) W19 judge-finalize landing verify: if PID 17108 "
              "exited, read results/trial_labor_w19/judge_finalize_r932b."
              "err.log -- products present (w19_judge.json + "
              "w19_reform_face.json + w19_paired_deltas.json) -> verify "
              "faces (n_judged 112, g1_pass_n, eligible_v2/reform, "
              "zero_variance_arms_excluded disclosed, paired per_face, "
              "onboard_list) -> python scripts/trial_labor_w19.py intake "
              "(s4, gate w19_reform_face) -> commit+push products (48h "
              "CEO clock starts at judge landing) -> THEN next candidate "
              "wave enrollment (supply_floor refill, standing "
              "trial-labor line); if died w/o products: iterate patch + "
              "relaunch DETACHED (r834 lesson); DUAL-IGNITION GUARD: "
              "never relaunch while a trial_labor_w19 judge-finalize "
              "python process is alive; (b) S6 full chain 10-14 15:30 "
              "data window (new-bar legs re-arm); (c) standing: GPU "
              "PSU-swap MODE=pause (i2v 27/53 held), unity POC editor "
              "window, bili-reply CEO cookie+aid, MF panel bm-a lane")
st["verdict"] = ("GREEN: salvage+integration complete, judge-finalize "
                 "healthy in flight (36+ CPU-min active); smoke 49/49; "
                 "dualrun streak 17; attrition CLEAN; orders 0 unacked; "
                 "D-19 consumed+advanced; flags = supply_floor "
                 "structural (pool empty behind W19, next-wave refill "
                 "follows judge landing) + GPU PSU-deferred standing "
                 "(MODE=pause)")
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---- heartbeat fleet/machines/bm-b.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["last_seen"] = now_iso
hb["last_round_at"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["round"] = 932
hb["round_no"] = 932
hb["round_no_label"] = "r932"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "r932 round-zero probe 12:52: py_faces=21 orphans=0"
hb["current_task"] = st["current_task"]
hb["did"] = st["did"]
hb["last_action"] = st["last_action"]
hb["last_action_at"] = now_iso
hb["next"] = st["next"]
hb["next_milestone"] = ("W19 judge-finalize landing verify + intake + "
                        "product push <=10-14 14:00 (48h CEO clock at "
                        "judge landing); S6 full chain 10-14 15:30; "
                        "next wave enrollment post-W19")
hb["verdict"] = st["verdict"]
hb["now_active"] = ("judge-finalize PID 17108 (1 core, W19 verdicts "
                    "compute) + autofill + SatEngine PT1M idle-tick + "
                    "qwen3.8:4b GPU-resident (O-0942) + bili-reply CPU "
                    "hot-standby; GPU MODE=pause PSU-deferred (i2v "
                    "27/53 held per O-0925 sec3-3)")
hb["task"] = st["current_task"]
hb["sync"] = {"last_push_ts": now_iso,
              "note": "r932: closeout commit+push follows this write"}
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# verify epoch int (smoke F7 law)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# ---- round report append ----
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = ("| " + now_iso + " | r932 | bm-b [dept:research/strategy] | Salvage + "
        "integration round, judge-finalize disclosed in-flight (prior "
        "loop instance died at 25min runner kill mid-r932 with uncommitted "
        "patch + detached finalize -- salvage law r834 applied): "
        "(1) S0: origin +4 (bm-a r983/984) ff-absorbed; 18 stale shared "
        "regen faces discarded pre-stash ts-newer-wins (r930 law); "
        "marks-20261014.jsonl stash-pop conflict -> HEAD-identical "
        "resolve with fsck-verified ZERO unique-loss (stash theirs 10/10 "
        "lines contained in HEAD 11, r570 union satisfied by superset); "
        "PS pit second hit: unquoted stash@{0} in PS = hashtable mangle "
        "(pit-git CRT family -- quote stash refs in PS). "
        "(2) Salvage: dead instance's scripts/trial_labor_w19.py "
        "zero-variance guard patch (25+/6-: judge-finalize DSR "
        "ValueError zero-variance crash x2 forensics results/_r932bmb_jf."
        "err + judge_finalize_r932.err.log; weekly_grid 0-entry "
        "treatment arm = prereg sec.5.5 trade-gate branch; DSR undefined "
        "on constant returns, G1 keeps frozen refuse, G2 refuses on "
        "missing DSR, reform face excludes never-traded arm, fully "
        "disclosed) COMMITTED this round + detached judge-finalize PID "
        "17108 (launched 12:33:28) left running healthy (36+ CPU-min "
        "active, out/err logs buffered 0B). "
        "(3) S0.5: orders diff 0 unacked (88 files vs 213 acks); D-19 "
        "dual-delta consumed (dec 86187eff->d77f5fa1 ord "
        "348eaf34->83454e8f; new rows D-20261014-01..04: zero BigMoney "
        "dispatch, bigmoney mentions informational re HQ-FEEDBACK "
        "staleness since 10-11 = our domain face, no filler append "
        "honest); watermark ADVANCED read-back verified. "
        "(4) S1 smoke 49/49. (5) round-zero orphan probe py_faces=21 "
        "orphans=0. (6) SatEngine alive rc0 idle queue 0. "
        "(7) S6 quick legs: dualrun ZERO-DRIFT streak 17 (456 entries, "
        "MUST precede compute_audit law) + compute_audit FLAG "
        "supply_floor (pool_ready 0/3, structural serial-burn aftermath "
        "-- W19-JUDGE was last entry, claimed+burned; refill = next wave "
        "enrollment after W19 chain closes) + pywm insufficient_history "
        "local_batch_running=true (the finalize = legal work in flight, "
        "NOT idle) + update_daily/market_regime wrote + minute_feed +20 "
        "rows intraday (5 symbols) + astock/etf no-op fresh + rev_osc "
        "no-op idempotent + thermo DONE + dualarm DUALARM-2026-09-30 "
        "written + token delta 0 + attrition scan CLEAN (4 ledgers). "
        "(8) board: job_list empty + fleet tasks 0 open (claimed rows "
        "left to owners per collision law). "
        "(9) S7: loop/watchdog/claws verified + state round_no 931->932 "
        "+ heartbeat epoch int + commit/push follows. "
        "| 当前活: W19 judge-finalize burning (PID 17108, patched "
        "zero-variance guard, 1-core) + qwen3.8:4b GPU-resident (O-0942) "
        "| 最近实物: scripts/trial_labor_w19.py zero-variance guard "
        "salvage commit (12:xx) + S0 ff+4 + marks zero-loss resolve "
        "| 下个里程碑: judge-finalize landing verify + intake + product "
        "push <=10-14 14:00 (48h CEO clock at judge landing); S6 full "
        "chain 15:30; next wave enrollment post-W19 "
        "| watermark: GREEN (red=false; supply_floor structural "
        "pool-empty-behind-W19, NOT idle -- finalize burn in flight; "
        "next_pick empty) | orphan-faces=0 (probe 12:52: py_faces=21 "
        "orphans=0) | orders: 0 unacked (213 cumulative) | evidence: "
        "git ff 5facf09a9->50fa77623 + stash drop sha adb7abcb9 + smoke "
        "49/49 + dualrun streak 17 + attrition CLEAN + d19 watermark "
        "advance read-back | unacked_orders=0 | registry-zero-hit: no "
        "sweep/archive/delete actions this round | "
        "local-unreached-origin-commits: 0 at S0 (ff absorbed) -> "
        "closeout commit+push follows + self-proof | next-pointer r933: "
        "(a) judge-finalize landing verify (DUAL-IGNITION GUARD: never "
        "relaunch while alive; if exited read judge_finalize_r932b.err."
        "log) -> product face verify -> intake (s4) -> commit+push "
        "(48h clock) -> next wave enrollment; (b) S6 full chain 15:30 "
        "data window; (c) standing: GPU PSU-swap MODE=pause, unity POC, "
        "bili-reply CEO cookie+aid, MF panel bm-a lane | [r932 bm-b]\n"
        )
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("closeout writes done; epoch=", epoch)
