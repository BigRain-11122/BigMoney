import io, os
from datetime import datetime, timedelta, timezone
ROOT = os.getcwd()
rep = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
row = (
"| " + stamp + " | r2029 **addendum**（送达核验） | commit **7a856f8642** 已推 origin/main"
"（456be3a780..7a856f8642），fetch 后 **AHEAD=0 / BEHIND=0**，git ls-tree -r origin/main 七件全在位"
"（scripts/astock_veto_hedge_band.py / results/astock_veto_hedge_band.json / research/ASTOCK_VETO_HEDGE_BAND.md / "
"负控 results/_r2029bmc_band_negative.py / 收口 _r2029bmc_closeout.py、_r2029bmc_hb_fields.json，"
"`_r[0-9]*` 走 `git add -f` 既有惯例）→ **本地未达 origin commit 数=0**。"
"**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
"集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
"`attrition_ledger_guard scan` **CLEAN**；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，首燃 06:05）；"
"`pre-commit` / `pre-push` 爪均与 Tools/git-hooks 源同（True/True）；fleet/inbox 0 件。"
"记账：本行 1 处（轮报告 addendum），本轮合计 4。 |\n"
)
with io.open(rep, "a", encoding="utf-8", newline="") as fh:
    fh.write(row)
print("appended", stamp)
