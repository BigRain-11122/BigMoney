"""r1257 closeout: round report row + state file + heartbeat, single fresh read-modify-write."""
import io
import json
import os
import time
from datetime import datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

NOW = datetime.now().astimezone().replace(microsecond=0).isoformat()
MACHINE = "bm-b"
ROUND = 1257

ROW = (
    "| %s | r%d | dept:research+engineering | "
    "**WATERMARK**: GREEN at open (results/watermark_red.json red=false lane=healthy; "
    "idle_trigger.bm-b green_idle=true ram_free 46.1%%, pool ready 1 = E231) and the "
    "ready card was real work, so the round burned it | "
    "**CURRENT**: E231 path test of E230's one passing band | "
    "**LAST ARTIFACT**: results/state_tilt/BANDPATH-2026-10-29.json @ 22:40 | "
    "**NEXT MILESTONE**: E232 cost-curvature sweep (cost = c*|dw|^gamma, gamma "
    "0.75/1.0/1.25/1.5), window <=48h (deadline 2026-10-31 23:00) | "
    "**PRODUCT**: scripts/e231_band_path_test.py (run / selftest 18/18) + "
    "results/state_tilt/BANDPATH-2026-10-29.json + bandpath_latest.json + "
    "bandpath_by_cell_2026-10-29.csv + research/digests/DIGEST-20261029-r1257-e231-band-path.md "
    "+ knowledge/METHODOLOGY_ASSETS.md card E231 + S6 leg band_path_test after hysteresis_toll "
    "+ smoke leg cross-replaying the global path against E230 | "
    "**WHAT IT DOES**: E230 left exactly one of thirty cells above its bar, at the SMALLEST "
    "band in the grid (tilt_linear / single / f=0.10, t=4.04, +286 bp/yr) -- the shape E188 "
    "warns about. This re-measures that whole fine grid (eight rungs 0.02..0.20) on 25 "
    "panel-paths in three families: the IS/OOS split moved +/-10/20/40 sessions, the decision "
    "lagged 1-3 sessions (both arms alike), and calendar eras re-derived end to end, then "
    "publishes the SHARE of paths that keep the sign instead of the best cell. Two bars: "
    "E230's own 3.34 reused verbatim for the survival test (give the band every advantage) "
    "and a strict 4.10 over this study's 600 cells, disclosed and never used to rescue | "
    "**READ**: the focus cell keeps its sign on 12 of 12 paths and its size on 8 of 12. "
    "Structural paths (split + lag, same sample) hold 145.2..290.0 bp/yr, median 285.9, and "
    "the two misses are lag 2 and lag 3 -- so the finding is not an artefact of where the "
    "IS/OOS line sits but it decays when the decision reaches the book later. Era paths are "
    "where it goes: 77.1..80.8 bp/yr at t 1.36/1.75, i.e. the +286 is a FULL-SAMPLE effect "
    "that shrinks 3.5x inside either era and cannot be resolved there. Across the fine grid "
    "0 of 48 cells survive every path under the lenient bar; 7 are sign-unstable, 41 hold "
    "their sign and miss the bar somewhere, 0 collapsed, 0 under-powered. Disclosed on both "
    "sides: the cell's LEVEL is a loss -- at x2 costs the base arm's pair is -878.7 bp/yr and "
    "the banded arm's own pair is -592.8, so +286 is an improvement in a loss | "
    "**PITS**: the answer sentence was first written as prose and it contradicted the data "
    "(\"every one of those paths clears the bar\" beside 8 of 10) -- every claim in the face "
    "is now derived from the published numbers, and the two path families are never merged "
    "into one range because a full-sample median would then read as a statement about a "
    "period (a selftest leg pins the separation). Sibling: the smoke gate went red on the "
    "heartbeat GPU face (free family spread 307.2 MiB across 17 keys) -- two samples written "
    "by different lanes; healed by the sanctioned chokepoint python -m Tools.gpu_face apply "
    "(32 keys, findings []), never by hand-editing the heartbeat | "
    "**TESTS**: e231 selftest 18/18; S6 39/39 rc=0 (249.4s) with band_path_test rc=0 27.12s; "
    "dualrun ZERO-DRIFT 702 entries streak 15; compute_audit py 12.9%; attrition CLEAN 4 "
    "ledgers; machine_health OK 3 machines 8/8; gpu_face findings [] 32 keys; pagegate 2 of "
    "656 numbers unproduced and 0 new; smoke %%SMOKE%% | "
    "**D-19**: decisions 97fe122f / orders 122ab707 == stored watermark (repro @71eff9f, "
    "blob sha256 in the C:/Fluxgroup/FluxGroup group tree) -> zero new rows; 114 order files "
    "/ 115 acks / 0 unacked | "
    "**S7**: loop pin=2 no-op (first fire 22:47); LoopWatchdog re-registered S4U SWA=false; "
    "pre-commit + pre-push claws reinstalled (source in sync); sat engine rc=0 idle at open | "
    "**ORPHAN**: 0 (12 py faces) | "
    "**S8**: a pool row was burned, so the self-drive step did not fire | "
    "**NOT RUN**: GPU untouched (parked C-20261014-01; the media lanes hold ~6.8 GB); cloud "
    "untouched; no cleanup/quarantine action (nothing deleted, treasure_guard not exercised); "
    "bm-a/bm-c lane collectors honoured their guards; CODELY.md untouched (this session "
    "carries no append_memory tool) | "
    "**REGISTRY**: zero hits (no cleanup/archive action this round) | "
    "**MEMORY**: not written -- no append_memory tool in this session; the lesson is card "
    "E231 + DIGEST-20261029-r1257 | "
    "**POOL**: E231 done with result_ref, E232-COST-CURVATURE seeded ready (702 done / 1 "
    "ready) | **LOCAL-NOT-ON-ORIGIN**: 27 behind / 8 ahead"
)

