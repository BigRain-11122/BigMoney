"""r431 bm-a push-closeout addendum append (file-face, CJK-safe)."""
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
line = (
    f"{NOW} | r431 addendum | push-closeout: push#1 rejected (origin advanced mid-round) -> pull --rebase 17-UU "
    "canon-resolved (6 ALL_FACES merge_lane_views + 11 snapshot/twin/js _r431bma_resolve deep-ts probes, "
    "ALL took :3: replay-side = my 14:02-14:05 S6 run newer than origin 13:49-13:50 stale-window faces, "
    "all parse-verified) -> push#2 rejected AGAIN (same-window storm continues, third machine advance) -> "
    "per D-20260925-01(3) pushed origin machine/bm-a-r431; merge-back = next bm-a round S0 first action "
    "(pit-93 pointer, r430 precedent). Note: prior r430 merge-back completed clean this round "
    "(c25577b88..5d6a6f55c) before the storm resumed.\n"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("addendum appended:", NOW)
