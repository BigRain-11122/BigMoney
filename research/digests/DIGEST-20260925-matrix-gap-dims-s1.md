# DIGEST-20260925 · 多维矩阵缺口维度 s1（T-2026-09-25-60 · O-20260925-1152 CEO 直令）

> 正典=firm/PRODUCT_MATRIX.md v1.0（bm-a 随令已交·本册不重述四轴表）。本册=三空白维度首批调研：(a) 转债数据可达性审计+外源战法锚、(b) 中线摆动维度 T-47 收敛消费、(c) 套利 carry 候选面。五步制第 1-2 步（外源调研→数据审计），**零引擎改动零 prereg**。dept:研究+数据 联合。

## 〇 通道纪律（slice-1 实况）

零网络内省优先（R118 律：inspect 源码 URLs 非文档宣称）；实网探针=盘后窗再发（当前盘中 11:4x+EM/集思录限速与礼貌律）；集思录 feed=已验通道（R138/R141 基线 20 IDs·results/jisilu_feed_baseline.json）。

## 一 面 (a) 转债维度·数据可达性审计（akshare 函数面内省实读）

| 面 | akshare 函数（签名实读） | 源（源码 URL 内省） | 转债战法对应 | 诚实注记 |
|---|---|---|---|---|
| 个券历史日线 | bond_zh_hs_cov_daily(symbol='sh010107') | 新浪财经 vip.stock.finance.sina.com.cn | 双低/动量面的价格腿 | **docstring 明示「大量抓取容易封 IP」→须 2.5s+ 步速+页级重试（R109 公民步速律照抄 EM 面）** |
| 全表截面 | bond_cb_jsl(cookie=None) | www.jisilu.cn/data/cbnew/ | 双低全谱（价+溢价+双低分） | **cookie 参数=登录墙面**（全表面须 cookie，集思录公开面≠全表面）——免费空间内全谱截面得走 EM/THS 替代面 |
| 强赎面 | bond_cb_redeem_jsl() | jisilu /data/cbnew/#redeem | 强赎博弈 | 无 cookie 参数=公开面候选（盘后窗 1 发探针验证） |
| 转股价调整记录 | bond_cb_adj_logs_jsl(symbol) | jisilu adj_logs API | **下修博弈直接数据面** | 同上待探 |
| 转债等权指数 | bond_cb_index_jsl() | jisilu /webapi/cb/index_history/ | 市场基准/状态面 | 公开 webapi 候选 |
| 发行条款面 | bond_zh_cov() / bond_zh_cov_info(symbol, indicator) | EM datacenter-web kzz | 条款（转股价/强赎条款/到期） | datacenter-web 家族=与 moneyflow 同面（R108 域活路径死教训：**双面冗余律照用**） |
| 溢价率分析 | bond_zh_cov_value_analysis(symbol) | EM datacenter-web | 双低面的溢价腿 | 逐券面=批量成本高，s2 审计频度 |
| 比价截面 | bond_cov_comparison() | EM 16.push2 clist | 双低截面（价+溢价全谱） | **push2 clist=盘中 09:15-15:05 禁拉面+间歇阻断史（R108/R109）→盘后单发+限速** |
| THS 聚合 | bond_zh_cov_info_ths() | data.10jqka.com.cn | 行情聚合 | R118 教训预警：**先量纲级审计**（聚合口径无溢价分解则不可冒充双低面） |

**审计结论（s1 级）**：免费 API 空间内转债面=三源结构（jsl 公开三面[redeem/adj_logs/index]+EM datacenter 条款/溢价面+sina 个券日线）——可达性**无结构性死面**，但全谱双低截面依赖 EM clist（受限面）或 jsl cookie（墙面）；条款示面（下修公告）覆盖度=盘后探针后如实披露。**百万资金可投性**：转债 10 张/手起（面值 1000 元/手），百万资金无门槛。

### 外源战法锚（借力律·不重复采集）

