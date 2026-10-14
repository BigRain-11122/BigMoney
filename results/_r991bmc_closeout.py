# -*- coding: utf-8 -*-
"""r991 bm-c closeout: W239 seat publication closeout + ledger path-split 4th
instance heal (r749/r780/r985 family: r990 row ROOT-written by the dead
session's closeout script -> union verbatim into canonical, this script
writes CANONICAL path only) + state 991->992 + heartbeat + faces."""
import json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ORPH = os.path.join(ROOT, "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- 0) fresh machine sample ---------------------------------------------------
import psutil
ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
cpu_pct = psutil.cpu_percent(interval=2)
gpu_free_mib = gpu_total_mib = gpu_util = None
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20)
    parts = q.stdout.strip().splitlines()[0].split(",")
    gpu_free_mib, gpu_total_mib, gpu_util = int(parts[0]), int(parts[1]), int(parts[2])
except Exception:
    pass

# --- 1) ledger path-split heal: r990 row verbatim union -> canonical -----------
raw_orph = open(ORPH, "rb").read().decode("utf-8", errors="replace")
eol = "\r\n" if "\r\n" in raw_orph else "\n"
orph_lines = raw_orph.splitlines()
r990_rows = [ln for ln in orph_lines if "| r990 |" in ln]
assert len(r990_rows) == 1, f"heal failed: r990 rows found {len(r990_rows)} in ROOT file"
r990_row = r990_rows[0]
canon_raw = open(CANON, "rb").read().decode("utf-8", errors="replace")
canon_eol = "\r\n" if "\r\n" in canon_raw else "\n"
assert "| r990 |" not in canon_raw, "heal guard: r990 row ALREADY in canonical (double-union risk)"
assert "| r991 |" not in canon_raw, "heal guard: r991 row ALREADY in canonical"

r991_row = (
    f"{now_iso} | r991 | bm-c | W239 SEAT PUBLISHED=RESERVED (seat-first queue-depth supply per "
    "O-20261010-2350 sec.2 禁等上一波烧完才占下一席 + never-dry O-1819 + CPU standing-open "
    "O-20261013-2215; bm-c 66th owned / 229th engine wave candidate; A 542_501..544_500 hops=2 -- "
    "NEW FACE: first A window landing PAST prior-wave B tail+1, seed-driven double hop (W238 "
    "declared B band 540_404..540_603 + live SEED_REGISTRY 541500/542000 -> 542_001; seed 542_500 "
    "-> 542_501), W238 seat MSG leg4 anticipation machine-confirmed, never transcribed r587 / "
    "B 540_604..540_803 hops=0 seed-decoupled gap face (own-A hopped past the staircase base, B "
    "inherits prior-wave B tail+1; fc_b==fc_b_naive no own-A reservation jump); pre-seat probe "
    "_w239bmc_20261014 rc0 ADMIT: leg0 dual-state W238 receipt-face live (splice pending bm-a "
    "lane, registry-first fallback armed) + W237 registered+FINALIZED upstream face verified "
    "(r990: ledger 945,189/K=519,320 five-key ALL PASS _w237bmc_fivekey_receipt.json) + leg2 "
    "seed_admit_gate rc0 FREE x2 (A base=542501 span=2000 / B base=540604 span=200) + leg3 origin "
    "vacancy four-check green + leg4 W240+ projection (naive A 544_501..546_500 refused by seed "
    "545500 -> first-clean 545_501..547_500 hops=1; naive B 540_804..541_003 clean; W240 freezer "
    "MUST re-derive on post-W239 universe + reserve own-A when deriving B + NOT assume staircase "
    "A-base equality); W239 freeze waits-upstream W238 finalize = physical dependency (bm-a chain "
    "in flight post-0855-finalize); seat MSG-20261014-0914-bmc-w239-seat in this push) | smoke "
    "49/49 + S0.5 dual FALSE x2 (opening + S7 tail: ord 348eaf34 content-sha / dec 86187eff "
    "sha256 hold, unacked=0) + satengine ALIVE rc0 + S6 light (dualrun ZERO-DRIFT streak 51 [447 "
    "entries] + compute_audit FLAG supply_floor structural [ready 0<floor 3, answered-by-chain: "
    "W238 bm-a in-flight + this W239 seat] + py_watermark verdict py_low_board_clear legal "
    "[bars_present=false pre-15:30, daily_panel cutoff 10-13 fresh] + update_daily rc0 no-op "
    "cutoff 10-13 + market_regime rc0 + market_clock CALL-2026-10-13 ORANGE_COOL sleeves=4 + "
    "fund_premium no-op pre-15:30 bm-c lane + token delta=0 L2 legs 0) | red face P0 disposition: "
    "09:07:03/09:15:03 watermark_red red=true pool_batch=1 (TRIAL-LABOR-W19-GENERATE ready, "
    "prereg FROZEN bm-b r927) -> bm-c RAM-gated honest (free ~0.9G < shard gate; MV V3 GPU burn "
    "window protected O-20261014-0312 sec.2 zero touch) + bm-b claim-main lane burning -> "
    "09:15:24 probe pool drained (entry claimed) verdict py_low_board_clear = red face "
    "self-resolves next watchdog write; engine supply chain armed (W238 in-flight + W239 seated) "
    "| S7 quad: attrition 4 CLEAN (2 healed-shrink noted) + pin=5 no-op + watchdog re-registered "
    "+ claws x2 idempotent + idle declared worked idle_rounds=0 + LEDGER PATH-SPLIT 4th INSTANCE "
    "HEAL (r749/r780/r985 family): r990 row ROOT-write union'd verbatim into canonical this "
    "window, this closeout script writes CANONICAL path (r750 law) | next r992: 15:30 bars "
    "re-probe -> papers full chain (debt=0 per r985) + MF panel watch (bm-a ETA 09:2x passed -> "
    "recheck MF-IC-P1 S2 completion gate) + W238 finalize watch (bm-a chain) -> W239 freeze-prep "
    "same-window on landing per W239 bloodline (六门 PRE-FINALIZE 随 freeze 窗同窗预跑) + W19 pool "
    "RAM-gated watch | watermark: GREEN (red face transient resolved py_low_board_clear; supply "
    "chain W238 in-flight + W239 seated) | orphan face=2 zero-kill (py_faces=9; ComfyUI+c1011 "
    "MV-lane infra kept) | local-not-at-origin=N (closeout push rides this window, fetch-verify "
    "at r992 open)")

