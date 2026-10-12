# -*- coding: utf-8 -*-
# r911 bm-b closeout: state.json + heartbeat + ledger line (ASCII-safe ops, utf-8 files)
import ctypes, json, time

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def ram_free_gb():
    class MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
    m = MEM()
    m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 2**30, 2)


DID = ("r911: (1) S0 FIRST MISSION DONE: fetch + 6-face rebase resolver integration (machine-health/attrition/compute_audit/"
       "regime/token_usage/update_status -- 5 scalar newer-wins OURS + compute_audit history union 67->65) + push main "
       "DELIVERED 2e0c884a2 (ls-remote self-verified, unreached=0). (2) S0.5: 79/79 orders acked, unacked=0, zero new orders; "
       "D-19 re-probe deferred standing (group repo external-session in flight + r908 probe 00:27 fresh zero-delta). (3) S1 "
       "smoke 49/49. (4) MAIN PRODUCT = i2v batch OOM death root-caused + REVIVED: KN13 len=226 long-clip render window + "
       "EngineTick on-demand qwen3.8:4b co-load (3.7GB) vs ComfyUI 7.5GB -> WDDM spill commit 25.3GB > RAM 24GB -> page "
       "thrash (2-4min/clip degraded to 60min+) -> ComfyUI OOM death @02:0x (GPU 1%/9W, driver 2148 stale-polling, progress "
       "frozen at 15/53); revival = ollama stop qwen (VRAM 3927->215MiB) + kill stale driver + ComfyUI r911c (PID 6280, :8188 "
       "ready) + driver r911c SKIP resume (15/53 preserved verbatim) -> KN13 re-SUBMITTED + GPU 100% back; root-cause pit "
       "direct-write pit-machine.md 1367B sha16=7754f356fa88de12 (r666/r903 precedent, receipt _r911bmb_pit_append.json). "
       "(5) E15 48h CEO report DELIVERED 9h EARLY: research/digests/CEO-48H-E15-EMOTION-REEVAL-20261013.md (due 11:2x met; "
       "verdict 2/4 pass W3-27009/W2-23057, 2 intra-batch cluster rejects, g_repro 4/4; s4 intake = monthly-boundary leg). "
       "(6) S6 chain 41 legs: 40 rc0 + t35_open_fill_verify rc=1 legal weekend no-evidence face (10-12 Sat); dualrun "
       "ZERO-DRIFT streak 51; attrition guard CLEAN 4 ledgers. (7) S3 faces: SatEngine alive idle; watermark green "
       "next_pick=claimed-by-other; pool N2U3-LEG3-TRAIN waiting double-gate HOLD (batch not done). (8) Orphan probe 17 "
       "faces 0 orphans. (9) Tuanjie editor OPEN (PID 23276 2022.3.62t15) = unity-mcp POC hard-precondition opportunity noted.")

NEXT = ("r912: i2v batch watch (KN13 226-frame long clip in render on fresh ComfyUI r911c; long-clip OOM repeat watch -- if "
        "death recurs 2x escalate Ollama co-load face to O-order/machine-state decision, single machine must not touch "
        "EngineTick) > at 53/53: remove keepwarm.pause + flip N2U3-LEG3-TRAIN waiting->ready (batch-done + RAM>=4GB double "
        "gate) -> autofill burn (~3.3h) -> export-topk K=32 -> judged legs > unity-mcp POC due 10-13 12:00 (Tuanjie editor "
        "NOW OPEN -- verify project binding in POC window; GPU window = post-batch) > W18 48h CEO report due 10-14 00:44 > "
        "Speech-02+Music3 install-prep (O-2215 bm-b lane, post-batch network idle) > surgery3 completion re-verify (external "
        "session; takeover only if dead-and-unowned next round) > E15 s4 intake legs = monthly boundary.")

VERDICT = ("GREEN-with-flags: watch+revival round under legal GPU burn (i2v batch 15/53 done + KN13 226-frame long clip "
           "re-in-flight on fresh ComfyUI r911c, 180W cap); batch OOM root-caused (qwen on-demand co-load + long clip) + "
           "revived + pit landed; E15 48h CEO report met 9h early; flags=pool_starvation/supply_floor standing "
           "(resource-blocked until batch completes)")

