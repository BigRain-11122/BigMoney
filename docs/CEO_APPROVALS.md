# CEO_APPROVALS · 实盘模拟盘准入认可台账（O-20260926-1326 立法·追加式）

- 准入法：年内回放纸盘结果 → **【CEO 认可】（唯一准入门·名单以 CEO 为准）** → 实盘模拟盘（QMT/Ptrade 模拟账户·PLAN P4 通道）→ 模拟观察 → 实盘真金=CEO 唯一门（既有阶梯不变）。
- 认可面=既有晋升阶梯之上的追加门；未认可者留在纸盘继续跑。
- 记录法：CEO 名单落地后逐行追加（日期｜账户｜CEO 原话/渠道｜生效动作）；禁删改历史行。

## 认可记录（空——候 CEO 名单）

| 日期 | 账户 | CEO 认可出处 | 生效动作（模拟盘网关接线） |
|---|---|---|---|

## 模拟盘网关接线队列（工程部 mandate·名单落地后开动）

- 通道：QMT/Ptrade 模拟账户网关（PLAN P4 机制，live/gateway.py 骨架在位）。
- 接线顺序=CEO 名单顺序；每账户接线后入模拟观察期，战绩入每日战报。

## 呈报指针

- 年内回放纸盘榜：results/retro_paper_2026/LEADERBOARD.md（RETRO-PAPER-2026 批）。
- 真前向纸盘（09-23 起双轨互证）：results/paper/、results/aggr_paper/、results/alloc_paper/、results/grid_paper/。
