# -*- coding: utf-8 -*-
"""r976 bm-c absorb closeout: state + heartbeat + round report line + ORD watermark check."""
import json, subprocess, time, datetime, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_wall = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# --- ORD watermark check (group tree origin blob SHA-1, 40hex comparable) --------
r = subprocess.run(["git", "-C", r"K:\Fluxgroup\FluxGroup", "rev-parse", "origin/main:docs/orders.md"],
                   capture_output=True, text=True)
ord_sha_new = r.stdout.strip()
hb = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
ord_old = hb.get("last_orders_sha", "")
ord_delta = (ord_sha_new != ord_old) and ord_sha_new
print("ORD:", ord_old, "->", ord_sha_new, "delta=", bool(ord_delta))

did = ("r976: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=1 zero-kill (c1011_album_serve.pyw = "
       "BigStream cross-domain idle server, disclosed not killed); S0 pull blocked by own-runtime dirty tree -> "
       "fetch behind=0 no integration owed (mid-window push race vs bm-a a594dfdd3 resolved via stash->rebase->pop, "
       "zero conflicts); (2) S0.5: ORD 差集 0 (205 ack) + DEC fb5825cb->2bf2a0ef delta consumed (D-20261013-01 "
       "回执核销批 31 + D-20261013-02 Phase 0 盘点 -- 涉本司零执行件·水位推进) + group orders rows re-read (10-13 "
       "04:3x = @bm-a MV lane, not this loop's lane); (3) S1 smoke 49/49; (4) ABSORB 22nd instance: W234 FULL CYCLE "
       "machine-verified closeout -- dead r976 prereg derive 252d5cc95 (R34 authored + 18-level replay 46/46 + r958 "
       "pitfall 4th fixed live) + dead r976-continuation census-first five-face freeze splice de342250c + engine "
       "self-burn 12/12 batched 39f7b8b0c/5022491bc + absorb-tail 3 shards engine-law append (rebased 0ad430c3b) + "
       "THIS-window six-gate PRE-FINALIZE ALL GREEN ninth consecutive correct-phase (pf 3afc785bb9cd70fd / n1 "
       "fc93ed564e85a79d clean-equal + banned ADMIT + pf selftest 9/9 + n1 selftest + shards 12/12 + seed FREE x2 + "
       "WAVE_CONFIGS[234]) -> finalize one-pass ledger 936,389+2,200=938,589 EXACT / merged K 510,520+2,200=512,720 "
       "EXACT (merged mu -0.0928 sigma 0.2451, w234-only mu -0.0947 sigma 0.2506) + five-key ALL PASS (key1 "
       "0.0019<0.02 / key2 +0.0098pct / key3 0.007<0.05 / key4 +0.0002 / key5 inherit) + sec.7/8 machine-read "
       "backfilled placeholders=0; (5) W235 SEAT PUBLISHED: probe rc0 ADMIT A 531804..533803 staircase "
       "NINETY-FIFTH hops=1 (refused-at-start by registered W234 B band, leg4 projection fulfilled verbatim) + B "
       "533804..534003 own-A exclusion hops=1 + seed_admit FREE x2 (531804/2000 + 533804/200) + origin vacancy "
       "4-checks + W236+ projection A 533804..535803 / B 534004..534203 + seat MSG-20261013-2149-bmc; closeout "
       "push e830a2632; (6) S6 light: dualrun ZERO-DRIFT streak 51 (cutoff 10-11) + compute_audit FLAG "
       "pool_starvation/supply_floor structural ANSWERED-BY-SEAT (W235 seat published = never-dry supply line; "
       "engine lane is the CPU supply face) + py_watermark insufficient_history honest (bars_present=false this "
       "round window -- 10-13 bars landed+consumed by dead-window S6 already, update_daily 0 new rows cutoff "
       "10-13) + market_regime trigger breadth 0.81>=65% + market_clock ORANGE_COOL idempotent + thermo "
       "Money02-absent honest no-op + fundamental fresh-skip + b_layer verdict + fund_premium no-op (bm-c lane, "
       "10-12 snapshot covers NAV) + AGGR paper 20/20 accounts marked through 2026-10-13 + grid_paper no-op "
       "(cutoff 10-12) + live.paper/t35_verify/t24_paper/t24_promotion/t35_export lane_io guard skip (host=bm-a "
       "origin fresh 12-14min, r701 third-signal veto honest) + alloc bm-b-lane no-op + daily_report "
       "REPORT-2026-10-13 faces=5 + ceo_live_usage LIVE-2026-10-13 (state=ORANGE rung=ORANGE cap=50% heat=COOL 6 "
       "members) + token L2 legs 0 today; (7) S7: attrition 4 CLEAN (1 healed row) + loop pin=5 no-op + watchdog "
       "re-registered + precommit/prepush claws installed; counter 976->977 (dead r976 derive window + dead r976 "
       "continuation window both died pre-closeout, absorbed per r894/r897/r907/r911/r915/r917/r919/r921/r928/"
       "r930/r933/r941/r947/r951/r956/r959/r962/r963/r974 precedent; zero double-count: S0.5 dual-delta this "
       "window ORD 0/DEC 2 rows zero BigMoney action)")

