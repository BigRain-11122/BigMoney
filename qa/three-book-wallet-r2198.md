# QA — three_book_wallet (r2198 bm-c)

**产品**：`scripts/three_book_wallet.py` → `results/three_book_wallet.json` + `results/three_book_wallet.md` + `research/THREE_BOOK_WALLET.md`

**判词** `THE_THIRD_BOOK_IS_BEHIND_A_GATE`

## 一句话
三本书（ETF 复合 0.958 / 转债 0.540 / 股指基差对冲 1.445）各缩放到同一 8% 波动预算后放进一个钱包：**Sharpe 最高的那本在 100 万钱包里权重是 0.00**，因为一手 IC 就吃掉 91,029 元的波动预算——它要等到钱包 5,689,312 元（w=0.20）才进得来。

## 读数（窗口 2020-01-06..2026-11-26，1670 bars，evidence_cutoff 2026-11-26）

| 面 | 值 |
|---|---|
| 门内最优（可行） | ETF 65% / 转债 35% / carry 0% → 6.51%/yr，SR 1.060，vol 6.12%，maxdd -6.72%，需 73,858 元 |
| 忽略门最优（不可行） | ETF 35% / 转债 15% / carry 50% → 9.40%/yr，SR 1.844，vol 4.94%，需 2,275,725 元 |
| 门槛的价格 | 0.784 Sharpe（**不是损失，是没人付过的价钱**） |
| 一手门槛 | IC 一手波动预算 91,029 元 ÷ 8% = 1,137,862.5 元整本资本 |
| 权重—门槛关系 | w 需要钱包 ≥ floor/w：10% → 11,378,625 / 20% → 5,689,312 / 1/3 → 3,413,588 |
| 相关性 | ETF×转债 日 0.090（月 0.145）· ETF×carry 日 **-0.046**（月 -0.123）· 转债×carry 日 **-0.049** |
| 同跌月 | ETF×carry 仅 13/83 · 转债×carry 22/83 |
| 门内组合再放大 | vol 6.12% → 要到 8% 需 1.31x 杠杆（SR 不变，回撤变大）→ 8.59%/yr |

## 证据链

1. `selftest` **12/12 legs pass**（含：vol 缩放命中 8% / 常数序列不除零 / 单调下跌 maxdd==total / 网格权重和为 1 / 门槛算术 / 相关 ±1 / 判词由门槛决定 / 漂移文案含 STALE）
2. `run` 一次通过，`check` rc0
3. **check 行为腿（真面毒化）**：把 `provenance.inputs.etf.mtime` 改成 2000-01-01 → `check` rc3 且 stdout 首词 `STALE`；按字节还原后 rc0
4. **对账**：etf/cb 与 `book_pair_blend.in_window` **逐位一致**（0.957817 vs 0.9578173792；0.540241 vs 0.5402413276）；carry 与族内 hedged 臂 1.4162 差 +0.0284（窗口差），**不与 basis-only 3.189 比**（那是名义额读数，任何钱包都持不住）
5. `check` 内建对账腿：若 `book_pair_blend` 换钟，本面自动转红（容差 1e-6）

## 本轮自捕（写盘前发现并修掉）

1. `feasible()` 把 dict 的字符串键当整数下标用 → KeyError
2. `feasible()` 对 w=0 的书仍要求覆盖 floor → 100 万钱包下所有组合都「不可行」→ best=None 崩溃。修：w≤0 = 不开这本书 = 无需资本
3. `load_books()` 把父面的 **NAV 水平**当日收益混合（etf max 2.03、cb max 5.11）→ 组合溢出 inf。修：`pct_change()`
4. carry 用「主力连续收盘价相对收益差」自拼序列，vol 4.77% 是族内正典的 2.6 倍（换月噪声）→ SR 只有 0.607，与已发布 1.4162 不符。修：改用族内正典 `idx_fut_carry_paper.per_lot_daily` 的 `excess_points`（点数序列，缩放后 SR=1.445，与已发布对齐）
5. `stats()` 在常数序列上 vol 被四舍五入成 0.0 却仍做除法 → Sharpe 1e17（会印出「奇迹」）。修：`VOL_FLOOR=1e-9`
6. `maxdd` 用 `eq.cummax()`，首个 bar 就亏的钱不算回撤 → 峰谷从自己第一个收盘起算。修：峰值序列前置 1.0
7. `gates.max_weight_now` 用 `min(1, W/floor)` → carry 在 100 万钱包印成 0.88（读者会读成「可以放 88%」）。修：0.00 + 另设 `budget_cover_now`
8. 渲染串 `%.4f` 撞上正文里的 `8%` / `10%` → ValueError。修：文案去 printf

## 未做（如实）

- 未接冒烟腿 / 链腿 / CEO 一页纸小节：`smoke_test.py`、`Tools/s6_chain_bmc.py`、`scripts/ceo_live_usage.py` 全是共享面，本轮 `repo_write_contention.py` rc=3（对端 interactive pid 30500 自 2026-11-27T21:54:41 存活，16 张共享面别宿主先写过）→ 按 r1907/r1927 只落新增文件面
- carry 的对冲腿资本与成本沿用父面 excess 口径，未重估（真对冲需要第二个账户）
- 三书只做了「固定权重」网格（step 0.05），未做时变权重 / 再平衡成本
- 8% 缩放是风险刻度，不是承诺：门内组合实际 vol 6.12%

## 已知局限（读者须知）

- carry 序列是**点数/手**，与另两本的小数收益率不同尺；面里先各自缩放到 8% 波动再混合，所以权重语义 = 风险预算份额，不是名义份额
- 窗口是三者交集（carry 起 2018-10-23、ETF 起 2020-01-03），任何一本的全史数字都不混进交集
- 转债书 8% 缩放后 maxdd -14.50%，其原始读数 -22.59% 在 JSON 的 `raw` 里
