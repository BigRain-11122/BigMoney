# -*- coding: utf-8 -*-
"""r1124 bm-c closeout: state counter 1124->1125 + heartbeat + round-report row.
EOL-preserving (r1029 law), epoch int asserted (R170/R178), clock_read T-form
(R262). Zero ledger/marks writes on the research faces."""
import ctypes
import datetime
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def sample_ram_gb():
    class MEMSTAT(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPage", ctypes.c_ulonglong), ("ullAvailPage", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEMSTAT()
    m.dwLength = ctypes.sizeof(MEMSTAT)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1024 ** 3), 2), round(m.ullTotalPhys / (1024 ** 3), 2), round(100 - m.dwMemoryLoad, 1)


def sample_gpu():
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free,utilization.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, creationflags=CNW)
        tot, used, free, util = [x.strip() for x in p.stdout.strip().split("\n")[0].split(",")]
        return int(tot), int(used), int(free), float(util)
    except Exception:
        return None


def sample_cpu():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=2), 1)
    except Exception:
        return None


def load_json(path):
    raw = io.open(path, "rb").read()
    eol = "\r\n" if b"\r\n" in raw[:4000] else "\n"
    return json.loads(raw.decode("utf-8")), eol


def save_json(path, obj, eol):
    txt = json.dumps(obj, indent=1, ensure_ascii=False)
    if eol == "\r\n":
        txt = txt.replace("\n", "\r\n")
    io.open(path, "w", encoding="utf-8", newline="").write(txt)


ram_free, ram_total, ram_idle_pct = sample_ram_gb()
gpu = sample_gpu()
cpu = sample_cpu()