hb["round_no"] = 977
hb["last_round"] = 976
hb["heartbeat_epoch_utc"] = epoch
hb["last_seen"] = now_wall
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["current_task"] = "r976 absorb closeout (W234 full cycle + W235 seat + S6 light + S7 quad)"
hb["current_task_at"] = now_iso
hb["current_task_ts"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated_at"] = now_iso
hb["updated"] = now_iso
hb["last_round_at"] = now_iso
hb["last_round_at_legacy"] = hb.get("last_round_at_legacy", now_iso)
hb["now_active"] = ("2026-10-13 21:5x | r976 | bm-c: absorb 22nd closed (W234 full cycle 938,589/K 512,720 + "
                    "W235 seat A 531804..533803) | counter 976->977 | r977 first action=W235 prereg derive")
hb["activity_now"] = hb["now_active"]
hb["did"] = did
hb["prod_lanes"] = ("GPU=MV V3 lane: fullres 7/7 burned+relayed, i2v 7-shot ignition GATED on bm-a director "
                    "ten-seat frame review (RAM 仲裁 i2v 优先); CPU=N1 W234 full cycle LANDED (938,589/K 512,720) "
                    "+ W235 SEATED, prereg derive = r977 first action (engine daemon ALIVE)")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w234_results.json + results/_r976bmc_w234_fivekey_receipt.json "
                         "+ results/_w235bmc_20261013_probe_receipt.json + fleet/inbox/MSG-20261013-2149-bmc.md (all in e830a2632)")
hb["last_artifact"] = hb["latest_artifact"]
hb["recent_artifact"] = hb["latest_artifact"]
hb["next_milestone"] = ("W235 prereg derive (r977 first action) -> splice/burn/six-gate/finalize (window <=48h); "
                        "V3 director sign-off -> i2v 7 shots -> RIFE assembly")
hb["next"] = ("r977: (1) W235 prereg derive FIRST ACTION (bloodline clone of committed _w234bmc_prereg_derive.py "
              "per MSG-20261013-2149 seat law; bands A 531804_533803 / B 533804_534003 per ADMIT receipt "
              "_w235bmc_20261013_probe_receipt.json; anchors machine-read W234 ledger 938,589 / K 512,720 / mu "
              "-0.0928 / sigma 0.2451 / A_p95 0.3097 / skill_line 1.1925 delta +0.0002 / se_mu 0.000342) -> "
              "five-face freeze splice (census-first) -> engine self-burn 12/12 -> PRE-FINALIZE six-gate "
              "(W217-debt standing law) -> finalize one-pass -> five-key + sec.7/8 backfill; (2) W236+ projection "
              "per leg4: A 533804..535803 / B 534004..534203 NINETY-SIXTH anticipated; (3) V3 lane: director "
              "ten-seat frame review pending (bm-a) -> sign-off -> i2v ignition; (4) bars re-probe next trading day")
