# market_rules_hk.md — 香港证券市场交易规则（官源核验件）

- 归属: T-2026-09-24-17 deliverable (5)（GM order O-20260924-1155 / CEO 方向: 基金/HK 套利研究线）
- 纪律: RULES-AUDIT —— 每条事实带官源 URL；**无源禁推测**；未核验面一律标 `PENDING-VERIFY`（诚实失败可见），下轮以站点 sitemap/稳定锚点发现 URL 后补验。
- 核验轮: bm-a R169 (2026-09-25 15:2x-15:4x) 首轮首落（两官源主面）; bm-a R171 (2026-09-25 16:0x) 父页 href 发现律补验三面（交易时段/恶劣天气/交收周期 T+2）; bm-a R172 (2026-09-25 16:0x) 二批四面（交易费率 Chap 8 字面/征费机制 Chap 11/CCASS 交收费/逐只 board lot 全表+印花适用列）; bm-a R173 (2026-09-25 16:2x) **费率数值面四子面齐验**（HKEX Fees>Securities(HK)>Trading>Transaction 页单页五值: 印花税率 0.1% 双边+SFC 0.0027%+AFRC 0.00015%+ICL 0.002% suspended+Trading Fee 交叉验; elegislation=JS 检查墙死面如实记）, PENDING 余 2 项（红利税/盘中回转负面主张）。

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
- 每只证券的手数（board lot size）由发行人定、逐只不同——**逐只全表官源实证（R172）**: List of Securities 官方 xlsx（ https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx , "Updated as at 25/09/2026" 实读, 17,587 只证券, Board Lot 列 17,587/17,587 全非空; 全列含 Stock Code/Name/Category/Sub-Category/Board Lot/ISIN/Expiry Date/**Subject to Stamp Duty**/Shortsell/CAS/VCM/POS Eligible/Spread Table/Trading Currency/RMB Counter; AH 名单抽查 15/15 全中——BYD ELECTRONIC 500、SINOPEC CORP 2,000、CNOOC 1,000、CCB 1,000、AIR CHINA 2,000 等; 证据=results/shortline/hkex_full_list_probe.json, URL=Trading Mechanism 父页 href 发现律在册）。

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

### 6. 交易费用（HKEX 侧官源字面, R172 机制面 + R173 数值面）

源: Rules of the Exchange Chap 8/Chap 11 官方 PDF（URL=SEHK Rules 父页 href 发现律在册, 2026-09-25 实读）+ Fees>Securities(Hong Kong)>Clearing and Settlement>Operational 页（Updated 22 Nov 2023, 2026-09-25 实读）; 证据=results/shortline/hkex_rules_pdf_probe.json + hkex_clearing_fee_probe.json + hkex_chap{8,11,13}*.txt。

- **交易费（Trading Fee）: 0.00565% of the amount of the consideration**——每笔证券买卖各收（rounded to the nearest cent）（Rules of the Exchange Rule 802(12A), Chap_8_eng.pdf, 页 8-2 字面: "Trading Fee; 0.00565% of the amount of the consideration for: (a) each purchase or sale of securities admitted to trading..."）。
- **交易征费机制（Chap 11）**: SFC Transaction Levy（费率=Securities and Futures (Levy) Order 不时规定）+ AFRC Transaction Levy（费率=AFRC Ordinance 不时规定）+ Investor Compensation Levy（费率=SFC (Investor Compensation – Levy) Rules; Rule 1103A=宽免公告生效期免征, 由 Board 以通函通知）——Rule 1103 字面「rate as specified from time to time」=机制在 Rules, **费率数值已由 HKEX Fees 页官源落定（R173, 下条）**。买卖双方各付（Rule 1101/1101A）。
- **费率数值面（R173 官源字面, 单页五值）**: 源=https://www.hkex.com.hk/Services/Rules-and-Forms-and-Fees/Fees/Securities-(Hong-Kong)/Trading/Transaction?sc_lang=en （HKEX Fees>Securities(Hong Kong)>Trading>Transaction 页, 2026-09-25 实读; URL=父页 href 发现律两跳在册; 证据=results/shortline/hkex_fees_transaction_r173.json）:
  - **股票转让印花税: 0.1%** on the value of the transaction, **买卖双方各付**（rounded up to the nearest dollar）; 逐只豁免面见 List of Securities「Subject to Stamp Duty」列（§一.6 上文 R172 全表）。——IRD 域 603B 反爬死面由交易所官源数值面替代收口。
  - **SFC Transaction Levy: 0.0027%** per side（effective 1 Nov 2014, rounded to nearest cent, SMM 交易免征）。
  - **AFRC Transaction Levy: 0.00015%** per side（effective 1 Jan 2022, rounded to nearest cent, SMM 交易免征, collected for AFRC）。
  - **Investor Compensation Levy: 0.002%** per side **自 2005-12-19 起 suspended by the SFC（现行状态=免征）**——Rule 1103A 宽免机制（R172）对应现行实况落定。
  - **Trading Fee: 0.00565%** per side——与 Chap 8 PDF 字面（R172）**双官源交叉验一致**。
  - 非港元币别交易: 各费以印花税计算用汇率折算（页面字面）。
