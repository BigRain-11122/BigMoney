# market_rules_hk.md — 香港证券市场交易规则（官源核验件）

- 归属: T-2026-09-24-17 deliverable (5)（GM order O-20260924-1155 / CEO 方向: 基金/HK 套利研究线）
- 纪律: RULES-AUDIT —— 每条事实带官源 URL；**无源禁推测**；未核验面一律标 `PENDING-VERIFY`（诚实失败可见），下轮以站点 sitemap/稳定锚点发现 URL 后补验。
- 核验轮: bm-a R169 (2026-09-25 15:2x-15:4x) 首轮首落（两官源主面）; bm-a R171 (2026-09-25 16:0x) 父页 href 发现律补验三面（交易时段/恶劣天气/交收周期 T+2）, 余 3 面 PENDING。

## 一、已核验事实（官源在册）

### 1. 交易机制（无涨跌停停板 + 报价守卫 + VCM）

源: https://www.hkex.com.hk/Services/Trading/Securities?sc_lang=en （HKEX 官网 Trading Mechanism 页, 2026-09-25 实读）

- 港股**无单日涨跌停板**。约束为三层报价守卫+VCM:
  - 连续交易时段限价/增强限价/特别限价单，输入价偏离名义价 9 倍及以上即拒单（Rules of Exchange Rule 505A）。
  - 当日首笔报价: 买价不得低于 prev close 的 24 个价位或 5%（ETP 为 3.5%）以下（取更宽者），卖价对称; 且任何情况不得偏离 prev close 9 倍及以上。
  - VCM（市场波动调节机制）: 适用于恒生综合大型/中型/小型股指数成份股、SPAC 股/权证、合资格 ETF 与杠杆及反向产品; 触发阈值 ±5% 至 ±50%（按证券分级）; 价格偏离 5 分钟前最后成交价超阈值→5 分钟冷静期（限价带内交易）; 仅适用于连续交易时段特定窗口的整手买卖盘输入。
- 开市前时段（POS）与收市竞价时段（CAS）只接受竞价盘与竞价限价盘; POS 竞价限价盘偏离 prev close 9 倍及以上即拒。
- CAS（适用证券）: 参考价上下 **±5%** 为允许价格带（两阶段: 输入时段 ±5%，不可取消时段收紧至买低卖高带内）; 随机收市 2 分钟内; 最终 IEP 为收市价，IEP 无法确定时以参考价收市。
- 非收市竞价证券收市价=最后 1 分钟名义价 5 次快照（15:59:00 起每 15 秒一次）的中位数 → 连续交易时段 16:00 结束; CAS 证券收市竞价至随机收市 16:08-16:10（时段表见 §一.4）。
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
- **交收周期 T+2 字面官源实证**（R171, https://www.hkex.com.hk/Services/Settlement-and-Depository/Settlement?sc_lang=en , 页脚 Updated 22 Jul 2011, 2026-09-25 实读）: "Stock and money positions of all Exchange Trades and Clearing Agency Transactions are required to be settled on **T+2 day** whereas stock positions of China Connect Securities Trades are settled on **T day**."
  - 北向（沪港通/深港通 A 股）股票头寸 T 日交收; CNS 货币头寸 T+1 日上午发 CHATS 支付指令、当日中午前完成付款。
  - 交收以 DVP（货银对付）为基: CNS 交收恒 DVP; 隔离/SI/ISI 可选 DVP/FOP/RDP。

### 4. 交易时段表（R171 官源实证）

源: https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Trading-Hours?sc_lang=en （HKEX Trading Hours 页, 页脚 Updated 16 Sep 2017, 2026-09-25 实读; URL=父页 href 发现律在册, 非盲猜）

**港股证券市场（周一至周五, 公众假期除外）:**

| 时段 | 全日交易 | 半日交易 |
|---|---|---|
| 开市前时段（POS） | 9:00-9:30 | 9:00-9:30 |
| 持续交易·早市 | 9:30-12:00 | 9:30-12:00 |
| 延长早市 | 12:00-13:00 | 不适用 |
| 持续交易·午市 | 13:00-16:00 | 不适用 |
| 收市竞价（CAS） | 16:00 至 16:08-16:10 随机收市 | 12:00 至 12:08-12:10 随机收市 |

