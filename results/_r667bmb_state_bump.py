# -*- coding: utf-8 -*-
# r667 bm-b state.json round increment (r645: programmatic json.dump + json.loads self-verify)
import json, io, datetime

p = "state.json"
d = json.load(io.open(p, encoding="utf-8"))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["round_no"] = 667
d["last_round_at"] = now
d["round_no_label"] = ("bm-b round 667 (golden-week watch; trio V725/Q558/D410 of 2000 @~9-12/hr slowed; "
                       "S6 38/38 green; D-19 dual MATCH; origin merge integrated 0 UU)")
d["last_decisions_read_at"] = now
d["note"] = ("r667: golden-week watch round -- S0 pull --rebase benign-blocked by daemon 8 faces (r666 same), "
             "HEAD-vs-origin intersection zero -> merge origin/main clean 0 UU (r437 netpath) integrated "
             "bm-c r464-465 + bm-a r673 (58 files); D-19 decisions MATCH + group orders MATCH via "
             "sparse-clone raw-bytes probe (K: absent fallback D-20261004-02(3), r660 subprocess law, "
             "r458 per-key caliber); fleet orders 153/153 zero-unacked; S6 38/38 rc0 ALL-GREEN "
             "(dualrun ZERO-DRIFT streak 51; update_daily golden-week no-op legal; market_regime ORANGE; "
             "bm-a host faces guarded-skip fresh 18-19min; daily_report + live_usage regenerated); "
             "trio V725/Q558/D410 of 2000 healthy (3 burners CIM full-scan, dup_k=0 x3; rate slowed "
             "to ~9-12/hr/family, watch item next round); S7 attrition CLEAN + tasks/claws 4/4 + "
             "inbox zero unread")
d["ts"] = now
d["updated"] = now
d["last_seen"] = now
d["clock_read"] = now
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
# self-verify
chk = json.loads(io.open(p, encoding="utf-8").read())
assert chk["round_no"] == 667 and isinstance(chk["round_no"], int), "round_no verify failed"
assert "T" in chk["clock_read"], "clock_read format"
print("state.json round_no ->", chk["round_no"], "verify OK")
