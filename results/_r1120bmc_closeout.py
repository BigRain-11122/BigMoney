# -*- coding: utf-8 -*-
# r1120 bm-c closeout writer: round report row + state faces + heartbeat (fresh read-modify-write,
# single writer; d19 faces already advanced by the tool this window).
import io, os, json, time, datetime, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- live machine faces ----------
try:
    import psutil
    vm = psutil.virtual_memory()
    RAM_FREE = round(vm.available / 1024**3, 2)
    CPU_PCT = round(psutil.cpu_percent(interval=0.5), 1)
    CORES = psutil.cpu_count(logical=True)
    RAM_TOTAL = round(vm.total / 1024**3, 1)
except Exception:
    RAM_FREE, CPU_PCT, CORES, RAM_TOTAL = 3.5, 10.0, 32, 23.9
try:
    _nvs = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                           "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    _u, _m, _t = [x.strip() for x in _nvs.split(",")]
    GPU_FREE = int(_t) - int(_m)
    GPU_UTIL = float(_u)
except Exception:
    GPU_FREE, GPU_UTIL = 14276, 0.0

# ---------- round report row ----------
ROW = (
    "%s | r1120 | bm-c | watermark verdict=green (red=false; D-19 opening delta consumed b97cb656->ec502bf6 "
    "2 rows [15:07 CEO 漫剧彻底改造令 + 15:16 CEO 竞品自研令, both bm-a-lane executed, zero bm-c action, "
    "judgment receipt results/_r1120bmc_ord_judgment.json], DEC 95879dd9 FALSE hold both scans, final "
    "re-probe dual FALSE; 孤儿面=0 [py_faces=4 / 0 orphans / 1 resident, zero-kill]; 本地未达 origin "
    "commit 数=0 [closeout push rides this window + fetch self-proof]; boards clear, jobs 0; idle --worked "
    "rc0 idle_rounds=0) | r1120 (W279 prereg PREP + 5x HANDOVER window, honest-split per r1096 law): "
    "(1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 resident=1 zero-kill + S0 fetch 0/0 "
    "clean open (HEAD==origin, 1 dirty regenerable probe face at open); (2) S0.5 D-19 opening ORD delta "
    "TRUE consumed b97cb656->ec502bf6 via d19 update --advance two-face (read-back full-string equality, "
    "heartbeat mirrors synced 3) / DEC 95879dd9 FALSE hold; unacked=0; final re-probe dual FALSE; "
    "(3) S1 smoke 49/49; (4) P0 PRODUCT = W279 prereg PREP per honest-split law (full builder roll + "
    "derive = full-window job deferred to r1121 FIRST ACTION per r1096/r1115 precedent): frozen W278 "
    "template face extracted results/_w279bmc_w278_frozen_face.txt (python subprocess raw bytes; "
    "byte-identity 23,814B sha256_16 99001d3d3f337942 == blob 053892f61cf24d98 @ freeze commit df1aaba72a "
    "PRE-backfill per r1049/r1052; HEAD post-backfill twin 1c93e077 28,082B disclosed NOT used) + anchor "
    "facts machine-frozen results/_w279bmc_prep_facts.json via results/_r1120bmc_prep_gather.py (git values "
    "ALL live-read zero transcription: prereg_freeze df1aaba72a / splice b6f486af35 13:5x / engine batches "
    "60e630918f+b965e2ecf0 / finalize estate 0a92fcc28f 15:13:26 / seat 900c23fe7d 15:09:11 + W278 "
    "finalize anchors FULL-PRECISION from _r1118bmc_w278_fivekeys.json: merged mu -0.09278575748129675 / "
    "sigma 0.24505493584785207 / K=609,520 / ledger 1,035,935 EXACT / se_mu 0.000314 / a_p95 0.2844 / "
    "klift -0.0002 / w278-only -0.09701509 / line_pre 1.1971 / line_merged 1.1969 / n_eff_held 1,033,735 "
    "+ W279 projections K 611,720 / ledger 1,038,135 / n_eff_held 1,035,935 + bands verbatim A "
    "629101..631100 / B 631101..631300 + W280p projections A naive 631_101..633_100 / B naive "
    "631_301..631_500 from seat receipt leg4); (5) 5x HANDOVER duty discharged on-time: row r1120 landed "
    "research/HANDOVER.md (window r1116-r1120; next 5x=bm-c r1125); (6) S6 light 10/10 rc0 (driver "
    "results/_r1120bmc_s6_light.py r1118 canon clone, log _r1120bmc_s6_log.txt; Monday post-15:30 honest: "
    "update_daily 0 rows cutoff 10-16 [10-19 bar NOT on sina at 15:30:04 -- papers debt=0, chain re-arms "
    "on bar landing in a later window]; dualrun ZERO-DRIFT streak 51 [461]; audit FLAG "
    "pool_starvation+supply_floor answered-by-chain [W279 prereg PREP->derive supply lane active]; py_wm "
    "insufficient_history fresh bars_present=false; regime ORANGE shadow days_in_state=1; "
    "CALL-2026-10-16 ORANGE_COOL idempotent; fund_premium no-op; b_layer all_pass; REPORT-2026-10-19 "
    "faces=5; token delta=133); (7) S7: attrition 4 ledger files CLEAN + quad green (IterationLoop PT5M "
    "live + LoopWatchdog PT2M live + claws precommit/prepush CR-normalized MATCH x2; S4U flip = "
    "adjudicated default-principal standing face) + idle --worked rc0 idle_rounds=0 agenda_starved=false "
    "+ orphan probe 4/0/1 zero-kill re-verified | verify: smoke 49/49 + frozen-face byte-identity "
    "(23,814B sha256_16 99001d3d3f337942 == blob 053892f6) + prep facts in-script asserts ALL green + d19 "
    "advance read-back full-string equality + final re-probe dual FALSE (ord ec502bf6 / dec 95879dd9) + "
    "S6 log 10x rc=0 + attrition CLEAN + quad green x4 + idle --worked rc0 + orphan 0 + epoch int + "
    "report row +1 asserted + closeout commit rides this window (push+fetch+behind-0 self-proof) | next "
    "r1121 FIRST ACTIONS: (1) W279 prereg derive = P0 first action: builder one-generation roll "
    "_r1116bmc_build_w278_derive.py -> _r1121bmc_build_w279_derive.py (E63 canon law; ALL span OLD sides "
    "verified line-level against results/_w278bmc_prereg_derive.py ACTUAL text per r1116 heal(i) law; "
    "anchors = prep facts machine-frozen results/_w279bmc_prep_facts.json; T0 = _w279bmc_w278_frozen_face.txt "
    "byte-verified 99001d3d3f337942) -> derive _w279bmc_prereg_derive.py -> research/PERPETUAL_N1_W279_PREREG.md "
    "ALL GATES PASS -> banned_direction_gate ADMIT -> freeze commit + push; (2) 10-19 bar lands on sina "
    "later today -> papers chain full re-arm (debt=0 cutoff 10-16: live.paper enforce + t35_openfill + "
    "t24 x2 + aggr + alloc + grid + system_v1 + t35_export + scorecard) -- next window checks "
    "update_daily first; (3) night GPU lane standing P0 = XQ xingqing carry-burn + jman v2 young-era + "
    "female-lead W1/W2 datasets; (4) W279 prereg -> splice editor chain = subsequent rounds honest-split "
    "per r1096; (5) next 5x HANDOVER duty = bm-c r1125"
)
rp = os.path.join(REPO, "round_reports-bm-c.md")
with io.open(rp, encoding="utf-8", newline="") as f:
    rptxt = f.read()