- 圣诞/新年/农历新年前夕无延长早市与午市; 无早市则无延长早市。
- **北向（Stock Connect, SSE/SZSE 时段）**: 开盘集合竞价 9:15-9:25 / 早市连续竞价 9:30-11:30 / 午市 13:00-14:57 / 收盘集合竞价 14:57-15:00; 港方 EP 落单窗 9:10-11:30 + 12:55-15:00（9:20-9:25 与 14:57-15:00 沪深不收撤单; 9:10-9:15/9:25-9:30/12:55-13:00 单可收但沪深未开市不处理）。

### 5. 恶劣天气交易安排（SWT, R171 官源实证——修正民间旧识）

源: https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Severe-Weather-Arrangements?sc_lang=en （HKEX Severe Weather Arrangements Overview, 页脚 Updated 19 Sep 2024, 2026-09-25 实读）

- **自 2024 年起实施恶劣天气交易（Severe Weather Trading, SWT）, 2024-09-23 正式生效**（实施通告 16 Sep 2024 在册）: 八号风球/黑雨等恶劣天气下香港证券与衍生品市场**照常按既定交易日历交易**, 含 Stock Connect、衍生品假期交易与收市后交易时段。
- 远端作业与线上服务为 SWT 日主推方式, 对公众开放的实体网点当日停服; 全体证券/衍生品 EP/CP 已申报 SWT 就绪（截至 2025-03-31 更新行）。
- ⚠ 民间通行「八号风球=休市」为 2024-09 前旧识, 现行机制下禁再当事实引用。

## 二、与 A 股面差异速查（本研究线消费面）

| 维度 | A 股（本仓 knowledge/market_rules.md 域） | 港股（本件 §一） |
|---|---|---|
| 涨跌停 | ±10%/±20% 硬停板 | 无停板; 9 倍报价守卫+VCM±5%~50% |
| T+N | T+1 | 交收 T+2（§一.3 官源字面）; 盘中回转无禁止条款见 §三.3 残余面 |
| 收市价 | 15:00 收盘最后价 | 非竞价证券=15:59-16:00 五快照中位; 竞价证券=CAS IEP（随机收市 16:08-16:10, §一.4） |
| 碎股 | 竞价撮合整手为主 | 碎股 "D" 型交易入 OTP-C 正典类型 |

## 三、PENDING-VERIFY（未核验面, 官源 URL 未落, 禁当事实引用）

R171 迁出三项（原 1/3/6 → §一.4/§一.3/§一.5）。余三项:

1. **费用/印花税**: 交易费率、SFC/AFRC 征费、CCASS 交收费、股票转让印花税率（民间通行数字一律未核验禁入）。R171 探针实录: Fees>Securities(Hong Kong)>Trading>Participantship 页（ https://www.hkex.com.hk/Services/Rules-and-Forms-and-Fees/Fees/Securities-(Hong-Kong)?sc_lang=en ）只载 participantship 费（交易权申请 $500,000/月费 $2,900/忠诚基金/印花税保证金 $5,000）, 页自注「not exhaustive→Chapter 8 of the Rules」——交易费率表在 Rules of the Exchange 第 8 章 PDF 或 Fees>Clearing and Settlement 子页; 印花税率本体归 IRD 域（禁盲猜 URL, 待 IRD 站内发现）。
2. **逐只 board lot 数表与碎股卖出规则细节**: HKEX 证券资料/单手证券数目面（Trading Mechanism 页 nav 在册「Full List of Securities」, URL 未取）; 价位表（Second Schedule spreads）PDF 已在册 `/-/media/HKEX-Market/Services/Rules-and-Forms-and-Fees/Rules/SEHK/Securities/Rules/Sch_2_eng.pdf`（spreads 非 lot 数, 两面勿混）。
3. **港股通红利税（内地个人投资者）**: 财税〔2014〕81号及其后续公告（财政部/税务总局/证监会官源 URL 未落; 属内地官源域, HKEX 站内无此件）。
4. **盘中回转（当日买卖同股）无禁止之负面主张**: 已验 T+2 交收字面（§一.3）, 但「日内回转允许」系未见禁止条款的推论面, 未见正面官源字面, 禁当硬事实引用（回测 T+1 约束建模时以本仓 engine 保守口径为准）。

## 四、维护律

- 每条新核验事实须带源 URL+实读日期行级追加; `PENDING-VERIFY` 项核验后移入 §一并删本节对应行。
- 本件只入机制事实，不入策略结论; 策略面归 research/shortline/AH_PANEL.md。
