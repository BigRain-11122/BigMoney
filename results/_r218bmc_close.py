"""_r218bmc_close.py -- r218 bm-c S7 closeout bookkeeping (state/heartbeat/report)."""
import json
import shutil
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state-bm-c.json
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 218
st["updated"] = ts
st["last_round_ts"] = ts
st["last_round_at"] = "r217"
st["did"] = ("S0 pull ff (bm-a r427 landed; MSG-1211 processed by bm-a zero double-flip) -> S0.5 orders 122/122 zero-diff + "
             "decisions zero new lines + MSG-1235 (ALL) processed: W8 freeze landed with my r117 MSG-1230 correction adopted "
             "same-commit (lane_owner bm-b + T-18 premise) -> smoke 26/26 -> S3 W8 runner-build slice CLAIMED first-claimer "
             "(heartbeat current_task commit f5fe5ee03 pushed 12:41 pre-bm-b-pin, commit-order law; spec TRIAL_LABOR_W8_PREREG.md "
             "FROZEN full absorption + probe reference _r423bmb_w8tstate_probe.py census-verbatim tstate_faces + SEED w8 3-key "
             "registry verified live) -> build deferred to r219 by round-budget law (no half-file risk; claim sticky) -> S6 "
             "37 legs ALL GREEN (reused generic chain runner results/_r424bmb_s6_chain.py anti-rebuild law) -> S7 close")
st["verify"] = ("orders diff programmatic 122/122; smoke 26/26; S6 chain rc0/rc1 only zero non-green; dualrun ZERO-DRIFT "
                "streak 25/3; regime ORANGE trigger breadth 0.83; clock ORANGE_COOL sleeves=4; LIVE-0929 state=ORANGE "
                "written; SEED_REGISTRY w8 keys live-verified [20306500,20307000,20307500]; claim commit f5fe5ee03 on origin/main")
st["next"] = ("r219: (a) W8 runner build tranche (claim held): scripts/trial_labor_w8.py = copy trial_labor_w7.py lineage + "
              "mechanical w7->w8 renames + SEED 3-key + GRAMMAR_FILE w8_grammar.json + import tl7 + tstate_faces "
              "census-verbatim from probe + eleven-tuple grammar builder (TSTATE axis {none,deep_pullback,oversold_rsv}) + "
              "exclusion eight-source/eight-list (W7_screen 284 added) + semantic-identity none==W7 baseline + selftest legs "
              "(hermetic + TSTATE causality 178/59 warmup + six-gate cross 64-cell 44-nonempty + probe anchors 383/632/"
              "3305/3424 + NaN-comparison artifact leg) then GENERATE pool entry lane_owner=null; (b) 15:30 window: fund_premium "
              "snapshot + paper chain regen; (c) W9 AMP berth untouched")
st["current_task"] = ("r218 closed: W8 runner-build slice claim held (f5fe5ee03 first-claimer; bm-b yield expected per "
                      "commit-order); frozen spec + probe reference fully absorbed; build = r219 tranche; S6 37 legs green")
st["updated_at"] = ts
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 2) heartbeat fleet/machines/bm-c.json
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.isoformat()
hb["current_task"] = st["current_task"]
hb["round_no"] = 218
hb["updated_at"] = ts
hb["verdict"] = ("healthy: smoke 26/26; S6 37 legs rc0/1; dualrun streak 25/3; WM chain-idle py 0 honest; "
                 "W8 runner-build claim held f5fe5ee03 build=r219")
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("state 218 + heartbeat epoch int", chk["heartbeat_epoch_utc"], "| clock", chk["clock_read"])

# 3) MSG-1235 (ALL) processed by this machine -> archive
src = "fleet/inbox/MSG-20260929-1235-bmb-ALL-W8-prereg-freeze.md"
dst = "fleet/inbox/processed/" + src.split("\\")[-1]
shutil.move(src, dst)
print("MSG-1235 archived ->", dst)
