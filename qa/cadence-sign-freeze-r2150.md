# QA · 节奏符号冻结面 r2150

实物：`scripts/etf_book_cadence_sign_freeze.py` / `results/etf_book_cadence_sign_freeze.json` /
`research/ETF_BOOK_CADENCE_SIGN_FREEZE.md`

## 验收

| 项 | 判据 | 实测 |
|---|---|---|
| selftest | 全绿 | **19/19 PASS** |
| run | 落盘 + 桌面句可读 | rc0，`WROTE results/etf_book_cadence_sign_freeze.json` |
| check（幂等） | 同输入重算逐字相等 | **CHECK OK frozen_rho=-0.107 tracked=11** |
| 冻结不可被 2024+ 影响 | 训练窗只取 hi ≤ 2023-12-31 的季度 | `frozen_rule.train_quarters` = 2022Q2..2023Q4（7 个），无 2024 行 |
| 数据泄漏自查 | 预测读数取自季度 lo 之前的 bar | 每行 `asof` 严格早于 `bounds[0]`（2026Q4 asof=2026-09-30 < 2026-10-01） |
| 薄片不冒充 0 | 开季片 <40 根 → 记 holes 并标「开季中」 | 2026Q4 `n_starts=None`、holes 记 `slice too thin (36/36 bars < 40)` |
| 单起跑不当季度 | <2 个同网格起跑 → 记 hole | 2022Q1 只 1 起跑 → hole；自检 `one_start_is_not_the_quarter` |
| 选慢亏钱必须如实 | 选慢遇上正差 → 负贡献 | 2025Q3 选慢 +0.15 → 记 -0.15 |

## 自检腿（19）

- 季度标签算术：2026Q1→[2026-01-01,2026-04-01)、2026Q4→[2026-10-01,2027-01-01)（2 腿）
- 符号从训练窗学出：负方向 / 深→慢 / 浅→快 / 正方向反转（4 腿）
- 冻结拒绝噪声：薄窗拒绝 / 常数列拒绝（2 腿）
- 钱的算术：选快 +Δ / 选慢 -Δ / 缺差记 None（3 腿）
- 账本：改善 = 规则 − 基线 / 命中按钱算 / 亏钱说 DOUBTFUL / 空账说 THIN（4 腿）
- 配对：中位=中位数 / 无对=hole / 单起跑=hole / 双起跑=地板且取中点（4 腿）

## 本轮未做（如实）

- 未接入 `Tools/s6_chain_bmc.py`（同树 S6 链在飞，改链文件=改共享面）；
- 全量冒烟本窗发起后仍在跑（pid 107028），其 summary 未在本轮收口；
- 未改 `etf_book_cadence_regime_split.py` 的季度表（2026 季度由本面自建，避免动共享面）。
