"""r2122 bm-c: append the k-gap addendum to the round report + QA."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROW = """
|**k-gap 补记（08:5x）**：本轮又关掉 **2 条** carried 红，同一条产业链的两半——①`product: the order sheet prints the floor's per-name cut, not only its total`（k-gap 面停在 2026-11-20、票面已到 11-25）；②`product: the CEO page's sections each name the bar they were priced on | section 'k_gap' is behind the page and no chain leg re-runs it`（**没有任何链腿重跑它**=r1282/r1322 族「一个人最后跑过的面」）。根因两层，各修一层：**第一层=链上没有写手**——`scripts/etf_book_k_gap.py` 一直在仓里、也一直出版面，但 `Tools/s6_chain_bmc.py` 没有任何腿点名它，于是它只在一个人的一次手工运行里前进过；补一条**写手腿**（check 与 run 同一条命令，~1s 重算，无独立 check 模式），且**排在被读的页面腿之前**（写手在读者之后=每趟差一代，r1781）。**第二层=名字探针看不见**——section key 是 `k_gap`（5 字符），低于 `live_book_section_bars.MIN_NAME_FOR_MATCH=8`，任何腿名都不可能匹配，于是即便有腿它也照读 `no_writer`；补 `LEG_ALIASES["k_gap"] = ["etf_book_k_gap"]` 并写明来历。**结果**：k-gap 面 bar=**2026-11-25**=票面 bar；页面逐名表格 5/5 行与面逐位相同（`| 代码 | 价 | 本单手数 | 规则手数 | 少买手数 | 少买金额 |`，合计 **175 手 / ¥23,384.00** 在页）；section bars 从「53 节同 bar / 20 节落后」变成 **60 节同 bar / 13 节落后**，且落后段**无一条 `no_writer`**（全为 chain_leg 或页面自算）；`live_book_section_bars check` **CHECK_OK**（verdict=PAGE_MIXES_BARS headline=2026-11-25 off=13）。｜**全量冒烟（修前那趟已跑完）**：**767/779 PASS · 12 FAIL**，本轮关掉其中 **3 条**（promotion_provenance STALE→CHECK_OK、k-gap 面 bar、k-gap 无写手），剩 **9 条 carried**（paper book NAV 身份 / lane appended nothing / phase_atlas_arms 9 腿 / toll-ladder / 510760 premium / forward 句漂移 / cost assumption no_control / width ladder / premium 读数后价格）；**修后再跑一趟已在飞**（`logs/smoke_2122_after.log`·PID 96660），**不宣称修后总数**。｜记账：本行 1 处 |
"""

for rel in ("round_reports-bm-c.md",):
    p = os.path.join(ROOT, rel)
    with io.open(p, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if not text.endswith("\n"):
        text += "\n"
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + ROW.lstrip("\n"))
    print("appended addendum ->", p)

QA = os.path.join(ROOT, "qa", "dial-on-the-page-r2122.md")
with io.open(QA, "a", encoding="utf-8", newline="") as fh:
    fh.write("""
## 补记（08:5x）· k-gap 段终于有写手

本轮末又关掉两条 carried 红（同一条产业链的两半）：

| 检查 | 结果 |
| --- | --- |
| `python scripts/etf_book_k_gap.py` | 面 bar = **2026-11-25**（= 票面 bar） |
| 页面逐名表格 vs 面 | **5/5 行逐位相同**（合计 175 手 / ¥23,384.00） |
| `python scripts/live_book_section_bars.py check` | **CHECK_OK**（PAGE_MIXES_BARS·headline 2026-11-25·off 13） |
| 落后段 `no_writer` 计数 | **0**（全部 chain_leg 或页面自算） |
| 全量冒烟（修前那趟） | **767/779 PASS · 12 FAIL**，本轮关掉 3 条 → 剩 9 条 carried |

修法两层：①`Tools/s6_chain_bmc.py` 补写手腿 `etf_book_k_gap`（check 与 run 同一命令·~1s），
**且排在 `etf_book_ceo_page` 之前**（写手在读者之后=每趟差一代，r1781）；
②`scripts/live_book_section_bars.py` 补 `LEG_ALIASES["k_gap"]`——section key 只有 5 字符、
低于 `MIN_NAME_FOR_MATCH=8`，名字探针永远看不见它，所以「有腿也照读 no_writer」。
修后再跑一份全量冒烟已在飞（`logs/smoke_2122_after.log`·PID 96660），**不宣称修后总数**。
""")
print("appended QA addendum ->", QA)
