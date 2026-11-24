# 一条读不出的轨，凭什么让整本书闭嘴

一张面，回答每轮都要问的那句话：权限面把整本书按成 UNREADABLE 的时候，
到底是「算不出来」还是「算得出来却不肯印」？
由 `scripts/etf_book_unreadable_rail_floor.py` 渲染；只描述不修面、不放宽规则。

<!-- BEGIN unreadable_rail_floor -->
generated 2026-11-25T04:42:07 | verdict **FLOOR_IS_COMPUTABLE** | machine bm-c | inputs bce7c9b555f4

| 项 | 读数 |
|---|---|
| 在册尺寸 k_now | 43.500300% |
| 地板线 k_now-size_tol | 43.000300% |
| 可读路径轨 | universe 43.500300%, window 74.708600%, window_x_universe 66.766500% |
| 读不出的轨 | baseline_published 46.025300% |
| 会压低地板的那条 | 无（都在地板线上或之上） |
| 权限（按规则） | 43.500300% |
| 绑定轨 | universe |
| 可保留 | 可保留 |
| 应变现（pp） | 0.00 |
| 已发布面判词 | UNREADABLE |
| 已发布 permitted_k | — |
| 按规则可持（毛额） | 435,003.00 元 |
| 票面在册市值 | 434,723.80 元 |
| 距权限余量 | 279.20 元 |
| 对下面摊 gap 面 | **没有 gap_k（存根）**（generated 2026-11-24T18:59:00+0800） |
| 冒烟红腿读数 | 765 条腿 / 34 红 @ 2026-11-24T20:12:28；其中 3 条死在这张存根上 |

**判词**：FLOOR_IS_COMPUTABLE

> every unreadable rail sits at or above the floor line 0.430003, so the minimum over the 3 readable path(s) is already the permission

**本轮可做什么**：权限可以印；未分类轨必须作为声明并列，禁默默丢掉。
<!-- END unreadable_rail_floor -->

## 它不声称什么

- 不改 `scripts/etf_book_rebalance_permission.py` 的判据（共享面，竞争窗内禁改）
- 不替代 producer 的 `UNREADABLE`：它只说「这条轨无法分类」，本面说的是「无法分类能不能证明印不出来」——两句话不是一句
- 未分类轨永远要作为声明并列：本面给的是下限，不是把那条轨当成「没问题」
