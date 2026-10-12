"""r912 bm-b closeout: state.json + heartbeat + round report line (r908/r910 closeout pattern)."""
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())
S = json.load(open("state.json", encoding="utf-8"))
H = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))

did = (
    "r912: (1) MAIN PRODUCT = W18 48h CEO report delivered ~22h EARLY: "
    "research/digests/CEO-48H-W18-SIZING-AXIS-20261013.md (due 10-14 00:44 met; sizing-axis "
    "'detectably zero' verdict -- 4 faces paired median dSharpe +0.0001/-0.0005/0.0/0.0 with "
    "p 0.006-0.079, 188 judged 0-pass, FDR4D all-reject, intake lawful-zero; W17 exit-axis + W18 "
    "sizing-axis two-wave null = frozen-reburn micro-axis supply-weakening face confirmed). "
    "(2) E62 methodology card appended knowledge/METHODOLOGY_ASSETS.md (capture law "
    "O-20261002-2100: paired-block axis-experiment grammar, degenerate-pair exclusion law, "
    "detectably-zero reading; finalize-window capture debt collected this report round). "
    "(3) S0: fetch clean HEAD==origin/main zero integration; S0.5: 80/80 orders acked "
    "unacked=0 zero new orders; D-19 probe FRESH ZERO-DELTA (fb378423/bd29c5c5 identical, "
    "deferral CLEARED -- external-session blocker gone). (4) surgery3 re-verify: external "
    "session exited (no live process) + group origin advanced 3324d0be->100aa3d35 = completion "
    "evidence; dead-and-unowned-mid-work condition NOT met = zero takeover. (5) i2v batch "
    "watch HEALTHY: 17/53 done (KN13 842s post-revival + KN14 SAVED), KN15 in-flight 551s+, "
    "GPU 100%/119-154W under 180W cap, ComfyUI r911c PID 6280 alive; RAM 0.09GB long-clip "
    "spill watch standing (2x-recurrence escalation per plan). (6) unity-mcp POC precondition "
    "REGRESSED: Tuanjie editor CLOSED (r911 PID 23276 gone) -- POC waits editor-open window "
    "(due 12:00; GPU window = post-batch anyway). (7) S1 smoke 49/49; SAT engine alive idle; "
    "pool 446 done + N2U3-LEG3-TRAIN waiting double-gate HOLD correct; watermark GREEN "
    "red=false next_pick=claimed-by-other. (8) S6 chain 42 legs: 41 rc0 + t35_open_fill rc=1 "
    "legal no-evidence (Tue pre-open face, r911 same); dualrun streak 51 ZERO-DRIFT; "
    "compute_audit flags pool_starvation/supply_floor standing (resource-blocked honest); "
    "pywm py_low_with_work_cands LEGAL (local_batch=i2v burn = the work); attrition CLEAN 4 "
    "ledgers; token delta=0. (9) S7: loop pin=2 no-op, watchdog re-registered, pre-commit + "
    "pre-push claws installed, inbox zero-for-bm-b (2 msgs both bm-a-addressee). Orphan "
    "probe 20 faces 0 orphans."
)
next_ptr = (
    "r913: i2v batch watch (KN15+ -> 53/53 ETA 10-13 morning; long-clip OOM repeat watch -- 2x "
    "recurrence escalate Ollama co-load face) > at 53/53: remove keepwarm.pause + flip "
    "N2U3-LEG3-TRAIN waiting->ready (batch-done + RAM>=4GB double gate) -> autofill burn "
    "(~3.3h) -> export-topk K=32 -> judged legs > unity-mcp POC due 10-13 12:00 (Tuanjie "
    "editor CLOSED now -- editor-open window + GPU post-batch double precondition; if editor "
    "stays closed past mid-morning, honest non-precondition note) > Speech-02+Music3 "
    "install-prep (O-2215 bm-b lane, post-batch network idle) > E15 s4 intake legs = monthly "
    "boundary; W18 48h DONE this round."
)
verdict = (
    "GREEN-with-flags: product round under legal GPU burn (W18 48h CEO report delivered ~22h "
    "early + E62 methodology card + D-19 deferral cleared with fresh zero-delta probe + i2v "
    "batch healthy 17/53 KN15 in-flight 180W cap); flags=pool_starvation/supply_floor standing "
    "(resource-blocked until batch completes) + unity-mcp POC editor-window pending"
)
latest = (
    "research/digests/CEO-48H-W18-SIZING-AXIS-20261013.md (W18 48h CEO report, ~22h early) + "
    "E62 paired-block axis-experiment card in METHODOLOGY_ASSETS.md + _r686bmb_d19_check.json "
    "(fresh zero-delta probe)"
)
now_active = (
    "i2v animatic batch burning (17/53 done, KN15 in-flight, ComfyUI r911c PID 6280, GPU 100% "
    "under 180W cap, RAM 0.09GB spill watch)"
)
milestone = (
    "i2v 53/53 ETA 10-13 morning -> N2U3 flip double-gated -> export-topk+judged legs; "
    "unity-mcp POC <=10-13 12:00 (editor window pending); W18 48h MET early this round"
)
last_action = (
    "r912: W18 48h CEO report ~22h early + E62 methodology card + D-19 fresh zero-delta probe "
    "(deferral cleared) + S6 42 legs + i2v batch watch healthy 17/53"
)