- **集思录 category-5 feed ID 504636（CB 双低轮动 2025 日志）**：r147 已登记录（时为 P1 域外注册）；**本令（O-1152+T-60 P1·immediate）=GM 署名到位，P1 门槛已过**——升级为 s1-slice2 深捕获头号目标（feed 通道已验·1 fetch 面）。
- 民间标准战法清单（folkllore-standard·社区数字一律假设级标签）：双低轮动（价+溢价双低分排名）、下修博弈（转股价下修事件驱动）、强赎博弈（强赎条款触发博弈）、低价+纯债溢价防御面。**全部=未验证假设，验证独立归门禁链（借力律）**。

## 二 面 (b) 中线摆动维度·T-47 收敛消费（cite not re-harvest）

**T-47 已 done（波-6 收敛·result_ref=DIGEST-20260925-wave6-slice8.md+链）→ T-60 s3 物理依赖本轮解除**。可消费供给（全部已入册卡）：

1. 窗口有利性衰减律×4 外证（20419 动量 27y Sharpe 0.089 崩/20417 HMM 窗衰减/20416 一月效应 27y 反转/2607.01550 短期趋势 demise）→ **中线维度设计铁则：多虚拟起点+27y 级长窗检验入场，禁 5y 窗选型**。
2. 成本集中律（Lesmond JFE 2004·508 引）：高动量收益股=高交易成本股→中线轮动若走股票面须成本面分层；**ETF 面天然规避**（公司主战场口径一致）。
3. vol-regime 条件化变体（PBCSF T+1 隔夜贴水·市场波动分层）+LeBaron 效应卡——中线摆动的条件化入场候选（s3 prereg 素材）。
4. 19360 regime 轮动=三军架构外证（REGIME_GUARD 慢线+半步快线镜像）——中线维度的状态机骨架直接复用正典件。

**s3 开工条件已满足**：T-47 收敛件在册+依赖注记可翻转；s3=周-月频轮动/动量旋转设计+prereg（等 s1-slice2/s2 转债批同期排片，预注册从 PREREG_TEMPLATE.md 起草，D6 正交门 vs 现有六员+PROSPECT 族）。

## 三 面 (c) 套利 carry 候选（登记面·不立项）

- **ETF 折价申赎**：P-A1 溢价子线判负**不翻案不更名复活**（T-50 面(f) 已消费 WorldQuant/Wilmott 平台族，与本面无涉）。
- **REITs 折溢价**：T-16 NAV 面（bm-c 车道·results/fund_premium_status.json 在册）=数据面已备；carry 主题与折溢价子线判负面**严格分册**（T-53 面(d) 防混淆注记在先）。
- **转债 carry 面**：转股溢价<0 的纯套利腿=**另册**（本 digest 只登记数据面=bond_zh_cov_value_analysis），与双低轮动（β 面）分口径；任何立项=五步制另票。

## 四 漏斗双列（funnel dual-column law）

| 面 | 采集（harvest） | 过闸（gated/采纳） |
|---|---|---|
| (a) 转债 | 数据面 9 函数内省实读+1 外源锚（504636 升格）+4 战法清单 | **0**（探针盘后发；0 回测 0 引擎） |
| (b) 中线 | T-47 收敛消费（4 卡+依赖解除） | **0**（s3 未起草） |
| (c) carry | 3 面登记 | **0** |

## 五 s1-slice2+ 续作指针

1. 盘后窗转债探针批（≤5 发·串行 2.5s）：bond_cb_redeem_jsl/bond_cb_index_jsl/bond_cb_adj_logs_jsl(1 券样例)/bond_zh_cov/bond_zh_hs_cov_daily(1 券样例)——可达性三态如实（活/死/形状漂移），R109 步速+失败退避。
2. 504636 深捕获（feed 通道 1 fetch）→双低战法外源卡。
3. 数据窗/条款覆盖度披露节成形→s2 prereg 起草（转债首批·模式规则+数据窗+成本面 R99 冻结）。
4. s3 中线 prereg 与 T-47 收敛卡对接（§二素材）。

—— s1 slice-1 交付止于此（bm-b r175）。
