import json, io, time
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = "2026-10-13T23:37:12+08:00"
EPOCH = 1791905832

# --- heartbeat fleet/machines/bm-b.json ---
hp = ROOT + r"\fleet\machines\bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h["clock_read"] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["ts"] = NOW
h["last_seen"] = NOW
h["last_action_at"] = NOW
h["last_round_at"] = NOW
h["round"] = 918
h["round_no"] = 919
h["round_no_label"] = "r918"
h["free_ram_gb"] = 11.9
h["idle_ram_gb"] = 11.9
h["idle_ram_pct"] = 49.6
h["ram_free_gb"] = 11.9
h["ram_free_pct"] = 49.6
h["gpu_idle_vram_gb"] = 6.9
h["gpu_free_vram_gb"] = 6.9
h["gpu"] = {"util_pct": 9.0, "mem_used_mb": 1023.0, "power_w": 14.01,
            "face": "GPU idle 14W (MODE=pause PSU-deferred, i2v 27/53 held for PSU swap/CEO re-order)"}
h["last_action"] = ("r918: probe#4 + bridge-level diagnosis landed: editor session was MobTide -batchmode -quit "
                    "Douyin build instance (game-lane, AutoQuitter exits it) + MobTide project has NO MCP plugin "
                    "(manifest+Assets both absent) -> unconnected is mechanical two-factor, not transient; "
                    "report results/_r918bmb_unity_bridge_probe4.json; S6 core legs green (streak 51, smoke 49/49, "
                    "attrition CLEAN, token 0)")
h["did"] = ("r918: (1) S0 absorb daemon faces pre-rebase (d46b6b2a8, behind=0). (2) D-19 double delta probe: zero "
            "new orders/decisions (watermarks unchanged b137f331/91d9fad3). (3) S1 smoke 49/49. (4) unity bridge "
            "probe#4 DONE during live editor window: Tuanjie PID 23584 = MobTide -batchmode -quit BuildDouyin build "
            "batch (not interactive), no MCP bridge port in listener set, MobTide manifest.json + Assets both show "
            "NO MCP for Unity plugin -> root cause adjudicated mechanical (batchmode instance x plugin-absent), "
            "report results/_r918bmb_unity_bridge_probe4.json. (5) S6: pool_dualrun streak 51 ZERO-DRIFT, "
            "compute_audit flags pool_starvation+supply_floor = N2U3 double-gate known-blocked honest carry, "
            "py_watermark insufficient_history legal (astock refresh in-flight = the work), token_meter 0 today. "
            "(6) S7: attrition CLEAN, loop pin=2 no-op, watchdog alive, both claws reinstalled idempotent, inbox 0.")
h["latest_artifact"] = "results/_r918bmb_unity_bridge_probe4.json (probe#4 mechanical diagnosis, 23:36)"
h["current_task"] = ("r919: PSU-swap watch (i2v 27/53 160W-clause deferred) + N2U3 chain at batch-done (flip "
                     "double-gate, RAM leg OK 11.9GB) + S6 full chain at 10-14 15:30 data window + unity POC "
                     "next-step decision (plugin install project pick vs wait interactive window)")
h["task"] = h["current_task"]
h["next"] = ("r919: (a) GPU line: hold MODE=pause until PSU swap (750W gold ATX3.x pending) or CEO re-ignition "
             "order; (b) unity POC: next step needs project-pick decision for plugin install (do NOT touch MobTide "
             "while build batch running) or wait for interactive editor window on a plugin-installed project; "
             "(c) at batch-done: keepwarm.pause removal + N2U3 flip (batch-done + RAM>=4GB, RAM leg OK) -> autofill "
             "-> export-topk K=32 -> judged; (d) Speech-02 adjudication pending committee/CEO; Music3 install gated "
             "post-batch; game audio batch after gates; (e) S6 full chain next data window 10-14 15:30.")
h["note"] = ("r918: diagnosis round; product = unity bridge probe#4 mechanical adjudication (batchmode x "
             "plugin-absent two-factor); standing faces honest-carried")