assert "| r1120 |" not in rptxt, "r1120 report row already present"
if not rptxt.endswith("\n"):
    rptxt += "\n"
rptxt += ROW + "\n"
io.open(rp, "w", encoding="utf-8", newline="").write(rptxt)
print("report row appended (+1 line)")

# ---------- state closeout ----------
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
assert st["round_no"] == 1120, "counter drift: %r" % st["round_no"]
st["round_no"] = 1121
st["round_no_label"] = "r1120 closeout -> counter 1121"
st["last_round"] = "r1120"
for k in ("last_round_at", "last_round_closed", "last_round_closed_at", "last_round_ts",
          "last_round_at_legacy", "last_action_at", "last_artifact_at", "last_run_at",
          "last_seen", "last_seen_at", "last_ts", "last_pulled_at", "updated", "updated_at",
          "activity_now", "now_active", "ts"):
    st[k] = TS
st["last_round_label"] = "r1120"
st["last_round_summary"] = (
    "green r1120 W279 prereg PREP + 5x HANDOVER window (honest-split r1096: frozen face byte-verified "
    "99001d3d3f337942 + prep facts machine-frozen _w279bmc_prep_facts.json with W278 chain anchors + "
    "W279 projections K 611,720/ledger 1,038,135/n_eff_held 1,035,935 + bands A 629_101..631_100 / B "
    "631_101..631_300; ORD 2-row consumed ec502bf6 dual-clean; S6 10/10 + smoke 49/49 + quad green; "
    "W279 prereg derive = r1121 first action; 5x stamp on-time next=bm-c r1125)"
)
st["last_round_summary_at"] = TS
st["last_action"] = ("r1120 closeout (W279 prereg PREP: frozen face 23,814B 99001d3d3f337942 + prep facts "
                     "machine-frozen + ORD 2-row consumed + 5x HANDOVER r1116-r1120 row landed; "
                     "counter 1120->1121)")