FINDING = (
    "E230's one passing band keeps its sign on every path and loses its size. Re-measured on "
    "12 paths the focus cell (primary_single / tilt_linear / f=0.10) is positive 12/12 but "
    "above E230's own bar only 8/12: structural paths (split +/-10/20/40 sessions, decision "
    "lag 1-3) hold 145.2..290.0 bp/yr with the two misses at lag 2 and lag 3, while era "
    "paths collapse to 77.1..80.8 bp/yr at t 1.36/1.75 -- the +286 is a full-sample effect "
    "that shrinks ~3.5x inside either era and cannot be resolved there. 0 of 48 fine-grid "
    "cells survive every path under the lenient bar of 3.34; 7 are sign-unstable, 41 hold "
    "their sign and miss the bar somewhere. The cell's level is a loss on both sides "
    "(-878.7 base vs -592.8 banded at x2 costs), so the improvement is real in sign, "
    "unresolved in size, and never a positive return."
)

PIT = (
    "the answer sentence was first prose and it contradicted the face's own numbers "
    "(\"every one of those paths clears the bar\" next to 8 of 10); every claim is now "
    "derived from the published values. And a path range MUST be split by family -- merging "
    "the full-sample paths with the era paths gives a median that is the full-sample number "
    "and reads as a statement about a period (selftest leg pins the separation). Sibling: "
    "the smoke gate's GPU-face leg went red because two lanes stamped the heartbeat from "
    "different samples (307.2 MiB spread over 17 free keys); healed only via the chokepoint "
    "python -m Tools.gpu_face apply."
)

PRODUCT = [
    "scripts/e231_band_path_test.py",
    "results/state_tilt/BANDPATH-2026-10-29.json",
    "results/state_tilt/bandpath_latest.json",
    "results/state_tilt/bandpath_by_cell_2026-10-29.csv",
    "research/digests/DIGEST-20261029-r1257-e231-band-path.md",
    "knowledge/METHODOLOGY_ASSETS.md card E231",
    "Tools/s6_chain_bmb.py leg band_path_test",
    "smoke_test.py leg on the path test",
    "results/runnable_pool.json E231 done; E232 seeded ready 1",
]


