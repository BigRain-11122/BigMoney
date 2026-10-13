# -*- coding: utf-8 -*-
# r967 bm-c closeout: absorb note + counter 965->968 + watermark heal
# (genuine faces read PROGRAMMATICALLY from the s05 probe facts json --
# r583 law, zero literal shas) + heartbeat + round report line.
import json, time, datetime, subprocess, sys, psutil
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

# genuine watermark faces from the probe facts (r583: zero literals)
p = json.load(open(r"results\_s05_probe.bm-c.json", encoding="utf-8"))
wf = p["watermark_face"]
ORD_SHA, DEC_SHA = wf["orders_sha"], wf["decisions_sha"]
assert len(ORD_SHA) == 64 and len(DEC_SHA) == 64, "sha shape gate"
assert ORD_SHA != "c7d3ee65"[:8] and wf["wm_orders"].startswith("c7d3ee65"), "phantom-face precondition"

# live stats
ram = psutil.virtual_memory()
ram_avail = round(ram.available / 1e9, 1)
cpu_pct = psutil.cpu_percent(interval=1)
gpu_free = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    gpu_free = int(out)
except Exception:
    gpu_free = None

s = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", encoding="utf-8"))
assert s["round_no"] == 965, f"unexpected state counter {s['round_no']}"
s["round_no"] = 968
s["loop_round"] = 967
s["last_round"] = 967
s["last_round_at"] = now_iso
s["last_round_ts"] = epoch
s["last_round_closed"] = now_iso
s["last_round_summary"] = ("r967: W232 PREREG DERIVED+LANDED same-window (SIXTEEN-level lineage replay 46/46 "
    "preflight zero false-fails; tplgen A/B + subgen m29 + R32 authored-from-machine-facts; "
    "sha16 500c669da3d05060; bands A 525_204..527_203 NINETY-SECOND / B 527_204..527_403 per "
    "ADMIT receipt) + ORD/DEC phantom-watermark heal (genuine faces f4d2ea1b/fb5825cb, deltas "
    "FALSE both, r966 already consumed through 13:1x) + S6 light ALL-RC0 + S7 quad green + "
    "attrition 4 CLEAN; counter 965->968 (absorb dead r965 splice-editor window + dead r966 "
    "W231-full-cycle/W232-seat session, both committed pre-closeout)")
s["r967_absorb_note"] = ("r967 absorb note: prior windows -- dead 12:5x window (labeled r965, derived the "
    "W231 splice editor, zero commits) and the 13:0x-13:25 session (labeled r966, committed+pushed W231 "
    "five-face freeze splice estate aee0bd9fa + engine self-burn 492972ee7/4e373b743 + six-gate "
    "PRE-FINALIZE sixth consecutive correct-phase + finalize one-pass 931,989/K 506,120 five-key ALL "
    "PASS + sec.7/8 backfilled 0636c1d12 + W232 seat published 8d3a1b78a incl MSG-20261013-1345) died "
    "pre-closeout with state frozen at round_no=965 -- this session executed as r967 (next after "
    "highest committed label r966) per the bm-c absorb precedent lineage (19th instance) and advanced "
    "counter 965->968 so next session = r968; zero double-count: r966 body debts were handled by its "
    "own commits+pushes (origin 0/0 at open), the dead r965 editor was landed via r966's splice estate "
    "commit, S0.5 ORD/DEC consumption was handled by r966 (through 13:1x rows; DEC fb5825cb unchanged) "
    "-- this window's probe TRUE-verdicts were phantom-watermark artifacts (state keys c7d3ee65/f41caf26 "
    "NOT in blob history, corrupt-face 5th/6th per r966 heal evidence) and were healed programmatically "
    "this window; dead-session S6-light estate + inbox processed-moves landed by this closeout")
s["activity_now"] = (f"{now.strftime('%Y-%m-%d %H:%M')}x | r967 | bm-c: W232 PREREG DERIVED+LANDED "
    "(SIXTEEN-level replay 46/46, tplgen A/B+subgen m29+R32 machine-facts authored, sha16 500c669da3d05060, "
    "bands A 525_204..527_203 / B 527_204..527_403 per ADMIT) + ORD/DEC phantom-watermark heal (genuine "
    "f4d2ea1b/fb5825cb both FALSE-delta, r966 consumed through 13:1x) | counter 965->968 | W232 five-face "
    "freeze splice (clone committed _w231bmc_derive_editor.py) = next window FIRST ACTION")
