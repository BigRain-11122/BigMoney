# r593 bm-b: delivery accounting addendum line
import datetime as dt

now = dt.datetime.now().astimezone()
stamp = now.strftime("%Y-%m-%dT%H:%M") + "+08:00"
line = (
    f"| {stamp} | r593 delivery | round 593 closeout pushed FF 79e1812d8..2c51c7165 "
    "(pre-push claw pass, deletion-set = inbox MSG archive-move only, whitelisted); "
    "delivery self-check: fetch + rev-list origin/main..HEAD = 0, ls-tree confirms "
    "dashboard.html face on origin; 本地未达 origin commit 数=0"
)
with open(r"logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write("\n" + line + "\n")
print("addendum written")
