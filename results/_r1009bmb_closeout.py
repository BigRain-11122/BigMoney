"""r1009 bm-b closeout: state.json + heartbeat + round report row.
Pure ASCII source (repo encoding law; zh-CN hosts decode BOM-less as
GBK). Content faces in ASCII English per r1008 precedent. r504 atomic
writes + post-write readback assertions."""
import ctypes
import json
import os
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state.json")
HEART = os.path.join(REPO, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")

NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

DID = (
    "r1009: (a) S0 fast-forward absorb a56df48331->a965e16b1a (31 commits: bm-c "
    "r1095-r1098 W270/W271 full cycles + W272 seat publish + bm-a r1061-r1065 "
    "guard/S6 rounds); 3-face bridge (machine-health + watermark_red origin-side "
    "newer-wins per r1007/r751 law; bm-b heartbeat local-newer kept, idle face "
    "consumed via --worked). (b) S0.5: orders_ack_scan exit 3 -> O-20261018-1810 "
    "(all-hands resume broadcast) bm-b receipt line filled (no pause history, "
    "full power maintained) + dual-face ack via orders_ack_append (103/103 CLEAN); "
    "same-window ackfix: --help argv-gate miss appended a bogus ack target to both "
    "faces -> surgical dual-face removal (_r1009bmb_ackfix.py, 102/102 restored, "
    "ack_last repaired, scan re-verified CLEAN). D-19 double advance: ORD "
    "43a18d01->9b4f5992 (7 rows: bm-d hardware x3 + CEO meta-criticism 15:1x "
    "(result-supervision, bm-a executed C-20261018-05 group-side) + MV V5.8 "
    "feedback / producer-supervisor seat / all-stage expert coverage -- zero "
    "BigMoney dispatch), then S6-chain rescan delta 9b4f5992->1b6ccf2a (19:28 CEO "
    "efficiency-accountability row, BigStream lane, zero BigMoney dispatch); both "
    "via d19 update --advance in-tool r1090 dual-face (mirrors synced 3, read-back "
    "OK); DEC 4cfdd17c hold. (c) S3 FIRST ACTION: CODELY.md hot-cold surgery -- 4 "
    "cold rows moved verbatim to archive 202610.md r1009 bm-b batch (r1089 d19 "
    "single-face row superseded by r1090 in-tool dual-face / r1091 W268 editor / "
    "r1093 fivekeys anchor / r1093 autocrlf smudge) + 4 compact pointer backfill + "
    "r1008 window new pit law landed (rebase-continue GHOST-REFUSAL deadloop + "
    "mid-rebase stash-pop index poison + per-machine-keyed faces UNION law, "
    "1,084B); 9,968B->9,628B under 10KB hard line; prescan rc3 = authorized "
    "migration face TPL s2, zero-loss asserted, receipt "
    "_r1009bmb_codely_hotcold_receipt.json. (d) S6 43 legs rc0 2.3min: orphan 7/0, "
    "smoke 49/49, dualrun ZERO-DRIFT streak 51, idle --worked (0), audit FLAG "
    "pool_starvation/supply_floor (honest starvation: boards/pool empty; supply "
    "face = W272 seat published by bm-c 19:1x + bm-c r1099 W272 prereg derive "
    "in-flight), py_watermark insufficient_history (n=1 window), dualarm "
    "DUALARM-2026-09-30 regen (bm-b lane product), REPORT/LIVE-2026-10-18 "
    "regenerated, attrition healed-clean, token delta recorded; Sunday live.paper "
    "family honest skip x4; 6 lane-guard honest skips (host=bm-a faces fresh "
    "14-15min). (e) S2/S8: job board empty, zero open tickets, queues drained, "
    "local self-drive registry zero open -> maintenance round consumed via "
    "--worked; inbox MSG-W272-seat (owner bm-c) read zero-action left in place. "
    "(f) S7: loop task no-op pin=2 correct, watchdog S4U re-registered, "
    "pre-commit + pre-push claws installed."
)

VERDICT = (
    "GREEN: r1009 maintenance round -- S0 FF absorb a965e16b1a (31 commits) + "
    "O-1810 resume-broadcast receipt (bm-b no-pause full-power, dual-face ack "
    "103/103 CLEAN incl. bogus-target ackfix same window) + D-19 double advance "
    "(43a18d01->9b4f5992->1b6ccf2a, both deltas zero BigMoney dispatch, DEC hold) "
    "+ CODELY.md hot-cold surgery (9,968->9,628B under 10KB; 4 rows verbatim "
    "cold-migrated with pointer backfill; r1008 push-saga pit law landed) + S6 43 "
    "rc0 (dualarm/REPORT/LIVE regen, dualrun streak 51, orphan 7/0, idle --worked); "
    "leftovers = supply_floor honest starvation (W272 seat = bm-c 19:1x, r1099 "
    "prereg derive in-flight; bm-b lane awaits W273+ seat / secretary restock) + "
    "O-0948 window zero died-pre-closeout holding (close judgment 10-19 ~10:2x)"
)

NEXT = (
    "r1010: 1) O-0948 24h observation window close judgment (10-19 ~10:2x morning "
    "window, died-pre-closeout holding zero) 2) D-19 fresh delta advance 3) bm-b "
    "engine lane awaits W273+ seat publish (W272 = bm-c published 19:1x, r1099 "
    "prereg derive in-flight) / secretary restock for pool famine 4) 41-song P2 "
    "lyric batch if dispatched to bm-b = reuse lyric_calibration argv pattern "
    "(r1007 precedent) 5) 10-25 memory-governance review window"
)

NEXT_MILESTONE = (
    "O-0948 window close judgment 10-19 ~10:2x + W272 chain finalize (bm-c) then "
    "bm-b engine-lane supply face (48h milestone = 10-19 morning O-0948 judgment)"
)

LATEST_ARTIFACT = (
    "CODELY.md r1008 push-saga pit law landed + hot-cold reorg to 9,628B "
    "(archive 202610.md r1009 bm-b batch + receipt _r1009bmb_codely_hotcold_"
    "receipt.json) + O-20261018-1810 bm-b receipt line (all-hands resume "
    "broadcast, full power maintained) 19:3x"
)

LAST_ACTION = (
    "r1009: S0 FF absorb a965e16b1a + O-1810 dual-face receipt + D-19 double "
    "advance (1b6ccf2a) + CODELY.md hot-cold surgery + S6 43 rc0 + idle --worked"
)

NOTE = (
    "r1009: ackfix same-window (orders_ack_append --help argv-gate miss appended "
    "bogus target both faces, surgical dual-face removal, scan CLEAN re-verified); "
    "CODELY.md 4-row cold migration authorized face TPL s2 prescan rc3; W272 seat "
    "= bm-c owner (bm-b zero-crossing); supply_floor = honest starvation face"
)

TASK = "r1009: closeout (CODELY hotcold + O-1810 receipt + D-19 double advance + S6 chain + push)"

REPORT_ROW = (
    "%s | r1009 | S0 FF absorb 31 commits (a965e16b1a); O-1810 resume-broadcast "
    "receipt (bm-b no-pause full-power) + dual-face ack + bogus-target ackfix; "
    "D-19 double advance 43a18d01->9b4f5992->1b6ccf2a (zero BigMoney dispatch "
    "both deltas, DEC hold); CODELY.md hot-cold surgery 9,968->9,628B (4 rows "
    "verbatim cold-migrated + pointers + r1008 push-saga pit law landed, prescan "
    "rc3 TPL s2); S6 43 legs rc0 (dualarm/REPORT/LIVE regen, dualrun streak 51, "
    "orphan 7/0); S7 claws+watchdog re-verified | smoke 49/49; orders_ack_scan "
    "CLEAN 103/103; d19 read-back dual-face OK; hotcold receipt zero_loss=true; "
    "s6 log results/_r1009bmb_s6_log.txt | r1010: O-0948 window close judgment "
    "10-19 AM; D-19 fresh delta; engine lane awaits W273+ seat/secretary restock"
) % NOW_ISO

SYNC_ENTRY = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1010",
    "behind_origin_main": 0,
    "note": (
        "r1009 payload = own faces (O-1810 receipt + CODELY.md + archive 202610 "
        "+ state/heartbeat/round-report + r1009 work files + ackfix + hotcold "
        "receipt + s6 chain/log + bm-b-lane regen faces); base = a965e16b1a origin "
        "tip fresh at S0 FF; CODELY migration = authorized face TPL s2 (prescan "
        "rc3 recorded in receipt)"
    ),
}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump_atomic(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def free_ram_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS()
    ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return round(ms.ullAvailPhys / (1024 ** 3), 1)


def gpu_free_mb(default):
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            return int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    return default


def cpu_load(default):
    try:
        with open(os.path.join(REPO, "results", "compute_audit.json"),
                  encoding="utf-8") as f:
            return round(float(json.load(f).get("cpu_total_pct", default)), 1)
    except Exception:
        return default


def main():
    st = load(STATE)
    ht = load(HEART)
    ram = free_ram_gb()
    vram = gpu_free_mb(ht.get("gpu_free_vram_mb", 0))
    load_pct = cpu_load(ht.get("cpu_load_pct", 0))
    for obj in (st, ht):
        obj["round_no"] = 1009
        obj["round"] = 1009
        obj["current_task"] = TASK
        obj["task"] = TASK
        obj["did"] = DID
        obj["last_action"] = LAST_ACTION
        obj["last_action_at"] = NOW_ISO
        obj["verdict"] = VERDICT
        obj["current"] = VERDICT
        obj["next"] = NEXT
        obj["next_milestone"] = NEXT_MILESTONE
        obj["latest_artifact"] = LATEST_ARTIFACT
        obj["last_artifact"] = LATEST_ARTIFACT
        obj["note"] = NOTE
        obj["now_active"] = "r1009 closing"
        obj["last_seen"] = NOW_ISO
        obj["clock_read"] = NOW_ISO
        obj["ts"] = NOW_ISO
    st["round_no_label"] = "r1009"
    st["updated"] = NOW_ISO
    st["updated_at"] = NOW_ISO
    st["last_round_at"] = NOW_ISO
    st["last_round_ts"] = NOW_ISO
    st["last_action_at"] = NOW_ISO
    st["orphan_face"] = 7
    st["orphan_faces"] = 7
    st["orphan_face_note"] = "r1009 chain probe (19:31): 7 py faces / 0 orphans"
    st["sat_engine"] = {
        "status": "alive (r1009 S6 status rc0, idle verdict, queue_depth 0; "
                  "supply floor = honest starvation, W272 seat = bm-c, bm-b lane "
                  "awaits W273+)",
        "checked_at": NOW_ISO,
    }
    st["sync"]["r1009_main_push"] = SYNC_ENTRY
    st["sync"]["behind_origin_main"] = 0
    st["sync"]["last_push_ts"] = NOW_ISO
    st["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
    ht["idle_rounds"] = 0
    ht["agenda_starved"] = False
    ht["heartbeat_epoch_utc"] = EPOCH
    assert isinstance(ht["heartbeat_epoch_utc"], int), "epoch must be int"
    ht["cpu_cores"] = 16
    ht["free_ram_gb"] = ram
    ht["gpu_free_vram_mb"] = vram
    ht["cpu_load_pct"] = load_pct
    dump_atomic(STATE, st)
    dump_atomic(HEART, ht)
    # round report row (append-only)
    with open(REPORT, "a", encoding="utf-8", newline="") as f:
        f.write("\n" + REPORT_ROW)
    # readback assertions
    s2 = load(STATE)
    h2 = load(HEART)
    assert s2["round_no"] == 1009 and h2["round_no"] == 1009
    assert isinstance(h2["heartbeat_epoch_utc"], int)
    assert h2["last_orders_sha"] == s2["last_orders_sha"] == \
        "1b6ccf2a011505c1979b646f3ca376e7801d3ffd02ef8fb16f3b05eb5dc45669"
    assert h2["orders_ack_last"] == "O-20261018-1810-bm-c.md"
    print(json.dumps({
        "round": 1009, "epoch": EPOCH, "free_ram_gb": ram,
        "gpu_free_vram_mb": vram, "cpu_load_pct": load_pct,
        "state_bytes": os.path.getsize(STATE),
    }))


if __name__ == "__main__":
    main()