h["now_active"] = ("bm-b CPU/bookkeeping lanes alive (loop parent, SatEngine ticking, astock full-universe refresh "
                   "in-flight); GPU idle 14W (MODE=pause PSU-deferred, i2v 27/53)")
h["next_milestone"] = ("honest: GPU line blocked on PSU swap/CEO re-order; unity POC blocked on interactive window "
                      "+ plugin-installed project; N2U3 chain resumes after i2v 53/53; next data window 2026-10-14 "
                      "15:30")
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = "r918 probe 23:29: py_faces=12 orphans=0 killed=[] (satengine faces + astock refresh = legal lanes)"
h["verdict"] = ("GREEN-with-flags: probe#4 root-cause adjudicated (mechanical, report landed); flags = GPU PSU-deferred "
                "+ N2U3 chain batch-gated + pool starvation = known-blocked supply face")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["green_idle"] = False
h["sync"] = {"last_push_ts": NOW,
             "note": "r918: absorb commit d46b6b2a8 pre-rebase; closeout commit+push follows this write"}
json.dump(h, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- state.json ---
sp = ROOT + r"\state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round"] = 918
s["round_no"] = 919
s["round_no_label"] = "r918"
s["clock_read"] = NOW
s["ts"] = NOW
s["updated"] = NOW
s["updated_at"] = NOW
s["last_round_at"] = NOW
s["last_round_ts"] = NOW
s["last_seen"] = NOW
s["last_action_at"] = NOW
s["last_action"] = ("r918: probe#4 mechanical diagnosis landed (results/_r918bmb_unity_bridge_probe4.json: "
                     "batchmode-build-instance x plugin-absent two-factor) + S6 core green + S7 all green")
s["did"] = h["did"]
s["latest_artifact"] = h["latest_artifact"]
s["current_task"] = h["current_task"]
s["task"] = h["task"]
s["next"] = h["next"]
s["note"] = h["note"]
s["now_active"] = h["now_active"]
s["next_milestone"] = h["next_milestone"]
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = h["orphan_face_note"]
s["verdict"] = h["verdict"]
s["sync"] = h["sync"]
json.dump(s, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- round report append ---
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
line = ("| " + NOW + " | r918 bm-b [dept:eng/fleet] | unity bridge probe#4 = mechanical diagnosis round (main deliverable) "
        "| watermark: GREEN (red=false; D-19 double delta zero-new b137f331/91d9fad3 unchanged) | orphan-faces=0 "
        "(probe 23:29: py_faces=12, satengine+astock legal) | currently-active: CPU/bookkeeping lanes (loop parent, "
        "SatEngine idle-tick, astock full-universe refresh in-flight); GPU idle 14W (MODE=pause PSU-deferred, i2v 27/53) "
        "| latest-artifact: results/_r918bmb_unity_bridge_probe4.json 23:36 (probe#4 done IN a live editor window: "
        "Tuanjie PID 23584 23:33 = MobTide -batchmode -quit BuildDouyin build batch, not interactive; no MCP port in "
        "listener set; MobTide manifest+Assets = NO MCP plugin -> unconnected = batchmode x plugin-absent two-factor "
        "mechanical, 4-probe mystery closed; POC next = plugin-install project pick (NOT MobTide mid-build) or "
        "interactive window) | S6: pool_dualrun streak 51 ZERO-DRIFT, compute_audit flags pool_starvation+supply_floor "
        "= N2U3 double-gate known-blocked honest carry, py_watermark insufficient_history legal local_batch, "
        "token 0 today | S7: attrition CLEAN, smoke 49/49, loop pin=2 no-op, watchdog alive, claws reinstalled, inbox 0 "
        "| evidence: results/_r918bmb_unity_bridge_probe4.json + results/_attrition_guard_scan.json + smoke 49/49 "
        "| next: r919 PSU-swap watch + N2U3 at batch-done + S6 full chain 10-14 15:30 + unity POC project-pick decision "
        "| unreached_origin_commits: 0 (S0 behind=0, closeout push follows)\n")
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)

# self-proof epoch int check
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
print("closeout write OK: heartbeat round_no=%d epoch=%d(int) | state round_no=%d | report line appended" % (
    h2["round_no"], h2["heartbeat_epoch_utc"], s["round_no"]))
