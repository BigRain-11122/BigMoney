# 把「日历拒绝」的署名从被取消资格的尺子换到当选的尺子（r1431 bm-c）

## 为什么这一轮存在

r1426 证明 `net_top2_share`（闸的 Y4）在它自己 4 条臂里有 3 条**判不了自己**，所以"被日历拒"
这句话从来没被一把可信的仪器核实过。r1429 在夹具上选出 `years_for_half`（8/8 夹具、零误放行），
并观察到当选尺子在 5/5 相位同样拒绝手上的书。**两件事都只是记录，一件也没被执行**——因为
换掉闸的拒因是一次准入规则变更，需要它自己的轮次：预注册 + 保守性测试 + 自判测试。

本件就是那一轮。只读已发布回执（`results/etf_book_year_caliber.json` 的 cells、
`results/admission/CANDIDATES.json` 的年度表），两把尺子全部 import（不做第二份实现），回答一个问题：

> 如果拒因由 `years_for_half` 打印而不是 `net_top2_share`，会不会有今天被拒的东西被放进来？

## 预注册（读之前写死，随回执逐字重印）

| 条件 | 内容 |
|---|---|
| A1 ELECTED | r1429 选举（imported，重跑）仍选 `years_for_half` |
| A2 NO_NEW_ADMISSIONS | 22 格里「新 ADMIT 且旧非 ADMIT」计数必须为 0 |
| A3 SELF_ADJUDICABLE | 有相位集的书，新尺子必须判得了自己（r1426 的 S 测试） |
| A4 LENGTH_FLOOR | 每本被判的书 n_years ≥ 5（r1429 记录的尺子隐含地板） |
| A5 NOT_DEGENERATE | `|net|/gross ≤ 0.5` 的格子只能印 indeterminate，永远不许印拒绝 |

A1..A4 全过 = **ADOPT**；任一不过 = HOLD 并点名失败条件。A5 是打印规则，不是否决票。

## 实读

| 书 | 单元格 | 旧尺子 | 新尺子 | 方向 |
|---|---|---|---|---|
| 手上的书 plain（5 相位） | 0.711 / 0.795 / 0.796 / 0.798 / 0.796 | 全 REFUSE | 1 / 2 / 2 / 2 / 1 年，全 REFUSE | same |
| cap_comm_1（5 相位） | 0.736 ~ 0.887 | 全 REFUSE | 1-2 年，全 REFUSE | same |
| cap_comm_2（5 相位） | 0.734 ~ 0.818 | 全 REFUSE | 1-2 年，全 REFUSE | same |
| cap_comm_1_conv_1（5 相位） | 0.778 ~ 0.923 | 全 REFUSE | 1-2 年，全 REFUSE | same |
| **smallcap_book:n20** | 0.695 | **ADMIT**（离 0.70 线只差 0.005） | **2 年 < 3 → REFUSE** | **tightened** |
| breadth_book:ALL | 0.793 | REFUSE | 2 年 → REFUSE | same |

- **判决 = ADOPT**（5 条件全过，`failing_conditions=[]`），拒因改为 `years_for_half`。
- 22 格里 **0 格放松、1 格收紧、21 格同向**。收紧的那格是本轮最有信息的一句：
  `smallcap_book:n20` 今天唯一的日历及格项，是靠一条**离被取消资格线只差 0.005** 的读数拿到的；
  换到当选尺子后它掉出头（2 年 < 3）。
- **A3 的口径变了**：同一批书在 r1426 的旧尺子下有 2 条臂 UNADJUDICABLE，在新尺子下 4 条臂全部
  自判通过（state=FAIL，5 相位同侧，spread 1.0 落在到线距离 1.0-2.0 内）。也就是说
  「拒」这个结论第一次站在一把自己能判自己的尺子上。（plain 臂 spread 1.0 恰好等于 margin 1.0，
  贴在边界上，照印不修。）
- **A5**：22 格 0 格退化（没有净额接近零的书），所以没有任何一格被迫印 indeterminate。
- **身份腿**：用 r1426/r1429 的单一实现重算 20 个单元的 `years_for_half`，与已发布 calibers
  最大偏差 **0.0**；对不上即 rc3 不出文件。

## 两枚自踩（都是「拿我猜的去当断言」）

1. **`read_ruler()` 吃的是序列，不是字典**。`scripts/etf_book_admission_ruler_election.py::read_ruler`
   内部 `_rows(years)` 对参数做 `enumerate` 并**自己重建年份标签（2000+i）**——传 `{year: net}` 进去，
   它把**年份标签当成收益率**算，不报错、不告警，读出一个看起来正常的数。本轮首跑就是这样：
   字典键 2020..2026 被当成 [2020.0, 2021.0, …] 在算。修法=`series()` 按年份排序取**数值**，
   并在 selftest 里加「非 mapping 直接抛错」+「按年份而非插入顺序」两条腿。
   （本条与 r1429 的 L8 同族：夹具期望值必须实读一次尺子再写死。）
2. **A2 的「放松」在代数上不可能发生，所以我造不出那个夹具**。首版想造一张「旧拒新过」的表，
   连造两次失败，原因是：`years_for_half ≥ 3` 意味着最好的两年**不足**净额的一半 ⇒
   `net_top2_share < 0.5 < 0.70` ⇒ 旧尺子必然也过。于是 A2 不是一个经验发现，而是一条**代数保证**；
   本轮把它改成两腿：一条用手工伪造的格子证明**探测器本身还能响**（否则这条子是摆设），
   一条在 600 张随机年度表上做性质检验，实读 **0 次放松**。
   这条的重要性在于：换尺子**只可能更严，不可能更松**——这是采纳它的理由，不是它的副产品。

## 生产面现状（诚实）

本件是**采纳证据**，不改闸的行为：`candidate_year_gate` 仍按 Y4 打印旧拒因。真正接线（把供给日历面
的拒因换成新尺子并重发那 4 条候选的拒因行）是下一步的接线动作，需在自己的轮次里落，且必须先有
本回执的 ADOPT。**不改任何生产判据**是本轮的有意选择：换判据不能在同一轮里既决定又执行。

## 交付

- `scripts/etf_book_admission_refusal_caliber_adoption.py`（selftest 12/12 + check 复 derive）
- `results/etf_book_admission_refusal_caliber_adoption.json`
- S6 链腿 `refusal_caliber_adoption`（check 形态，0.9s，rc0）+ smoke 双腿
- 方法论卡 E437