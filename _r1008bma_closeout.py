# r1008 bm-a S7 closeout: state + heartbeat + round-report append
import json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# ---- state-bm-a.json ----
sp = "state-bm-a.json"
d = json.load(open(sp, encoding="utf-8"))

did = ("r1008: dead-window estate absorb closeout - W244 chain FULL LANDED: "
       "five-face freeze (r1007 10bdb987b, pushed) -> engine self-burn 12/12 06:59-07:11 "
       "(claim-exempt engine lane) -> finalize one-pass fivekeys ALL PASS "
       "(merged K=534,720 EXACT 532,520+2,200; ledger 958,935+2,200=961,135 EXACT; "
       "mu -0.09280 / sigma 0.24505 / se_mu 0.000335 narrowing; K-lift -0.0001 first-negative "
       "in-chain precedent-band; A p95 0.2952 delta 0.0241) -> prereg sec7/8 backfill LANDED -> "
       "E42 writer-pause rebase onto origin/main behind4 (18 UU shared generated faces take-theirs "
       "merge-mode r708) -> push 074c10349..5e24d1fdb verified behind=0 -> S6 chain 41 legs rc0 "
       "post-rebase re-derive -> D-19 dual probe DEC 6910a9ed/ORD 58b9ee88 both MATCH zero delta")

d["round_no"] = 1009
d["round"] = 1008
d["loop_round"] = 1008
d["last_round"] = 1008
d["last_round_at"] = now_iso
d["last_round_closed"] = now_iso
d["last_round_ts"] = now_iso
d["last_run"] = now_iso
d["last_seen"] = now_iso
d["updated"] = now_iso
d["updated_at"] = now_iso
d["ts"] = now_iso
d["clock_read"] = now_iso
for k in ("current", "current_task", "did", "now_active", "task"):
    d[k] = did
d["last_action"] = "r1008 W244 finalize one-pass landed + rebase push behind=0 + S6 chain rc0"
art = ("results/_r1008bma_w244_fivekeys.json (ALL PASS) + research/PERPETUAL_N1_W244_PREREG.md "
       "sec7/8 backfilled + results/perpetual_faces/n1_w244_results.json (commit 5e24d1fdb pushed 07:47)")
for k in ("last_artifact", "latest_artifact", "recent_artifact"):
    d[k] = art
d["next"] = ("r1009: board watch - W245 seat publish+freeze belongs to bm-c (their counter awaits W244 "
             "finalize = now LANDED, unblocked); bm-a next own wave derive (W246 class) starts only after "
             "W245 seat/freeze/finalize chain lands (seat-first publish law + live re-derive + probe receipt "
             "leg1 B_semantics + prereg buildgen from PERPETUAL_N1_W245 tpl if bm-c cedes or stalls >1 round "
             "-> takeover per GM re-assignment lane); meanwhile claim P2/P3 queue head if new rows seeded "
             "(queue_seed_gate check first) else trial-labor standing line; S6 chain per round")
d["next_milestone"] = ("W245 chain (bm-c seat) consumed + bm-a next own-wave prereg draft <=48h; "
                       "W244 products on origin = CEO-visible: n1_w244_results.json + fivekeys receipt")
d["verdict"] = ("green (red=false; W244 freeze->burn 12/12->finalize fivekeys ALL PASS chain complete; "
                "satengine ALIVE rc0 queue0 idle post-burn = W245 seat not yet published (bm-c); "
                "py 0.3 pct py_low_board_clear legal idle whitelist (board clear, P2/P3 heads done, "
                "supply line just landed); orphan 0/27; CEO daytime GPU face 1.5G free = normal)")
d["verify"] = ("green (smoke 49/49 + S6 chain 41 legs rc0 + dualrun streak 37 consecutive green + "
               "attrition scan rc0 CLEAN + D-19 dual MATCH + push range-verified 074c10349..5e24d1fdb "
               "behind=0 + rebase 18 UU take-theirs merge-mode r708 zero-loss)")
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["heartbeat_epoch_utc"] = epoch
d["last_heartbeat_epoch_utc"] = epoch
d["heartbeat_epoch_utc_type_int"] = True
d["last_orders_seen"] = ("r1008: ORD 58b9ee88 re-verified UNCHANGED (python-raw origin blob sha256 == "
                         "watermark); zero delta; zero action")
d["last_decisions_seen"] = ("r1008: DEC 6910a9ed re-verified UNCHANGED (python-raw origin blob sha256 == "
                            "watermark); zero delta; zero action")
d["last_orders_at"] = now_iso
d["last_decisions_at"] = now_iso
d["push_verified"] = {
    "ts": now_iso,
    "note": ("r1008: estate absorb commit 5e24d1fdb pushed 074c10349..5e24d1fdb rc0 (range line verified; "
             "behind=0); W244 finalize unblocks bm-c W245 seat"),
    "origin_tip": "5e24d1fdb",
}
d["sync"] = {
    "ahead_behind": "0/0",
    "origin_tip": "5e24d1fdb",
    "ts": now_iso,
    "note": "r1008: post-closeout re-verify below",
}
d["d19_watermark_guard"] = {
    "tool": "scripts/d19_watermark.py",
    "probe": "results/_r686bmb_d19_check.py",
    "probe_evidence": "C:\\Users\\sjs20\\Desktop\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json",
    "method_decisions": "sha256",
    "method_orders": "sha256",
    "verbatim": True,
    "advance": True,
    "round_ref": 1009,
    "ts": now_iso,
}
d["notes_seq_repair_r1008"] = ("r1008 sequence-honest: r1007 dead 06:15 window (watermark probe only) + "
                               "r1007 3-commits pushed by 06:4x-07:1x window (50dfc18e4/71ac3a885/"
                               "10bdb987b freeze landed, report line absent) + r1008 finalize window "
                               "06:5x-07:35 died pre-commit (fivekeys 07:27/backfill 07:29/quarantine "
                               "07:35) -> absorbed + landed by THIS window as r1008 closeout per r962/"
                               "r1006 precedent; canonical face = round_reports-bm-a.md + git log")
json.dump(d, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-a.json ----
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = now_iso
h["ts"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["current_task"] = "r1008 W244 finalize absorb-closeout landed (chain complete: freeze->burn 12/12->fivekeys ALL PASS->pushed)"
h["recent_artifact"] = art
h["next_milestone"] = "W245 seat (bm-c) unblocked; bm-a next own-wave derive <=48h"
h["cpu_cores"] = 32
h["ram_free_gb"] = 40.7
h["gpu_free_vram_mb"] = 1501
h["verdict"] = "green"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["now_active"] = "idle-watch post-W244 (engine queue 0, W245 seat=bm-c)"
h["last_action"] = "r1008 W244 finalize landed + push behind=0"
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- round report append (canonical face, root) ----
rp = "round_reports-bm-a.md"
line = (f"\n{now_iso} | r1008 | {did[:900]} | "
        f"smoke 49/49 + S6 chain 41 legs rc0 (dualrun streak37) + D-19 dual MATCH + push "
        f"074c10349..5e24d1fdb verified + orphan 0/27 + post_review tail zero x | "
        f"r1009: W245 seat watch (bm-c) + bm-a next own-wave derive after W245 chain + "
        f"queue-head claim per seed gate | 本地未达 origin commit 数=0\n")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)

print("STATE_OK epoch_int:", isinstance(d["heartbeat_epoch_utc"], int))
print("HEARTBEAT_OK epoch_int:", isinstance(h["heartbeat_epoch_utc"], int))
print("REPORT_APPENDED", now_iso)
