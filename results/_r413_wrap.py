"""r413 wrap: state bump 412->413 + round report line + heartbeat update (S5/S7)."""
import glob
import json
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- state-bm-a.json: round_no +1 ---
st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 413
st["did"] = ("r412 stuck-rebase resurrect: 3 collision windows (7+18+6 UU) canon-resolved "
             "(classifier GREEN x3; ALL_FACES merge_lane_views resolve; 11 snapshots take-:2: by deep-ts probe "
             "= bm-b r408 lawful stale-takeover 04:11 faces; x2 multiset-union 1518 lines multiplicity-preserved "
             "sorted-by-ts) -> push LANDED e14911215; S0.5 orders 122/122 dual-scan (README.md false-positive "
             "excluded) + inbox empty + decisions.md no new repo-relevant lines; smoke 26/26; S6 36 legs rc=0")
st["verify"] = ("git push e14911215 landed; pool_dualrun ZERO-DRIFT streak 1/3; smoke 26/26 PASS; "
                "compute_audit FLAG pool_starvation+supply_floor (ready=0<3, streak 723.2min) honestly carried; "
                "regime ORANGE shadow; market clock ORANGE_COOL; x2 1524 lines monotonic")
st["next"] = ("W7 prereg draft candidate (TRIAL_LABOR_LAW standing line, next wave after bm-c r198 W6 freeze "
              "takeover); CODELY pit-law batch-83 (x2 multiset-union multiplicity law)固化 if not landed; "
              "supply_floor flag awaits W6 autofill ignition")
st["last_round_at"] = NOW
st["current_task"] = "r413: stuck-rebase resurrection + maintenance close"
st["updated"] = NOW
if "round" in st:
    st["round"] = 413
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state-bm-a.json -> round_no 413")

# --- round report line (bm-a file per fleet README sec.6) ---
cands = glob.glob("logs/iteration-loop/round_reports-bm-a.md") or glob.glob("round_reports-bm-a.md") or glob.glob("**/round_reports-bm-a.md", recursive=True)
assert cands, "round_reports-bm-a.md not found"
line = (f"{NOW} | r413 | WATERMARK VERDICT: GREEN (red=false, lane=healthy; py tail 5.3/4.9/4.8% low-load = "
        f"board 0 open + bandit moneyflow-IC claimed panel source-blocked self-heal = legal-idle face) | "
        f"did: r412 stuck-rebase RESURRECT (dead session 04:06 mid-rebase; 3 collision windows 7+18+6 UU "
        f"classifier-GREEN canon-resolved: ALL_FACES merge_lane_views resolve x6/x6/x6, 11+11 snapshots take-:2: "
        f"deep-ts probe = bm-b r408 lawful stale-takeover 04:11 fresher faces, x2_watch multiset-union 1518 "
        f"lines multiplicity-preserved ts-sorted vs batch-82 byte-prefix form, semantic equivalence asserted) "
        f"-> push LANDED e14911215 r412 full closure preserved; S0.5 122/122 orders dual-scan, inbox empty, "
        f"decisions.md no new repo lines; smoke 26/26; S6 36 legs rc=0 (update_daily 0-new-row pre-15:30 legal "
        f"no-op, scorecard S=2/A=4 re-derived, daily_report+ceo_live_usage+build_status written; paper legs "
        f"skipped no-new-bar by gate design; moneyflow+ah spawned detached self-heal) | verify: push e14911215, "
        f"pool_dualrun ZERO-DRIFT streak 1/3, compute_audit FLAG pool_starvation+supply_floor (ready=0<floor3, "
        f"supply streak 723.2min) HONESTLY CARRIED -- W6 prereg frozen by bm-c r198 healthy takeover (bm-a draft "
        f"stall >57min cited; W6 face = bm-c lane, zero touch this round), ignition expected to end starvation | "
        f"next: W7 prereg draft (standing line), CODELY batch-83 x2-multiset-law固化, supply floor watch\n")
with open(cands[0], "a", encoding="utf-8") as f:
    f.write(line)
print(f"report line -> {cands[0]}")

# --- heartbeat fleet/machines/bm-a.json ---
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = NOW
hb["current_task"] = "r413: r412 stuck-rebase resurrect (3-window canon resolve, push e14911215) + S6 36 legs rc=0"
hb["cpu_cores"] = 32
hb["verdict"] = ("green; r412 resurrected+pushed e14911215 (3 collision windows resolved canon-zero-loss); "
                 "orders 122/122; smoke 26/26; S6 36 legs rc=0; compute_audit FLAG pool_starvation+supply_floor "
                 "(W6 frozen by bm-c r198 takeover, ignition pending); W7 prereg draft = next standing-line step")
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = 413
if "round" in hb:
    hb["round"] = 413
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
re = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(re["heartbeat_epoch_utc"], int)
assert "T" in re["clock_read"]
print(f"heartbeat -> epoch={re['heartbeat_epoch_utc']} (int OK) clock={re['clock_read']}")