def main(smoke_line, dept_note=""):
    # ---- 1. round report row
    rp = os.path.join("logs", "iteration-loop", "round_reports.md")
    with io.open(rp, encoding="utf-8") as fh:
        text = fh.read()
    row = ROW.replace("%%SMOKE%%", smoke_line)
    if "| r1257 |" in text:
        raise SystemExit("r1257 row already present -- refusing to double-append")
    with io.open(rp, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row + "\n")

    # ---- 2. state file
    sp = "state-%s.json" % MACHINE
    with io.open(sp, encoding="utf-8") as fh:
        st = json.load(fh)
    if st.get("round_no") == ROUND:
        raise SystemExit("state already at r1257")
    st["round"] = ROUND
    st["round_no"] = ROUND
    st["round_no_label"] = "r%d" % ROUND
    st["round_no_ts"] = NOW
    st["ts"] = NOW
    st["updated"] = NOW
    st["updated_at"] = NOW
    st["status"] = "green"
    st["dept"] = "research+engineering"
    st["task"] = ("r1257: E231 path-tests E230's one passing band -- the sign survives every "
                  "path, the size does not: it shrinks 3.5x inside either era")
    st["task_short"] = "E231 band path test"
    st["work"] = ("E231 face published and wired: runner + S6 leg band_path_test + smoke leg "
                  "cross-replaying E230's cell + digest + card E231; E232 cost curvature seeded")
    st["finding"] = FINDING
    st["pit"] = PIT
    st["verdict"] = (
        "WATERMARK GREEN at open (red=false lane=healthy, pool ready 1 = E231) and the ready "
        "card was real work, so E231 was burned in-window. | " + FINDING + " | "
        "smoke %s | S6 39/39 rc=0 | orphan 0 | pool 702 done / 1 ready" % smoke_line)
    st["product"] = PRODUCT
    st["d19"] = ("decisions 97fe122f / orders 122ab707 == stored watermark (repro @71eff9f) "
                 "-> zero new rows; 114 order files / 115 acks / 0 unacked")
    st["s6"] = ("39/39 rc=0 (249.4s); band_path_test rc=0 27.12s; dualrun ZERO-DRIFT 702 "
                "entries streak 15; compute_audit py 12.9%; attrition CLEAN 4 ledgers; "
                "machine_health OK 8/8; gpu_face findings [] 32 keys; pagegate 2 of 656 "
                "unsourced, 0 new")
    st["smoke"] = smoke_line.replace("PASS", "PASS").strip()
    st["selftest"] = "e231_band_path_test 18/18"
    st["pool"] = ("E231 done with result_ref; E232-COST-CURVATURE seeded ready "
                  "(702 done / 1 ready)")
    st["orphan"] = 0
    st["not_run"] = ("GPU untouched (parked C-20261014-01); cloud untouched; no cleanup or "
                     "quarantine action (nothing deleted, treasure_guard not exercised); "
                     "bm-a/bm-c lane collectors honoured their guards; CODELY.md not touched "
                     "(no append_memory tool in this session)")
    st["r1257"] = {
        "d19": st["d19"],
        "dept": st["dept"],
        "finding": FINDING,
        "pit": PIT,
        "product": PRODUCT,
        "pool": st["pool"],
        "s6": st["s6"],
        "smoke": smoke_line,
        "selftest": "18/18",
        "orphan": 0,
        "ts": NOW,
    }
    with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(st, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    json.loads(io.open(sp, encoding="utf-8").read())

    # ---- 3. heartbeat (own file only)
    hp = os.path.join("fleet", "machines", "%s.json" % MACHINE)
    with io.open(hp, encoding="utf-8") as fh:
        hb = json.load(fh)
    # GPU keys are owned by the Tools.gpu_face chokepoint (r1284/r1315): a closeout that
    # stamps vram_free_gb from its own probe leaves the face half-owned and turns the
    # smoke leg red, so this writer only re-stamps through the chokepoint afterwards.
    try:
        import subprocess
        subprocess.run(["python", "-m", "Tools.gpu_face", "apply"],
                       capture_output=True, text=True, timeout=90,
                       creationflags=0x08000000)
    except Exception as exc:
        hb["gpu_probe_warning"] = "gpu_face apply failed: %r" % (exc,)
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
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
        ram_load = float(ms.dwMemoryLoad)
        ram_free_pct = round(100.0 - ram_load, 1)
        hb["ram_free_gb"] = round(ms.ullAvailPhys / (1024.0 ** 3), 1)
        hb["ram_load_pct"] = ram_load
    except Exception:
        ram_free_pct = None
    hb["ts"] = NOW
    hb["clock_read"] = NOW
    hb["heartbeat_epoch_utc"] = int(time.time())
    hb["last_seen"] = NOW
    hb["current"] = ("r1257: E231 path-tests E230's passing band -- sign survives every path, "
                     "size does not")
    hb["current_task"] = "S6 chain + closeout (E231 face published, chain leg wired, card closed)"
    hb["verdict"] = st["verdict"][:600]
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["did"] = ("r1257 E231-BAND-PATH-TEST done: results/state_tilt/BANDPATH-2026-10-29.json")
    hb["orders_ack"] = hb.get("orders_ack") or []
    if ram_free_pct is not None:
        hb["ram_free_pct"] = ram_free_pct
    
    with io.open(hp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(hb, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    hb2 = json.loads(io.open(hp, encoding="utf-8").read())
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be an int"
    assert "T" in hb2["ts"] and ("+" in hb2["ts"] or "-" in hb2["ts"][10:]), hb2["ts"]
    print("closeout ok: row appended, state r%d, heartbeat %s ram_free %s" % (ROUND, hb2["ts"], ram_free_pct))


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "pending")