s["current_task"] = "r967 closeout (W232 prereg landed + absorb estate + watermark heal)"
s["current_task_at"] = now_iso
s["verdict"] = ("green: W232 PREREG LANDED (research/PERPETUAL_N1_W232_PREREG.md, SIXTEEN-level replay 46/46 "
    "zero false-fails, all STALE/NEW/band/chain-leg guards PASS) + absorb r965/r966 dead windows (estate "
    "all committed+pushed by r966, this window landed the residual S6-light + inbox faces) + ORD/DEC "
    "genuine watermarks healed (both FALSE delta, zero consumption owed) + smoke 49/49 + S6 light "
    "ALL-RC0 + S7 quad green + attrition 4 CLEAN")
s["next_pointer"] = ("r968: (1) W232 five-face freeze splice FIRST ACTION (bloodline clone of committed "
    "_w231bmc_derive_editor.py per W232 prereg estate-face prose; gate0 origin + gate0.5 W231 row + W231 "
    "finalize 件在场 anchors 931,989/K=506,120; freeze receipt + edits clone of _w231bmc_freeze_edits.py "
    "template) -> engine self-burn 12/12 -> PRE-FINALIZE six-gate (W217-debt standing law, seventh "
    "consecutive) -> finalize one-pass (ledger 931,989+2,200=934,189 projection / K 506,120+2,200=508,320) "
    "-> five-key + sec.7/8 backfill; (2) W233 seat publish after W232 finalize per seat-first law (probe "
    "derive + ADMIT + MSG pre-freeze; W233+ projection A 527_204..529_203 / B 527_404..527_603 NINETY-THIRD "
    "anticipated per W232 prereg §5.5); (3) Tue 15:30 new-bar window: papers full chain + update family")
s["next"] = s["next_pointer"]
s["next_milestone"] = "W232 splice + burn + six-gate + finalize (next window first action per chain law); Tue 15:30 papers full chain"
s["latest_artifact"] = "research/PERPETUAL_N1_W232_PREREG.md (sha16 500c669da3d05060) + results/_w232bmc_prereg_derive.py"
s["last_artifact"] = s["latest_artifact"]
s["recent_artifact"] = s["latest_artifact"]
s["last_action"] = "r967 closeout (W232 prereg derive+land + absorb + watermark heal + S6 light + S7 quad)"
s["last_orders_sha"] = ORD_SHA
s["last_decisions_sha"] = DEC_SHA
s["last_orders_sha_method"] = "sha256 raw-blob bytes (healed this window from phantom c7d3ee65; genuine face read programmatically from results/_s05_probe.bm-c.json per r583 law; r966 consumed through 13:1x rows)"
s["last_decisions_sha_method"] = "sha256 raw-blob bytes (healed this window from phantom f41caf26; genuine face read programmatically from results/_s05_probe.bm-c.json per r583 law; fb5825cb unchanged since 00:07)"
s["last_orders_at"] = now_iso
s["last_decisions_read_at"] = now_iso
s["last_orders_read_at"] = now_iso
s["orders_ack_receipt"] = ("r967: ORD/DEC genuine watermarks healed (phantom c7d3ee65/f41caf26 both NOT in blob "
    "history, corrupt-face 5th/6th per r966 heal evidence); genuine faces ORD f4d2ea1b (tail = 10-13 13:1x "
    "rows, exactly r966's consumption point -- zero new rows) / DEC fb5825cb (unchanged since 00:07) -> "
    "both deltas FALSE, zero consumption owed this window; unacked=0")
