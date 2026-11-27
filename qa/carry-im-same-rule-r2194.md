# QA · carry-im-same-rule · r2194 (bm-c)

日期：2026-11-28 00:3x +08:00 · 审判面：`results/carry_im_same_rule.json`
页面：`results/carry_im_same_rule.md` + `research/CARRY_IM_SAME_RULE.md`
脚本：`scripts/carry_im_same_rule.py`

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\carry_im_same_rule.py run` → `THE_SAME_RULE_READS_TWO_DIFFERENT_THINGS` / `THE_TWO_LEGS_ARE_ONE_BET_IN_TWO_TICKETS`，rc0 | PASS |
| 2 | 自检全绿 | `selftest` → **27/27 PASS** | PASS |
| 3 | 漂移守卫可用 | `check` → `{"ok": true, "notes": []}` rc0 | PASS |
| 4 | **复现腿 IC（波动）** | 最近 242 收益日重算 → **91,029.00**，逐位 = `open_capital.accounts.IC.per_lot_vol_cny_hedged` | MATCH |
| 5 | **复现腿 IC（门槛）** | 91,029.0 / 8% → **1,137,862.50** = `accounts.IC.funding.first_rung_cny` | MATCH |
| 6 | **复现腿 IM（波动）** | 最近 242 收益日重算 → **93,259.93** = `accounts.IM.per_lot_vol_cny_hedged` | MATCH |
| 7 | **复现腿 IM（门槛）** | 93,259.93 / 8% → **1,165,749.12** = `accounts.IM.funding.first_rung_cny` | MATCH |
| 8 | SIZING 面同源核对 | 两腿 `SIZING.accounts.<P>.hedged.ann_vol_per_lot_cny` 与重算值逐位一致（门槛不与 SIZING 的未舍入派生值比，见 #15） | PASS |
| 9 | 复现失败即不发布 | `reproduction.verdict != MATCH` → 判词 `UNREADABLE`、exit 2、不写面（本窗首跑即被此闸拦下一次，见页尾自捕） | PASS |
| 10 | 输入字节动 = STALE（行为腿） | selftest：把 `inputs_digest` 任一 sha 改 0 → rc3 且含 `STALE` | PASS |
| 11 | 改判词 = CHECK FAILED 且不带 STALE（行为腿） | selftest：改 `judgement.verdict` → rc1 含 `CHECK FAILED`、无 `STALE` | PASS |
| 12 | 改腿分位 = CHECK FAILED（行为腿） | selftest：改 `today_percentile` → rc1 含 `CHECK FAILED` | PASS |
| 13 | 改复现腿 = CHECK FAILED（行为腿） | selftest：改 `reproduction.IC.recomputed_vol_cny` → rc1 含 `CHECK FAILED` | PASS |
| 14 | 判词机逐字复用 r2193 | `judge()` / `pct_rank()` / `quantile()` / `lots_at()` / `first_rung()` 与 `carry_first_rung_vol_ruler` 同门槛（90/75/60/40），未按新样本调线 | PASS |
| 15 | 十进制一致 | 表内下游数一律从 2dp 波动派生；`SIZING.capital_for_one_lot_at_target`（未舍入派生，1,137,862.55）与已发布 2dp 门槛的 5 分钱差只披露不比较 | PASS |
| 16 | 共同日历对齐到日期 | IC 剪到 IM 首收益日（2022-07-25）之后切片；两腿滚动窗数同为 812、共同日 1053——对齐在日期键上，不在行号上 | PASS |
| 17 | 相关性只算共同日 | `_align()` 按日期键取交集；`_corr()` 逐位与手算一致（selftest 完美相关/完美反相关/退化三条腿） | PASS |
| 18 | 零网络零回测 | 仅本地面板重放（`CP.position_series` / `CP.per_lot_daily` / `BASE.load_index`）+ 四张已发布面读取 | PASS |
| 19 | 不改任何已发布面 | 只写 `results/carry_im_same_rule.{json,md}` 与 `research/CARRY_IM_SAME_RULE.md` | PASS |
| 20 | 相关性高也不宣称分散 | `bet_verdict` = ONE_BET_IN_TWO_TICKETS，页面明写「不能相加」；`ADOPTION.what_the_adoption_forbids` 第三条即禁此读法 | PASS |

## 本轮读数（cutoff 2026-11-26 · 两腿 · 100 万 · 8% 目标）

| 腿 | 样本 | 收益日 | 滚动一年窗 | 今日每手波动 | 分位 | 历史买得起率 | 今天第一手门槛 | 中位年份门槛 | 判词 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| IC | 自身全样本 | 1965 | 1724 | 91,029.00 | 93.79 | 78.13% | 1,137,862.50 | 837,496.51 | VOLATILITY_READ |
| IC | 同一本日历 | 1053 | 812 | 91,029.00 | 86.82 | 53.57% | 1,137,862.50 | 979,720.45 | PARTLY_VOLATILITY_READ |
| IM | 自身全样本 | 1053 | 812 | 93,259.93 | 84.61 | **30.05%** | 1,165,749.12 | 1,093,332.72 | **CAPITAL_THRESHOLD** |

- 两腿共同日 **1053**（2022-07-25 → 2026-11-26），日对冲残差相关 **0.816** → ONE_BET_IN_TWO_TICKETS
- 解禁线（100 万 × 8%）两腿同为 **80,000 元**；IC 中位年份门槛 979,720 在线上、IM 1,093,333 在线下

## 自捕（本窗实弹）

1. **首跑被自己的复现腿拦下**：`ok_sizing` 拿重算门槛去比 `SIZING.hedged.capital_for_one_lot_at_target`
   （1,137,862.55，按未舍入波动派生）→ 5 分钱假差异 → rc2 不发布。修法与 r2193 自捕②同源：门槛只与
   `open_capital` 的 2dp 发布值比，SIZING 只比波动。
2. **行为腿首版写反了漂移分类**：把「改判词」判成 STALE。按 r1934 漂移分类改成——先比输入字节（STALE），
   同输入下数字不符一律 `CHECK FAILED`；selftest 从 25/26 修到 27/27，并补了「输入 sha 改一位 → STALE」正交腿。

## 未做（如实）

- 链腿与冒烟腿：共享面（`Tools/s6_chain_bmc.py` / `smoke_test.py`），本轮 `repo_write_contention` rc=3
  CONTENTION，按 r1907/r1927 只落新增文件面 —— **连续第 11 轮留账**
- 全量冒烟本轮 detached 起跑（`results/_smoke_r2194.out`），收轮时 231 行 / 13 FAIL，读到的多为
  `etf_book_*` 面代差（STALE）与 `r1933 substitution rulers` 的 CEO 页缺块；未读完、不作全绿宣称
- S6 链、`attrition_ledger_guard`、`py_watermark`、`compute_audit` 未跑（同上：皆写共享面）