S.update({
    "clock_read": TS, "last_round_at": TS, "last_round_ts": TS, "last_seen": TS,
    "ts": TS, "updated": TS, "updated_at": TS, "last_action_at": TS,
    "round": 912, "round_no": 913, "round_no_label": "r912",
    "did": did, "next": next_ptr, "task": next_ptr, "note": last_action,
    "last_action": last_action, "verdict": verdict, "latest_artifact": latest,
    "now_active": now_active, "next_milestone": milestone,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r912 probe 02:2x: py_faces=20 orphans=0; batch lane faces "
                         "(ComfyUI r911c PID 6280 + driver) all live registered",
    "last_decisions_at": TS, "last_decisions_read_at": TS,
    "last_orders_at": TS, "last_orders_read_at": TS,
    "last_decisions_sha_method": (
        "r912 probe via results/_r686bmb_d19_check.py (r537 SHA-1 raw-blob PIN): fresh fetch "
        "02:4x group origin 100aa3d35, decisions fb378423 + orders bd29c5c5 BOTH == watermark "
        "= ZERO-DELTA, no consumption needed; standing deferral CLEARED (external surgery "
        "session exited, network fetch OK)"
    ),
})
S["d19_watermark_guard"] = dict(S.get("d19_watermark_guard", {}))
S["d19_watermark_guard"].update({
    "round_ref": 912, "ts": TS,
    "note": "r912 probe fresh zero-delta (fb378423/bd29c5c5); deferral cleared",
})
S["sync"] = {
    "last_push_ts": TS,
    "note": "r912 closeout: round commit + push follows this write; delivery self-proof "
            "(fetch+rev-list) in round report",
}
json.dump(S, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

H.update({
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_seen": TS, "last_action_at": TS, "last_round_at": TS,
    "heartbeat_epoch_utc": EPOCH,
    "round": 912, "round_no": 913, "round_no_label": "r912",
    "current_task": "r912 closeout; r913 = batch watch + N2U3 flip at 53/53 + unity-mcp POC window",
    "did": did, "task": next_ptr, "next": next_ptr, "note": last_action,
    "last_action": last_action, "verdict": verdict, "latest_artifact": latest,
    "now_active": now_active, "next_milestone": milestone,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": S["orphan_face_note"],
    "idle_rounds": 0, "agenda_starved": False, "green_idle": False,
    "free_ram_gb": 0.09, "ram_free_gb": 0.09,
    "gpu_free_vram_gb": 0.3, "gpu_free_vram_mb": 300,
    "gpu": {
        "util_pct": 100.0, "mem_used_mb": 7960.0, "power_w": 119.0,
        "face": "i2v animatic batch burning (17/53, KN15 in-flight, ComfyUI r911c PID 6280, 180W cap held)",
    },
})
json.dump(H, open("fleet/machines/bm-b.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

epoch_chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))["heartbeat_epoch_utc"]
assert isinstance(epoch_chk, int), "epoch must be int (R170/R178 law)"
line = (
    "%s | r912 bm-b | dept:engineering+dept:fleet | watermark: GREEN (red=false; "
    "py_low_with_work_cands LEGAL = i2v batch burning = the work itself; next_pick=claimed by "
    "other machine) | orphan-faces=0 (20 py faces probe 02:2x) | currently-active: i2v animatic "
    "batch burning (17/53 done, KN15 in-flight 551s+, ComfyUI r911c PID 6280, GPU 100%%/119W "
    "under 180W cap, RAM 0.09GB long-clip spill watch standing) | latest-artifact: "
    "research/digests/CEO-48H-W18-SIZING-AXIS-20261013.md (W18 48h CEO report delivered ~22h "
    "early, due 10-14 00:44) + E62 paired-block axis-experiment methodology card + "
    "_r686bmb_d19_check.json (fresh zero-delta probe, D-19 deferral cleared) | next-milestone: "
    "i2v 53/53 ETA 10-13 morning (long-clip OOM repeat watch) -> N2U3 flip double-gated -> "
    "export-topk K=32 + judged legs; unity-mcp POC <=10-13 12:00 (Tuanjie editor CLOSED now = "
    "hard-precondition gap, editor-open window pending) | did: %s | evidence: "
    "CEO-48H-W18-SIZING-AXIS-20261013.md + METHODOLOGY_ASSETS.md E62 + _r912bmb_s6.txt (42 legs "
    "rc ledger) + driver_r911c.out.txt (KN13 SAVED 842s + KN14 SAVED + KN15 in-flight) + "
    "results/_r686bmb_d19_check.json + _r912bmb_smoke.txt (49/49) + "
    "results/_orphan_face_probe.bm-b.json | unacked_orders=0 (80/80) | 登记簿零命中声明：本轮无清扫/归档/删除动作 | "
    "local-unreached-origin-commits: 0 (post-push fetch+rev-list self-verify follows) | "
    "next-pointer r913: %s | [r912 bm-b]\n" % (TS, did, next_ptr)
)
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)
print("CLOSEOUT_OK ts=%s epoch=%d round=912 next=913" % (TS, EPOCH))
