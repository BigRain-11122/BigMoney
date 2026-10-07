# -*- coding: utf-8 -*-
"""r725 bm-c S7 addendum: push-race window receipt (pre-push claw correct
intercept on phantom deletion set from mid-window origin advance; r437
net-path rebase resolution; delivery self-verified). Appends one line to
the round report and updates the state note field."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

line = (
    TS + " | r725-S7\u9644\u52a0 | S7 push-race \u7a97\u5b9e\u5f55\uff1apre-push \u722a\u6b63\u62e6"
    "\uff08\u63a8\u7a97=origin \u76d8\u4e2d\u524d\u8fdb bm-a r860 \u4e09 commit"
    "\uff08bc3e9fec8 W16 screen finalize+judge seat enroll/e2a9cd61e S0 absorb/"
    "552862e6b autofill claim\u00b703:49:59-03:51:05\uff09\u00b7\u672c\u673a HEAD \u5bf9\u65b0 "
    "origin \u542b bm-a \u5c5e\u4e3b\u4ef6\u5e7b\u5f71\u5220\u9664\u96c6\uff08_r860bma_* 7 \u4ef6"
    "+trial_labor_w16 3 \u4ef6\u00b7\u722a\u5c5e\u4e3b\u95e8\u6b63\u6267\u6cd5\u96f6\u7ed5\u8fc7"
    "\uff09\uff09\u2192r437 \u51c0\u8def\uff1afetch \u5b9e\u6838\uff08ahead=1/behind=3\uff09"
    "\u2192pull --rebase 1/1 \u96f6\u51b2\u7a81\uff08\u672c\u673a 577b05c83\u2192\u91cd\u653e "
    "17aef9efa\uff09\u2192push DELIVERED 552862e6b..17aef9efa\u2192\u53cc\u96f6\u81ea\u8bc1"
    "\uff08ahead=0/behind=0\u00b7commit \u540e push+fetch+rev-list\uff09 | \u722a\u62e6\u622a"
    "\u5b9a\u6027=\u5047\u9633\u6027\u65cf\u6b63\u786e\u6267\u6cd5\u9762\uff08\u5e7b\u5f71\u5220"
    "\u9664\u96c6=origin \u524d\u8fdb\u7ade\u6001\u975e\u771f\u5220\u9664\u610f\u56fe\u00b7\u51c0"
    "\u8def rebase \u5373\u6839\u6cbb\u00b7--no-verify \u9003\u751f\u53e3\u672a\u7528\uff09 "
    "[via bm-c r725]\n"
)

rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)

sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["note"] = (st.get("note", "") +
              " S7 push-race: pre-push claw correct intercept (phantom deletion set "
              "from mid-window origin advance, bm-a r860 trio) -> r437 net-path "
              "rebase 1/1 zero-conflict (577b05c83 replayed as 17aef9efa) -> push "
              "DELIVERED 552862e6b..17aef9efa, ahead=0/behind=0; no-verify hatch "
              "unused.")
st["last_round_summary"] = (st.get("last_round_summary", "") +
                            " S7 push-race claw-intercept resolved net-path "
                            "(rebase 1/1, DELIVERED 17aef9efa, 0/0).")
st["last_action"] = st["last_round_summary"]
st["verify"] = (st.get("verify", "") +
                " + S7 addendum: push DELIVERED 552862e6b..17aef9efa "
                "(ahead=0/behind=0 fetch+rev-list self-verified)")
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must stay JSON int"
assert "17aef9efa" in chk["note"], "addendum missing"
print("addendum appended @", TS)
