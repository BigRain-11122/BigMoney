"""r913 bm-b closeout: state.json + heartbeat + round report line (r912 closeout pattern)."""
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())
S = json.load(open("state.json", encoding="utf-8"))
H = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))

did = (
    "r913: (1) MAIN PRODUCT = research/SPEECH02_MUSIC3_LICENSE_PRECHECK.md (Speech-02+Music3 install-"
    "batch PRECHECK board v1, O-20261012-1505 ②③ + O-20261012-2215 ③ license-first law): Music3 "
    "license check PASS (MiniMax-Music3 COMMUNITY LICENSE verbatim read -- free "
    "use/copy/distribute/sublicense incl. commercial; NO region limits [research claim verified "
    "live]; $20M/yr revenue authorization line far above our scale; binding = prominent "
    "'MiniMax-Music3' UI credit + AUP incl. machine-generated disclosure; upstream blood "
    "Qwen3-8B Apache-2.0 + stable-audio-tools MIT + descript-audio-codec MIT all permissive) + "
    "8G recipe pinned FILE-LEVEL (Comfy-Org/MiniMax-Music-3: dit_int8_convrot + "
    "text_encoder_pruned_int8_convrot + dav vae -- same int8_convrot tech family as our live H3 "
    "batch line); Speech-02 SUPPLY check FAIL (exhaustive 3-platform probe ALL MISS: HF "
    "MiniMax-Audio org ZERO models + MiniMaxAI 21-repo org listing has NO TTS + site search zero "
    "official hits; ModelScope 3 namespaces x 8 candidates ALL 404 + dolphin search 0 hits; "
    "GitHub 37 repos -- audio-tools = text-preproc utilities NOT weights) -> install-verification "
    "batch as designed CANNOT start, POOL-0002 stays gated, daily narration stays on cloud "
    "TJGenerators (legal: TTS not in LEDGER cloud-ban list), 3-option adjudication filed "
    "(A=HQ retrace 10-09 evidence source / B=substitute open TTS needs new decision per "
    "no-direct-replacement law / C=on-prem commercial). (2) i2v batch watch HEALTHY: 18/53 done "
    "(KN15 SAVED), KN17 in-flight 481s+, driver PID 2848 alive, GPU 100%/90W under 180W cap, RAM "
    "RECOVERED 0.09->2.62GB (long-clip spill window passed). (3) unity-mcp POC precondition "
    "RE-CHECKED: tuanjie PID 2208 = Cowork HUB (tray, empty title) NOT the editor; unity-mcp "
    "probe 'No Unity Editor instances found' = editor still CLOSED; due 12:00 with mid-morning "
    "re-check window per plan. (4) S0 fetch clean HEAD==origin/main (behind0/ahead0); S0.5 "
    "80/80 orders acked unacked=0; D-19 pinned probe FRESH ZERO-DELTA (fb378423/bd29c5c5 == "
    "watermark, group origin 100aa3d35 unchanged; inline PS-pipe hash attempt mangled = pinned "
    "probe is the only reliable face). (5) S1 smoke 49/49; SAT engine alive idle; pool "
    "N2U3-LEG3-TRAIN waiting double-gate HOLD correct; watermark GREEN red=false. (6) S6 chain 41 "
    "legs (r911 verbatim pattern): 40 rc0 + t35_open_fill rc=1 legal Tue pre-open no-evidence "
    "(r911/r912 same); t35_paper_export face bm-a heartbeat stale 53h -> LEGAL stale-takeover "
    "derive by bm-b (O-2100 s2.4); chain split by tool 5min-silent-kill at leg 37 -> continuation "
    "face all rc0 (pit: silent long chain must print progress). (7) S7: loop pin=2 no-op, watchdog "
    "re-registered, pre-commit+pre-push claws installed, attrition CLEAN 4 ledgers, inbox 2 msgs "
    "both bm-a-addressee zero-for-bm-b. Orphan probe 11 py_faces 1 orphan = i2v driver "
    "sleep-window FALSE-POSITIVE NOT killed (CEO batch face, r910 precedent); 2 live detached "
    "jobs legal (astock refresh + backfill_ext_slots)."
)
next_ptr = (
    "r914: i2v batch watch (KN17+ -> 53/53 ETA 10-13 morning; long-clip OOM repeat watch) > at "
    "53/53: remove keepwarm.pause + flip N2U3-LEG3-TRAIN waiting->ready (batch-done + RAM>=4GB "
    "double gate) -> autofill burn (~3.3h) -> export-topk K=32 -> judged legs > Music3 install "
    "window (license PASS r913: int8 three-file download ~12-14GB + ComfyUI smoke + comparison "
    "board v2 vs cloud Music3) > unity-mcp POC due 10-13 12:00 (Tuanjie Hub running but editor "
    "CLOSED -- re-check editor-open window, honest non-precondition note if past mid-morning) > "
    "Speech-02 3-option adjudication awaiting committee/CEO (board filed, POOL-0002 frozen) > "
    "E15 s4 intake legs = monthly boundary."
)
verdict = (
    "GREEN-with-flags: product round under legal GPU burn (Speech-02+Music3 precheck board "
    "landed: Music3 license PASS + 8G int8 recipe pinned, Speech-02 supply FAIL = honest "
    "adjudication filed; i2v batch healthy 18/53 KN17 in-flight 90W under cap, RAM recovered "
    "2.62GB); flags=pool_starvation/supply_floor standing (resource-blocked until batch "
    "completes) + unity-mcp POC editor-window still pending + Speech-02 route blocked pending "
    "committee/CEO pick of A/B/C"
)
latest = (
    "research/SPEECH02_MUSIC3_LICENSE_PRECHECK.md (install-batch precheck board: Music3 "
    "license PASS + file-level 8G int8 recipe; Speech-02 supply FAIL + 3-option adjudication) "
    "+ probe evidence family results/_r913bmb_* (gh repos json, ms probes, s6 log, d19 recheck)"
)
now_active = (
    "i2v animatic batch burning (18/53 done, KN17 in-flight, ComfyUI r911c PID 6280 + driver "
    "PID 2848, GPU 100%/90W under 180W cap, RAM 2.62GB free spill window passed)"
)
milestone = (
    "i2v 53/53 ETA 10-13 morning -> N2U3 flip double-gated -> export-topk+judged legs; Music3 "
    "install window ready post-batch (license PASS); unity-mcp POC <=10-13 12:00 (editor window "
    "pending); Speech-02 route adjudication filed"
)
last_action = (
    "r913: Speech-02+Music3 precheck board (Music3 PASS/Speech-02 supply FAIL) + i2v watch "
    "18/53 + S6 41 legs + D-19 zero-delta + S7 self-heal green"
)