s["cpu_pct"] = cpu_pct
s["cpu_util_pct"] = cpu_pct
s["free_ram_gb"] = ram_avail
s["ram_free_gb"] = ram_avail
s["idle_ram_gb"] = ram_avail
s["ts"] = now_iso
s["clock_read"] = now_iso
s["updated"] = now_iso
s["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
s["heartbeat_epoch_utc"] = epoch
s["idle_rounds"] = 0
s["agenda_starved"] = False
if gpu_free is not None:
    s["gpu_free_vram_mib"] = gpu_free
    s["gpu_free_vram_mb"] = gpu_free
    s["gpu_idle_vram_mb"] = gpu_free
    s["gpu_free_vram_gb"] = round(gpu_free / 1024, 1)
s["head_sha"] = "quant: rides this window's closeout commit; group-tree: 5f69a62 (unchanged)"
s["health"] = "ok"
s["orphan_face"] = 2
s["orphan_faces"] = 2

# ---- heartbeat ----
hb_path = rf"{REPO}\fleet\machines\bm-c.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int)
hb["current_task"] = "W232 prereg landed; next = W232 five-face freeze splice (first action r968)"
hb["verdict"] = "green: W232 prereg derived+landed; ORD/DEC watermarks healed; S6 light ALL-RC0; quad green"
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = ram_avail
if gpu_free is not None:
    hb["gpu_free_vram_mib"] = gpu_free
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- state write ----
json.dump(s, open(rf"{REPO}\state-bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(rf"{REPO}\state-bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and chk["round_no"] == 968
assert chk["last_orders_sha"] == ORD_SHA and chk["last_decisions_sha"] == DEC_SHA

# ---- round report line ----
rr = (f"| {now_iso} | r967 | W232 PREREG DERIVED+LANDED same-window: SIXTEEN-level lineage replay 46/46 "
      "preflight zero false-fails (pairs216 + SUB17..SUB31, one deeper than W231's fifteen); generation "
      "chain = _r967bmc_tplgen.py (phase A, 30 assert-verified reps) + _r967bmc_tplgen_b.py (phase B "
      "STALE/NEW/in-band/tail) + _w232bmc_subgen.py (SUB31 extract from committed _w231bmc derive, m29 "
      "materialization, R32 authored from machine facts) + assembly; output research/PERPETUAL_N1_"
      "W232_PREREG.md 25380B sha16 500c669da3d05060 (bands A 525_204..527_203 NINETY-SECOND staircase / "
      "B 527_204..527_403 own-A mutual-exclusion per ADMIT receipt; anchors 931,989/K 506,120/merged mu "
      "-0.09268999/w231-only -0.09203368/sigma 0.24507072/p95 0.3251/KL +0.0001/se_mu 0.000344 machine-"
      "read; RAM ~6.0GB live; engine idle verified; W233+ projection A 527_204..529_203 / B 527_404.."
      "527_603 NINETY-THIRD) || ABSORB r965 (dead 12:5x splice-editor window, zero commits) + r966 "
      "(W231 full cycle + W232 seat, all committed+pushed, died pre-closeout; counter 965->968) || "
      "ORD/DEC phantom-watermark heal (genuine f4d2ea1b/fb5825cb read programmatically from s05 probe "
      "facts per r583; both deltas FALSE, r966 already consumed through 13:1x; zero owed) || pitfall "
      "found+disclosed: committed _r964bmc_tplgen.py tail py_compile = non-fatal dead leg (bare "
      "@@SUB_BLOCK@@ marker invalid python pre-assembly; write precedes compile so r964's product "
      "landed anyway) -- my clone drops the dead leg, compile gate runs post-assembly || S6 light "
      "ALL-RC0 (dualrun streak + wm + update family no-ops pre-15:30 + papers + daily_report + "
      "ceo_live_usage + token) || S7 quad green (loop+watchdog present via redirect probe; claws "
      "CR-normalized match) + attrition 4 CLEAN | next: r968 W232 five-face freeze splice FIRST "
      "ACTION -> engine self-burn -> six-gate PRE-FINALIZE -> finalize one-pass -> five-key + "
      "sec.7/8; W233 seat after; Tue 15:30 papers full chain |")
open(rf"{REPO}\round_reports-bm-c.md", "a", encoding="utf-8").write(rr + "\n")
print("closeout OK: counter 968, epoch", epoch, "| ram_avail", ram_avail, "| cpu", cpu_pct, "| gpu_free", gpu_free)
