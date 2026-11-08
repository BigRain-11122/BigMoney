# DIGEST-20261108-r1431 — 换拒因的尺子：22 格 0 放松、1 收紧（bm-c）

**问题**：r1426 取消了 `net_top2_share` 的资格、r1429 选出了 `years_for_half`，但从没人把闸的拒因
真的换过去——因为那是准入规则变更，需要它自己的一轮。

**这一轮的答案**：可以换。5 条预注册条件全过（A1 选举仍选它 / A2 零放松 / A3 每本有相位集的书
都能自判 / A4 全部 n=7≥5），判决 ADOPT；A5（退化格只能印 indeterminate）22 格零命中。

**读数**（6 本书 22 格）：
- 手上的书 4 条臂 × 5 相位：旧尺子 0.711~0.923 全拒，新尺子 1-2 年全拒 → 同向。
- `smallcap_book:n20`：旧 0.695 **ADMIT**（离 0.70 只差 0.005），新 2 年 → **REFUSE**。换尺子
  收紧的唯一一格，也是最能说明问题的一格：那本书今天唯一的日历及格项站在线边上。
- `breadth_book:ALL`：0.793 拒 → 2 年拒，同向。
- A3 口径变了：旧尺子下 2/4 条臂判不了自己（UNADJUDICABLE），新尺子下 4/4 自判通过
  （plain 的 spread 1.0 恰好等于 margin 1.0，贴边照印）。

**两条判例**：
1. **`read_ruler()` 吃序列不吃字典**——它 `enumerate` 参数并自己重建年份标签，传 `{year: net}`
   会把年份当成收益率算，不报错。收敛=`series()` 按年份排序取数值 + selftest 两条腿。
2. **换尺子只可能更严，不可能更松（代数，不是经验）**：`years_for_half ≥ 3` ⇒ 最好两年不足净额一半
   ⇒ `net_top2_share < 0.5 < 0.70` ⇒ 旧尺子必过。所以 A2 是代数保证；本轮把它的检验改成
   「探测器还能响」（伪造格子）+「600 张随机表 0 次放松」（性质腿），而不是假装造出了一个反例。

正身 = `scripts/etf_book_admission_refusal_caliber_adoption.py`（selftest 12/12 / check rc0）
+ `results/etf_book_admission_refusal_caliber_adoption.json` + `research/ETF_BOOK_ADMISSION_REFUSAL_CALIBER.md`
+ S6 腿 `refusal_caliber_adoption` + smoke 双腿。生产判据未动：接线（供给日历面改印新拒因）走下一轮。