# ---- state.json ----
s = json.load(open("state.json", encoding="utf-8"))
s["round_no"] = 912
s["round_no_label"] = "r911"
s["round"] = 911
s["did"] = DID
s["task"] = NEXT
s["next"] = NEXT
s["next_milestone"] = ("i2v 53/53 ETA 10-13 morning (long-clip OOM watch) -> N2U3 flip double-gated -> export-topk+judged; "
                       "E15 48h MET early; W18 48h 10-14 00:44; unity-mcp POC <=10-13 12:00")
s["verdict"] = VERDICT
s["note"] = ("r911: S0 6-face resolver integration + main re-push delivered; i2v batch OOM death diagnosed (EngineTick "
             "on-demand qwen co-load x KN13 len=226 long clip -> WDDM spill -> commit 25.3GB) + revived (ComfyUI r911c + "
             "driver r911c SKIP resume); E15 48h CEO report delivered early; pit direct-write pit-machine.md per r666/r903")
s["last_action"] = ("r911: S0 integration delivered 2e0c884a2 + i2v batch OOM root-caused+revived (KN13 re-in-flight) + "
                    "E15 48h report early + S6 41 legs + pit-machine entry")
s["last_action_at"] = NOW
s["last_seen"] = NOW
s["last_round_at"] = NOW
s["last_round_ts"] = NOW
s["now_active"] = ("i2v animatic batch re-burning post-revival (15/53 done, KN13 226-frame long clip in-flight, ComfyUI "
                   "r911c PID 6280 + driver r911c, GPU 100% under 180W cap)")
s["latest_artifact"] = ("driver_r911c.out.txt (KN13 SUBMITTED revival proof) + CEO-48H-E15-EMOTION-REEVAL-20261013.md + "
                        "pit-machine.md r911 entry (sha16 7754f356fa88de12) + main delivery 2e0c884a2")
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = ("r911 probe 02:1x: py_faces=17 orphans=0; stale driver 2148 killed deliberately (dead-server "
                         "poll face), successor driver r911c + ComfyUI r911c PID 6280 both live registered faces")
s["sync"] = {"last_push_ts": NOW,
            "note": "r911 closeout: S0 first-mission push delivered 2e0c884a2 to origin/main (ls-remote verified, "
                    "unreached=0); round commit + push follow this write"}
s["ts"] = NOW
s["updated"] = NOW
s["updated_at"] = NOW
s["clock_read"] = NOW
s["current_task"] = "r911 closeout; r912 = batch watch + long-clip OOM watch + N2U3 flip at 53/53 + unity-mcp POC window"
json.dump(s, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["clock_read"] = NOW
h["ts"] = NOW
h["last_seen"] = NOW
h["updated"] = NOW
h["updated_at"] = NOW
h["last_round_at"] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["round_no"] = 911
h["round"] = 911
h["round_no_label"] = "r911"
h["current_task"] = s["current_task"]
h["last_action"] = s["last_action"]
h["last_action_at"] = NOW
h["did"] = DID
h["task"] = NEXT
h["next"] = NEXT
h["next_milestone"] = s["next_milestone"]
h["now_active"] = s["now_active"]
h["latest_artifact"] = s["latest_artifact"]
h["verdict"] = VERDICT
h["note"] = s["note"]
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = s["orphan_face_note"]
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["green_idle"] = False
h["free_ram_gb"] = ram_free_gb()
h["ram_free_gb"] = ram_free_gb()
h["ram_free_pct"] = round(ram_free_gb() / 24 * 100, 1)
h["gpu_free_vram_gb"] = 0.3
h["vram_free_gb"] = 0.3
h["gpu"] = {"util_pct": 100.0, "mem_used_mb": 7899.0, "power_w": 72.0,
            "face": "i2v animatic batch re-burning post-revival (ComfyUI r911c PID 6280 + driver r911c, KN13 226-frame long clip in-flight, 180W cap held)"}
h["sync"] = s["sync"]
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state+heartbeat written; ram_free=%.2fGB epoch=%d(int)" % (ram_free_gb(), EPOCH))
print("epoch is int:", isinstance(h["heartbeat_epoch_utc"], int))