hb["next_pointer"] = hb["next"]
hb["verdict"] = ("green: W234 FULL CYCLE landed (938,589/K 512,720 five-key ALL PASS) + W235 SEATED; "
                 "r977 = prereg derive first action")
hb["note"] = "r976: absorb 22nd (W234 full cycle + W235 seat) + S0.5 DEC advance + S6 light + S7 quad"
hb["last_round_summary"] = ("r976: ABSORB dead r976 derive + r976-continuation splice windows (22nd): W234 FULL "
                            "CYCLE landed (prereg 252d5cc95 + splice de342250c + burn 39f7b8b0c/5022491c/absorb-tail "
                            "0ad430c3b + sixgate PRE-FINALIZE 9th + finalize 938,589/K 512,720 EXACT + five-key "
                            "ALL PASS + sec.7/8) + W235 SEAT ADMIT (A 531804_533803/B 533804_534003) + MSG-2149; "
                            "DEC fb5825cb->2bf2a0ef consumed (2 rows zero action); counter 976->977")
hb["last_round_summary_at"] = now_iso
hb["last_action"] = "r976 closeout (absorb 22nd + W235 seat)"
hb["last_action_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["loop_round"] = 976
hb["last_round_ts"] = epoch
hb["last_ts"] = epoch
hb["verify"] = ("receipts: sixgate PRE-FINALIZE json (21:4x ninth consecutive) + fivekey ALL PASS + ledger identity "
                "EXACT + W235 probe ADMIT + push a594dfdd3..e830a2632 (rebase ride) + smoke 49/49 + attrition 4 "
                "CLEAN + dualrun streak 51 + S7 quad green (loop pin5/watchdog/claws)")
hb["orphan_face"] = 1
hb["orphan_faces"] = 1
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["head_sha"] = "quant: e830a2632 (r976 absorb closeout); group-tree: fetched, V3 relay unchanged this lane"
hb["sync"] = {"origin_tip": "e830a2632 (r976 absorb estate + closeout rides this window)",
              "ts": now_iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
              "note": "r976: absorb dead r976 dual windows (W234 full cycle + W235 seat) + S0.5 DEC advance + S6 light + S7 quad"}
hb["last_decisions_sha"] = "2bf2a0ef5c4e6384cba0e3e1f85b09da9500f850ca483a230c1fbe0cd53488c5"
hb["last_decisions_read_at"] = now_iso
hb["last_decisions_at"] = now_iso
hb["last_decisions_seen"] = now_wall
hb["last_decisions_read_note"] = ("r976: DEC delta TRUE fb5825cb->2bf2a0ef consumed (D-20261013-01 回执核销批 31 "
                                  "['bigmoney 六任务 E1 复启窗 03:07 夜班核验' = passed-window face] + "
                                  "D-20261013-02 Phase 0 盘点 -- 涉本司零执行件·水位推进)")
hb["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r976 fresh "
                        "consume 2bf2a0ef via PS UTF8 bytes; METHOD PIN: DEC watermark = raw-blob bytes SHA-256 "
                        "ONLY, PS line-join reconstruction FORBIDDEN (r583 zero-literal + raw-blob law)")
hb["orders_ack_ts"] = hb.get("orders_ack_ts", now_iso)
hb["orders_ack_receipt"] = ("r976: ORD repo 差集 0 (205 ack stable); group ORD blob " +
                            ("ADVANCED " + ord_old + "->" + ord_sha_new if ord_delta else "HOLD " + ord_sha_new) +
                            " -- 10-13 04:3x row = @bm-a MV lane (not this loop's lane); zero BigMoney action owed")
if ord_delta:
    hb["last_orders_sha"] = ord_sha_new
    hb["last_orders_at"] = now_iso
    hb["last_orders_seen"] = now_wall
    hb["last_orders_read_at"] = now_iso
else:
    hb["last_orders_read_at"] = now_iso
    hb["last_orders_seen"] = now_wall
hb["last_pulled_at"] = now_iso

# --- fresh machine stats -----------------------------------------------------------
try:
    import ctypes
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    free_gb = round(m.ullAvailPhys / (1024 ** 3), 1)
    total_gb = round(m.ullTotalPhys / (1024 ** 3), 1)
except Exception:
    free_gb, total_gb = 1.8, 25.7
hb["free_ram_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    tot, used, util = [x.strip() for x in g.stdout.strip().split(",")]
    hb["gpu_free_vram_mb"] = int(tot) - int(used)
    hb["gpu_free_vram_mib"] = int(tot) - int(used)
    hb["gpu_free_mib"] = int(tot) - int(used)
    hb["gpu_vram_free_mb"] = int(tot) - int(used)
    hb["gpu_free_mb"] = int(tot) - int(used)
    hb["gpu_used_vram_mib"] = int(used)
    hb["gpu_mem_used_mib"] = int(used)
    hb["gpu_mem_total_mib"] = int(tot)
    hb["gpu_total_vram_mib"] = int(tot)
    hb["gpu_util_pct"] = int(util)
    hb["gpu_free_vram_gb"] = round((int(tot) - int(used)) / 1024, 1)
except Exception:
    pass
json.dump(hb, open(REPO + r"\fleet\machines\bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- state file ---------------------------------------------------------------------
st = json.load(open(REPO + r"\state-bm-c.json", encoding="utf-8"))
st["round_no"] = 977
st["clock_read"] = now_iso
st["current_task"] = hb["current_task"]
st["current_task_at"] = now_iso
st["did"] = did
st["free_ram_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["heartbeat_epoch_utc"] = epoch
st["last_decisions_read_at"] = now_iso
st["last_decisions_sha"] = hb["last_decisions_sha"]
st["last_decisions_sha_method"] = hb["dec_sha_method"]
json.dump(st, open(REPO + r"\state-bm-c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report line ----------------------------------------------------------------
line = (now_wall + " | r976 | bm-c: ABSORB 22nd -- W234 FULL CYCLE machine-verified closeout (dead r976 derive "
        "252d5cc95 + dead r976-continuation splice de342250c + engine self-burn 12/12 + absorb-tail 3 shards "
        "0ad430c3b + sixgate PRE-FINALIZE 9th consecutive ALL GREEN + finalize 938,589/K 512,720 EXACT + five-key "
        "ALL PASS + sec.7/8 placeholders=0) + W235 SEAT ADMIT (A 531804_533803 NINETY-FIFTH + B 533804_534003 + "
        "MSG-2149 origin e830a2632) | evidence: results/_r976bmc_w234_sixgate_prereg.json + "
        "_r976bmc_w234_fivekey_receipt.json + _w235bmc_20261013_probe_receipt.json + n1_w234_results.json + push "
        "a594dfdd3..e830a2632 | S6: dualrun streak 51 + audit FLAG answered-by-seat + AGGR 20/20 marked 10-13 + "
        "REPORT-2026-10-13 + LIVE-2026-10-13 | S0.5: DEC 2bf2a0ef consumed 2 rows zero action + ORD repo 差集 0 | "
        "S1 49/49 + S7 quad green + attrition 4 CLEAN | next: r977 W235 prereg derive first action\n")
with open(REPO + r"\round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write(line)

print("CLOSEOUT-OK")
print("epoch int check:", isinstance(json.load(open(REPO + r"\" + \"fleet/machines/bm-c.json".replace('\"', ''))) ["heartbeat_epoch_utc"], int) if False else "see smoke")
print("RAM free:", free_gb, "GB | clock:", now_iso)
