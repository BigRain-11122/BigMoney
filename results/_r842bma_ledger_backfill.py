# -*- coding: utf-8 -*-
"""r842 bm-a: backfill 7 missing round-ledger lines (r835-r841) to
round_reports-bm-a.md. Evidence = on-origin commits + state-bm-a.json notes.
Honest markers: each line labeled 补记 (backfill), watermark verdict line
omitted where not reconstructable (r835-r838 windows), commit shas cited.
Append-only, fresh single-file read-modify-write per multi-writer law."""
import io

P = r"round_reports-bm-a.md"
t = io.open(P, encoding="utf-8", newline="").read()
assert t.endswith("\r\n"), "file must end with CRLF line"
assert "round 835" not in t and "round 841 补记" not in t, "backfill already present or unexpected"

lines = [
    "2026-10-07T17:59:22+08:00 | round 835 补记（r842 回填·当时窗会话未落账本行） (bm-a, dept:工程/舰队) | S0 rebase 风暴 18UU 正典解 + r787 三态 commit/quit/branch-f 治愈（pit-git-resolver 直写）+ FUND-DIVLOWVOL-P1-NULLS 接管预备让路 bm-b 新鲜 claim 17:46:16（MSG-1752 让路裁决·fuse clear 留证）| 验证: commits 23ddfde82+5204ac4b9+c7ab2c5f8+churn 族 | 下轮指针: r836 W16-GENERATE 供给解锁",
    "2026-10-07T18:23:23+08:00 | round 836 补记（r842 回填） (bm-a, dept:工程/舰队) | W16-GENERATE 供给解锁（catalog runner SLOT-10 翻面 + fill_ladder 正典入册 404→405 ready·floor 1→2）+ W14 screen-finalize 指针 MSG 致 bm-c | 验证: commit 3141f67c4 | 下轮指针: r837 维护窗",
    "2026-10-07T18:54:12+08:00 | round 837 补记（r842 回填） (bm-a, dept:工程) | 旁路维护窗·仅 daemon churn absorb 证据（007f82c51+56cd6f93e·r620 律）·主体工作由他会话承载（state 注记 r836-r838 carried by prior sessions）| 验证: commit 时间戳族 | 下轮指针: r838",
    "2026-10-07T19:16:33+08:00 | round 838 补记（r842 回填） (bm-a, dept:工程) | 同 r837 维护窗·churn absorb pre-rebase+retry（0d59a2b41+3da8c0b09）·r838 temp blob 未跟踪遗留（state 注记如实）| 验证: commit 时间戳族 | 下轮指针: r839 W176 finalize",
    "2026-10-07T20:10:39+08:00 | round 839 补记（r842 回填） (bm-a, dept:研究+工程/舰队) | W176 finalize one-pass 落地（ledger 793,105=790,905+2,200 运行时 derive·merged K 385,120·skill_line 1.1845·SS5 4/4 PASS）+ r752 三闸回执 + SS7/SS8 回填 + S0 风暴正典解（6 lane UU R31 owner 侧+history union 149 零丢失·r835 三态治愈·merge-mode r708）+ S6 ~30 腿 rc0 + S7 quartet 绿 | 验证: commit f97372f1a + state r839 注记 | 下轮指针: r840",
    "2026-10-07T20:23:28+08:00 | round 840 补记（r842 回填·state r841 注记所引「r840 报告行」当时实未落盘·本行即补正） (bm-a, dept:工程/舰队) | O-20261008-1300 可见控制台封印同轮执行（orphan_face_probe v1.1: WATCH-only kill+stdio 豁免+持久门·selftest 4/4·扫描 orphan=0）+ postscript push-race wave-2 收口（probe v1.1.1 merge 溯源+stage-label 勘误+送达 behind-0）| 验证: commits a1f778640+33c7a7894+f999c3e0c | 下轮指针: r841",
    "2026-10-07T20:37:11+08:00 | round 841 补记（r842 回填） (bm-a, dept:研究+工程/舰队) | [watermark verdict: 绿 red=false·satengine alive rc0 queue0 idle] W177 席位链落地（pre-seat probe rc0 ADMIT post-W176 宇宙 re-derive 强制·seat MSG published=reserved 780a0cd30·A 404_204..406_203 阶梯 37th E36/B 406_204..406_403 own-A 保留·conflicts=0 origin 空位保持）+ S0 push-race 治愈（orphan ts-resolve+r835 三态）+ S6 37/37 rc0 + state 治愈 839→841（r840 state 写失于 20:24 postscript 手术·r624 branch-f 复原 r839 时点 blob·序列按账本诚实）| 验证: commits 780a0cd30+48810198a+45f946cb6·smoke 48/48·quartet 绿·孤儿面=0 | 下轮指针: r842 W177 prereg 构建窗（buildgen r833 血统）",
]
add = "\r\n".join(lines) + "\r\n"
t2 = t + add
io.open(P, "w", encoding="utf-8", newline="").write(t2)
chk = io.open(P, encoding="utf-8", newline="").read()
assert chk == t2, "roundtrip drift"
assert chk.count("补记（r842 回填") == 7, chk.count("补记（r842 回填")
print("backfill OK: +7 lines, file lines now", chk.count("\r\n"))
