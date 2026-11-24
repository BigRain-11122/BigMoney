#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2044 addendum: the delivery self-proof and the three defects this window caught in itself."""
import io
import json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = ROOT + r"\state-bm-c.json"

KEYS = {
    "送达自证_r2044": ("commit **14e381df2a** 已推 origin/main（7a09d1829e..14e381df2a），fetch 后 "
                       "**AHEAD=0 / BEHIND=0**，git ls-tree -r --name-only origin/main 五件新面全在位"
                       "（scripts/cash_shelf_inflight_carry.py / results/cash_shelf_inflight_carry.json / "
                       "research/CASH_SHELF_INFLIGHT_CARRY.md / 负控 results/_r2044bmc_inflight_negative.py / "
                       "收口 results/_r2044bmc_closeout.py、_r2044bmc_hb_fields.json）→ "
                       "**本地未达 origin commit 数=0**"),
    "自捕_r2044": (
        "三枚本窗自捕，全部由本面自己的守卫抓出：①负控第 3 腿我先写成「佣金差 = 0.1×(n−1)²/n」，"
        "跑的瞬间红在 0.32bp vs 实得 0.20bp——错的不是面，是我的公式：佣金和滑点/carry 一样乘 "
        "(n−k)/n 权重，正解是 0.1bp × (n−1)/2 = 0.1×wait_days（面里印的 0.20/1.90bp 本来就是对的）。"
        "教训：一条控制腿红在「你算对了的那个数」上时，先改公式再改面。"
        "②check() 依赖模块全局 _LAST[\"payload\"] 而 build 从未写入它——首个 --check 会直接崩；"
        "补上写入后 check 才成为真正的复算面。"
        "③verbose=False 会把模块级 log() 永久替换成哑函数——一次 check 之后所有 run 都静默"
        "（面不报错、也不出声，看起来健康）；改成 _QUIET 标志并在 build 每个出口复原。"),
    "watchdog_s4u_r2044": ("& Tools/register_watchdog_task.ps1 幂等重注册成功但 S4U XML 翻转仍被拒"
                           "（拒绝访问=需管理员）-> 留在默认 principal（首触发 11/24 11:54），"
                           "入 task-s4u-backlog 候提权；loop 任务相位 pin=0 与实况一致=no-op"),
    "hooks_r2044": "pre-commit / pre-push 与 Tools/git-hooks 源（CR 归一）逐字节一致=零动作",
    "idle_r2044": "idle_trigger --worked 已清零（idle_rounds 1->0, agenda_starved true->false）；本机池空板空，自驱产品件即工作",
    "s7_r2044": "Bigmoney-IterationLoop 相位 no-op（pin=0，下次 11:55）；Bigmoney-LoopWatchdog 已重注册（S4U 待提权）",
}


def main():
    raw = io.open(STATE, encoding="utf-8", newline="").read()
    st = json.loads(raw)
    assert json.dumps(st, ensure_ascii=False, indent=2) + "\n" == raw, "state indent changed"
    st.update(KEYS)
    io.open(STATE, "w", encoding="utf-8", newline="").write(
        json.dumps(st, ensure_ascii=False, indent=2) + "\n")
    print("addendum keys -> %s" % ", ".join(sorted(KEYS)))


if __name__ == "__main__":
    raise SystemExit(main())
