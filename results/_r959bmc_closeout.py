# -*- coding: utf-8 -*-
"""r959 bm-c closeout: round report line + state-bm-c.json + heartbeat writes.
All narrative faces composed here; machine stats sampled live; epoch int + T-format
clock asserted before write (R170/R178/R262 laws)."""
import json
import time
import datetime as dt

sys_tz = dt.timezone(dt.timedelta(hours=8))
now = dt.datetime.now(sys_tz)
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ROUND_LINE = ("| " + ts_iso + " | r959 | bm-c: W228 FULL CYCLE completed same-window (absorb 16th instance: dead r959 window ran editor derive + five-face freeze splice on disk 08:19:16 (receipt pf cd94b040->f4347ccd / n1 2dd9a003->aed7ae3d) + engine mtime-watch self-burn 12/12 (ledger appends 03bca8089+95e210be1 self-committed), died pre-commit -- this window machine-verified estate (sha16 receipt-match both faces + py_compile both + WAVE row census 227/228=1/1 shape-correct + N1_BANDS[228]==receipt bands) -> splice estate commit 842f817ad -> SIX-GATE PRE-FINALIZE ALL GREEN correct-phase = results/_r959bmc_w228_sixgate_prereg.json (third consecutive correct-phase wave per W217-debt standing law) -> finalize one-pass PID 2968 = ledger identity 923,189+2,200=925,389 EXACT + merged K=497,320+2,200=499,520 EXACT vs sixgate ledger_pre projection, merged mu -0.09272118173446509 sigma 0.24508298198205417, w228-only mu -0.08495759090909091, skill_line_v2 1.1918->1.1918 @n_eff 923,189 K-lift +0.0, voids LOWAMP-P1/P2 -> FIVE-KEY ALL PASS key1 0.00776<0.02/key2 +0.00235pct<10pct/key3 A p95 0.32 vs W227 0.3206 diff 0.0006<0.05/key4 0.0 = results/_r959bmc_w228_fivekey_receipt.json -> sec.7/8 machine-read backfilled into PERPETUAL_N1_W228_PREREG.md placeholders=0 (se_mu chain 0.000348->0.000347 narrowed; W229+ projection A 518_404..520_403/B 518_604..518_803 EIGHTY-NINTH anticipated) -> closeout 6744db794 pushed origin-verified) + W229 SEAT PUBLISHED same-window (probe derive verbatim bare228=47/bare227=57 pairs count-asserted residual zero py_compile green, one bloodline delta disclosed: receipt-name pair not needed source date already 20261013; probe rc0 ADMIT A 518_604..520_603 EIGHTY-NINTH staircase instance hops=1 naive 518_404 refused by registered W228 B + B 520_604..520_803 own-A mutual exclusion hops=1; seed_admit FREE x2 base=518604/base=520604; conflicts=0; origin vacancy 4-checks held; leg4 W230+ projection A 520_604..522_603/B 520_804..521_003 NINETIETH anticipated; anchor W228 ledger 925,389 K=499,520 leg0 machine-read; seat MSG-20261013-0855 pushed BEFORE freeze per r565; commit c9e9e83b8) | S0.5 dual-delta FALSE both windows + S7 double-scan same (dec fb5825cb/ord d559e530, unacked=0) | S1 smoke 49/49 | satengine rc0 ALIVE | S6: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG pool_starvation/supply_floor structural (answered by W229 seat, chain continues) + wm insufficient_history fresh-window honest local_batch_running finalize + update_daily 0 new rows (Tuesday bars pending 15:30 papers window) + market_regime rc0 + market_clock CALL-2026-10-12 ORANGE_COOL sleeves=4 + fund_premium no-op pre-15:30 + regime_thermo Money02-face absent honest no-op + fundamental fresh-skip 14.1h + b_layer rc0 + daily_report REPORT-2026-10-13 + ceo_live_usage LIVE-2026-10-13 (ORANGE cap 50% heat COOL) + token_meter delta=0 | attrition 4 CLEAN | S7 quad green (loop pin=5 + watchdog + both claws installed) + round-zero probe py_faces=5 orphans=2 zero-kill | idle_trigger green_idle=false (RAM 13.4% far below 40% gate, VRAM 14.51G disclosure-only per T-183; no obligation) | counter 959->960 | W229 prereg derive = next window FIRST ACTION |\n")

