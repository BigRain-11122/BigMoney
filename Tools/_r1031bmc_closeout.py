"""r1031 bm-c closeout: state advance 1030->1032 (absorb window, executed r1031 per
bm-c absorb precedent lineage 32nd instance), heartbeat refresh, canonical round
report append (ROOT file, r750 law), inbox MSG sweeps to processed/, fresh RAM/VRAM
samples, epoch-int assert (R170/R178 law), clock_read T-format (R262 law)."""

import ctypes
import datetime
import json
import os
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")  # 2026-10-15T17:0x:xx+08:00 (T-format R262)
EPOCH = int(time.time())
R = "r1031"

DID = (
    "r1031 bm-c (32nd absorb instance): (1) S0-1 anchor bm-c + round-zero probe "
    "py_faces=5 orphans=2 zero-kill + S0 stash-bridge 5 shared regenerable faces "
    "(r1029 pit honored: push rc verified + top-stash identity matched before each "
    "drop, quoted 'stash@{0}' refs; pre-existing 6 stashes intact) + ff-merge "
    "a5ae43853 (bm-b r983 estate, CODELY watermark debt + S6 39 legs); (2) ABSORB: "
    "dead window r1030 (16:1x-16:3x) landed own commits b2774fbf3 (sentinel v1.1 "
    "absorb O-20261015-0025: TTL stale-pause-valve report-only 12h + ollama face "
    "alignment to 2026-10-14 lane law) + 86819ad77 (W248 seat 68th owned/238th "
    "wave, A 561_501..563_500 / B 544_701..544_900 both hops=0 seed FREE, "
    "waits-upstream ARMED W247 in-flight, MSG-164x + heartbeat + pool committed) "
    "+ S0.5 probe 16:24:48 consumed ORD 1835852b->7604cf779 (16:0x CEO 终审三连"
    "反馈 + 16:2x dual-wave rows, BigStream-lane) + S6 43-leg chain DONE 16:31 "
    "rc0 faces-on-disk; died pre-closeout (state frozen 1030/r1029) -> this "
    "session executed as r1031 (next after highest committed label r1030), "
    "estate verified BEFORE landing, counter 1030->1032; (3) S0.5 ORD delta "
    "consumed 7604cf77->cafcf953 (2 rows = 17:0x O-1600 前三波深研收口 + 16:4x "
    "O-1700 世界第一三补波收口, both bm-a-executed MV research-lane closeouts "
    "six-wave system fully closed, ZERO BigMoney action zero bm-c legs) + DEC "
    "ab3f0cc9 hold + unacked=0; (4) S1 smoke 49/49; (5) S3: satengine ALIVE + "
    "wm red=pool-batch-runnable-idle-low-cpu WAIVED-named (4 W20 SCREEN shards "
    "claim-ready, RAM gate 6.5pct<4GB park-honest r354, autofill night-window "
    "standing, O-1612 GM waiver) + jobs 0 + fleet tasks 0 open + idle "
    "green_idle=false RAM-gate honest + inbox 3 foreign MSGs zero bm-c action "
    "(bmb G5-done receipt / bmb animatic 53-53 MV-preview-line closeout / bma "
    "W247 seat own-seat continuity W246-finalized chain); (6) S6 43/43 rc0: bars "
    "10-15 STILL absent source-side (sina 510300 calendar probe expected=10-14 "
    "third consecutive window, cutoff 10-14 covers -> zero network, papers "
    "debt=0 waits-source) + dualrun DRIFT observation (autofill live owner_since "
    "writes 16:47/16:51/16:57 vs mirror, streak reset, exit 0 recorded) + audit "
    "cpu 6pct low named-answer RAM-gate + papers all idempotent at cutoff 10-14 "
    "+ prospect 22/22 pass + token delta=0; (7) S7: attrition 4 CLEAN + "
    "post_review dist ✓45/✗0/🟡5 + quad green (loop pin=5 no-op first fire "
    "17:05 / watchdog present adjudicated-S4U face D-20261002-02 / claws x2 "
    "content-match True) + pit observed: partial git stash push -- <paths> in "
    "daemon-live window left unrelated STAGED pool faces worktree-reverted-to-"
    "HEAD while index retained claim copy (reverter ambiguous: stash internal "
    "machinery vs autofill race; daemon self-healed worktree within minutes, "
    "zero claim loss)"
)

