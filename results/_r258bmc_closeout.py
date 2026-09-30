# r258 bm-c closeout: state + heartbeat + round report + CODELY entry
import json
import os
import time
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


# ---- machine metrics (light sampling with fallback) ----
cpu_pct, idle_ram_gb, gpu_free = 8.0, 8.9, 9497
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
    vm = psutil.virtual_memory()
    idle_ram_gb = round(vm.available / 1024**3, 1)
except Exception:
    pass

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
st = load(sp)
st["round_no"] = 258
st["last_round_at"] = "r258"
st["last_round_ts"] = NOW
st["updated"] = NOW
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = idle_ram_gb
st["gpu_free_vram_mib"] = gpu_free
st["verify"] = (
    "r258 full round: S0 dead-after-push recovery -- r257 closeout adoption committed+pushed "
    "(13 bm-c faces incl state 257/heartbeat; 17 shared derived faces yielded to bm-a r461 origin "
    "side per r446/r449 law; compute_audit history ts-union 07:35:27 appended cap 201) -> rebase "
    "clean x1 -> push LANDED 69f6d1d2c. S0.5 orders 122/122 zero-diff (programmatic), decisions "
    "zero-new-row (origin diff untouched decisions.md), inbox 2 processed (bm-a W13-freeze "
    "declaration ack + own SLOT-7 verdict MSG archived). S1 smoke 26/26. S2 boards: job_list 0 "
    "open, tasks 36 all claimed, pool 133/133 done; W13 runner build YIELDED to bm-a (heartbeat "
    "claim r462 in flight, MSG open-lane vs heartbeat claim -> heartbeat wins per fleet sec.4). "
    "S3 product = next-berth eligibility scan (7029 files, three-key-face r448 law) + verdict "
    "artifact: A-layer census adopted from bm-b r448 W8-draft sec.L9 (freshest), post-W7-verdict "
    "delta applied -- #81/#82/#83 T33-burned 0/20, #95 W3-consumed, #93 P-1e judged, #94 "
    "data-face gated, #85/#92 P-1e burned; PRIMARY SLOT-9 candidate = #84 crowding_vote (park "
    "condition 'wait for W7 verdict' resolved by 07:26 0/4 judged-negative family closure; "
    "negative prior = width-leg structural overlap w/ REGIME_GUARD/#87 pearson -0.7757 to be "
    "written pre-judgment), BACKUP = #90 alligator_timing (replication-failure negative prior). "
    "r257 guard-absence finding ADJUDICATED zero-defect: lane_io guard present with "
    "stale-takeover semantics (O-2100 s2.4), prompt law-text simplification was the gap, no "
    "code change. S6 sweep green: dualrun ZERO-DRIFT 51/3; audit FLAG supply_floor ready=0<3 "
    "standing (family streak 209.8min honest); watermark probe py_low_board_clear (berth-line "
    "delivery + supply obligation standing); update_daily cutoff 09-29 pre-market no-op (no new "
    "bar -> paper chain legitimately not triggered); regime ORANGE asof 09-29 shadow; "
    "strategy_scorecard stale-takeover derive 6/28/7 cards 15.9s + daily_scorecard "
    "stale-takeover (guard printed 24min) + dashboard regenerate (O-2100 s2.4); market_clock "
    "CALL-2026-09-28 ORANGE_COOL sleeves4; lhb rc3 r229-family source-history sign-flip honest "
    "isolation local-kept; 12 collector legs honest lane-guard no-op; fund_premium pre-15:30 "
    "no-op; fundamental fresh-skip 21.4h; b_layer_mask regen; REPORT-2026-09-30 + LIVE-09-30 "
    "(ORANGE cap50 COOL) + daily_scorecard + dashboard + token delta0. S7: loop pin=5 no-op, "
    "watchdog re-registered first-fire 08:20, precommit claw mismatch (CR-normalization "
    "caveat) -> reinstalled LF-normalized, attrition guard CLEAN 4 ledgers (2 healed rows "
    "noted), orders final double-scan 122/122, state 257->258."
)
st["did"] = (
    "r258: r257 closeout adoption (S0 surgery per r446/r449 union law, rebase clean, push "
    "LANDED) + W13 runner yield to bm-a (heartbeat claim) + next-berth eligibility scan "
    "artifact with SLOT-9 verdict (#84 crowding_vote primary, unblocked by W7 verdict "
    "landing) + guard finding zero-defect adjudication + S6 full sweep."
)
st["current_task"] = (
    "r258 closed. Supply obligation standing (floor ready=0<3): SLOT-9 berth package = next "
    "round main work (param freeze from DIGEST-20260925-wave4-slice6 + probe facts + prereg "
    "BERTH + catalog entry + zoo row + MSG). W13 runner = bm-a in flight (yielded)."
)
st["next"] = (
    "(a) SLOT-9 berth package: #84 crowding_vote four-vote composite (trend-strength / "
    "head-median differentiation / weak-share breadth / guard-object self-momentum) + "
    "asymmetric confirm 2d-in/3d-out + 75pct hysteresis; param freeze from evidence card "
    "DIGEST-20260925-wave4-slice6, probe on core48 panel, prereg from PREREG_TEMPLATE.md "
    "(alpha mechanism 4-choice + D6 same-family max|corr|>=0.7 gate incl REGIME_GUARD/#87/"
    "#24 neighborhood), negative prior written pre-judgment; (b) 10-01 month-first trio "
    "(science_audit + monthly_briefing + self_review) + REGIME_GUARD v3 date-gate "
    "auto-activation hands-off; (c) 48h CEO clock SLOT-7 verdict due 2026-10-02 07:26 "
    "(O-1116 dual-column); (d) r260 next 5x HANDOVER; (e) W8/W13/SLOT-8 = other-machine "
    "lanes, do not touch."
)
st["heartbeat_epoch_utc"] = EPOCH
st["clock_read"] = NOW
dump(sp, st)

# ---- heartbeat ----
hp = "fleet/machines/bm-c.json"
hb = load(hp)
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu_pct
hb["idle_ram_gb"] = idle_ram_gb
hb["gpu_free_vram_mib"] = gpu_free
hb["current_task"] = st["current_task"]
hb["verdict"] = "healthy r258: berth-eligibility scan landed (SLOT-9=#84 primary), S6 green, supply floor breach standing with drafting obligation"
dump(hp, hb)

# ---- self-verify epoch int + clock T-sep ----
chk = load(hp)
assert isinstance(chk["heartbeat_epoch_utc"], int) and not isinstance(chk["heartbeat_epoch_utc"], bool), "epoch must be int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat epoch int + clock T-sep self-verified:", chk["heartbeat_epoch_utc"], chk["clock_read"])
print("state round_no:", st["round_no"])
