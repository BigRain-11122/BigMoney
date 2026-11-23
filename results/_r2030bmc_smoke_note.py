"""r2030 smoke note: the full suite finished after the closeout -- record what it said.

The round report line said the full smoke had not returned and that no green was being
claimed.  It has now returned, so the same file is corrected with the actual verdict
instead of leaving the honest placeholder standing.
"""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

LINE = (
    "| 2026-11-24 06:4x | r2030 **addendum 2（全量 smoke 实际结果·修正上一行「未返回」）** | "
    "`python -m smoke_test` 收口后返回：**758/765 PASS · 6 FAIL · 1 UNVERIFIED**（wall 1163.6s / 763 腿，"
    "reused 59 腿·prefetched 3 早启）。**六红逐条判型（全部 STALE/页面代差，非算术缺陷，且无一在 r2030 新面）**："
    "①`the substitution rulers reach the CEO page (r1933)`=CEO 页缺 substitution 块（他机单写面）；"
    "②`etf_book_year_gate`=exit2「gate 面板停在 2026-11-20，官方日历已要 2026-11-2x」＝上游数据面落后；"
    "③`swap section freshness`=exit2「上面每一条腿都是 stale 不是错·去付它的 producer」；"
    "④`the sheet's swap-section freshness`=section=True live=STALE；"
    "⑤`a stale swap leg says who can move it`=waiting=3 own_producer_stale=7；"
    "⑥`the page names the board session the premium section never captured`=页面未印板缺、未印下次取数日 2026-11-24。"
    "**1 UNVERIFIED**=`the operator page prices the cash half` 比对的两张面（LIVE-BOOK-20261120.json / "
    "TICKET-2026-11-20.json）在本轮开始后被重写＝r1861 的「面在动」第三态，按律不计红。"
    "**处置**：六红的修法都要重算/刷新共享面（CEO 页、swap 节、数据面板），正是本窗竞争护栏（rc=3）禁止的动作，"
    "且对端 interactive 宿主 pid 51252 正在写这些面 → 本轮不修不碰，留作**无竞争窗第一优先**（与 r2022–r2030 接链腿同批）。"
    "**本轮新面复核**：`astock_veto_hedge_walkforward check` 仍 rc0（本面不在红单内）。｜"
    "记账：本行 1 处，本轮合计 5。 |\n"
)


def main() -> int:
    with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(LINE)
    print("smoke note appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