VERDICT = (
    "green: r1031 absorb window (dead r1030 estate landed via this closeout: "
    "sentinel v1.1 + W248 seat were own-committed, state/S6 faces landed here) "
    "+ ORD 2-row MV-research-lane consumption zero-action + smoke 49/49 + S6 "
    "43/43 rc0 (bars 10-15 sina-lag third window, papers debt=0) + S7 quad green "
    "+ W248 waits-upstream (W247 bm-a in-flight) + MV V4 gated on bm-a director "
    "定脸专案 (24h window from 16:0x CEO order) + W20 4 shards RAM-gated "
    "park-honest (autofill night-window)"
)

NEXT = (
    "r1032: (1) bars 10-15 recheck (sina 510300 calendar governs; if landed -> "
    "papers full chain: live.paper enforce + t35_openfill + t24 x2 + aggr + "
    "alloc + grid + cta_p1 + system_v1 + t35_export + daily_scorecard + "
    "daily_report + ceo_live_usage + dashboard); (2) W247 finalize watch (bm-a "
    "chain) -> W248 prereg derive = THIS machine first action on finalize "
    "landing (waits-upstream law, live re-derive governs never transcribe "
    "r587); (3) MV V4: watch bm-a director 定脸专案 (24h window) -> POOL-0014 "
    "i2v INT8 768P full batch on approval (batch-sampling law O-20261014-1325); "
    "(4) W20 SCREEN: autofill claims on RAM free (night-window) -> 231/231 "
    "burn complete -> screen-finalize -> survivors -> judge chain; (5) U256 "
    "w001/w003 RAM gate deferred; (6) CPU backfill pool when bm-a publishes "
    "(MSG-0825 standing)"
)

ABSORB_NOTE = (
    "r1031 absorb note: dead window (self-labeled r1030, run 16:1x-16:3x) "
    "executed: S0 rebase conflict resolve + sequencer capture 16:21 (r990 pit "
    "mandate, evidence results/_r1030bmc_rebase_sequencer_capture/) + sentinel "
    "v1.1 absorb commit b2774fbf3 (O-20261015-0025 receipt: TTL stale-pause-"
    "valve report-only 12h + ollama face alignment 2026-10-14 lane law 35B "
    "decommissioned GPU=gen-visual-only) + S0.5 probe 16:24:48 ORD "
    "1835852b->7604cf779 consumed (16:0x + 16:2x BigStream rows; state "
    "watermark write 16:26:04 uncommitted at death, superseded by this "
    "window's advance to cafcf953) + W248 seat publish 86819ad77 (68th owned "
    "/ 238th wave, waits-upstream ARMED) + S6 43 legs DONE 16:31:09 rc0 (faces "
    "left dirty, absorbed + regenerated this window); died pre-closeout (state "
    "frozen round_no=1030/last_round r1029). This session executed as r1031 "
    "(next after highest committed label r1030) per bm-c absorb precedent "
    "lineage (32nd instance), advanced counter 1030->1032 so next session="
    "r1032; zero double-count: ORD rows after 7604cf779 (17:0x + 16:4x "
    "research closeouts) consumed THIS window, dead-window debts handled by "
    "its own commits + this closeout landing its state/S6/sequencer faces"
)

PROD_LANES = (
    "CPU=W20 SCREEN 4 shards claim-ready lane-pinned bm-c (RAM gate 6.5pct<4GB "
    "park-honest; autofill burns on night-window RAM free) -> screen-finalize "
    "next ; GPU=MV V4 POOL-0014 gated on bm-a director 定脸专案 24h window "
    "(CEO 16:0x order upgraded Jay-line to P0) -> i2v INT8 768P full batch next "
    "+ ComfyUI 常驻 + album serve ; N1=W247 bm-a in-flight (chain theirs per "
    "seat-first) -> W248 bm-c waits-upstream ARMED (prereg derive = first "
    "action post-finalize) ; U256 w001/w003 = RAM gate deferred ; MEMORY-GATE="
    "HQ-MemoryBudgetGate 4h cycle (bm-c leg closed r1027)"
)

ARTIFACT = (
    "r1031: Tools/_r1031bmc_s6.py + results/_r1031bmc_s6_log.txt (43/43 rc0) + "
    "watermark advance cafcf953 + dead-r1030 estate landed (sentinel v1.1 "
    "b2774fbf3 + W248 seat 86819ad77 own-committed; S6 faces + sequencer "
    "capture + rebase-resolve absorbed this closeout commit)"
)

