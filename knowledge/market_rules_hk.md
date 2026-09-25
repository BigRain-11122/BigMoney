# market_rules_hk.md — 香港证券市场交易规则（官源核验件）

- 归属: T-2026-09-24-17 deliverable (5)（GM order O-20260924-1155 / CEO 方向: 基金/HK 套利研究线）
- 纪律: RULES-AUDIT —— 每条事实带官源 URL；**无源禁推测**；未核验面一律标 `PENDING-VERIFY`（诚实失败可见），下轮以站点 sitemap/稳定锚点发现 URL 后补验。
- 核验轮: bm-a R169 (2026-09-25 15:2x-15:4x)。首轮首落=部分核验版（两官源主面落地），非全闭。

## 一、已核验事实（官源在册）

### 1. 交易机制（无涨跌停停板 + 报价守卫 + VCM）

源: https://www.hkex.com.hk/Services/Trading/Securities?sc_lang=en （HKEX 官网 Trading Mechanism 页, 2026-09-25 实读）

- 港股**无单日涨跌停板**。约束为三层报价守卫+VCM:
  - 连续交易时段限价/增强限价/特别限价单，输入价偏离名义价 9 倍及以上即拒单（Rules of Exchange Rule 505A）。
  - 当日首笔报价: 买价不得低于 prev close 的 24 个价位或 5%（ETP 为 3.5%）以下（取更宽者），卖价对称; 且任何情况不得偏离 prev close 9 倍及以上。
  - VCM（市场波动调节机制）: 适用于恒生综合大型/中型/小型股指数成份股、SPAC 股/权证、合资格 ETF 与杠杆及反向产品; 触发阈值 ±5% 至 ±50%（按证券分级）; 价格偏离 5 分钟前最后成交价超阈值→5 分钟冷静期（限价带内交易）; 仅适用于连续交易时段特定窗口的整手买卖盘输入。
- 开市前时段（POS）与收市竞价时段（CAS）只接受竞价盘与竞价限价盘; POS 竞价限价盘偏离 prev close 9 倍及以上即拒。
- CAS（适用证券）: 参考价上下 **±5%** 为允许价格带（两阶段: 输入时段 ±5%，不可取消时段收紧至买低卖高带内）; 随机收市 2 分钟内; 最终 IEP 为收市价，IEP 无法确定时以参考价收市。
- 非收市竞价证券收市价=最后 1 分钟名义价 5 次快照（15:59:00 起每 15 秒一次）的中位数 → **下午收市时刻 16:00**（官源快照表实证）。
- 自动撮合股票每买卖盘上限 3,000 手（board lots）。

### 2. 碎股/整手（board lot 与 odd lot）

源: 同上 Trading Mechanism 页（公开交易类型表）

- OTP-C 支持公开交易类型含 **碎股买卖（Odd Lot Trade, 类型码 "D"）**: 少于一手之数量可经碎股交易操作于 OTP-C 撮合; 非经 OTP-C 成交时由卖方负责向交易所申报。
- **特别大手买卖（Special Lot Trade）**: 数量大于一手且可非整手倍数。
- 每只证券的手数（board lot size）由发行人定、逐只不同（逐手数表 `PENDING-VERIFY`——见 §三.4）。

### 3. 清算与交收（CCASS）

源: https://www.hkex.com.hk/Services/Clearing/Securities?sc_lang=en （HKEX CCASS Clearing – Securities Overview, 页脚标注 Updated 03 Oct 2017, 2026-09-25 实读）

- 交易所买卖以 **CNS（持续净额交收）** 制结算（除非被隔离为逐笔）; HKSCC 以 novation 成为双方交收对手方并提供交收保证; 同证券同日买卖轧抵为单一净额，未结算净额滚存至下一交收日继续对冲。
- 隔离买卖（Isolated Trades）逐笔交收，HKSCC 仅 facilitator 不作保证。
- T 日 18:00/20:00 后发临时清算结单，T+1 日 14:00 后发最终清算结单。
- 「交易所买卖的交收日=T+2」字面未在本页出现（页仅述 T/T+1 结单时点）→ 交收周期 T+2 本身 `PENDING-VERIFY`（见 §三.3）。

## 二、与 A 股面差异速查（本研究线消费面）

| 维度 | A 股（本仓 knowledge/market_rules.md 域） | 港股（本件 §一） |
|---|---|---|
| 涨跌停 | ±10%/±20% 硬停板 | 无停板; 9 倍报价守卫+VCM±5%~50% |
| T+N | T+1 | 交收周期 PENDING-VERIFY（§三.3）; 盘中回转无限制（无 T+0 禁令面官源实证, 见 §三.3） |
| 收市价 | 15:00 收盘最后价 | 非竞价证券=15:59-16:00 五快照中位; 竞价证券=CAS IEP |
| 碎股 | 竞价撮合整手为主 | 碎股 "D" 型交易入 OTP-C 正典类型 |

## 三、PENDING-VERIFY（未核验面, 官源 URL 未落, 禁当事实引用）

1. **交易时段表**: POS/早市/午休/午市精确时刻（§一.1 仅实证 16:00 收市）。探针计划: HKEX sitemap 或站内 Trading Hours 稳定锚点页。
2. **费用/印花税**: 交易费率、SFC/AFRC 征费、CCASS 交收费、股票转让印花税率（民间通行数字一律未核验禁入）。
3. **交收周期 T+2 与盘中 T+0**: 官方字面（HKSCC Operational Procedures / Settlement 面页 URL 未落）。
4. **逐只 board lot 数表与碎股卖出规则细节**: HKEX 证券资料/单手证券数目面。
5. **港股通红利税（内地个人投资者）**: 财税〔2014〕81号及其后续公告（财政部/税务总局/证监会官源 URL 未落）。
6. **恶劣天气交易安排**: 官网有该锚点（Trading Mechanism 页 Quick Links 在册）, 内容未读。

## 四、维护律

- 每条新核验事实须带源 URL+实读日期行级追加; `PENDING-VERIFY` 项核验后移入 §一并删本节对应行。
- 本件只入机制事实，不入策略结论; 策略面归 research/shortline/AH_PANEL.md。