- **CCASS 股票交收费（Stock Settlement Fee, 交收参与者面）**: 经由交易所买卖（broker-broker）=**0.0042% per side** of gross value（合资格 ETF 例外=0.002%）; broker-custodian/clearing agency 交易=0.002% of gross value; SI/ISI/组合调动按 HKSCC Operational Procedures §21 费率表; EFN/指定工具转移=0.002% nominal, min HK$2, max HK$100（Clearing-and-Settlement>Operational 页字面）。
- **印花税适用面（逐只列）**: List of Securities xlsx「Subject to Stamp Duty」列——Equity 2,816 只中 **2,809 只 Y+7 只空**（空=AMGEN-T 等 6 只 Trading Only Securities 美国评论-only + CINDA 21USDPREF 1 只）; 股本权证 6 只全 Y; Debt/DW/CBBC/ETP/REITs 全空（全表 Y 合计 2,815=2,809+6）。**税率数值本体归 IRD 域 PENDING 见 §三.1**。
- ⚠ 民间通行「佣金」等经纪面费率=非交易所定价（broker 自由佣金, 无官源单值）, 一律以券商实际费率为准; 已验交易所/法定侧全值见上文（交易费 0.00565%+印花税 0.1% 双边+SFC 0.0027%+AFRC 0.00015%+CCASS 0.0042% 双边, ICL 现行免征）; 未验面以 engine 保守口径为准。

## 二、与 A 股面差异速查（本研究线消费面）

| 维度 | A 股（本仓 knowledge/market_rules.md 域） | 港股（本件 §一） |
|---|---|---|
| 涨跌停 | ±10%/±20% 硬停板 | 无停板; 9 倍报价守卫+VCM±5%~50% |
| T+N | T+1 | 交收 T+2（§一.3 官源字面）; 盘中回转无禁止条款见 §三.3 残余面 |
| 收市价 | 15:00 收盘最后价 | 非竞价证券=15:59-16:00 五快照中位; 竞价证券=CAS IEP（随机收市 16:08-16:10, §一.4） |
| 碎股 | 竞价撮合整手为主 | 碎股 "D" 型交易入 OTP-C 正典类型 |

## 三、PENDING-VERIFY（未核验面, 官源 URL 未落, 禁当事实引用）

R171 迁出三项（原 1/3/6 → §一.4/§一.3/§一.5）; R172 迁出两项（原 1/2 → §一.6/§一.2, 费用面部分核验）; **R173 迁出一项**（原 1 费率数值面四子面 → §一.6, 单页五值齐验）。余:

1. **港股通红利税（内地个人投资者）**: 财税〔2014〕81号及其后续公告（财政部/税务总局/证监会官源 URL 未落; 属内地官源域, HKEX 站内无此件）。R172 实录: Bing 搜索通道返回非官源垃圾（pixelverse 噪音）=通道死, 下轮走 mof.gov.cn/chinatax.gov.cn 站内发现或政府网政策文件库检索面。
2. **盘中回转（当日买卖同股）无禁止之负面主张**: 已验 T+2 交收字面（§一.3）, 但「日内回转允许」系未见禁止条款的推论面, 未见正面官源字面, 禁当硬事实引用（回测 T+1 约束建模时以本仓 engine 保守口径为准）。

## 四、维护律

- 每条新核验事实须带源 URL+实读日期行级追加; `PENDING-VERIFY` 项核验后移入 §一并删本节对应行。
- 本件只入机制事实，不入策略结论; 策略面归 research/shortline/AH_PANEL.md。