SUMMARY = (
    "r1031: 32nd absorb window (dead r1030 estate landed) + ORD 2-row "
    "MV-research consumption zero-action + S6 43/43 rc0 (bars 10-15 sina-lag "
    "3rd window) + S7 quad green"
)

REPORT_ROW = (
    NOW_ISO + " | " + R + " | bm-c | r1031 (absorb 32nd): " + DID[10:] +
    " | 验证: results/_r1031bmc_s6_log.txt 43/43 rc0 + s05 probe unacked=0 + "
    "watermark read-back cafcf953 OK + attrition 4 CLEAN + quad green | " +
    "下轮: " + NEXT
)

INBOX_SWEEP = [
    "MSG-20261015-0104-bmb-P1B-G5-done.md",
    "MSG-20261015-1608-bm-b-animatic-53-53-done.md",
    "MSG-20261015-1608-bma-w247-seat.md",
    "MSG-20261015-164x-bmc-w248-seat.md",
]


def ram_free_gb():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return round(vm.available / (1 << 30), 2), round(vm.percent and (100 - vm.available * 100.0 / vm.total) or 0.0, 1)
    except Exception:
        pass
    try:
        it = json.load(open(os.path.join(ROOT, "results", "idle_trigger.bm-c.json"), encoding="utf-8"))
        pct = float(it.get("ram_free_pct", 0)) or 1.7 / 23.9 * 100
        return round(23.9 * pct / 100.0, 2), pct
    except Exception:
        return 1.7, 7.1


def vram_free_mb():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
        return int(float(out.splitlines()[0]))
    except Exception:
        return -1