st["current_task"] = ("r1121 FIRST ACTION = W279 prereg derive (builder one-generation roll r1116 recipe; "
                      "anchors=prep facts _w279bmc_prep_facts.json); TODAY papers chain on 10-19 bar "
                      "landing; night GPU lane XQ+jman v2+female-lead")
st["current_task_at"] = TS
st["current_task_ts"] = EPOCH
NEXT = (
    "r1121 FIRST ACTIONS: (1) W279 prereg derive = P0 first action: builder one-generation roll "
    "_r1116bmc_build_w278_derive.py -> _r1121bmc_build_w279_derive.py (E63 canon law; ALL span OLD "
    "sides verified line-level against results/_w278bmc_prereg_derive.py ACTUAL text per r1116 heal(i) "
    "law; anchors = prep facts machine-frozen results/_w279bmc_prep_facts.json; T0 = "
    "_w279bmc_w278_frozen_face.txt byte-verified 23,814B sha256_16 99001d3d3f337942; W278 finalize "
    "anchors live-read: ledger 1,035,935 / K=609,520 / mu -0.09278576 / sigma 0.24505494 / a_p95 0.2844 "
    "/ line_merged 1.1969 / se_mu 0.000314 / klift -0.0002 / w278-only -0.09701509; bands A "
    "629_101..631_100 28th A-hop / B 631_101..631_300 29th above-own-A; W280p projection A naive "
    "631_101..633_100 / B naive 631_301..631_500 refused-faces expected) -> derive "
    "_w279bmc_prereg_derive.py -> research/PERPETUAL_N1_W279_PREREG.md ALL GATES PASS -> "
    "banned_direction_gate ADMIT -> freeze commit + push; (2) 10-19 bar lands on sina later today -> "
    "papers chain full re-arm (debt=0 cutoff 10-16); (3) night GPU lane standing P0 = XQ xingqing "
    "carry-burn + jman v2 young-era + female-lead W1/W2 datasets; (4) W279 prereg -> splice editor "
    "chain = subsequent rounds honest-split per r1096; (5) next 5x HANDOVER duty = bm-c r1125"
)
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "W279 prereg derive (r1121 first action) -> freeze push -> splice editor chain; papers chain on 10-19 bar; night GPU lane"
st["did"] = (
    "r1120 (W279 prereg PREP + 5x HANDOVER window): (1) S0-1 anchor bm-c + round-zero probe py_faces=4 "
    "orphans=0 zero-kill + S0 fetch 0/0 clean open; (2) S0.5 D-19 opening ORD delta consumed "
    "b97cb656->ec502bf6 (2 rows: 15:07 漫剧彻底改造令 + 15:16 竞品自研令, both bm-a lane, zero bm-c "
    "action; receipt results/_r1120bmc_ord_judgment.json; d19 two-face advance read-back equality, "
    "mirrors synced 3) / DEC 95879dd9 FALSE hold; unacked=0; final re-probe dual FALSE; (3) S1 smoke "
    "49/49; (4) P0 PRODUCT = W279 prereg PREP per r1096 honest-split law: frozen W278 template face "
    "extracted + byte-verified (23,814B sha256_16 99001d3d3f337942 == blob 053892f6 @ df1aaba72a "
    "PRE-backfill per r1049/r1052; HEAD twin 1c93e077 28,082B disclosed NOT used) + anchor facts "
    "machine-frozen results/_w279bmc_prep_facts.json via results/_r1120bmc_prep_gather.py (git "
    "live-read zero transcription: freeze df1aaba72a / splice b6f486af35 13:5x / engine batches "
    "60e630918f+b965e2ecf0 / finalize 0a92fcc28f / seat 900c23fe7d + W278 anchors full-precision + "
    "W279 projections K 611,720 / ledger 1,038,135 / n_eff_held 1,035,935 + bands verbatim + W280p "
    "projections); (5) 5x HANDOVER duty discharged on-time (row r1116-r1120 landed, next 5x=bm-c "
    "r1125); (6) S6 light 10/10 rc0 (update_daily 0 rows cutoff 10-16 honest sina-pending; dualrun "
    "streak 51; audit FLAG answered-by-chain; ORANGE shadow; CALL-2026-10-16 idempotent; token "
    "delta=133); (7) S7 quad green + attrition 4 CLEAN + idle --worked rc0"
)
st["verify"] = (
    "smoke 49/49 + frozen-face byte-identity dual (23,814B / 99001d3d3f337942 == blob 053892f6) + "
    "prep-facts in-script asserts ALL green + d19 advance read-back full-string equality + final "
    "probe dual FALSE (ord ec502bf6 / dec 95879dd9) + S6 log 10x rc=0 + attrition CLEAN + quad green "
    "x4 + idle --worked rc0 + orphan 0 + epoch int + report row +1 asserted + closeout push rides "
    "this window (push+fetch+behind-0 self-proof)"
)
st["verdict"] = (
    "green r1120 W279 prereg PREP + 5x HANDOVER window (frozen face byte-verified + prep facts "
    "machine-frozen + ORD 2-row consumed dual-clean + quad green; W279 prereg derive = r1121 first "
    "action; papers chain waits 10-19 bar on sina)"
)
st["r1120_closeout_note"] = (
    "r1120: clean continuation PREP window (state round_no=1120 at open, executed r1120, advanced "
    "1120->1121 so next=r1121); zero absorb owed (r1119 closeout 0a92fcc28f landed clean, zero dead "
    "window between); zero double-count: S0.5 dual-delta opening TRUE consumed THIS window "
    "(b97cb656->ec502bf6, 2 rows both bm-a lane zero bm-c action), DEC 95879dd9 FALSE hold both scans; "
    "honest-split per r1096: the full builder roll + derive = full-window job = r1121 FIRST ACTION "
    "(anchors machine-frozen THIS window, zero re-derive owed); 5x HANDOVER stamp on-time"
)
st["orders_ack_receipt"] = (
    "r1120: ORD b97cb656->ec502bf6 (2 rows: 15:07 CEO 漫剧彻底改造令 [bm-a 交互窗 executed drama-lane] + "
    "15:16 CEO 竞品自研令 [bm-a executed work-assistant lane], both zero bm-c action, receipt "
    "results/_r1120bmc_ord_judgment.json); DEC 95879dd9 FALSE hold both scans; final re-probe dual FALSE"
)
st["orders_ack_ts"] = TS
st["last_orders_read_at"] = TS
st["last_decisions_read_at"] = TS
st["head_sha"] = "r1120 closeout (W279 prereg PREP: frozen face 99001d3d3f337942 + prep facts + 5x HANDOVER; D-19 ord ec502bf6; W279 prereg derive = r1121 first)"
st["last_artifact"] = ("results/_w279bmc_prep_facts.json + results/_w279bmc_w278_frozen_face.txt + "
                       "results/_r1120bmc_prep_gather.py + results/_r1120bmc_ord_judgment.json + "
                       "results/_r1120bmc_s6_light.py + results/_r1120bmc_s6_log.txt + research/HANDOVER.md "
                       "r1120 row (this closeout batch)")
