line = (
    "2026-09-26 16:4x | r260 addendum (bm-b) | S7 push-collision with bm-a r256 close (CN-REGIME-"
    "POLICY judged NEGATIVE full-arc + post_review check-ROT repair landed in-window) resolved: "
    "watchdog tick stash -> rebase -> 12-UU S6-face batch classified via conflict-resolve skill "
    "(10 classified + 2 UNKNOWN): daily_report json/md pair qualified per r242 precedent (json "
    "generated_at 16:28:21 > 16:20:47 -> take bm-b both, md whole-byte); snapshots x8 take-new "
    "whole (bm-b newer on every face 16:27-16:29 vs 16:19-16:20); compute_audit history "
    "identity-union 201+201->202 zero-loss asserted + latest take-new; regime_state "
    "transitions/history/triggers identity-union (identical dedupe) + state take-new; resolver "
    "results/_r260bmb_resolve.py; autofill_state stash-pop second conflict = committed face "
    "taken per R252 step-2 (HEAD launches ledger completeness carries bm-a 16:20:02 "
    "CN-REGIME-POLICY launch row; beaten local 16:30 tick dropped, watchdog self-heals); landed "
    "19732f51 + d8c4c514 on main; post-push double-scan orders 82/82 zero un-acked + tree "
    "clean; HANDOVER 5x check round (r260=5-multiple): anchor-insert r260 increment, r250 "
    "demoted, board facts = pool 47/47 done / post_review 748 rows 0 X / ledger 187,585 / "
    "orders 82/82"
)
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write("\r\n" + line + "\r\n")
print("addendum appended", len(line))
