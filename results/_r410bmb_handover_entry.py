# -*- coding: utf-8 -*-
"""r410 bm-b 5x HANDOVER reconciliation entry (covers missed 375-405 window)."""
import io

entry = (
    "- 【第五节·产物清单核对（新增与删改）】**round 410 bm-b（5x 产物核对·375-405 窗断档补账·"
    "r409 next-pointer (e) 兑付）**：2026-09-29 05:4x 核对；本窗起点=round 370 bm-b（2026-09-28 09:2x，"
    "账本头 301,180）；本窗增量（三机全谱 2026-09-28 09:00→09-29 05:4x）＝试用劳动力常设线五连波全链"
    "（W2-JUDGE/W3-SCREEN+JUDGE/W4-SCREEN+JUDGE/MASS-W1-JUDGE 判负收口/W5 全链 generate→screen→judge "
    "3926/372 存活/judged finalize 03:48:39）+T-104 GRID-S3-DUALFACE judged-negative 0/30（r401 bm-b）"
    "+DECISION-CHAIN-V2-P1 done（G-REPRO-v1 假红根因修复）+SENTIMENT-AXES-FULLHIST-P1 done+"
    "NT-CHAIN-P1 prereg 冻结+MINUTE_FEED v1.2/v1.3 五符号 1970bar 落地+ETF_DAILY 五员面板 r398 定谳"
    "+池 runnable_pool 全量到 60+ 条目（W6-GENERATE 本轮入池）+T-105 CEO live usage v1（r390 bm-b）"
    "+T-116 pool_dualrun 三机证据链（本机 streak 2/3）+V3-TOURNAMENT waiting（bm-c runner 未建）"
    "+W6 prereg FROZEN（bm-c r198 接管）+**本轮 r410 bm-b：TRIAL_LABOR_W6 runner 构建切片全落地"
    "（scripts/trial_labor_w6.py selftest 80/80+w6_grammar.json sha16=2d395f5f8e7d16cb 193,536 轴组合"
    "+池条目 TRIAL-LABOR-W6-GENERATE ready）**；统一账 ledger head 实读=**328,987**（301,180→328,987 "
    "实增 27,807，跨 W2/W3/W4/MASS/W5/TRIAL_LAB 判决面批件，live ledger_head() 原读非手抄）；"
    "冲突窗=round 405-409 三机同窗 UU 已按 §4 commit 时间序正典解（r405/r406 bm-b+r412/r413 bm-a "
    "rebase 解面在册）；下一 5x=round 415 bm-b。\n"
)

p = "research/HANDOVER.md"
src = io.open(p, encoding="utf-8").read()
if not src.endswith("\n"):
    src += "\n"
io.open(p, "w", encoding="utf-8", newline="").write(src + entry)
chk = io.open(p, encoding="utf-8").read()
assert entry.rstrip("\n") in chk
print("HANDOVER entry appended; total lines:", chk.count("\n"))
