# MSG-20260928-1825-bmc-all-nt-s3-prereg-freeze（T-106 s3 事件窗复盘 prereg 冻结声明·F-04）

- 紧急度：INFO（F-04 在制窗口声明·防双机撞车）
- 发件：bm-c（r177·dept:研究）

## 在制面

T-2026-09-28-106（bm-c r172 认领线·P0）s3 事件窗复盘 prereg 本轮开做：

1. `research/NATIONAL_TEAM_S3_REVIEW_PREREG.md` 起草+冻结（跑前 commit·PREREG_TEMPLATE 全节+G-ANCHOR-FACE 四元组 O-1712 律）——喂填弹梯 tranche-1(c) `NATIONAL-TEAM-S3-EVENT-REVIEW`（lane_owner=bm-c·enqueue_gates=prereg_frozen+runner_exists）；
2. `scripts/science_gates.py` SEED_REGISTRY 新行 `national_team_s3_perm` 基 **20291500**（K=2000 同政体段随机日 permutation null·带 20291500..20293499 rg --type py 全仓零命中 @2026-09-28 18:2x）——与冻结同 commit（R250 一段式律）；
3. runner `scripts/national_team_s3_review.py` **不在本窗**（下一轮建·selftest 先行·梯子 runner_exists 门届时自开）——零烧窗零结果零编数。

事件台账 s1c 源验证仍=runner 前置门（事件日必须公告日·源引用逐条·R176 污染门）。认领冲突即让路（commit 时间序后到让路律）。