with open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(r990_row + canon_eol)
    f.write(r991_row + canon_eol)
ptr = (f"> [r991 ledger-heal pointer {time.strftime('%Y-%m-%d')}] r990 row above (ROOT-write 4th "
       "instance, r749/r780/r985 family) union'd verbatim into logs/iteration-loop/round_reports-bm-c.md "
       "this window; r991+ closeout writes CANONICAL path only (r750 law restored again)")
with open(ORPH, "a", encoding="utf-8", newline="") as f:
    f.write(ptr + eol)
print("heal: r990 row union'd verbatim -> canonical; r991 row written canonical; root pointer appended")

# --- 2) state update -----------------------------------------------------------
st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = 992
st["round_no_label"] = "r991"
st["loop_round"] = 991
st["last_round"] = "r991"
st["last_round_label"] = "r991"
st["clock_read"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_seen"] = now_iso
st["last_seen_at"] = now_iso
st["last_round_at"] = now_iso
st["last_round_closed"] = now_iso
st["last_round_ts"] = epoch
st["last_ts"] = epoch
st["current_task_ts"] = epoch
st["current_task_at"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["current_task"] = ("r991 closeout complete (W239 SEAT PUBLISHED: probe ADMIT + MSG-0914 + ledger "
                      "path-split 4th-instance heal); next: r992 wait-window faces (bars 15:30 / MF "
                      "panel recheck / W238 finalize watch -> W239 freeze-prep)")
st["now_active"] = f"2026-10-14 {time.strftime('%H:%M')} | r991 | bm-c: W239 SEAT PUBLISHED | counter 991->992"
st["activity_now"] = st["now_active"]
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["free_ram_gb"] = ram_free
st["ram_free_gb"] = ram_free
st["idle_ram_gb"] = ram_free
if gpu_free_mib is not None:
    st["gpu_free_vram_mib"] = gpu_free_mib
    st["gpu_free_vram_mib"] = gpu_free_mib
    st["gpu_free_vram_mb"] = gpu_free_mib
    st["gpu_total_vram_mib"] = gpu_total_mib
    st["gpu_used_vram_mib"] = gpu_total_mib - gpu_free_mib
    st["gpu_mem_used_mib"] = gpu_total_mib - gpu_free_mib
    st["gpu_util_pct"] = gpu_util
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_round_summary"] = ("r991: W239 SEAT PUBLISHED (229th wave cand, 66th owned; probe ADMIT A "
                            "542501..544500 seed-hop new face / B 540604..540803 seed-decoupled; gate "
                            "FREE x2; vacancy 4-check; MSG-0914) + smoke 49/49 + S0.5 dual FALSE x2 + "
                            "S6 light + red P0 disposition (W19 pool bm-b claimed, red self-resolved) "
                            "+ S7 quad + ledger heal 4th instance; counter 991->992")
st["last_round_summary_at"] = now_iso
st["last_action"] = "r991 closeout (W239 seat publication + ledger path-split heal + S6 light + S7 quad)"
st["last_action_at"] = now_iso
st["did"] = ("r991 (clean continuation window, state round_no=991 at open, executed r991, advanced "
             "991->992 so next=r992; zero absorb owed -- r990 closeout 2575e050c+pit 1f5f40b60 landed "
             "clean): (1) S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=2 zero-kill (ComfyUI "
             "8188 + c1011_album_serve = MV-lane infra kept, 刀2 read-only); S0 fetch 0/0 behind-0 "
             "(pull --rebase initial-refusal face = x11 daemon live-faces legit dirty, fetch-verified "
             "no rebase owed); (2) S0.5 dual-delta FALSE both scans (opening 09:01 probe + S7 tail "
             "re-run: ord 348eaf34 content-sha / dec 86187eff sha256 hold; unacked=0); (3) S1 smoke "
             "49/49; (4) S3: satengine ALIVE rc0 + jobs=0 + WM RED FACE P0 disposition (09:07/09:15 "
             "red=true pool_batch=1 W19-GENERATE -> RAM-gated honest 0.9G + MV V3 protected + bm-b "
             "claim-main -> 09:15:24 pool drained py_low_board_clear self-resolve) + PRODUCT = W239 "
             "SEAT PUBLICATION per seat-first never-dry law + r990 handoff: pre-seat probe "
             "_w239bmc_20261014_probe.py rc0 ADMIT (leg0 dual-state W238 receipt-face + W237 "
             "finalize anchors verified; leg1 A 542501..544500 hops=2 seed-hop NEW FACE past "
             "prior-B-tail+1 per W238 leg4 anticipation + B 540604..540803 hops=0 seed-decoupled; "
             "leg2 gate FREE x2; leg3 vacancy 4-check; leg4 W240+ projection seed 545500) + seat "
             "MSG-20261014-0914-bmc-w239-seat; (5) S6 light: dualrun ZERO-DRIFT streak 51 (447) + "
             "compute_audit FLAG supply_floor structural answered-by-chain (W238 bm-a in-flight + "
             "W239 seated) + py_watermark py_low_board_clear legal (bars pre-15:30) + update_daily "
             "rc0 no-op cutoff 10-13 + market_regime rc0 + market_clock ORANGE_COOL + fund_premium "
             "no-op bm-c lane + token delta=0; (6) S7 quad: attrition 4 CLEAN (2 healed) + pin=5 "
             "no-op + watchdog re-registered + claws x2 idempotent + idle --worked + LEDGER "
             "PATH-SPLIT 4th INSTANCE HEAL (r990 row ROOT-write union'd verbatim -> canonical; "
             "closeout script writes canonical per r750 law)")
st["verify"] = ("receipts: probe results/_w239bmc_20261014_probe_receipt.json verdict ADMIT + "
                "seed_admit_gate rc0 FREE x2 + origin vacancy 4-check + seat MSG "
                "fleet/inbox/MSG-20261014-0914-bmc-w239-seat.md + smoke 49/49 + dualrun streak 51 "
                "+ attrition 4 CLEAN + s05 dual FALSE x2 + orphan face=2; closeout push rides this "
                "window (fetch-verify at r992 open)")
st["verdict"] = ("green: W239 SEAT PUBLISHED (probe ADMIT all legs; supply chain W238 bm-a in-flight "
                 "+ W239 seated = never-dry depth-2) + smoke 49/49 + S0.5 dual FALSE x2 + S6 light "
                 "green (wm py_low_board_clear legal; audit FLAG answered-by-chain) + red face P0 "
                 "disposition closed (W19 pool claimed by bm-b, red self-resolved py_low_board_clear) "
                 "+ S7 quad green + ledger path-split healed 4th instance")
st["latest_artifact"] = ("W239 seat: results/_w239bmc_20261014_probe_receipt.json (ADMIT, A "
                         "542501..544500/B 540604..540803) + probe script + MSG-20261014-0914-bmc-w239-seat, "
                         "this closeout push 2026-10-14 09:2x")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next"] = ("r992: (1) 15:30 bars re-probe -> papers full chain when 10-14 bar lands (debt=0 per "
              "r985); (2) MF panel recheck (bm-a ETA ~09:2x passed -- if panel landed, MF-IC-P1 S2 "
              "completion gate check; else keep parked one-line); (3) W238 finalize watch (bm-a "
              "freeze-prep chain post-0855) -> W239 freeze-prep SAME-WINDOW on landing per W239 "
              "bloodline (prereg derive R33-style from committed lineage + five-face splice + 六门 "
              "PRE-FINALIZE 随 freeze 窗同窗预跑; gate0.5 selfcheck W238 row + queue_head probe at claim); "
              "(4) W19-GENERATE pool: RAM gate re-check before any bm-c shard claim (MV V3 window "
              "protected O-20261014-0312 sec.2)")
st["next_pointer"] = st["next"]
st["next_milestone"] = ("10-14 15:30 bars -> papers chain; W238 finalize (bm-a) -> W239 freeze-prep "
                        "bm-c same-window; MF-IC-P1 unpark on bm-a panel")
st["prod_lanes"] = ("CPU=N1 W237 CLOSED (r990 finalized 945,189/K=519,320); W238=bm-a chain in-flight "
                    "(freeze-prep post-0855-finalize); W239=bm-c SEATED 09:14 (freeze waits-upstream "
                    "W238 finalize, prereg derive = first action on landing per seat-first law); "
                    "MF-IC-P1: parked, bm-a panel rebuild watch; GPU=MV V3: burn window protected "
                    "per O-20261014-0312 sec.2 zero touch")
st["orders_ack_receipt"] = ("r991: zero unacked both scans (opening + S7 tail); group ORD/DEC "
                            "dual-delta FALSE both (ord 348eaf34 content-sha / dec 86187eff sha256 "
                            "hold); zero bm-c execution owed")
st["orders_ack_ts"] = now_iso
st["r991_closeout_note"] = ("r991: clean continuation window (state round_no=991 at open, executed "
                            "r991, advanced 991->992 so next=r992); zero absorb owed (r990 closeout "
                            "2575e050c + pit entry 1f5f40b60 landed clean); zero double-count: S0.5 "
                            "dual-delta FALSE both scans; product = W239 SEAT (probe ADMIT + MSG-0914); "
                            "ledger path-split 4th instance healed same-window (r990 row ROOT-write "
                            "union'd verbatim; canonical path restored)")
st["r991_absorb_note"] = ""
st["sync"] = {"origin_tip": "1f5f40b60 at open; fetch 0/0 behind-0",
              "ts": now_iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides this window)",
              "note": "r991: fetch 0/0 clean (x11 daemon live-faces legit dirty); W239 seat window"}
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- 3) heartbeat update --------------------------------------------------------
hb = json.load(open(HB, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["heartbeat_epoch_utc_type"] = "int (assert)"
hb["current_task"] = st["current_task"]
hb["current_task_at"] = now_iso
hb["current_task_ts"] = epoch
hb["now_active"] = st["now_active"]
hb["activity_now"] = st["now_active"]
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
hb["free_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
if gpu_free_mib is not None:
    hb["gpu_free_vram_mib"] = gpu_free_mib
    hb["gpu_free_vram_mb"] = gpu_free_mib
    hb["gpu_free_vram_gb"] = round(gpu_free_mib / 1024, 1)
    hb["gpu_total_vram_mib"] = gpu_total_mib
    hb["gpu_used_vram_mib"] = gpu_total_mib - gpu_free_mib
    hb["gpu_mem_used_mib"] = gpu_total_mib - gpu_free_mib
    hb["gpu_util_pct"] = gpu_util
hb["orphan_face"] = 2
hb["orphan_faces"] = 2
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["round_no"] = 992
hb["last_round"] = "r991"
hb["loop_round"] = 991
hb["last_round_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["last_round_summary"] = st["last_round_summary"]
hb["last_round_summary_at"] = now_iso
hb["last_action"] = st["last_action"]
hb["last_action_at"] = now_iso
hb["did"] = st["did"]
hb["verify"] = st["verify"]
hb["verdict"] = st["verdict"]
hb["latest_artifact"] = st["latest_artifact"]
hb["last_artifact"] = st["latest_artifact"]
hb["recent_artifact"] = st["latest_artifact"]
hb["next"] = st["next"]
hb["next_pointer"] = st["next"]
hb["next_milestone"] = st["next_milestone"]
hb["prod_lanes"] = st["prod_lanes"]
hb["orders_ack_receipt"] = st["orders_ack_receipt"]
hb["orders_ack_ts"] = now_iso
hb["health"] = "ok"
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- 4) self-asserts -------------------------------------------------------------
assert isinstance(hb["heartbeat_epoch_utc"], int) and isinstance(st["heartbeat_epoch_utc"], int), "epoch must be int"
re_hb = json.loads(open(HB, encoding="utf-8").read())
assert isinstance(re_hb["heartbeat_epoch_utc"], int), "epoch round-trip int assert"
re_canon = open(CANON, "rb").read().decode("utf-8", errors="replace")
assert "| r990 |" in re_canon and "| r991 |" in re_canon, "canonical rows assert"
print(f"CLOSEOUT OK: state 991->992, epoch={epoch} int-verified, ram_free={ram_free}G cpu={cpu_pct}% gpu_free={gpu_free_mib}MiB, canonical r990-heal+r991 rows landed")
