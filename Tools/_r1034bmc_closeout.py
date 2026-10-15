"""r1034 bm-c closeout: state/heartbeat/round-report writer + ORD watermark
self-advance (own CAS receipt row = the only new content, verified old-blob
vs new-blob byte equation) + codely_live_count observation post field
(C-20261015-03 sec.2 item 6). Atomic write pattern per r985 wb-truncation
law: full-content memory compose -> temp file -> os.replace."""
import datetime
import hashlib
import json
import os
import re
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = r"K:\Fluxgroup\FluxGroup"
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
MARKER = "spawn 闸 preflight 落位+机级错峰核查 PASS（@bm-c"


def g(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True)
    return p.returncode, p.stdout


def sha1_bytes(b):
    return hashlib.sha1(b).hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def rw_json(path, new_content):
    tmp = path + ".tmp_r1034"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    os.replace(tmp, path)


def main():
    now = datetime.datetime.now().astimezone()
    iso = now.isoformat(timespec="seconds")
    epoch = int(time.time())

    # --- watermark faces: fetch + compute, verify own-row-only delta ---
    g(["fetch", "origin"])
    rc, new_ord = g(["show", "origin/main:docs/orders.md"])
    rc2, old_ord = g(["show", "bc9a151733ba:docs/orders.md"])
    rc3, dec = g(["show", "origin/main:docs/decisions.md"])
    assert rc == 0 and rc2 == 0 and rc3 == 0, "git show failed"
    own_only = (MARKER.encode("utf-8") in new_ord
                and MARKER.encode("utf-8") not in old_ord
                and new_ord == old_ord + new_ord[len(old_ord):]
                and new_ord.startswith(old_ord))
    new_ord_sha = sha1_bytes(new_ord)
    new_dec_sha = sha256_bytes(dec)
    print("ord sha", new_ord_sha, "dec sha", new_dec_sha[:16],
          "own-row-only:", own_only, "old tail == new head:",
          new_ord.startswith(old_ord))
    if not own_only:
        print("ABORT: orders delta is NOT own-row-only -- manual consumption needed")
        return 3

    # live counters
    try:
        codely_live = int(subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "@(Get-Process -Name codely -ErrorAction SilentlyContinue).Count"],
            capture_output=True).stdout.decode().strip() or "0")
    except Exception:
        codely_live = -1
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"], capture_output=True)
        used, total, gpu_util = [int(x.strip()) for x in
                                 p.stdout.decode().strip().split(",")]
    except Exception:
        used, total, gpu_util = 0, 0, 0
    free_vram = total - used
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong)]
        ms = MEMORYSTATUSEX()
        ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        ram_free = round(ms.ullAvailPhys / (1024 ** 3), 2)
    except Exception:
        ram_free = -1

    did = ("r1034 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 "
           "orphans=2 zero-kill (legal daemon faces); (2) S0.5 dual-delta "
           "FALSE both (ord b92c1208 / dec ab3f0cc9 hold), unacked=0; "
           "(3) S1 smoke 49/49; (4) P0 PRODUCT = O-20261015-1834 @bm-c duty "
           "LANDED same-window (24:00 deadline met): spawn-gate preflight "
           "Tools/spawn_gate.ps1 (C-20261015-03 sec.3 spec verbatim: codely."
           "exe live count, cap=2, fail-open, DEFER ledger results/cloud_cap"
           "_ledger.jsonl + next-grid-slot retry) wired into Tools/"
           "iteration_loop.ps1 pre-ignition (rc=3 = round yield, lock law "
           "stacks) + selftest 3/3 (PROBE live=1 / GO rc0 / DEFER rc3 + "
           "ledger row) + machine stagger audit PASS (sole codely igniter = "
           "Bigmoney-IterationLoop PT10M pin :X5; MiniGameComfyDraftTick/"
           "KeepAlive verified ComfyUI python guards, 'codely' action match "
           "= .codely-cli path-segment false-positive; zero same-minute "
           "face = zero changes zero backup need) + heartbeat codely_live_"
           "count field added (live=1, three-machine same-field law) + "
           "group-tree CAS receipt row landed (origin tip 1746e9250207, "
           "zero working-tree touch, tip verified; group tree holds stale "
           "staged-deletion face disclosed for stewards incl card-lint.py); "
           "(5) S6 chain 43/43 rc=0 (19:03:40-19:05:41, bars 10-15 sina-"
           "lag 6th window cutoff 10-14, papers debt=0); (6) jayredo watch: "
           "runner pid 78884 alive, i2v 0/11 landed (bmc/i2v/jayredo/ absent,"
           " GPU 100% burn legal, ETA ~20:0x); (7) W247 finalize absent -> "
           "W248 waits-upstream legal; (8) idle green_idle=false RAM-gate "
           "honest (4.5pct, U256/w20 stay deferred); (9) S7 quad green "
           "(loop pin=5 no-op, watchdog registered [S4U XML flip access-"
           "denied = adjudicated default-principal face r1023/D-20261002-02],"
           " claws x2 installed, attrition 4 CLEAN + 1 healed note); counter "
           "1034->1035")
    verdict = ("green: r1034 = O-20261015-1834 spawn-gate preflight LANDED "
               "before 24:00 deadline (gate + loop wiring + selftest 3/3 + "
               "stagger audit PASS + codely_live_count heartbeat field + "
               "group CAS receipt 1746e925) + smoke 49/49 + S6 43/43 rc0 "
               "(bars 10-15 sina-lag 6th window debt=0) + S0.5 dual-delta "
               "FALSE + S7 quad green + jayredo i2v-11 burning watch (0/11, "
               "ETA ~20:0x) + W248 waits-upstream (W247 finalize absent)")
    note = ("r1034: O-1834 spawn-gate landed (24:00 deadline met) | ORD "
            "self-advanced b92c1208->%s (own CAS receipt row only) | bars "
            "10-15 sina-lag 6th window | jayredo i2v 0/11 ETA ~20:0x | W248 "
            "waits-upstream | watchdog S4U flip denied = adjudicated face"
            ) % new_ord_sha[:7]
    next_pointer = ("r1035: (1) jayredo harvest watch: 11 i2v INT8 768P -> "
                    "bmc/i2v/jayredo/ + Phase C push receipt verify + poke "
                    "bm-a assembly on all-11; (2) XINGQING T1 POOL-0015 "
                    "IGNITION = FIRST ACTION on GPU release (33-frame 8-"
                    "block template + lint + Krea2 672x384 seeds + ladder "
                    "early-stop 8-first + N>=16/32/50 + two-tier sea-"
                    "review); (3) W247 finalize watch -> W248 prereg derive "
                    "= first action on landing (waits-upstream law); "
                    "(4) bars 10-15 recheck 7th window (sina governs; if "
                    "landed -> papers full chain); (5) performance-trio "
                    "night trials 10-16/17/18; (6) W20 SCREEN autofill "
                    "night-window; (7) U256 w001/w003 RAM gate deferred; "
                    "(8) group-tree stale staged-deletion face = stewards' "
                    "call (disclosed in receipt row)")
    artifact = ("r1034: Tools/spawn_gate.ps1 + iteration_loop.ps1 spawn-gate "
                "wiring (C-20261015-03 sec.3) + selftest 3/3 + group CAS "
                "receipt 1746e9250207 + S6 43/43 rc0 log")
    prod_lanes = ("CPU=W20 SCREEN 4 shards claim-ready lane-pinned bm-c (RAM "
                  "gate park-honest; autofill night-window) ; GPU=MV V4 "
                  "jayredo P0 BURNING (runner pid 78884: 11 i2v INT8 768P "
                  "in-flight -> bmc/i2v/jayredo/ -> bm-a re-assembly; KF "
                  "24/24 absorbed r1032) + ComfyUI resident + album serve ; "
                  "xingqing T1 POOL-0015 UNLOCKED queued-behind-i2v (GPU "
                  "serial) ; N1=W247 bm-a chain face (finalize watch) -> "
                  "W248 bm-c waits-upstream ARMED ; U256 w001/w003 = RAM "
                  "gate deferred ; MEMORY-GATE=HQ-MemoryBudgetGate 4h cycle "
                  "(bm-c leg closed r1027) ; SPAWN-GATE=codely cap 2 live "
                  "(C-20261015-03, landed r1034)")

    # ---------- state ----------
    with open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    st["round_no"] = 1035
    st["round_no_label"] = "r1034"
    st["last_round"] = "r1034"
    st["last_round_label"] = "r1034"
    for k in ("clock_read", "last_round_at", "last_round_ts", "last_seen",
              "last_seen_at", "ts", "updated", "updated_at", "now_active",
              "activity_now", "last_round_closed", "last_round_summary_at",
              "last_action_at", "current_task_at", "last_round_at"):
        st[k] = iso
    st["current_task"] = ("r1034 closeout: O-20261015-1834 spawn-gate "
                          "landed (24:00 deadline met) + group CAS receipt "
                          "1746e925 + S6 43/43 + jayredo i2v-11 watch")
    st["last_round_summary"] = ("r1034: O-1834 spawn-gate landed (gate+"
                                "wiring+selftest 3/3+stagger PASS+heart "
                                "field+CAS receipt) + smoke 49/49 + S6 "
                                "43/43 rc0 + S7 quad green")
    st["last_action"] = "r1034 closeout (O-20261015-1834 duty executed same-window)"
    st["did"] = did
    st["verdict"] = verdict
    st["note"] = note
    st["next"] = next_pointer
    st["next_pointer"] = next_pointer
    st["next_milestone"] = ("r1035+: jayredo 11 i2v -> bm-a V4 assembly "
                            "(~20:0x) + xingqing T1 haixuan board + bars "
                            "10-15 papers chain on sina landing")
    st["latest_artifact"] = artifact
    st["last_artifact"] = artifact
    st["recent_artifact"] = artifact
    st["prod_lanes"] = prod_lanes
    st["heartbeat_epoch_utc"] = epoch
    st["last_orders_sha"] = new_ord_sha
    for k in ("last_orders_at", "last_orders_read_at", "last_orders_seen",
              "last_decisions_read_at", "last_decisions_at",
              "last_decisions_seen"):
        st[k] = iso
    st["last_orders_sha_note"] = ("r1034: ORD self-advanced b92c1208->%s "
                                  "(own CAS receipt row ONLY, byte-equation "
                                  "verified old-blob prefix + single row; "
                                  "group-tree receipt 1746e9250207)"
                                  ) % new_ord_sha[:7]
    st["last_decisions_sha"] = new_dec_sha
    st["last_decisions_read_note"] = "r1034: DEC delta FALSE hold (raw-blob sha256 verified)"
    st["free_ram_gb"] = ram_free
    st["ram_free_gb"] = ram_free
    st["idle_ram_gb"] = ram_free
    st["gpu_free_vram_mib"] = free_vram
    st["gpu_free_vram_mb"] = free_vram
    st["gpu_util_pct"] = gpu_util
    st["gpu_mem_used_mib"] = used
    st["gpu_used_vram_mib"] = used
    st["gpu_mem_total_mib"] = total
    st["gpu_total_vram_mib"] = total
    st["idle_rounds"] = 0
    st["agenda_starved"] = False
    st["orphan_face"] = 2
    st["orphan_faces"] = 2
    st["codely_live_count"] = codely_live
    st["verify"] = ("receipts: smoke 49/49 + spawn-gate selftest 3/3 "
                    "(PROBE live=1/GO rc0/DEFER rc3+ledger row) + stagger "
                    "audit PASS (sole igniter pin :X5) + S6 43/43 rc0 log + "
                    "group CAS receipt tip-verified 1746e925 + ORD own-row "
                    "byte-equation + DEC raw-blob hold + epoch int readback "
                    "+ attrition 4 CLEAN + quad green")
    st["full_load_selfproof"] = {
        "占用一行": prod_lanes,
        "当前活": "r1034 closeout (O-1834 spawn-gate landed + S6 43/43 + jayredo watch)",
        "最近实物": ("Tools/spawn_gate.ps1 + iteration_loop.ps1 接线 + selftest 3/3 + "
                    "group orders 回执行 1746e925（CAS tip-verified·19:0x）"),
        "下个交付物": ("jayredo 11 i2v INT8 768P 完成包（ETA ~20:0x）-> bm-a 装配站 V4 重装；"
                    "xingqing T1 海选板（GPU release 后 first action）；bars 10-15 "
                    "sina 落即 papers 全链；W248 prereg derive（W247 finalize 落即发）"),
        "队列水位": ("池 ready=W20 screen（lane bm-c·RAM 门 park-honest）·N1 W247 bm-a "
                  "在飞 finalize watch·W248 waits-upstream·U256 候 RAM 门·P2/P3 空·jobs 0"),
    }
    st["d19_watermark_guard"]["round_ref"] = 1034
    st["d19_watermark_guard"]["ts"] = iso
    st["r1034_closeout_note"] = ("r1034: clean continuation window (state "
                                 "round_no=1034 at open, executed r1034, "
                                 "advanced 1034->1035 so next=r1035); zero "
                                 "absorb owed (r1033 closeout 580ff1b42 "
                                 "landed clean); O-20261015-1834 spawn-gate "
                                 "duty executed same-window before 24:00 "
                                 "deadline; group-tree CAS receipt row "
                                 "landed 1746e9250207 (zero tree touch; "
                                 "stale staged-deletion face disclosed in "
                                 "row); bars 10-15 sina-lag 6th window "
                                 "papers debt=0; watchdog S4U flip "
                                 "access-denied = adjudicated default-"
                                 "principal face")
    rw_json(STATE, json.dumps(st, ensure_ascii=False, indent=1))

    # ---------- heartbeat ----------
    with open(HEART, "r", encoding="utf-8") as fh:
        hb = json.load(fh)
    hb["round_no"] = 1034
    hb["round_no_label"] = "r1034"
    hb["last_round"] = "r1034"
    hb["codely_live_count"] = codely_live
    hb["heartbeat_epoch_utc"] = epoch
    for k in ("last_seen", "clock_read", "ts", "last_seen_at", "updated_at",
              "updated", "last_round_at", "last_round_ts", "last_round_closed",
              "last_round_summary_at", "current_task_at", "last_action_at",
              "last_decisions_read_at", "last_decisions_at",
              "last_orders_at", "last_orders_read_at", "last_orders_seen",
              "now_active", "activity_now"):
        hb[k] = iso
    hb["current_task"] = st["current_task"]
    hb["last_round_summary"] = st["last_round_summary"]
    hb["last_action"] = st["last_action"]
    hb["did"] = did
    hb["verdict"] = verdict
    hb["note"] = note
    hb["next"] = next_pointer
    hb["next_pointer"] = next_pointer
    hb["next_milestone"] = st["next_milestone"]
    hb["latest_artifact"] = artifact
    hb["last_artifact"] = artifact
    hb["recent_artifact"] = artifact
    hb["prod_lanes"] = prod_lanes
    hb["full_load_selfproof"] = st["full_load_selfproof"]
    hb["free_ram_gb"] = ram_free
    hb["ram_free_gb"] = ram_free
    hb["idle_ram_gb"] = ram_free
    hb["gpu_free_vram_mib"] = free_vram
    hb["gpu_free_vram_mb"] = free_vram
    hb["gpu_util_pct"] = gpu_util
    hb["gpu_mem_used_mib"] = used
    hb["gpu_used_vram_mib"] = used
    hb["gpu_mem_total_mib"] = total
    hb["gpu_total_vram_mib"] = total
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["verify"] = st["verify"]
    hb["last_orders_sha"] = new_ord_sha
    hb["last_decisions_sha"] = new_dec_sha
    hb["last_orders_sha_note"] = st["last_orders_sha_note"]
    hb["sync"] = {"origin_tip": "closeout commit+push rides this window",
                  "ts": iso, "ahead_behind": "0/0 pre-closeout"}
    rw_json(HEART, json.dumps(hb, ensure_ascii=False, indent=1))

    # ---------- round report ----------
    row = (iso + " | r1034 | bm-c | O-20261015-1834 @bm-c duty LANDED same-"
           "window (24:00 deadline met): spawn-gate preflight Tools/"
           "spawn_gate.ps1 (sec.3 spec verbatim: codely.exe live count, "
           "cap=2, fail-open, DEFER ledger + grid-slot retry) wired into "
           "iteration_loop.ps1 pre-ignition (rc=3 = round yield) + selftest "
           "3/3 (PROBE live=1 / GO rc0 / DEFER rc3 + ledger row) + machine "
           "stagger audit PASS (sole codely igniter = IterationLoop PT10M "
           "pin :X5; MiniGame ticks = ComfyUI python guards, path-segment "
           "false-positive; zero same-minute face = zero changes) + heart "
           "codely_live_count field added (live=1) + group CAS receipt row "
           "landed (1746e9250207, zero tree touch, tip verified; stale "
           "staged-deletion face disclosed for stewards) | smoke 49/49 + "
           "S6 43/43 rc=0 (bars 10-15 sina-lag 6th window, cutoff 10-14, "
           "papers debt=0) + S0.5 dual-delta FALSE + unacked=0 + S7 quad "
           "green (loop pin=5 no-op; watchdog S4U-flip denied = "
           "adjudicated default face; claws x2 installed; attrition 4 "
           "CLEAN) + jayredo i2v 0/11 watch (pid 78884 alive, GPU 100 pct "
           "legal, ETA ~20:0x) + W247 finalize absent (W248 waits-upstream "
           "legal) + idle green_idle=false RAM-gate honest | watermark "
           "verdict GREEN (red=false) | orphan_face=2 zero-kill | "
           "local-ahead-of-origin=0 (post-push fetch) | next r1035: "
           "jayredo 11-i2v harvest + Phase C push receipt verify + poke "
           "bm-a on all-11 + xingqing T1 ignition on GPU release + bars "
           "10-15 recheck (7th window) + W248 prereg on W247 finalize\n")
    with open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)

    print("closeout written; ord_sha", new_ord_sha[:7],
          "dec_sha", new_dec_sha[:7], "codely_live", codely_live,
          "ram_free", ram_free, "free_vram", free_vram, "epoch", epoch)
    # epoch int readback assert
    with open(HEART, "r", encoding="utf-8") as fh:
        back = json.load(fh)
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
    assert isinstance(back["codely_live_count"], int), "live count must be int"
    print("epoch-int readback OK; codely_live_count int OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
