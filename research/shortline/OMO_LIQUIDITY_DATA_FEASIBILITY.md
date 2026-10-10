# OMO 流动性指标面数据可行性调研（P3 explore E4·调研先行·判读件）

> Ticket：state/queue/explore.md E4（央行公开市场操作流动性指标面：OMO 净投放→REPO 利率联动·REPO_PANEL 消费）
> 执行：bm-b r825（2026-10-10）·探针 `scripts/omo_liquidity_probe.py`（45s 超时夹克+2.5s 限速+getattr 守卫+签名感知调用+selftest 16/16）·证据 `results/omo_liquidity_probe.json`
> 纪律：**纯调研零 prereg 零面板写零回测零引擎零判据**（E1/E3 家族范式）；一切读数为描述面。生产车道落地=GM 署名票 + T-67 §2 前向 ≥12 个月冻结律。

## 一、E4 问句

央行公开市场操作（OMO）净投放流量 → 交易所逆回购利率（REPO_PANEL）联动，可否立数据面？

## 二、测量结论（akshare 1.18.96·本机 bm-b 实弹·13 端点 8 可达）

### F1 · OMO 操作流量面：akshare 内**不存在**（E4 核心面判负-数据源层）

- 全库清点：1141 个公开函数名 × 17 关键词（omo/reverse_repo/pboc/mlf/slp/liquidity/money_supply/shibor/interbank/swap_rate/repo_rate/lpr/base_rate/open_market/central/bank_financing/bank_china_interest）→ 命中 10 名，**无一为 OMO 日频操作流量端点**。
- 显式名探针三连 MISSING：`macro_china_reverse_repo` / `macro_china_omo` / `macro_china_base_rate` 在本 build 不存在（诚实 MISSING 记录）。
- 全部 8 个 OK 面无一携带可解析「净投放/操作量」列（linkage_status=unavailable）。
- **判读：日频净投放生产车道 via akshare 不可立**——与 E3 北向（披露断崖）、E2 期权（CEO 收死）同族=数据源层判负收口。

### F2 · 月度存量面可达（政策工具资产负债表族）

| 面 | 行数 | 窗口 | 性质 |
|---|---|---|---|
| `macro_china_central_bank_balance` | 356 | 1993.3→2026.8 | 央行资产负债表（**对其他存款性公司债权=OMO+MLF+SLF+PSL 工具存量**·月频·发布滞后 ~6 周） |
| `macro_china_bank_financing` | 273 | 2000-03→2026-09 | 银行融资月度序列（单一值+涨跌幅族） |
| `macro_china_money_supply` | 224 | →2026-08 | M2/M1/M0 月度宏观流动性 |

判读：月度工具存量 Δ = 净投放的**月频近似**（滞后 ~6 周），可作慢速流动性状态分类面候选；不可作日频择时面。

### F3 · 日频价格面可达且新鲜（OMO 操作目标利率的市场读数）

| 面 | 行数 | 窗口 | 新鲜度 |
|---|---|---|---|
| `repo_rate_query`（FR001/FR007/FR014 定盘） | 747 | 2023-10-09→2026-10-09 | 1 日（最新交易日） |
| `macro_china_shibor_all`（O/N..1Y 定盘+涨跌） | 2380 | 2015-05-08→2026-10-09 | 1 日 |
| `macro_china_lpr`（LPR1Y/5Y+旧基准） | 1576 | 1991-04-21→2026-09-20 | 月度步进（20 日发布） |

死面如实：`repo_rate_hist`（17 行死窗 2020-09→2020-10）；`macro_bank_china_interest_rate`（218 行但止 2019-11-20=决议事件表陈旧）；`macro_china_swap_rate` FAIL（形状故障）；`rate_interbank` FAIL（CJK 参数值不匹配——有效参数发现=5 分钟级小活候选）。

### F4 · 价格联动实证（描述面·E4 可测半面的直接回答）

**FR007（银行间 7 天定盘）× GC007（交易所 7 天·REPO_PANEL 本地面板）同日联动**：

- 重叠窗 2023-10-09→2026-10-09（728 重叠日）
- 同日 Pearson **r=0.869**
- 基差（交易所−银行间）均值 **+0.0305pp**、std 0.2229pp

判读：银行间→交易所回购利率传导**紧密**（OMO 操作所锚定的 FR 利率与 REPO_PANEL 强共动）——「REPO_PANEL 消费」面在价格维度得到正向描述性证据；但这是价格共动非流量→利率因果面，**不构成任何判据/ prereg 主张**。

## 三、与在飞件对账（不冲突声明）

- **E12（逆回购月末脉冲策略化）**：本调研的 FR007 联动证据（r=0.869）可供其后续消费，机制正交（月末日历 vs 流量/价格指标），无重复立项。
- **集团 M1 资金面季节效应（D-20260930-29/30 在册派工）**：OMO 面=流量/存量机制，与日历季节机制正交；司内未见 M1 开跑记录，零冲突。
- **CEO 令面**：O-20261009-1105「不做期权」不涉本域；当日无新令（D-19 水位双 MATCH）。

## 四、落地门槛清单（E1 范式·未满足项如实）

1. GM 署名 P1 任务单（新指标面产线落地）——**未满足**。
2. T-67 §2 前向 ≥12 个月窗——FR 价格面已有 ~2 年史+前向积累可行；若走净投放新渠道=FIRST_DATE 前向积累制起算——**面依赖**。
3. 净投放若立产线：**须非 akshare 渠道探针**（直连 HTTP 家族先例=cb_data_probe/northbound）——PBOC 公开市场业务交易公告（官方日频 ~16:00 发布：期限/量/中标利率/净投放）与 EM datacenter 公开市场操作表为候选渠道，**均未验证**（借力律：外源宣称=未验证假设）——**未满足**。
4. 披露口径冻结：公告时点 ~16:00 晚于 GC001 收盘 15:30 → T+0 盘中消费不可得，T+1 起可用——产线设计须冻结披露口径——**未满足**。
5. 消费面 prereg 判据冻结——未启动（本件纯调研）。

## 五、结论与后续

- **E4 核心判负（数据源层）**：OMO 净投放日频面 via akshare 不可立；akshare 生态内无可替代流量源。
- **正向副产出**：① FR007/GC007 同日 r=0.869 描述性联动证据（REPO_PANEL 消费面）② 月度工具存量面可达（慢速状态分类候选）③ `repo_rate_query`/`shibor_all` 日频价格面新鲜可达（未来现金腿择时研究的供给面候选）。
- **后续候选**（均须 GM 署名/新探针轮）：① PBOC 公告页/EM datacenter 净投放渠道探测（可入 P3 队列新项）② `rate_interbank` 有效参数发现小活 ③ 一切 prereg 门=T-67 §2+GM 署名。
- 本件零 prereg 零面板写零回测零引擎零判据；复活通道=新渠道实证 + GM 署名票，禁换皮重跑（描述面重复测量不构成新证据）。
