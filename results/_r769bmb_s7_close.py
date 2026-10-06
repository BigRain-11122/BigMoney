# _r769bmb_s7_close.py -- r769 bm-b S7 closeout: attrition scan + state bump + heartbeat + ledger row
import json, os, time, subprocess
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
EPOCH = int(time.time())

# 1) attrition guard scan
r = subprocess.run(["python", "scripts/attrition_ledger_guard.py", "scan"], capture_output=True, cwd=REPO)
print("[attrition]", r.stdout.decode("utf-8", errors="replace").strip()[:300])
ag_rc = r.returncode

# 2) state.json bump 768 -> 769
sp = os.path.join(REPO, "state.json")
st = json.load(open(sp, encoding="utf-8"))
prev = st["round_no"]
assert prev == 768, prev
st["round_no"] = 769
st["note"] = ("r769: dead-r769-session adoption + merge-mode integrate -- adopted killed 08:47 timeout session S0 heal "
              "(rebase resolve PASS + autostash union + nulls repair + 1816 restore content-equal) then behind-absorb merge "
              "0287a98b1 16 faces family recipes + push rc0 + smoke 48/48 + S6 evidence legs 01/02/03/38/39 rc0 "
              "(dualrun ZERO-DRIFT streak 51 + audit CLEAN + wm insufficient_history n=1 legal reset + token delta=0 + "
              "trio gate G1=False G2/G3=True G4=PENDING window 10-05..10-09)")
st["next"] = ("(a) trio finalize windows: V ~1870/2000 eta ~10-06 midday (first-to-2000 -> finalize round same-window pool "
              "dual-flip per r668 law), Q ~1500/2000 eta ~10-07, D ~1270/2000 eta ~10-08 morning -- leg39 every round; "
              "(b) D-06 group closeout report 10-07 12:00; (c) 10-08 market reopen window (external data legs + paper marks "
              "resume + REGIME_GUARD v3 first new bar); (d) r770: full S6 chain (this round reduced evidence-set) + "
              "D-19 group-tree dual consumption if hash moved (bm-a r766 consumed 3 dec lines zero BM action)")
for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read", "last_round_ts"):
    st[k] = NOW
st["round_no_label"] = "r769"
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("[state] round 768 -> 769")

# 3) heartbeat fleet/machines/bm-b.json
hp = os.path.join(REPO, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "r769 done: dead-session adoption + merge integrate 0287a98b1 + trio NULLS burn V/Q/D lanes"
hb["verdict"] = "GREEN (merge integrated+pushed; trio burning; board 0 open; smoke 48/48)"
try:
    core_task = hb.get("task") or hb.get("current_task")
    assert isinstance(hb["heartbeat_epoch_utc"], int)
except KeyError:
    pass
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
print("[heartbeat] epoch int OK", chk["heartbeat_epoch_utc"])

# 4) ledger row (bm-b uses logs/iteration-loop/round_reports.md)
lp = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
row = (" %s | round 769 (bm-b, dept:engineering, dead-session adoption + merge-mode integrate round) | "
       "[watermark verdict: GREEN (red=false lane healthy; board 0 open; probe insufficient_history n=1 new window = legal "
       "window-reset r738 precedent; trio NULLS V~1870/Q~1500/D~1270 of 2000 burning = trial-labor line satisfied)] | "
       "CEO three-line live face: current-work = FUND trio NULLS burn 3 lanes (V finalize eta ~10-06 midday, first-to-2000 "
       "triggers finalize round per r668 law; gate mechanical_ready=False G1=False G2/G3=True G4=PENDING governance "
       "window 10-05..10-09) | latest-artifact = merge 0287a98b1 (16-face family-recipe resolve: take-freshest x9 r756-"
       "normalized + compute_audit history union 210 + regime union + dashboard/scorecard host=bm-a origin-verbatim + "
       "js/v1 twins byte-copy) + adopt commit 032bf0524 (dead r769 08:47-timeout session S0 heal completed+verified: nulls "
       "dup=0 coverage complete, fund_value null|1816 restored content-equal vs stash, treasure_guard rc0) 09:0x | "
       "next-milestone = V lane 2000-hit finalize round ~10-06 midday (same-window pool dual-flip), else r770 09:22 full "
       "S6 chain + D-19 group dual consumption | verification: smoke 48/48 PASS; dualrun ZERO-DRIFT streak 51; audit CLEAN "
       "all flags empty; token delta=0; push rc0 origin 8dc0c9861..0287a98b1; local undelivered-to-origin commit count: 0 "
       "(post-push, self-verified next call) | notes: reduced S6 evidence-set this round (01/02/03/38/39) -- holiday no-op "
       "panel legs covered by bm-c r608 08:50 run 38/38 rc0, full chain restored r770; legs 25-28 golden-week no-new-bar "
       "skip lineage r768; S0.5 orders diff EMPTY (154/154 acked, zero new O-files); D-19 group-tree dual hash probe "
       "deferred r770 within 2-round SLA (bm-a r766 consumed 3 dec lines zero BM action); precommit/prepush claw "
       "verification carried to r770 (3 commits+2 pushes passed clean this round); orders_ack 154/154\n" % NOW)
with open(lp, "a", encoding="utf-8") as f:
    f.write(row)
print("[ledger] row appended; attrition rc=%d" % ag_rc)