# 1) round report append (anchor tail, append-only)
rr_path = REPO + r"\round_reports-bm-c.md"
rr = open(rr_path, encoding="utf-8").read()
assert rr.rstrip().endswith("W228 five-face freeze splice = next window FIRST ACTION |"), "round report tail anchor mismatch"
open(rr_path, "a", encoding="utf-8", newline="").write(ROUND_LINE)

# 2) state-bm-c.json update
st_path = REPO + r"\state-bm-c.json"
st = json.load(open(st_path, encoding="utf-8"))
prev_round = st["round_no"]
assert prev_round == 959, "expected state round_no 959, got %s" % prev_round
st["round_no"] = 960
st["loop_round"] = 960
st["last_round"] = 959
st["clock_read"] = ts_iso
st["ts"] = ts_iso
st["updated"] = ts_iso
st["updated_at"] = ts_iso
st["last_round_at"] = ts_iso
st["last_round_closed"] = ts_iso
st["last_round_ts"] = epoch
st["last_ts"] = epoch
st["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_seen_at"] = ts_iso
st["last_round_summary"] = ("r959: W228 FULL CYCLE (absorb 16th: splice estate verified+landed 842f817ad + six-gate PRE-FINALIZE ALL GREEN + finalize 925,389/K 499,520 EXACT + five-key ALL PASS + sec.7/8 backfilled -> 6744db794) + W229 seat published (rc0 ADMIT A 518_604..520_603/B 520_604..520_803, c9e9e83b8); counter 959->960")
st["last_round_summary_at"] = ts_iso
st["last_action"] = "r959 closeout (W228 full cycle absorb + W229 seat publish + S6 light + S7 quad)"
st["last_action_at"] = ts_iso
st["last_artifact"] = "results/perpetual_faces/n1_w228_results.json + research/PERPETUAL_N1_W228_PREREG.md (sec.7/8 backfilled) + results/_w229bmc_20261013_probe_receipt.json"
st["latest_artifact"] = st["last_artifact"]
st["recent_artifact"] = st["last_artifact"]
st["current_task"] = "r960 W229 prereg derive (bloodline clone of committed _w228 prereg derive + lineage replay preflight)"
st["current_task_at"] = ts_iso
st["current_task_ts"] = ts_iso
st["did"] = ("r959 (W228 full cycle absorb + W229 seat): (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill; S0 fetch behind=0/ahead=0, round-start dirty=own live faces + uncommitted splice estate (dead r959 window); (2) S0.5 dual-delta FALSE both + S7 closeout double-scan same (unacked=0); (3) S1 smoke 49/49; boards clear; satengine rc0 ALIVE; (4) PRODUCT-1 = W228 FULL CYCLE: splice estate machine-verified (sha16 receipt-match + py_compile + WAVE census + N1_BANDS==receipt bands + shards 12/12 + finalize-absent proof) -> commit 842f817ad -> six-gate PRE-FINALIZE ALL GREEN (banned ADMIT + pf 9/9 + n1 selftest + shards 12/12 + seed_admit FREE x2 + WAVE_CONFIGS[228] row + ledger_pre projection) -> finalize one-pass (ledger 923,189+2,200=925,389 EXACT; merged K 499,520 EXACT; skill_line 1.1918 flat K-lift +0.0) -> five-key ALL PASS -> sec.7/8 backfilled placeholders=0 -> 6744db794 pushed; (5) PRODUCT-2 = W229 seat published: derive verbatim (bare228=47/bare227=57, one disclosed delta: receipt-name pair unneeded) + probe rc0 ADMIT (A 518_604..520_603 EIGHTY-NINTH hops=1; B 520_604..520_803 own-A hops=1; seed FREE x2; leg4 W230+ NINETIETH anticipated) + MSG-20261013-0855 pushed pre-freeze -> c9e9e83b8; (6) S6 light: dualrun streak 51 + audit FLAG structural answered-by-seat + wm honest + update family no-ops (pre-15:30) + daily_report/ceo_live_usage/token rc0; (7) S7 quad green + attrition 4 CLEAN; counter 959->960")
st["verdict"] = ("green: W228 FULL CYCLE LANDED (ledger 925,389 / K 499,520 EXACT; five-key ALL PASS; six-gate PRE-FINALIZE correct-phase third consecutive; sec.7/8 backfilled) + W229 SEAT PUBLISHED (rc0 ADMIT A 518_604..520_603 / B 520_604..520_803, MSG pushed pre-freeze) + smoke 49/49 + dualrun streak 51 + attrition CLEAN + S7 quad green; audit FLAG pool_starvation/supply_floor structural answered by W229 seat (chain continues prereg -> splice -> burn -> six-gate -> finalize)")
st["activity_now"] = ("2026-10-13 08:4x | r959 | bm-c: W228 full cycle landed (925,389/K 499,520, five-key pass, 6744db794) + W229 seat published (rc0 ADMIT, c9e9e83b8); counter 959->960")
st["now_active"] = st["activity_now"]
st["next_pointer"] = ("r960: (1) W229 prereg derive FIRST ACTION (bloodline clone of committed _w228bmc_prereg_derive.py; lineage replay preflight; finds machine-generated from committed _w228 SUB new-sides; bands A 518_604..520_603 / B 520_604..520_803 per ADMIT receipt _w229bmc_20261013_probe_receipt.json; S5 anchors machine-read W228 ledger 925,389 / K 499,520 / mu -0.09272118 / sigma 0.24508298 / A p95 0.32 / KL 1.1918 +0.0000 / se_mu 0.000347) -> five-face freeze splice (clone committed _w228bmc_freeze_edits.py per receipt) -> engine self-burn 12/12 -> PRE-FINALIZE six-gate (W217-debt standing law) -> finalize one-pass -> five-key + sec.7/8 backfill; (2) Tue 15:30 new-bar window: papers full chain + update family; (3) W230 seat publish after W229 finalize per seat-first law; (4) W230+ projection A 520_604..522_603 / B 520_804..521_003 NINETIETH anticipated (A-hops-prior-B)")
st["next"] = st["next_pointer"]
st["next_milestone"] = ("W229 prereg derive + splice + burn + six-gate + finalize (next window first action per chain law); Tue 15:30 new-bar papers full chain")
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = epoch
st["r959_absorb_note"] = ("r959 absorb note: prior session (labeled r959) executed the W228 freeze-splice body: editor derive (_w228bmc_derive_editor.py 08:18:40 -> _w228bmc_freeze_edits.py 08:18:56) + splice on disk (receipt 08:19:16, pf cd94b040->f4347ccd / n1 2dd9a003->aed7ae3d) after which the engine daemon mtime-watch self-burned 12/12 (batched ledger appends 03bca8089 08:19:19 + 95e210be1 08:22:00 self-committed), then died pre-commit (state frozen at 959) -- this session absorbed per the bm-c absorb precedent lineage (r894/r897/r907/r911/r915/r917/r919/r921/r928/r930/r933/r941/r947/r951/r956, 16th instance): splice estate machine-verified before landing (842f817ad), six-gate + finalize + five-key + sec.7/8 executed THIS window correct-phase, W229 seat published same-window; counter advanced 959->960 so next session = r960; zero double-count: S0.5 dual-delta FALSE both windows (dec fb5825cb / ord d559e530 both current, zero consumption owed)")
st["r959_closeout_note"] = ("r959: (1) S0-1 anchor bm-c + probe py_faces=5 orphans=2 zero-kill + fetch 0/0 (no rebase needed); (2) S0.5 dual-delta FALSE both + S7 double-scan same; (3) smoke 49/49; (4) W228 full cycle (see r959_absorb_note + did); (5) W229 seat (probe derive + ADMIT + MSG pre-freeze); (6) S6 light streak 51 + FLAG structural answered-by-seat; (7) S7 quad green + attrition 4 CLEAN + idle_trigger green_idle=false RAM-gate honest; pitfall same-window: none new (backfill self-check needle comma-format false-fail fixed in-script idempotent guard)")
st["prod_lanes"] = ("GPU=MV i2v lane idle (night batch 4 clips + reshakes landed per r952/r953 notes; director re-shakes + assembly ride bm-a lane); CPU=N1 W228 FULL CYCLE LANDED (925,389 / K 499,520) + W229 SEATED + seat MSG pushed (prereg derive = next window first action per chain law)")
st["sync"] = {
    "origin_tip": "c9e9e83b8 (W229 seat published; r959 closeout rides this window)",
    "ts": ts_iso,
    "ahead_behind": "0/0 post-push (re-verify at commit)",
    "note": "r959: W228 full cycle absorb + W229 seat + S6 light + S7 closeout; state/heartbeat this round",
}
st["head_sha"] = "quant: c9e9e83b8 (pre-closeout) -> closeout commit rides; group-tree: 5f69a62 (unchanged this window)"
st["health"] = "ok"
json.dump(st, open(st_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# 3) heartbeat fleet/machines/bm-c.json
hb_path = REPO + r"\fleet\machines\bm-c.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["round_no"] = 960
hb["last_round"] = 959
hb["clock_read"] = ts_iso
hb["ts"] = ts_iso
hb["updated"] = ts_iso
hb["updated_at"] = ts_iso
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
hb["last_seen_at"] = ts_iso
hb["last_round_at"] = ts_iso
hb["last_round_ts"] = epoch
hb["last_ts"] = epoch
hb["heartbeat_epoch_utc"] = epoch
hb["last_round_closed"] = ts_iso
hb["last_round_summary"] = st["last_round_summary"]
hb["last_round_summary_at"] = ts_iso
hb["last_action"] = st["last_action"]
hb["last_action_at"] = ts_iso
hb["last_artifact"] = st["last_artifact"]
hb["latest_artifact"] = st["last_artifact"]
hb["recent_artifact"] = st["last_artifact"]
hb["current_task"] = st["current_task"]
hb["current_task_at"] = ts_iso
hb["current_task_ts"] = ts_iso
hb["did"] = st["did"]
hb["verdict"] = st["verdict"]
hb["activity_now"] = st["activity_now"]
hb["now_active"] = st["activity_now"]
hb["next_pointer"] = st["next_pointer"]
hb["next"] = st["next_pointer"]
hb["next_milestone"] = st["next_milestone"]
hb["orphan_face"] = 2
hb["orphan_faces"] = 2
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["prod_lanes"] = st["prod_lanes"]
hb["r959_absorb_note"] = st["r959_absorb_note"]
hb["r959_closeout_note"] = st["r959_closeout_note"]
hb["head_sha"] = st["head_sha"]
hb["health"] = "ok"
json.dump(hb, open(hb_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# 4) self-verification (R170/R178/R262 laws)
st2 = json.load(open(st_path, encoding="utf-8"))
hb2 = json.load(open(hb_path, encoding="utf-8"))
for face, obj in [("state", st2), ("heartbeat", hb2)]:
    e = obj["heartbeat_epoch_utc"]
    c = obj["clock_read"]
    assert isinstance(e, int) and not isinstance(e, bool), face + " epoch not int"
    assert "T" in c and "+" in c and " " not in c, face + " clock not T-format: " + c
    assert obj["round_no"] == 960, face + " round_no != 960"
rr2 = open(rr_path, encoding="utf-8").read()
assert rr2.rstrip().endswith("W229 prereg derive = next window FIRST ACTION |"), "round report append failed"
assert rr2.count("| r959 |") == 1, "r959 line count != 1"
print("CLOSEOUT-WRITES-OK")
print("ts:", ts_iso, "| epoch:", epoch, "| counter 959->960 | r959 line appended")