DID = ("r1124: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 resident_servers=1 zero-kill "
       "(ComfyUI listener legal) + S0 fetch behind=0 HEAD==origin df00a34e6f clean open (pull --rebase refused on 2 own "
       "post-commit estate faces = r1123-tail heartbeat mirror + re-probe, absorbed this closeout); zero absorb owed "
       "(r1123 closed clean 19:41:26: S7-tail consumed the 19:35 CEO 机队 B/C 满负荷执行令 O-20261019-1935 with "
       "receipt _r1123bmc_ord_judgment.json s7_tail section, adjudicated zero-new-bm-c-action beyond standing chain "
       "continuation -- THIS window = the demanded output); (2) S0.5 dual-delta FALSE both scans (opening estate probe "
       "19:39:05/19:40:48 + S7 tail re-probe 20:09; ord 4f2a5c3b / dec 60a98a02 hold; unacked=0); (3) S1 smoke 49/49; "
       "(4) P0 PRODUCT = W279 CYCLE COMPLETE one-window per r1123 next_pointer: gate-clone builder "
       "_r1124bmc_build_gate_clones.py canon-clone of _r1118bmc_build_gate_clones.py (90 needles all-count-asserted "
       "first-try CLEAN-AT-BIRTH zero heals; W278 anchors live-read n1_w278_results.json machine-verified [mu "
       "-0.09278575748129675 / sigma 0.24505493584785207 / a_p95 0.2844 / line_merged@609,520 1.1969 / se_mu 0.000314 "
       "/ klift -0.0002 / ledger 1,035,935 / K 609,520]; SPLICE located by message grep = 3810f4a7ac2ece994246cac557c901511bab5121 "
       "landed [authored 61a65dd55d mid-window rebase face, next_pointer prophecy confirmed]) -> sixgate PRE-FINALIZE "
       "ALL PASS 42nd consecutive (results/_r1124bmc_w279_sixgate.json: row_faces 5/5 [a_seed_base_629101 / "
       "b_exit_seed_base_631101 / n1_w279 / n1_w279_results / engine_owner bm-c], boundary W278 kept [626901+628901 in "
       "W278 seg], setwave 279:1/278:0/277:0 whole-file counts 1/1/1, shards 12/12 >100KB, banned ADMIT rc0, pf/n1 "
       "selftest rc0, clean_state_ok + CR-normalized worktree==landed @ 3810f4a7ac + pf diff-empty, gate0.5 upstream "
       "W278 ledger 1,035,935/K=609,520 EXACT match vs freeze receipt w278_upstream face; GBK reader-thread noise on "
       "one selftest capture = known pit-encoding face zero impact) -> finalize one-pass ledger 1,035,935+2,200="
       "1,038,135 EXACT / K 609,520+2,200=611,720 EXACT (w279-only mu -0.1033/sigma 0.2464 K=2,200; merged mu "
       "-0.09282362698620283/sigma 0.24506025197871714; K-lift +0.0000; n_eff held 1,035,935; product "
       "results/perpetual_faces/n1_w279_results.json landed) -> fivekeys 6/6 ALL PASS (_r1124bmc_w279_fivekeys.py; "
       "key1 w279-vs-merged gap 0.0104919 / key1b merged-vs-W278-key 3.79e-05 chain-tight / key2 sigma rel 2.17e-05 / "
       "key3 A p95 0.2844->0.3104 delta +0.026 double-direction in-band / key4 K-lift +0.0000 held-flat / key5 se_mu "
       "0.000313<=0.000314 narrowing-resumed; ledger+K identities EXACT) -> sec.7/8 backfill zero-placeholder "
       "(_r1124bmc_w279_sec78_backfill.py canon-clone of _r1119bmc_w278_sec78_backfill.py; NEW7/NEW8 all "
       "machine-read; frozen PRE-backfill sha16 c2fc7c34d0e41a68 per r1049/r1052; placeholders remaining 0); "
       "(5) W280 SEAT PUBLISHED origin f96272d8b9 pushed behind=0: machine roller _r1124bmc_roll_w280_probe.py (E63 "
       "canon-clone one-generation shift of the _r1119bmc_build_w279_probe.py lineage; arithmetic +2,200 token-map "
       "extension [band/ledger/K chains W279->W280: 629_101->631_301 / 631_100->633_300 / 631_101->633_301 / "
       "631_300->633_500 / 630_900->633_100 / 633_100->635_300 / 631_301->633_501 / 631_500->633_700 / "
       "1_035_935->1_038_135 / 609_520->611_720; WMAP extended W281->W282/W282->W283; ORDM extended "
       "TWENTY-NINTH->THIRTIETH; BARE extended 269/279/280/97] + 21 count-asserted context patches; preflight 53/53 "
       "vs on-disk W279 probe; ZERO heals first-try) -> builder _r1124bmc_build_w280_probe.py (53 needles "
       "all-count-asserted + MUST all-green, 34,202B sha16 264e55bc9d27daab) -> probe _w280bmc_20261019_probe.py "
       "rc0 ADMIT first-try on the post-W279-REGISTERED+FINALIZED universe: leg0 277 rows chain-relation "
       "W277->W278->W279 ledger 1,033,735->1,035,935->1,038,135 (+2,200/+2,200 EXACT) K 607,320->609,520->611,720 "
       "(+2,200/+2,200 EXACT) owner=269 -> W280=270th wave bm-c 99th own wave candidate; leg0.5 vacancy held + zero "
       "W281/W282 skip-claims + waits-upstream=NONE; leg1 live walk A (631301,633300) hops=1 [naive 631101..633100 "
       "refused at registered W279 B 631101..631300] TWENTY-NINTH consecutive A-hop / B (633301,633500) hops=1 [naive "
       "631301..631500 refused inside own-A first-clean window] THIRTIETH consecutive above-own-A == W279 freeze "
       "receipt downstream_seat projection confirmed live r587; leg2 seed_admit FREE x2 base=631301 span=2000 + "
       "base=633301 span=200; leg3 origin vacancy four-check TRUE; leg4 W281+ naive A 633301..635300 / naive B "
       "633501..633700 == arithmetic-chain prediction; seat MSG-20261019-200x-bmc-w280-seat.md @ALL landed "
       "fleet/inbox/; push race: origin advanced 2 (bm-b r1033 postscript chain 422b68de01) mid-push -> cycle estate "
       "commit first -> pull --rebase clean 2/2 -> PUSH LANDED f96272d8b9 (seat) + 6bdbdb9a07 (cycle) behind=0/ahead=0 "
       "fetch-verified; (6) S6 light 10/10 rc0 (driver _r1124bmc_s6_light.py r1123 canon-clone: dualrun ZERO-DRIFT "
       "streak 51 [461] / compute_audit rc0 / py_watermark rc0 / update_daily 0 rows cutoff 10-16 [10-19 bar "
       "sina-lag ~20:4x honest, papers debt=0, full-chain re-arm = the window that sees the bar] / market_regime rc0 / "
       "market_clock rc0 / fund_premium rc0 [bm-c lane post-15:30 snapshot] / b_layer all_pass / REPORT-2026-10-19 "
       "faces=5 / token delta=0 L2 legs 0 today); (7) S7: orphan face=0 zero-kill + idle --worked rc0 "
       "idle_rounds=0 + attrition 4 CLEAN + watermark red=false healthy [next_pick=claimed moneyflow-IC parked "
       "source-blocked bm-a lane standing] + quad green (loop pin=5 no-op first fire 20:15 + watchdog first fire "
       "20:12 [S4U XML flip access-denied = adjudicated default-principal standing face per D-20261002-02] + "
       "precommit claw + prepush claw installed LF-normalized) + D-19 tail dual FALSE (ord 4f2a5c3b / dec 60a98a02 "
       "hold, zero mid-round arrivals); counter 1124->1125 so next session = r1125")

