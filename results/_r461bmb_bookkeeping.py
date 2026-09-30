# r461 bookkeeping: state.json bump, round report append, heartbeat update (bm-b)
import json, time, datetime

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- state.json: round 461 ---
s = json.load(open("state.json", encoding="utf-8"))
s["round_no"] = 461
s["note"] = ("r461 CLOSED -- CRASH-RESUME: inherited dead mid-rebase state (r460 replay onto 9fdec68fb frozen at 19 UU, session died ~13:0x) "
 "RESOLVED per bigmoney-conflict-resolve canon in two batches and LANDED on origin as 93624d1ab: "
 "batch-1 (19 UU, resolvers results/_r460bmb_resolve.py): direction INVERTED vs normal -- replayed r460 S6 outputs 12:54-55 were NEWER than base 12:47-49 -> "
 "17 snapshots+js take-theirs(newer-ts, ts-dir asserts passed) + compute_audit union 206+201->207 zero-loss + regime union 3/3 + 2 background-write MM files (p1d_gates 13:10 rerun + marks +2 ticks) folded per r261 add-dirty law; "
 "push rejected (bm-a r472 landed 13:0x) -> rebase #2 batch-2 (32 UU, results/_r460bmb_resolve2.py): 20 ts-asserted snapshots + 8 paper/export faces take-:2 UNCONDITIONAL (post-RW-1-fix canonical, MSG-1330 do-not-revert red line; old-engine readings incl CE-01 OOS 1.7479->0.8620 are dead) "
 "+ marks take-:3 (base 35 strict subset of ours 38) + x2_watch line-union 1914+6+6->1926 + compute_audit union 201+207->208 HEALING bm-a r472 201-row regression + regime union; zero-loss asserts all passed. "
 "FREEZE COMPLIANCE: RW-5 freeze order in effect (MSG-1330 processed to inbox/processed) -- zero new prereg/slot/supply-line this round; pool 139/139 done; burn advisory honored (no engine-dependent batch in flight); "
 "S6 data-refreshes legal face ran 37/38 rc0 (minute_feed +98 rows real work, marks tick 18 pos, lane guards all honest skip, dualrun ZERO-DRIFT streak held) + lhb rc3 EM source-rewrite fail-closed 9th obs honest. "
 "ORDERS: 127/127 acked zero unacked (S0.5 double-scan; fleet/orders README.md excluded as non-order). DECISIONS: firm/DECISIONS.md tail 09-26 all consumed, group ../..docs/decisions.md absent on tree, zero repo-relevant new rows; D-20260930-05 RW-1~7 known via MSG-1330 receipt line here. "
 "NEXT r462: (a) 15:30 post-close unlock legs fire on the >=15:35 rounds (09-30 bars -> live.paper/t35/prospect accrue); (b) RW-1~4 unfreeze watch (bm-a T-127, <=48h -> 2026-10-02), W14 prereg drafting strictly after unfreeze; (c) 2026-10-01 00:00+ month-first trio (science_audit + monthly_briefing + self_review) fires on first October round; REGIME_GUARD v3 date-gate hands-off 10-01")
s["last_round_at"] = iso
s["last_round_ts"] = iso
s["ts"] = iso
s["updated"] = iso
json.dump(s, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report append (bm-b uses logs/iteration-loop/round_reports.md) ---
line = (f"{iso} | r461 bm-b | WATERMARK: green (13:10 probe red=false lane healthy; py_series 7.5/0.2/0.2 low BUT board 0 open + pool 139/139 done + RW-5 freeze in effect = lawful idle freeze face, same legal-idle class as bm-a r472 WM) | "
 "CURRENT-ACTIVE: r461 crash-resume -- inherited dead mid-rebase (r460 replay frozen at 19 UU) -> canon two-batch resolve -> LANDED 93624d1ab on origin main | "
 "LAST-ARTIFACTS: results/_r460bmb_resolve.py + results/_r460bmb_resolve2.py @13:1x (batch-1 19 UU: ts-dir-inverted take-theirs snapshots + compute_audit union 207 + regime union + r261 dirty-add p1d_gates/marks; batch-2 32 UU: 28 take-:2 incl 8 RW-1 post-fix canonical paper/export faces per MSG-1330 do-not-revert + marks take3 superset 38 + x2watch union 1926 + compute_audit union 208 HEALING bm-a r472 201-regression; zero-loss asserts printed) + r460 products now on origin (CEO-REPORT-WAVE13-20260930.md 48h face closes 10-02 12:28 + HANDOVER r456-460 rows) | "
 "NEXT-MILESTONE: 15:30 post-close unlock today (>=15:35 rounds: 09-30 bars -> live.paper/t35/prospect accrue); RW-1~4 unfreeze <=48h (bm-a T-127, 2026-10-02) then W14 prereg window opens -- within 48h | "
 "EVIDENCE: smoke 27/27 (bm-a RW-1 assertion suite now 27); S6 37 rc0 + lhb rc3 EM source-rewrite fail-closed 9th obs honest (bm-a r472 self-heal did not hold, lane quarantine standing); dualrun ZERO-DRIFT 51/3 @139; minute_feed +98 rows; marks tick 18 pos; lane_io guards honest skips 10x; attrition CLEAN 4 ledgers (2 healed); claw MATCH; loop task running (13:22 firing=this session); watchdog ready 13:40; orders 127/127 double-scan zero unacked; MSG-1315 (SLOT-11 zero-burn retraction, observed zero action) + MSG-1330 (RW-1 landed + RW-5 freeze + do-not-revert red line) both processed -> inbox/processed; MSG-1332 bma->bmc scope-division left for bm-c; heartbeat epoch int self-verified | "
 "NEXT-POINTER: r462+ today = 15:30 post-close unlock legs + freeze watch only (no burns until RW unfreeze); 2026-10-01 first round fires month-first trio (science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 date-gate auto-activates hands-off [via bm-b]\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)

# --- heartbeat fleet/machines/bm-b.json ---
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
h["last_seen"] = iso
h["current_task"] = "r461 crash-resume closure: r460 rebase two-batch canon-resolve landed origin (93624d1ab); RW-5 freeze compliance; S6 37/38 green (lhb rc3 quarantine honest)"
h["cpu_cores"] = 16
h["idle_ram_gb"] = 6.8
h["gpu_free_vram_mb"] = 2167
h["verdict"] = "idle_watch: RW-5 freeze lawful-idle face (pool 139/139 done, board 0 open); next unlock = 15:30 post-close bars"
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
d = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(d["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d["clock_read"]
print("BOOKKEEP-OK", iso, "epoch", epoch)
