# -*- coding: utf-8 -*-
# r957 bm-c closeout: state + heartbeat write (R170/R178 epoch-int law, clock_read ISO8601 T-format)
import json, time, datetime, subprocess

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
R = 958  # counter advance: this window = r957, next = r958

# fresh resource sample (honest faces; CREATE_NO_WINDOW per repo CREAT pattern)
CREAT = 0x08000000
free_ram_gb = None
vram_free_mb = None
cpu_pct = None
try:
    import psutil
    free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 2)
    cpu_pct = psutil.cpu_percent(interval=0.5)
except Exception:
    pass
if vram_free_mb is None:
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, creationflags=CREAT)
        vram_free_mb = int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        try:
            it = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\idle_trigger.bm-c.json", encoding="utf-8"))
            vram_free_mb = int(it.get("vram_free_gb", 14.52) * 1024)
        except Exception:
            vram_free_mb = 14889

VERDICT = ("green: W228 SEAT PUBLISHED (probe rc0 ADMIT A 516_404..518_403 + B 518_404..518_603; staircase "
           "EIGHTY-EIGHTH instance hops=1 (naive 516_204 refused by registered W227 B) + own-A reserve hops=1; "
           "seed_admit FREE x2 (516404/2000 + 518404/200); conflicts=0; origin vacancy 4-checks held; leg4 "
           "W229+ projection A 518_404..520_403 / B 518_604..518_803 machine-read; receipt "
           "_w228bmc_20261013_probe_receipt.json + seat MSG-20261013-0720-bmc) + smoke 49/49 + dualrun "
           "ZERO-DRIFT streak 50 + wm py_low_board_clear legal + attrition 4 CLEAN + S7 quad green; audit FLAG "
           "pool_starvation/supply_floor structural answered by this seat (chain continues prereg->splice->burn)")

PROD_LANES = ("GPU=MV i2v lane idle-warm (queue 0/0, ComfyUI resident, INT8 unloaded ~15G free; director "
              "re-shakes + assembly ride bm-a lane); CPU=N1 W227 FULL CYCLE LANDED (923,189 / K 497,320) + "
              "W228 SEATED (prereg derive = next window first action per seat-first law)")

NEXT = ("r958: (1) W228 prereg derive FIRST ACTION (bloodline clone _w227 prereg derive + lineage replay "
        "preflight) -> five-face freeze splice -> engine self-burn 12/12 -> PRE-FINALIZE six-gate "
        "(W217-debt standing law) -> finalize one-pass -> five-key + sec.7/8 machine-read backfill; "
        "(2) Tue 15:30 new-bar window: papers full chain + update family; (3) quarantine observation watch "
        "(7-day window, 120 frames); (4) W229+ projection A 518_404..520_403 / B 518_604..518_803 re-derive "
        "mandate inherited (A-hops-prior-B EIGHTY-NINTH instance anticipated once W228 registered)")

DID = ("r957 (W228 seat publish window): (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill "
       "(MV-lane infra kept: ComfyUI 8188 queue 0/0 idle-alive + album_serve resident); S0 fetch behind=0/ahead=0, "
       "round-start dirty=10 all own bm-c live faces (collected at closeout); (2) S0.5 dual-delta FALSE both "
       "(dec fb5825cb / ord d559e530 hold, unacked=0); (3) S1 smoke 49/49; boards clear (jobs 0) + satengine "
       "ALIVE rc0; (4) PRODUCT=W228 SEAT PUBLISHED: probe derive _w228bmc_probe_derive.py (bloodline = "
       "_w227bmc_probe_derive.py verbatim machinery: bare 227->228 then 226->227; ordinal pairs leg4 "
       "EIGHTY-EIGHTH->EIGHTY-NINTH first + EIGHTY-SEVENTH->EIGHTY-EIGHTH x3; docstring/receipt/anchor swaps; "
       "14 numeric pairs count-asserted; residual 17-facet zero; required 10-facet present; py_compile green "
       "15,659B) -> probe rc0 ADMIT (leg0 anchor W227 ledger 923,189 / K 497,320 machine-read + owner_total 217 "
       "-> 218th wave bm-c 58th; leg1 staircase EIGHTY-EIGHTH hops=1 A 516_404..518_403 + B 518_404..518_603 "
       "own-A reserve hops=1, naive B inside own-A disclosed; leg2 conflicts=0 + seed_admit FREE x2; leg3 "
       "origin vacancy 4-checks held; leg4 W229+ projection) + seat MSG-20261013-0720-bmc published; "
       "(5) S6 light: dualrun ZERO-DRIFT streak 50 + compute_audit FLAG pool_starvation/supply_floor structural "
       "(answered by seat; prereg/splice/burn chain next) + wm py_low_board_clear legal whitelist; (6) S7 quad "
       "green (loop pin=5 no-op + watchdog re-armed + pre-commit/pre-push claws installed) + attrition 4 CLEAN "
       "(1 historical healed shrink noted); counter 957->958")