VERIFY = ("gate-clone builder 90 needles first-try + sixgate verdict ALL PASS rc0 (ledger_pre match + setwave gates "
          "green + shards 12/12) + finalize rc0 ledger/K EXACT (1,038,135/611,720) + fivekeys rc0 6/6 "
          "(ledger_identity.exact=true + merged_k_identity.exact=true) + sec78 backfill placeholders=0 + roller "
          "preflight 53/53 + patches 21/21 count-asserted + builder 53/53 + probe ADMIT rc0 (bands 631301-633300 / "
          "633301-633500 live-walk measured) + seat+cycle commits PUSHED behind=0/ahead=0 (422b68de01..6bdbdb9a07 "
          "ls-remote verified) + smoke 49/49 + S6 10/10 rc0 + attrition CLEAN + D-19 dual FALSE both scans + quad "
          "green + 本地未达 origin commit 数=0")

NEXT = ("r1125 FIRST ACTIONS: (1) W280 prereg derive = P0 first action (post-W279 universe; r1096 honest-split law; "
        "anchors machine-frozen: frozen W279 prereg template face @ origin ba5c725b42 blob sha256_16 c2fc7c34d0e41a68 "
        "PRE-backfill face per r1049/r1052 [HEAD post-backfill twin disclosed NOT used]; W279 actuals live-read from "
        "results/_r1124bmc_w279_fivekeys.json [merged mu -0.09282362698620283 / sigma 0.24506025197871714 / "
        "se_mu@611,720 0.000313 / a_p95 0.3104 / line_merged@611,720 1.197 / K-lift +0.0000 / ledger 1,038,135 / "
        "K=611,720]; W280 seat bands A 631_301..633_300 / B 633_301..633_500 per seat receipt "
        "_w280bmc_20261019_probe_receipt.json verbatim in-gate; derive = E63 canon-clone of "
        "_w279bmc_prereg_derive.py bloodline); (2) 10-19 bar sina-lag ~20:4x -> update_daily re-arm when the bar "
        "lands -> papers full chain (live.paper enforce + t35_open_fill_verify + t24_prospect_paper + "
        "t24_prospect_promotion + aggressive_lab + grid_paper + t35_paper_export) = the window that sees the bar; "
        "(3) 5x HANDOVER duty = bm-c r1125 (due at the r1125 window); (4) NATS heartbeat task standing")

VERDICT = ("green r1124 product window: W279 CYCLE COMPLETE (sixgate 42nd PRE-FINALIZE ALL PASS + finalize one-pass "
           "1,038,135/611,720 EXACT + fivekeys 6/6 + sec78 zero-placeholder) + W280 SEAT published f96272d8b9 (A "
           "631_301..633_300 TWENTY-NINTH A-hop / B 633_301..633_500 THIRTIETH above-own-A, probe ADMIT first-try, "
           "roller zero-heal first-try) + S0.5 dual FALSE both scans + S6 10/10 + smoke 49/49 + attrition CLEAN + "
           "quad green")

ARTIFACT = ("results/perpetual_faces/n1_w279_results.json + results/_r1124bmc_w279_sixgate.json + "
            "results/_r1124bmc_w279_fivekeys.json + research/PERPETUAL_N1_W279_PREREG.md (sec78 backfilled) + "
            "results/_w280bmc_20261019_probe.py + results/_w280bmc_20261019_probe_receipt.json + "
            "fleet/inbox/MSG-20261019-200x-bmc-w280-seat.md @ origin f96272d8b9+6bdbdb9a07")

THREE = {
    "占用一行": ("CPU=W279 cycle complete one-window (sixgate+finalize+fivekeys+sec78) + W280 seat published + S6 "
                 "10/10; GPU=idle day (resident ComfyUI listener only); NATS 心跳任务常设在役"),
    "最近实物": ARTIFACT + " @ " + NOW_ISO,
    "下个里程碑": ("W280 prereg derive+freeze (r1125 FIRST ACTION, window <=30min after open); 10-19 bar papers "
                  "re-arm ~20:4x; 5x HANDOVER row due r1125"),
}