S.update({
    "clock_read": TS, "last_round_at": TS, "last_round_ts": TS, "last_seen": TS,
    "ts": TS, "updated": TS, "updated_at": TS, "last_action_at": TS,
    "round": 913, "round_no": 914, "round_no_label": "r913",
    "did": did, "next": next_ptr, "task": next_ptr, "note": last_action,
    "last_action": last_action, "verdict": verdict, "latest_artifact": latest,
    "now_active": now_active, "next_milestone": milestone,
    "orphan_face": 1, "orphan_faces": 1,
    "orphan_face_note": "r913 probe 03:0x: py_faces=11 orphans=1 = i2v driver "
                         "(results/_r897bmb_i2v/h3_i2v_album.py --lane bmb, PID 2848) "
                         "sleep-window FALSE-POSITIVE between ComfyUI polls, NOT killed (CEO "
                         "batch face, r910 precedent); driver alive writing "
                         "driver_r911c.out.txt + KN17 in-flight proof",
    "last_decisions_at": TS, "last_decisions_read_at": TS,
    "last_orders_at": TS, "last_orders_read_at": TS,
    "last_decisions_sha_method": (
        "r913 pinned probe re-run via results/_r686bmb_d19_check.py: fresh fetch group origin "
        "100aa3d35 unchanged, decisions fb378423 + orders bd29c5c5 BOTH == watermark = "
        "ZERO-DELTA no consumption; inline PS-pipe hash attempt (f7659b38/454f7712) was encoding-"
        "mangled garbage = discarded, pinned python probe is the only reliable face (PS text-pipe "
        "hash pit, logged)"
    ),
})
S["d19_watermark_guard"] = dict(S.get("d19_watermark_guard", {}))
S["d19_watermark_guard"].update({
    "round_ref": 913, "ts": TS,
    "note": "r913 pinned probe zero-delta (fb378423/bd29c5c5 unchanged)",
})
S["sync"] = {
    "last_push_ts": TS,
    "note": "r913 closeout: round commit + push follows this write; delivery self-proof "
            "(fetch+rev-list) in round report",
}
json.dump(S, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

H.update({
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_seen": TS, "last_action_at": TS, "last_round_at": TS,
    "heartbeat_epoch_utc": EPOCH,
    "round": 913, "round_no": 914, "round_no_label": "r913",
    "current_task": "r913 closeout; r914 = batch watch + N2U3 flip at 53/53 + Music3 install window + unity-mcp editor watch",
    "did": did, "task": next_ptr, "next": next_ptr, "note": last_action,
    "last_action": last_action, "verdict": verdict, "latest_artifact": latest,
    "now_active": now_active, "next_milestone": milestone,
    "orphan_face": 1, "orphan_faces": 1,
    "orphan_face_note": S["orphan_face_note"],
    "idle_rounds": 0, "agenda_starved": False, "green_idle": False,
    "free_ram_gb": 2.62, "ram_free_gb": 2.62,
    "gpu_free_vram_gb": 0.4, "gpu_free_vram_mb": 400,
    "gpu": {
        "util_pct": 100.0, "mem_used_mb": 7953.0, "power_w": 90.4,
        "face": "i2v animatic batch burning (18/53, KN17 in-flight, ComfyUI r911c PID 6280 + driver PID 2848, 180W cap held, 90W draw)",
    },
})
json.dump(H, open("fleet/machines/bm-b.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

epoch_chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))["heartbeat_epoch_utc"]
assert isinstance(epoch_chk, int), "epoch must be int (R170/R178 law)"
line = (
    "%s | r913 bm-b | dept:engineering+dept:fleet | watermark: GREEN (red=false; py_low_with_work"
    "_cands LEGAL = i2v batch burning = the work itself; next_pick=claimed by other machine) | "
    "orphan-faces=1 (i2v driver sleep-window FALSE-POSITIVE NOT killed, CEO batch face, r910 "
    "precedent; probe 11 py_faces) | currently-active: i2v animatic batch burning (18/53 done, "
    "KN17 in-flight 481s+, ComfyUI r911c PID 6280 + driver PID 2848, GPU 100%%/90W under 180W "
    "cap, RAM recovered 0.09->2.62GB) | latest-artifact: research/SPEECH02_MUSIC3_LICENSE_PRE"
    "CHECK.md (install-batch precheck board v1: Music3 license PASS with community-license "
    "verbatim read [no region limits, $20M line far above scale, binding credit+AUP terms] + "
    "file-level 8G int8_convrot recipe [Comfy-Org/MiniMax-Music-3]; Speech-02 SUPPLY FAIL "
    "3-platform exhaustive probe -- install batch as designed cannot start, POOL-0002 frozen, "
    "3-option adjudication filed) | next-milestone: i2v 53/53 ETA 10-13 morning -> N2U3 flip "
    "double-gated -> export-topk+judged; Music3 install window post-batch; unity-mcp POC "
    "<=10-13 12:00 (editor still CLOSED -- Tuanjie Hub PID 2208 running but is HUB not editor, "
    "unity-mcp probe 'No instances found') | did: %s | evidence: SPEECH02_MUSIC3_LICENSE_PRE"
    "CHECK.md + _r913bmb_gh_minimax_repos.json + _r913bmb_ms_probe.json/_r913bmb_ms_search.json "
    "+ _r913bmb_s6_log.txt (41 legs: 40 rc0 + t35 legal rc1 + continuation face after tool "
    "5min-silent-kill) + _r686bmb_d19_check.json (pinned zero-delta) + driver_r911c.out.txt "
    "(KN15 SAVED + KN17 in-flight) + _orphan_face_probe.bm-b.json + _attrition_guard_scan.json "
    "| unacked_orders=0 (80/80) | registry-zero-hit: no sweep/archive/delete actions this round "
    "| local-unreached-origin-commits: 0 (post-push fetch+rev-list self-verify follows) | "
    "next-pointer r914: %s | [r913 bm-b]\n" % (TS, did, next_ptr)
)
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)
print("CLOSEOUT_OK ts=%s epoch=%d round=913 next=914" % (TS, EPOCH))
