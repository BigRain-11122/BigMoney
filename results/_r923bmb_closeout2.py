# -*- coding: utf-8 -*-
# r923-continuation-2 closeout: heartbeat update + round report append
import json, io, os, time

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = "2026-10-14T05:55:02+08:00"
EPOCH = 1791928503  # int per R170/R178 law (verified isinstance int at write)

hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with io.open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)

hb["clock_read"] = NOW
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
hb["last_seen"] = NOW
hb["last_round_at"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["round"] = 923
hb["round_no"] = 924
hb["round_no_label"] = "r923"
hb["current_task"] = ("r924: verify JUDGED-2026-10-09.json landed (judge PID 8908 detached) "
                      "-> judged ledger 32 check -> supply refill (pool floor 3 breach) "
                      "-> S6 full chain 10-14 15:30 data window")
hb["task"] = ("r924: verify JUDGED landed + ledger 32; supply refill next prereg wave; "
              "S6 full chain 15:30; standing: PSU-swap GPU hold, unity POC editor-window, "
              "Speech-02/Music3 gates, bili-reply CEO physical items, MF bm-a lane crash-blocked")
hb["did"] = ("r923-continuation-2 takeover: (1) r923 chain (multi-session, HEAD d6b569d6f 05:34) "
             "died 05:36 with judge leg triple-broken (judge_burn_r923.log NameError ROOT_RESULTS@L1924); "
             "(2) PRODUCT: adopted dead-session WIP repair (sg.RESULTS_DIR + d6_fn injection per job#1 "
             "design-lock + D6 registered-members merge per frozen D6 def stricter-not-looser), selftest "
             "50/50 rc0 live re-verified, commit bea04fc64; (3) judge leg IGNITED detached pythonw PID 8908 "
             "05:48 (survives session death) -> JUDGED-2026-10-09.json in flight at closeout; "
             "(4) S0 absorb c697f5eeb + rebase onto bm-c r984 ba3403128; (5) order O-20261014-0312-bm-c "
             "acked (bm-c-scoped, zero bm-b action); D-19 dual-delta zero; (6) S6 core: dualrun ZERO-DRIFT "
             "streak 4, audit FLAG supply_floor (LEG3 done both faces, over-burn gate closed), pywm LEGAL, "
             "token 0; (7) S7: smoke 49/49, loop pin=2, watchdog re-registered, claws installed, attrition "
             "CLEAN, idle --worked 0, inbox 1 msg To:bm-a left for addressee.")
hb["last_action"] = ("r923: judge-leg NameError repair adopted (bea04fc64, selftest 50/50) + FIRST judged "
                     "N2U3 battery ignited detached PID 8908 -> JUDGED-2026-10-09.json + ledger 32 "
                     "(in flight at closeout)")
hb["last_action_at"] = NOW
hb["latest_artifact"] = ("scripts/alphagen_rl_p1.py judge-leg repair (bea04fc64) + judge battery in flight "
                         "(PID 8908, log results/alphagen_rl_p1/judge_burn_r923c.log)")
hb["next"] = ("r924: (a) verify JUDGED-2026-10-09.json + ledger 32 -> aggregates report = first judged N2U3 "
             "channel-1 evidence; (b) supply refill next prereg wave (TRIAL_LABOR_LAW standing line); "
             "(c) S6 full chain 10-14 15:30; (d) standing: GPU PSU-swap MODE=pause i2v 27/53, unity POC "
             "editor window, Speech-02 adjudication, Music3 post-batch, bili-reply CEO cookie+aid, "
             "MF panel bm-a lane code-crash blocked")
hb["next_milestone"] = ("JUDGED-2026-10-09.json + ledger 32 landing (judge PID 8908 in flight) = first judged "
                        "N2U3 evidence; supply refill next wave; S6 full chain 10-14 15:30")
hb["note"] = ("r923-continuation-2: dead-session-takeover round; judge leg triple-break repaired+verified+"
              "committed and battery ignited detached the same round")
hb["now_active"] = ("judge battery PID 8908 detached pythonw burning (NEVER kill = legal lane per r922 pit "
                    "law); SatEngine ticking; GPU idle MODE=pause PSU-deferred; Cowork hub+app running")
hb["verdict"] = ("GREEN: r923 chain closed by takeover -- judge-leg triple-break repaired (selftest 50/50) + "
                 "FIRST judged N2U3 battery in flight detached; flags = GPU PSU-deferred (MODE=pause) + "
                 "supply_floor (pool 0 ready < 3, refill due next round) + unity POC editor-window-gated + "
                 "Speech-02/Music3 standing gates")
hb["sync"] = {"last_push_ts": NOW,
              "note": "r923-continuation-2: closeout commit+push follows this write; delivery self-proof via fetch+rev-list"}
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["free_ram_gb"] = 12.7
hb["ram_free_gb"] = 12.7
hb["ram_free_pct"] = 52.9
hb["idle_ram_gb"] = 12.7
hb["idle_ram_pct"] = 52.9
hb["gpu_free_vram_gb"] = 7.4
hb["gpu_free_vram_mb"] = 7385
hb["gpu_idle_vram_gb"] = 7.4
hb["gpu"] = {"util_pct": 2.0, "power_w": 8.9,
             "face": "GPU idle (MODE=pause PSU-deferred, i2v 27/53 held for PSU swap/CEO re-order); "
                     "judge battery = pure CPU face"}
hb["green_idle"] = False
hb["orphan_face"] = 0
hb["orphan_face_note"] = ("r923 probe 05:43: py_faces=14 orphans=0 killed=[]; judge PID 8908 (05:48 ignition) "
                          "= legal lane, parent session may die first -- successors MUST NOT kill (r922 pit law)")
hb["orphan_faces"] = 0

# orders ack: add the one unacked order
ack = hb.setdefault("orders_ack", [])
new_order = "O-20261014-0312-bm-c.md"
if new_order not in ack:
    ack.append(new_order)
hb["orders_ack_count"] = len(ack)
hb.setdefault("orders_ack_notes", {})[new_order] = (
    "r923-continuation-2 bm-b receipt: bm-c-scoped heartbeat burn-window rhythm order (PT-20261014-01); "
    "receipt already filed by bm-c r978-continuation in-order; bm-b zero mechanism action (ack-only); "
    "bm-b own face: pulse cadence honored -- this very heartbeat written mid-round at 05:55, "
    "session start 05:42 = 13min gap << 2h law")

with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# round report append
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = ("| 2026-10-14T05:55:02+08:00 | r923 bm-b [dept:eng/fleet] | dead-session-takeover closeout: "
        "judge-leg NameError repair adopted+verified (selftest 50/50, commit bea04fc64) + FIRST judged N2U3 "
        "battery IGNITED detached PID 8908 (JUDGED-2026-10-09.json in flight at closeout) | watermark: "
        "GREEN (red=false 05:50; D-19 dual-delta zero b137f331/348eaf34 unchanged) | orphan-faces=0 "
        "(probe 05:43: py_faces=14 orphans=0; judge PID 8908 = legal lane in flight, successors MUST NOT "
        "kill per r922 pit law) | orders: O-20261014-0312-bm-c acked 208->209 (bm-c-scoped heartbeat "
        "rhythm, receipt by bm-c in-order, zero bm-b mechanism action; bm-b pulse face honored = this "
        "heartbeat written mid-round 05:55 vs session start 05:42) | did: (1) takeover forensics: r923 "
        "chain = multi-session relay (salvage 3702e297e -> postburn P0 d6b569d6f 05:34:45 'judge leg "
        "ignited' -> died 05:36:55 with uncommitted estate); judge_burn_r923.log = NameError ROOT_RESULTS "
        "@L1924 = triple-broken judge leg (undefined const + missing d6_fn arg + unimported _d6_corr_cell "
        "in core); (2) WIP repair adopted: sg.RESULTS_DIR canonical + d6_fn injection per job#1 "
        "design-lock + D6 gate corr-checks registered members merged with same-batch per frozen D6 "
        "definition (stricter-not-looser), selftest 50/50 rc0 re-verified live, commit bea04fc64; "
        "(3) judge leg ignited detached pythonw PID 8908 05:48 (README zheng-fa: survives session death; "
        "pre-battery stages re-proven live: freeze gates + panel gate ready + G-ANCHOR-FACE assert + "
        "member_rets REG6 build all passed, CPU ~285s+ at closeout); (4) S0: absorb c697f5eeb + rebase "
        "onto bm-c r984 ba3403128 (0/0 clean, no file overlap); (5) pool truth: N2U3-LEG3-TRAIN = done "
        "BOTH faces (over-burn gate closed; autofill 05:50 tick = pool_empty_or_busy; compute_audit "
        "ready=0; py_watermark pool_ready_ids display discrepancy noted = non-operative stale face); "
        "(6) S6 core: dualrun ZERO-DRIFT 446 entries streak 4, compute_audit FLAG supply_floor (ready "
        "0<3 = N2U3-tail known-blocked honest carry, refill due r924), pywm insufficient_history LEGAL "
        "(local_batch=judge is the work), token delta 0; (7) S7: smoke 49/49, SatEngine alive, loop "
        "pin=2 no-op (first fire 06:02), watchdog re-registered (first fire 05:55), both claws installed "
        "idempotent, attrition CLEAN (1 healed historical shrink), idle_trigger --worked rounds=0, "
        "inbox 1 unread MSG-20261014-0512 To:bm-a (MF collector code-level crash loop, code-not-network "
        "diagnosis) = left for addressee per R31 zero-touch, bm-b zero action | evidence: commit "
        "bea04fc64 + selftest 50/50 rc0 + judge_burn_r923c.log PID 8908 + pool faces readback + "
        "results/_attrition_guard_scan.json + smoke 49/49 + results/_r686bmb_d19_check.json | "
        "unacked_orders=0 (209/209) | registry-zero-hit: no sweep/archive/delete actions this round | "
        "local-unreached-origin-commits: round-start 1 (bm-c r984 absorbed via rebase) -> closeout "
        "commit+push follows + self-proof | next-pointer r924: verify JUDGED-2026-10-09.json landed "
        "(PID 8908) -> judged ledger 32 + aggregates (n_g1/n_reg/n_d6_refused) = first judged N2U3 "
        "channel-1 evidence delivery -> supply refill next prereg wave (pool floor 3 breach, "
        "TRIAL_LABOR_LAW standing line: judged batch consumed = next candidate wave due) > S6 full "
        "chain 10-14 15:30 data window (new-bar legs re-arm) > standing: GPU line PSU-swap (MODE=pause "
        "holds, i2v 27/53), unity POC first interactive editor window (Cowork running = R2 live), "
        "Speech-02 committee/CEO, Music3 post-batch, bili-reply CEO cookie+aid, MF panel bm-a lane "
        "code-crash blocked (MSG-0512) | [r923 bm-b]\n")
with io.open(rr_path, "a", encoding="utf-8") as f:
    f.write(line)

# self-proof: heartbeat epoch is int
with io.open(hb_path, encoding="utf-8") as f:
    check = json.load(f)
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be int"
print("hb_ok round=923 epoch_int=%d acks=%d" % (check["heartbeat_epoch_utc"], check["orders_ack_count"]))
print("rr_appended bytes=%d" % len(line.encode("utf-8")))