CLOSEOUT_NOTE = ("r1124: clean continuation product window (state round_no=1124 at open, executed r1124, advanced "
                 "1124->1125 so next=r1125); zero absorb owed (r1123 closed clean 19:41:26 incl S7-tail 满负荷令 "
                 "consumption + riders); zero double-count: S0.5 dual FALSE both scans (opening estate + S7 tail "
                 "re-probe; ord 4f2a5c3b / dec 60a98a02 hold, unacked=0); products = W279 CYCLE COMPLETE "
                 "(sixgate 42nd + finalize 1,038,135/611,720 EXACT + fivekeys 6/6 + sec78 zero-placeholder) + "
                 "W280 SEAT published (probe ADMIT first-try A 631_301..633_300 / B 633_301..633_500; roller "
                 "arithmetic +2,200 token-map extension + 21 patches zero-heal first-try); splice-const face "
                 "healed-by-evidence: next_pointer's 61a65dd55d = pre-rebase authored sha, landed = 3810f4a7ac "
                 "located by message grep per the next_pointer law; push race bm-b r1033 absorbed via "
                 "commit-estate-first + pull --rebase clean; S6 10/10 (bars 10-19 sina-lag honest 0 rows cutoff "
                 "10-16, papers debt=0); smoke 49/49 + attrition CLEAN + quad green (watchdog S4U flip = "
                 "adjudicated default-principal standing face); orphan face=0 zero-kill")

