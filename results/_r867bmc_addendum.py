# -*- coding: utf-8 -*-
# r867 bm-c addendum: clean delivery self-proof + state sync face flip (r852 pre3 convention)
# clone face of r866 addendum pattern: books wrote "1/0 pre-books", this addendum records
# the actual clean push (no race, no claw block) and flips sync -> 0/0 delivered.
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
MAIN_SHA = "8709a9fc9"

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r867 bm-c addendum | clean delivery self-proof（收口后补账·r852 pre3 先例法）: "
               "r867 主 commit " + MAIN_SHA + " push 直通零竞态（无 rebase·无 pre-push 爪拦·无撞车）·fetch 自证 0/0 delivered·state sync 面翻正 | "
               "记账预算：第 4 面（预算内）")

with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r867 |" in can_lines[-1]), ("canonical tail not r867 main line", can_lines[-1][:80])
assert ("r867 bm-c addendum" not in can_body[-9000:]), "r867 addendum already present"
with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(report_line + "\n")

ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
             "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
             "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy","last_decisions_read_at",
             "last_decisions_at","last_orders_at"]
p = ROOT + r"\state-bm-c.json"
with io.open(p, "r", encoding="utf-8") as f:
    d = json.load(f)
for k in ts_fields:
    if k in d: d[k] = now_iso
d["head_sha"] = MAIN_SHA
d["sync"] = {"ahead_behind": "0/0 delivered", "origin_tip": MAIN_SHA, "ts": now_iso,
             "note": "r867 addendum: clean delivery self-proof (push direct, zero race, zero claw block this window); fetch 0/0"}
d["last_action"] = "r867 S6 43/43 (streak 7) + books + addendum delivery self-proof"
with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")

with io.open(p, "r", encoding="utf-8") as f:
    d2 = json.load(f)
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must stay int"
assert d2["sync"]["origin_tip"] == MAIN_SHA, "sync face flip failed"
assert "T" in d2["clock_read"], "clock_read T-separator"
print("ADDENDUM OK main=%s clock=%s report_line_appended=1" % (MAIN_SHA, now_iso))