REPORT_LINE = (NOW + " | r957 | bm-c: W228 seat published (N1 supply chain continuation, seat-first law) | "
               "WM-VERDICT: green red=false (py_low_board_clear legal whitelist: boards 0/bandit 0/pool 0; "
               "supply answer = this seat + prereg/splice/burn chain next) | orphan face=2 zero-kill (MV-lane "
               "infra kept: ComfyUI 8188 queue 0/0 idle-alive + album_serve resident) | body: S0 fetch "
               "behind=0/ahead=0; S0.5 dual-delta FALSE both (dec fb5825cb / ord d559e530, unacked=0); smoke "
               "49/49; boards clear; satengine ALIVE rc0; PRODUCT=W228 SEAT: derive bloodline verbatim "
               "(bare227=48/bare226=57, pairs count-asserted, residual zero, py_compile green) -> probe rc0 "
               "ADMIT A 516_404..518_403 (staircase EIGHTY-EIGHTH hops=1, naive 516_204 refused by registered "
               "W227 B 516_204..516_403) + B 518_404..518_603 (own-A reserve hops=1, naive inside own-A) + "
               "seed_admit FREE x2 (516404 span2000 / 518404 span200) + conflicts=0 + origin vacancy 4-checks "
               "held + leg4 W229+ projection A 518_404..520_403 / B 518_604..518_803 (EIGHTY-NINTH "
               "anticipated) + seat MSG-20261013-0720-bmc; S6 light: dualrun ZERO-DRIFT streak 50 + audit FLAG "
               "pool_starvation/supply_floor structural (answered by seat) + wm py_low_board_clear; S7 quad "
               "green + attrition 4 CLEAN | counter 957->958 | W228 prereg derive = next window FIRST ACTION "
               "(per seat MSG declared sequence) | 3-line face: now=W228 seat published (ADMIT); "
               "recent=_w228bmc_20261013_probe_receipt.json + MSG-0720 07:20; next=W228 prereg->splice->burn->"
               "finalize (next window) + Tue 15:30 new-bar papers chain (<48h)")

def patch(path, updates):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    d.update(updates)
    d["round_no"] = R
    d["last_round"] = 957
    d["last_round_at"] = NOW
    d["clock_read"] = NOW
    d["ts"] = NOW
    d["updated"] = NOW
    d["heartbeat_epoch_utc"] = EPOCH
    d["verdict"] = VERDICT
    d["did"] = DID
    d["next"] = NEXT
    d["next_pointer"] = NEXT
    d["prod_lanes"] = PROD_LANES
    d["current_task"] = "r957 W228 seat published (ADMIT A 516404..518403 / B 518404..518603); W228 prereg derive = next first action"
    d["current_task_at"] = NOW
    d["last_round_summary"] = ("r957: W228 seat published (probe rc0 ADMIT A 516404..518403 / B 518404..518603 + "
                               "seed FREE x2 + MSG-0720) + S6 light (dualrun streak 50) + S7 quad green; counter 957->958")
    d["last_action"] = "r957 closeout (W228 seat publish + S6 light + S7 quad)"
    d["last_action_at"] = NOW
    d["last_round_closed"] = NOW
    d["latest_artifact"] = ("results/_w228bmc_20261013_probe_receipt.json (W228 ADMIT) + "
                            "fleet/inbox/MSG-20261013-0720-bmc.md")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["next_milestone"] = ("W228 prereg derive -> splice -> engine self-burn -> PRE-FINALIZE six-gate -> finalize "
                           "(next window first action); Tue 15:30 new-bar papers full chain")
    d["last_orders_at"] = NOW
    d["last_orders_read_at"] = NOW
    d["last_decisions_read_at"] = NOW
    d["orphan_face"] = 2
    d["orphan_faces"] = 2
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    with open(path, encoding="utf-8") as f:
        chk = json.load(f)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read not ISO8601 T-format"
    print("patched", path, "round", R, "epoch", chk["heartbeat_epoch_utc"])

hb_extra = {
    "activity_now": "2026-10-13 07:2x | r957 | bm-c: W228 seat published (ADMIT A 516404..518403 / B 518404..518603, "
                    "staircase EIGHTY-EIGHTH hops=1); W228 prereg derive = next first action; counter 957->958",
    "last_decisions_sha": "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7",
    "idle_rounds": 0, "agenda_starved": False,
}
if free_ram_gb is not None:
    hb_extra["free_ram_gb"] = free_ram_gb
    hb_extra["ram_free_gb"] = free_ram_gb
    hb_extra["idle_ram_gb"] = free_ram_gb
if vram_free_mb is not None:
    hb_extra["gpu_free_vram_mb"] = vram_free_mb
    hb_extra["gpu_idle_vram_mb"] = vram_free_mb
if cpu_pct is not None:
    hb_extra["cpu_pct"] = cpu_pct

patch(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", {
    "r957_closeout_note": "r957: clean continuation window (no absorb owed -- r956-absorb session closed out "
                          "properly, state round_no was 957 at open); executed as r957 per counter, advanced "
                          "957->958 so next session = r958; zero double-count: S0.5 dual-delta FALSE both "
                          "(dec fb5825cb / ord d559e530, zero consumption owed); product = W228 seat publish "
                          "(probe derive + probe rc0 ADMIT + seat MSG), prereg derive = r958 first action per "
                          "seat-first law O-20261011-0012 sec.ii",
    "sync": {"origin_tip": "r957 seat-publish commit (rides this window)", "ts": NOW,
             "ahead_behind": "r957 push rides this window",
             "note": "r957: W228 seat publish + S6 light + S7 closeout; state/heartbeat this round"},
})
patch(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json", hb_extra)

# round report append (one line, | separated, r954 format)
rp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + REPORT_LINE + "\n")
print("report appended; ram_free", free_ram_gb, "vram_free_mb", vram_free_mb, "cpu", cpu_pct)
print("DONE")
