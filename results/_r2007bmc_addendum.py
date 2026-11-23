# -*- coding: utf-8 -*-
import io, sys

P = "fleet/round_reports-bm-c.md"
MARK = "r2007 **addendum**"
ROW = (
"| 2026-11-23 20:0x | " + MARK + "（送达核验 + S7 实况 + 两条诚实声明） | "
"commit **ef2ac44abe** 已推 origin/main（d27d962ff0..ef2ac44abe），fetch 后 **AHEAD=0 / BEHIND=0**；"
"`git ls-tree -r origin/main` 五件 blob 在位（scripts/idx_fut_carry_hedge_beta_lots.py / "
"results/idx_fut_carry_hedge_beta_lots.json / research/IDX_FUT_CARRY_HEDGE_BETA_LOTS.md / "
"负控 results/_r2007bmc_beta_lots_negative.py 与收口脚本 results/_r2007bmc_closeout.py，"
"两者 `git add -f` 走既有 `_r[0-9]*` 惯例）→ **本地未达 origin commit 数=0**。"
"**S7 实况**：`register_loop_task.ps1` phase ok（machine=bm-c pin=0 current=0，首燃 11/23 20:05 未动）；"
"`attrition_ledger_guard scan` **CLEAN**（4 账本；bm-a 4 行、主账 1 行历史缩行 healed 注记照录）；"
"**pre-commit 与 pre-push 两枚爪本轮实测与 Tools/git-hooks/ 不一致，已按幂等配方重装**（两件 LF-normalized 落盘）"
"——这是一条真漂移不是 no-op，如实记。"
"**诚实声明一**：`fleet/machines/bm-c.json` 的 `current` 字段本轮被本面覆盖——覆盖前对端（pid 51252 interactive）"
"写的是「bench cell cmdty_xsec: 44-contract commodity cross-section momentum -> NO_EDGE」，即同一台机器上还有"
"一条线在跑 bench cell；心跳是单写者面、后写者胜，但读者不应把这行读成「bench 线停了」。"
"**诚实声明二**：本轮 `--selftest` 的第一版**跑出了自相矛盾的输出**（表格印 242 日窗整数手 {1,2}，判词却印 STABLE），"
"根因是 `rolling_row` 忘了写 `state` 键而使 `verdict_of` 把每一行当 NO_WINDOW 跳过；"
"是**数据自相矛盾**抓出来的、不是自检抓出来的。现已把行构造抽成 `rolling_row()` 并把这条事故做成 selftest 三腿"
"（行自带 state / 行点名手数跨度 / 由该行拼出的面不得判 STABLE）。"
"**未验证（承上）**：全量 smoke 与 S6 链未跑（竞争窗，smoke_test.py / logs/smoke_legs.json / "
"Tools/s6_chain_bmc.py 为对端写的共享面）；本面尚未接 smoke 两腿与 S6 腿。|\n"
)

def main():
    s = io.open(P, encoding="utf-8").read()
    if MARK in s:
        print("already appended")
        return 3
    if not s.endswith("\n"):
        s += "\n"
    io.open(P, "w", encoding="utf-8", newline="").write(s + ROW)
    print("addendum appended")
    return 0

if __name__ == "__main__":
    sys.exit(main())
