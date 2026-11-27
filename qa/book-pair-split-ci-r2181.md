# QA · book_pair_split_ci（r2181）

- 面：`scripts/book_pair_split_ci.py` → `results/book_pair_split_ci.json` / `results/book_pair_split_ci.md`
- 叙事：`research/BOOK_PAIR_SPLIT_CI.md`
- 轮：bm-c r2181 · 2026-11-27 · bar 2026-11-26

## 1. 本司 QA 清单

| 项 | 判据 | 实况 |
|---|---|---|
| 能跑 | `python scripts/book_pair_split_ci.py build` rc0 | ✅ rc0，面重生 |
| 自检 | `selftest` 全绿 | ✅ **22/22 PASS** |
| 契约 | `check` rc0 且非无条件重建 | ✅ rc0 `{"ok": true, "verdict": "CUSHION_SEPARABLE_POSITIVE"}`；STALE/CHECK FAILED 两态由 L22 行为腿钉死 |
| 对账（父面） | 四个数（n / mean_etf / mean_blend / cushioned）与父面 1e-9 内一致 | ✅ `parent_reconciliation.matched=true` |
| 对账（组合月度序列） | 组合月收益取自组合价格序列，而非线性近似 | ✅ 差异量被印出来：均值 0.2bp / 单月最大 17.5bp |
| 预注册 | 判词规则、块长、抽样次数、种子写进脚本头注，先定后跑 | ✅ 头注 + 常量 `PRIMARY_BLOCK/DRAWS/SEED/EPS_ZERO` |
| 三铁律 | 无未来数据 | ✅ 月度读数只用截至 bar 2026-11-26 的已实现收益；窗口末 = 最新 bar |
| | 无「跑到达标为止」 | ✅ 单次 4,000 抽样固定种子；其它臂是稳健性读数，不改主判词 |
| | 试验数 N 披露 | ✅ `trial_count_note`：本面无参数搜索（一个公布权重 + 一个预注册块长） |
| 数字可读 | 页面含均值 / 区间 / 赢率 / 分年 / 留一 / 50/50 稳健臂 | ✅ `results/book_pair_split_ci.md` |
| 不断言过头 | 不称「组合能预判坏月」；明确「算术不是技能」 | ✅ 三处（句 3、What this face does not say、research §5） |

## 2. 本窗自捕（两个真缺陷，都是自己的 check 先抓出来的）

1. **首版用线性近似拼组合月收益**：`w·cb + (1-w)·etf` 与父面 `mean_blend` 差 1.9e-5、
   逐月最大 17.5bp。`check` 报 `CHECK FAILED derived blend month does not reproduce the level`，
   逼出正解：三条序列各自取月收益。修后父面四个数 1e-9 内全对。
2. **`cushioned` 键名错位**：本面写 `improved`、父面写 `cushioned`，对账因此永久假红。
   改为显式键映射（`improved ↔ cushioned`）+ 行为腿 L20/L21 钉死「一个数动了必须点名」。

另有两处自检腿本身写错（L15 留一期望值、L18 链式期望漏了首月），当场修正——
腿红了先怀疑腿，再怀疑面。

## 3. 未做（如实）

- **链腿未接**：`Tools/s6_chain_bmc.py` 未新增本面腿。
- **冒烟腿未加**：`smoke_test.py` 无本面腿，即本面坏了没有套件级告警。
  两者同因：本轮 `repo_write_contention --lookback-min 45` 判 **rc=3 CONTENTION**
  （另一交互宿主 pid=129772 在动共享面），按 r1927/r1907 只落新增文件面。
- **全量冒烟未跑**：约 1,142s，10 分钟轮窗装不下；本轮不宣称套件全绿。

## 4. 下轮续作点（精确）

1. 共享面空出（`repo_write_contention` rc0）后：
   - `Tools/s6_chain_bmc.py` 加腿 `book_pair_split_ci`，写法 `(check, run)` 对：
     结算态 `check` 应 <2s，漂移态付一次 build（父面两份均需重 derive，约 60-90s）。
   - `smoke_test.py` 加 product 腿：从 `results/book_pair_split_ci.json` 重推五件事——
     区间下界 > 0 与 verdict 一致 / 点估计落在区间内 / `improved <= n` /
     `parent_reconciliation.matched` 为真 / 页面同时出现「+0.43pp」与区间两端；
     并把 `verdict` 与 `primary_ci90` 反向改一个数，断言腿会红。
2. 若要把本面接进 CEO 一页纸：先等共享面空出，且 `ceo_live_usage.py` 的 ⑨ 节已在印
   `REBALANCE_PAYS`；新增句应只补「0.43pp 的区间跨 0 吗」一句话，不重印父面数字。
