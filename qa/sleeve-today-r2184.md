# r2184 · 这一轮的产品：把「今天转债那半边该不该在仓里」送到读者那一页

## 起点（为什么这不是记账）

r2183 交付了 `results/book_pair_cushion_regime.json`：一条规则（转债市场溢价率处于自己历史
顶三分位时，转债袖持现金）和它的价钱（规则 9.97%/夏普 1.383/回撤 -4.37% vs 一直满仓
9.29%/1.215/-8.96% vs 同样暴露但不择时 8.15%/1.266/-5.16%，全窗多赚 11.64pp，其中最好 5 个月
占 64.7%）。但那张面里**没有一个字告诉读者今天该怎么做**，而且它当时是 r1282 孤儿类：
发布、`check` 能说 STALE、但链里没有驱动者，所以 `today` 这个读数只会一天天变旧而没人重算。
r2182 的 `current.today` 之前也不存在——面只印「最后标签 rich」，读者要自己推出「所以袖子在
现金」。

## 做了什么（三件，都可跑、可查）

1. **生产者发布决定本身**（`scripts/book_pair_cushion_regime.py`）
   `current.today` 新增六个字段：`label_in_force` / `decided_at_month_end` /
   `month_the_label_applies_to` / `sleeve_state`（cash 或 in_book）/
   `sleeve_share_of_wallet` / `next_decision_day`。语义钉死：`labels[k]` 由上一个月底决定，
   所以最后一个月是**现在生效**的那个。实锚：label=rich，2026-10-31 读的，管到 11-30，
   下一次拍板 2026-11-30 → 今天袖子持现金，钱包形态 = ETF 100% / 转债 0%。
   同时 `_verify` 新增两条：`today.sleeve_state` 必须由 label 决定（rich→cash、其余→in_book），
   `next_decision_day` 必须等于 `label_asof_month_end`。selftest 24/24（新增两腿：正例两面 +
   反例「label=mid 却写 cash」必须被判 CHECK FAILED）。

2. **读者那一页印这句话**（`scripts/ceo_live_usage.py` 新 ⑩ 节）
   页面只读生产的 `current.today`，不重算标签（两处实现必漂）。节内印：结论先行（今天待在
   现金/书里）、钱包此刻形态、溢价读数与百分位、规则一句话 + 换手 11 次/成本 0.33pp、三条腿
   并排、对照组骨架（同平均暴露 43%）、诚实的一半（64.7% 的边缘在 5 个月里）、按体制切开的
   缓冲表 + `CUSHION_DIFFERENCE_NOT_SEPARABLE`、生产者自己的 generated/cutoff、以及「本面截止
   X 落后本书 Y 就先别照它下单」的本地滞后守卫。缺面时印「未产出」，不印 30/70（r98）。
   selftest 新增三腿：侧面词与决策日必须来自面、出处戳必须在节内、缺面必须印理由且不出现
   「今天应该待在」。`selftest: ALL PASS`（212 行输出）；`page_repeat_guard scan` CEO 页
   248 句 **0 repeated**。

3. **两条孤儿面接上链**（`Tools/s6_chain_bmc.py`）
   `book_pair_split_ci`（r2180）与 `book_pair_cushion_regime`（r2183）此前都没有驱动者。
   两腿都用 check/run 对：check 各自锚外部输入（blend 面的权重与窗口、cb 面板戳），只有漂移
   才付 run。实测 `--only=book_pair_split_ci,book_pair_cushion_regime` **2/2 rc0 0.4s**；
   `chain_writer_audit` / `chain_writer_audit_check` / `chain_contract_word_audit`
   **3/3 rc0**（契约词审计 ok:true n_current 13）。

## 这一轮**没有**验证到的

- 全量冒烟本轮以 detached 方式起跑，结果未在本窗读完（如实留账，下一轮读 `logs/smoke_r2184.out`）。
- 规则的边缘仍然只有一个窗口（2020-02..2026-11），且 46/81 个月市场偏贵——一条周期的一次读数。
- 溢价是市场中位数，不是这只 20 只债券袖的读数；按月换手，日内不建模。
