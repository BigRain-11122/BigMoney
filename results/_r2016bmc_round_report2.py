import io

ROW = (
    "| 2026-11-24 01:2x | r2016 **addendum**（送达核验 + 一处口径说明） | "
    "commit **c28ffaa973** 已推 origin/main（155d4fa7b0..c28ffaa973），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r origin/main` 六件 blob 在位（scripts/astock_veto_turnover_band.py / "
    "results/astock_veto_turnover_band.json / research/ASTOCK_VETO_TURNOVER_BAND.md / "
    "负控 results/_r2016bmc_turnover_band_negative.py / 收口 _r2016bmc_round_report.py 与 _r2016bmc_hb_fields.json，"
    "`_r[0-9]*` 走 `git add -f` 既有惯例）→ **本地未达 origin commit 数=0**。"
    "**口径说明（读者会追问的两个数）**：①「税只省 0.02 bp」听起来像带子没生效，其实它生效了——"
    "换手确实降了（23.95%→23.86%），只是降的幅度太小：这条账每期换掉的是 q 排名在大盘中部翻动的那一层，"
    "而带子只管「被踢出后何时回来」这一条边，两者量级差一个数量级；"
    "②band_4_2 与 band_4_1 的净差（+2.70 / +3.41 bp）大而 t 反而低（1.85 / 1.05），不是算错，"
    "是两本书共享约四分之三的名字、逐期差值的方差被放大：**均值变大但一致性变差**，"
    "所以判词只写到 `BAND_PAYS`（方向），没写「已证」。"
    "**S7 实况**：`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/24 01:10 未动）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；"
    "`pre-commit` / `pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 --no-verify。"
    "**未验证（承上条）**：全量 smoke 与 S6 链未跑（竞争窗，`smoke_test.py` / `logs/smoke_legs.json` / "
    "`Tools/s6_chain_bmc.py` 为对端写的共享面）；本面尚未接 smoke 两腿与 S6 腿。|\n"
)

p = "fleet/round_reports-bm-c.md"
with io.open(p, "r", encoding="utf-8", newline="") as fh:
    d = fh.read()
if not d.endswith("\n"):
    d += "\n"
with io.open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(d + ROW)
print("appended addendum", len(ROW))