# ---- state ----
SP = os.path.join(ROOT, "state-bm-c.json")
st, eol = load_json(SP)
st["round_no"] = 1125
st["round_no_label"] = "r1124 closeout -> counter 1125"
st["last_round"] = "r1124"
st["last_round_at"] = NOW_ISO
st["last_round_closed"] = NOW_ISO
st["last_round_closed_at"] = NOW_ISO
st["last_round_ts"] = NOW_ISO
st["last_round_label"] = "r1124"
st["last_round_summary"] = VERDICT
st["last_round_summary_at"] = NOW_ISO
st["activity_now"] = NOW_ISO
st["now_active"] = NOW_ISO
st["updated"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["ts"] = NOW_ISO
st["clock_read"] = NOW_ISO
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW_ISO
st["last_seen_at"] = NOW_ISO
st["last_ts"] = NOW_ISO
st["last_action"] = "r1124 closeout"
st["last_action_at"] = NOW_ISO
st["current_task"] = ("r1125 FIRST ACTION = W280 prereg derive (post-W279 universe, anchors machine-frozen) + "
                      "10-19 bar papers re-arm when bars land + 5x HANDOVER duty")
st["current_task_at"] = NOW_ISO
st["current_task_ts"] = EPOCH
st["did"] = DID
st["verify"] = VERIFY
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = THREE["下个里程碑"]
st["verdict"] = VERDICT
st["last_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["latest_artifact"] = ARTIFACT
st["last_artifact_at"] = NOW_ISO
st["last_pulled_at"] = NOW_ISO
st["last_run_at"] = NOW_ISO
st["full_load_selfproof"] = THREE
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["ram_critical_face"] = "none (loop CPU-only, GPU idle day)"
st["ram_free_gb"] = ram_free
st["free_ram_gb"] = ram_free
st["idle_ram_gb"] = ram_free
st["total_ram_gb"] = ram_total
st["cpu_idle_pct"] = ram_idle_pct
if cpu is not None:
    st["cpu_pct"] = cpu
    st["cpu_util_pct"] = cpu
    st["cpu_idle_pct"] = round(100 - cpu, 1)
if gpu is not None:
    tot, used, free, util = gpu
    st["gpu_total_vram_mib"] = tot
    st["gpu_used_vram_mib"] = used
    st["gpu_free_vram_mib"] = free
    st["gpu_free_mb"] = free
    st["gpu_free_mib"] = free
    st["gpu_idle_mb"] = free
    st["gpu_idle_vram_mb"] = free
    st["gpu_idle_mib"] = free
    st["gpu_vram_free_mb"] = free
    st["gpu_free_vram_mb"] = free
    st["gpu_free_vram_gb"] = round(free / 1024, 2)
    st["gpu_util_pct"] = util
st["head_sha"] = "6bdbdb9a07 (r1124 cycle complete; W280 seat f96272d8b9 rides the same window; closeout rides this window)"
st["r1124_closeout_note"] = CLOSEOUT_NOTE
st["orders_ack_ts"] = NOW_ISO
st["orders_ack_receipt"] = ("r1124: dual FALSE both scans (opening estate probe 19:39/19:40 + S7 tail 20:09); ord "
                           "4f2a5c3b / dec 60a98a02 hold; unacked=0; the 19:35 CEO 机队 B/C 满负荷执行令 "
                           "O-20261019-1935 was consumed by the r1123 S7-tail with receipt "
                           "_r1123bmc_ord_judgment.json (zero new bm-c action beyond standing chain continuation; "
                           "THIS window landed the demanded output)")
assert isinstance(st["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
save_json(SP, st, eol)
print("state updated: round_no=1125, epoch=%d (int asserted), clock=%s" % (EPOCH, NOW_ISO))

# ---- heartbeat ----
HP = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb, eol2 = load_json(HP)
for k in ["activity_now", "now_active", "updated", "updated_at", "ts", "clock_read",
          "last_round_at", "last_round_closed", "last_round_closed_at", "last_seen",
          "last_seen_at", "last_ts", "last_action_at", "last_artifact_at", "current_task_at"]:
    hb[k] = NOW_ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_round"] = "r1124"
hb["last_round_label"] = "r1124"
hb["last_round_summary"] = VERDICT
hb["last_round_summary_at"] = NOW_ISO
hb["last_action"] = "r1124 closeout"
hb["current_task"] = st["current_task"]
hb["current_task_ts"] = EPOCH
hb["did"] = DID
hb["verify"] = VERIFY
hb["next"] = NEXT
hb["next_pointer"] = NEXT
hb["next_milestone"] = THREE["下个里程碑"]
hb["verdict"] = VERDICT
hb["last_artifact"] = ARTIFACT
hb["recent_artifact"] = ARTIFACT
hb["latest_artifact"] = ARTIFACT
hb["full_load_selfproof"] = THREE
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["ram_free_gb"] = ram_free
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["total_ram_gb"] = ram_total
hb["last_orders_read_at"] = NOW_ISO
hb["last_decisions_read_at"] = NOW_ISO
hb["orders_ack_ts"] = NOW_ISO
hb["health"] = "ok"
if gpu is not None:
    tot, used, free, util = gpu
    hb["gpu_free_mb"] = free
    hb["gpu_free_mib"] = free
    hb["gpu_idle_mb"] = free
    hb["gpu_idle_mib"] = free
    hb["gpu_used_vram_mib"] = used
    hb["gpu_total_vram_mib"] = tot
    hb["gpu_util_pct"] = util
if cpu is not None:
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["cpu_idle_pct"] = round(100 - cpu, 1)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
save_json(HP, hb, eol2)
print("heartbeat updated: epoch=%d int, ts=%s" % (EPOCH, NOW_ISO))

# ---- round report row ----
RP = os.path.join(ROOT, "round_reports-bm-c.md")
raw = io.open(RP, "rb").read()
eol3 = "\r\n" if b"\r\n" in raw[-2000:] else "\n"
row = (eol3 + NOW_ISO + "｜r1124｜W279 CYCLE COMPLETE one-window (gate-clone builder 90-needle first-try + sixgate "
       "42nd ALL PASS + finalize 1,038,135/611,720 EXACT + fivekeys 6/6 [key3 A p95 0.2844->0.3104 in-band / key5 "
       "se_mu 0.000313 narrowing] + sec78 zero-placeholder) + W280 SEAT published f96272d8b9 (roller 53/53 preflight "
       "+ 21 patches zero-heal first-try + probe ADMIT A 631_301..633_300 29th A-hop / B 633_301..633_500 30th "
       "above-own-A + seed FREE x2 + vacancy four-check + zero W281/W282 skip-claims)｜smoke 49/49 + S6 10/10 rc0 "
       "(bars 10-19 sina-lag honest, papers debt=0) + attrition CLEAN + D-19 dual FALSE both scans + quad green + "
       "本地未达 origin commit 数=0｜r1125 = W280 prereg derive FIRST ACTION + 10-19 bar papers re-arm + 5x "
       "HANDOVER duty")
io.open(RP, "a", encoding="utf-8", newline="").write(row)
print("round report row appended (eol=%r)" % eol3)
print("CLOSEOUT OK r1124 -> counter 1125")