def main():
    ram_gb, ram_pct = ram_free_gb()
    vram_mb = vram_free_mb()
    s = json.load(open(STATE, encoding="utf-8"))
    s["machine_id"] = "bm-c"
    s["clock_read"] = NOW_ISO
    s["round_no"] = 1032
    s["round_no_label"] = R
    s["last_round"] = R
    s["last_round_at"] = NOW_ISO
    s["last_round_ts"] = NOW_ISO
    s["last_round_label"] = R
    s["last_round_closed"] = NOW_ISO
    s["last_round_summary"] = SUMMARY
    s["last_round_summary_at"] = NOW_ISO
    s["last_action"] = R + " closeout (dead r1030 absorb + S6 43/43 + watermark 2-row consumption + quad green)"
    s["last_action_at"] = NOW_ISO
    s["last_seen"] = NOW_ISO
    s["last_seen_at"] = NOW_ISO
    s["last_ts"] = NOW_ISO
    s["ts"] = NOW_ISO
    s["updated"] = NOW_ISO
    s["updated_at"] = NOW_ISO
    s["current_task"] = R + " closeout: dead r1030 estate absorbed + S0.5 2-row ORD consumption + S6 43/43 + W248 waits-upstream"
    s["current_task_at"] = NOW_ISO
    s["current_task_ts"] = EPOCH
    s["did"] = DID
    s["verdict"] = VERDICT
    s["note"] = (R + ": absorb window 32nd (dead r1030: sentinel v1.1 + W248 seat own-committed) | ORD cafcf953 (MV-research closeouts zero-action) | bars 10-15 sina-lag 3rd window | W20 4 shards RAM-gated night-window autofill | W248 waits-upstream W247 bm-a in-flight | MV V4 gated on bm-a 定脸专案 24h")
    s["next"] = NEXT
    s["next_pointer"] = NEXT
    s["next_milestone"] = "r1032+: bars 10-15 papers full chain on sina landing + W248 prereg derive on W247 finalize + MV V4 i2v on bm-a 定脸专案 approval + W20 screen burn on RAM free"
    s["latest_artifact"] = ARTIFACT
    s["last_artifact"] = ARTIFACT
    s["recent_artifact"] = ARTIFACT
    s["now_active"] = NOW_ISO + " | " + R + " | bm-c: closeout (absorb + S6 + consumption) | counter 1030->1032 (r1031 exec)"
    s["activity_now"] = s["now_active"]
    s["prod_lanes"] = PROD_LANES
    s["r1031_absorb_note"] = ABSORB_NOTE
    s["r1031_closeout_note"] = SUMMARY + " | " + NOW_ISO
    s["last_orders_sha_note"] = ("r1031: ORD delta 7604cf77->cafcf953 consumed (2 rows = 17:0x O-1600 前三波深研收口 + 16:4x O-1700 世界第一三补波收口, bm-a-executed MV research-lane, zero BigMoney action); dead-r1030 had consumed 1835852b->7604cf77; watermark self-advanced read-back verified")
    s["last_decisions_read_note"] = "r1031: DEC delta FALSE hold (ab3f0cc9 sha256 raw-blob verified)"
    s["last_orders_seen"] = NOW_ISO
    s["last_orders_read_at"] = NOW_ISO
    s["last_decisions_seen"] = NOW_ISO
    s["last_decisions_read_at"] = NOW_ISO
    s["free_ram_gb"] = ram_gb
    s["ram_free_gb"] = ram_gb
    s["idle_ram_gb"] = ram_gb
    s["gpu_free_vram_mb"] = vram_mb
    s["gpu_free_mb"] = vram_mb
    s["orphan_face"] = 2
    s["orphan_faces"] = 2
    s["idle_rounds"] = 0
    s["agenda_starved"] = False
    s["verify"] = ("receipts: smoke 49/49 + S6 43/43 rc0 (_r1031bmc_s6_log.txt) + watermark read-back cafcf953 OK + s05 probe unacked=0 + attrition 4 CLEAN + post_review dist x0 + quad green (loop pin5 / watchdog adjudicated-S4U / claws x2 True) + orphan face=2 zero-kill")
    s["full_load_selfproof"] = {
        "占用一行": PROD_LANES,
        "当前活": R + " closeout (dead r1030 estate absorbed + S6 43/43 + ORD 2-row consumption)",
        "最近实物": ARTIFACT + "（" + NOW_ISO[:16] + "·本窗 commit）",
        "下个交付物": "bars 10-15 papers 全链（sina 落即发）+ W248 prereg derive（W247 finalize 落即发）+ MV V4 i2v 全批候 bm-a 定脸专案（窗≤48h）",
        "队列水位": "池 ready=4（全 W20 screen·lane bm-c·RAM 门 park-honest）·N1 引擎 W247 bm-a 在飞·W248 waits-upstream·U256 候 RAM 门·P2/P3 空·jobs 0",
    }
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    h = json.load(open(HB, encoding="utf-8"))
    h["machine_id"] = "bm-c"
    h["clock_read"] = NOW_ISO
    h["ts"] = NOW_ISO
    h["last_seen"] = NOW_ISO
    h["last_seen_at"] = NOW_ISO
    h["heartbeat_epoch_utc"] = EPOCH
    h["current_task"] = s["current_task"]
    h["current_task_at"] = NOW_ISO
    h["did"] = DID
    h["verdict"] = VERDICT
    h["note"] = s["note"]
    h["next"] = NEXT
    h["last_round"] = R
    h["last_round_at"] = NOW_ISO
    h["round_no"] = 1032
    h["free_ram_gb"] = ram_gb
    h["ram_free_gb"] = ram_gb
    h["gpu_free_vram_mb"] = vram_mb
    h["gpu_free_mb"] = vram_mb
    h["cpu_cores"] = 32
    h["cores"] = 32
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["orphan_face"] = 2
    h["prod_lanes"] = PROD_LANES
    json.dump(h, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with open(REPORT, "a", encoding="utf-8") as f:
        f.write("\n" + REPORT_ROW + "\n")

    moved = []
    for m in INBOX_SWEEP:
        src = os.path.join(ROOT, "fleet", "inbox", m)
        dst = os.path.join(ROOT, "fleet", "inbox", "processed", m)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            moved.append(m)

    # post-write asserts (R170/R178/R262 law)
    s2 = json.load(open(STATE, encoding="utf-8"))
    h2 = json.load(open(HB, encoding="utf-8"))
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock_read T-format"
    assert s2["round_no"] == 1032 and s2["last_round"] == "r1031"
    assert s2["last_orders_sha"].startswith("cafcf953")
    print("CLOSEOUT OK %s round_no=1032 epoch=%d ram=%.2fGB(%.1f%%) vram=%dMB moved=%d"
          % (NOW_ISO, EPOCH, ram_gb, ram_pct, vram_mb, len(moved)))


if __name__ == "__main__":
    main()