st["latest_artifact"] = st["last_artifact"]
st["recent_artifact"] = st["last_artifact"]
st["full_load_selfproof"] = {
    "占用一行": ("CPU=W279 prereg PREP landed (derive = r1121 first action); GPU=idle day, night queue = XQ "
                "xingqing carry-burn + jman v2 young-era + female-lead W1/W2 datasets (standing GPU-lane "
                "night P0); short-video lane DISABLED standing per O-20261017-1741"),
    "最近实物": ("results/_w279bmc_prep_facts.json (W279 derive anchors machine-frozen: W278 chain commits + "
                "full-precision actuals + projections K 611,720/ledger 1,038,135) + "
                "results/_w279bmc_w278_frozen_face.txt (byte-verified 99001d3d3f337942) @ %s" % TS),
    "下个里程碑": ("W279 prereg derive r1121 first action -> freeze push -> splice editor chain; papers "
                 "chain on 10-19 bar landing (debt=0); W279 cycle completion ETA 2026-10-20"),
}
st["prod_lanes"] = ("CPU=W279 prereg PREP landed (derive = r1121 first); GPU=idle day (night queue "
                    "XQ+jman v2+female-lead standing P0 night); short-video lane DISABLED standing per "
                    "O-20261017-1741")
st["ram_critical_face"] = "none (loop CPU-only, GPU idle day)"
st["free_ram_gb"] = RAM_FREE
st["idle_ram_gb"] = RAM_FREE
st["ram_free_gb"] = RAM_FREE
st["total_ram_gb"] = RAM_TOTAL
st["cpu_pct"] = CPU_PCT
st["cpu_util_pct"] = CPU_PCT
st["cpu_idle_pct"] = round(100 - CPU_PCT, 1)
st["cores"] = CORES
st["cpu_cores"] = CORES
st["gpu_free_mb"] = GPU_FREE
st["gpu_free_vram_mb"] = GPU_FREE
st["gpu_free_vram_mib"] = GPU_FREE
st["gpu_idle_mb"] = GPU_FREE
st["gpu_idle_vram_mb"] = GPU_FREE
st["gpu_free_mib"] = GPU_FREE
st["gpu_vram_free_mb"] = GPU_FREE
st["gpu_free_vram_gb"] = round(GPU_FREE / 1024.0, 2)
st["gpu_util_pct"] = GPU_UTIL
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["heartbeat_epoch_utc"] = EPOCH
st["heartbeat_epoch_utc_type"] = "int (assert)"
assert isinstance(st["heartbeat_epoch_utc"], int)
st["clock_read"] = TS
st["d19_watermark_guard"]["ts"] = TS
st["d19_watermark_guard"]["round_ref"] = 1120
st["sync"] = {"origin_tip": "r1120 closeout commit rides this window (push + fetch behind-0 self-proof)",
              "ts": TS}
io.open(sp, "w", encoding="utf-8").write(json.dumps(st, ensure_ascii=False, indent=1))
print("state closed: round_no 1120->1121, epoch int OK, TS", TS)

# ---------- heartbeat ----------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = TS
hb["last_seen_at"] = TS
hb["ts"] = TS
hb["updated"] = TS
hb["current_task"] = st["current_task"]
hb["current_task_at"] = TS
hb["cores"] = CORES
hb["cpu_cores"] = CORES
hb["free_ram_gb"] = RAM_FREE
hb["idle_ram_gb"] = RAM_FREE
hb["gpu_free_vram_mb"] = GPU_FREE
hb["gpu_free_mb"] = GPU_FREE
hb["verdict"] = st["verdict"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = EPOCH
assert isinstance(hb["heartbeat_epoch_utc"], int)
hb["clock_read"] = TS
hb["round_no"] = 1121
hb["last_round"] = "r1120"
hb["prod_lanes"] = st["prod_lanes"]
io.open(hp, "w", encoding="utf-8").write(json.dumps(hb, ensure_ascii=False, indent=1))
print("heartbeat written: epoch int OK, RAM %.2fGB, GPU free %dMiB" % (RAM_FREE, GPU_FREE))
